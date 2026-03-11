"""Unit tests for config.env (init_env)."""

import importlib
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestInitEnv:
    """Tests for init_env()."""

    def test_init_env_calls_load_dotenv_with_override_false(self):
        import autoppia_iwa.config.env as env_module

        with patch.object(env_module, "load_dotenv", MagicMock(return_value=None)) as m:
            env_module.init_env(override=False)
            m.assert_called_once()
            args, kwargs = m.call_args
            assert kwargs.get("override") is False
            path_arg = args[0]
            assert isinstance(path_arg, Path) and path_arg.name == ".env"

    def test_init_env_calls_load_dotenv_with_override_true(self):
        import autoppia_iwa.config.env as env_module

        with patch.object(env_module, "load_dotenv", MagicMock(return_value=None)) as m:
            env_module.init_env(override=True)
            m.assert_called_once()
            _, kwargs = m.call_args
            assert kwargs.get("override") is True

    def test_init_env_uses_fallback_when_dotenv_not_installed(self):
        """Covers env.py lines 5-8: fallback load_dotenv when dotenv import fails."""
        import autoppia_iwa.config.env as env_module

        real_import = __import__

        def fake_import(name, *args, **kwargs):
            if name == "dotenv":
                raise ImportError("No module named 'dotenv'")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", fake_import):
            importlib.reload(env_module)
        try:
            env_module.init_env(override=False)
            env_module.init_env(override=True)
        finally:
            importlib.reload(env_module)
