import asyncio
import glob
import os
import platform
import shutil
import traceback
from pathlib import Path
from typing import Any, Literal

from browser_use import Agent, AgentHistoryList, Browser
from loguru import logger
from pydantic import BaseModel, Field

from autoppia_iwa.config.config import OPENAI_MODEL
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import BaseAction
from autoppia_iwa.src.web_agents.classes import BaseAgent


def _env_first(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    return None


def _expand_existing_file(path_str: str | None) -> str | None:
    if not path_str:
        return None
    expanded = Path(path_str).expanduser()
    if expanded.is_file():
        return str(expanded)
    return None


def _iter_browser_candidates(*, prefer_system_chrome: bool) -> list[str]:
    playwright_root = Path(os.getenv("PLAYWRIGHT_BROWSERS_PATH", "~/.cache/ms-playwright")).expanduser()
    system = platform.system()

    if system == "Darwin":
        system_candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        ]
        playwright_patterns = [
            playwright_root / "chromium-*" / "chrome-mac" / "Chromium.app" / "Contents" / "MacOS" / "Chromium",
            playwright_root / "chromium_headless_shell-*" / "chrome-mac" / "Chromium.app" / "Contents" / "MacOS" / "Chromium",
        ]
    elif system == "Windows":
        system_candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files\Chromium\Application\chrome.exe",
            r"C:\Program Files (x86)\Chromium\Application\chrome.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
        playwright_patterns = [
            playwright_root / "chromium-*" / "chrome-win" / "chrome.exe",
            playwright_root / "chromium_headless_shell-*" / "chrome-win" / "chrome.exe",
        ]
    else:
        system_candidates = [
            "/usr/bin/google-chrome-stable",
            "/usr/bin/google-chrome",
            "/usr/local/bin/google-chrome",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/usr/local/bin/chromium",
            "/snap/bin/chromium",
            "/usr/bin/brave-browser",
        ]
        playwright_patterns = [
            playwright_root / "chromium-*" / "chrome-linux*" / "chrome",
            playwright_root / "chromium_headless_shell-*" / "chrome-linux*" / "chrome",
        ]

    candidates: list[str] = []

    chrome_binaries = [path for path in system_candidates if "chrome" in Path(path).name.lower()]
    non_chrome_binaries = [path for path in system_candidates if path not in chrome_binaries]
    ordered_system_candidates = chrome_binaries + non_chrome_binaries if prefer_system_chrome else system_candidates

    for candidate in ordered_system_candidates:
        resolved = shutil.which(candidate) if os.path.sep not in candidate else candidate
        existing = _expand_existing_file(resolved)
        if existing:
            candidates.append(existing)

    for pattern in playwright_patterns:
        matches = sorted(glob.glob(str(pattern)))
        for match in matches:
            existing = _expand_existing_file(match)
            if existing:
                candidates.append(existing)

    # Preserve order while deduplicating.
    return list(dict.fromkeys(candidates))


def resolve_browser_executable_path(
    explicit_path: str | None = None,
    *,
    user_data_dir: str | None = None,
    profile_directory: str | None = None,
) -> str | None:
    configured_path = explicit_path or _env_first("CHROME_EXECUTABLE_PATH", "BROWSER_USE_EXECUTABLE_PATH")
    if configured_path:
        resolved = _expand_existing_file(configured_path)
        if resolved is None:
            raise FileNotFoundError(f"Configured browser executable was not found: {configured_path}")
        return resolved

    prefer_system_chrome = bool(user_data_dir or profile_directory)
    candidates = _iter_browser_candidates(prefer_system_chrome=prefer_system_chrome)
    return candidates[0] if candidates else None


class BrowserUseConfig(BaseModel):
    llm_provider: Literal["anthropic", "openai"] = "openai"
    llm_model: str = OPENAI_MODEL
    max_steps: int = 15
    use_vision: bool = False
    headless: bool = False
    executable_path: str | None = Field(default_factory=lambda: _env_first("CHROME_EXECUTABLE_PATH", "BROWSER_USE_EXECUTABLE_PATH"))
    chrome_executable_path: str | None = None
    user_data_dir: str | None = Field(default_factory=lambda: _env_first("BROWSER_USE_USER_DATA_DIR", "CHROME_USER_DATA_DIR"))
    profile_directory: str | None = Field(default_factory=lambda: _env_first("BROWSER_USE_PROFILE_DIRECTORY", "CHROME_PROFILE_DIRECTORY"))


class BrowserUseWebAgent(BaseAgent):
    """Web agent that integrates with browser-use for solving web-based tasks."""

    def __init__(self, config: BrowserUseConfig | None = None):
        super().__init__()
        config = config or BrowserUseConfig()

        self.llm_provider = config.llm_provider
        self.llm_model = config.llm_model
        self._max_steps = config.max_steps
        self._use_vision = config.use_vision
        self.isheadless = config.headless
        self._user_data_dir = config.user_data_dir
        self._profile_directory = config.profile_directory
        self._browser_executable_path = resolve_browser_executable_path(
            config.executable_path or config.chrome_executable_path,
            user_data_dir=self._user_data_dir,
            profile_directory=self._profile_directory,
        )

        self._agent: Agent | None = None
        self._context: Browser | None = None
        self._current_task: asyncio.Task | None = None

    async def step(
        self,
        *,
        task: Task,
        html: str = "",
        screenshot: str | bytes | None = None,
        url: str,
        step_index: int,
        history: list[dict[str, Any]] | None = None,
        snapshot_html: str | None = None,
    ) -> list[BaseAction]:
        """Runs browser-use agent on first step, returns empty on subsequent steps."""
        if step_index == 0:
            try:
                self._current_task = asyncio.current_task()
                await self.execute_browser_use_agent(task)
            except asyncio.CancelledError:
                logger.warning("Task was cancelled.")
                raise
            except Exception as e:
                logger.error(f"Failed to solve task {task.id}: {e}")
                logger.debug(traceback.format_exc())
            finally:
                self._current_task = None
                await self._cleanup_resources()
        return []

    async def execute_browser_use_agent(self, task: Task) -> AgentHistoryList | None:
        """Executes the browser agent and returns the history of actions taken."""
        vps = {"width": task.specifications.screen_width, "height": task.specifications.screen_height}
        self._context = Browser(
            headless=self.isheadless,
            viewport=vps,
            executable_path=self._browser_executable_path,
            user_data_dir=self._user_data_dir,
            profile_directory=self._profile_directory,
            chromium_sandbox=False,
        )

        llm = self._build_llm(self.llm_provider, self.llm_model)

        self._agent = Agent(
            initial_actions=[{"go_to_url": {"url": task.url}}],
            use_vision=self._use_vision,
            browser=self._context,
            task=task.prompt,
            llm=llm,
        )

        try:
            result: AgentHistoryList = await self._agent.run(max_steps=self._max_steps)
            return result
        except Exception as e:
            logger.error(f"Error executing browser agent: {e}")
            raise

    async def stop(self):
        """Stops the agent if it is running."""
        if self._agent:
            self._agent.stop()
            self._agent = None

        if self._current_task:
            self._current_task.cancel()

        await self._cleanup_resources()

    async def _cleanup_resources(self):
        """Cleans up browser and context resources."""
        try:
            if self._context:
                await self._context.kill()
                self._context = None
        except Exception as e:
            logger.error(f"Error during resource cleanup: {e}")

    @staticmethod
    def _build_llm(provider: Literal["anthropic", "openai"], model: str):
        """Factory for the LLM instance based on provider."""
        if provider == "anthropic":
            from browser_use import ChatAnthropic

            return ChatAnthropic(model=model)
        else:
            from browser_use import ChatOpenAI

            return ChatOpenAI(model=model)
