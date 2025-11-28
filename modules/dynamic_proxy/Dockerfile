FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PYTHONPATH=/app
ENV DYNAMIC_PROXY_CONFIG=/config/proxy_config.json

CMD ["python", "scripts/run_demo_web_proxy.py"]
