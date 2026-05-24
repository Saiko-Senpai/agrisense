"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { MapPin, Wind, Droplets, Thermometer } from "lucide-react";
import { fetchWeatherByCoords, getWeatherAdvisory, getGeolocation } from "@/lib/weather";
import { WeatherData, Advisory } from "@/types";
import { crops } from "@/data/crops";
import SectionHeader from "@/components/ui/SectionHeader";

export default function WeatherSection() {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [advisory, setAdvisory] = useState<Advisory[]>([]);
  const [selectedCrop, setSelectedCrop] = useState("Rice");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const coords = await getGeolocation().catch(() => ({ latitude: 22.57, longitude: 88.36 }));
        const data = await fetchWeatherByCoords(coords.latitude, coords.longitude);
        setWeather(data);
        setAdvisory(getWeatherAdvisory(data, selectedCrop));
      } catch {
        setError("Unable to load weather data.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  useEffect(() => {
    if (weather) setAdvisory(getWeatherAdvisory(weather, selectedCrop));
  }, [selectedCrop, weather]);

  const advTypeStyle: Record<string, string> = {
    info: "border-l-green-400 bg-white",
    warn: "border-l-amber-400 bg-amber-50/50",
    danger: "border-l-red-400 bg-red-50/50",
  };

  return (
    <section className="px-4 md:px-6 max-w-7xl mx-auto">
      <SectionHeader badge="🌤️ Live Data" title="Weather Advisory Dashboard" subtitle="Real-time weather with crop-specific farming recommendations" />

      {loading && (
        <div className="rounded-2xl bg-gradient-to-br from-blue-50 to-green-50 p-8">
          <div className="skeleton h-8 w-48 mb-4" />
          <div className="skeleton h-24 mb-6" />
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5].map((i) => <div key={i} className="skeleton h-28" />)}
          </div>
        </div>
      )}

      {error && (
        <div className="text-center py-12 text-gray-500">{error}</div>
      )}

      {!loading && !error && weather && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl bg-gradient-to-br from-blue-50 to-green-50 p-6 md:p-8 border border-blue-100/60"
        >
          {/* Location */}
          <div className="flex items-center gap-2 text-green-700/60 text-sm mb-6">
            <MapPin size={14} />
            <span>{weather.name}</span>
            {weather.mock && (
              <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full border border-amber-200">
                Demo Data — Add API Key for Live Data
              </span>
            )}
          </div>

          {/* Main weather + crop selector */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Temp card */}
            <div className="glass rounded-2xl p-6 flex items-center gap-6">
              <div>
                <div className="text-7xl font-serif text-green-700 leading-none">
                  {Math.round(weather.main.temp)}°
                </div>
                <div className="text-green-600/60 mt-1 capitalize">{weather.weather[0]?.description}</div>
                <div className="text-xs text-green-600/40 mt-0.5">
                  Feels like {Math.round(weather.main.feels_like)}°C
                </div>
              </div>
              <div className="grid grid-cols-1 gap-3">
                {[
                  { icon: <Droplets size={14} />, label: "Humidity", val: `${weather.main.humidity}%` },
                  { icon: <Wind size={14} />, label: "Wind", val: `${Math.round(weather.wind.speed)} km/h` },
                  { icon: <Thermometer size={14} />, label: "Pressure", val: `${weather.main.pressure} hPa` },
                ].map((d) => (
                  <div key={d.label} className="bg-white/80 rounded-xl px-3 py-2 text-center">
                    <div className="flex items-center gap-1 text-green-600/50 text-xs mb-0.5 justify-center">
                      {d.icon} {d.label}
                    </div>
                    <div className="font-bold text-green-800 text-sm">{d.val}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Crop selector */}
            <div className="glass rounded-2xl p-6">
              <label className="block text-sm font-semibold text-green-800 mb-3">
                🌾 Select Crop for Advisory
              </label>
              <select
                value={selectedCrop}
                onChange={(e) => setSelectedCrop(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-green-200 bg-white font-medium text-green-800 text-sm outline-none focus:ring-2 focus:ring-green-300 cursor-pointer mb-4"
              >
                {crops.map((c) => (
                  <option key={c.id} value={c.name}>
                    {c.emoji} {c.name}
                  </option>
                ))}
              </select>
              <p className="text-xs text-green-600/50 leading-relaxed">
                Advisory cards below update automatically based on your selected crop and current weather conditions.
              </p>
            </div>
          </div>

          {/* Advisory cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {advisory.map((adv, i) => (
              <motion.div
                key={adv.title}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 }}
                className={`rounded-xl p-4 border-l-4 ${advTypeStyle[adv.type]}`}
              >
                <div className="text-2xl mb-2">{adv.icon}</div>
                <div className="font-semibold text-gray-800 text-sm mb-1">{adv.title}</div>
                <p className="text-gray-500 text-xs leading-relaxed">{adv.text}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </section>
  );
}
