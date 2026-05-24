import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow images from OpenWeatherMap icons
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "openweathermap.org" },
    ],
  },
};

export default nextConfig;
