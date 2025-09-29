"""
Code-first entrypoint: configure projects, agents, runs, and options here.
Then run with:  python -m entrypoints.benchmark.run
"""

import asyncio

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent

# =========================
# 💡 Code configuration
# =========================

# 1) Agents (ports where your agents are listening)
AGENTS = [
    ApifiedWebAgent(id="1", name="AutoppiaAgent1", host="127.0.0.1", port=5000, timeout=120),
    # ApifiedWebAgent(id="2", name="AutoppiaAgent2",
    #                 host="127.0.0.1", port=7000, timeout=120),
]

# 2) Projects to evaluate (by id from demo_web_projects)
PROJECT_IDS = [
    # "autozone", "cinema", "books", ...
    "work",
]
PROJECTS = get_projects_by_ids(demo_web_projects, PROJECT_IDS)

# 3) Benchmark parameters
CFG = BenchmarkConfig(
    projects=PROJECTS,
    agents=AGENTS,
    # Tasks
    use_cached_tasks=False,  # load project tasks from JSON cache if available
    prompts_per_use_case=1,
    num_use_cases=0,  # 0 = all use-cases
    # Execution
    runs=1,  # how many runs do you want?
    max_parallel_agent_calls=1,  # limit concurrency to avoid overloading agents
    use_cached_solutions=False,  # if True, skip calling agent when cached solution exists
    record_gif=False,  # if your evaluator returns GIFs
    # Persistence
    save_results_json=True,
    plot_results=False,
)


def main():
    if not CFG.projects:
        logger.error("No valid projects in PROJECT_IDS.")
        return
    benchmark = Benchmark(CFG)
    asyncio.run(benchmark.run())


if __name__ == "__main__":
    main()
