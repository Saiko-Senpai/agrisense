# AgriSense Backend

> AI-powered crop disease detection platform — FastAPI backend with dual Vision Language Model orchestration.

---

## Architecture Overview

```
Image Upload
    ↓
Image Validation & Preprocessing (Pillow)
    ↓
┌─────────────────────────────────┐
│  Gemini Vision  ║  Qwen Vision  │  ← Run CONCURRENTLY
└─────────────────────────────────┘
    ↓
Comparator Service (rapidfuzz fuzzy match)
    ↓
   MATCH?
  ┌──YES──────────────────────────────┐
  │  Pick higher-confidence result    │
  └───────────────────────────────────┘
  └──NO───────────────────────────────┐
     │  Consensus AI (Gemini 1.5 Pro) │
     └────────────────────────────────┘
    ↓
Structured JSON Response
```

---

## Tech Stack

| Component        | Technology                         |
|------------------|------------------------------------|
| Framework        | FastAPI + Uvicorn                  |
| Models           | Pydantic v2                        |
| Vision Model 1   | Google Gemini 1.5 Flash/Pro        |
| Vision Model 2   | Qwen-VL-Max (Alibaba DashScope)    |
| Consensus AI     | Google Gemini 1.5 Pro              |
| Fuzzy Matching   | rapidfuzz                          |
| Image Processing | Pillow                             |
| HTTP Client      | httpx (async)                      |

---

## Folder Structure

```
backend/
├── api/
│   └── routes/
│       ├── analyze.py       # POST /analyze — image upload + diagnosis
│       ├── chat.py          # POST /chat — agricultural chatbot
│       └── health.py        # GET /health — health check
├── services/
│   ├── gemini_service.py    # Gemini Vision API wrapper
│   ├── qwen_service.py      # Qwen Vision API wrapper
│   ├── comparator_service.py # Fuzzy match comparator
│   ├── consensus_service.py # Consensus AI arbitration
│   ├── diagnosis_service.py # Central pipeline orchestrator
│   └── chatbot_service.py   # Agricultural chatbot
├── utils/
│   ├── prompts.py           # All prompt engineering
│   ├── parser.py            # JSON extraction + validation
│   ├── validators.py        # Image upload validation
│   └── image_utils.py       # PIL preprocessing + base64
├── models/
│   ├── request_models.py    # Pydantic request schemas
│   └── response_models.py   # Pydantic response schemas
├── uploads/                 # Temporary image storage
├── .env                     # Environment variables
├── requirements.txt
├── main.py                  # FastAPI application entry point
└── README.md
```

---

## Setup Instructions

### 1. Prerequisites

- Python 3.11+
- pip or conda

### 2. Clone and Navigate

```bash
cd backend
```

### 3. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Copy `.env` and fill in your API keys:

```bash
cp .env .env.local
```

Edit `.env`:

```env
GEMINI_API_KEY=your_google_gemini_api_key
QWEN_API_KEY=your_alibaba_dashscope_api_key
CONSENSUS_API_KEY=your_consensus_model_key   # Can reuse GEMINI_API_KEY
```

#### Getting API Keys

| Service | URL |
|---------|-----|
| Gemini  | https://aistudio.google.com/app/apikey |
| Qwen (DashScope) | https://dashscope.aliyun.com/ |

### 6. Run the Server

**Development (with hot reload):**
```bash
python main.py
```

**Or with uvicorn directly:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## API Endpoints

### `GET /health`

Liveness and readiness check.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "uptime_seconds": 42.1,
  "version": "1.0.0",
  "services": {
    "gemini": "configured",
    "qwen": "configured",
    "consensus": "configured"
  }
}
```

---

### `POST /analyze`

Upload a crop image for disease detection.

```bash
curl -X POST http://localhost:8000/analyze \
  -F "image=@/path/to/crop_photo.jpg"
```

**Response:**
```json
{
  "success": true,
  "request_id": "a3f2c1b4",
  "data": {
    "disease": "Late Blight",
    "pathogen": "Phytophthora infestans",
    "confidence": 94,
    "stage": "Severe",
    "description": "Late blight is a devastating oomycete disease...",
    "treatment": [
      "Apply Metalaxyl + Mancozeb (Ridomil Gold) immediately",
      "Remove and destroy heavily infected plant parts",
      "Avoid moving equipment between fields"
    ],
    "prevention": [
      "Plant resistant varieties (Kufri Jyoti, Kufri Bahar)",
      "Ensure excellent field drainage before planting",
      "Apply preventive copper-based fungicide at 10-day intervals"
    ],
    "chips": [
      { "t": "Severe Stage", "c": "chip-red" },
      { "t": "High Confidence", "c": "chip-green" },
      { "t": "Gemini Verified", "c": "chip-blue" },
      { "t": "High Spread Risk", "c": "chip-red" }
    ],
    "source": "gemini",
    "similarity_score": 88.5,
    "matched": true
  }
}
```

---

### `POST /chat`

Ask the agricultural AI assistant a question.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the best organic treatment for late blight?",
    "crop_context": "potato",
    "disease_context": "Late Blight",
    "conversation_history": []
  }'
```

**Response:**
```json
{
  "success": true,
  "request_id": "b1d4e2f7",
  "data": {
    "reply": "For organic management of Late Blight on potatoes, I recommend...",
    "is_agriculture_related": true,
    "crop_context": "potato",
    "disease_context": "Late Blight"
  }
}
```

---

## Environment Variables Reference

| Variable              | Default                              | Description                               |
|-----------------------|--------------------------------------|-------------------------------------------|
| `GEMINI_API_KEY`      | —                                    | Google Gemini API key (required)          |
| `QWEN_API_KEY`        | —                                    | Alibaba DashScope API key (required)      |
| `CONSENSUS_API_KEY`   | Falls back to `GEMINI_API_KEY`       | Consensus model API key                   |
| `QWEN_BASE_URL`       | `https://dashscope.aliyuncs.com/...` | Qwen OpenAI-compatible endpoint           |
| `QWEN_MODEL`          | `qwen-vl-max`                        | Qwen model name                           |
| `CONSENSUS_MODEL`     | `gemini-1.5-pro`                     | Consensus LLM model name                  |
| `GEMINI_MODEL`        | `gemini-1.5-flash`                   | Gemini model for vision + chat            |
| `MATCH_THRESHOLD`     | `75`                                 | Fuzzy match score (0–100) for VLM agreement |
| `MAX_IMAGE_SIZE_MB`   | `10`                                 | Maximum upload size in megabytes          |
| `HOST`                | `0.0.0.0`                            | Server bind address                       |
| `PORT`                | `8000`                               | Server port                               |
| `ENV`                 | `development`                        | `development` enables hot reload          |
| `ALLOWED_ORIGINS`     | `http://localhost:3000`              | Comma-separated CORS allowed origins      |

---

## Interactive API Docs

Once running, access the auto-generated Swagger UI:

```
http://localhost:8000/docs
```

ReDoc UI:
```
http://localhost:8000/redoc
```
