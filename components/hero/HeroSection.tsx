"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useLanguage } from "@/lib/language-context";
import Button from "@/components/ui/Button";
import ImageUploadCard from "@/components/scan/ImageUploadCard";

export default function HeroSection() {
  const { t } = useLanguage();

  return (
    <section className="px-4 md:px-6 pt-10 pb-16 max-w-7xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        {/* Left */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-2 bg-green-100 text-green-800 border border-green-200 px-4 py-2 rounded-full text-sm font-semibold mb-6"
          >
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            {t.hero.badge}
          </motion.div>

          <h1 className="text-4xl md:text-5xl lg:text-6xl font-serif text-green-800 leading-[1.1] mb-5">
            {t.hero.title.split("Crop").map((part, i) =>
              i === 0 ? (
                <span key={i}>{part}</span>
              ) : (
                <span key={i}>
                  <span className="text-amber-600">Crop</span>
                  {part}
                </span>
              )
            )}
          </h1>

          <p className="text-lg text-green-700/70 leading-relaxed mb-8 max-w-lg">
            {t.hero.subtitle}
          </p>

          <div className="flex flex-wrap gap-3">
            <Button
              variant="primary"
              size="lg"
              onClick={() =>
                document.getElementById("scan-section")?.scrollIntoView({ behavior: "smooth" })
              }
            >
              🔬 {t.hero.scanBtn}
            </Button>
            <Link href="/crops">
              <Button variant="secondary" size="lg">
                🌾 {t.hero.browseBtn}
              </Button>
            </Link>
          </div>

          {/* Stats row */}
          <div className="flex gap-8 mt-10 pt-8 border-t border-green-200/60">
            {[
              { val: "200+", label: "Diseases Detected" },
              { val: "10+", label: "Indian Crops" },
              { val: "94%", label: "Accuracy Rate" },
            ].map((s) => (
              <div key={s.label}>
                <div className="text-2xl font-serif font-bold text-green-700">{s.val}</div>
                <div className="text-xs text-green-600/60 mt-0.5">{s.label}</div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Right — Upload Card */}
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.15, ease: "easeOut" }}
          id="scan-section"
        >
          <ImageUploadCard />
        </motion.div>
      </div>
    </section>
  );
}
