"""
Script to run the Web Verification Pipeline

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
import os
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

from autoppia_iwa.entrypoints.benchmark.utils.logging import setup_logging
from autoppia_iwa.entrypoints.benchmark.utils.task_generation import get_projects_by_ids
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.demo_webs.config import demo_web_projects

from .config import WebVerificationConfig
from .web_verification_pipeline import WebVerificationPipeline


def _is_development() -> bool:
    """True when running in local development (DEMO_WEBS_DEPLOYMENT=local)."""
    return os.environ.get("DEMO_WEBS_DEPLOYMENT", "").lower() in ("local")


def validate_project_setup(web_project) -> tuple[bool, list[str]]:
    """
    Validate that the project is correctly configured before running the pipeline.

    This function checks:
    - Project has ID and name
    - URLs are valid
    - Events are defined
    - Use cases are defined
    - Each use case has a valid event associated
    - Events are registered in the EventRegistry
    - Use case events match project events list

    Args:
        web_project: The WebProject instance to validate

    Returns:
        Tuple[bool, list[str]]: (is_valid, list_of_messages)
            - is_valid: True if no critical errors found
            - list_of_messages: List of error and warning messages
    """
    errors = []
    warnings = []

    # 1. Validate project has ID and name
    if not web_project.id:
        errors.append("❌ Project ID is missing")
    if not web_project.name:
        errors.append("❌ Project name is missing")

    # 2. Validate URLs (https only when not local; http allowed when DEMO_WEBS_DEPLOYMENT=local)
    is_development = _is_development()
    allowed_schemes = ("http://") if is_development else ("https://",)
    if not web_project.frontend_url:
        errors.append("❌ Frontend URL is missing")
    elif not web_project.frontend_url.startswith(allowed_schemes):
        warnings.append("⚠️  Frontend URL should start with https://" if not is_development else "⚠️  Frontend URL should start with http:// or https://")

    if not web_project.backend_url:
        errors.append("❌ Backend URL is missing")
    elif not web_project.backend_url.startswith(allowed_schemes):
        warnings.append("⚠️  Backend URL should start with https://" if not is_development else "⚠️  Backend URL should start with http:// or https://")

    # 3. Validate events are defined
    if not web_project.events:
        errors.append("❌ No events defined for this project")
    else:
        logger.info(f"✓ Found {len(web_project.events)} events defined")

    # 4. Validate use cases are defined
    if not web_project.use_cases:
        errors.append("❌ No use cases defined for this project")
    else:
        logger.info(f"✓ Found {len(web_project.use_cases)} use cases")

        # 5. Validate each use case has an event associated
        from autoppia_iwa.src.demo_webs.projects.base_events import EventRegistry

        use_cases_without_events = []
        use_cases_with_invalid_events = []
        events_not_in_registry = []

        for use_case in web_project.use_cases:
            if not use_case.event:
                use_cases_without_events.append(use_case.name)
            else:
                # Check that the event is in the registry
                event_class_name = use_case.event.__name__ if hasattr(use_case.event, "__name__") else str(use_case.event)
                try:
                    registered_event = EventRegistry.get_event_class(event_class_name)
                    # Compare by class name, not by object identity (same class may have different instances)
                    if registered_event.__name__ != use_case.event.__name__:
                        use_cases_with_invalid_events.append(f"{use_case.name} (event: {event_class_name})")
                except (KeyError, ValueError):
                    events_not_in_registry.append(f"{use_case.name} -> {event_class_name}")

        if use_cases_without_events:
            errors.append(f"❌ Use cases without events: {', '.join(use_cases_without_events)}")

        if use_cases_with_invalid_events:
            errors.append(f"❌ Use cases with invalid events: {', '.join(use_cases_with_invalid_events)}")

        if events_not_in_registry:
            errors.append(f"❌ Events not found in registry: {', '.join(events_not_in_registry)}")

        # 6. Validate that use case events are in the project events list
        project_event_names = {evt.__name__ for evt in web_project.events}
        use_case_event_names = set()

        for use_case in web_project.use_cases:
            if use_case.event:
                event_name = use_case.event.__name__ if hasattr(use_case.event, "__name__") else str(use_case.event)
                use_case_event_names.add(event_name)

        missing_events = use_case_event_names - project_event_names
        if missing_events:
            warnings.append(f"⚠️  Some use case events not in project events list: {', '.join(missing_events)}")

        # 7. Validate use cases have examples
        use_cases_without_examples = []
        for use_case in web_project.use_cases:
            if not use_case.examples or len(use_case.examples) == 0:
                use_cases_without_examples.append(use_case.name)

        if use_cases_without_examples:
            warnings.append(f"⚠️  Use cases without examples: {', '.join(use_cases_without_examples)}")

    # 8. Display summary
    if errors:
        logger.error("=" * 80)
        logger.error("PROJECT VALIDATION FAILED")
        logger.error("=" * 80)
        for error in errors:
            logger.error(error)
        logger.error("=" * 80)

    if warnings:
        logger.warning("=" * 80)
        logger.warning("PROJECT VALIDATION WARNINGS")
        logger.warning("=" * 80)
        for warning in warnings:
            logger.warning(warning)
        logger.warning("=" * 80)

    if not errors:
        logger.info("=" * 80)
        logger.info("✓ PROJECT VALIDATION PASSED")
        logger.info("=" * 80)
        logger.info(f"Project: {web_project.name} ({web_project.id})")
        logger.info(f"Events: {len(web_project.events) if web_project.events else 0}")
        logger.info(f"Use Cases: {len(web_project.use_cases) if web_project.use_cases else 0}")
        logger.info(f"Frontend: {web_project.frontend_url}")
        logger.info(f"Backend: {web_project.backend_url}")
        logger.info("=" * 80)

    return len(errors) == 0, errors + warnings


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run web verification pipeline for a specific web project")

    parser.add_argument(
        "-p",
        "--project-id",
        type=str,
        required=True,
        help="ID of the web project to verify (e.g., 'autocinema_1', 'autobooks_2')",
    )

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
        "--no-data-extraction-verification",
        action="store_true",
        help="Disable data-extraction trajectories verification",
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


async def main():
    """Main entry point"""
    args = parse_args()

    # Standardized logging (same format as benchmark: YYYY-MM-DD HH:mm:ss.SSS, single handler, no duplicates)
    log_dir = Path(args.output_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "web_verification.log"
    setup_logging(str(log_file), console_level="DEBUG" if args.verbose else "INFO")

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

    # Validate project setup before proceeding
    logger.info("=" * 80)
    logger.info("🔍 VALIDATING PROJECT SETUP")
    logger.info("=" * 80)

    is_valid, _ = validate_project_setup(web_project)
    if not is_valid:
        logger.error("❌ Project validation failed. Please fix the errors before running the pipeline.")
        sys.exit(1)

    logger.info("✓ Project validation passed. Proceeding with verification pipeline...")
    logger.info("")
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
        data_extraction_verification_enabled=not args.no_data_extraction_verification,
        data_extraction_seed=args.data_extraction_seed,
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
    asyncio.run(main())
