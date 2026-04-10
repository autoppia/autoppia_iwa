from __future__ import annotations

import base64
import re
from typing import Any
from urllib.parse import urlparse, urlunparse

import aiohttp
from loguru import logger

from autoppia_iwa.config.config import DEMO_WEBS_ENDPOINT
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import BaseAction, NavigateAction
from autoppia_iwa.src.shared.utils import generate_random_web_agent_id
from autoppia_iwa.src.web_agents.classes import IWebAgent
from autoppia_iwa.src.web_agents.protocol import StepRequest, StepResponse, StepToolCall


class ApifiedWebAgent(IWebAgent):
    """
    Iterative agent that calls a remote /step endpoint to get next actions.

    The remote API accepts a JSON payload describing the current browser state
    and returns one or more actions to execute.
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
        send_allowed_tools: bool = False,
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
        self.send_allowed_tools = bool(send_allowed_tools)
        if max_actions_per_step is not None and int(max_actions_per_step) <= 0:
            raise ValueError("max_actions_per_step must be greater than 0 when provided.")
        self.max_actions_per_step = int(max_actions_per_step) if max_actions_per_step is not None else None
        self.last_reasoning: str | None = None
        self.last_content: str | None = None
        self.last_done: bool = False
        self.last_act_response: dict[str, Any] | None = None
        self.tools: list[dict[str, Any]] = self._build_tools() if self.send_allowed_tools else []
        self.allowed_tools = self.tools
        self._step_rewrite_page_url: str | None = None

    @staticmethod
    def _screenshot_for_json(screenshot: str | bytes | None) -> str | None:
        """PNG bytes cannot be JSON-encoded for /step; use a data URL string."""
        if screenshot is None:
            return None
        if isinstance(screenshot, bytes):
            if not screenshot:
                return None
            b64 = base64.b64encode(screenshot).decode("ascii")
            return f"data:image/png;base64,{b64}"
        s = str(screenshot).strip()
        return s or None

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
        """Call the remote /step endpoint and translate the response into BaseAction instances."""
        if snapshot_html is not None:
            html = snapshot_html
        self._step_rewrite_page_url = url
        request = StepRequest(
            task_id=getattr(task, "id", None),
            prompt=getattr(task, "prompt", None),
            url=self._force_localhost(url),
            html=html,
            screenshot=self._screenshot_for_json(screenshot),
            step_index=int(step_index),
            history=history,
            tools=self.tools,
            include_reasoning=self.request_reasoning,
        )
        payload = request.model_dump(mode="json", exclude_none=True)

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.post(f"{self.base_url}/step", json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return self._parse_actions_response(data if isinstance(data, dict) else {})
            except Exception as exc:
                logger.warning(f"ApifiedWebAgent.step failed: {exc}")
        return []

    async def act(self, **kwargs) -> list[BaseAction]:
        """Backward-compatible alias for local callers; HTTP contract is /step."""
        return await self.step(**kwargs)

    async def solve_task(self, task: Task):
        raise NotImplementedError("ApifiedWebAgent only supports step(), not solve_task().")

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _cache_parsed_response(self, parsed: StepResponse) -> None:
        self.last_act_response = parsed.model_dump(mode="json", exclude_none=True)
        self.last_reasoning = self._strip_optional_text(parsed.reasoning, allow_empty=True)
        self.last_content = self._strip_optional_text(parsed.content, allow_empty=False)
        self.last_done = bool(parsed.done)

    @staticmethod
    def _strip_optional_text(value: Any, *, allow_empty: bool) -> str | None:
        if not isinstance(value, str):
            return None
        stripped = value.strip()
        if stripped or allow_empty:
            return stripped
        return None

    def _parse_actions_response(self, payload: StepResponse | dict[str, Any]) -> list[BaseAction]:
        if isinstance(payload, dict):
            parsed = self._parse_canonical_response(payload)
            if parsed is None:
                return self._parse_legacy_actions_response(payload)
            self._cache_parsed_response(parsed)
        else:
            parsed = payload

        actions: list[BaseAction] = []
        for tool_call in parsed.tool_calls:
            action = self._build_action_from_tool_call(tool_call)
            if action is not None:
                actions.append(action)

        if self.max_actions_per_step is not None and actions:
            actions = actions[: self.max_actions_per_step]

        return actions

    def _parse_canonical_response(self, payload: dict[str, Any]) -> StepResponse | None:
        if not self._looks_like_canonical_response(payload):
            return None
        return StepResponse.from_raw(payload)

    @staticmethod
    def _looks_like_canonical_response(payload: dict[str, Any]) -> bool:
        if "tool_calls" in payload:
            return True
        actions = payload.get("actions")
        if not isinstance(actions, list):
            return False
        if not actions:
            return any(key in payload for key in ("done", "protocol_version", "content", "reasoning", "error"))
        return all(
            isinstance(item, dict) and isinstance(item.get("name"), str) and ("arguments" not in item or item.get("arguments") is None or isinstance(item.get("arguments"), dict)) for item in actions
        )

    def _parse_legacy_actions_response(self, data: dict[str, Any]) -> list[BaseAction]:
        actions_payload: list[dict[str, Any]] = []

        if isinstance(data.get("actions"), list):
            actions_payload = [item for item in data["actions"] if isinstance(item, dict)]
        elif isinstance(data.get("action"), dict):
            actions_payload = [data["action"]]
        elif isinstance(data.get("navigate_url"), str):
            actions_payload = [
                {
                    "type": "NavigateAction",
                    "url": self._rewrite_to_remote(data["navigate_url"]),
                }
            ]

        if not actions_payload:
            return []

        actions: list[BaseAction] = []
        for raw in actions_payload:
            try:
                if isinstance(raw, dict) and raw.get("type") in {"NavigateAction", "navigate"}:
                    raw = dict(raw)
                    raw["url"] = self._rewrite_to_remote(raw.get("url"))
                action = BaseAction.create_action(raw)
                if action is None:
                    continue
                if isinstance(action, NavigateAction):
                    action.url = self._rewrite_to_remote(getattr(action, "url", None))
                actions.append(action)
            except Exception:
                continue
        return actions

    def _build_action_from_tool_call(self, tool_call: StepToolCall) -> BaseAction | None:
        try:
            action_payload = self._tool_call_to_action_payload(tool_call)
            action = BaseAction.create_action(action_payload)
            if action is None:
                return None
            if isinstance(action, NavigateAction):
                action.url = self._rewrite_to_remote(getattr(action, "url", None))
            return action
        except Exception:
            return None

    def _tool_call_to_action_payload(self, tool_call: StepToolCall) -> dict[str, Any]:
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

    @staticmethod
    def _build_tools() -> list[dict[str, Any]]:
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
        if tool_name in {"done", "evaluate"}:
            return None
        namespaced = "user.request_input" if tool_name == "request_user_input" else f"browser.{tool_name}"
        return {
            "name": namespaced,
            "description": str(fn.get("description") or ""),
            "parameters": fn.get("parameters") if isinstance(fn.get("parameters"), dict) else {},
        }

    @staticmethod
    def _force_localhost(original_url: str | None) -> str | None:
        if not original_url:
            return original_url
        parsed = urlparse(original_url)
        netloc = "localhost"
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"
        rewritten = parsed._replace(netloc=netloc)
        return urlunparse(rewritten)

    _BARE_LOOPBACK = re.compile(r"^(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$", re.I)

    def _rewrite_to_remote(self, original_url: str | None) -> str | None:
        if not original_url:
            return original_url
        s = str(original_url).strip()
        if s and "://" not in s and not s.startswith("/") and "/" not in s and self._BARE_LOOPBACK.match(s):
            s = f"http://{s}/"
        remote = DEMO_WEBS_ENDPOINT if DEMO_WEBS_ENDPOINT.startswith("http") else f"http://{DEMO_WEBS_ENDPOINT}"
        remote_parsed = urlparse(remote)
        if s.startswith("/"):
            out = f"{remote_parsed.scheme}://{remote_parsed.netloc}{s}"
        else:
            parsed = urlparse(s)
            if not parsed.scheme and not parsed.netloc:
                cleaned_path = s if s.startswith("/") else f"/{s}"
                out = f"{remote_parsed.scheme}://{remote_parsed.netloc}{cleaned_path}"
            else:
                new_url = parsed._replace(scheme=remote_parsed.scheme or parsed.scheme, netloc=remote_parsed.netloc)
                out = urlunparse(new_url)
        return self._merge_loopback_origin_with_page(out)

    def _merge_loopback_origin_with_page(self, rewritten: str | None) -> str | None:
        """
        If the operator returns http://localhost/... without a port but the browser is on
        localhost:8013, keep the page origin so NavigateAction targets the demo frontend.
        """
        if not rewritten or not self._step_rewrite_page_url:
            return rewritten
        page = urlparse(self._step_rewrite_page_url)
        cur = urlparse(rewritten)
        if cur.port is not None:
            return rewritten
        if not self._is_loopback_hostname(cur.hostname):
            return rewritten
        if not self._is_loopback_hostname(page.hostname) or page.port is None:
            return rewritten
        merged = cur._replace(netloc=page.netloc)
        return urlunparse(merged)

    @staticmethod
    def _is_loopback_hostname(hostname: str | None) -> bool:
        if not hostname:
            return False
        h = str(hostname).lower()
        return h in ("localhost", "127.0.0.1", "::1") or h == "[::1]"


ApifiedIterativeWebAgent = ApifiedWebAgent

__all__ = ["ApifiedIterativeWebAgent", "ApifiedWebAgent"]
