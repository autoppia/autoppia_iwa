import asyncio
import traceback
from typing import Any, Literal

from browser_use import Agent, AgentHistoryList, Browser
from loguru import logger
from pydantic import BaseModel

from autoppia_iwa.config.config import OPENAI_MODEL
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import BaseAction
from autoppia_iwa.src.web_agents.classes import BaseAgent, TaskSolution


class BrowserUseConfig(BaseModel):
    llm_provider: Literal["anthropic", "openai"] = "openai"
    llm_model: str = OPENAI_MODEL
    max_steps: int = 15
    use_vision: bool = False
    headless: bool = False


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

        self._agent: Agent | None = None
        self._context: Browser | None = None
        self._current_task: asyncio.Task | None = None
        self._cached_solution: TaskSolution | None = None

    async def act(
        self,
        *,
        task: Task,
        snapshot_html: str,
        url: str,
        step_index: int,
        history: list[dict[str, Any]] | None = None,
    ) -> list[BaseAction]:
        """
        Act method for stateful mode. For concurrent mode agents, this returns
        all actions on the first step (step_index == 0) and empty list afterwards.
        """
        if step_index == 0:
            # First call: generate solution and cache it
            solution = await self.solve_task(task)
            self._cached_solution = solution
            return solution.actions
        else:
            # Subsequent calls: return empty list (all actions already returned)
            return []

    async def solve_task(self, task: Task) -> TaskSolution:
        """Attempts to solve a task by executing browser actions."""
        try:
            self._current_task = asyncio.current_task()
            await self.execute_browser_use_agent(task)
            return TaskSolution(
                task_id=task.id,
                actions=[],
                web_agent_id=self.id,
            )
        except asyncio.CancelledError:
            logger.warning("Task was cancelled.")
            return TaskSolution(task_id=task.id, actions=[], web_agent_id=self.id)
        except Exception as e:
            logger.error(f"Failed to solve task {task.id}: {e}")
            logger.debug(traceback.format_exc())
            return TaskSolution(task_id=task.id, actions=[], web_agent_id=self.id)
        finally:
            self._current_task = None
            await self._cleanup_resources()

    async def execute_browser_use_agent(self, task: Task) -> AgentHistoryList | None:
        """Executes the browser agent and returns the history of actions taken."""
        vps = dict(width=task.specifications.screen_width, height=task.specifications.screen_height)
        self._context = Browser(
            headless=self.isheadless,
            viewport=vps,
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
