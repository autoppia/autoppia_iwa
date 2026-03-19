from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.web_agents.examples.browser_use import agent as browser_use_agent_module


def test_resolve_browser_executable_path_uses_explicit_existing_path(tmp_path):
    browser_path = tmp_path / "chrome"
    browser_path.write_text("")

    resolved = browser_use_agent_module.resolve_browser_executable_path(str(browser_path))

    assert resolved == str(browser_path)


def test_resolve_browser_executable_path_raises_for_missing_configured_path(monkeypatch):
    monkeypatch.setenv("CHROME_EXECUTABLE_PATH", "/tmp/does-not-exist")

    with pytest.raises(FileNotFoundError, match="Configured browser executable was not found"):
        browser_use_agent_module.resolve_browser_executable_path()


def test_resolve_browser_executable_path_prefers_system_chrome_for_persistent_profile(monkeypatch):
    seen: list[bool] = []

    def fake_iter_browser_candidates(*, prefer_system_chrome: bool) -> list[str]:
        seen.append(prefer_system_chrome)
        return ["/usr/bin/google-chrome"]

    monkeypatch.setattr(browser_use_agent_module, "_iter_browser_candidates", fake_iter_browser_candidates)

    resolved = browser_use_agent_module.resolve_browser_executable_path(
        user_data_dir="/home/usuario1/.config/google-chrome",
        profile_directory="Jake",
    )

    assert resolved == "/usr/bin/google-chrome"
    assert seen == [True]


@pytest.mark.asyncio
async def test_execute_browser_use_agent_passes_profile_launch_settings(monkeypatch, tmp_path):
    browser_path = tmp_path / "chrome"
    browser_path.write_text("")

    captured_browser_kwargs: dict = {}

    class DummyBrowser:
        def __init__(self, **kwargs):
            captured_browser_kwargs.update(kwargs)

        async def kill(self):
            return None

    agent_run = AsyncMock(return_value=SimpleNamespace())

    class DummyAgent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        async def run(self, max_steps):
            return await agent_run(max_steps=max_steps)

    monkeypatch.setattr(browser_use_agent_module, "Browser", DummyBrowser)
    monkeypatch.setattr(browser_use_agent_module, "Agent", DummyAgent)
    monkeypatch.setattr(
        browser_use_agent_module.BrowserUseWebAgent,
        "_build_llm",
        staticmethod(lambda provider, model: {"provider": provider, "model": model}),
    )

    config = browser_use_agent_module.BrowserUseConfig(
        executable_path=str(browser_path),
        user_data_dir="/tmp/browser-profile",
        profile_directory="Jake",
        headless=True,
    )
    agent = browser_use_agent_module.BrowserUseWebAgent(config=config)

    task = Task(url="https://example.com", prompt="Open page", web_project_id="dummy")

    await agent.execute_browser_use_agent(task)

    assert captured_browser_kwargs["executable_path"] == str(browser_path)
    assert captured_browser_kwargs["user_data_dir"] == "/tmp/browser-profile"
    assert captured_browser_kwargs["profile_directory"] == "Jake"
    assert captured_browser_kwargs["headless"] is True
