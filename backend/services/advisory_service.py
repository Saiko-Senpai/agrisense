"""
services/advisory_service.py — Llama Weather Advisory Service.

Analyzes weather metrics and the selected crop to generate highly contextualized,
professional, and actionable farming recommendations using Llama 3.2.
"""

import asyncio
import logging
import os
import json
import time
from typing import Any

import httpx
from utils.parser import extract_json

logger = logging.getLogger("agrisense.services.advisory")

ADVISORY_PROMPT_TEMPLATE = """
You are an expert agronomist and AI agricultural specialist. 
Your task is to analyze the current weather conditions and generate highly specific, professional, and actionable crop-specific farming suggestions for the crop: {crop_name}.

Current Weather Data at {location_name}:
- Temperature: {temp}°C (feels like {feels_like}°C)
- Humidity: {humidity}%
- Weather Conditions: {description}
- Wind Speed: {wind_speed} km/h
- Atmospheric Pressure: {pressure} hPa

Please generate exactly 3 advisory recommendations tailored to these conditions and this crop. 
Each recommendation MUST be returned in the following JSON format:
{{
  "advisories": [
    {{
      "icon": "💧",
      "title": "Irrigation Advice",
      "text": "Specific irrigation advice for {crop_name} based on {humidity}% humidity and {temp}°C temp. Suggest if they need to increase, reduce, or stop irrigation, mentioning potential waterlogging or drought stress.",
      "type": "info"
    }},
    {{
      "icon": "🌡️",
      "title": "Temperature Alert",
      "text": "Detailed temperature impact advice for {crop_name} at {temp}°C. E.g. heat stress risk, optimal growth range, mulching suggestions, cold protection.",
      "type": "info"
    }},
    {{
      "icon": "🦠",
      "title": "Disease Risk",
      "text": "Pathogen & disease risk assessment for {crop_name} due to weather. Name specific diseases of {crop_name} favored by {humidity}% humidity and {temp}°C temp (e.g., blast, downy mildew, leaf spot, root rot).",
      "type": "info"
    }}
  ]
}}

Guidelines for 'type':
- Use "danger" for severe risks (e.g., temperatures above 36°C causing flower drop, humidity above 80% with high fungal threat, heavy rain/storms, frost).
- Use "warn" for moderate risks (e.g., moderate temperature stress, winds above 12 km/h interfering with foliar spraying, rising disease pressure).
- Use "info" for ideal or standard growth conditions and standard practices.

Rules:
- Be highly professional, scientific, and specific to the crop "{crop_name}" (do NOT give generic advice). Mention details unique to {crop_name}.
- Format all text content clearly. Keep descriptions highly concise, professional, and actionable (1-2 sentences each).
- Return ONLY valid JSON matching the exact schema specified above. No markdown formatting outside of the JSON itself, and no extra keys.
"""


class AdvisoryService:
    """
    Service layer to interact with OpenRouter API and generate weather-based crop advisories using Llama.
    """

    def __init__(self) -> None:
        self._api_key = os.getenv("LLAMA_API_KEY") or os.getenv("QWEN_API_KEY")
        if not self._api_key:
            logger.warning("LLAMA_API_KEY / QWEN_API_KEY not set. Advisory service will fail on first call.")

        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://agrisense.ai",
            "X-Title": "AgriSense AI",
        }

        self._model_name = os.getenv("LLAMA_MODEL", "meta-llama/llama-3.2-11b-vision-instruct")
        
        # Simple in-memory cache to protect the free tier OpenRouter API key from StrictMode double-mounts
        # Key: (crop_name, temp, humidity, description) -> (timestamp, response_dict)
        self._cache: dict[tuple[str, int, int, str], tuple[float, dict[str, Any]]] = {}
        self._cache_ttl = 300  # 5 minutes cache lifetime
        logger.info(f"AdvisoryService initialized with model: {self._model_name} (with 5-minute memory caching enabled)")

    async def generate_advisory(self, crop_name: str, weather_data: dict[str, Any]) -> dict[str, Any]:
        """
        Invoke Llama via OpenRouter to generate dynamic weather advisory cards.
        """
        # Extract fields safely with defaults
        main_weather = weather_data.get("main", {})
        temp = main_weather.get("temp", 32)
        feels_like = main_weather.get("feels_like", 35)
        humidity = main_weather.get("humidity", 70)
        pressure = main_weather.get("pressure", 1010)

        weather_list = weather_data.get("weather", [])
        description = weather_list[0].get("description", "clear sky") if weather_list else "clear sky"

        wind = weather_data.get("wind", {})
        wind_speed = wind.get("speed", 5.0)

        location_name = weather_data.get("name", "Unknown Location")

        # --- In-memory cache check ---
        # Round values slightly to absorb minor temperature/humidity fluctuations
        cache_key = (crop_name, int(round(float(temp))), int(round(float(humidity))), description.lower())
        now = time.time()
        
        if cache_key in self._cache:
            timestamp, cached_res = self._cache[cache_key]
            if now - timestamp < self._cache_ttl:
                logger.info(f"Cache Hit | Returning cached weather advisory for crop={crop_name}...")
                return cached_res
            else:
                del self._cache[cache_key]

        # Format the prompt
        prompt = ADVISORY_PROMPT_TEMPLATE.format(
            crop_name=crop_name,
            location_name=location_name,
            temp=temp,
            feels_like=feels_like,
            humidity=humidity,
            description=description,
            wind_speed=wind_speed,
            pressure=pressure
        )

        logger.info(f"Generating weather advisory for crop={crop_name} in {location_name}...")

        payload = {
            "model": self._model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert agronomist. Generate crop weather advisories matching the requested schema. Return ONLY valid JSON matching the exact schema requested, with no explanations, markdown formatting, or code blocks outside the JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=self._headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                raw_text = data["choices"][0]["message"]["content"].strip()

            logger.debug(f"Raw Llama Advisory Response: {raw_text}")

            parsed = extract_json(raw_text)
            if "advisories" not in parsed:
                raise ValueError("JSON response missing 'advisories' key.")

            # Save successful response to cache
            self._cache[cache_key] = (now, parsed)
            return parsed

        except Exception as e:
            logger.warning(
                f"Llama weather advisory generation failed ({e}). Falling back to static advisory...",
                exc_info=True
            )
            return self._generate_static_fallback(crop_name, weather_data)

    def _generate_static_fallback(self, crop_name: str, weather_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generates clean, pre-calculated agronomical advice as a resilient fallback
        when the Gemini API is rate-limited or unavailable.
        """
        main = weather_data.get("main", {})
        temp = int(round(float(main.get("temp", 32))))
        humidity = int(round(float(main.get("humidity", 70))))
        weather_list = weather_data.get("weather", [])
        desc = weather_list[0].get("description", "clear sky") if weather_list else "clear sky"

        return {
            "advisories": [
                {
                    "icon": "💧",
                    "title": "Irrigation Advice",
                    "text": (
                        f"High humidity at {humidity}%. Reduce irrigation frequency to prevent "
                        f"waterlogging and fungal disease spread in {crop_name}."
                    ) if humidity > 80 else (
                        f"Humidity at {humidity}%. Irrigate {crop_name} every "
                        f"{'5' if temp > 30 else '7'} days at root zone for optimal growth."
                    ),
                    "type": "warn" if humidity > 80 else "info"
                },
                {
                    "icon": "🌡️",
                    "title": "Temperature Alert",
                    "text": (
                        f"Heat stress risk at {temp}°C! {crop_name} may face flower drop. "
                        "Apply mulch and increase irrigation frequency."
                    ) if temp > 35 else (
                        f"Temperature {temp}°C is {'warm but' if temp > 25 else 'ideal —'} "
                        f"suitable for {crop_name} growth."
                    ),
                    "type": "danger" if temp > 35 else "info"
                },
                {
                    "icon": "🦠",
                    "title": "Disease Risk",
                    "text": (
                        f"High disease pressure! {humidity}% humidity strongly favors fungal "
                        f"diseases in {crop_name}. Apply preventive fungicide."
                    ) if humidity > 75 else (
                        f"Low to moderate disease risk at {humidity}% humidity. "
                        f"Continue regular monitoring of {crop_name}."
                    ),
                    "type": "danger" if humidity > 75 else "info"
                }
            ],
            "is_fallback": True
        }
