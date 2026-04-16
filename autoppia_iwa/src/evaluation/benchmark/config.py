from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from autoppia_iwa.config.config import PROJECT_BASE_DIR, VALIDATOR_ID

TestTypes = Literal["event_only", "data_extraction_only"]
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.web_agents.classes import IWebAgent


@dataclass(slots=True)
class BenchmarkConfig:
    """
    Configuration for the Benchmark runner.

    Usage:
        config = BenchmarkConfig(
            projects=[autocinema_project, autobooks_project],
            agents=[ApifiedWebAgent(base_url="http://localhost:8000")],
            use_cases=["login", "search"],       # None = all use cases
            prompts_per_use_case=2,
            evaluator_mode="stateful",
            max_steps_per_task=30,
        )
        benchmark = Benchmark(config)
        results = await benchmark.run()
    """

    # What to test
    projects: list[WebProject] = field(default_factory=list)
    agents: list[IWebAgent] = field(default_factory=list)
    use_cases: list[str] | None = None

    # Task generation
    prompts_per_use_case: int = 1
    dynamic: bool = False
    use_cached_tasks: bool = False
    # When "data_extraction_only", tasks and tests follow the data-extraction pipeline
    # (DataExtractionTest / DEtasks). Mirrors TaskGenerationConfig.test_types.
    test_types: TestTypes = "event_only"

    # Evaluation mode
    evaluator_mode: Literal["stateful"] = "stateful"
    max_steps_per_task: int = 50

    # Execution
    runs: int = 1
    max_parallel_evaluations: int = 1
    web_agent_id_prefix: str = "benchmark-agent"
    validator_id_prefix: str = VALIDATOR_ID or "validator_001"
    record_gif: bool = False
    headless: bool | None = None
    save_results_json: bool = True
    print_summary: bool = True

    # Paths (auto-resolved)
    base_dir: Path = field(default_factory=lambda: PROJECT_BASE_DIR.parent)
    output_dir: Path = field(init=False)
    log_file: Path = field(init=False)
    recordings_dir: Path = field(init=False)
    traces_dir: Path = field(init=False)

    def __post_init__(self):
        if self.evaluator_mode != "stateful":
            raise ValueError(f"Invalid evaluator_mode: {self.evaluator_mode}")
        if self.max_steps_per_task <= 0:
            raise ValueError("max_steps_per_task must be > 0 in stateful mode")
        if self.runs <= 0:
            raise ValueError("runs must be > 0")
        if self.max_parallel_evaluations <= 0:
            raise ValueError("max_parallel_evaluations must be > 0")
        if self.prompts_per_use_case <= 0:
            raise ValueError("prompts_per_use_case must be > 0")
        self.web_agent_id_prefix = str(self.web_agent_id_prefix or "benchmark-agent").strip() or "benchmark-agent"
        self.validator_id_prefix = str(self.validator_id_prefix or VALIDATOR_ID or "validator_001").strip() or "validator_001"

        benchmark_dir = self.base_dir / "benchmark-output"
        self.output_dir = benchmark_dir / "results"
        self.log_file = benchmark_dir / "logs" / "benchmark.log"
        self.recordings_dir = benchmark_dir / "recordings"
        self.traces_dir = benchmark_dir / "traces"

        for d in (self.output_dir, self.log_file.parent, self.recordings_dir, self.traces_dir):
            d.mkdir(parents=True, exist_ok=True)

    def serialize(self) -> dict[str, object]:
        return {
            "project_ids": [project.id for project in self.projects],
            "agent_ids": [agent.id for agent in self.agents],
            "use_cases": list(self.use_cases) if self.use_cases else None,
            "prompts_per_use_case": self.prompts_per_use_case,
            "dynamic": self.dynamic,
            "use_cached_tasks": self.use_cached_tasks,
            "test_types": self.test_types,
            "evaluator_mode": self.evaluator_mode,
            "max_steps_per_task": self.max_steps_per_task,
            "runs": self.runs,
            "max_parallel_evaluations": self.max_parallel_evaluations,
            "web_agent_id_prefix": self.web_agent_id_prefix,
            "validator_id_prefix": self.validator_id_prefix,
            "record_gif": self.record_gif,
            "headless": self.headless,
            "save_results_json": self.save_results_json,
        }
