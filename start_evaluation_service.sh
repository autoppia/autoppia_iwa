#!/bin/bash

# Startup script for the Evaluation Endpoint Service
# This service allows agents to quickly check if their solutions will pass tests

echo "=========================================="
echo "Starting Evaluation Endpoint Service"
echo "=========================================="
echo ""

# Default port
PORT=${1:-5060}

echo "Configuration:"
echo "  Port: $PORT"
echo "  Endpoint: http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop the service"
echo ""

# Start the service
python -m autoppia_iwa.entrypoints.evaluation_endpoint $PORT
