from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import urlparse, urlunparse

import aiohttp

from autoppia_iwa.config.config import DEMO_WEBS_ENDPOINT
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import BaseAction, NavigateAction
from autoppia_iwa.src.shared.utils import generate_random_web_agent_id
from autoppia_iwa.src.web_agents.act_protocol import ActRequest, ActResponse, ActToolCall
from autoppia_iwa.src.web_agents.classes import IWebAgent, TaskSolution


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
        self.last_content: str | None = None
        self.last_done: bool = False
        self.last_act_response: dict[str, Any] | None = None
        self._task_state: dict[str, Any] = {}
        self._task_state_task_id: str | None = None
        self.allowed_tools: list[dict[str, Any]] = self._build_allowed_tools()

    async def act(
        self,
        *,
        task: Task,
        snapshot_html: str,
        screenshot: str | bytes | None = None,
        url: str,
        step_index: int,
        history: list[dict[str, Any]] | None = None,
        state: dict[str, Any] | None = None,
    ) -> list[BaseAction]:
        """
        Call the remote /act endpoint and translate the response into BaseAction instances.
        """
        state_payload = self._resolve_state_for_step(task=task, step_index=step_index, state=state)
        request = ActRequest(
            task_id=getattr(task, "id", None),
            prompt=getattr(task, "prompt", None),
            url=self._force_localhost(url),
            snapshot_html=snapshot_html,
            screenshot=screenshot,
            step_index=int(step_index),
            web_project_id=getattr(task, "web_project_id", None),
            history=history,
            state_in=state_payload,
            allowed_tools=self.allowed_tools,
            include_reasoning=self.request_reasoning,
        )
        payload = request.model_dump(mode="json", exclude_none=True)

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.post(f"{self.base_url}/act", json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    parsed_response = ActResponse.from_raw(data if isinstance(data, dict) else {})
                    self._cache_parsed_response(parsed_response)
                    return self._parse_actions_response(parsed_response)
            except Exception:
                pass
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
        state: dict[str, Any] | None = None,
    ) -> list[BaseAction]:
        return asyncio.run(
            self.act(
                task=task,
                snapshot_html=snapshot_html,
                screenshot=screenshot,
                url=url,
                step_index=step_index,
                history=history,
                state=state,
            )
        )

    async def solve_task(self, task: Task) -> TaskSolution:
        raise NotImplementedError("ApifiedWebAgent is iterative and only supports act(); use act() for step-by-step execution.")

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _cache_parsed_response(self, parsed: ActResponse) -> None:
        self.last_act_response = parsed.model_dump(mode="json", exclude_none=True)
        self.last_reasoning = self._strip_optional_text(parsed.reasoning, allow_empty=True)
        self.last_content = self._strip_optional_text(parsed.content, allow_empty=False)
        self.last_done = bool(parsed.done)
        if isinstance(parsed.state_out, dict):
            self._task_state = dict(parsed.state_out)

    @staticmethod
    def _strip_optional_text(value: Any, *, allow_empty: bool) -> str | None:
        if not isinstance(value, str):
            return None
        stripped = value.strip()
        if stripped or allow_empty:
            return stripped
        return None

    def _parse_actions_response(self, parsed: ActResponse) -> list[BaseAction]:
        actions: list[BaseAction] = []
        for tool_call in parsed.tool_calls:
            action = self._build_action_from_tool_call(tool_call)
            if action is not None:
                actions.append(action)

        if self.max_actions_per_step is not None and actions:
            actions = actions[: self.max_actions_per_step]

        return actions

    def _build_action_from_tool_call(self, tool_call: ActToolCall) -> BaseAction | None:
        try:
            action_payload = self._tool_call_to_action_payload(tool_call)
            action = BaseAction.create_action(action_payload)
            if action is None:
                return None
            if isinstance(action, NavigateAction):
                # Ensure any navigate URLs are rewritten consistently.
                action.url = self._rewrite_to_remote(getattr(action, "url", None))
            return action
        except Exception:
            return None

    def _tool_call_to_action_payload(self, tool_call: ActToolCall) -> dict[str, Any]:
        name = str(tool_call.name or "").strip().lower()
        args = dict(tool_call.arguments or {})
        if name.startswith("browser."):
            action_type = name.split(".", 1)[1].strip()
            if not action_type:
                raise ValueError("Invalid browser tool call name.")
            args["type"] = str(args.get("type") or action_type)
            return args
        if name == "user.request_input":
            args["type"] = str(args.get("type") or "request_user_input")
            return args
        raise ValueError(f"Unsupported tool call name: {name}")

    def _resolve_state_for_step(
        self,
        *,
        task: Task,
        step_index: int,
        state: dict[str, Any] | None,
    ) -> dict[str, Any]:
        task_id = str(getattr(task, "id", "") or "")
        if int(step_index) <= 0 or task_id != self._task_state_task_id:
            self._task_state_task_id = task_id
            self._task_state = {}

        if state is not None:
            self._task_state = self._normalize_state_blob(state)

        return dict(self._task_state)

    @staticmethod
    def _normalize_state_blob(raw_state: Any) -> dict[str, Any]:
        if isinstance(raw_state, dict):
            return dict(raw_state)
        return {}

    @staticmethod
    def _build_allowed_tools() -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        defs_fn = getattr(BaseAction, "all_function_definitions", None)
        if not callable(defs_fn):
            return out
        try:
            defs = defs_fn()
        except Exception:
            return out
        for item in defs if isinstance(defs, list) else []:
            normalized = ApifiedWebAgent._normalize_allowed_tool(item)
            if normalized is not None:
                out.append(normalized)
        return out

    @staticmethod
    def _normalize_allowed_tool(item: Any) -> dict[str, Any] | None:
        if not isinstance(item, dict):
            return None
        fn = item.get("function") if isinstance(item.get("function"), dict) else {}
        tool_name = str(fn.get("name") or "").strip()
        if not tool_name:
            return None
        # Keep content/done outside tool_calls.
        if tool_name in {"done"}:
            return None
        namespaced = "user.request_input" if tool_name == "request_user_input" else f"browser.{tool_name}"
        return {
            "name": namespaced,
            "description": str(fn.get("description") or ""),
            "parameters": fn.get("parameters") if isinstance(fn.get("parameters"), dict) else {},
        }

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

__all__ = ["ApifiedIterativeWebAgent", "ApifiedWebAgent"]
