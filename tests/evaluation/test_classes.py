"""Tests for evaluation.classes."""

from autoppia_iwa.src.evaluation.classes import (
    EvaluationResult,
    EvaluationStats,
    EvaluatorConfig,
    Feedback,
    TestResult as EvalTestResult,
)
from autoppia_iwa.src.execution.actions.actions import NavigateAction
from autoppia_iwa.src.execution.classes import ActionExecutionResult, BrowserSnapshot


def test_test_result():
    r = EvalTestResult(success=True, extra_data={"key": "value"})
    out = r.model_dump()
    assert out["success"] is True
    assert out["extra_data"] == {"key": "value"}


def test_feedback():
    feedback = Feedback(
        task_prompt="Do X",
        final_score=8.5,
        executed_actions=5,
        failed_actions=0,
        passed_tests=3,
        failed_tests=0,
        total_execution_time=10.0,
        time_penalty=0.0,
            critical_test_penalty=0,
            test_results=[EvalTestResult(success=True)],
            execution_history=[],
    )
    out = feedback.model_dump()
    assert out["task_prompt"] == "Do X"
    assert out["final_score"] == 8.5
    assert out["executed_actions"] == 5


def test_evaluation_stats_get_summary_dict():
    stats = EvaluationStats(
        web_agent_id="agent1",
        task_id="task1",
        action_count=4,
        start_time=0.0,
        action_execution_times=[1.0, 2.0],
        final_score=7.5,
        tests_passed=2,
        total_tests=2,
        total_time=5.0,
    )
    out = stats.get_summary_dict()
    assert out["agent_id"] == "agent1"
    assert out["task_id"] == "task1"
    assert out["actions"] == 4
    assert out["score"] == 7.5
    assert out["tests_passed"] == "2/2"
    assert out["success"] is True


def test_evaluation_stats_get_summary_dict_with_errors():
    stats = EvaluationStats(
        web_agent_id="a",
        task_id="t",
        action_count=0,
        start_time=0.0,
        had_errors=True,
        error_message="fail",
    )
    out = stats.get_summary_dict()
    assert out["success"] is False


def test_evaluation_result_model_dump():
    action = NavigateAction(url="http://x.com")
    snapshot = BrowserSnapshot(
        iteration=0,
        action=action,
        prev_html="",
        current_html="",
        screenshot_before="",
        screenshot_after="",
        backend_events=[],
        current_url="http://x.com",
    )
    exec_result = ActionExecutionResult(
        action=action,
        action_event="NavigateAction",
        successfully_executed=True,
        execution_time=1.0,
        browser_snapshot=snapshot,
    )
    result = EvaluationResult(
        final_score=8.0,
        test_results=[EvalTestResult(success=True)],
        execution_history=[exec_result],
        raw_score=8.0,
    )
    out = result.model_dump()
    assert out["final_score"] == 8.0
    assert len(out["execution_history"]) == 1
    assert "action_event" in out["execution_history"][0]


def test_evaluation_result_model_dump_feedback_pops():
    result = EvaluationResult(
        final_score=5.0,
        feedback=Feedback(
            task_prompt="P",
            final_score=5.0,
            executed_actions=2,
            failed_actions=0,
            passed_tests=1,
            failed_tests=0,
            total_execution_time=3.0,
            time_penalty=0.0,
            critical_test_penalty=0,
            test_results=[],
            execution_history=[],
        ),
    )
    out = result.model_dump()
    assert "feedback" in out
    if isinstance(out["feedback"], dict):
        assert "execution_history" not in out["feedback"]
        assert "test_results" not in out["feedback"]


def test_evaluator_config_defaults():
    config = EvaluatorConfig()
    assert config.task_delay_in_seconds == 0.1
    assert config.chunk_size == 20
    assert config.enable_grouping_tasks is True
    assert config.max_consecutive_action_failures == 2


def test_evaluator_config_custom():
    config = EvaluatorConfig(
        task_delay_in_seconds=0.5,
        chunk_size=10,
        should_record_gif=True,
    )
    assert config.task_delay_in_seconds == 0.5
    assert config.chunk_size == 10
    assert config.should_record_gif is True
