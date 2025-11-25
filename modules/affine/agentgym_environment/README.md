# Affine AgentGym Environment for IWA

This module packages the `autoppia_iwa` validator stack as an AgentGym-compatible
environment so Affine miners can train/evaluate web agents that operate on the
Autoppia demo applications.

## Layout

```
autoppia_iwa/affine_env/
├── agent_client.py     # Talks to miner `/solve_task` endpoints
├── config.py           # Environment configuration + env-var overrides
├── dataset.py          # Loads & indexes cached tasks for AgentGym ids
├── evaluator.py        # Wraps ConcurrentEvaluator to score TaskSolutions
├── env.py              # FastAPI app (uvicorn entrypoint) with /evaluate
├── prepare_tasks.py    # Helper script to pre-generate cached tasks
├── Dockerfile          # Container recipe for affinetes/AgentGym
└── README.md
```

## Usage

1. **Generate task cache (optional but recommended):**

   ```bash
   export IWA_AFFINE_PROJECT_IDS="autocinema,autobooks,autowork"
   export IWA_AFFINE_TASKS_CACHE_DIR="data/cache/tasks/affine_env"
   python -m autoppia_iwa.affine_env.prepare_tasks
   ```

   The script reuses the standard benchmark generation pipeline; if
   `IWA_AFFINE_USE_CACHED_TASKS=true`, the HTTP server will only read these
   cached JSON files during runtime.

2. **Run the HTTP server locally:**

   ```bash
   uvicorn autoppia_iwa.affine_env.env:app --host 0.0.0.0 --port 8000
   ```

   The `/health` endpoint returns a quick status, while `/evaluate` exposes the
   AgentGym-compatible contract used by Affinetes. Requests should include the
   miner `model` (metadata) and `base_url` (Chutes endpoint exposing the
   `/solve_task` API). When `ids` are omitted, the server samples a handful of
   cached tasks per request and records pass/fail statistics identical to the
   Autoppia validator.

3. **Build a container for Affine:**

   ```bash
   docker build \
     -f autoppia_iwa/affine_env/Dockerfile \
     -t your-registry/iwa-agentgym:latest \
     .
   ```

   The Dockerfile installs Playwright dependencies, the demo web projects, and
   the FastAPI server. Push the resulting image to a registry accessible by the
   Affine validators, then register it as an AgentGym environment.

## Environment Variables

| Variable | Description | Default |
| --- | --- | --- |
| `IWA_AFFINE_PROJECT_IDS` | Comma-separated demo web ids to expose | First 3 demo projects |
| `IWA_AFFINE_TASKS_CACHE_DIR` | Directory for cached tasks | `data/cache/tasks/affine_env` |
| `IWA_AFFINE_PROMPTS_PER_USE_CASE` | Prompts per use case when (re)generating tasks | `2` |
| `IWA_AFFINE_NUM_USE_CASES` | Use cases per project | `3` |
| `IWA_AFFINE_ENABLE_DYNAMIC_HTML` | Enable deterministic seed insertion | `false` |
| `IWA_AFFINE_USE_CACHED_TASKS` | Skip live generation and only read cache | `true` |
| `IWA_AFFINE_AGENT_TIMEOUT` | Timeout for miner `/solve_task` calls (seconds) | `180` |
| `IWA_AFFINE_BROWSER_TIMEOUT` | Playwright timeout per evaluation (seconds) | `120` |
| `IWA_AFFINE_MAX_TASKS_PER_EVAL` | Default number of tasks per `/evaluate` | `3` |
| `IWA_AFFINE_RECORD_GIF` | Store GIFs during scoring | `false` |
| `IWA_AFFINE_VERBOSE_LOGS` | Enable verbose evaluator logging | `false` |

Set these variables at build time (for baked defaults) or runtime (when
affinetes launches the container).

## API Contract

```
POST /evaluate
{
  "model": "hf-user/iwa-agent",
  "base_url": "https://<slug>.chutes.ai/v1",
  "ids": [12, 48, 73],      # optional – otherwise the server samples tasks
  "max_tasks": 3            # optional – ignored when ids are supplied
}
```

Response:

```
{
  "environment": "autoppia_iwa_agentgym",
  "total_score": 2.5,
  "success_rate": 0.66,
  "evaluated": 3,
  "dataset_size": 120,
  "project_ids": ["autocinema", "..."],
  "details": [
    {
      "affine_id": 12,
      "task_id": "uuid",
      "project_id": "autocinema",
      "score": 1.0,
      "success": true,
      "tests_passed": 4,
      "total_tests": 4,
      ...
    }
  ]
}
```

Affine validators only need the `total_score` and `success_rate`, while the
`details` array provides rich telemetry for debugging miners and publishing
analytics.

## Live Miner Smoke Test

The repo ships with an integration test that pings the deployed miner exposed in
`autoppia_iwa.autoppia_iwa.entrypoints.benchmark.run` (default
`http://84.247.180.192:6789`).

```bash
pytest autoppia_iwa/affine_env/tests/test_remote_agent.py
```

Override the target endpoint via `AUTOPPIA_REMOTE_AGENT_BASE_URL` if needed. The
test automatically skips when the miner is offline, but when it is reachable it
ensures the `/info` endpoint works and that `RemoteAgentClient` can fetch a
`TaskSolution` for a demo task. Use it after every deployment to confirm the
Affine environment can talk to the live miner.
