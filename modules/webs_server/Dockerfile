# Stage 1: Build environment
FROM python:3.9-slim AS builder

WORKDIR /app
COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev
RUN pip install --user -r requirements.txt

# Stage 2: Runtime environment
FROM python:3.9-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY ./src .
COPY ./scripts/ .

RUN chmod +x ./run_api.sh

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

EXPOSE 8080

ENTRYPOINT ["./run_api.sh"]
