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

from autoppia_iwa.entrypoints.benchmark.utils.task_generation import get_projects_by_ids
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.demo_webs.config import demo_web_projects

from .config import WebVerificationConfig
from .web_verification_pipeline import WebVerificationPipeline


def _validate_url(url: str, url_type: str, errors: list[str], warnings: list[str]) -> None:
    """Validate a URL and add errors/warnings to the respective lists."""
    if not url:
        errors.append(f"❌ {url_type} URL is missing")
    elif not url.startswith(("https://", "http://")):
        warnings.append(f"⚠️  {url_type} URL doesn't start with http:// or https://")
    # Note: SonarCloud flags http:// as insecure, but we allow it for local development
    # In production, prefer https:// for security


def _validate_basic_project_info(web_project, errors: list[str]) -> None:
    """Validate basic project information (ID and name)."""
    if not web_project.id:
        errors.append("❌ Project ID is missing")
    if not web_project.name:
        errors.append("❌ Project name is missing")


def _validate_events(web_project, errors: list[str]) -> None:
    """Validate that events are defined for the project."""
    if not web_project.events:
        errors.append("❌ No events defined for this project")
    else:
        logger.info(f"✓ Found {len(web_project.events)} events defined")


def _validate_use_cases_basic(web_project, errors: list[str]) -> None:
    """Validate that use cases are defined for the project."""
    if not web_project.use_cases:
        errors.append("❌ No use cases defined for this project")
    else:
        logger.info(f"✓ Found {len(web_project.use_cases)} use cases")


def _check_event_in_registry(use_case, event_class_name: str) -> tuple[bool, bool]:
    """
    Check if event is in registry and if it's valid.
    Returns: (is_in_registry, is_valid)
    """
    from autoppia_iwa.src.demo_webs.projects.base_events import EventRegistry

    try:
        registered_event = EventRegistry.get_event_class(event_class_name)
        is_valid = registered_event.__name__ == use_case.event.__name__
        return True, is_valid
    except (KeyError, ValueError):
        return False, False


def _validate_use_case_events(web_project, errors: list[str]) -> None:
    """Validate that each use case has a valid event associated."""
    use_cases_without_events = []
    use_cases_with_invalid_events = []
    events_not_in_registry = []

    for use_case in web_project.use_cases:
        if not use_case.event:
            use_cases_without_events.append(use_case.name)
        else:
            event_class_name = use_case.event.__name__ if hasattr(use_case.event, "__name__") else str(use_case.event)
            is_in_registry, is_valid = _check_event_in_registry(use_case, event_class_name)
            if not is_in_registry:
                events_not_in_registry.append(f"{use_case.name} -> {event_class_name}")
            elif not is_valid:
                use_cases_with_invalid_events.append(f"{use_case.name} (event: {event_class_name})")

    if use_cases_without_events:
        errors.append(f"❌ Use cases without events: {', '.join(use_cases_without_events)}")

    if use_cases_with_invalid_events:
        errors.append(f"❌ Use cases with invalid events: {', '.join(use_cases_with_invalid_events)}")

    if events_not_in_registry:
        errors.append(f"❌ Events not found in registry: {', '.join(events_not_in_registry)}")


def _validate_use_case_events_in_project(web_project, warnings: list[str]) -> None:
    """Validate that use case events are in the project events list."""
    project_event_names = {evt.__name__ for evt in web_project.events}
    use_case_event_names = set()

    for use_case in web_project.use_cases:
        if use_case.event:
            event_name = use_case.event.__name__ if hasattr(use_case.event, "__name__") else str(use_case.event)
            use_case_event_names.add(event_name)

    missing_events = use_case_event_names - project_event_names
    if missing_events:
        warnings.append(f"⚠️  Some use case events not in project events list: {', '.join(missing_events)}")


def _validate_use_case_examples(web_project, warnings: list[str]) -> None:
    """Validate that use cases have examples."""
    use_cases_without_examples = []
    for use_case in web_project.use_cases:
        if not use_case.examples or len(use_case.examples) == 0:
            use_cases_without_examples.append(use_case.name)

    if use_cases_without_examples:
        warnings.append(f"⚠️  Use cases without examples: {', '.join(use_cases_without_examples)}")


def _display_validation_summary(web_project, errors: list[str], warnings: list[str]) -> None:
    """Display validation summary (errors, warnings, or success)."""
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
    _validate_basic_project_info(web_project, errors)

    # 2. Validate URLs
    _validate_url(web_project.frontend_url, "Frontend", errors, warnings)
    _validate_url(web_project.backend_url, "Backend", errors, warnings)

    # 3. Validate events are defined
    _validate_events(web_project, errors)

    # 4. Validate use cases are defined
    _validate_use_cases_basic(web_project, errors)

    # 5-7. Validate use case details if use cases exist
    if web_project.use_cases:
        _validate_use_case_events(web_project, errors)
        _validate_use_case_events_in_project(web_project, warnings)
        _validate_use_case_examples(web_project, warnings)

    # 8. Display summary
    _display_validation_summary(web_project, errors, warnings)

    return len(errors) == 0, errors + warnings


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
