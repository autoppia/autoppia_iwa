from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from loguru import logger

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.web_agents.classes import IWebAgent


@dataclass(slots=True)
class BenchmarkConfig:
    """
    Central configuration used by the Benchmark orchestrator.
    Configure everything in code (no CLI required).

    Key groups:
      • Task generation (prompts_per_use_case, use_cases)
      • Execution controls (runs, max_parallel_agent_calls, record_gif, dynamic)
      • Persistence (save_results_json, directory fields resolved in __post_init__)
    """

    agents: list[IWebAgent] = field(default_factory=list)
    # Task generation
    projects: list[WebProject] = field(default_factory=list)
    use_cases: list[str] | None = None
    prompts_per_use_case: int = 1
    dynamic: bool = False

    # Execution
    runs: int = 1
    max_parallel_agent_calls: int = 1
    record_gif: bool = False

    # Evaluator mode
    # "concurrent": El agente genera todas las acciones de una vez (modo tradicional)
    # "stateful": El agente decide paso a paso viendo el estado del browser (iterativo)
    evaluator_mode: Literal["concurrent", "stateful"] = "concurrent"

    # Solo para modo stateful: límite de pasos por tarea
    max_steps_per_task: int = 50

    # Persistence / plotting
    save_results_json: bool = True

    # Paths
    base_dir: Path = field(default_factory=lambda: PROJECT_BASE_DIR.parent)
    output_dir: Path = field(init=False)
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

        # Validate evaluator mode
        if self.evaluator_mode not in ("concurrent", "stateful"):
            raise ValueError(f"Invalid evaluator_mode: {self.evaluator_mode}. Must be 'concurrent' or 'stateful'.")

        if self.evaluator_mode == "stateful" and self.max_steps_per_task <= 0:
            raise ValueError("max_steps_per_task must be > 0 when using stateful mode.")

        # Use benchmark-output/ directory for all generated artifacts
        benchmark_dir = self.base_dir / "benchmark-output"

        self.output_dir = benchmark_dir / "results"
        self.benchmark_log_file = benchmark_dir / "logs" / "benchmark.log"
        self.recordings_dir = benchmark_dir / "recordings"

        # Create directories with proper error handling
        for d in (
            self.output_dir,
            self.benchmark_log_file.parent,  # Create logs directory
            self.recordings_dir,
        ):
            try:
                d.mkdir(parents=True, exist_ok=True)
                # logger.debug(f"Ensured directory exists: {d}")
            except Exception as e:
                logger.error(f"Failed to create directory {d}: {e}")
                raise
