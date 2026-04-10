"""
Generate tasks and save to JSON.

Usage:
    python -m autoppia_iwa.entrypoints.generate_tasks.run
    python -m autoppia_iwa.entrypoints.generate_tasks.run -p autocinema -n 3 -o tasks.json
    iwa generate-tasks -p autocinema -o tasks.json
"""

import argparse
import asyncio
import json
from pathlib import Path


def _parse_args():
    parser = argparse.ArgumentParser(prog="iwa generate-tasks", description="Generate tasks to JSON")
    parser.add_argument("--project", "-p", type=str, action="append", help="Project ID(s)")
    parser.add_argument("--use-case", "-u", type=str, action="append", help="Use case filter")
    parser.add_argument("--prompts-per-use-case", "-n", type=int, default=2)
    parser.add_argument("--output", "-o", type=str, default="tasks.json")
    parser.add_argument("--dynamic", action="store_true", default=False)
    return parser.parse_args()


def _require_llm_credentials() -> None:
    """Task generation needs an LLM; load .env first, then validate provider credentials."""
    from autoppia_iwa.config.config import HAS_CHUTES_CREDENTIALS, HAS_OPENAI_CREDENTIALS, LLM_PROVIDER

    if LLM_PROVIDER == "openai" and not HAS_OPENAI_CREDENTIALS:
        raise ValueError(
            "OPENAI_API_KEY is not set. Task generation calls an LLM.\n"
            "  • Export OPENAI_API_KEY, or\n"
            "  • Set LLM_PROVIDER=chutes with CHUTES_API_KEY (and CHUTES_BASE_URL if needed), or\n"
            "  • Add credentials to a .env file in the autoppia_iwa repo root (see .env.example)."
        )
    if LLM_PROVIDER == "chutes" and not HAS_CHUTES_CREDENTIALS:
        raise ValueError("CHUTES_API_KEY is not set while LLM_PROVIDER=chutes. Set CHUTES_API_KEY in your environment or .env (see .env.example).")


async def run(
    project_ids: list[str] | None = None,
    use_cases: list[str] | None = None,
    prompts_per_use_case: int = 2,
    output: str = "tasks.json",
    dynamic: bool = False,
):
    from autoppia_iwa.config.env import init_env

    init_env()
    _require_llm_credentials()

    from autoppia_iwa.src.bootstrap import AppBootstrap
    from autoppia_iwa.src.data_generation.tasks.classes import TaskGenerationConfig
    from autoppia_iwa.src.data_generation.tasks.pipeline import TaskGenerationPipeline
    from autoppia_iwa.src.demo_webs.config import demo_web_projects
    from autoppia_iwa.src.evaluation.benchmark.utils.task_generation import get_projects_by_ids

    AppBootstrap()

    projects = get_projects_by_ids(demo_web_projects, project_ids) if project_ids else demo_web_projects
    output_path = Path(output)

    all_tasks = {}
    for project in projects:
        print(f"Generating tasks for {project.name}...")
        config = TaskGenerationConfig(
            prompts_per_use_case=prompts_per_use_case,
            use_cases=use_cases,
            dynamic=dynamic,
        )
        tasks = await TaskGenerationPipeline(web_project=project, config=config).generate()
        all_tasks[project.id] = {
            "project_id": project.id,
            "project_name": project.name,
            "tasks": [t.serialize() for t in tasks],
        }
        print(f"  {len(tasks)} tasks generated")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(all_tasks, indent=2, ensure_ascii=False, default=str))
    print(f"\nSaved to {output_path}")
    return all_tasks


def main():
    args = _parse_args()
    raise SystemExit(asyncio.run(_main_async(args)))


async def _main_async(args) -> int:
    try:
        await run(
            project_ids=args.project,
            use_cases=args.use_case,
            prompts_per_use_case=args.prompts_per_use_case,
            output=args.output,
            dynamic=args.dynamic,
        )
    except ValueError as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    main()
