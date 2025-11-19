"""
Code-first entrypoint: configure projects, agents, runs, and options here.
Then run with:  python -m entrypoints.benchmark.run
"""

import asyncio

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent

# =========================
# 💡 Code configuration
# =========================

# 1) Agents (ports where your agents are listening)
AGENTS = [
    ApifiedWebAgent(id="1", name="AutoppiaAgent1", host="127.0.0.1", port=5000, timeout=120),
    # ApifiedWebAgent(id="2", name="AutoppiaAgent2", host="127.0.0.1", port=7000, timeout=120),
    # ApifiedWebAgent(id="2", name="BrowserUse-OpenAI", host="127.0.0.1", port=5000, timeout=120),
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
    "BOOK_DETAIL"
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

# 3) Benchmark parameters
CFG = BenchmarkConfig(
    projects=PROJECTS,
    agents=AGENTS,
    # Tasks
    use_cached_tasks=False,  # load project tasks from JSON cache if available
    prompts_per_use_case=1,
    num_use_cases=1,  # 0 = all use-cases
    use_cases=USE_CASES,
    # Execution
    runs=1,  # how many runs do you want?
    max_parallel_agent_calls=1,  # limit concurrency to avoid overloading agents
    use_cached_solutions=False,  # if True, skip calling agent when cached solution exists
    record_gif=False,  # if your evaluator returns GIFs
    # Dynamic features: array of v1, v2, v3 (or combinations)
    dynamic=True,
    # Persistence
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
