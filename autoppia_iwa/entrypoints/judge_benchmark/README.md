
# Web Voyager

Web Voyager is a benchmarking framework for evaluating web agents on real-world web tasks. It automates the process of generating tasks, running agents, and collecting performance metrics using LLM-based and rule-based evaluation strategies.

## Features

- **Task Generation:** Create realistic web tasks from datasets or custom prompts.
- **Agent Evaluation:** Supports multiple agent types (e.g., browser automation, LLM-based).
- **Metrics & Logging:** Tracks cost, duration, token usage, and success rates.
- **Visualization:** Plots and prints performance statistics.
- **Extensible:** Easily add new agents, tasks, or evaluation criteria.

## Configuration

Edit the configuration in `autoppia_iwa/entrypoints/judge_benchmark/run.py`:

- **Agents:** Define agents and their endpoints.
- **Task Source:** Set URLs and prompts, or use indices to select tasks.
- **Benchmark Options:** Adjust number of tasks, caching, GIF recording, etc.

Example:
```python
AGENTS = [
    ApifiedWebAgent(id="2", name="BrowserUse-OpenAI", host="127.0.0.1", port=5000, timeout=120),
]
CFG = WebVoyagerConfig(
    agents=AGENTS,
    url="https://www.allrecipes.com/",
    prompt="Provide a recipe for vegetarian lasagna...",
)
```

## How to Run

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start your agent(s):**
   Make sure the agents you configured are running and accessible.

3. **Run the benchmark:**
   ```bash
   python -m autoppia_iwa.entrypoints.judge_benchmark.run
   ```

4. **View results:**
   Results, logs, and plots are saved in the `results/` directory.

## Advanced Usage

- **Custom Tasks:**
  Pass a custom URL and prompt to `WebVoyagerConfig`.
- **Task Selection:**
  Use `task_indices` to select specific tasks from the dataset.
- **Caching:**
  Enable solution caching for faster repeated runs.

## File Structure

- `entrypoints/judge_benchmark/run.py` — Main entrypoint for running benchmarks.
- `entrypoints/judge_benchmark/test_real_web.py` — Benchmark orchestration logic.
- `src/shared/web_voyager_utils.py` — Utilities for loading tasks and data.
- `src/evaluation/evaluator/evaluator.py` — Evaluation logic for agent solutions.

## License

See `LICENSE` for details.
