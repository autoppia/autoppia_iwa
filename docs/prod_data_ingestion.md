# Prod Task/Solution Ingestion

Use this guide to mirror production task activity into the local reward-model
dataset. The workflow is:

1. Fetch tasks + solutions from the production API into `data/rm/raw_evaluations/`.
2. Run the usual reward-model builders (`make_splits.py`, `build_obs_and_labels.py`, etc.).

## API access

```
BASE_URL = https://<host>/api           # configure via AUTOPPIA_PROD_BASE_URL
TOKEN    = <Bearer token>               # configure via AUTOPPIA_PROD_API_TOKEN
```

| Header            | Value                          |
|-------------------|--------------------------------|
| `Authorization`   | `Bearer <TOKEN>`               |
| `Content-Type`    | `application/json`             |
| `Accept`          | `application/json`             |

## Useful endpoints

| Purpose               | Method | Path                                      |
|-----------------------|--------|-------------------------------------------|
| List tasks            | GET    | `/tasks?status=<open|assigned|done>&page=<n>&page_size=<k>&search=<q>` |
| Get task              | GET    | `/tasks/{task_id}`                        |
| Create/claim task     | POST   | `/tasks` or `/tasks/{task_id}/claim`      |
| Submit solution       | POST   | `/tasks/{task_id}/solutions`              |
| List solutions        | GET    | `/tasks/{task_id}/solutions`              |
| Get solution          | GET    | `/solutions/{solution_id}`                |

Responses paginate with `page` / `page_size` and usually contain `results`,
`items`, or `data` plus `total`/`next` hints.

## Canonical payloads

```json
// Task
{
  "id": "task_123",
  "title": "Fill checkout form",
  "description": "…",
  "inputs": { "url": "…", "seed": 42 },
  "created_at": "2025-11-07T16:00:00Z",
  "status": "open",
  "metadata": { "difficulty": "m", "tags": ["forms","navigation"] }
}
```

```json
// Solution request payload
{
  "agent_id": "miner_77",
  "artifacts": {
    "steps": [{"action":"click","selector":"#buy"}],
    "logs": "…",
    "screenshots": ["data:image/png;base64,….=="]
  },
  "answer": { "fields": {"email":"a@b.com"} },
  "runtime": { "browser":"chromium", "version":"…", "time_ms": 18342 }
}
```

```json
// Solution response
{
  "id": "sol_999",
  "task_id": "task_123",
  "status": "evaluating",
  "score": null,
  "verdict": null,
  "created_at": "2025-11-07T16:05:00Z"
}
```

```json
// Evaluation result
{
  "id": "sol_999",
  "status": "passed",
  "score": 0.85,
  "verdict": "All checks passed (6/6)",
  "checks": [
    {"name":"backend_event:order_created","passed":true},
    {"name":"dom:button_clicked", "value":"#buy", "passed":true}
  ]
}
```

Statuses typically include `pending`, `evaluating`, `passed`, `failed`, `partial`.

## Minimal flows

```bash
# 1) List open tasks
curl -H "Authorization: Bearer $TOKEN" \
     "$BASE_URL/tasks?status=open&page=1&page_size=20"

# 2) Get task details
curl -H "Authorization: Bearer $TOKEN" \
     "$BASE_URL/tasks/task_123"

# 3) Submit a solution
curl -X POST -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d @solution.json \
     "$BASE_URL/tasks/task_123/solutions"

# 4) Poll solution status
curl -H "Authorization: Bearer $TOKEN" \
     "$BASE_URL/solutions/sol_999"

# 5) List solutions for a task
curl -H "Authorization: Bearer $TOKEN" \
     "$BASE_URL/tasks/task_123/solutions?page=1&page_size=50"
```

## Downloader CLI

Use `autoppia_iwa/src/rl/score_model/cli/fetch_prod_data.py` to mirror tasks +
solutions into the repo:

```bash
export AUTOPPIA_PROD_BASE_URL="https://your.host/api"
export AUTOPPIA_PROD_API_TOKEN="secret"

python -m autoppia_iwa.src.rl.score_model.cli.fetch_prod_data \
    --task-status done --task-status partial \
    --task-page-size 200 \
    --solution-page-size 200 \
    --output data/rm/raw_evaluations/prod_tasks.jsonl
```

Flags:

| Flag | Description |
|------|-------------|
| `--task-status` | Repeatable status filters (defaults to `done`). |
| `--max-tasks` | Limit number of tasks for smoke tests. |
| `--include-empty` | Keep tasks without solutions. |
| `--sleep-ms` | Backoff between paged requests. |

Each JSONL row contains `{ "task": {...}, "solutions": [...], "fetched_at": "..." }`.
Point downstream scripts (e.g. `make_splits.py`) at this raw dump once you wire
the conversion into `EvaluationEpisode` format.

## Gotchas

- Some deployments require an additional nonce / `run_id`; send it if the API
  responds with an explicit error code.
- Large artifacts may need multipart uploads; the downloader only reads JSON
  fields surfaced by the API.
- Prefer cursor pagination if the backend exposes it; otherwise stick to
  `page`/`page_size`.
