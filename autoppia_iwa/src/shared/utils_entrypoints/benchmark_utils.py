import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeVar

from loguru import logger

from autoppia_iwa.config.config import PROJECT_BASE_DIR

try:
    from autoppia_iwa.src.demo_webs.classes import WebProject
except ImportError:
    WebProject = TypeVar("WebProject")  # type: ignore


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark testing of web automation tasks."""

    PROJECT_SELECTOR: str = "all"  # Can be "all", a single number "ID", or comma-separated "ID1,ID2"
    use_cached_tasks: bool = False
    use_cached_solutions: bool = False
    evaluate_real_tasks: bool = False

    m: int = 1  # Number of copies of each solution to evaluate
    prompts_per_url: int = 1
    num_of_urls: int = 1
    prompt_per_use_case: int = 1

    # Paths
    base_dir: Path = field(default_factory=lambda: PROJECT_BASE_DIR.parent)
    data_dir: Path = field(init=False)
    tasks_cache_dir: Path = field(init=False)
    solutions_cache_dir: Path = field(init=False)
    output_dir: Path = field(init=False)

    def __post_init__(self):
        """Initializes the configuration by validating selector format,
        creating necessary directories, and logging initial settings.
        """
        self.data_dir = self.base_dir / "data"
        self.tasks_cache_dir = self.data_dir / "tasks_cache"
        self.solutions_cache_dir = self.data_dir / "solutions_cache"
        self.output_dir = self.base_dir / "results"

        self._validate_project_selector_format()
        self._create_directories()
        self._log_initial_configuration()

    def _validate_project_selector_format(self):
        """Validates the basic format of PROJECT_SELECTOR."""
        selector = self.PROJECT_SELECTOR.strip().lower()
        if selector == "all" or not selector:  # Empty string means no projects
            return

        parts = selector.split(",")
        if not parts:
            raise ValueError("PROJECT_SELECTOR format error: selector is invalid (e.g. just a comma).")

        for part in parts:
            part = part.strip()
            if not part:  # Handles "1,,2"
                raise ValueError(f"Empty project number found in PROJECT_SELECTOR: '{self.PROJECT_SELECTOR}'.")
            if not part.isdigit():
                raise ValueError(f"Invalid part '{part}' in PROJECT_SELECTOR: '{self.PROJECT_SELECTOR}'. Must be 'all', a positive integer, or comma-separated positive integers.")
            if int(part) <= 0:
                raise ValueError(f"Project numbers in PROJECT_SELECTOR '{self.PROJECT_SELECTOR}' must be positive integers.")

    def get_projects_to_run(self, available_projects: list[WebProject]) -> list[WebProject]:
        """
        Determines which projects to run based on PROJECT_SELECTOR and the provided list of available projects.
        Returns a new list of WebProject objects.
        """
        selector = self.PROJECT_SELECTOR.strip().lower()
        project_count = len(available_projects)

        if selector == "all":
            if not available_projects:
                logger.info("PROJECT_SELECTOR is 'all', but no demo web projects are available/loaded.")
                return []
            return available_projects[:]

        if not selector:
            logger.info("PROJECT_SELECTOR is empty, no projects will be run.")
            return []

        selected_indices = set()
        parts = selector.split(",")

        for part_str in parts:
            part_str = part_str.strip()
            # Format validation (isdigit, >0) already done in _validate_project_selector_format
            project_number = int(part_str)  # 1-based

            if not (1 <= project_number <= project_count):
                raise ValueError(
                    f"Project number {project_number} (from selector '{self.PROJECT_SELECTOR}') is out of range. "
                    f"There are {project_count} available project(s) (numbered 1 to {project_count})."
                    f"\n{self.get_available_project_details_static(available_projects)}"
                )
            selected_indices.add(project_number - 1)  # Convert to 0-based index

        resolved_projects = [available_projects[i] for i in sorted(list(selected_indices))]
        if not resolved_projects and parts:  # if selector was not empty but resolved to no projects
            logger.warning(f"PROJECT_SELECTOR '{self.PROJECT_SELECTOR}' did not resolve to any projects from the available list of {project_count} project(s).")
        return resolved_projects

    @staticmethod
    def get_available_project_details_static(project_list: list[WebProject]) -> str:
        if not project_list:
            return "No demo web projects provided in the list."
        details = ["Available projects in the provided list:"]
        for i, project in enumerate(project_list):
            try:
                details.append(f"  {i + 1}: {getattr(project, 'name', 'Unnamed Project')} (ID: {getattr(project, 'id', 'N/A')})")
            except Exception:
                details.append(f"  {i + 1}: (Error accessing project details)")
        return "\n".join(details)

    def _create_directories(self):
        """Create all required directories if they don't exist."""
        for directory in (self.tasks_cache_dir, self.solutions_cache_dir, self.output_dir):
            directory.mkdir(parents=True, exist_ok=True)
            logger.trace(f"Ensured directory exists: {directory}")

    def _log_initial_configuration(self):
        """Outputs the initial benchmark configuration settings (without project list context)."""
        logger.info("Initial Benchmark Configuration (prior to project loading):")
        logger.info(f"  Project Selector: '{self.PROJECT_SELECTOR}'")
        logger.info(f"  Using cached tasks: {self.use_cached_tasks}")
        logger.info(f"  Using cached solutions: {self.use_cached_solutions}")
        logger.info(f"  Evaluation mode: {'Real tasks' if self.evaluate_real_tasks else 'Synthetic tasks'}")
        logger.debug(f"  Task replication factor (m): {self.m}")
        logger.debug(f"  Prompts per URL: {self.prompts_per_url}")
        logger.debug(f"  Number of URLs: {self.num_of_urls}")
        logger.debug(f"  Prompts per use case: {self.prompt_per_use_case}")


# ==================================
# ======= LOGGING SETUP ============
# ==================================
def setup_logging(log_file: str):
    """Configure loguru logger with enhanced formatting"""
    logger.remove()

    # Console logging with colors
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # File logging
    logger.add(log_file, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}", rotation="10 MB", retention="7 days")
