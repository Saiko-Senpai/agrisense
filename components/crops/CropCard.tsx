"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Crop } from "@/types";

interface CropCardProps {
  crop: Crop;
  index?: number;
}

export default function CropCard({ crop, index = 0 }: CropCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.4, delay: index * 0.05 }}
      whileHover={{ y: -8, scale: 1.02 }}
    >
      <Link href={`/crops/${crop.id}`} className="block">
        <div className="bg-white rounded-2xl overflow-hidden border border-green-100 shadow-md hover:shadow-xl hover:shadow-green-900/15 transition-all duration-300 cursor-pointer">
          {/* Image area */}
          <div
            className="h-36 flex items-center justify-center text-7xl relative overflow-hidden"
            style={{ background: crop.color }}
          >
            <motion.span
              animate={{ y: [0, -6, 0] }}
              transition={{ duration: 3 + index * 0.3, repeat: Infinity, ease: "easeInOut" }}
              className="drop-shadow-md"
            >
              {crop.emoji}
            </motion.span>
          </div>

          {/* Body */}
          <div className="p-4">
            <h3 className="font-serif font-semibold text-green-800 text-base mb-2">{crop.name}</h3>
            <div className="flex gap-2 flex-wrap">
              <span className="px-2.5 py-0.5 bg-green-50 text-green-700 border border-green-200 rounded-full text-xs font-semibold">
                {crop.season}
              </span>
              <span className="px-2.5 py-0.5 bg-amber-50 text-amber-700 border border-amber-200 rounded-full text-xs font-medium">
                {crop.region}
              </span>
            </div>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}
