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
# Daryxx Finetuned served by simple_api on localhost:6789
AGENTS = [
    ApifiedWebAgent(id="2", name="AutoppiaAgent1",
                    host="84.247.180.192", port=6789, timeout=120)
    # ApifiedWebAgent(id="2", name="AutoppiaAgent2", host="127.0.0.1", port=7000, timeout=120),
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
    # Dynamic HTML
    enable_dynamic_html=True,
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
