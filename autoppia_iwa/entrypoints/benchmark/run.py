"""
Code-first entrypoint: configure projects, agents, runs, and options here.

Run with:
  python -m autoppia_iwa.entrypoints.benchmark.run
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

# =========================
# 💡 Code configuration
# =========================

# Define external HTTP SOTA agents (examples). Uncomment to enable.
# Ensure unique `id` per agent.

# BROWSER_USE_AGENT = ApifiedWebAgent(
#     id="browser_use",
#     name="BrowserUse",
#     host="browser-use-agent-sota.autoppia.com",
#     port=80,
#     timeout=120,
# )

# OPENAI_CUA_AGENT = ApifiedWebAgent(
#     id="openai_cua",
#     name="OpenAI CUA",
#     host="openai-cua-agent-sota.autoppia.com",
#     port=80,
#     timeout=120,
# )

# CLAUDE_CUA_AGENT = ApifiedWebAgent(
#     id="claude_cua",
#     name="Claude CUA",
#     host="anthropic-cua-agent-sota.autoppia.com",
#     port=80,
#     timeout=120,
# )

# Group SOTA agent examples (commented). Uncomment to use, or set
# `AGENTS = SOTA_AGENTS` below after uncommenting individual agents.
SOTA_AGENTS = [
    # BROWSER_USE_AGENT,
    # OPENAI_CUA_AGENT,
    # CLAUDE_CUA_AGENT,
]
# Active agents to run.
AGENTS = [
    ApifiedWebAgent(base_url="http://localhost:5000", id="1", name="LocalAgent", timeout=120),
]

# 2) Projects to evaluate (by id from demo_web_projects)
PROJECT_IDS = [
    "autocrm",
]
PROJECTS = get_projects_by_ids(demo_web_projects, PROJECT_IDS)
USE_CASES = None  # None = all use cases

# =====================================================
# CONFIGURACIÓN: Elige el modo de evaluación aquí
# =====================================================

# OPCIÓN 1: Modo CONCURRENT (tradicional)
# El agente genera TODAS las acciones de una vez y se evalúan
CFG = BenchmarkConfig(
    projects=PROJECTS,
    agents=AGENTS,
    # Evaluator mode
    evaluator_mode="concurrent",  # ← Agente genera lista completa de acciones
    # Tasks
    prompts_per_use_case=3,
    # use_cases=None means all use-cases
    use_cases=None,
    # Execution
    runs=1,  # single run is enough for this fixed agent
    max_parallel_agent_calls=1,  # limit concurrency to avoid overloading agents
    record_gif=False,  # if your evaluator returns GIFs
    # Dynamic mode: disabled for this simple fixed-task test to avoid seed constraints.
    dynamic=True,
    # TODO REVISAR PORQUE SOLO DEBEIRA HABER UNO
    # dynamic_phase_config=DynamicPhaseConfig(
    #     enable_d1_structure=True,
    #     enable_d3_attributes=True,
    #     enable_d4_overlays=True,
    # ),
    # Persistence
    save_results_json=True,
)

# --- STATEFUL: agent decides step-by-step (must use ApifiedWebAgent in AGENTS) ---
# Uncomment this block and comment the CFG block above to run in stateful mode.
# CFG = BenchmarkConfig(
#     projects=PROJECTS,
#     agents=AGENTS,
#     # Evaluator mode
#     evaluator_mode="stateful",  # ← Modo iterativo: agente decide paso a paso
#     max_steps_per_task=50,  # ← Límite de pasos por tarea
#     # Tasks
#     use_cached_tasks=True,
#     prompts_per_use_case=1,
#     num_use_cases=0,
#     use_cases=USE_CASES,
#     # Execution
#     runs=1,
#     max_parallel_agent_calls=1,
#     use_cached_solutions=False,  # ⚠️ No compatible con modo stateful
#     record_gif=True,  # Recomendado para ver la navegación adaptativa
#     # Dynamic mode
#     dynamic=False,
#     # Persistence
#     save_results_json=True,
#     plot_results=False,
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

        benchmark = Benchmark(CFG)
        asyncio.run(benchmark.run())

    except KeyboardInterrupt:
        logger.warning("Benchmark interrupted by user")
    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
