#!/bin/bash
# TriageAI – Google Cloud Run Deployment Script
# Usage: ./deploy/deploy.sh

set -e

# ── Configuration ─────────────────────────────────────────────────────────────
GCP_PROJECT_ID="${GCP_PROJECT_ID:-your-gcp-project-id}"
GCR_HOSTNAME="${GCR_HOSTNAME:-gcr.io}"
REGION="${REGION:-us-central1}"
BACKEND_SERVICE="triageai-backend"
FRONTEND_SERVICE="triageai-frontend"

# ── Colors ────────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🏥 TriageAI Deployment starting...${NC}"
echo "Project: $GCP_PROJECT_ID | Region: $REGION"

# ── Build & Push Backend ──────────────────────────────────────────────────────
echo -e "${YELLOW}[1/4] Building backend image...${NC}"
BACKEND_IMAGE="$GCR_HOSTNAME/$GCP_PROJECT_ID/$BACKEND_SERVICE:latest"
docker build -t "$BACKEND_IMAGE" ./backend
docker push "$BACKEND_IMAGE"
echo -e "${GREEN}✅ Backend image pushed: $BACKEND_IMAGE${NC}"

# ── Build & Push Frontend ─────────────────────────────────────────────────────
echo -e "${YELLOW}[2/4] Building frontend image...${NC}"
FRONTEND_IMAGE="$GCR_HOSTNAME/$GCP_PROJECT_ID/$FRONTEND_SERVICE:latest"
docker build -t "$FRONTEND_IMAGE" ./frontend
docker push "$FRONTEND_IMAGE"
echo -e "${GREEN}✅ Frontend image pushed: $FRONTEND_IMAGE${NC}"

# ── Deploy Backend to Cloud Run ───────────────────────────────────────────────
echo -e "${YELLOW}[3/4] Deploying backend to Cloud Run...${NC}"
gcloud run deploy "$BACKEND_SERVICE" \
  --image "$BACKEND_IMAGE" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "GOOGLE_API_KEY=${GOOGLE_API_KEY},SEED_DEMO_PATIENTS=true" \
  --project "$GCP_PROJECT_ID"

BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE" \
  --region "$REGION" --project "$GCP_PROJECT_ID" \
  --format 'value(status.url)')
echo -e "${GREEN}✅ Backend deployed: $BACKEND_URL${NC}"

# ── Deploy Frontend to Cloud Run ──────────────────────────────────────────────
echo -e "${YELLOW}[4/4] Deploying frontend to Cloud Run...${NC}"
WS_URL=$(echo "$BACKEND_URL" | sed 's/https/wss/')
gcloud run deploy "$FRONTEND_SERVICE" \
  --image "$FRONTEND_IMAGE" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --port 80 \
  --memory 256Mi \
  --set-env-vars "VITE_API_BASE_URL=${BACKEND_URL},VITE_WS_URL=${WS_URL}/ws/dashboard" \
  --project "$GCP_PROJECT_ID"

FRONTEND_URL=$(gcloud run services describe "$FRONTEND_SERVICE" \
  --region "$REGION" --project "$GCP_PROJECT_ID" \
  --format 'value(status.url)')

echo ""
echo -e "${GREEN}🚀 TriageAI deployed successfully!${NC}"
echo -e "  Frontend: ${GREEN}$FRONTEND_URL${NC}"
echo -e "  Backend:  ${GREEN}$BACKEND_URL${NC}"
echo -e "  API Docs: ${GREEN}$BACKEND_URL/docs${NC}"
