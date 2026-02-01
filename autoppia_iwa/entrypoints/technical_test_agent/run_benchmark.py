"""
Script para ejecutar el benchmark con el agente de la prueba técnica.
El agente esperado está hardcodeado para el formulario de contacto de autocinema:
- Las tareas de contacto deberían pasar si el agente está bien implementado
- El resto de use cases fallarán (no los maneja) y eso es aceptable para la prueba
"""

import asyncio
from loguru import logger

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.utils.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent

# Configuración del agente esperado en la prueba técnica
TECHNICAL_TEST_AGENT = ApifiedWebAgent(
    id="technical_test_agent",
    name="Technical Test Agent (Contact Form)",
    host="127.0.0.1",
    port=7000,
    timeout=120,
)

# Projects to evaluate
PROJECT_IDS = [
    "autocinema",  # Web1 - has contact form and many other tasks
]

# Use cases - the agent is hardcoded for CONTACT, so most should fail
USE_CASES = [
    # Leave empty to test all use cases, or specify specific ones
    # "CONTACT",  # This should pass if agent is implemented correctly
    # "FILM_DETAIL",  # This will fail
    # "VIEW_USER_PROFILE",  # This will fail
    # etc.
]

PROJECTS = get_projects_by_ids(demo_web_projects, PROJECT_IDS)

CFG = BenchmarkConfig(
    projects=PROJECTS,
    agents=[TECHNICAL_TEST_AGENT],
    # Tasks
    prompts_per_use_case=1,
    # use_cases=None means all use cases
    use_cases=USE_CASES,
    # Execution
    runs=1,
    max_parallel_agent_calls=1,
    record_gif=False,
    # Dynamic mode
    dynamic=True,
    # Persistence
    save_results_json=True,
)


async def main():
    """Ejecuta el benchmark."""
    logger.info("=" * 80)
    logger.info("TECHNICAL TEST BENCHMARK")
    logger.info("=" * 80)
    logger.info(f"Agent: {TECHNICAL_TEST_AGENT.name} ({TECHNICAL_TEST_AGENT.id})")
    logger.info(f"Projects: {PROJECT_IDS}")
    logger.info(f"Use Cases: {USE_CASES}")
    logger.info("")
    logger.info("Expected behavior:")
    logger.info("  - Contact form tasks should SUCCEED (if the agent handles them)")
    logger.info("  - Most other tasks will FAIL (agent is scoped to contact form)")
    logger.info("  - This is expected for the technical test")
    logger.info("=" * 80)
    logger.info("")
    
    if not CFG.projects:
        logger.error("No valid projects found!")
        return
    
    if not CFG.agents:
        logger.error("No agents configured!")
        return
    
    benchmark = Benchmark(CFG)
    results = await benchmark.run()
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("BENCHMARK COMPLETED")
    logger.info("=" * 80)
    logger.info(f"Results saved to: data/outputs/benchmark/")
    
    return results


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Benchmark interrupted by user")
    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        raise
