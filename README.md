# 🏥 TriageAI

> AI-powered Emergency Room Triage System — Real-time severity assessment, dynamic priority queuing, and instant doctor alerts powered by Gemini 1.5 Flash.

## Architecture

```
Patient (Browser)  →  Intake Chat  →  FastAPI Backend  →  Gemini 1.5 Flash
                                            ↓
                                     ADK Agent Layer
                                     ├── Intake Agent
                                     ├── Diagnosis Agent
                                     ├── Priority Queue Agent
                                     └── Alert Agent
                                            ↓
Doctor Dashboard  ←  WebSocket  ← Dashboard Agent ← In-memory Store (SQLite)
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google API Key (Gemini 1.5 Flash access)

### 1. Clone & Setup
```bash
git clone <repo-url>
cd triageai

# Copy env file
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 2. Start Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. With Docker Compose
```bash
docker-compose up --build
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/intake` | Submit patient symptoms |
| `GET` | `/api/queue` | Get priority-sorted patient queue |
| `GET` | `/api/alerts` | Get active alerts |
| `GET` | `/api/patients/{id}` | Get patient details |
| `PATCH` | `/api/patients/{id}/status` | Update patient status |
| `WS` | `/ws/dashboard` | Live queue & alert stream |

## Severity Levels

| Level | Color | Description |
|-------|-------|-------------|
| 🔴 Critical | Red | Immediate life-threatening — treat NOW |
| 🟠 Urgent | Orange | Serious — treat within 15 minutes |
| 🟢 Minor | Green | Non-urgent — can wait |

## Deployment (Google Cloud Run)

```bash
# Build and push images
./deploy/deploy.sh

# Or use Cloud Build
gcloud builds submit --config deploy/cloudbuild.yaml
```

## Tech Stack

- **Backend**: FastAPI, Python 3.11, Uvicorn
- **AI**: Google Gemini 1.5 Flash, Google Generative AI SDK
- **Frontend**: React.js, Vite, Axios
- **Database**: In-memory store + SQLite
- **Infrastructure**: Docker, Google Cloud Run, GCR
