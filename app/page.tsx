import HeroSection from "@/components/hero/HeroSection";
import CropGrid from "@/components/crops/CropGrid";
import WeatherSection from "@/components/weather/WeatherSection";
import MarketSection from "@/components/market/MarketSection";

export default function HomePage() {
  return (
    <div className="space-y-20 pb-24">
      <HeroSection />

      <section className="px-4 md:px-6 max-w-7xl mx-auto">
        <CropGrid
          title="Explore Crop Library"
          subtitle="Click any crop for detailed growing guides, disease prevention & smart farming tips"
        />
      </section>

      <WeatherSection />

      <MarketSection />
    </div>
  );
}
