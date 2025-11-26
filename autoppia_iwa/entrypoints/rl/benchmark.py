"""
Benchmark entrypoint for the in-repo RL agent.

Runs the standard benchmark orchestrator but wires `RLModelAgent` as the
active agent. Useful to quickly evaluate a trained model (or the fallback
policy when a model file is not available).

Run with:
  python -m autoppia_iwa.entrypoints.rl.benchmark
"""

from __future__ import annotations

import asyncio

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents.rl import RLModelAgent, RLModelAgentConfig


# =========================
# RL Agent configuration
# =========================

# Hardcoded model path (no .env needed)
RL_MODEL_PATH = "/data/rl/models/ppo_real.zip"

RL_AGENT = RLModelAgent(
    id="rl-model",
    name="RLModelAgent",
    config=RLModelAgentConfig(model_path=RL_MODEL_PATH,
                              topk=12, max_steps=30, deterministic=True),
)


# =========================
# Projects selection
# =========================

# Limit benchmark strictly to 1 project for faster iteration
PROJECT_IDS = [demo_web_projects[0].id]
PROJECTS = get_projects_by_ids(demo_web_projects, PROJECT_IDS)


# =========================
# Benchmark parameters
# =========================

CFG = BenchmarkConfig(
    projects=PROJECTS,
    agents=[RL_AGENT],
    # Tasks
    use_cached_tasks=True,
    prompts_per_use_case=1,  # 1 prompt → 1 task per selected use case
    num_use_cases=1,  # select only 1 use case → 1 task total per project
    # Execution
    runs=1,
    max_parallel_agent_calls=1,  # RL env uses a real browser; keep serial
    use_cached_solutions=False,
    record_gif=False,
    # Dynamic HTML
    enable_dynamic_html=False,
    # Persistence
    save_results_json=True,
    plot_results=False,
)


def main():
    try:
        logger.info("Initializing RL benchmark...")

        if not CFG.projects:
            logger.error("No valid projects in PROJECT_IDS.")
            return

        if not CFG.agents:
            logger.error("No agents configured.")
            return

        logger.info(
            f"Configuration: {len(CFG.projects)} projects, {len(CFG.agents)} agents, {CFG.runs} runs"
        )

        benchmark = Benchmark(CFG)
        asyncio.run(benchmark.run())

    except KeyboardInterrupt:
        logger.warning("Benchmark interrupted by user")
    except Exception as e:
        logger.error(f"RL benchmark failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
