#!/bin/bash
# Start the Evaluation Service
# Usage: ./start_service.sh [port]

PORT=${1:-5060}

echo "🚀 Starting Evaluation Service on port $PORT..."
echo "📍 API will be available at: http://localhost:$PORT"
echo "📍 Health check: http://localhost:$PORT/health"
echo ""

python -m autoppia_iwa.entrypoints.evaluation.endpoint "$PORT"
