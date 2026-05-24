"use client";

import { motion } from "framer-motion";

const STEPS = [
  { icon: "📸", label: "Image Upload", sub: "Processing image data" },
  { icon: "⚡", label: "LLama 3.2 Vision", sub: "Visual pattern recognition" },
  { icon: "🧠", label: "Qwen 2.5 Instruct 7B", sub: "Disease classification" },
  { icon: "✅", label: "Consensus Verification", sub: "Cross-model validation" },
  { icon: "💊", label: "Final Diagnosis", sub: "Treatment plan generation" },
];

interface AIPipelineProps {
  currentStep: number; // 0-indexed; -1 = not started; 5+ = all done
}

export default function AIPipeline({ currentStep }: AIPipelineProps) {
  return (
    <div className="bg-white rounded-2xl p-6 border border-green-100 shadow-md">
      <h3 className="text-base font-serif text-green-800 text-center mb-5 font-semibold">
        🤖 AI Analysis Pipeline
      </h3>
      <div className="flex flex-col gap-0">
        {STEPS.map((step, idx) => {
          const isDone = currentStep > idx;
          const isActive = currentStep === idx;

          return (
            <div key={idx}>
              <motion.div
                animate={isActive ? { backgroundColor: "#f0fdf4" } : {}}
                className={`flex items-center gap-3 p-3 rounded-xl transition-all duration-300 ${
                  isActive ? "bg-green-50 shadow-sm" : isDone ? "opacity-75" : ""
                }`}
              >
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-lg flex-shrink-0 transition-all duration-300
                    ${isActive ? "bg-green-600 text-white animate-glow" : isDone ? "bg-green-400 text-white" : "bg-gray-100"}`}
                >
                  {step.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold text-gray-800">{step.label}</div>
                  <div className="text-xs text-gray-400 truncate">{step.sub}</div>
                </div>
                <div className="text-xs font-semibold ml-auto flex-shrink-0">
                  {isDone && <span className="text-green-600">✓ Done</span>}
                  {isActive && (
                    <span className="text-amber-500 animate-pulse">Processing…</span>
                  )}
                </div>
              </motion.div>
              {idx < STEPS.length - 1 && (
                <div className={`text-center text-lg leading-4 py-0.5 transition-colors duration-300 ${isDone ? "text-green-400" : "text-gray-200"}`}>
                  ↓
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
