"""
Entrypoint para probar el benchmark en modo STATEFUL.

Run with:
  python -m autoppia_iwa.entrypoints.benchmark.run_stateful
"""

import asyncio

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.utils.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents.cua import ApifiedWebCUA

# Configuración para modo STATEFUL
PROJECT_IDS = ["autobooks"]
PROJECTS = get_projects_by_ids(demo_web_projects, PROJECT_IDS)

# ✅ IMPORTANTE: En modo stateful, los agentes DEBEN ser HTTP (ApifiedWebCUA)
# El agente debe estar corriendo en un servidor y exponer el endpoint /act
#
# Ejemplo: Si tienes un agente corriendo en http://localhost:5000
# AGENTS = [
#     ApifiedWebCUA(base_url="http://localhost:5000", id="1", name="MyAgent"),
# ]
#
# ⚠️ NO usar agentes Python locales (FixedAutobooksAgent, etc.) en modo stateful
# Esos son para modo concurrent solamente.

AGENTS = [
    # Ejemplo: Agente HTTP corriendo localmente
    ApifiedWebCUA(base_url="http://localhost:5000", id="1", name="LocalAgent"),
    # O agente remoto
    # ApifiedWebCUA(base_url="http://mi-agente.com", id="1", name="RemoteAgent"),
]

# Configuración en modo STATEFUL
CFG = BenchmarkConfig(
    projects=PROJECTS,
    agents=AGENTS,
    # Evaluator mode
    evaluator_mode="stateful",  # ← Modo iterativo
    max_steps_per_task=50,  # ← Límite de pasos
    # Tasks
    prompts_per_use_case=1,
    # Execution
    runs=1,
    max_parallel_agent_calls=1,
    record_gif=False,
    # Dynamic mode
    dynamic=False,
    # Persistence
    save_results_json=True,
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

        logger.info(f"Configuration: {len(CFG.projects)} projects, {len(CFG.agents)} agents, {CFG.runs} runs, evaluator_mode={CFG.evaluator_mode}")
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
