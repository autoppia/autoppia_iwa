# syntax=docker/dockerfile:1

FROM mcr.microsoft.com/playwright/python:v1.46.0-jammy

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# Install system deps for demo webs (postgres client, git, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl && \
    rm -rf /var/lib/apt/lists/*

# Copy repo contents
COPY . /app

# Install Autoppia IWA in editable mode (installs demo webs + evaluator deps)
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e autoppia_iwa && \
    playwright install --with-deps chromium

# Default configuration (override via env vars in affinetes)
ENV IWA_AFFINE_TASKS_CACHE_DIR=/app/data/cache/tasks/affine_env \
    IWA_AFFINE_USE_CACHED_TASKS=true \
    IWA_AFFINE_PROJECT_IDS="" \
    PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "autoppia_iwa.affine_env.env:app", "--host", "0.0.0.0", "--port", "8000"]
