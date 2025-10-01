from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.web_agents.base import IWebAgent


@dataclass(slots=True)
class BenchmarkConfig:
    """
    Central configuration used by the Benchmark orchestrator.
    Configure everything in code (no CLI required).
    """

    projects: list[WebProject] = field(default_factory=list)
    agents: list[IWebAgent] = field(default_factory=list)

    # Task generation
    use_cached_tasks: bool = False
    prompts_per_use_case: int = 1
    num_use_cases: int = 0  # 0 = use all available use-cases

    # Execution
    runs: int = 1
    max_parallel_agent_calls: int = 1
    use_cached_solutions: bool = False
    record_gif: bool = False

    # Persistence / plotting
    save_results_json: bool = True
    plot_results: bool = False

    # Visualization
    enable_visualization: bool = True

    # Paths
    base_dir: Path = field(default_factory=lambda: PROJECT_BASE_DIR.parent)
    data_dir: Path = field(init=False)
    tasks_cache_dir: Path = field(init=False)
    solutions_cache_dir: Path = field(init=False)
    output_dir: Path = field(init=False)
    recordings_dir: Path = field(init=False)

    def __post_init__(self):
        """
        Prepare directory structure used by the benchmark.
        """
        # Validate required fields
        if not self.projects:
            logger.warning("No projects configured - benchmark will not run")

        if not self.agents:
            logger.warning("No agents configured - benchmark will not run")

        self.data_dir = self.base_dir / "data"
        self.tasks_cache_dir = self.data_dir / "tasks_cache"
        self.solutions_cache_dir = self.data_dir / "solutions_cache"
        self.output_dir = self.base_dir / "results"
        self.recordings_dir = PROJECT_BASE_DIR / "recordings"

        # Create directories with proper error handling
        for d in (self.tasks_cache_dir, self.solutions_cache_dir, self.output_dir, self.recordings_dir):
            try:
                d.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured directory exists: {d}")
            except Exception as e:
                logger.error(f"Failed to create directory {d}: {e}")
                raise
