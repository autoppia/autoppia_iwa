
## Judge Benchmark (Web Voyager)

A simple benchmark to evaluate web agents on real websites. It runs tasks, collects solutions, and evaluates them using rule- and LLM-based judges. No runtime flags or CLI are needed—just edit one file and run.

### What you get
- **Task sources**: Either a custom URL + prompt, or tasks from the bundled dataset
- **Agent evaluation**: Works with agents exposing a local HTTP API
- **Outputs**: Plots, JSON summaries, rich console tables, and usage logs

---

## Quick start

1) Start your agent (example shown uses BrowserUse on `127.0.0.1:5000`).

2) Open and edit `autoppia_iwa/entrypoints/judge_benchmark/run.py`.

Pick ONE mode by flipping a single boolean:

- Mode A – custom task (recommended for a quick smoke test)
  - Set `USE_CUSTOM_TASK = True`
  - Set `CUSTOM_URL` and `CUSTOM_PROMPT`

- Mode B – dataset selection
  - Set `USE_CUSTOM_TASK = False`
  - Either set `NUM_OF_URLS = N` (first N tasks) OR set `TASK_INDICES = [i, j, ...]`

Minimal example inside `run.py`:
```python
# Agent
AGENTS = [
    ApifiedWebAgent(id="1", name="BrowserUse-OpenAI", host="127.0.0.1", port=5000, timeout=120),
]

# Choose how to select tasks
USE_CUSTOM_TASK = True  # or False to use the dataset

# Custom task (used when USE_CUSTOM_TASK=True)
CUSTOM_URL = "https://www.allrecipes.com/"
CUSTOM_PROMPT = "Provide a vegetarian lasagna recipe..."

# Dataset selection (used when USE_CUSTOM_TASK=False)
NUM_OF_URLS = 1
TASK_INDICES = []  # e.g. [0, 2, 5]

# Run options
RECORD_GIF = True
```

3) Run the benchmark:
```bash
python -m autoppia_iwa.entrypoints.judge_benchmark.run
```

---

## Outputs
- Results (plots and JSON) are saved under `results/`
- Evaluation log: `real_web_evaluation.log` (at project root)
- Judge usage logs: `judge_tests_usage_logs.jsonl` (created automatically when LLM-based judges run)

You can also summarize judge usage logs:
```bash
python -m autoppia_iwa.entrypoints.judge_benchmark.benchmark_llm_tests
# Optional: specify a different file
# python -m autoppia_iwa.entrypoints.judge_benchmark.benchmark_llm_tests --src /path/to/judge_tests_usage_logs.jsonl
```

---

## Dataset location
By default, tasks are loaded from:
- `autoppia_iwa/entrypoints/judge_benchmark/web_voyager_tasks/web_voyager_data.jsonl`

If not found, it falls back to:
- `data/web_voyager_tasks/web_voyager_data.jsonl`

Impossible tasks (if present) are filtered using `web_voyager_impossible_tasks.json` in the same directory. If the file is missing, all tasks are considered possible.

---

## Tips & troubleshooting
- Ensure your agent is reachable at the host/port you configured in `AGENTS`
- If GIFs are not needed, set `RECORD_GIF = False`
- If you see no plots or JSON, check `real_web_evaluation.log` for errors
- LLM provider setup (e.g., OpenAI API key) is managed via environment variables in `autoppia_iwa/config/config.py`

---

## File map
- `entrypoints/judge_benchmark/run.py` — edit-and-run entrypoint
- `entrypoints/judge_benchmark/test_real_web.py` — orchestration & evaluation
- `src/shared/web_voyager_utils.py` — dataset loading helpers
- `entrypoints/benchmark/utils/*` — metrics, results, plotting utilities
