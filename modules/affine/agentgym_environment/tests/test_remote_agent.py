import importlib
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = REPO_ROOT / "autoppia_iwa"
for path in (PACKAGE_ROOT, REPO_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def _alias_inner(submodule: str) -> None:
    alias = f"autoppia_iwa.{submodule}"
    if alias in sys.modules:
        return
    try:
        target = importlib.import_module(f"autoppia_iwa.autoppia_iwa.{submodule}")
    except ModuleNotFoundError:
        return
    sys.modules[alias] = target


_alias_inner("src")
_alias_inner("config")

import httpx
import pytest

from autoppia_iwa.affine_env.agent_client import RemoteAgentClient
from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task

REMOTE_AGENT_BASE_URL = os.getenv("AUTOPPIA_REMOTE_AGENT_BASE_URL", "http://84.247.180.192:6789").rstrip("/")


def _require_remote_agent() -> dict:
    """Ping the live miner; skip tests when it is unavailable."""

    try:
        response = httpx.get(f"{REMOTE_AGENT_BASE_URL}/info", timeout=5.0)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        pytest.skip(f"Remote miner not reachable at {REMOTE_AGENT_BASE_URL}/info: {exc}")


def test_remote_agent_info_endpoint():
    info = _require_remote_agent()
    assert info.get("status") in {"active", "ok"}
    assert info.get("agent", {}).get("port") is not None


@pytest.mark.asyncio
async def test_remote_agent_returns_task_solution():
    _require_remote_agent()

    task = Task(
        prompt="Open the Autoppia Books homepage and capture a screenshot.",
        url="http://localhost:8001/",
        web_project_id="autobooks",
        specifications=BrowserSpecification(),
        tests=[],
    )

    client = RemoteAgentClient(base_url=REMOTE_AGENT_BASE_URL, timeout=30, web_agent_name="affine-integration-test")
    solution = await client.solve_task(task)

    assert solution.task_id == task.id
    assert isinstance(solution.actions, list)
