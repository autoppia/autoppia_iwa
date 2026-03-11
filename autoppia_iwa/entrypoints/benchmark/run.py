"""
Code-first entrypoint: configure projects, agents, runs, and options here.
Run: python -m autoppia_iwa.entrypoints.benchmark.run

- Tasks from JSON: set CFG.tasks_json_path to e.g. benchmark-output/cache/tasks/automail_tasks.json.
- Remote agents: BENCHMARK_AGENT_TARGET=remote in .env (uses SOTA hostnames in run.py).
- Remote webs: DEMO_WEBS_ENDPOINT in .env to your remote base (e.g. https://webs.autoppia.com).
- Local single-agent: set AGENTS = LOCAL_AGENTS[:1] to run only the first agent.
"""

import asyncio

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig, get_benchmark_agent_target
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

# BENCHMARK_AGENT_TARGET in .env: "remote" = SOTA_AGENTS, "local" = LOCAL_AGENTS.
AGENT_TARGET = get_benchmark_agent_target()

# Remote SOTA agents (run benchmark remotely with DEMO_WEBS_ENDPOINT set for remote webs)
OPENAI_CUA = ApifiedWebAgent(id="openai_cua", name="OpenAI CUA", host="openai-cua-agent-sota.autoppia.com", port=80, timeout=120)
ANTHROPIC_CUA = ApifiedWebAgent(id="anthropic_cua", name="Anthropic CUA", host="anthropic-cua-agent-sota.autoppia.com", port=80, timeout=120)
BROWSER_USE = ApifiedWebAgent(id="browser_use", name="Browser Use", host="browser-use-agent-sota.autoppia.com", port=80, timeout=120)
BROWSER_USE_OPENAI = ApifiedWebAgent(id="browser_use_openai", name="Browser Use OpenAI", host="browser-use-openai-agent-sota.autoppia.com", port=80, timeout=120)
BROWSER_USE_ANTHROPIC = ApifiedWebAgent(id="browser_use_anthropic", name="Browser Use Anthropic", host="browser-use-anthropic-agent-sota.autoppia.com", port=80, timeout=120)
SOTA_AGENTS = [OPENAI_CUA, ANTHROPIC_CUA, BROWSER_USE, BROWSER_USE_OPENAI, BROWSER_USE_ANTHROPIC]

# Local agents (run simple_api per agent on these ports)
LOCAL_AGENTS = [
    ApifiedWebAgent(host="127.0.0.1", port=5000, id="browser_use_openai", name="Browser Use OpenAI", timeout=120),
    ApifiedWebAgent(host="127.0.0.1", port=5001, id="browser_use_anthropic", name="Browser Use Anthropic", timeout=120),
    ApifiedWebAgent(host="127.0.0.1", port=5002, id="browser_use_native", name="Browser Use Native", timeout=120),
    ApifiedWebAgent(host="127.0.0.1", port=5003, id="openai_cua", name="OpenAI CUA", timeout=120),
    ApifiedWebAgent(host="127.0.0.1", port=5004, id="anthropic_cua", name="Anthropic CUA", timeout=120),
]
AGENTS = SOTA_AGENTS if AGENT_TARGET == "remote" else LOCAL_AGENTS[:1]  # Or LOCAL_AGENTS[:1] for single-agent local run

# 2) Projects and tasks. To use a tasks JSON file set CFG.tasks_json_path (e.g. benchmark-output/cache/tasks/automail_tasks.json).
PROJECT_IDS = ["automail"]
PROJECTS = get_projects_by_ids(demo_web_projects, PROJECT_IDS)
# Use case names must match UseCase.name in the project (e.g. automail_6/use_cases.py), not the variable names.
USE_CASES = [
    "SEARCH_EMAIL",
    # "VIEW_EMAIL",
    # "ARCHIVE_EMAIL",
    # "STAR_AN_EMAIL",
    # "MARK_EMAIL_AS_IMPORTANT",
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
    agent_target=AGENT_TARGET,
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
        logger.info(f"Agents target: {CFG.agent_target} | {len(CFG.agents)} agents")
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
        import traceback

        traceback.print_exc()
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
