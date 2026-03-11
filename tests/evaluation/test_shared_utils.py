"""Unit tests for evaluation.shared.utils (display helpers)."""

from autoppia_iwa.src.evaluation.classes import EvaluationStats
from autoppia_iwa.src.evaluation.shared.utils import (
    display_batch_evaluation_summary,
    display_single_evaluation_summary,
)


def _make_stats(
    web_agent_id: str = "agent-1",
    task_id: str = "task-1",
    action_count: int = 3,
    start_time: float = 1000.0,
    total_time: float = 5.0,
    browser_setup_time: float = 1.0,
    action_execution_times: list[float] | None = None,
    test_execution_time: float = 0.5,
    random_clicker_time: float = 0.0,
    final_score: float = 0.8,
    raw_score: float = 0.8,
    tests_passed: int = 2,
    total_tests: int = 3,
    had_errors: bool = False,
    error_message: str = "",
    action_types: dict[str, int] | None = None,
) -> EvaluationStats:
    if action_execution_times is None:
        action_execution_times = [0.5, 0.3, 0.2]
    if action_types is None:
        action_types = {"click": 2, "type": 1}
    return EvaluationStats(
        web_agent_id=web_agent_id,
        task_id=task_id,
        action_count=action_count,
        action_types=action_types,
        start_time=start_time,
        total_time=total_time,
        browser_setup_time=browser_setup_time,
        action_execution_times=action_execution_times,
        test_execution_time=test_execution_time,
        random_clicker_time=random_clicker_time,
        raw_score=raw_score,
        final_score=final_score,
        tests_passed=tests_passed,
        total_tests=total_tests,
        had_errors=had_errors,
        error_message=error_message,
    )


class TestDisplaySingleEvaluationSummary:
    """Tests for display_single_evaluation_summary()."""

    def test_debug_mode_returns_without_error(self):
        stats = _make_stats()
        display_single_evaluation_summary(stats, debug_mode=True)

    def test_non_debug_mode_returns_without_error(self):
        stats = _make_stats()
        display_single_evaluation_summary(stats, debug_mode=False)

    def test_calls_get_summary_dict(self):
        stats = _make_stats()
        d = stats.get_summary_dict()
        assert "agent_id" in d and d["agent_id"] == stats.web_agent_id

    def test_with_errors_flag(self):
        stats = _make_stats(had_errors=True, error_message="Something failed")
        display_single_evaluation_summary(stats, debug_mode=True)


class TestDisplayBatchEvaluationSummary:
    """Tests for display_batch_evaluation_summary()."""

    def test_debug_mode_returns_early(self):
        display_batch_evaluation_summary("task-1", [_make_stats()], debug_mode=True, action_type_timing={}, errors=[])

    def test_empty_stats_returns_early(self):
        display_batch_evaluation_summary("task-1", [], debug_mode=False, action_type_timing={}, errors=[])

    def test_filters_by_task_id(self):
        stats1 = _make_stats(task_id="task-a", web_agent_id="agent-1")
        stats2 = _make_stats(task_id="task-b", web_agent_id="agent-2")
        display_batch_evaluation_summary("task-a", [stats1, stats2], debug_mode=False, action_type_timing={}, errors=[])

    def test_with_action_type_timing(self):
        stats = _make_stats(task_id="t1")
        timing = {"click": [0.1, 0.2], "type": [0.05]}
        display_batch_evaluation_summary("t1", [stats], debug_mode=False, action_type_timing=timing, errors=[])

    def test_with_errors_list(self):
        stats = _make_stats(task_id="t1")
        display_batch_evaluation_summary("t1", [stats], debug_mode=False, action_type_timing={}, errors=["error one"])
