# 🌾 AgriSense — AI Crop Disease Detection Platform

> A production-quality, AI-powered crop disease detection and smart farming platform built with **Next.js 15**, **TypeScript**, **Tailwind CSS**, and **Framer Motion**. Designed for Indian farmers with multilingual support (English, Hindi, Bengali), live weather integration, and real-time market prices.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [API Integrations](#-api-integrations)
- [Pages & Routes](#-pages--routes)
- [Key Components](#-key-components)
- [Multilingual Support](#-multilingual-support)
- [Adding Real AI](#-replacing-mock-ai-with-real-ai)
- [Deployment](#-deployment)

---

## ✨ Features

| Feature | Status | Notes |
|---|---|---|
| AI Crop Disease Scan | ✅ | Mock pipeline — replace with Gemini/Qwen API |
| Animated AI Pipeline | ✅ | 5-step pipeline with glow animations |
| Chat-style Disease Result | ✅ | Confidence score, treatment, prevention |
| Crop Library (10 crops) | ✅ | Rice, Wheat, Potato, Tomato, Cotton, Maize, Sugarcane, Mustard, Onion, Chili |
| Individual Crop Detail Pages | ✅ | SSG — all 10 statically generated |
| Live Weather Advisory | ✅ | OpenWeatherMap API + geolocation |
| Crop-specific Weather Advisory | ✅ | Irrigation, disease risk, fertilizer timing |
| Live Market Prices | ✅ | Mock data (Agmarknet API ready) |
| AI Farming Chatbot | ✅ | Mock responses — swap in real LLM |
| Multilingual (EN / HI / BN) | ✅ | JSON locale files, client-side switching |
| Glassmorphism Navbar | ✅ | Sticky, blur, mobile hamburger menu |
| Responsive / Mobile-First | ✅ | Tested across breakpoints |
| Framer Motion Animations | ✅ | Page transitions, floating cards, scan flow |

---

## 🛠️ Tech Stack

- **Framework:** Next.js 15 (App Router, RSC + Client Components)
- **Language:** TypeScript
- **Styling:** Tailwind CSS v4
- **Animations:** Framer Motion
- **Icons:** Lucide React
- **Fonts:** Playfair Display (headings) + DM Sans (body) via Google Fonts
- **Weather:** OpenWeatherMap REST API
- **Hosting:** Vercel (recommended)

---

## 📁 Project Structure

```
agrisense/
├── app/                          # Next.js App Router pages
│   ├── layout.tsx                # Root layout — fonts, providers, Navbar
│   ├── globals.css               # Tailwind + custom utilities (glass, glow, float)
│   ├── page.tsx                  # Home page (Hero + Crops + Weather + Market)
│   ├── about/
│   │   └── page.tsx              # About page — team, features, tech stack
│   ├── assistant/
│   │   ├── page.tsx              # AI Chatbot page
│   │   └── AssistantClient.tsx   # Reads ?q= URL param for follow-up routing
│   ├── crops/
│   │   ├── page.tsx              # All crops listing
│   │   └── [id]/
│   │       ├── page.tsx          # SSG crop detail (generateStaticParams)
│   │       └── CropDetailClient.tsx  # Animated crop detail UI
│   └── weather/
│       └── page.tsx              # Weather + Market page
│
├── components/
│   ├── navbar/
│   │   └── Navbar.tsx            # Floating glassmorphism navbar
│   ├── hero/
│   │   └── HeroSection.tsx       # Hero heading + upload card layout
│   ├── scan/
│   │   ├── ImageUploadCard.tsx   # Upload / camera / drag-drop + state machine
│   │   ├── AIPipeline.tsx        # Animated 5-step AI pipeline
│   │   └── DiseaseResult.tsx     # Chat-bubble disease result UI
│   ├── crops/
│   │   ├── CropCard.tsx          # Single floating crop card
│   │   └── CropGrid.tsx          # 10-crop responsive grid
│   ├── weather/
│   │   └── WeatherSection.tsx    # Geolocation + weather cards + advisory
│   ├── market/
│   │   └── MarketSection.tsx     # Mandi price cards with trend indicators
│   ├── chatbot/
│   │   └── Chatbot.tsx           # Full conversational chatbot UI
│   └── ui/
│       ├── Button.tsx            # Reusable button (primary/secondary/white/ghost)
│       ├── GlassCard.tsx         # Glassmorphism card wrapper
│       └── SectionHeader.tsx     # Badge + title + subtitle header
│
├── data/
│   ├── crops.ts                  # Full data for all 10 Indian crops
│   ├── diseases.ts               # Mock disease results + follow-up responses
│   ├── market.ts                 # Market price mock data (8 crops)
│   └── chatbot.ts                # Chatbot response map + suggested prompts
│
├── lib/
│   ├── language-context.tsx      # React Context for EN/HI/BN language switching
│   ├── weather.ts                # OpenWeatherMap fetch + advisory generator
│   └── chatbot.ts                # Response matching logic + ID generator
│
├── locales/
│   ├── en.json                   # English translations
│   ├── hi.json                   # Hindi translations
│   └── bn.json                   # Bengali translations
│
├── types/
│   └── index.ts                  # TypeScript interfaces (Crop, WeatherData, etc.)
│
├── public/                       # Static assets
├── .env.local.example            # Environment variable template
├── next.config.ts
├── tsconfig.json
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites

- **Node.js** v18.17 or newer
- **npm** v9+ (or yarn / pnpm)

### 2. Clone the Repository

```bash
git clone https://github.com/your-username/agrisense.git
cd agrisense
```

### 3. Install Dependencies

```bash
npm install
```

### 4. Set Up Environment Variables

```bash
cp .env.local.example .env.local
```

Open `.env.local` and fill in your API key (see [Environment Variables](#-environment-variables)).

### 5. Run the Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 6. Build for Production

```bash
npm run build
npm start
```

---

## 🔑 Environment Variables

Create a `.env.local` file in the project root:

```env
# Required for live weather data
NEXT_PUBLIC_OPENWEATHER_API_KEY=your_key_here

# Optional — for live market prices (future)
# NEXT_PUBLIC_AGMARKNET_API_KEY=your_key_here
```

### Getting Your OpenWeatherMap API Key

1. Go to [https://openweathermap.org/api](https://openweathermap.org/api)
2. Click **Sign Up** (it's free)
3. After signup, go to **My API Keys** in your dashboard
4. Copy the default key (or generate a new one)
5. Paste it as `NEXT_PUBLIC_OPENWEATHER_API_KEY` in `.env.local`
6. **Free tier** allows 1,000 calls/day — more than sufficient

> **Without an API key:** The app still works — it automatically falls back to realistic mock weather data for Kolkata with a "Demo Data" badge shown to the user.

---

## 🌐 API Integrations

### Weather API — OpenWeatherMap

**File:** `lib/weather.ts`

```typescript
// Fetches weather by GPS coordinates (geolocation)
fetchWeatherByCoords(lat, lon)

// Fetches weather by city name
fetchWeatherByCity("Kolkata")

// Generates 5 crop-specific advisory cards from weather data
getWeatherAdvisory(weatherData, cropName)
```

The weather section automatically requests browser geolocation. If denied, it defaults to Kolkata coordinates.

### Market Prices — Agmarknet (Ready to Connect)

**File:** `data/market.ts` — Currently uses realistic mock data.

To connect the live Agmarknet / data.gov.in API:

1. Register at [https://data.gov.in](https://data.gov.in/catalogs/agriculture)
2. Get your API key
3. Create `lib/market.ts` with a fetch utility
4. Replace the static `marketPrices` array in `components/market/MarketSection.tsx` with a `useEffect` fetch call

Example API endpoint:
```
https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
  ?api-key=YOUR_KEY&format=json&filters[state.keyword]=Uttar Pradesh
```

---

## 📄 Pages & Routes

| Route | Type | Description |
|---|---|---|
| `/` | Static | Home — Hero scan, Crop grid, Weather, Market |
| `/crops` | Static | All 10 crops listing grid |
| `/crops/[id]` | SSG × 10 | Individual crop detail page |
| `/weather` | Static | Full weather advisory + market prices |
| `/assistant` | Static | AI Farming Chatbot (accepts `?q=` param) |
| `/about` | Static | About page — features, team, tech stack |

The `/crops/[id]` pages are **statically generated at build time** via `generateStaticParams()` — they load instantly with zero server cost.

---

## 🧩 Key Components

### `ImageUploadCard`
State machine with 4 stages: `idle → preview → pipeline → result`
- Drag-and-drop, file picker, camera capture
- Triggers `AIPipeline` animation then shows `DiseaseResult`

### `AIPipeline`
Receives a `currentStep: number` prop, animates each step with glow + processing states.

### `DiseaseResult`
Chat-bubble UI with animated confidence bar, disease chips, treatment/prevention grid, and follow-up question buttons that route to `/assistant?q=...`

### `WeatherSection`
Fully client-side, uses `useEffect` with `navigator.geolocation`. Falls back to mock data gracefully. The crop selector dropdown updates advisory cards without re-fetching weather.

### `Chatbot`
Full conversational UI with typing animation, message history, and suggested prompt chips. Accepts an optional `initialQuery` prop used by the `?q=` URL routing from the disease result follow-ups.

### `LanguageContext`
A React Context wrapping the entire app (`app/layout.tsx`). Call `useLanguage()` in any client component to get the current `t` (translations object) and `cycleLang()` function.

---

## 🌍 Multilingual Support

Locale files are in `locales/`:

```
locales/
├── en.json   # English (default)
├── hi.json   # Hindi
└── bn.json   # Bengali
```

**Adding a new language:**
1. Copy `locales/en.json` to `locales/te.json` (for Telugu, etc.)
2. Translate all values
3. In `lib/language-context.tsx`, add `"te"` to the `Language` type and `langs` array
4. Add `te: require("./locales/te.json")` to the `locales` map
5. Add `te: "తె"` to `langLabels`

---

## 🤖 Replacing Mock AI with Real AI

### Disease Detection (Gemini Vision API)

In `components/scan/ImageUploadCard.tsx`, replace the `runAnalysis()` function:

```typescript
async function runAnalysis() {
  setStage("pipeline");
  // ... run pipeline animation steps ...

  // Replace mock pick with real API call:
  const base64 = previewUrl!.split(",")[1];
  const response = await fetch("/api/detect", {
    method: "POST",
    body: JSON.stringify({ image: base64 }),
  });
  const data = await response.json();
  setResult(data);
  setStage("result");
}
```

Create `app/api/detect/route.ts` calling Gemini 2.5 Flash:
```typescript
import { GoogleGenAI } from "@google/generative-ai";
const genAI = new GoogleGenAI(process.env.GEMINI_API_KEY!);
```

### Chatbot (Real LLM)

In `lib/chatbot.ts`, replace `getAIResponse()` with a call to your `/api/chat` route using the Anthropic or Gemini SDK.

---

## 🚢 Deployment

### Vercel (Recommended — one command)

```bash
npx vercel --prod
```

Set environment variables in your Vercel dashboard under **Settings → Environment Variables**.

### Docker

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY . .
RUN npm ci && npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Other Platforms

The app is a standard Next.js app — it deploys to Netlify, Railway, Render, AWS Amplify, or any Node.js host. Run `npm run build && npm start`.

---

## 📜 Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start development server with hot reload |
| `npm run build` | Build optimized production bundle |
| `npm start` | Start production server |
| `npm run lint` | Run ESLint |

---

## 🪪 License

MIT — free for personal projects, hackathons, and startup MVPs.

---

**Built with 🌿 for Indian farmers** — AgriSense makes cutting-edge AI accessible in every field.
