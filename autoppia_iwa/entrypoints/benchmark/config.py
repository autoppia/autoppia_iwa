from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.execution.dynamic import DynamicPhaseConfig
from autoppia_iwa.src.web_agents.base import IWebAgent


@dataclass(slots=True)
class BenchmarkConfig:
    """
    Central configuration used by the Benchmark orchestrator.
    Configure everything in code (no CLI required).

    Key groups:
      • Task generation (use_cached_tasks, prompts_per_use_case, num_use_cases, use_cases)
      • Execution controls (runs, max_parallel_agent_calls, use_cached_solutions, record_gif, enable_dynamic_html)
      • Persistence (save_results_json, plot_results, directory fields resolved in __post_init__)
      • Visualization toggles (enable_visualization, dynamic_phase_config shared with evaluator)
    """

    projects: list[WebProject] = field(default_factory=list)
    agents: list[IWebAgent] = field(default_factory=list)
    use_cases: list[str] | None = None

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

    # Dynamic features: array of v1, v2, v3 (or combinations)
    # v1 = assign seed, v2 = assign v2-seed, v3 = assign seed structure
    dynamic: bool = False
    # Dynamic HTML
    dynamic_phase_config: DynamicPhaseConfig | None = None

    # Visualization
    enable_visualization: bool = True

    # Paths
    base_dir: Path = field(default_factory=lambda: PROJECT_BASE_DIR.parent)
    benchmark_dir: Path = field(init=False)
    cache_dir: Path = field(init=False)
    data_dir: Path = field(init=False)
    tasks_cache_dir: Path = field(init=False)
    solutions_cache_dir: Path = field(init=False)
    output_dir: Path = field(init=False)
    per_project_results: Path = field(init=False)
    logs_dir: Path = field(init=False)
    benchmark_log_file: Path = field(init=False)
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

        # Use outputs/ directory for all generated artifacts
        outputs_dir = self.base_dir / "outputs"
        self.benchmark_dir = outputs_dir / "benchmark"
        self.cache_dir = self.benchmark_dir / "cache"

        self.tasks_cache_dir = self.cache_dir / "tasks"
        self.solutions_cache_dir = self.cache_dir / "solutions"

        self.output_dir = self.benchmark_dir / "results"
        self.per_project_results = self.benchmark_dir / "per_project"
        self.logs_dir = self.benchmark_dir / "logs"
        self.benchmark_log_file = self.logs_dir / "benchmark.log"
        self.recordings_dir = self.benchmark_dir / "recordings"

        # Create directories with proper error handling
        for d in (
            self.benchmark_dir,
            self.cache_dir,
            self.tasks_cache_dir,
            self.solutions_cache_dir,
            self.output_dir,
            self.per_project_results,
            self.logs_dir,
            self.recordings_dir,
        ):
            try:
                d.mkdir(parents=True, exist_ok=True)
                # logger.debug(f"Ensured directory exists: {d}")
            except Exception as e:
                logger.error(f"Failed to create directory {d}: {e}")
                raise
