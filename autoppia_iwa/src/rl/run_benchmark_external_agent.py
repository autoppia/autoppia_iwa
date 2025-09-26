"""
Run the built-in Benchmark against your external agent.

Usage:
  python -m autoppia_iwa.src.rl.run_benchmark_external_agent
"""

import asyncio

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent

# =========================
# External Agent Config
# =========================
AGENT_NAME = "autoppia_agent"
AGENT_HOST = "http://84.247.180.192"  # you can leave scheme, we sanitize below
AGENT_PORT = 6789
AGENT_TIMEOUT = 180

# Project(s) to evaluate (must exist in demo_web_projects)
PROJECT_IDS = ["dining"]  # or ["work"] if you prefer
# =========================


def _sanitize_host(h: str) -> str:
    return h.replace("http://", "").replace("https://", "").rstrip("/")


def main():
    projects = get_projects_by_ids(demo_web_projects, PROJECT_IDS)
    if not projects:
        logger.error(f"No valid projects in PROJECT_IDS={PROJECT_IDS}")
        return

    host = _sanitize_host(AGENT_HOST)
    agents = [ApifiedWebAgent(id="ext-1", name=AGENT_NAME, host=host, port=AGENT_PORT, timeout=AGENT_TIMEOUT)]

    cfg = BenchmarkConfig(
        projects=projects,
        agents=agents,
        use_cached_tasks=True,  # reuse cached tasks if present
        prompts_per_use_case=1,
        num_use_cases=0,  # 0 = all use-cases
        runs=1,
        max_parallel_agent_calls=1,
        use_cached_solutions=False,
        record_gif=False,
        save_results_json=True,
        plot_results=False,
    )

    logger.info(f"Running Benchmark for projects={PROJECT_IDS} against agent {AGENT_NAME}@{host}:{AGENT_PORT}")
    asyncio.run(Benchmark(cfg).run())


if __name__ == "__main__":
    main()
