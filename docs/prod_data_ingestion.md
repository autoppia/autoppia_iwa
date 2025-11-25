# Prod Task/Solution Ingestion

Use this guide to mirror production task activity into the local reward-model
dataset. The workflow is now fully driven by the leaderboard endpoint so we can
pull canonical `task+solution+score` tuples without juggling multiple services:

1. Fetch tasks + solutions from `https://api-leaderboard.autoppia.com/api/v1/tasks/with-solutions`.
2. Store the raw dump under `data/score_model_pipeline/raw/`.
3. Reuse the prepared dataset (`build_score_model_training_dataset.py`) for
   feature extraction + training.

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

## Leaderboard-powered CLI

Use `autoppia_iwa/src/rl/score_model/cli/build_score_model_training_dataset.py`
to mirror leaderboard data straight into the new pipeline directories:

```bash
python -m autoppia_iwa.src.rl.score_model.cli.build_score_model_training_dataset \
    --website autocinema --website autobooks \
    --success true --success false \
    --pages-per-filter 5 \
    --limit 200 \
    --dedupe-strategy task_solution
```

Flags:

| Flag | Description |
|------|-------------|
| `--website`, `--use-case`, `--miner-uid` | Repeatable filters to avoid duplicate pulls. |
| `--success` | `true`, `false`, or `all` to control pass/fail coverage. |
| `--pages-per-filter` / `--limit` | Pagination knobs (limit ≤ 500). |
| `--output-prefix` | Custom filename prefix for datasets + metrics. |

Outputs land in:

- `data/score_model_pipeline/raw/<prefix>.jsonl` – raw leaderboard payload.
- `data/score_model_pipeline/datasets/<prefix>.jsonl` – flattened samples for training.
- `data/score_model_pipeline/metrics/<prefix>.json` – summary counts/filters.

Downstream scripts (`build_dom_event_features.py`, `train_reward_model.py`, etc.)
can now consume the `datasets/*.jsonl` files directly without rebuilding ad-hoc
splits.

## Replaying solutions for DOM/JS traces

To capture per-action DOM snapshots, JS events, backend payloads, and optional
screenshots, replay the flattened dataset through the instrumented evaluator:

```bash
python -m autoppia_iwa.src.rl.score_model.cli.replay_leaderboard_solutions \
  --dataset data/score_model_pipeline/datasets/leaderboard_full_20251110_234743.jsonl \
  --output-dir data/score_model_pipeline/raw_traces/leaderboard_full_20251110_234743 \
  --limit 2000 --per-website-limit 300
```

Those traces live under `output-dir` and plug directly into
`build_dom_event_features.py`, enabling feature sets based on actual DOM diffs
and runtime events instead of text-only summaries.

## Gotchas

- Some deployments require an additional nonce / `run_id`; send it if the API
  responds with an explicit error code.
- Large artifacts may need multipart uploads; the downloader only reads JSON
  fields surfaced by the API.
- Prefer cursor pagination if the backend exposes it; otherwise stick to
  `page`/`page_size`.
