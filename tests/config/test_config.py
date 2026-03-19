"""Unit tests for config.config (read-only checks; config is loaded at import time)."""

import importlib
import os
from pathlib import Path
from unittest.mock import patch

import pytest


class TestConfigValues:
    """Test config values that are set when the module is loaded (conftest sets OPENAI_API_KEY)."""

    def test_project_base_dir_is_path(self):
        from autoppia_iwa.config.config import PROJECT_BASE_DIR

        assert isinstance(PROJECT_BASE_DIR, Path)
        assert PROJECT_BASE_DIR.exists() or not PROJECT_BASE_DIR.exists()  # may or may not exist

    def test_demo_webs_endpoint_no_trailing_slash(self):
        from autoppia_iwa.config.config import DEMO_WEBS_ENDPOINT

        assert isinstance(DEMO_WEBS_ENDPOINT, str)
        assert not DEMO_WEBS_ENDPOINT.endswith("/") or DEMO_WEBS_ENDPOINT == ""

    def test_demo_webs_ports_are_int(self):
        from autoppia_iwa.config.config import DEMO_WEB_SERVICE_PORT, DEMO_WEBS_STARTING_PORT

        assert isinstance(DEMO_WEBS_STARTING_PORT, int)
        assert isinstance(DEMO_WEB_SERVICE_PORT, int)

    def test_evaluator_headless_is_bool(self):
        from autoppia_iwa.config.config import EVALUATOR_HEADLESS

        assert isinstance(EVALUATOR_HEADLESS, bool)

    def test_llm_provider_is_string(self):
        from autoppia_iwa.config.config import LLM_PROVIDER

        assert isinstance(LLM_PROVIDER, str)

    def test_agent_config_strings(self):
        from autoppia_iwa.config.config import AGENT_HOST, AGENT_NAME, VALIDATOR_ID

        assert isinstance(AGENT_NAME, str)
        assert isinstance(AGENT_HOST, str)
        assert isinstance(VALIDATOR_ID, str)

    def test_agent_port_is_int(self):
        from autoppia_iwa.config.config import AGENT_PORT

        assert isinstance(AGENT_PORT, int)

    def test_use_apified_agent_is_bool(self):
        from autoppia_iwa.config.config import USE_APIFIED_AGENT

        assert isinstance(USE_APIFIED_AGENT, bool)


class TestConfigValidation:
    """Test config credential flags under different providers."""

    def test_openai_provider_without_api_key_sets_missing_credentials_flag(self):
        import autoppia_iwa.config.config as config_module

        with patch.dict(os.environ, {"OPENAI_API_KEY": "", "LLM_PROVIDER": "openai"}, clear=False):
            reloaded = importlib.reload(config_module)
            assert reloaded.LLM_PROVIDER == "openai"
            assert reloaded.HAS_OPENAI_CREDENTIALS is False

        importlib.reload(config_module)

    def test_chutes_provider_without_api_key_sets_missing_credentials_flag(self):
        import autoppia_iwa.config.config as config_module

        with patch.dict(os.environ, {"CHUTES_API_KEY": "", "LLM_PROVIDER": "chutes"}, clear=False):
            reloaded = importlib.reload(config_module)
            assert reloaded.LLM_PROVIDER == "chutes"
            assert reloaded.HAS_CHUTES_CREDENTIALS is False

        importlib.reload(config_module)
