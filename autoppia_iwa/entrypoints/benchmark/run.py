"""
Code-first entrypoint: configure projects, agents, runs, and options here.

Run with:
  python -m autoppia_iwa.entrypoints.benchmark.run
"""
import asyncio

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.execution.dynamic import DynamicPhaseConfig
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent

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

# Active agents to run. Configure your local simple_api agent here.
AGENTS = [
    ApifiedWebAgent(id="openai-cua", name="OpenAI CUA (local)",
                    host="127.0.0.1", port=13111, timeout=400)
]

# 2) Projects to evaluate (by id from demo_web_projects)
PROJECT_IDS = [
    # "autocinema",
    "autobooks",
    # "autozone",
    # "autodining",
    # "autocrm",
    # "automail",
    # "autodelivery",
    # "autolodge",
    # "autoconnect",
    # "autowork",
    # "autocalendar",
    # "autolist",
    # "autodrive",
    # add more project ids here
]
PROJECTS = get_projects_by_ids(demo_web_projects, PROJECT_IDS)
USE_CASES = [
    # "VIEW_USER_PROFILE",
    # "FILM_DETAIL",
    # "EDIT_USER_BOOK"
]

CFG = BenchmarkConfig(
    projects=PROJECTS,
    agents=AGENTS,
    use_cached_tasks=False,
    prompts_per_use_case=10,
    num_use_cases=1,  
    use_cases=USE_CASES,
    runs=1, 
    max_parallel_agent_calls=1, 
    use_cached_solutions=False,
    record_gif=False,
    enable_dynamic_html=True,
    dynamic_phase_config=DynamicPhaseConfig(
        enable_d1_structure=True,
        enable_d3_attributes=True,
        enable_d4_overlays=True,
    ),
    save_results_json=True,
    plot_results=False,
)


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

        logger.info(
            f"Configuration: {len(CFG.projects)} projects, {len(CFG.agents)} agents, {CFG.runs} runs")

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
