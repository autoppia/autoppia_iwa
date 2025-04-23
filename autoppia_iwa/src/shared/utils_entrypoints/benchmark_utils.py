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
        web_project_number (Required): The identifier number of the web project to test (not list index)
        use_cached_tasks: Whether to use previously cached tasks
        use_cached_solutions: Whether to use previously cached solutions
        evaluate_real_tasks: Whether to evaluate against real-world tasks
        m: Number of copies of each solution to evaluate
        prompts_per_url: Number of prompts to generate per URL
        num_of_urls: Number of URLs to include in testing
        prompt_per_use_case: Number of prompts per use case
    """

    web_project_number: int
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
        try:
            return demo_web_projects[self.current_web_project_index]
        except IndexError as e:
            available = self.get_available_project_numbers()
            raise ValueError(f"Invalid web project number {self.web_project_number}. Available projects: {available}") from e

    @staticmethod
    def get_available_project_numbers() -> list[int]:
        """Get list of available web project numbers.

        Returns:
            List of valid 1-based project numbers
        """
        return list(range(1, len(demo_web_projects) + 1))

    def __post_init__(self):
        """Initialize and validate configuration."""
        self._validate_project_number()
        self._create_directories()
        self._log_configuration()

    def _validate_project_number(self):
        """Validate that the web project number is valid."""
        # The property access will automatically validate
        _ = self.current_web_project_index
        _ = self.selected_project

    def _create_directories(self):
        """Create all required directories if they don't exist."""
        for directory in (self.tasks_cache_dir, self.solutions_cache_dir, self.output_dir):
            directory.mkdir(parents=True, exist_ok=True)
            logger.trace(f"Ensured directory exists: {directory}")

    def _log_configuration(self):
        """Log the current configuration."""
        logger.info("Benchmark Configuration:")
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
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # File logging
    logger.add(log_file, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}", rotation="10 MB", retention="7 days")
