import WeatherSection from "@/components/weather/WeatherSection";
import MarketSection from "@/components/market/MarketSection";

export const metadata = { title: "Weather Advisory — AgriSense" };

export default function WeatherPage() {
  return (
    <div className="space-y-20 pt-10 pb-24">
      <WeatherSection />
      <MarketSection />
    </div>
  );
}
