"""
Run benchmark against a web agent.

Usage:
    python -m autoppia_iwa.entrypoints.benchmark.run http://localhost:8000
    python -m autoppia_iwa.entrypoints.benchmark.run random-clicker
    python -m autoppia_iwa.entrypoints.benchmark.run http://localhost:8000 -p autocinema -u login
    iwa benchmark http://localhost:8000
"""

import argparse
import asyncio
import json
from pathlib import Path


def _parse_args():
    parser = argparse.ArgumentParser(prog="iwa benchmark", description="Run benchmark against a web agent")
    parser.add_argument("agent", type=str, help="Agent base URL or local preset (e.g. http://localhost:8000, random-clicker)")
    parser.add_argument("--project", "-p", type=str, action="append", help="Project ID(s)")
    parser.add_argument("--use-case", "-u", type=str, action="append", help="Use case(s)")
    parser.add_argument("--tasks", "-t", type=str, help="Load tasks from JSON file")
    parser.add_argument("--output", "-o", type=str, default=".", help="Base directory where benchmark-output/ will be created")
    parser.add_argument("--max-steps", type=int, default=50)
    parser.add_argument("--prompts-per-use-case", "-n", type=int, default=1)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--parallel", "-j", type=int, default=1, help="Max parallel evaluations (browsers)")
    parser.add_argument("--web-agent-prefix", type=str, default="benchmark-agent", help="Prefix used to generate unique web_agent_id values per evaluation")
    parser.add_argument("--validator-prefix", type=str, default=None, help="Prefix used to generate unique validator_id values per evaluation")
    parser.add_argument("--headless", action="store_true", default=True)
    parser.add_argument("--no-headless", dest="headless", action="store_false")
    return parser.parse_args()


def _build_agent(agent: str):
    from autoppia_iwa.src.web_agents import ApifiedWebAgent
    from autoppia_iwa.src.web_agents.examples.random_clicker.agent import RandomClickerWebAgent

    normalized = agent.strip()
    if normalized in {"random-clicker", "random", "random_clicker"}:
        return RandomClickerWebAgent(id="random-clicker", name="Random Clicker")
    return ApifiedWebAgent(base_url=normalized, name=f"agent@{normalized}")


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
):
    from autoppia_iwa.src.bootstrap import AppBootstrap
    from autoppia_iwa.src.demo_webs.config import demo_web_projects
    from autoppia_iwa.src.evaluation.benchmark import Benchmark, BenchmarkConfig
    from autoppia_iwa.src.evaluation.benchmark.utils.task_generation import get_projects_by_ids

    AppBootstrap()

    if mode != "stateful":
        raise ValueError("Only stateful benchmark mode is supported. Concurrent evaluation has moved to autoppia_iwa.src.evaluation.legacy.")

    projects = get_projects_by_ids(demo_web_projects, project_ids) if project_ids else demo_web_projects
    web_agent = _build_agent(agent)

    base_dir = Path(output_dir)
    if base_dir.name == "benchmark-output":
        base_dir = base_dir.parent

    config = BenchmarkConfig(
        projects=projects,
        agents=[web_agent],
        use_cases=use_cases,
        prompts_per_use_case=prompts_per_use_case,
        max_steps_per_task=max_steps,
        runs=runs,
        max_parallel_evaluations=parallel,
        web_agent_id_prefix=web_agent_prefix,
        validator_id_prefix=validator_prefix or "validator_001",
        headless=headless,
        base_dir=base_dir,
        use_cached_tasks=bool(tasks_file),
    )

    if tasks_file:
        _stage_tasks(Path(tasks_file), config)

    benchmark = Benchmark(config)
    await benchmark.run()
    return benchmark.last_run_report or {}


def _stage_tasks(tasks_path: Path, config):
    cache_dir = config.base_dir / "benchmark-output" / "cache" / "tasks"
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


def _write_staged_tasks(cache_dir: Path, payload: dict) -> None:
    pid = str(payload.get("project_id", "unknown"))
    (cache_dir / f"{pid}_tasks.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str))


def main():
    args = _parse_args()
    raise SystemExit(asyncio.run(_main_async(args)))


async def _main_async(args) -> int:
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
        )
    except ValueError as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    main()
