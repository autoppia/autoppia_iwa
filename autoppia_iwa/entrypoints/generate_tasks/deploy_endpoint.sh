#!/bin/bash
# Deploy Tasks Generation Service with PM2
# Usage: ./deploy_service.sh [port]

PORT=${1:-5080}
SERVICE_NAME="generate-tasks-$PORT"

echo "🚀 Deploying Tasks Generation Service with PM2 on port $PORT..."
echo ""

# Stop existing service (if running)
pm2 delete "$SERVICE_NAME" >/dev/null 2>&1

source ./.venv/bin/activate

# Start new service
pm2 start "python -m autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint" \
  --name "$SERVICE_NAME" -- "$PORT"

# Save PM2 process list so it restarts on reboot
pm2 save
