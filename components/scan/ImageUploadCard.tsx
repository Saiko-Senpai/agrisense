"use client";

import { useState, useRef, DragEvent, ChangeEvent } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, Camera, Scan, X } from "lucide-react";
import { useLanguage } from "@/lib/language-context";
import Button from "@/components/ui/Button";
import AIPipeline from "@/components/scan/AIPipeline";
import DiseaseResult from "@/components/scan/DiseaseResult";
import { diseaseResults } from "@/data/diseases";
import { DiseaseResult as DiseaseResultType } from "@/types";

type Stage = "idle" | "preview" | "pipeline" | "result";

const PIPELINE_STEP_DURATION = 900; // ms per step

export default function ImageUploadCard() {
  const { t } = useLanguage();
  const fileRef = useRef<HTMLInputElement>(null);
  const camRef = useRef<HTMLInputElement>(null);
  const [stage, setStage] = useState<Stage>("idle");
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [pipelineStep, setPipelineStep] = useState(-1);
  const [result, setResult] = useState<DiseaseResultType | null>(null);
  const [dragging, setDragging] = useState(false);

  function loadFile(file: File) {
    if (!file.type.startsWith("image/")) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreviewUrl(e.target?.result as string);
      setStage("preview");
    };
    reader.readAsDataURL(file);
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) loadFile(file);
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) loadFile(file);
  }

  function reset() {
    setStage("idle");
    setPreviewUrl(null);
    setPipelineStep(-1);
    setResult(null);
  }

  async function runAnalysis() {
    setStage("pipeline");
    setPipelineStep(0);

    for (let i = 0; i <= 4; i++) {
      await new Promise((r) => setTimeout(r, PIPELINE_STEP_DURATION));
      setPipelineStep(i + 1);
    }

    await new Promise((r) => setTimeout(r, 400));
    const pick = diseaseResults[Math.floor(Math.random() * diseaseResults.length)];
    setResult(pick);
    setStage("result");
  }

  return (
    <div className="flex flex-col gap-5">
      {/* Upload zone */}
      <AnimatePresence mode="wait">
        {stage === "idle" && (
          <motion.div
            key="idle"
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.97 }}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all duration-300 cursor-pointer
              ${dragging
                ? "border-green-500 bg-green-50 scale-[1.02] shadow-lg"
                : "border-green-300 bg-white hover:border-green-400 hover:bg-green-50/50 hover:shadow-md"
              }`}
            onClick={() => fileRef.current?.click()}
          >
            <div className="text-6xl mb-4">🌱</div>
            <h3 className="text-xl font-serif text-green-800 mb-2">{t.upload.title}</h3>
            <p className="text-green-600/60 text-sm mb-6">{t.upload.subtitle}</p>
            <div className="flex gap-3 justify-center flex-wrap">
              <Button
                variant="primary"
                size="md"
                onClick={(e) => { e.stopPropagation(); camRef.current?.click(); }}
              >
                <Camera size={16} /> {t.upload.capture}
              </Button>
              <Button
                variant="secondary"
                size="md"
                onClick={(e) => { e.stopPropagation(); fileRef.current?.click(); }}
              >
                <Upload size={16} /> {t.upload.upload}
              </Button>
            </div>
            <p className="text-xs text-green-600/40 mt-4">{t.upload.dragDrop}</p>
            <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={handleFileChange} />
            <input ref={camRef} type="file" accept="image/*" capture="environment" className="hidden" onChange={handleFileChange} />
          </motion.div>
        )}

        {stage === "preview" && previewUrl && (
          <motion.div
            key="preview"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="bg-white rounded-2xl overflow-hidden border border-green-200 shadow-md"
          >
            <div className="relative">
              <img src={previewUrl} alt="Crop preview" className="w-full h-56 object-cover" />
              <button
                onClick={reset}
                className="absolute top-3 right-3 w-8 h-8 bg-black/50 text-white rounded-full flex items-center justify-center hover:bg-black/70 transition-colors"
              >
                <X size={14} />
              </button>
            </div>
            <div className="p-5 flex gap-3">
              <Button variant="primary" size="lg" className="flex-1" onClick={runAnalysis}>
                <Scan size={16} /> {t.upload.analyzeBtn}
              </Button>
              <Button variant="secondary" size="md" onClick={reset}>Reset</Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Pipeline */}
      <AnimatePresence>
        {(stage === "pipeline" || stage === "result") && (
          <motion.div
            key="pipeline"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <AIPipeline currentStep={pipelineStep} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Result */}
      <AnimatePresence>
        {stage === "result" && result && (
          <motion.div
            key="result"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <DiseaseResult result={result} onReset={reset} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
