export interface Crop {
  id: string;
  name: string;
  emoji: string;
  color: string;
  season: string;
  region: string;
  intro: string;
  growing: string[];
  soil: string[];
  diseases: string[];
  prevention: string[];
  fertilizer: string[];
  weather: string[];
  practices: string[];
}

export interface DiseaseResult {
  disease: string;
  pathogen: string;
  confidence: number;
  stage: string;
  text: string;
  treatment: string[];
  prevention: string[];
  chips: { t: string; c: string }[];
  crop?: string;
}

export interface MarketPrice {
  crop: string;
  emoji: string;
  price: number;
  change: number;
  mandi: string;
  unit: string;
}

export interface WeatherData {
  name: string;
  main: {
    temp: number;
    humidity: number;
    feels_like: number;
    pressure: number;
  };
  weather: { description: string; icon: string }[];
  wind: { speed: number };
  visibility: number;
  mock?: boolean;
}

export interface Advisory {
  icon: string;
  title: string;
  text: string;
  type: "info" | "warn" | "danger";
}

export interface ChatMessage {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

export type Language = "en" | "hi" | "bn";
