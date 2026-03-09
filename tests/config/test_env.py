"""Unit tests for config.env (init_env)."""

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
