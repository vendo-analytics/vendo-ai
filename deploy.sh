echo "Loading .env..."
set -a
source .env
set +a

echo "Environment variables loaded:"
echo "Project: $GOOGLE_CLOUD_PROJECT"
echo "Region: $GOOGLE_CLOUD_LOCATION"
echo "Service Name: $SERVICE_NAME"
echo "App Name: $APP_NAME"
echo "Agent Path: $AGENT_PATH"

# ------------------------------
# ✅ 2) Deploy with ADK to Cloud Run
# ------------------------------

echo "Deploying to Cloud Run..."

# Build with your Dockerfile
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/$SERVICE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \  --image gcr.io/$GOOGLE_CLOUD_PROJECT/$SERVICE_NAME \
  --region $GOOGLE_CLOUD_LOCATION \
  --allow-unauthenticated \
  --memory 4Gi \
  --set-env-vars \
GOOGLE_GENAI_USE_VERTEXAI=FALSE,\
GOOGLE_API_KEY=AIzaSyCWwBTu2VGBWnOrH4J6IT1E35CIAs4sL4E,\
OPENAI_API_KEY="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",\
MODEL_GEMINI="gemini-2.0-flash",\
MODEL_GPT_4O="openai/gpt-4o",\
GOOGLE_CLOUD_PROJECT=gam-dwh,\
FIREBASE_DB_URL=https://gam-dwh.firebaseio.com/,\
LANGFUSE_PUBLIC_KEY=pk-lf-71df995d-7f77-4463-887c-fac68c7a58d6,\
LANGFUSE_SECRET_KEY=sk-lf-60e3bbab-2498-4363-bd37-49240d4f2947,\
LANGFUSE_HOST=https://us.cloud.langfuse.com,\
SLACK_BOT_TOKEN=xoxb-730511548960-9084760827025-whoqhxTKY6b19o4GzIXGiGLp,\
SLACK_APP_TOKEN=xapp-1-A092SFAU4AC-9094525711712-8c31a7b09d82f268c0e0399f1be980c76be55f231a6f48d7ca59da2b95f26960,\ 
AGENT_PATH="./api/agents",\
NEXT_PUBLIC_API_BASE=https://vendoai-service-294500785221.us-central1.run.app,\
NEXT_PUBLIC_WS_URL=wss://vendoai-service-294500785221.us-central1.run.app