import { WeatherData, Advisory } from "@/types";

const OPENWEATHER_API_KEY = process.env.NEXT_PUBLIC_OPENWEATHER_API_KEY;
const BASE_URL = "https://api.openweathermap.org/data/2.5";

// Fallback mock data when API key is not set or request fails
const getMockWeather = (cityName = "Kolkata"): WeatherData => ({
  name: cityName,
  main: { temp: 32, humidity: 78, feels_like: 36, pressure: 1008 },
  weather: [{ description: "Partly Cloudy", icon: "02d" }],
  wind: { speed: 12 },
  visibility: 8000,
  mock: true,
});

export async function fetchWeatherByCoords(
  lat: number,
  lon: number
): Promise<WeatherData> {
  if (!OPENWEATHER_API_KEY || OPENWEATHER_API_KEY === "your_api_key_here") {
    console.warn("OpenWeatherMap API key not set. Using mock weather data.");
    return getMockWeather();
  }

  try {
    const res = await fetch(
      `${BASE_URL}/weather?lat=${lat}&lon=${lon}&appid=${OPENWEATHER_API_KEY}&units=metric`,
      { next: { revalidate: 600 } } // Cache for 10 minutes
    );

    if (!res.ok) {
      throw new Error(`Weather API error: ${res.status}`);
    }

    return res.json();
  } catch (error) {
    console.error("Weather fetch failed:", error);
    return getMockWeather();
  }
}

export async function fetchWeatherByCity(city: string): Promise<WeatherData> {
  if (!OPENWEATHER_API_KEY || OPENWEATHER_API_KEY === "your_api_key_here") {
    return getMockWeather(city);
  }

  try {
    const res = await fetch(
      `${BASE_URL}/weather?q=${encodeURIComponent(city)}&appid=${OPENWEATHER_API_KEY}&units=metric`
    );

    if (!res.ok) throw new Error(`Weather API error: ${res.status}`);
    return res.json();
  } catch (error) {
    console.error("Weather fetch failed:", error);
    return getMockWeather(city);
  }
}

export function getWeatherAdvisory(weather: WeatherData, cropName: string): Advisory[] {
  const temp = Math.round(weather.main?.temp ?? 32);
  const humidity = weather.main?.humidity ?? 70;
  const desc = weather.weather?.[0]?.description ?? "Clear";

  return [
    {
      icon: "💧",
      title: "Irrigation Advice",
      text:
        humidity > 80
          ? `High humidity at ${humidity}%. Reduce irrigation frequency to prevent waterlogging and fungal disease spread in ${cropName}.`
          : `Humidity at ${humidity}%. Irrigate ${cropName} every ${temp > 30 ? "5" : "7"} days at root zone for optimal growth.`,
      type: humidity > 80 ? "warn" : "info",
    },
    {
      icon: "🌡️",
      title: "Temperature Alert",
      text:
        temp > 35
          ? `Heat stress risk at ${temp}°C! ${cropName} may face flower drop. Apply mulch and increase irrigation frequency.`
          : `Temperature ${temp}°C is ${temp > 25 ? "warm but" : "ideal —"} suitable for ${cropName} growth.`,
      type: temp > 35 ? "danger" : "info",
    },
    {
      icon: "🦠",
      title: "Disease Risk",
      text:
        humidity > 75
          ? `High disease pressure! ${humidity}% humidity strongly favors fungal diseases in ${cropName}. Apply preventive fungicide.`
          : `Low to moderate disease risk at ${humidity}% humidity. Continue regular monitoring of ${cropName}.`,
      type: humidity > 75 ? "danger" : "info",
    },
    {
      icon: "🌾",
      title: "Farming Suggestion",
      text: `Based on current ${desc.toLowerCase()} conditions, it's ${temp < 30 && humidity < 70 ? "ideal" : "acceptable"} for field operations. Monitor ${cropName} for any visible stress symptoms.`,
      type: "info",
    },
    {
      icon: "🧪",
      title: "Fertilizer Timing",
      text:
        desc.toLowerCase().includes("rain")
          ? `Delay foliar fertilizer application. Rain expected — apply granular fertilizer for ${cropName} instead to avoid wash-off losses.`
          : `Good conditions for foliar spray application on ${cropName}. Apply in early morning or evening.`,
      type: desc.toLowerCase().includes("rain") ? "warn" : "info",
    },
  ];
}

export function getGeolocation(): Promise<GeolocationCoordinates> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Geolocation not supported"));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve(pos.coords),
      (err) => reject(err),
      { timeout: 8000 }
    );
  });
}
