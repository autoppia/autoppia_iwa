from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

from autoppia_iwa.src.shared import logging as shared_logging


def test_setup_iwa_logging_replaces_known_handlers(monkeypatch, tmp_path):
    remove = Mock()
    add = Mock(side_effect=[101, 202])
    info = Mock()
    monkeypatch.setattr(shared_logging.logger, "remove", remove)
    monkeypatch.setattr(shared_logging.logger, "add", add)
    monkeypatch.setattr(shared_logging.logger, "info", info)
    shared_logging._console_handler_id = 11
    shared_logging._file_handler_id = 22
    shared_logging._logging_initialized = False

    shared_logging.setup_iwa_logging(str(tmp_path / "logs" / "iwa.log"), console_level="DEBUG")

    assert remove.call_count == 2
    assert add.call_count == 2
    assert (tmp_path / "logs").exists()
    info.assert_called_once()


def test_log_event_formats_context_and_agent(monkeypatch):
    log = Mock()
    monkeypatch.setattr(shared_logging.logger, "log", log)

    shared_logging.log_event("EVALUATION", "message", context="STEP", web_agent_id="agent-1", level="WARNING")

    log.assert_called_once_with("WARNING", "[EVALUATION] [STEP] [agent=agent-1] message")
