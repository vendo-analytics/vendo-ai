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

adk deploy cloud_run \
  --project="$GOOGLE_CLOUD_PROJECT" \
  --region="$GOOGLE_CLOUD_LOCATION" \
  --service_name="$SERVICE_NAME" \
  --app_name="$APP_NAME" \
  "$AGENT_PATH"
echo "✅ Deploy complete! 🚀"