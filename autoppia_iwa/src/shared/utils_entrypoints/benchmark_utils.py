import sys
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.demo_webs.config import demo_web_projects


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark testing of web automation tasks.

    Attributes:
        web_project_number: The identifier number (1-based) of the specific web project to test.
                           Ignored if `run_all_web_projects` is True.
        run_all_web_projects: If True, all defined web projects will be executed sequentially,
                               overriding the `web_project_number`. This also implies ignoring
                               any potential indexing issues or errors encountered during the
                               execution of individual projects to ensure all are attempted.
        use_cached_tasks: Whether to utilize previously saved tasks from the cache.
        use_cached_solutions: Whether to utilize previously saved solutions from the cache.
        evaluate_real_tasks: Whether to perform evaluation against real-world, as opposed to
                              synthetically generated, tasks.
        m: The number of duplicate evaluations to run for each generated solution.
        prompts_per_url: The number of different prompts to generate for each unique URL being tested.
        num_of_urls: The total number of distinct URLs to include in the benchmark testing.
        prompt_per_use_case: The number of different prompts to generate for each defined use case
                               within a web project.
    """

    web_project_number: int = 1
    run_all_web_projects: bool = False
    use_cached_tasks: bool = False
    use_cached_solutions: bool = False
    evaluate_real_tasks: bool = False

    m: int = 1  # Number of copies of each solution to evaluate
    prompts_per_url: int = 1
    num_of_urls: int = 1
    prompt_per_use_case: int = 1

    # Paths
    base_dir: Path = PROJECT_BASE_DIR.parent
    data_dir: Path = base_dir / "data"
    tasks_cache_dir: Path = data_dir / "tasks_cache"
    solutions_cache_dir: Path = data_dir / "solutions_cache"
    output_dir: Path = base_dir / "results"

    @property
    def current_web_project_index(self) -> int:
        """Get the 0-based index of the selected web project.

        Returns:
            The 0-based index corresponding to the 1-based project number

        Raises:
            ValueError: If web_project_number is invalid
        """
        if not isinstance(self.web_project_number, int) or self.web_project_number < 1:
            raise ValueError(f"Invalid web project number {self.web_project_number}, must be a positive integer.")
        return self.web_project_number - 1

    @property
    def selected_project(self):
        """Get the selected web project object.

        Returns:
            The web project object corresponding to web_project_number

        Raises:
            ValueError: If no project matches the web_project_number
        """
        if self.run_all_web_projects:
            return None
        try:
            return demo_web_projects[self.current_web_project_index]
        except IndexError as e:
            available = self.get_available_project_numbers()
            raise ValueError(f"Invalid web project number {self.web_project_number}. Available projects: {available}") from e

    @property
    def all_projects_to_run(self) -> list:
        """Get the list of all web projects when run_all_web_projects is True.

        Returns:
            A list of all demo web project objects.
        """
        if self.run_all_web_projects:
            return demo_web_projects[:]
        return []

    @staticmethod
    def get_available_project_numbers() -> list[int]:
        """Get list of available web project numbers.

        Returns:
            List of valid 1-based project numbers
        """
        return list(range(1, len(demo_web_projects) + 1))

    def __post_init__(self):
        """Initializes the configuration by validating the project number,
        creating necessary directories, and logging the current settings.
        """
        self._validate_project_number_format()
        self._create_directories()
        self._log_configuration()
        if not self.run_all_web_projects:
            self._validate_project_existence()

    def _validate_project_number_format(self):
        """Validates that the web project number is a positive integer."""
        if not isinstance(self.web_project_number, int) or self.web_project_number < 1:
            raise ValueError(f"Invalid web project number format: {self.web_project_number}, must be a positive integer.")

    def _validate_project_existence(self):
        """Confirms that the specified web project number corresponds to an existing project."""
        try:
            _ = self.current_web_project_index
            _ = self.selected_project
        except ValueError:
            raise

    def _create_directories(self):
        """Create all required directories if they don't exist."""
        for directory in (self.tasks_cache_dir, self.solutions_cache_dir, self.output_dir):
            directory.mkdir(parents=True, exist_ok=True)
            logger.trace(f"Ensured directory exists: {directory}")

    def _log_configuration(self):
        """Outputs the current benchmark configuration settings for informational purposes."""
        logger.info("Benchmark Configuration:")
        if self.run_all_web_projects:
            logger.info("  Mode: Running ALL web projects")
            logger.debug("  The web_project_number will not be accessible now.")
        else:
            logger.info(f"  Web Project: #{self.web_project_number} - {self.selected_project.name}")
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
