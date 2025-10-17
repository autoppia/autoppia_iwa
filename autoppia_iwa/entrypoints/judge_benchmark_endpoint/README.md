# Judge Benchmark Endpoint (Web Voyager)

A FastAPI service to run Web Voyager benchmarks on real websites via a REST API. It accepts agent and task configuration, executes the benchmark, and returns results. Designed for easy integration and automation.

---

## Features

- **REST API** for triggering web agent benchmarks
- **CORS support** for cross-origin requests
- **Unique agent IDs** per request
- **PM2 deployment script** for robust process management
- **Flexible task selection**: custom URL+prompt or dataset-based

---

## API Usage

### Endpoint

`POST /test-judge-agent`

#### Request Body

- **Custom task mode** (recommended for quick tests):
  ```json
  {
    "url": "https://www.allrecipes.com/",
    "prompt": "Provide a recipe for vegetarian lasagna with more than 100 reviews and a rating of at least 4.5 stars suitable for 6 people.",
    "agent_host": "127.0.0.1",
    "agent_port": 5000,
    "agent_timeout": 250,
    "task_indices": [],
    "num_of_urls": 1
  }
  ```
- **Dataset selection mode**:
  ```json
  {
    "url": "",
    "prompt": "",
    "agent_host": "127.0.0.1",
    "agent_port": 5000,
    "agent_timeout": 250,
    "task_indices": [0, 2, 5],
    "num_of_urls": 0
  }
  ```
  Note: Here task_indices has priority over num_of_urls, if both are provided.

#### Response

```json
{
  "status": "success",
  "message": "Benchmark completed. See results in output directory."
}
```

---

## Quick Start

1. **Start your agent** (example: BrowserUse on `127.0.0.1:5000`).

2. **Run the endpoint locally:**
   ```bash
   pip install -r requirements.txt
   uvicorn autoppia_iwa.entrypoints.judge_benchmark_endpoint.app:app --host 0.0.0.0 --port 5070
   ```

3. **Send a request** (example using `curl`):
   ```bash
   curl -X POST http://localhost:5070/test-judge-agent \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://www.allrecipes.com/",
       "prompt": "Provide a recipe for vegetarian lasagna with more than 100 reviews and a rating of at least 4.5 stars suitable for 6 people.",
       "agent_host": "127.0.0.1",
       "agent_port": 5000,
       "agent_timeout": 250,
       "task_indices": [],
       "num_of_urls": 1
     }'
   ```

---

## Production Deployment (PM2)

Use the provided script for robust deployment:

```bash
./autoppia_iwa/entrypoints/judge_benchmark_endpoint/deploy_endpoint.sh [port]
```

- Default port: `5070`
- The service is named `judge-benchmark-[port]` in PM2

**Example:**
```bash
./autoppia_iwa/entrypoints/judge_benchmark_endpoint/deploy_endpoint.sh 5070
```

---

## Outputs

- Results (plots and JSON) are saved under `results/`
- Evaluation log: `real_web_evaluation.log` (at project root)
- Judge usage logs: `judge_tests_usage_logs.jsonl` (created automatically when LLM-based judges run)

---

## File Map

- `entrypoints/judge_benchmark_endpoint/app.py` — FastAPI app and endpoint
- `entrypoints/judge_benchmark_endpoint/deploy_endpoint.sh` — PM2 deployment script
- `entrypoints/judge_benchmark_endpoint/__init__.py` — package marker

---

## Notes

- Ensure your agent is running and reachable at the specified host/port.
- Task selection logic matches the code-first benchmark: use a custom URL+prompt or select from the dataset using `num_of_urls` or `task_indices`.
- For more details on the benchmark logic, see `entrypoints/judge_benchmark/README.md`.

---
