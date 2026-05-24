import { notFound } from "next/navigation";
import Link from "next/link";
import { crops } from "@/data/crops";
import type { Metadata } from "next";
import CropDetailClient from "./CropDetailClient";

interface Props {
  params: Promise<{ id: string }>;
}

export async function generateStaticParams() {
  return crops.map((c) => ({ id: c.id }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const crop = crops.find((c) => c.id === id);
  return {
    title: crop ? `${crop.name} — AgriSense Crop Library` : "Crop Not Found",
    description: crop?.intro,
  };
}

export default async function CropDetailPage({ params }: Props) {
  const { id } = await params;
  const crop = crops.find((c) => c.id === id);
  if (!crop) notFound();

  return <CropDetailClient crop={crop} />;
}
