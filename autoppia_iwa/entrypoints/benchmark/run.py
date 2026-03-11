"""
Code-first entrypoint: configure projects, agents, runs, and options here.

Run with:
  python -m autoppia_iwa.entrypoints.benchmark.run
"""

import asyncio

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.utils.logging import setup_logging
from autoppia_iwa.entrypoints.benchmark.utils.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents import ApifiedWebAgent

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
# Active agents to run. For OpenAI CUA: run simple_api with --agent_number 4 on port 7000.
AGENTS = [
    ApifiedWebAgent(host="127.0.0.1", port=7000, id="openai_cua", name="OpenAI CUA", timeout=120),
]

# 2) Projects to evaluate (by id from demo_web_projects)
# Single project + 5 use cases below => exactly 5 tasks (no separate tasks.json or scripts).
PROJECT_IDS = ["autolist"]
PROJECTS = get_projects_by_ids(demo_web_projects, PROJECT_IDS)
# Use case names must match UseCase.name in the project (e.g. automail_6/use_cases.py), not the variable names.
USE_CASES = [
    "AUTOLIST_ADD_TASK_CLICKED",
    "AUTOLIST_SELECT_DATE_FOR_TASK",
    "AUTOLIST_SELECT_TASK_PRIORITY",
    "AUTOLIST_TASK_ADDED",
    "AUTOLIST_CANCEL_TASK_CREATION",
]

# =====================================================
# CONFIGURATION: Choose the evaluation mode here
# =====================================================

# OPTION 1: CONCURRENT mode (traditional)
# Agent generates ALL actions at once and they are evaluated
# CFG = BenchmarkConfig(
#     projects=PROJECTS,
#     agents=AGENTS,
#     # Evaluator mode
#     evaluator_mode="concurrent",  # ← Agent generates full action list
#     # Tasks
#     prompts_per_use_case=1,
#     # use_cases=None means all use-cases
#     use_cases=USE_CASES,
#     # Execution
#     runs=1,  # single run is enough for this fixed agent
#     max_parallel_agent_calls=1,  # limit concurrency to avoid overloading agents
#     record_gif=False,  # if your evaluator returns GIFs
#     # Dynamic mode: disabled for this simple fixed-task test to avoid seed constraints.
#     dynamic=True,
#     # Persistence
#     save_results_json=True,
#     headless=True,  # Show Chromium window (set True or omit to use EVALUATOR_HEADLESS env)
# )

# --- STATEFUL: agent decides step-by-step (must use ApifiedWebAgent in AGENTS) ---
# 5 tasks = PROJECT_IDS (autolist) + USE_CASES (5 names) + prompts_per_use_case=1; no tasks_json_path, no new files.
CFG = BenchmarkConfig(
    projects=PROJECTS,
    agents=AGENTS,
    evaluator_mode="stateful",
    max_steps_per_task=50,
    # Tasks: generated from USE_CASES * prompts_per_use_case (no cache, no tasks_json_path)
    use_cached_tasks=False,
    prompts_per_use_case=1,
    use_cases=USE_CASES,
    runs=1,
    max_parallel_agent_calls=1,
    record_gif=True,
    dynamic=False,
    save_results_json=True,
    headless=True,
)


def main():
    """
    Main entrypoint for the benchmark.
    """
    try:
        setup_logging(str(CFG.benchmark_log_file))
        logger.info(f"Selected {len(CFG.projects)} projects: {[p.name for p in CFG.projects]}")
        logger.info("Initializing benchmark...")

        # Validate configuration early
        if not CFG.projects:
            logger.error("No valid projects in PROJECT_IDS.")
            return

        if not CFG.agents:
            logger.error("No agents configured in AGENTS.")
            return

        benchmark = Benchmark(CFG)
        asyncio.run(benchmark.run())

    except KeyboardInterrupt:
        logger.warning("Benchmark interrupted by user")
    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
