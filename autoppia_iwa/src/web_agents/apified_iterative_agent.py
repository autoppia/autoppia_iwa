from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import urlparse, urlunparse

import aiohttp

from autoppia_iwa.config.config import DEMO_WEBS_ENDPOINT
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import BaseAction, DoneAction, NavigateAction
from autoppia_iwa.src.shared.utils import generate_random_web_agent_id
from autoppia_iwa.src.web_agents.act_protocol import ActExecutionMode, ActRequest, ActResponse
from autoppia_iwa.src.web_agents.classes import IWebAgent


class ApifiedWebAgent(IWebAgent):
    """
    Iterative agent that calls a remote /act (or /step) endpoint to get next actions.

    The remote API is expected to accept a JSON payload describing the current
    browser state and return one or more actions to execute.
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        id: str | None = None,
        name: str | None = None,
        timeout: float = 180,
        base_url: str | None = None,
        request_reasoning: bool = False,
        max_actions_per_step: int | None = None,
    ):
        self.id = id or generate_random_web_agent_id()
        self.name = name or f"Agent {self.id}"

        if base_url:
            self.base_url = base_url.rstrip("/")
        else:
            if host is None:
                raise ValueError("host must be provided when base_url is not set")
            if port is not None:
                self.base_url = f"http://{host}:{port}"
            else:
                self.base_url = f"http://{host}"

        self.timeout = float(timeout)
        self.request_reasoning = bool(request_reasoning)
        if max_actions_per_step is not None and int(max_actions_per_step) <= 0:
            raise ValueError("max_actions_per_step must be greater than 0 when provided.")
        self.max_actions_per_step = int(max_actions_per_step) if max_actions_per_step is not None else None
        self.last_reasoning: str | None = None
        self.last_act_response: dict[str, Any] | None = None

    async def act(
        self,
        *,
        task: Task,
        snapshot_html: str,
        screenshot: str | bytes | None = None,
        url: str,
        step_index: int,
        history: list[dict[str, Any]] | None = None,
    ) -> list[BaseAction]:
        """
        Call the remote /act endpoint and translate the response into BaseAction instances.
        """
        request = ActRequest(
            task_id=getattr(task, "id", None),
            prompt=getattr(task, "prompt", None),
            url=self._force_localhost(url),
            snapshot_html=snapshot_html,
            screenshot=screenshot,
            step_index=int(step_index),
            web_project_id=getattr(task, "web_project_id", None),
            history=history,
            include_reasoning=self.request_reasoning,
        )
        payload = request.model_dump(mode="json", exclude_none=True)

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Prefer /act, fall back to /step if needed.
            for path in ("/act", "/step"):
                try:
                    async with session.post(f"{self.base_url}{path}", json=payload) as response:
                        response.raise_for_status()
                        data = await response.json()
                        parsed_response = ActResponse.from_raw(data if isinstance(data, dict) else {})
                        self.last_act_response = parsed_response.model_dump(mode="json", exclude_none=True)
                        self.last_reasoning = parsed_response.reasoning.strip() if isinstance(parsed_response.reasoning, str) else None
                        return self._parse_actions_response(data)
                except Exception:
                    continue
        # If all calls fail, return a NOOP (no actions) so the caller can decide.
        return []

    def act_sync(
        self,
        *,
        task: Task,
        snapshot_html: str,
        screenshot: str | bytes | None = None,
        url: str,
        step_index: int,
        history: list[dict[str, Any]] | None = None,
    ) -> list[BaseAction]:
        return asyncio.run(
            self.act(
                task=task,
                snapshot_html=snapshot_html,
                screenshot=screenshot,
                url=url,
                step_index=step_index,
                history=history,
            )
        )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _parse_actions_response(self, data: dict[str, Any]) -> list[BaseAction]:
        try:
            parsed = ActResponse.from_raw(data if isinstance(data, dict) else {})
        except Exception:
            return []
        actions_payload = parsed.actions

        actions: list[BaseAction] = []
        for raw in actions_payload:
            try:
                action = BaseAction.create_action(raw)
                if action is None:
                    continue
                if isinstance(action, NavigateAction):
                    # Ensure any navigate URLs are rewritten consistently.
                    action.url = self._rewrite_to_remote(getattr(action, "url", None))
                actions.append(action)
            except Exception:
                continue

        if parsed.done and not actions:
            actions.append(DoneAction(reason=parsed.reasoning))

        if parsed.execution_mode == ActExecutionMode.SINGLE_STEP and actions:
            actions = actions[:1]

        if self.max_actions_per_step is not None and actions:
            actions = actions[: self.max_actions_per_step]

        return actions

    @staticmethod
    def _force_localhost(original_url: str | None) -> str | None:
        """Rewrite any URL so the host becomes localhost while preserving port/path."""
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
        """Rewrite URLs to point at the configured remote demo webs endpoint."""
        if not original_url:
            return original_url

        remote = DEMO_WEBS_ENDPOINT if DEMO_WEBS_ENDPOINT.startswith("http") else f"http://{DEMO_WEBS_ENDPOINT}"
        remote_parsed = urlparse(remote)

        # Relative paths from the agent should be anchored to the remote host
        if original_url.startswith("/"):
            return f"{remote_parsed.scheme}://{remote_parsed.netloc}{original_url}"

        parsed = urlparse(original_url)
        if not parsed.scheme and not parsed.netloc:
            cleaned_path = original_url if original_url.startswith("/") else f"/{original_url}"
            return f"{remote_parsed.scheme}://{remote_parsed.netloc}{cleaned_path}"

        new_url = parsed._replace(scheme=remote_parsed.scheme or parsed.scheme, netloc=remote_parsed.netloc)
        return urlunparse(new_url)


ApifiedIterativeWebAgent = ApifiedWebAgent

__all__ = ["ApifiedWebAgent", "ApifiedIterativeWebAgent"]
