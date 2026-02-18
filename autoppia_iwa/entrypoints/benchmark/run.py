"""
Single entrypoint for the IWA benchmark. Configure mode, projects, and agents here.

Run:
  python -m autoppia_iwa.entrypoints.benchmark.run

See README.md for evaluator modes (concurrent vs stateful) and agent requirements.
"""

import asyncio

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.utils.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents.cua import ApifiedWebAgent

# =============================================================================
# 1) AGENTS
# =============================================================================
# Standard: all agents expose POST /act. Use ApifiedWebAgent for both modes.
# - Concurrent: benchmark calls /act once (step_index=0); agent returns full action list.
# - Stateful:   benchmark calls /act repeatedly with browser snapshot each step.
# Legacy: if your agent only exposes POST /solve_task, use ApifiedOneShotWebAgent instead.

AGENTS = [
    ApifiedWebAgent(base_url="http://localhost:5000", id="1", name="LocalAgent", timeout=120),
]

# =============================================================================
# 2) PROJECTS & USE CASES
# =============================================================================

PROJECT_IDS = ["autocinema"]
PROJECTS = get_projects_by_ids(demo_web_projects, PROJECT_IDS)
USE_CASES = ["FILM_DETAIL"]  # or None for all use cases

# =============================================================================
# 3) EVALUATOR MODE: choose one block (concurrent or stateful)
# =============================================================================
# Both use POST /act. Concurrent: call /act once (step_index=0), agent returns all actions.
# Stateful: call /act repeatedly with snapshot_html each step.

# --- CONCURRENT (default): agent generates full action sequence in one go ---
CFG = BenchmarkConfig(
    projects=PROJECTS,
    agents=AGENTS,
    evaluator_mode="concurrent",
    use_cases=USE_CASES,
    prompts_per_use_case=1,
    use_cached_tasks=False,
    runs=1,
    max_parallel_agent_calls=1,
    record_gif=False,
    dynamic=True,
    save_results_json=True,
)

# --- STATEFUL: agent decides step-by-step (must use ApifiedWebAgent in AGENTS) ---
# Uncomment this block and comment the CFG block above to run in stateful mode.
# CFG = BenchmarkConfig(
#     projects=PROJECTS,
#     agents=AGENTS,
#     evaluator_mode="stateful",
#     max_steps_per_task=50,
#     use_cases=USE_CASES,
#     prompts_per_use_case=1,
#     use_cached_tasks=True,
#     runs=1,
#     max_parallel_agent_calls=1,
#     record_gif=True,
#     dynamic=False,
#     save_results_json=True,
# )


def main():
    """
    Main entrypoint for the benchmark.
    """
    try:
        logger.info("Initializing benchmark...")

        # Validate configuration early
        if not CFG.projects:
            logger.error("No valid projects in PROJECT_IDS.")
            return

        if not CFG.agents:
            logger.error("No agents configured in AGENTS.")
            return

        logger.info(f"Configuration: {len(CFG.projects)} projects, {len(CFG.agents)} agents, {CFG.runs} runs, evaluator_mode={CFG.evaluator_mode}")

        if CFG.evaluator_mode == "stateful":
            logger.info(f"Stateful mode enabled: max {CFG.max_steps_per_task} steps per task")

        # Create and run benchmark
        benchmark = Benchmark(CFG)
        asyncio.run(benchmark.run())

    except KeyboardInterrupt:
        logger.warning("Benchmark interrupted by user")
    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
