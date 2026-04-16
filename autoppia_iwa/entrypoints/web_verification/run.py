"""
Run web verification pipeline for a project.

Usage from terminal:
    python -m autoppia_iwa.entrypoints.web_verification.run -p <project_id> [options]

Usage from PyCharm:
    Set up a run configuration with:
    - Script path: path/to/autoppia_iwa/autoppia_iwa/entrypoints/web_verification/run.py
    - Parameters: -p <project_id> [options]
    - Working directory: path/to/autoppia_iwa
"""

import argparse
import asyncio


def _parse_args():
    parser = argparse.ArgumentParser(prog="iwa verify", description="Run web verification pipeline")
    parser.add_argument("--project", "-p", type=str, required=True, help="Project ID")
    parser.add_argument(
        "-p",
        "--project-id",
        type=str,
        action="append",
        dest="use_case",
        help="Restrict verification to this use case (repeat for multiple); same as iwa benchmark",
    )
    parser.add_argument("--output", "-o", type=str, default="./verification_results")
    parser.add_argument("--tasks-per-use-case", type=int, default=2)
    parser.add_argument("--seeds", type=str, default="1,50,100,200,300")
    parser.add_argument("--no-llm-review", action="store_true")
    parser.add_argument(
        "-n",
        "--tasks-per-use-case",
        type=int,
        default=2,
        help="Number of tasks to generate per use case (default: 2)",
    )

    parser.add_argument(
        "--dynamic",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable or disable dynamic seed generation (default: enabled)",
    )

    parser.add_argument(
        "--no-llm-review",
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
    parser.add_argument(
        "--no-event-trajectory-verification",
        action="store_true",
        help="Disable event trajectories verification",
    )

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

    parser.add_argument(
        "-i",
        "--iwap-url",
        type=str,
        default=None,
        help="Base URL for IWAP service (default: from env or config)",
    )

    parser.add_argument(
        "-s",
        "--seeds",
        type=str,
        default="1,50,100,200,300",
        help="Comma-separated list of seed values to test (default: 1,50,100,200,300)",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default="./verification_results",
        help="Directory to save results (default: ./verification_results)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

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
        tasks_per_use_case=args.tasks_per_use_case,
        dynamic_enabled=args.dynamic,
        llm_review_enabled=not args.no_llm_review,
        iwap_enabled=not args.no_iwap,
        iwap_base_url=args.iwap_url,
        iwap_use_mock=args.iwap_use_mock,
        dynamic_verification_enabled=not args.no_dynamic_verification,
        event_trajectory_verification_enabled=not args.no_event_trajectory_verification,
        data_extraction_verification_enabled=not args.no_data_extraction_verification,
        data_extraction_seed=args.data_extraction_seed,
        seed_values=seed_values,
        output_dir=args.output_dir,
        verbose=args.verbose,
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
        results = await pipeline.run()

        # Print summary
        print(pipeline.get_summary())

        # Exit with appropriate code
        # Check if all required checks passed (LLM reviews + executed DE verification)
        all_passed = True
        for use_case_data in results.get("use_cases", {}).values():
            reviews = use_case_data.get("llm_reviews", [])
            if reviews and not all(r.get("valid", False) for r in reviews):
                all_passed = False
                break

        data_extraction = results.get("data_extraction_project_verification", {})
        if isinstance(data_extraction, dict):
            skipped = data_extraction.get("skipped", False)
            if not skipped and data_extraction.get("all_passed") is False:
                all_passed = False

        event_trajectory = results.get("event_trajectory_project_verification", {})
        if isinstance(event_trajectory, dict):
            skipped = event_trajectory.get("skipped", False)
            if not skipped and event_trajectory.get("all_passed") is False:
                all_passed = False

        data_extraction_task_generation = results.get("data_extraction_task_generation_verification", {})
        if isinstance(data_extraction_task_generation, dict):
            skipped = data_extraction_task_generation.get("skipped", False)
            if not skipped and data_extraction_task_generation.get("all_passed") is False:
                all_passed = False

        sys.exit(0 if all_passed else 1)

    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Pipeline failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
