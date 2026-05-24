import { crops } from "@/data/crops";
import CropCard from "./CropCard";
import SectionHeader from "@/components/ui/SectionHeader";

interface CropGridProps {
  title?: string;
  subtitle?: string;
  limit?: number;
}

export default function CropGrid({
  title = "Explore Crop Library",
  subtitle = "Click any crop for detailed growing guides, disease prevention & smart farming tips",
  limit,
}: CropGridProps) {
  const displayCrops = limit ? crops.slice(0, limit) : crops;

  return (
    <div>
      <SectionHeader badge="🌾 Indian Crops" title={title} subtitle={subtitle} />
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {displayCrops.map((crop, i) => (
          <CropCard key={crop.id} crop={crop} index={i} />
        ))}
      </div>
    </div>
  );
}
