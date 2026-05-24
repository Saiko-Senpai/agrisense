export const chatResponses: Record<string, string[]> = {
  blast: [
    "Rice Blast is caused by the fungus *Magnaporthe oryzae*. Look for diamond-shaped gray lesions with dark brown borders on leaves. Apply Tricyclazole 75% WP @ 0.6 g/L water. Use resistant varieties like Pusa Basmati 1509 or IR-64 for long-term prevention.",
    "For blast control, maintain proper water management (alternate wetting and drying), avoid excess nitrogen which increases plant susceptibility, and spray Isoprothiolane 40% EC @ 1.5 ml/L water as a curative measure.",
  ],
  blight: [
    "Late Blight caused by *Phytophthora infestans* is an emergency — it can destroy your crop in 7–10 days. Apply Metalaxyl + Mancozeb (Ridomil Gold) immediately. Remove and destroy infected material. Avoid moving equipment between fields.",
    "For Early Blight (*Alternaria solani*), spray Mancozeb 75% WP @ 2.5 kg/ha every 7–10 days. Remove lower infected leaves. Avoid overhead irrigation. Use resistant tomato and potato varieties.",
  ],
  pesticide: [
    "For fungal diseases: Mancozeb (contact), Propiconazole (systemic), Metalaxyl (oomycetes). For bacterial diseases: Copper oxychloride 50% WP. For viral diseases: control vectors (aphids/whiteflies) with Imidacloprid 17.8% SL @ 0.25 ml/L.",
    "Always follow the label dosage strictly. Wear full protective equipment during application. Observe pre-harvest intervals — typically 7–14 days depending on the chemical. Rotate fungicides to prevent resistance.",
  ],
  organic: [
    "Organic treatment options: Neem oil spray (3–5 ml/L water), Trichoderma viride bio-fungicide (10 g/L), Pseudomonas fluorescens 1% WP, compost tea foliar spray. These work best as preventives or in early disease stages.",
    "For organic pest control: use yellow sticky traps for whiteflies, pheromone traps for bollworms, release Trichogramma cards for egg parasitism, and apply Beauveria bassiana 1.15% WP @ 4 g/L for insect control.",
  ],
  fertilizer: [
    "Balanced nutrition improves crop immunity. Avoid excess nitrogen — it promotes succulent, disease-susceptible growth. Apply potassium for disease resistance. Micronutrients like Zinc (ZnSO₄ 25 kg/ha) and Boron (borax 5 kg/ha) boost plant immunity.",
    "For soil health: apply FYM (farmyard manure) 10 tonnes/ha before sowing. Use bio-fertilizers — Rhizobium for legumes, Azotobacter for cereals. Vermicompost improves soil structure and beneficial microbial population.",
  ],
  irrigation: [
    "Irrigation best practices: use drip irrigation to keep foliage dry and reduce disease. Irrigate in the morning so leaves dry during the day. Avoid waterlogging — maintain 70–80% field capacity. Critical stages needing water: germination, flowering, grain/fruit fill.",
    "Drip irrigation can reduce water use by 40–60% while improving yield. Place drippers at root zone, 30–40 cm spacing. Fertigation through drip delivers nutrients efficiently — 30% savings on fertilizer costs.",
  ],
  disease: [
    "Common crop diseases to watch for: (1) Fungal — blight, mildew, rust, smut. (2) Bacterial — wilt, canker, blight. (3) Viral — mosaic, leaf curl, streak. (4) Nematodes — root knot. Early detection and action is the key to saving your crop.",
  ],
  weather: [
    "Weather affects crop disease significantly: high humidity (>80%) promotes fungal diseases, warm nights with cool days favor rust diseases, and waterlogging promotes root rots. Monitor the weather advisory on AgriSense for crop-specific alerts.",
  ],
  harvest: [
    "Harvest at the right time to maximize quality and price. Rice: when 80% grains turn golden. Wheat: grain moisture 12–14%. Tomato: full red for fresh market, firm-ripe for transport. Post-harvest losses account for 10–30% — proper storage is critical.",
  ],
  default: [
    "I can help you with crop disease identification, treatment methods, organic farming, irrigation planning, fertilizer management, pest control, and market advice. Please describe your specific problem or mention a crop name for tailored guidance.",
    "As your AI farming assistant, I cover over 200 crop diseases and all major Indian crops. Ask me about symptoms you observe, and I'll help identify the disease and recommend appropriate treatment and prevention strategies.",
    "For the best advice, try telling me: (1) which crop you're growing, (2) what symptoms you see (spots, wilting, color change), and (3) how long the symptoms have been visible. This helps me give you more accurate recommendations.",
  ],
};

export const suggestedPrompts = [
  "What is rice blast disease?",
  "Best fertilizer for wheat?",
  "How to treat late blight?",
  "Organic pest control methods?",
  "Irrigation best practices?",
  "How to prevent powdery mildew?",
  "When to harvest tomatoes?",
  "Symptoms of nitrogen deficiency?",
];
