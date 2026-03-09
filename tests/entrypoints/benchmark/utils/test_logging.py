"""Unit tests for benchmark.utils.logging."""

from unittest.mock import patch


class TestSetupLogging:
    """Tests for setup_logging."""

    def test_setup_logging_calls_logger_add(self):
        from autoppia_iwa.entrypoints.benchmark.utils import logging as logging_module

        with patch.object(logging_module.logger, "remove") as mock_remove, patch.object(logging_module.logger, "add") as mock_add, patch.object(logging_module.logger, "info"):
            logging_module.setup_logging("/tmp/test_log.txt", console_level="DEBUG")
            mock_remove.assert_called_once()
            assert mock_add.call_count >= 2  # console + file

    def test_setup_logging_file_has_rotation(self):
        from autoppia_iwa.entrypoints.benchmark.utils import logging as logging_module

        with patch.object(logging_module.logger, "remove"), patch.object(logging_module.logger, "add") as mock_add, patch.object(logging_module.logger, "info"):
            logging_module.setup_logging("/tmp/test_log2.txt")
            file_call = next(c for c in mock_add.call_args_list if c[0][0] == "/tmp/test_log2.txt")
            assert file_call[1].get("rotation") == "10 MB"
            assert file_call[1].get("retention") == "7 days"


class TestEvaluationLoggers:
    """Tests for get_evaluation_logger and log_* evaluation helpers."""

    def test_get_evaluation_logger_returns_bound_logger(self):
        from autoppia_iwa.entrypoints.benchmark.utils.logging import get_evaluation_logger

        bound = get_evaluation_logger("ACTION_EXECUTION")
        assert bound is not None

    def test_log_action_execution(self):
        from autoppia_iwa.entrypoints.benchmark.utils.logging import log_action_execution

        with patch("autoppia_iwa.entrypoints.benchmark.utils.logging.logger") as mock_logger:
            log_action_execution("test message")
            mock_logger.info.assert_called_once()
            assert "ACTION EXECUTION" in mock_logger.info.call_args[0][0]
            assert "test message" in mock_logger.info.call_args[0][0]

    def test_log_evaluation_event_general(self):
        from autoppia_iwa.entrypoints.benchmark.utils.logging import log_evaluation_event

        with patch("autoppia_iwa.entrypoints.benchmark.utils.logging.logger") as mock_logger:
            log_evaluation_event("general msg", context="GENERAL")
            mock_logger.info.assert_called_once()
            assert "[EVALUATION]" in mock_logger.info.call_args[0][0]
            assert "general msg" in mock_logger.info.call_args[0][0]

    def test_log_evaluation_event_with_context(self):
        from autoppia_iwa.entrypoints.benchmark.utils.logging import log_evaluation_event

        with patch("autoppia_iwa.entrypoints.benchmark.utils.logging.logger") as mock_logger:
            log_evaluation_event("custom msg", context="CUSTOM_CTX")
            mock_logger.info.assert_called_once()
            assert "[CUSTOM_CTX]" in mock_logger.info.call_args[0][0]

    def test_get_task_generation_logger(self):
        from autoppia_iwa.entrypoints.benchmark.utils.logging import get_task_generation_logger

        bound = get_task_generation_logger("TEST_CTX")
        assert bound is not None

    def test_log_task_generation_event_default_context(self):
        from autoppia_iwa.entrypoints.benchmark.utils.logging import log_task_generation_event

        with patch("autoppia_iwa.entrypoints.benchmark.utils.logging.logger") as mock_logger:
            log_task_generation_event("task msg", context="TASK_GENERATION")
            mock_logger.info.assert_called_once()
            assert "task msg" in mock_logger.info.call_args[0][0]

    def test_log_task_generation_event_custom_context(self):
        from autoppia_iwa.entrypoints.benchmark.utils.logging import log_task_generation_event

        with patch("autoppia_iwa.entrypoints.benchmark.utils.logging.logger") as mock_logger:
            log_task_generation_event("task msg", context="CUSTOM")
            mock_logger.info.assert_called_once()
            assert "[CUSTOM]" in mock_logger.info.call_args[0][0]

    def test_log_gif_creation(self):
        from autoppia_iwa.entrypoints.benchmark.utils.logging import log_gif_creation

        with patch("autoppia_iwa.entrypoints.benchmark.utils.logging.logger") as mock_logger:
            log_gif_creation("gif done")
            mock_logger.info.assert_called_once()
            assert "GIF CREATION" in mock_logger.info.call_args[0][0]

    def test_log_backend_test(self):
        from autoppia_iwa.entrypoints.benchmark.utils.logging import log_backend_test

        with patch("autoppia_iwa.entrypoints.benchmark.utils.logging.logger") as mock_logger:
            log_backend_test("backend test msg")
            mock_logger.info.assert_called_once()
            assert "GET BACKEND TEST" in mock_logger.info.call_args[0][0]
