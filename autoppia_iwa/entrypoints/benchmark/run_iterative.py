"""
Entrypoint para benchmark en modo ITERATIVO.

El agente decide acción por acción viendo el estado del browser.

Run with:
  python -m autoppia_iwa.entrypoints.benchmark.run_iterative
"""

import asyncio

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents.cua import FixedAutobooksAgent

# =========================
# 💡 Configuración ITERATIVA
# =========================

# Agentes a evaluar
AGENTS = [
    FixedAutobooksAgent(id="1", name="FixedAutobooksAgent"),
]

# Proyectos a evaluar
PROJECT_IDS = [
    "autobooks",
]
PROJECTS = get_projects_by_ids(demo_web_projects, PROJECT_IDS)

# Configuración en modo ITERATIVO
CFG = BenchmarkConfig(
    projects=PROJECTS,
    agents=AGENTS,
    # ==================== MODO ITERATIVO ====================
    evaluator_mode="iterative",  # ← El agente decide acción por acción
    max_iterations_per_task=50,  # ← Máximo 50 acciones por tarea
    # =======================================================
    # Tasks
    use_cached_tasks=True,
    prompts_per_use_case=1,
    num_use_cases=0,
    use_cases=[],
    # Execution
    runs=1,
    max_parallel_agent_calls=1,
    use_cached_solutions=False,  # No compatible con iterativo
    record_gif=True,  # Recomendado para ver navegación adaptativa
    # Dynamic mode
    dynamic=False,
    # Persistence
    save_results_json=True,
    plot_results=False,
)


def main():
    """
    Main entrypoint for the iterative benchmark.
    """
    try:
        logger.info("Initializing ITERATIVE benchmark...")

        # Validate configuration early
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
        
        if CFG.evaluator_mode == "iterative":
            logger.info(f"Iterative mode enabled: max {CFG.max_iterations_per_task} iterations per task")

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
