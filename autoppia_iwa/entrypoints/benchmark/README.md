# 🔬 Benchmark Framework for Autoppia IWA

The **benchmark** acts as a sandbox where you can test **how good your web agents are**.

To use it, you need to:
1. Start the **demo web application** you want to test (e.g., `connect`, `cinema`, etc.).
2. Select that web project in the benchmark configuration (`PROJECT_IDS`).
3. Deploy your agent(s) on one or more ports and declare them in `run.py`.

The benchmark will then:
- **Generate tasks** for the selected projects.
- **Send those tasks** to the agents you configured.
- **Evaluate the solutions** returned by the agents.
- Allow you to **compare multiple agents side by side**.

---

## 📂 Directory structure

entrypoints/benchmark/

├─ __init__.py
├─ **config.py**              # Central BenchmarkConfig dataclass
├─ **tasks_generation.py**    # Wrapper to generate/load cached tasks per project
├─ **benchmark.py**           # Benchmark class (orchestrates the flow)
└─ **run.py**                 # Entry point: configure everything in code and run

---

## 🚀 How to run the benchmark

1. Go to your project root (where `autoppia_iwa` is located).
2. Execute:

    **python -m entrypoints.benchmark.run**

---

## ⚙️ Configuration (in `run.py`)

You configure everything directly in code, no CLI required.

Example:

    # 1) Agents
    AGENTS = [
        ApifiedWebAgent(id="1", name="AutoppiaAgent1", host="127.0.0.1", port=5000, timeout=120),
        ApifiedWebAgent(id="2", name="AutoppiaAgent2", host="127.0.0.1", port=7000, timeout=120),
    ]

    # 2) Projects (IDs from demo_web_projects)
    PROJECT_IDS = ["connect"]
    PROJECTS = get_projects_by_ids(demo_web_projects, PROJECT_IDS)

    # 3) Benchmark settings
    CFG = BenchmarkConfig(
        projects=PROJECTS,
        agents=AGENTS,
        use_cached_tasks=True,       # Load tasks from JSON cache if available
        prompts_per_use_case=1,
        num_use_cases=0,             # 0 = all use-cases
        runs=3,                      # How many runs to execute
        max_parallel_agent_calls=1,  # Control concurrency
        use_cached_solutions=False,  # Use solution cache if available
        record_gif=False,            # Save evaluation GIFs if available
        save_results_json=True,
        plot_results=False,          # Generate plots (optional)
    )

Finally, run:

    python -m entrypoints.benchmark.run

---

## 📊 What happens during a run?

For each project in PROJECT_IDS:

1. Generate or load tasks
   - If `use_cached_tasks=True`, tasks are loaded from
     `data/tasks_cache/<project>_tasks.json`
   - Otherwise, they are generated via the task generation pipeline and saved to cache.

2. Solve tasks with agents
   - Each agent attempts to solve each task.
   - If `use_cached_solutions=True`, the solution cache (`data/solutions_cache/solutions.json`) is used instead of calling the agent.

3. Evaluate solutions
   - The evaluator scores each solution.
   - If `record_gif=True`, base64-encoded GIFs are decoded and saved under `recordings/<agent>/`.

4. Persist results
   - A JSON report is saved under `results/benchmark_results_<timestamp>.json`
   - Optional: plots can be generated if `plot_results=True`.

5. Global statistics are printed in the console per agent (success rate, average solution time).

---

## 📁 Output artifacts

- Tasks cache: `data/tasks_cache/<project>_tasks.json`
- Solutions cache: `data/solutions_cache/solutions.json`
- Results: `results/benchmark_results_<timestamp>.json`
- GIF recordings: `recordings/<agent>/<task_id>_run_<n>.gif`
- Optional plots: `results/stress_test_chart_<timestamp>.png`

---

## 🛠️ Extending the benchmark

- Change projects: update `PROJECT_IDS` in `run.py`.
- Add agents: add `ApifiedWebAgent` instances to `AGENTS`.
- More/less runs: adjust `runs` in `BenchmarkConfig`.
- Parallel execution: increase `max_parallel_agent_calls`.
- Plots: set `plot_results=True`.

---

## 🧪 Example Run

    python -m entrypoints.benchmark.run

Example console output:

    2025-09-24 12:00:00 | INFO     | === Project: connect ===
    2025-09-24 12:00:00 | INFO     | Run 1/3
    2025-09-24 12:00:10 | INFO     | AutoppiaAgent1     |  83.33% (5/6) | avg 1.20s
    2025-09-24 12:00:10 | INFO     | AutoppiaAgent2     |  66.67% (4/6) | avg 1.35s
    ...
    2025-09-24 12:00:30 | SUCCESS  | Benchmark finished ✔

---

## ✅ Summary

- Simple code-based configuration → no CLI required.
- Cache-aware for tasks and solutions.
- JSON reports + optional plots for results.
- Agent statistics are aggregated per project and globally.

Use `run.py` as the main place to adjust what you want to test.
