"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowLeft, Leaf } from "lucide-react";
import { Crop } from "@/types";
import Button from "@/components/ui/Button";

interface Props { crop: Crop }

const sections = [
  { key: "growing" as const, icon: "🌱", title: "Growing Conditions" },
  { key: "soil" as const, icon: "🏔️", title: "Soil Requirements" },
  { key: "diseases" as const, icon: "🦠", title: "Common Diseases" },
  { key: "prevention" as const, icon: "🛡️", title: "Prevention Methods" },
  { key: "fertilizer" as const, icon: "💊", title: "Fertilizer Guidance" },
  { key: "weather" as const, icon: "⛈️", title: "Weather Risks" },
];

export default function CropDetailClient({ crop }: Props) {
  return (
    <div className="px-4 md:px-6 max-w-6xl mx-auto pt-8 pb-24">
      {/* Back button */}
      <Link href="/crops">
        <Button variant="ghost" size="sm" className="mb-6">
          <ArrowLeft size={15} /> Back to Library
        </Button>
      </Link>

      {/* Hero */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-3xl p-10 text-center mb-10 relative overflow-hidden"
        style={{ background: `linear-gradient(135deg, ${crop.color}, #d8f3dc)` }}
      >
        <motion.div
          animate={{ y: [0, -12, 0] }}
          transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}
          className="text-9xl mb-5 drop-shadow-lg"
        >
          {crop.emoji}
        </motion.div>
        <h1 className="text-5xl font-serif text-green-800 mb-3">{crop.name}</h1>
        <p className="text-green-700/70 text-lg max-w-2xl mx-auto leading-relaxed mb-5">
          {crop.intro}
        </p>
        <div className="flex gap-3 justify-center flex-wrap">
          <span className="px-4 py-1.5 bg-white/70 text-green-800 rounded-full text-sm font-semibold border border-white/80 backdrop-blur-sm">
            {crop.season}
          </span>
          <span className="px-4 py-1.5 bg-white/70 text-green-800 rounded-full text-sm font-semibold border border-white/80 backdrop-blur-sm">
            📍 {crop.region}
          </span>
        </div>
      </motion.div>

      {/* Info grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
        {sections.map(({ key, icon, title }, i) => (
          <motion.div
            key={key}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.07 }}
            className="bg-white rounded-2xl p-6 border border-green-100 shadow-md"
          >
            <h3 className="font-serif font-semibold text-green-800 text-lg mb-4 flex items-center gap-2">
              <span>{icon}</span> {title}
            </h3>
            <ul className="space-y-2.5">
              {crop[key].map((item) => (
                <li key={item} className="flex items-start gap-2.5 text-sm text-gray-600 leading-relaxed">
                  <Leaf size={13} className="text-green-400 flex-shrink-0 mt-0.5" />
                  {item}
                </li>
              ))}
            </ul>
          </motion.div>
        ))}
      </div>

      {/* Best practices full width */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="bg-white rounded-2xl p-6 border border-green-100 shadow-md mb-8"
      >
        <h3 className="font-serif font-semibold text-green-800 text-lg mb-4 flex items-center gap-2">
          🚜 Farming Best Practices
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {crop.practices.map((item, i) => (
            <div key={item} className="flex items-start gap-3 bg-green-50 rounded-xl p-4 border border-green-100">
              <span className="w-7 h-7 rounded-full bg-green-600 text-white text-sm font-bold flex items-center justify-center flex-shrink-0">
                {i + 1}
              </span>
              <p className="text-sm text-gray-600 leading-relaxed">{item}</p>
            </div>
          ))}
        </div>
      </motion.div>

      {/* CTA */}
      <div className="bg-gradient-to-r from-green-700 to-green-500 rounded-2xl p-8 text-center text-white">
        <h2 className="text-2xl font-serif mb-3">Ask AI About {crop.name}</h2>
        <p className="text-green-100 mb-6">
          Get personalized disease diagnosis, treatment plans, and smart farming tips powered by AI.
        </p>
        <Link href={`/assistant?q=Tell me about ${crop.name} farming best practices`}>
          <Button variant="white" size="lg">🤖 Ask AgriSense AI</Button>
        </Link>
      </div>
    </div>
  );
}
