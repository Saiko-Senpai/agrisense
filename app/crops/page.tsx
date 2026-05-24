import CropGrid from "@/components/crops/CropGrid";

export const metadata = { title: "Crop Library — AgriSense" };

export default function CropsPage() {
  return (
    <div className="px-4 md:px-6 max-w-7xl mx-auto pt-10 pb-24">
      <CropGrid
        title="Crop Library"
        subtitle="Explore detailed information about major Indian crops — growing conditions, diseases, fertilizers, and best practices."
      />
    </div>
  );
}
