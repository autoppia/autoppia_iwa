"""
Run benchmark against a web agent.

Default execution (no flags):
    python -m autoppia_iwa.entrypoints.benchmark.run

CLI execution (optional overrides):
    python -m autoppia_iwa.entrypoints.benchmark.run -t data_extraction_only -p autocinema -d EXTRACT_MOVIES
"""

import argparse
import asyncio
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from autoppia_iwa.config.env import init_env

init_env()

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.utils.logging import setup_logging
from autoppia_iwa.entrypoints.benchmark.utils.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents import ApifiedWebAgent
from autoppia_iwa.src.web_agents.examples.random_clicker.agent import RandomClickerWebAgent

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

AGENTS = (
    REMOTE_AGENTS
    if AGENT_TARGET == "remote"
    else [
        RandomClickerWebAgent(
            id="random-clicker",
            name="Random Clicker Zero Baseline",
            is_random=False,
        )
    ]
)

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
SMOKE_TASKS_TEMPLATE = Path(__file__).resolve().parent / "fixtures" / "random_clicker_zero_smoke.json"


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


def _build_agent(agent: str):
    """Build a benchmark agent from a friendly name or an HTTP base URL."""
    normalized = agent.strip()
    if normalized in {"random-clicker", "random", "random_clicker"}:
        return RandomClickerWebAgent(
            id="random-clicker",
            name="Random Clicker Zero Baseline",
            is_random=False,
        )
    return ApifiedWebAgent(base_url=normalized, name=f"agent@{normalized}")


def _materialize_smoke_tasks_json() -> Path:
    """Create an env-specific smoke tasks file from the bundled fixture."""
    template = json.loads(SMOKE_TASKS_TEMPLATE.read_text(encoding="utf-8"))
    projects_by_id = {project.id: project for project in demo_web_projects}
    autocinema = projects_by_id["autocinema"]

    for task in template.get("tasks", []):
        task["url"] = autocinema.frontend_url

    output_path = Path(__file__).resolve().parents[3] / "benchmark-output" / "smoke" / "random_clicker_zero_smoke.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(template, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


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
    parser.add_argument(
        "--agent",
        type=str,
        default=None,
        help="Agent to benchmark: 'random-clicker' or an HTTP base URL. Default: random-clicker",
    )
    parser.add_argument(
        "--agent-target",
        choices=("local", "remote"),
        default=None,
        help="Use configured local/default agents or configured remote agents. Ignored when --agent is set.",
    )
    parser.add_argument(
        "--tasks-json",
        type=str,
        default=None,
        help="Use a pre-generated tasks JSON file instead of generating tasks with an LLM.",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run the built-in random-clicker zero-score smoke benchmark. No external agent or LLM needed.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=None,
        help=f"Runs per task. Default: {RUNS}",
    )
    parser.add_argument(
        "-n",
        "--prompts-per-use-case",
        type=int,
        default=None,
        help=f"Generated prompts per use case. Default: {PROMPTS_PER_USE_CASE}",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=None,
        help=f"Maximum parallel agent calls. Default: {MAX_PARALLEL_AGENT_CALLS}",
    )
    parser.add_argument(
        "--mode",
        choices=("concurrent", "stateful"),
        default=None,
        help=f"Evaluator mode. Default: {EVALUATOR_MODE}",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=None,
        help="Maximum steps per task in stateful mode.",
    )
    parser.add_argument(
        "--record-gif",
        action="store_true",
        default=None,
        help="Record GIFs for benchmark executions.",
    )
    parser.add_argument(
        "--dynamic",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=f"Enable seed-based dynamic web variations. Default: {DYNAMIC}",
    )
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=f"Run browser evaluation headless. Default: {HEADLESS}",
    )

    return parser.parse_args(argv)


def build_config(args: argparse.Namespace | None = None) -> BenchmarkConfig:
    selected_task_types: TaskTypes = TASK_TYPES
    project_ids = list(PROJECT_IDS)
    use_cases = USE_CASES
    data_extraction_use_cases = DATA_EXTRACTION_USE_CASES
    agents = AGENTS
    evaluator_mode = EVALUATOR_MODE
    prompts_per_use_case = PROMPTS_PER_USE_CASE
    runs = RUNS
    max_parallel_agent_calls = MAX_PARALLEL_AGENT_CALLS
    record_gif = RECORD_GIF
    dynamic = DYNAMIC
    headless = HEADLESS
    max_steps_per_task = 50
    tasks_json_path = None

    if args is not None:
        if args.smoke:
            selected_task_types = "event_only"
            project_ids = ["autocinema"]
            agents = [_build_agent("random-clicker")]
            evaluator_mode = "concurrent"
            runs = 1
            max_parallel_agent_calls = 1
            record_gif = False
            dynamic = False
            headless = True
            tasks_json_path = str(_materialize_smoke_tasks_json())

        selected_task_types = args.task_types or args.task_types_legacy or selected_task_types
        project_ids = _resolve_optional_list(project_ids, args.project_ids, args.project_id) or []
        use_cases = _resolve_optional_list(USE_CASES, args.use_cases, args.use_case)
        data_extraction_use_cases = _resolve_optional_list(
            DATA_EXTRACTION_USE_CASES,
            args.data_extraction_use_cases,
            args.de_use_case,
        )
        if args.agent:
            agents = [_build_agent(args.agent)]
        elif args.agent_target == "remote":
            agents = REMOTE_AGENTS
        elif args.agent_target == "local":
            agents = AGENTS
        evaluator_mode = args.mode or evaluator_mode
        prompts_per_use_case = args.prompts_per_use_case if args.prompts_per_use_case is not None else prompts_per_use_case
        runs = args.runs if args.runs is not None else runs
        max_parallel_agent_calls = args.parallel if args.parallel is not None else max_parallel_agent_calls
        record_gif = args.record_gif if args.record_gif is not None else record_gif
        dynamic = args.dynamic if args.dynamic is not None else dynamic
        headless = args.headless if args.headless is not None else headless
        max_steps_per_task = args.max_steps if args.max_steps is not None else max_steps_per_task
        tasks_json_path = args.tasks_json or tasks_json_path

    enable_event_tasks, enable_data_extraction_tasks = _resolve_task_toggles(selected_task_types)

    return BenchmarkConfig(
        projects=get_projects_by_ids(demo_web_projects, project_ids),
        agents=agents,
        evaluator_mode=evaluator_mode,
        prompts_per_use_case=prompts_per_use_case,
        use_cases=use_cases,
        data_extraction_use_cases=data_extraction_use_cases,
        enable_event_tasks=enable_event_tasks,
        enable_data_extraction_tasks=enable_data_extraction_tasks,
        runs=runs,
        max_parallel_agent_calls=max_parallel_agent_calls,
        record_gif=record_gif,
        dynamic=dynamic,
        save_results_json=SAVE_RESULTS_JSON,
        headless=headless,
        max_steps_per_task=max_steps_per_task,
        tasks_json_path=tasks_json_path,
    )


# Backward-compatible default config export for modules that import CFG directly.
CFG = build_config()


def _write_staged_tasks(cache_dir: Path, payload: dict) -> None:
    pid = str(payload.get("project_id", "unknown"))
    is_data_extraction_cache = "dataextraction" in cache_dir.as_posix().lower()
    suffix = "_DE_tasks.json" if is_data_extraction_cache else "_tasks.json"
    (cache_dir / f"{pid}{suffix}").write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str))


def _stage_tasks(tasks_path: Path, config) -> None:
    """Compatibility helper to stage tasks JSON in benchmark cache."""
    test_types = getattr(config, "test_types", None)
    if test_types is None:
        enable_event = bool(getattr(config, "enable_event_tasks", True))
        enable_de = bool(getattr(config, "enable_data_extraction_tasks", False))
        test_types = "data_extraction_only" if (enable_de and not enable_event) else "event_only"

    sub = "DataExtraction" if test_types == "data_extraction_only" else "tasks"
    cache_dir = config.base_dir / "benchmark-output" / "cache" / sub
    cache_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(tasks_path.read_text())
    if "project_id" in data and "tasks" in data:
        _write_staged_tasks(cache_dir, data)
        return

    if isinstance(data, dict):
        wrote = False
        for payload in data.values():
            if isinstance(payload, dict) and "project_id" in payload and "tasks" in payload:
                _write_staged_tasks(cache_dir, payload)
                wrote = True
        if wrote:
            return

    raise ValueError(f"Unsupported tasks file format: {tasks_path}")


async def run(
    agent: str,
    project_ids: list[str] | None = None,
    use_cases: list[str] | None = None,
    tasks_file: str | None = None,
    output_dir: str = "./benchmark-output",
    mode: str = "stateful",
    max_steps: int = 50,
    prompts_per_use_case: int = 1,
    runs: int = 1,
    parallel: int = 1,
    web_agent_prefix: str = "benchmark-agent",
    validator_prefix: str | None = None,
    headless: bool = True,
    *,
    test_types: str = "event_only",
):
    """
    Legacy programmatic API kept for compatibility with existing tests/callers.
    Internally mapped to the modern benchmark runtime under entrypoints/benchmark.
    """
    from autoppia_iwa.src.bootstrap import AppBootstrap

    AppBootstrap()

    if mode != "stateful":
        raise ValueError("Only stateful benchmark mode is supported. Concurrent evaluation has moved to autoppia_iwa.src.evaluation.legacy.")

    projects = get_projects_by_ids(demo_web_projects, project_ids) if project_ids else demo_web_projects
    web_agent = _build_agent(agent)

    base_dir = Path(output_dir)
    if base_dir.name == "benchmark-output":
        base_dir = base_dir.parent

    enable_event_tasks = test_types != "data_extraction_only"
    enable_data_extraction_tasks = test_types == "data_extraction_only"
    data_extraction_use_cases = use_cases if test_types == "data_extraction_only" else None

    config = BenchmarkConfig(
        projects=projects,
        agents=[web_agent],
        evaluator_mode="stateful",
        use_cases=use_cases,
        prompts_per_use_case=prompts_per_use_case,
        max_steps_per_task=max_steps,
        runs=runs,
        max_parallel_agent_calls=parallel,
        dynamic=DYNAMIC,
        save_results_json=SAVE_RESULTS_JSON,
        record_gif=RECORD_GIF,
        headless=bool(headless),
        base_dir=base_dir,
        use_cached_tasks=bool(tasks_file),
        enable_event_tasks=enable_event_tasks,
        enable_data_extraction_tasks=enable_data_extraction_tasks,
        data_extraction_use_cases=data_extraction_use_cases,
    )

    if tasks_file:
        _stage_tasks(Path(tasks_file), config)

    benchmark = Benchmark(config)
    results = await benchmark.run()
    last_run_report = getattr(benchmark, "last_run_report", None)
    return last_run_report or results or {}


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Default parser for current benchmark CLI; monkeypatch target for compatibility tests."""
    return parse_args(argv)


async def _main_async_legacy(args: argparse.Namespace) -> int:
    """Compatibility async main for legacy positional-agent argument object."""
    try:
        await run(
            agent=args.agent,
            project_ids=args.project,
            use_cases=args.use_case,
            tasks_file=args.tasks,
            output_dir=args.output,
            max_steps=args.max_steps,
            prompts_per_use_case=args.prompts_per_use_case,
            runs=args.runs,
            parallel=args.parallel,
            web_agent_prefix=args.web_agent_prefix,
            validator_prefix=args.validator_prefix,
            headless=args.headless,
            test_types=args.test_types,
        )
    except ValueError as exc:
        print(str(exc))
        return 1
    return 0


def main(argv: Sequence[str] | None = None):
    args = _parse_args() if argv is None else _parse_args(argv)

    # Compatibility path (legacy API/tests monkeypatch this object shape).
    if hasattr(args, "project") and hasattr(args, "tasks"):
        raise SystemExit(asyncio.run(_main_async_legacy(args)))

    cfg = build_config(args)

    setup_logging(str(cfg.benchmark_log_file))
    if not cfg.projects:
        logger.error("No projects. Set PROJECT_IDS in run.py or pass --project-id / --project-ids.")
        raise SystemExit(1)
    if not cfg.agents:
        logger.error("No agents. Set AGENTS in run.py.")
        raise SystemExit(1)

    strategy_names = []
    if cfg.enable_event_tasks:
        strategy_names.append("event")
    if cfg.enable_data_extraction_tasks:
        strategy_names.append("data_extraction")

    logger.info(
        f"Benchmark: projects={[p.id for p in cfg.projects]} pipelines={strategy_names} event_use_cases={cfg.use_cases} data_extraction_use_cases={cfg.data_extraction_use_cases} agents={len(cfg.agents)}"
    )

    asyncio.run(Benchmark(cfg).run())
    raise SystemExit(0)


if __name__ == "__main__":
    main()
