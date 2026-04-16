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
    parser.add_argument(
        "--project",
        "--project-id",
        "-p",
        dest="project",
        type=str,
        required=True,
        help="Project ID",
    )
    parser.add_argument(
        "--use-case",
        "-u",
        type=str,
        action="append",
        dest="use_case",
        help="Restrict verification to this use case (repeat for multiple); same as iwa benchmark",
    )
    parser.add_argument("--output", "--output-dir", "-o", type=str, default="./verification_results")
    parser.add_argument("--tasks-per-use-case", "-n", type=int, default=2)
    parser.add_argument("--seeds", "-s", type=str, default="1,50,100,200,300")
    parser.add_argument("--dynamic", action=argparse.BooleanOptionalAction, default=True, help="Enable/disable dynamic seed generation")
    parser.add_argument("--no-llm-review", action="store_true")
    parser.add_argument(
        "--evaluate-trajectories",
        action="store_true",
        help="Also replay repo-local trajectories after the normal pipeline (requires OPENAI_API_KEY for task generation)",
    )
    parser.add_argument(
        "--trajectories-only",
        action="store_true",
        help="Trajectory replay only: skips task generation, LLM, bulk V2 dataset seed sweep, and IWAP (no OPENAI_API_KEY)",
    )
    parser.add_argument(
        "--no-trajectory-doability",
        action="store_true",
        help="Do not use registered trajectories for Step 3 reference solution; use IWAP only when IWAP is enabled",
    )
    parser.add_argument("--no-iwap", action="store_true", help="Disable IWAP doability check")
    parser.add_argument("--iwap-use-mock", action="store_true", help="Use mock IWAP response instead of real API")
    parser.add_argument("--iwap-url", "-i", type=str, default=None, help="Base URL for IWAP service")
    parser.add_argument("--no-dynamic-verification", action="store_true", help="Disable dynamic verification with different seeds")
    parser.add_argument("--no-event-trajectory-verification", action="store_true", help="Disable event trajectories verification")
    parser.add_argument(
        "--no-data-extraction-verification",
        action="store_true",
        help="Disable data-extraction verification (trajectories and task-generation checks)",
    )
    parser.add_argument(
        "--data-extraction-seed",
        type=int,
        default=1,
        help="Seed value used to select data-extraction trajectories (default: 1)",
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
    trajectories_only: bool = False,
    trajectory_doability_enabled: bool = True,
    use_cases: list[str] | None = None,
    *,
    dynamic_enabled: bool = True,
    iwap_enabled: bool = True,
    iwap_base_url: str | None = None,
    iwap_use_mock: bool = False,
    dynamic_verification_enabled: bool = True,
    no_event_trajectory_verification: bool = False,
    no_data_extraction_verification: bool = False,
    data_extraction_seed: int = 1,
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
        use_case_filter=use_cases,
        tasks_per_use_case=tasks_per_use_case,
        dynamic_enabled=dynamic_enabled,
        llm_review_enabled=(not trajectories_only) and (not no_llm_review),
        trajectory_doability_enabled=trajectory_doability_enabled,
        iwap_enabled=(not trajectories_only) and iwap_enabled,
        iwap_base_url=iwap_base_url,
        iwap_use_mock=iwap_use_mock,
        dynamic_verification_enabled=dynamic_verification_enabled,
        seed_values=[int(s.strip()) for s in seeds.split(",")],
        output_dir=output_dir,
        verbose=verbose,
        evaluate_trajectories=evaluate_trajectories or trajectories_only,
        evaluate_trajectories_only=trajectories_only,
        event_trajectory_verification_enabled=not no_event_trajectory_verification,
        data_extraction_verification_enabled=not no_data_extraction_verification,
        data_extraction_seed=int(data_extraction_seed),
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
            trajectories_only=args.trajectories_only,
            trajectory_doability_enabled=not args.no_trajectory_doability,
            use_cases=args.use_case,
            dynamic_enabled=getattr(args, "dynamic", True),
            iwap_enabled=not getattr(args, "no_iwap", False),
            iwap_base_url=getattr(args, "iwap_url", None),
            iwap_use_mock=getattr(args, "iwap_use_mock", False),
            dynamic_verification_enabled=not getattr(args, "no_dynamic_verification", False),
            no_event_trajectory_verification=getattr(args, "no_event_trajectory_verification", False),
            no_data_extraction_verification=args.no_data_extraction_verification,
            data_extraction_seed=args.data_extraction_seed,
        )
    except ValueError as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    main()
