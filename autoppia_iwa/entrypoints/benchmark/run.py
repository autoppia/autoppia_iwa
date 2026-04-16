"""
Benchmark: evaluate agents on demo-web tasks (stateful or concurrent).

Default execution (no flags):
    python -m autoppia_iwa.entrypoints.benchmark.run

CLI execution (optional overrides):
    python -m autoppia_iwa.entrypoints.benchmark.run -t data_extraction_only -p autocinema -d EXTRACT_MOVIES
"""

import argparse
import asyncio
from collections.abc import Sequence
from typing import Literal

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.utils.logging import setup_logging
from autoppia_iwa.entrypoints.benchmark.utils.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents import ApifiedWebAgent

TaskTypes = Literal["both", "event_only", "data_extraction_only"]

# -----------------------------------------------------------------------------
# Configuration — defaults used when CLI flags are not provided
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

# Projects and use cases
PROJECT_IDS = ["autocinema"]
USE_CASES = None
DATA_EXTRACTION_USE_CASES = None
TASK_TYPES: TaskTypes = "both"

# Execution defaults
EVALUATOR_MODE = "concurrent"
PROMPTS_PER_USE_CASE = 1
RUNS = 1
MAX_PARALLEL_AGENT_CALLS = 1
RECORD_GIF = False
DYNAMIC = True
SAVE_RESULTS_JSON = True
HEADLESS = True


def _split_csv(values: str | None) -> list[str]:
    if not values:
        return []
    return [v.strip() for v in values.split(",") if v and v.strip()]


def _unique_preserving_order(items: Sequence[str]) -> list[str]:
    seen = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _resolve_optional_list(default_value: list[str] | None, csv_value: str | None, repeated_values: list[str] | None) -> list[str] | None:
    cli_values = _split_csv(csv_value)
    if repeated_values:
        cli_values.extend([item.strip() for item in repeated_values if item and item.strip()])
    if cli_values:
        return _unique_preserving_order(cli_values)
    if default_value is None:
        return None
    return list(default_value)


def _resolve_task_toggles(task_types: TaskTypes) -> tuple[bool, bool]:
    if task_types == "event_only":
        return True, False
    if task_types == "data_extraction_only":
        return False, True
    return True, True


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run benchmark for event tasks, data extraction tasks, or both.",
    )
    parser.add_argument(
        "-t",
        "--task-types",
        choices=("both", "event_only", "data_extraction_only"),
        default=None,
        help="Choose which task pipelines run. Default: use TASK_TYPES from run.py",
    )
    # Backward-compatible alias requested by previous workflow.
    parser.add_argument(
        "--test",
        dest="task_types_legacy",
        choices=("both", "event_only", "data_extraction_only"),
        default=None,
        help=argparse.SUPPRESS,
    )

    parser.add_argument(
        "--project-ids",
        type=str,
        default=None,
        help="Comma-separated project ids (example: autocinema,autobooks)",
    )
    parser.add_argument(
        "-p",
        "--project-id",
        action="append",
        dest="project_id",
        default=None,
        help="Repeatable project id flag (example: -p autocinema -p autobooks)",
    )

    parser.add_argument(
        "-u",
        "--use-cases",
        type=str,
        default=None,
        help="Comma-separated EventTask use cases",
    )
    parser.add_argument(
        "-U",
        "--use-case",
        action="append",
        dest="use_case",
        default=None,
        help="Repeatable EventTask use case flag",
    )

    parser.add_argument(
        "-d",
        "--data-extraction-use-cases",
        type=str,
        default=None,
        help="Comma-separated DataExtraction use cases",
    )
    parser.add_argument(
        "-D",
        "--de-use-case",
        action="append",
        dest="de_use_case",
        default=None,
        help="Repeatable DataExtraction use case flag",
    )

    return parser.parse_args(argv)


def build_config(args: argparse.Namespace | None = None) -> BenchmarkConfig:
    selected_task_types: TaskTypes = TASK_TYPES
    project_ids = list(PROJECT_IDS)
    use_cases = USE_CASES
    data_extraction_use_cases = DATA_EXTRACTION_USE_CASES

    if args is not None:
        selected_task_types = args.task_types or args.task_types_legacy or TASK_TYPES
        project_ids = _resolve_optional_list(PROJECT_IDS, args.project_ids, args.project_id) or []
        use_cases = _resolve_optional_list(USE_CASES, args.use_cases, args.use_case)
        data_extraction_use_cases = _resolve_optional_list(
            DATA_EXTRACTION_USE_CASES,
            args.data_extraction_use_cases,
            args.de_use_case,
        )

    enable_event_tasks, enable_data_extraction_tasks = _resolve_task_toggles(selected_task_types)

    return BenchmarkConfig(
        projects=get_projects_by_ids(demo_web_projects, project_ids),
        agents=AGENTS,
        evaluator_mode=EVALUATOR_MODE,
        prompts_per_use_case=PROMPTS_PER_USE_CASE,
        use_cases=use_cases,
        data_extraction_use_cases=data_extraction_use_cases,
        enable_event_tasks=enable_event_tasks,
        enable_data_extraction_tasks=enable_data_extraction_tasks,
        runs=RUNS,
        max_parallel_agent_calls=MAX_PARALLEL_AGENT_CALLS,
        record_gif=RECORD_GIF,
        dynamic=DYNAMIC,
        save_results_json=SAVE_RESULTS_JSON,
        headless=HEADLESS,
    )


# Backward-compatible default config export for modules that import CFG directly.
CFG = build_config()


def main(argv: Sequence[str] | None = None):
    args = parse_args(argv)
    cfg = build_config(args)

    setup_logging(str(cfg.benchmark_log_file))
    if not cfg.projects:
        logger.error("No projects. Set PROJECT_IDS in run.py or pass --project-id / --project-ids.")
        return
    if not cfg.agents:
        logger.error("No agents. Set AGENTS in run.py.")
        return

    strategy_names = []
    if cfg.enable_event_tasks:
        strategy_names.append("event")
    if cfg.enable_data_extraction_tasks:
        strategy_names.append("data_extraction")

    logger.info(
        f"Benchmark: projects={[p.id for p in cfg.projects]} pipelines={strategy_names} event_use_cases={cfg.use_cases} data_extraction_use_cases={cfg.data_extraction_use_cases} agents={len(cfg.agents)}"
    )

    asyncio.run(Benchmark(cfg).run())


if __name__ == "__main__":
    main()
