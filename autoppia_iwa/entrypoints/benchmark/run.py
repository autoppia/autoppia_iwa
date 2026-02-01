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
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent

# from autoppia_iwa.src.execution.dynamic import DynamicPhaseConfig

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
    ApifiedWebAgent(id="1", name="AutoppiaAgent1", host="127.0.0.1", port=7000, timeout=120),
    # ApifiedWebAgent(id="2", name="AutoppiaAgent2", host="127.0.0.1", port=7000, timeout=120),
    # ApifiedWebAgent(id="2", name="BrowserUse-OpenAI", host="127.0.0.1", port=5000, timeout=120),
]

# 2) Projects to evaluate (by id from demo_web_projects)
PROJECT_IDS = [
    # "autocinema",
    # "autobooks",
    # "autozone",
    # "autodining",
    # "autocrm",
    "automail",
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
    # "BOOK_DETAIL"
    # "VIEW_USER_PROFILE",
    # "FILM_DETAIL",
    # "EDIT_USER_BOOK"
    # "RESERVE_HOTEL"
    # "VIEW_FULL_MENU"
    # "RESERVATION_COMPLETE"
    # "ORDER_COMPLETED",
    # "HIRE_CONSULTANT"
    # "VIEW_HOTEL"
    # "SEARCH_HOTEL"
    # "VIEW_HOTEL"
    # "INCREASE_NUMBER_OF_GUESTS"
    # "RESERVE_HOTEL"
    # "COLLAPSE_MENU"
    # "CHECKOUT_STARTED"
    # "ORDER_COMPLETED"
    # "NEW_LOG_ADDED"
    # "VIEW_MATTER_DETAILS"
    # "SEARCH_CLIENT"
    # "DOCUMENT_DELETED"
    # "SEARCH_EMAIL"
    # "PLACE_ORDER"
    # "DROPOFF_PREFERENCE"
    # "ADD_TO_CART_MENU_ITEM"
    # "DELETE_REVIEW"
    # "ITEM_INCREMENTED"
    # "VIEW_USER_PROFILE"
    # "BOOK_A_CONSULTATION"
    # "HIRE_CONSULTANT"
    # "SEARCH_LOCATION"
    # "SEARCH_DESTINATION"
    # "SEARCH"
    # "SELECT_CAR"
    # "RESERVE_RIDE"
]

CFG = BenchmarkConfig(
    projects=PROJECTS,
    agents=AGENTS,
    # Tasks
    prompts_per_use_case=1,
    # use_cases=None means all use-cases
    use_cases=USE_CASES,
    # Execution
    runs=1,  # how many runs do you want?
    max_parallel_agent_calls=1,  # limit concurrency to avoid overloading agents
    record_gif=False,  # if your evaluator returns GIFs
    # Dynamic mode: flag to enable or disable dynamic mode that assigns initial seed to the task URL.
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

        logger.info(f"Configuration: {len(CFG.projects)} projects, {len(CFG.agents)} agents, {CFG.runs} runs")

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
