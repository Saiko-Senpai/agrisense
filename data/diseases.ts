import { DiseaseResult } from "@/types";

export const diseaseResults: DiseaseResult[] = [
  {
    disease: "Early Blight",
    pathogen: "Alternaria solani",
    confidence: 89,
    stage: "Moderate",
    text: `Based on my analysis, your crop shows signs of <strong>Early Blight</strong> — a fungal disease caused by <em>Alternaria solani</em>. I can see characteristic dark brown to black spots with yellow halos (target-board appearance) on the lower and older leaves. The infection pattern suggests this is at a moderate stage and action is needed within 3–5 days.`,
    treatment: [
      "Apply Mancozeb 75% WP @ 2.5 kg/ha in 500L water",
      "Spray Chlorothalonil 75% WP every 7–10 days",
      "Remove and destroy all visibly infected leaves",
      "Avoid overhead irrigation that wets foliage",
    ],
    prevention: [
      "Use certified disease-free seeds from trusted source",
      "Maintain proper plant spacing for air circulation",
      "Apply mulch to prevent soil splash onto leaves",
      "Rotate crops — avoid solanaceous crops for 2–3 years",
    ],
    chips: [
      { t: "Moderate Stage", c: "chip-yellow" },
      { t: "Fungal Disease", c: "chip-red" },
      { t: "Treatable", c: "chip-green" },
      { t: "Spread Risk: Medium", c: "chip-blue" },
    ],
  },
  {
    disease: "Late Blight",
    pathogen: "Phytophthora infestans",
    confidence: 94,
    stage: "Severe",
    text: `My analysis indicates <strong>Late Blight</strong> — caused by <em>Phytophthora infestans</em>, a devastating water mold. I can see water-soaked, greasy-looking lesions on leaves with white sporulation on the undersides in humid conditions. This is a high-urgency situation — Late Blight can destroy an entire crop within 7–10 days if left untreated.`,
    treatment: [
      "Apply Metalaxyl + Mancozeb (Ridomil Gold) immediately",
      "Spray Propamocarb hydrochloride @ 0.1% as systemic option",
      "Remove and bag heavily infected plant parts carefully",
      "Do not move equipment between fields without sanitizing",
    ],
    prevention: [
      "Plant resistant varieties (Kufri Jyoti, Kufri Bahar)",
      "Ensure excellent field drainage before planting",
      "Avoid overhead irrigation during cool humid periods",
      "Apply preventive copper-based fungicide at 10-day intervals",
    ],
    chips: [
      { t: "Severe Stage", c: "chip-red" },
      { t: "Water Mold", c: "chip-red" },
      { t: "Urgent Action", c: "chip-red" },
      { t: "High Spread Risk", c: "chip-blue" },
    ],
  },
  {
    disease: "Powdery Mildew",
    pathogen: "Erysiphe cichoracearum",
    confidence: 82,
    stage: "Early",
    text: `I've detected <strong>Powdery Mildew</strong> caused by <em>Erysiphe cichoracearum</em>. The white powdery coating I can observe on the leaf surfaces is characteristic of this fungal disease. You've caught this at an early stage — good news! Early intervention significantly improves treatment success.`,
    treatment: [
      "Apply Sulphur 80% WP @ 3 kg/ha as first-line treatment",
      "Spray Triadimefon 25% WP @ 0.05% for systemic control",
      "Remove severely infected leaves and dispose away from field",
      "Apply Karathane (Dinocap) in severe cases",
    ],
    prevention: [
      "Use powdery mildew resistant varieties where available",
      "Avoid excess nitrogen fertilization that promotes succulent growth",
      "Maintain good air circulation through proper spacing",
      "Apply preventive sulphur spray during dry spells",
    ],
    chips: [
      { t: "Early Stage", c: "chip-green" },
      { t: "Fungal Disease", c: "chip-yellow" },
      { t: "Good Prognosis", c: "chip-green" },
      { t: "Spread Risk: Low", c: "chip-blue" },
    ],
  },
];

export const followUpResponses: Record<string, string> = {
  spread:
    "Disease spread depends on weather conditions (humidity/temperature), crop variety susceptibility, proximity to infected plants, and vector populations. Create isolation zones and remove infected material promptly to contain the spread.",
  pesticide:
    "For fungal diseases: use Mancozeb (contact fungicide) or Propiconazole (systemic). For bacterial diseases: use Copper oxychloride 50% WP. Always follow label dosage, wear gloves and mask during application, and observe the pre-harvest interval.",
  organic:
    "Effective organic treatments include: Neem oil spray (3–5 ml/L water), Trichoderma viride bio-fungicide (10g/L), Pseudomonas fluorescens 1% WP, compost tea foliar spray, and garlic-chili extract (fermented for 7 days).",
  prevention:
    "Key prevention strategies: (1) Use certified disease-free seeds, (2) Crop rotation every 2–3 years, (3) Maintain optimal plant spacing for air circulation, (4) Balanced NPK fertilization — avoid excess nitrogen, (5) Regular field monitoring every 7 days.",
  dangerous:
    "Disease severity depends on the stage at detection. Early-stage infections are manageable with fungicides within 3–5 days. Late-stage infections can cause 40–80% yield loss. The disease detected in your crop requires prompt action — please begin treatment today.",
};
