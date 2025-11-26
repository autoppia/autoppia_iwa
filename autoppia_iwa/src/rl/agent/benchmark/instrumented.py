from __future__ import annotations

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.web_agents.classes import TaskSolution

from ..evaluators.instrumented import InstrumentationConfig, JsInstrumentedEvaluator


class InstrumentedBenchmark(Benchmark):
    """Benchmark variant that replaces the evaluator with the JS-instrumented version."""

    def __init__(self, config, instrumentation: InstrumentationConfig | None = None):
        super().__init__(config)
        self._instrumentation = instrumentation or InstrumentationConfig()

    async def _evaluate_solutions_for_task(
        self,
        project: WebProject,
        task: Task,
        solutions: list[TaskSolution | None],
        run_index: int,
    ):  # type: ignore[override]
        valid_solutions = [s for s in solutions if s is not None]
        if not valid_solutions:
            return []

        evaluator = JsInstrumentedEvaluator(
            project,
            EvaluatorConfig(enable_grouping_tasks=False, chunk_size=20, should_record_gif=self.config.record_gif),
            instrumentation=self._instrumentation,
        )
        results = await evaluator.evaluate_task_solutions(task, valid_solutions)

        if self.config.record_gif:
            for res in results:
                if getattr(res, "gif_recording", None):
                    agent_name = next((a.name for a in self.config.agents if a.id == res.web_agent_id), "unknown")
                    self._persist_gif_recording(res.gif_recording, agent_name, task.id, run_index, self.config.recordings_dir)
        return results
