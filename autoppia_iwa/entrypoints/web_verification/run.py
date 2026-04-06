"""
Run web verification pipeline for a project.

Usage:
    python -m autoppia_iwa.entrypoints.web_verification.run --project autocinema
    iwa verify -p autocinema
"""

import argparse
import asyncio


def _parse_args():
    parser = argparse.ArgumentParser(prog="iwa verify", description="Run web verification pipeline")
    parser.add_argument("--project", "-p", type=str, required=True, help="Project ID")
    parser.add_argument("--output", "-o", type=str, default="./verification_results")
    parser.add_argument("--tasks-per-use-case", type=int, default=2)
    parser.add_argument("--seeds", type=str, default="1,50,100,200,300")
    parser.add_argument("--no-llm-review", action="store_true")
    parser.add_argument(
        "--evaluate-trajectories",
        action="store_true",
        help="Replay repo-local trajectories (autolist, autodrive, autohealth) through the evaluator",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    return parser.parse_args()


async def run(
    project_id: str,
    output_dir: str = "./verification_results",
    tasks_per_use_case: int = 2,
    seeds: str = "1,50,100,200,300",
    no_llm_review: bool = False,
    verbose: bool = False,
    evaluate_trajectories: bool = False,
):
    from autoppia_iwa.src.bootstrap import AppBootstrap
    from autoppia_iwa.src.demo_webs.config import demo_web_projects
    from autoppia_iwa.src.demo_webs.web_verification.config import WebVerificationConfig
    from autoppia_iwa.src.demo_webs.web_verification.pipeline import WebVerificationPipeline
    from autoppia_iwa.src.evaluation.benchmark.utils.task_generation import get_projects_by_ids

    AppBootstrap()

    projects = get_projects_by_ids(demo_web_projects, [project_id])
    if not projects:
        raise ValueError(f"Project IDs not found: ['{project_id}']")
    project = projects[0]

    config = WebVerificationConfig(
        tasks_per_use_case=tasks_per_use_case,
        llm_review_enabled=not no_llm_review,
        seed_values=[int(s.strip()) for s in seeds.split(",")],
        output_dir=output_dir,
        verbose=verbose,
        evaluate_trajectories=evaluate_trajectories,
    )

    pipeline = WebVerificationPipeline(web_project=project, config=config)
    results = await pipeline.run()
    print(pipeline.get_summary())
    return results


def main():
    args = _parse_args()
    raise SystemExit(asyncio.run(_main_async(args)))


async def _main_async(args) -> int:
    try:
        await run(
            project_id=args.project,
            output_dir=args.output,
            tasks_per_use_case=args.tasks_per_use_case,
            seeds=args.seeds,
            no_llm_review=args.no_llm_review,
            verbose=args.verbose,
            evaluate_trajectories=args.evaluate_trajectories,
        )
    except ValueError as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    main()
