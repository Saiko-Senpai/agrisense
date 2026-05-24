import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "About AgriSense" };

const features = [
  { icon: "🔬", title: "AI Disease Detection", desc: "Multi-model AI consensus using Gemini 2.5 Flash and Qwen 2.5 for highly accurate crop disease identification from a simple photo." },
  { icon: "🌤️", title: "Live Weather Advisory", desc: "Real-time OpenWeatherMap data integrated with crop-specific advice for irrigation, disease risk, and harvest timing." },
  { icon: "📊", title: "Market Price Tracker", desc: "Live mandi prices from across India so farmers can sell at the best time and at the best location." },
  { icon: "🗣️", title: "Multilingual Support", desc: "Available in English, Hindi, and Bengali — every farmer can access AI-powered farming intelligence in their own language." },
  { icon: "📱", title: "Mobile-First Design", desc: "Designed for smartphones with large touch targets and efficient layouts for rural connectivity conditions." },
  { icon: "🌱", title: "Crop Library", desc: "Detailed guides for 10+ major Indian crops covering diseases, prevention, fertilizers, weather risks, and best practices." },
];

const team = [
  { emoji: "👨‍🌾", name: "Arjun Sharma", role: "AI Research Lead", bg: "bg-green-50" },
  { emoji: "👩‍💻", name: "Priya Patel", role: "Frontend Architect", bg: "bg-blue-50" },
  { emoji: "🧑‍🔬", name: "Ravi Kumar", role: "Agricultural Expert", bg: "bg-amber-50" },
  { emoji: "👩‍🎨", name: "Meera Das", role: "UX Designer", bg: "bg-pink-50" },
];

const techStack = [
  { name: "Next.js 15", label: "App Router + RSC" },
  { name: "TypeScript", label: "Type Safety" },
  { name: "Framer Motion", label: "Animations" },
  { name: "Tailwind CSS", label: "Styling" },
  { name: "Gemini 2.5 Flash", label: "AI Vision (mock)" },
  { name: "Qwen 2.5 7B", label: "AI Text (mock)" },
  { name: "OpenWeatherMap", label: "Live Weather API" },
  { name: "Agmarknet", label: "Market Prices (ready)" },
];

export default function AboutPage() {
  return (
    <div className="px-4 md:px-6 max-w-6xl mx-auto pt-10 pb-24">
      {/* Hero */}
      <div className="rounded-3xl bg-gradient-to-br from-green-50 to-amber-50 border border-green-100 p-12 text-center mb-14">
        <div className="text-7xl mb-5">🌾</div>
        <h1 className="text-5xl font-serif text-green-800 mb-4">About AgriSense</h1>
        <p className="text-green-700/60 text-lg max-w-2xl mx-auto leading-relaxed">
          AI-powered crop disease detection and smart farming platform built for Indian farmers. Free, fast, and farmer-friendly.
        </p>
        <div className="flex gap-4 justify-center mt-8 flex-wrap">
          <Link href="/" className="px-6 py-3 bg-green-600 text-white rounded-full font-semibold text-sm hover:bg-green-500 transition-colors">
            🔬 Try AI Scan
          </Link>
          <Link href="/crops" className="px-6 py-3 bg-white border border-green-200 text-green-700 rounded-full font-semibold text-sm hover:bg-green-50 transition-colors">
            🌾 Crop Library
          </Link>
        </div>
      </div>

      {/* Mission */}
      <div className="bg-white rounded-2xl p-8 border border-green-100 shadow-md mb-10 text-center">
        <h2 className="text-2xl font-serif text-green-800 mb-4">Our Mission</h2>
        <p className="text-gray-600 leading-relaxed max-w-3xl mx-auto">
          India has over 150 million farming households. Most lack access to timely, accurate agricultural expertise. AgriSense bridges this gap by bringing AI-powered disease detection, real-time weather advisory, and live market intelligence to every farmer's smartphone — in their own language.
        </p>
      </div>

      {/* Features */}
      <h2 className="text-2xl font-serif text-green-800 text-center mb-6">Platform Features</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 mb-14">
        {features.map((f) => (
          <div key={f.title} className="bg-white rounded-2xl p-6 border border-green-100 shadow-md hover:shadow-lg transition-shadow">
            <div className="text-4xl mb-4">{f.icon}</div>
            <h3 className="font-serif text-green-800 text-lg mb-2">{f.title}</h3>
            <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </div>

      {/* Tech Stack */}
      <div className="bg-green-700 rounded-2xl p-8 mb-14">
        <h2 className="text-2xl font-serif text-white text-center mb-6">Technology Stack</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {techStack.map((t) => (
            <div key={t.name} className="bg-white/10 border border-white/20 rounded-xl p-4 text-center">
              <div className="font-bold text-white text-sm">{t.name}</div>
              <div className="text-green-200 text-xs mt-1">{t.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Team */}
      <h2 className="text-2xl font-serif text-green-800 text-center mb-6">Meet the Team</h2>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-5 mb-14">
        {team.map((m) => (
          <div key={m.name} className="bg-white rounded-2xl p-6 text-center border border-green-100 shadow-md">
            <div className={`w-16 h-16 rounded-full ${m.bg} flex items-center justify-center text-3xl mx-auto mb-3 border border-white shadow-sm`}>
              {m.emoji}
            </div>
            <div className="font-semibold text-gray-800 text-sm">{m.name}</div>
            <div className="text-gray-400 text-xs mt-0.5">{m.role}</div>
          </div>
        ))}
      </div>

      {/* CTA */}
      <div className="bg-gradient-to-r from-green-700 to-green-500 rounded-2xl p-8 text-center text-white">
        <h2 className="text-2xl font-serif mb-3">Ready to Transform Your Farming?</h2>
        <p className="text-green-100 mb-6">Upload your first crop photo and get AI-powered disease detection in seconds.</p>
        <Link href="/">
          <button className="px-8 py-3.5 bg-white text-green-700 font-bold rounded-full hover:-translate-y-1 hover:shadow-xl transition-all">
            🌱 Get Started Free
          </button>
        </Link>
      </div>
    </div>
  );
}
