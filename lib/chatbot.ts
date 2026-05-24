import { chatResponses } from "@/data/chatbot";

export function getAIResponse(query: string): string {
  const q = query.toLowerCase();

  const matchOrder = [
    "blast",
    "blight",
    "pesticide",
    "organic",
    "fertilizer",
    "irrigation",
    "disease",
    "weather",
    "harvest",
  ];

  for (const key of matchOrder) {
    if (q.includes(key)) {
      const responses = chatResponses[key];
      return responses[Math.floor(Math.random() * responses.length)];
    }
  }

  // Check for crop names
  const cropKeywords = [
    "rice",
    "wheat",
    "potato",
    "tomato",
    "cotton",
    "maize",
    "corn",
    "sugarcane",
    "mustard",
    "onion",
    "chili",
    "chilli",
  ];
  for (const crop of cropKeywords) {
    if (q.includes(crop)) {
      return `For ${crop} farming, I recommend: (1) Use certified seeds from a reliable source, (2) Monitor regularly for early disease signs, (3) Apply balanced NPK fertilization based on soil test, (4) Use integrated pest management to reduce chemical use. What specific aspect of ${crop} cultivation would you like to know more about?`;
    }
  }

  const defaults = chatResponses["default"];
  return defaults[Math.floor(Math.random() * defaults.length)];
}

export function generateId(): string {
  return Math.random().toString(36).substring(2, 9);
}
