"""Unit tests for llms.ui_parser_service."""

from unittest.mock import MagicMock

from autoppia_iwa.src.llms.ui_parser_service import UIParserService


def test_ui_parser_service_init():
    svc = UIParserService()
    assert svc is not None


def test_summarize_image_returns_empty_string():
    svc = UIParserService()
    result = svc.summarize_image(MagicMock())
    assert result == ""
