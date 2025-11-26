FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    SKIP_APP_BOOTSTRAP=1

WORKDIR /app

# System deps for Playwright/Chromium
RUN apt-get update && \
    apt-get install -y --no-install-recommends chromium wget ca-certificates fonts-liberation libnss3 && \
    rm -rf /var/lib/apt/lists/*

# Copy project code
COPY . /app

# Install python deps (autoppia_iwa + server)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir sb3-contrib && \
    pip install --no-cache-dir ./autoppia_iwa fastapi uvicorn[standard] && \
    python -m playwright install chromium

EXPOSE 8000

CMD ["uvicorn", "autoppia_iwa.affine_service.server:app", "--host", "0.0.0.0", "--port", "8000"]
