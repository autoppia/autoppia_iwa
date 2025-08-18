import sys
from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.web_agents.base import IWebAgent


@dataclass(slots=True)
class BenchmarkConfig:
    """Global benchmark configuration (no inheritance)."""

    projects_to_run: list[WebProject] = field(default_factory=list)
    agents: list[IWebAgent] = field(default_factory=list)

    # Caching / execution modes
    use_cached_tasks: bool = False
    use_cached_solutions: bool = False
    evaluate_real_tasks: bool = False

    # Prompt generation
    prompt_per_use_case: int = 1
    num_of_use_cases: int = 0  # set to 0 if you want to run all

    # Runtime options
    num_runs: int = 1
    max_parallel_agent_calls: int = 1
    return_evaluation_gif: bool = False

    # Plotting / persistence
    plot_benchmark_results: bool = False
    save_evaluation_results: bool = True

    # Base paths
    base_dir: Path = field(default_factory=lambda: PROJECT_BASE_DIR.parent)
    data_dir: Path = field(init=False)
    tasks_cache_dir: Path = field(init=False)
    solutions_cache_dir: Path = field(init=False)
    output_dir: Path = field(init=False)
    recordings_dir: Path = field(init=False)

    def __post_init__(self):
        self.data_dir = self.base_dir / "data"
        self.tasks_cache_dir = self.data_dir / "tasks_cache"
        self.solutions_cache_dir = self.data_dir / "solutions_cache"
        self.output_dir = self.base_dir / "results"
        self.recordings_dir = PROJECT_BASE_DIR / "recordings"
        for directory in (
            self.tasks_cache_dir,
            self.solutions_cache_dir,
            self.output_dir,
            self.recordings_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)
            logger.trace("Ensured directory exists: %s", directory)


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
