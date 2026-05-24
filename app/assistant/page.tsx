import { Suspense } from "react";
import AssistantClient from "./AssistantClient";

export const metadata = { title: "AI Farming Assistant — AgriSense" };

export default function AssistantPage() {
  return (
    <div className="px-4 md:px-6 max-w-4xl mx-auto pt-10 pb-24">
      <div className="text-center mb-10">
        <span className="inline-flex items-center gap-2 bg-green-100 text-green-800 border border-green-200 px-4 py-1.5 rounded-full text-sm font-semibold mb-4">
          🤖 AI Assistant
        </span>
        <h2 className="text-3xl md:text-4xl font-serif text-green-800 mb-3">
          AgriSense AI Farming Assistant
        </h2>
        <p className="text-green-700/60 text-base max-w-xl mx-auto">
          Ask anything about crops, diseases, fertilizers, irrigation, and smart farming.
        </p>
      </div>
      <Suspense fallback={<div className="h-96 skeleton rounded-2xl" />}>
        <AssistantClient />
      </Suspense>
    </div>
  );
}
