"use client";

import { motion } from "framer-motion";
import { TrendingUp, TrendingDown } from "lucide-react";
import { marketPrices } from "@/data/market";
import SectionHeader from "@/components/ui/SectionHeader";

export default function MarketSection() {
  return (
    <section className="px-4 md:px-6 max-w-7xl mx-auto">
      <SectionHeader
        badge="📊 Market Prices"
        title="Live Mandi Prices"
        subtitle="Real-time crop prices from major agricultural markets across India"
      />

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
        {marketPrices.map((item, i) => {
          const up = item.change > 0;
          return (
            <motion.div
              key={item.crop}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.35, delay: i * 0.06 }}
              whileHover={{ y: -6, scale: 1.02 }}
              className="bg-white rounded-2xl p-5 border border-green-100 shadow-md hover:shadow-xl hover:shadow-green-900/10 transition-all duration-300"
            >
              <div className="text-4xl mb-3">{item.emoji}</div>
              <div className="font-serif font-semibold text-gray-800 text-base mb-0.5">{item.crop}</div>
              <div className="text-xs text-gray-400 mb-3 flex items-center gap-1">
                📍 {item.mandi}
              </div>
              <div className="font-serif text-2xl text-green-700 font-bold mb-1">
                ₹{item.price.toLocaleString("en-IN")}
              </div>
              <div className="text-xs text-gray-400 mb-2">{item.unit}</div>
              <div
                className={`inline-flex items-center gap-1 text-sm font-bold px-2.5 py-1 rounded-full ${
                  up ? "bg-green-50 text-green-700" : "bg-red-50 text-red-600"
                }`}
              >
                {up ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
                {up ? "+" : ""}
                {item.change}%
              </div>
            </motion.div>
          );
        })}
      </div>

      <p className="text-center text-xs text-gray-400 mt-6">
        Prices are indicative. For live data, connect Agmarknet or data.gov.in API in{" "}
        <code className="bg-gray-100 px-1 rounded">lib/market.ts</code>
      </p>
    </section>
  );
}
