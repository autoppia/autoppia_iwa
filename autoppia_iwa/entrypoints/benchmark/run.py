"""
Benchmark: evaluate agents on demo-web tasks (stateful or concurrent).

Edit the Configuration section below, then run:
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

# -----------------------------------------------------------------------------
# Configuration — edit only this section
# -----------------------------------------------------------------------------
# Agents: "local" = use LOCAL_AGENTS, "remote" = use REMOTE_AGENTS
AGENT_TARGET = "local"

LOCAL_AGENTS = [
    ApifiedWebAgent(host="127.0.0.1", port=5000, id="browser_use_openai", name="Browser Use OpenAI", timeout=120),
    ApifiedWebAgent(host="127.0.0.1", port=5001, id="browser_use_anthropic", name="Browser Use Anthropic", timeout=120),
    ApifiedWebAgent(host="127.0.0.1", port=5002, id="browser_use_native", name="Browser Use Native", timeout=120),
    ApifiedWebAgent(host="127.0.0.1", port=5003, id="openai_cua", name="OpenAI CUA", timeout=120),
    ApifiedWebAgent(host="127.0.0.1", port=5004, id="anthropic_cua", name="Anthropic CUA", timeout=120),
    ApifiedWebAgent(host="127.0.0.1", port=5007, id="openclaw_cua", name="OpenClaw CUA", timeout=200),
]
REMOTE_AGENTS = [
    ApifiedWebAgent(id="openai_cua", name="OpenAI CUA", host="openai-cua-agent-sota.autoppia.com", port=80, timeout=120),
    ApifiedWebAgent(id="anthropic_cua", name="Anthropic CUA", host="anthropic-cua-agent-sota.autoppia.com", port=80, timeout=120),
    ApifiedWebAgent(id="browser_use", name="Browser Use", host="browser-use-agent-sota.autoppia.com", port=80, timeout=120),
    ApifiedWebAgent(id="browser_use_openai", name="Browser Use OpenAI", host="browser-use-openai-agent-sota.autoppia.com", port=80, timeout=120),
    ApifiedWebAgent(id="browser_use_anthropic", name="Browser Use Anthropic", host="browser-use-anthropic-agent-sota.autoppia.com", port=80, timeout=120),
]

AGENTS = REMOTE_AGENTS if AGENT_TARGET == "remote" else [LOCAL_AGENTS[5]]

# Projects and use cases (must exist in demo_web_projects / project use_cases)
PROJECT_IDS = ["autocinema"]
USE_CASES = None
DATA_EXTRACTION_USE_CASES = None

# =====================================================
# CONFIGURATION: Choose the evaluation mode here
# =====================================================

# Run config
# CFG = BenchmarkConfig(
#     projects=get_projects_by_ids(demo_web_projects, PROJECT_IDS),
#     agents=AGENTS,
#     agent_target=AGENT_TARGET,
#     evaluator_mode="stateful",
#     max_steps_per_task=50,
#     use_cached_tasks=False,
#     prompts_per_use_case=1,
#     use_cases=USE_CASES,
#     runs=1,
#     max_parallel_agent_calls=1,
#     record_gif=True,
#     dynamic=False,
#     save_results_json=True,
#     headless=True,
# )


CFG = BenchmarkConfig(
    projects=get_projects_by_ids(demo_web_projects, PROJECT_IDS),
    agents=AGENTS,
    # Evaluator mode
    evaluator_mode="concurrent",  # ← Agent generates full action list
    # Tasks
    prompts_per_use_case=1,
    # use_cases=None means all use-cases
    data_extraction_use_cases=DATA_EXTRACTION_USE_CASES,
    # use_cases=USE_CASES,
    # Execution
    runs=1,  # single run is enough for this fixed agent
    max_parallel_agent_calls=1,  # limit concurrency to avoid overloading agents
    record_gif=False,  # if your evaluator returns GIFs
    # Dynamic mode: disabled for this simple fixed-task test to avoid seed constraints.
    dynamic=True,
    # Persistence
    save_results_json=True,
    headless=True,  # Show Chromium window (set True or omit to use EVALUATOR_HEADLESS env)
)


def main():
    setup_logging(str(CFG.benchmark_log_file))
    if not CFG.projects:
        logger.error("No projects. Set PROJECT_IDS.")
        return
    if not CFG.agents:
        logger.error("No agents. Set AGENTS.")
        return
    logger.info(f"Benchmark: {[p.name for p in CFG.projects]}, {len(CFG.agents)} agent(s)")
    asyncio.run(Benchmark(CFG).run())


if __name__ == "__main__":
    main()
