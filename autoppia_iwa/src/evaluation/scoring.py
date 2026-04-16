from __future__ import annotations

from dataclasses import dataclass

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.evaluation.shared.utils import run_partial_tests
from autoppia_iwa.src.execution.classes import ActionExecutionResult


@dataclass
class ScoreDetails:
    raw_score: float = 0.0
    tests_passed: int = 0
    total_tests: int = 0
    success: bool = False


class TaskExecutionScorer:
    """Compute score details from an execution history."""

    async def score(self, project: WebProject | None, task: Task, history: list[ActionExecutionResult]) -> ScoreDetails:
        if not project:
            return ScoreDetails()
        matrix = await run_partial_tests(project, task, history)
        if not matrix:
            return ScoreDetails()
        last = matrix[-1] if matrix else []
        passed = sum(1 for result in last if getattr(result, "success", False))
        total = len(last)
        raw = (passed / total) if total > 0 else 0.0
        return ScoreDetails(
            raw_score=raw,
            tests_passed=passed,
            total_tests=total,
            success=(total > 0 and passed == total),
        )
