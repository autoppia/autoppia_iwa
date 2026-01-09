"""
Script to run the Web Verification Pipeline

Usage from terminal:
    python -m autoppia_iwa.entrypoints.web_verification.run --project-id <project_id> [options]

Usage from PyCharm:
    Set up a run configuration with:
    - Script path: path/to/autoppia_iwa/autoppia_iwa/entrypoints/web_verification/run.py
    - Parameters: --project-id <project_id> [options]
    - Working directory: path/to/autoppia_iwa
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directories to path for both terminal and PyCharm execution
# This ensures imports work regardless of how the script is invoked
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parents[4]  # Go up from entrypoints/web_verification/ to project root

# Add project root to path if not already there
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.task_generation import get_projects_by_ids
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.demo_webs.config import demo_web_projects

from .config import WebVerificationConfig
from .web_verification_pipeline import WebVerificationPipeline


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run web verification pipeline for a specific web project")

    parser.add_argument(
        "--project-id",
        type=str,
        required=True,
        help="ID of the web project to verify (e.g., 'autocinema_1', 'autobooks_2')",
    )

    parser.add_argument(
        "--tasks-per-use-case",
        type=int,
        default=2,
        help="Number of tasks to generate per use case (default: 2)",
    )

    parser.add_argument(
        "--dynamic",
        action="store_true",
        default=True,
        help="Enable dynamic seed generation (default: True)",
    )

    parser.add_argument(
        "--no-llm-review",
        action="store_true",
        help="Disable LLM review of tasks and tests",
    )

    parser.add_argument(
        "--no-iwap",
        action="store_true",
        help="Disable IWAP doability check",
    )

    parser.add_argument(
        "--iwap-use-mock",
        action="store_true",
        help="Use mock IWAP API response instead of calling real API (for testing)",
    )

    parser.add_argument(
        "--no-dynamic-verification",
        action="store_true",
        help="Disable dynamic verification with different seeds",
    )

    parser.add_argument(
        "--iwap-url",
        type=str,
        default=None,
        help="Base URL for IWAP service (default: from env or config)",
    )

    parser.add_argument(
        "--seeds",
        type=str,
        default="1,50,100,200,300",
        help="Comma-separated list of seed values to test (default: 1,50,100,200,300)",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="./verification_results",
        help="Directory to save results (default: ./verification_results)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser.parse_args()


async def main():
    """Main entry point"""
    args = parse_args()

    # Setup logging
    if args.verbose:
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level="DEBUG",
        )
    else:
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            level="INFO",
        )

    # Bootstrap application
    AppBootstrap()

    # Parse seed values
    seed_values = [int(s.strip()) for s in args.seeds.split(",")]

    # Get project
    projects = get_projects_by_ids(demo_web_projects, [args.project_id])
    if not projects:
        logger.error(f"Project '{args.project_id}' not found")
        logger.info(f"Available projects: {[p.id for p in demo_web_projects]}")
        sys.exit(1)

    web_project = projects[0]
    logger.info(f"Verifying project: {web_project.name} ({web_project.id})")

    # Create config
    config = WebVerificationConfig(
        tasks_per_use_case=args.tasks_per_use_case,
        dynamic_enabled=args.dynamic,
        llm_review_enabled=not args.no_llm_review,
        iwap_enabled=not args.no_iwap,
        iwap_base_url=args.iwap_url,
        iwap_use_mock=args.iwap_use_mock,
        dynamic_verification_enabled=not args.no_dynamic_verification,
        seed_values=seed_values,
        output_dir=args.output_dir,
        verbose=args.verbose,
    )

    # Create and run pipeline
    pipeline = WebVerificationPipeline(
        web_project=web_project,
        config=config,
    )

    try:
        results = await pipeline.run()

        # Print summary
        print(pipeline.get_summary())

        # Exit with appropriate code
        # Check if all LLM reviews passed
        all_passed = True
        for use_case_data in results.get("use_cases", {}).values():
            reviews = use_case_data.get("llm_reviews", [])
            if reviews and not all(r.get("valid", False) for r in reviews):
                all_passed = False
                break

        sys.exit(0 if all_passed else 1)

    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Pipeline failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
