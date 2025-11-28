from __future__ import annotations

import time
from collections.abc import Iterable

from loguru import logger
from pydantic import BaseModel, Field

try:
    from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
    from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
except ModuleNotFoundError:  # pragma: no cover - source-tree fallback
    from autoppia_iwa.autoppia_iwa.src.evaluation.classes import EvaluatorConfig
    from autoppia_iwa.autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator

from .agent_client import RemoteAgentClient
from .config import AffineEnvConfig
from .dataset import TaskEntry


class TaskEvaluationDetail(BaseModel):
    affine_id: int
    task_id: str
    project_id: str
    project_name: str
    score: float
    raw_score: float
    success: bool
    tests_passed: int
    total_tests: int
    action_count: int
    solution_actions: int
    evaluation_time: float
    web_agent_id: str | None = None
    error: str | None = None
    gif_recording: bool = Field(default=False, description="True when a GIF is attached to the evaluation result.")


class EvaluationRunner:
    """Runs validator-grade evaluations against miner task solutions."""

    def __init__(self, config: AffineEnvConfig):
        self.config = config

    def _build_evaluator_config(self) -> EvaluatorConfig:
        return EvaluatorConfig(
            task_delay_in_seconds=0.1,
            chunk_size=5,
            browser_timeout=self.config.browser_timeout,
            enable_grouping_tasks=False,
            verbose_logging=self.config.verbose_logging,
            debug_mode=False,
            should_record_gif=self.config.should_record_gif,
        )

    async def evaluate_tasks(
        self,
        entries: Iterable[TaskEntry],
        client: RemoteAgentClient,
    ) -> list[TaskEvaluationDetail]:
        details: list[TaskEvaluationDetail] = []
        for entry in entries:
            details.append(await self._evaluate_entry(entry, client))
        return details

    async def _evaluate_entry(self, entry: TaskEntry, client: RemoteAgentClient) -> TaskEvaluationDetail:
        start_time = time.perf_counter()
        try:
            solution = await client.solve_task(entry.task)
        except Exception as exc:
            logger.exception("Failed to fetch solution from miner for task %s", entry.task.id)
            return TaskEvaluationDetail(
                affine_id=entry.affine_id,
                task_id=entry.task.id,
                project_id=entry.project.id,
                project_name=entry.project.name,
                score=0.0,
                raw_score=0.0,
                success=False,
                tests_passed=0,
                total_tests=0,
                action_count=0,
                solution_actions=0,
                evaluation_time=time.perf_counter() - start_time,
                web_agent_id=client.web_agent_name,
                error=str(exc),
            )

        evaluator = ConcurrentEvaluator(entry.project, self._build_evaluator_config())
        try:
            result = await evaluator.evaluate_single_task_solution(entry.task, solution)
        except Exception as exc:
            logger.exception("Evaluation failed for task %s", entry.task.id)
            return TaskEvaluationDetail(
                affine_id=entry.affine_id,
                task_id=entry.task.id,
                project_id=entry.project.id,
                project_name=entry.project.name,
                score=0.0,
                raw_score=0.0,
                success=False,
                tests_passed=0,
                total_tests=0,
                action_count=len(solution.actions),
                solution_actions=len(solution.actions),
                evaluation_time=time.perf_counter() - start_time,
                web_agent_id=solution.web_agent_id,
                error=str(exc),
            )

        stats = result.stats
        tests_passed = stats.tests_passed if stats else 0
        total_tests = stats.total_tests if stats else 0
        action_count = stats.action_count if stats else len(solution.actions)
        success = bool(result.final_score > 0 and tests_passed == total_tests and not (stats and stats.had_errors))

        return TaskEvaluationDetail(
            affine_id=entry.affine_id,
            task_id=entry.task.id,
            project_id=entry.project.id,
            project_name=entry.project.name,
            score=float(result.final_score),
            raw_score=float(result.raw_score),
            success=success,
            tests_passed=tests_passed,
            total_tests=total_tests,
            action_count=action_count,
            solution_actions=len(solution.actions),
            evaluation_time=time.perf_counter() - start_time,
            web_agent_id=solution.web_agent_id,
            error=None,
            gif_recording=bool(result.gif_recording),
        )
