"""
Entrypoint para probar el benchmark en modo STATEFUL.

Run with:
  python -m autoppia_iwa.entrypoints.benchmark.run_stateful
"""

import asyncio

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents.cua import FixedAutobooksAgent

# Configuración para modo STATEFUL
PROJECT_IDS = ["autobooks"]
PROJECTS = get_projects_by_ids(demo_web_projects, PROJECT_IDS)

AGENTS = [
    FixedAutobooksAgent(id="1", name="FixedAutobooksAgent"),
]

# Configuración en modo STATEFUL
CFG = BenchmarkConfig(
    projects=PROJECTS,
    agents=AGENTS,
    # Evaluator mode
    evaluator_mode="stateful",  # ← Modo iterativo
    max_steps_per_task=50,      # ← Límite de pasos
    # Tasks
    use_cached_tasks=True,
    prompts_per_use_case=1,
    num_use_cases=0,
    # Execution
    runs=1,
    max_parallel_agent_calls=1,
    use_cached_solutions=False,  # No compatible con modo stateful
    record_gif=False,
    # Dynamic mode
    dynamic=False,
    # Persistence
    save_results_json=True,
    plot_results=False,
)


def main():
    """
    Main entrypoint para probar modo stateful.
    """
    try:
        logger.info("Initializing benchmark in STATEFUL mode...")

        if not CFG.projects:
            logger.error("No valid projects in PROJECT_IDS.")
            return

        if not CFG.agents:
            logger.error("No agents configured in AGENTS.")
            return

        logger.info(
            f"Configuration: {len(CFG.projects)} projects, {len(CFG.agents)} agents, "
            f"{CFG.runs} runs, evaluator_mode={CFG.evaluator_mode}"
        )
        logger.info(f"Stateful mode: max {CFG.max_steps_per_task} steps per task")

        # Create and run benchmark
        benchmark = Benchmark(CFG)
        asyncio.run(benchmark.run())

        logger.success("✅ Benchmark completado en modo STATEFUL!")

    except KeyboardInterrupt:
        logger.warning("Benchmark interrupted by user")
    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
