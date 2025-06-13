#!/bin/bash

HOST=0.0.0.0
PORT=8080
WORKERS=4
LOG_LEVEL=info

exec uvicorn server:app \
    --host $HOST \
    --port $PORT \
    --workers $WORKERS \
    --log-level $LOG_LEVEL \
    --no-access-log \
    --timeout-keep-alive 30
