import ipaddress
from typing import Any
from urllib.parse import urlparse, urlunparse

import aiohttp

from autoppia_iwa.config.config import DEMO_WEBS_ENDPOINT
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import BaseAction, NavigateAction
from autoppia_iwa.src.shared.utils import generate_random_web_agent_id
from autoppia_iwa.src.web_agents.classes import IHarvester, IWebAgent, TaskSolution


def _short_response_body(text: str, *, limit: int = 1000) -> str:
    compact = " ".join(str(text or "").split())
    if len(compact) <= limit:
        return compact
    return f"{compact[:limit]}..."


def _parse_remote_demo_endpoint():
    remote = DEMO_WEBS_ENDPOINT if DEMO_WEBS_ENDPOINT.startswith("http") else f"https://{DEMO_WEBS_ENDPOINT}"
    return urlparse(remote)


class ApifiedHarvester(IWebAgent, IHarvester):
    """One-shot harvester that calls /find_trayectory and returns a complete trajectory."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        id: str | None = None,
        name: str | None = None,
        timeout=180,
        base_url: str | None = None,
        endpoint_path: str = "/find_trayectory",
        fallback_endpoint_paths: list[str] | None = None,
    ):
        self.id = id or generate_random_web_agent_id()
        self.name = name or f"Harvester {self.id}"
        if base_url:
            self.base_url = base_url.rstrip("/")
        elif host is None:
            raise ValueError("host must be provided when base_url is not set")
        elif port is not None:
            self.base_url = f"http://{host}:{port}"
        else:
            self.base_url = f"http://{host}"
        self.timeout = timeout
        self.endpoint_path = self._normalize_endpoint_path(endpoint_path)
        self.fallback_endpoint_paths = [self._normalize_endpoint_path(path) for path in (fallback_endpoint_paths or [])]
        self._cached_solution: TaskSolution | None = None
        self.last_find_trayectory_response: dict[str, Any] | None = None

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
            solution = await self.find_trayectory(task)
            self._cached_solution = solution
            return solution.actions
        return []

    async def act(self, **kwargs) -> list[BaseAction]:
        return await self.step(**kwargs)

    async def find_trayectory(self, task: Task) -> TaskSolution:
        return await self._find_trayectory(task)

    async def _find_trayectory(self, task: Task) -> TaskSolution:
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                payload = task.clean_task()
                payload["url"] = self._force_localhost(payload.get("url"))
                response_json = await self._post_find_trayectory(session, payload)
                trajectory_data = self._extract_trajectory_data(response_json)
                web_agent_id = response_json.get("web_agent_id") or self.id
                rebuilt = [a for raw in trajectory_data if isinstance(raw, dict) for a in [self._create_action(raw)] if a]
        except Exception as exc:
            raise RuntimeError(f"Failed to find trayectory via remote harvester: {exc}") from exc

        return TaskSolution(
            task_id=task.id,
            actions=rebuilt,
            web_agent_id=web_agent_id,
            recording=response_json.get("recording"),
            cost_usd=float(response_json.get("cost_usd") or 0.0),
            input_tokens=int(response_json.get("input_tokens") or 0),
            output_tokens=int(response_json.get("output_tokens") or 0),
            model_used=response_json.get("model_used"),
            extracted_data=response_json.get("extracted_data"),
        )

    async def _post_find_trayectory(self, session: aiohttp.ClientSession, payload: dict[str, Any]) -> dict[str, Any]:
        endpoints = [self.endpoint_path, *[path for path in self.fallback_endpoint_paths if path != self.endpoint_path]]
        last_error: Exception | None = None
        for endpoint_path in endpoints:
            try:
                async with session.post(f"{self.base_url}{endpoint_path}", json=payload) as response:
                    status = int(getattr(response, "status", 200) or 200)
                    if status == 404 and endpoint_path != endpoints[-1]:
                        last_error = RuntimeError(f"{endpoint_path} returned 404")
                        continue
                    if status >= 400:
                        body = _short_response_body(await response.text())
                        raise RuntimeError(
                            f"{endpoint_path} returned HTTP {status} from {response.url}; body={body or '<empty>'}"
                        )
                    response_json = await response.json()
                    if not isinstance(response_json, dict):
                        raise ValueError("find_trayectory response must be a JSON object")
                    self.last_find_trayectory_response = response_json
                    return response_json
            except Exception as exc:
                last_error = exc
                break
        raise RuntimeError(last_error or "find_trayectory endpoint unavailable")

    @staticmethod
    def _extract_trajectory_data(response_json: dict[str, Any]) -> list[dict[str, Any]]:
        for field_name in ("trajectory", "tool_calls", "actions"):
            if field_name not in response_json:
                continue
            value = response_json[field_name]
            if not isinstance(value, list):
                raise ValueError(f"find_trayectory response `{field_name}` must be a list of tool calls")
            return [item for item in value if isinstance(item, dict)]
        return []

    def _create_action(self, raw: dict) -> BaseAction | None:
        try:
            action = BaseAction.create_action(raw)
            if action and isinstance(action, NavigateAction):
                action.url = self._rewrite_to_remote(getattr(action, "url", None))
            return action
        except Exception:
            return None

    @staticmethod
    def _normalize_endpoint_path(endpoint_path: str) -> str:
        endpoint = str(endpoint_path or "/find_trayectory").strip()
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
        return endpoint

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


class ApifiedOneShotWebAgent(ApifiedHarvester):
    """Backward-compatible name for ApifiedHarvester."""
