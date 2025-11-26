# Autoppia IWA Affine Service

Minimal `/evaluate` HTTP service that Affine validators can call. It:
- loads/generates demo-web tasks (cached by default),
- calls a remote agent at `base_url/solve_task`,
- evaluates the returned actions with `ConcurrentEvaluator` against the demo webs,
- responds with `{score, success, error, extra}`.

## Run locally
```bash
export DEMO_WEBS_ENDPOINT=https://your-remote-demo-webs.example.com  # required
python -m autoppia_iwa.affine_service.server
# curl -X POST :8000/evaluate -d '{"model":"foo/bar","base_url":"https://X.chutes.ai/v1"}'
```

Key env vars:
- `DEMO_WEBS_ENDPOINT`: remote demo webs base (scheme + host required).
- `AFFINE_PROJECT_IDS`: comma list of project IDs to enable (default all).
- `AFFINE_TASK_CACHE_DIR`: where to cache/load tasks (default `data/affine/tasks`).
- `AFFINE_USE_CACHED_TASKS`: `1` to prefer cache, `0` to regenerate.
- `AFFINE_PROMPTS_PER_USE_CASE`, `AFFINE_NUM_USE_CASES`: task generation knobs.

## Docker
```bash
docker build -f autoppia_iwa/affine_service/Dockerfile -t affine-iwa .
docker run --rm -p 8000:8000 \
  -e DEMO_WEBS_ENDPOINT=https://demo.example.com \
  affine-iwa
```

Entrypoint: `POST /evaluate`
```json
{
  "model": "meta-llama/Llama-3-70B-Instruct",
  "base_url": "https://my-chute.chutes.ai/v1",
  "task_id": 0,
  "temperature": 0.7,
  "timeout": 600,
  "seed": 123
}
```
Response:
```json
{"score": 0.8, "success": true, "error": null, "extra": {"task_index":0,"task_id":"...","web_project_id":"...","raw_score":0.8,"final_score":0.8,"tests_passed":5,"tests_total":6}}
```
