import ipaddress
from typing import Any
from urllib.parse import urlparse, urlunparse

import aiohttp

from autoppia_iwa.config.config import DEMO_WEBS_ENDPOINT
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import BaseAction, NavigateAction
from autoppia_iwa.src.shared.utils import generate_random_web_agent_id
from autoppia_iwa.src.web_agents.classes import IWebAgent, TaskSolution


def _parse_remote_demo_endpoint():
    remote = DEMO_WEBS_ENDPOINT if DEMO_WEBS_ENDPOINT.startswith("http") else f"https://{DEMO_WEBS_ENDPOINT}"
    return urlparse(remote)


class ApifiedOneShotWebAgent(IWebAgent):
    """One-shot agent that calls /solve_task. Returns all actions on first step."""

    def __init__(self, host: str | None = None, port: int | None = None, id: str | None = None, name: str | None = None, timeout=180, base_url: str | None = None):
        self.id = id or generate_random_web_agent_id()
        self.name = name or f"Agent {self.id}"
        if base_url:
            self.base_url = base_url.rstrip("/")
        elif host is None:
            raise ValueError("host must be provided when base_url is not set")
        elif port is not None:
            self.base_url = f"http://{host}:{port}"
        else:
            self.base_url = f"http://{host}"
        self.timeout = timeout
        self._cached_solution: TaskSolution | None = None

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
        if step_index == 0:
            solution = await self._solve_task(task)
            self._cached_solution = solution
            return solution.actions
        return []

    async def act(self, **kwargs) -> list[BaseAction]:
        return await self.step(**kwargs)

    async def solve_task(self, task: Task) -> TaskSolution:
        return await self._solve_task(task)

    async def _solve_task(self, task: Task) -> TaskSolution:
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                payload = task.clean_task()
                payload["url"] = self._force_localhost(payload.get("url"))
                async with session.post(f"{self.base_url}/solve_task_at_once", json=payload) as response:
                    response.raise_for_status()
                    response_json = await response.json()
                actions_data = response_json.get("actions", [])
                web_agent_id = response_json.get("web_agent_id", "unknown")
                rebuilt = [a for raw in actions_data if isinstance(raw, dict) for a in [self._create_action(raw)] if a]
        except Exception as exc:
            raise RuntimeError(f"Failed to solve task via one-shot agent: {exc}") from exc
        return TaskSolution(task_id=task.id, actions=rebuilt, web_agent_id=web_agent_id)

    def _create_action(self, raw: dict) -> BaseAction | None:
        try:
            action = BaseAction.create_action(raw)
            if action and isinstance(action, NavigateAction):
                action.url = self._rewrite_to_remote(getattr(action, "url", None))
            return action
        except Exception:
            return None

    @staticmethod
    def _force_localhost(url: str | None) -> str | None:
        if not url:
            return url
        parsed = urlparse(url)
        netloc = f"localhost:{parsed.port}" if parsed.port else "localhost"
        return urlunparse(parsed._replace(netloc=netloc))

    @staticmethod
    def _rewrite_to_remote(url: str | None) -> str | None:
        if not url:
            return url
        remote = _parse_remote_demo_endpoint()
        if url.startswith("/"):
            return f"{remote.scheme}://{remote.netloc}{url}"
        parsed = urlparse(url)
        if not parsed.scheme and not parsed.netloc:
            return f"{remote.scheme}://{remote.netloc}/{url.lstrip('/')}"
        netloc = remote.netloc
        host = remote.hostname or remote.netloc
        parsed_host = parsed.hostname or ""
        try:
            remote_is_ip = bool(host and ipaddress.ip_address(host))
        except ValueError:
            remote_is_ip = False
        if parsed.port and (parsed_host in {"localhost", "127.0.0.1"} or (not remote.port and remote_is_ip)):
            netloc = f"{host}:{parsed.port}"
        return urlunparse(parsed._replace(scheme=remote.scheme or parsed.scheme, netloc=netloc))
