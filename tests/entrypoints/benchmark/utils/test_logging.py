"""Tests for canonical benchmark logging utilities."""

from unittest.mock import MagicMock, patch

from autoppia_iwa.src.evaluation.benchmark.utils import logging as logging_module


class TestEvaluationLevelFilter:
    """Test the evaluation_level filter function (line 12 coverage)."""

    def test_evaluation_level_filter_returns_true_for_evaluation_level(self):
        record = {"level": MagicMock(name="EVALUATION")}
        record["level"].name = "EVALUATION"
        assert logging_module.evaluation_level(record) is True

    def test_evaluation_level_filter_returns_false_for_other_levels(self):
        record = {"level": MagicMock(name="INFO")}
        record["level"].name = "INFO"
        assert logging_module.evaluation_level(record) is False


class TestSetupLogging:
    """Tests for setup_logging."""

    def test_setup_logging_delegates_to_shared_setup(self):
        with patch.object(logging_module, "setup_iwa_logging") as mock_setup:
            logging_module.setup_logging("/tmp/test_log.txt", console_level="DEBUG")
            mock_setup.assert_called_once_with("/tmp/test_log.txt", console_level="DEBUG")


class TestEvaluationLoggers:
    """Tests for get_evaluation_logger and log_* evaluation helpers."""

    def test_get_evaluation_logger_returns_bound_logger(self):
        bound = logging_module.get_evaluation_logger("ACTION_EXECUTION")
        assert bound is not None

    def test_log_action_execution(self):
        with patch.object(logging_module, "log_event") as mock_log:
            logging_module.log_action_execution("test message")
            mock_log.assert_called_once_with("EVALUATION", "test message", context="ACTION EXECUTION")

    def test_log_evaluation_event_general(self):
        with patch.object(logging_module, "log_event") as mock_log:
            logging_module.log_evaluation_event("general msg", context="GENERAL")
            mock_log.assert_called_once_with("EVALUATION", "general msg", context=None)

    def test_log_evaluation_event_with_context(self):
        with patch.object(logging_module, "log_event") as mock_log:
            logging_module.log_evaluation_event("custom msg", context="CUSTOM_CTX")
            mock_log.assert_called_once_with("EVALUATION", "custom msg", context="CUSTOM_CTX")

    def test_get_task_generation_logger(self):
        bound = logging_module.get_task_generation_logger("TEST_CTX")
        assert bound is not None

    def test_log_task_generation_event_default_context(self):
        with patch.object(logging_module, "log_event") as mock_log:
            logging_module.log_task_generation_event("task msg", context="TASK_GENERATION")
            mock_log.assert_called_once_with("TASK_GENERATION", "task msg", context=None)

    def test_log_task_generation_event_custom_context(self):
        with patch.object(logging_module, "log_event") as mock_log:
            logging_module.log_task_generation_event("task msg", context="CUSTOM")
            mock_log.assert_called_once_with("TASK_GENERATION", "task msg", context="CUSTOM")

    def test_log_gif_creation(self):
        with patch.object(logging_module, "log_event") as mock_log:
            logging_module.log_gif_creation("gif done")
            mock_log.assert_called_once_with("EVALUATION", "gif done", context="GIF CREATION")

    def test_log_backend_test(self):
        with patch.object(logging_module, "log_event") as mock_log:
            logging_module.log_backend_test("backend test msg")
            mock_log.assert_called_once_with("EVALUATION", "backend test msg", context="GET BACKEND TEST")


def test_entrypoint_logging_module_re_exports_canonical_objects():
    from autoppia_iwa.entrypoints.benchmark.utils import logging as entrypoint_logging

    assert entrypoint_logging.setup_logging is logging_module.setup_logging
    assert entrypoint_logging.log_action_execution is logging_module.log_action_execution
