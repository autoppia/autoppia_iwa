#!/bin/bash

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Configurable options
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8080}
WORKERS=${WORKERS:-4}
LOG_LEVEL=${LOG_LEVEL:-info}

# Calculate workers if auto
if [ "$WORKERS" = "auto" ]; then
    WORKERS=$(( $(nproc) * 2 + 1 ))
fi

# Validate database URL
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable not set" >&2
    exit 1
fi

# Run the server
exec uvicorn server:app \
    --host $HOST \
    --port $PORT \
    --workers $WORKERS \
    --log-level $LOG_LEVEL \
    --no-access-log \
    --timeout-keep-alive 30
