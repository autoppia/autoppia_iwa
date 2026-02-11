import asyncio
import ipaddress
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, urlunparse

import aiohttp

from autoppia_iwa.config.config import DEMO_WEBS_ENDPOINT
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import BaseAction, NavigateAction
from autoppia_iwa.src.shared.utils import generate_random_web_agent_id
from autoppia_iwa.src.web_agents.classes import IWebAgent, TaskSolution


class ApifiedWebAgent(IWebAgent):
    """
    Calls a remote /solve_task endpoint and rebuilds a TaskSolution.
    """

    def __init__(self, host: str | None = None, port: int | None = None, id: str | None = None, name: str | None = None, timeout=180, base_url: str | None = None):
        self.id = id or generate_random_web_agent_id()
        self.name = name or f"Agent {self.id}"
        if base_url:
            # Respect provided base_url as-is
            self.base_url = base_url.rstrip("/")
        else:
            if host is None:
                raise ValueError("host must be provided when base_url is not set")
            # If port is provided, include it; otherwise omit
            if port is not None:
                self.base_url = f"http://{host}:{port}"
            else:
                self.base_url = f"http://{host}"
        self.timeout = timeout
        super().__init__()
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


    def _create_action(self, raw: dict) -> Optional[BaseAction]:
        """Build one BaseAction from dict; rewrite NavigateAction URL."""
        try:
            action = BaseAction.create_action(raw)
            if action is None:
                return None
            if isinstance(action, NavigateAction):
                action.url = self._rewrite_to_remote(getattr(action, "url", None))
            return action
        except Exception:
            return None

    async def solve_task(self, task: Task) -> TaskSolution:
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                payload = task.clean_task()
                payload["url"] = self._force_localhost(payload.get("url"))

                async with session.post(f"{self.base_url}/solve_task", json=payload) as response:
                    response.raise_for_status()
                    response_json = await response.json()
            except Exception as e:
                raise RuntimeError(f"Error during HTTP request to {self.base_url}/solve_task: {e}") from e

            actions_data = response_json.get("actions", [])
            for action in actions_data:
                if isinstance(action, dict) and action.get("type") in {"NavigateAction", "navigate"}:
                    action_url = action.get("url")
                    action["url"] = self._rewrite_to_remote(action_url)

            web_agent_id = response_json.get("web_agent_id", "unknown")
            recording_str = response_json.get("recording", "")
            rebuilt_actions: List[BaseAction] = []
            for a in actions_data:
                if isinstance(a, dict):
                    built = self._create_action(a)
                    if built is not None:
                        rebuilt_actions.append(built)
        return TaskSolution(task_id=task.id, actions=rebuilt_actions, web_agent_id=web_agent_id, recording=recording_str)

    def solve_task_sync(self, task: Task) -> TaskSolution:
        return asyncio.run(self.solve_task(task))

    @staticmethod
    def _force_localhost(original_url: str | None) -> str | None:
        """Rewrite any task URL so the host becomes localhost while preserving port/path."""
        if not original_url:
            return original_url

        parsed = urlparse(original_url)
        netloc = "localhost"
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"

        rewritten = parsed._replace(netloc=netloc)
        return urlunparse(rewritten)

    @staticmethod
    def _rewrite_to_remote(original_url: str | None) -> str | None:
        """Rewrite agent-produced URLs to point at the configured remote demo webs endpoint."""

        if not original_url:
            return original_url

        remote = DEMO_WEBS_ENDPOINT if DEMO_WEBS_ENDPOINT.startswith("http") else f"http://{DEMO_WEBS_ENDPOINT}"
        remote_parsed = urlparse(remote)

        # Relative paths from the agent should be anchored to the remote host
        if original_url.startswith("/"):
            return f"{remote_parsed.scheme}://{remote_parsed.netloc}{original_url}"

        parsed = urlparse(original_url)

        # If agent sent something like "localhost:8001" without scheme, treat it as path
        if not parsed.scheme and not parsed.netloc:
            cleaned_path = original_url if original_url.startswith("/") else f"/{original_url}"
            return f"{remote_parsed.scheme}://{remote_parsed.netloc}{cleaned_path}"

        # Keep the remote host; preserve original port when the agent points to localhost/loopback,
        # otherwise only carry over the port if the remote host is an IP and has no explicit port.
        netloc = remote_parsed.netloc
        host = remote_parsed.hostname or remote_parsed.netloc
        parsed_host = parsed.hostname or ""
        try:
            remote_is_ip = bool(host and ipaddress.ip_address(host))
        except ValueError:
            remote_is_ip = False
        parsed_is_loopback = parsed_host in {"localhost", "127.0.0.1"}

        if parsed.port and (parsed_is_loopback or (not remote_parsed.port and remote_is_ip)):
            netloc = f"{host}:{parsed.port}"

        new_url = parsed._replace(scheme=remote_parsed.scheme or parsed.scheme, netloc=netloc)
        return urlunparse(new_url)
