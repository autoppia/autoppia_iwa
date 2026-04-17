"""
IWA Debugger — FastAPI server for inspecting benchmark traces.

Reads trace data written by Benchmark (trace_index.json + episode JSONs)
and serves a web UI for step-by-step inspection with HTML diffs, screenshots,
and live browser replay.

Usage:
    python -m modules.debugger.server
    python -m modules.debugger.server --trace-dir ./benchmark-output/traces/run_20260316
    iwa debug
"""

from __future__ import annotations

import asyncio
import contextlib
import difflib
import json
import os
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="IWA Debugger")

ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
DEFAULT_TRACE_DIR = os.getenv("IWA_DEBUG_TRACE_DIR", "").strip()

# Extra allowed roots for trace_dir (query param / env), separated by os.pathsep.
# Without this, trace_dir must resolve under cwd, under TRACE_SCAN_ROOTS, or equal IWA_DEBUG_TRACE_DIR.
_TRACE_ALLOW_EXTRA_RAW = os.getenv("IWA_DEBUG_TRACE_ALLOW_ROOTS", "").strip()

# Scan these directories for trace_index.json files
TRACE_SCAN_ROOTS = [
    Path.cwd() / "benchmark-output" / "traces",
    Path.cwd() / "data" / "traces",
]

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── Helpers ─────────────────────────────────────────────────────────────


def _jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    return value


def _allowed_trace_roots() -> tuple[Path, ...]:
    """Resolved directories under which a user-supplied trace_dir may lie."""
    candidates: list[Path] = []
    seen: set[str] = set()

    def add(p: Path) -> None:
        try:
            r = p.expanduser().resolve()
        except (OSError, RuntimeError):
            return
        key = str(r)
        if key not in seen:
            seen.add(key)
            candidates.append(r)

    add(Path.cwd())
    for root in TRACE_SCAN_ROOTS:
        add(root)
    if DEFAULT_TRACE_DIR:
        add(Path(DEFAULT_TRACE_DIR))
    for part in _TRACE_ALLOW_EXTRA_RAW.split(os.pathsep):
        part = part.strip()
        if part:
            add(Path(part))
    return tuple(candidates)


def _is_under_allowed_root(resolved: Path, roots: tuple[Path, ...]) -> bool:
    for root in roots:
        try:
            resolved.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def _resolved_if_valid(path: Path) -> Path | None:
    with contextlib.suppress(OSError, RuntimeError):
        return path.expanduser().resolve()
    return None


def _iter_known_trace_dirs(roots: tuple[Path, ...]) -> list[Path]:
    items: list[Path] = []
    seen: set[str] = set()

    def add(path: Path) -> None:
        resolved = _resolved_if_valid(path)
        if resolved is None:
            return
        key = str(resolved)
        if key in seen:
            return
        if (resolved / "trace_index.json").is_file():
            seen.add(key)
            items.append(resolved)

    for root in roots:
        add(root)
        if not root.exists():
            continue
        for idx_path in root.rglob("trace_index.json"):
            add(idx_path.parent)
    return items


def _trace_dir_allowlist() -> dict[str, Path]:
    roots = _allowed_trace_roots()
    allowlist: dict[str, Path] = {}
    for path in _iter_known_trace_dirs(roots):
        allowlist[str(path)] = path
        for root in roots:
            with contextlib.suppress(ValueError):
                rel = path.relative_to(root)
                key = rel.as_posix().strip()
                if key:
                    allowlist.setdefault(key, path)
    return allowlist


def _normalize_safe_trace_dir_input(raw: str) -> str | None:
    value = str(raw or "").strip()
    if not value or "\x00" in value:
        return None
    if os.path.isabs(value):
        return None

    normalized = value.replace("\\", "/")
    parts: list[str] = []
    for part in normalized.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            return None
        parts.append(part)
    return "/".join(parts) if parts else None


def _resolved_lookup_keys(raw: str) -> list[str]:
    normalized = _normalize_safe_trace_dir_input(raw)
    return [normalized] if normalized is not None else []


def _episode_file_map(trace_dir: Path) -> dict[str, Path]:
    """Allow episode file access only for direct *.json children discovered on disk."""
    out: dict[str, Path] = {}
    for candidate in trace_dir.glob("*.json"):
        if candidate.name == "trace_index.json":
            continue
        resolved = _resolved_if_valid(candidate)
        if resolved is None:
            continue
        if resolved.parent != trace_dir:
            continue
        out[candidate.name] = resolved
    return out


def _resolve_trace_dir(raw: str | None = None) -> Path:
    value = str(raw if raw is not None else DEFAULT_TRACE_DIR or "").strip()
    if not value or "\x00" in value:
        raise HTTPException(status_code=400, detail="trace_dir_missing")

    allowed = _trace_dir_allowlist()
    if not allowed:
        raise HTTPException(status_code=404, detail="trace_dir_not_found")

    if raw is None:
        path = allowed.get(value)
        if path is not None:
            return path

    for key in _resolved_lookup_keys(value):
        path = allowed.get(key)
        if path is not None:
            return path
    raise HTTPException(status_code=404, detail="trace_dir_not_found")


def _load_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise HTTPException(status_code=500, detail=f"invalid_json:{path}")
    return data


def _pretty_json(value: Any) -> str:
    return json.dumps(value if value is not None else {}, indent=2, ensure_ascii=False, sort_keys=True)


def _unified_diff(before: str, after: str, *, from_label: str, to_label: str, limit: int = 400) -> str:
    lines = list(
        difflib.unified_diff(
            str(before or "").splitlines(),
            str(after or "").splitlines(),
            fromfile=from_label,
            tofile=to_label,
            lineterm="",
            n=2,
        )
    )
    if len(lines) > limit:
        lines = [*lines[:limit], f"... truncated ({len(lines) - limit} more lines)"]
    return "\n".join(lines)


def _normalize_image(raw: Any) -> str | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    data = raw.strip()
    return data if data.startswith("data:image/") else f"data:image/png;base64,{data}"


def _scan_trace_dirs() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for root in TRACE_SCAN_ROOTS:
        if not root.exists():
            continue
        for idx_path in root.rglob("trace_index.json"):
            trace_dir = idx_path.parent.resolve()
            with contextlib.suppress(Exception):
                idx = _load_json(idx_path)
                episodes = idx.get("episodes") if isinstance(idx.get("episodes"), list) else []
                items.append(
                    {
                        "trace_dir": str(trace_dir),
                        "name": trace_dir.name,
                        "project": str(idx.get("project") or idx.get("web_project_id") or ""),
                        "model": str(idx.get("model") or ""),
                        "created_at_utc": str(idx.get("created_at_utc") or ""),
                        "episodes": len(episodes),
                    }
                )
    items.sort(key=lambda x: x.get("created_at_utc", ""), reverse=True)
    return items


# ── Trace loading ───────────────────────────────────────────────────────


def _load_trace_bundle(trace_dir: Path) -> dict[str, Any]:
    idx = _load_json(trace_dir / "trace_index.json")
    raw_episodes = idx.get("episodes") if isinstance(idx.get("episodes"), list) else []
    episode_files = _episode_file_map(trace_dir)
    episodes = []
    for item in raw_episodes:
        if not isinstance(item, dict):
            continue
        file_name = str(item.get("file") or "").strip()
        ep_file = episode_files.get(file_name) if file_name else None
        summary = {
            "episode_task_id": str(item.get("episode_task_id") or ""),
            "task_id": str(item.get("task_id") or ""),
            "use_case": str(item.get("use_case") or ""),
            "success": bool(item.get("success")),
            "score": float(item.get("score") or 0.0),
            "steps": int(item.get("steps") or 0),
            "file": str(item.get("file") or ""),
        }
        if ep_file is not None:
            with contextlib.suppress(Exception):
                ep = _load_json(ep_file)
                meta = ep.get("episode") if isinstance(ep.get("episode"), dict) else {}
                summary["task_seconds"] = float(meta.get("task_seconds") or meta.get("evaluation_time") or 0.0)
                summary["llm_calls"] = int(meta.get("llm_calls") or 0)
        episodes.append(summary)
    return {"trace_dir": str(trace_dir), "trace_index": idx, "episodes": episodes}


def _compact_step(step: dict[str, Any]) -> dict[str, Any]:
    before = step.get("before") or {}
    after = step.get("after") or {}
    agent = step.get("agent") or {}
    execution = step.get("execution") or {}
    actions = step.get("actions") or []
    return {
        "step_index": int(step.get("step_index") or 0),
        "before_url": str(before.get("url") or ""),
        "after_url": str(after.get("url") or ""),
        "before_score": float(before.get("score") or 0.0),
        "after_score": float(after.get("score") or 0.0),
        "done": bool(agent.get("done")),
        "action_types": [str((a or {}).get("type") or "") for a in actions if isinstance(a, dict)],
        "exec_ok": bool(execution.get("exec_ok", True)),
        "error": str(execution.get("error") or ""),
        "reasoning": str(agent.get("reasoning") or ""),
    }


def _annotate_step(step: dict[str, Any]) -> dict[str, Any]:
    before = step.get("before") or {}
    after = step.get("after") or {}
    step.get("agent") or {}
    out = dict(step)
    out["before"] = dict(before)
    out["after"] = dict(after)
    out["before"]["screenshot"] = _normalize_image(before.get("screenshot"))
    out["after"]["screenshot"] = _normalize_image(after.get("screenshot"))
    out["diffs"] = {
        "html": _unified_diff(str(before.get("html") or ""), str(after.get("html") or ""), from_label="before", to_label="after"),
    }
    return out


def _load_episode(trace_dir: Path, episode_task_id: str) -> dict[str, Any]:
    bundle = _load_trace_bundle(trace_dir)
    episode_files = _episode_file_map(trace_dir)
    for item in bundle["episodes"]:
        if str(item.get("episode_task_id") or "") != episode_task_id:
            continue
        file_name = str(item.get("file") or "").strip()
        if not file_name:
            raise HTTPException(status_code=404, detail=f"episode_file_missing:{episode_task_id}")
        path = episode_files.get(file_name)
        if path is None:
            raise HTTPException(status_code=404, detail=f"episode_file_not_found:{episode_task_id}")
        payload = _load_json(path)
        steps = payload.get("steps") if isinstance(payload.get("steps"), list) else []
        annotated = [_annotate_step(s) for s in steps if isinstance(s, dict)]
        payload["steps"] = annotated
        payload["step_summaries"] = [_compact_step(s) for s in annotated]
        payload["trace_dir"] = str(trace_dir)
        return payload
    raise HTTPException(status_code=404, detail=f"episode_not_found:{episode_task_id}")


# ── Replay manager ──────────────────────────────────────────────────────


class ReplayManager:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._task: asyncio.Task | None = None
        self._evaluator = None
        self._paused = False
        self._step_tokens = 0
        self._status: dict[str, Any] = {"state": "idle"}

    def status(self) -> dict[str, Any]:
        return {**self._status, "paused": self._paused, "running": bool(self._task and not self._task.done())}

    async def start(self, *, trace_dir: Path, episode_payload: dict[str, Any]) -> dict[str, Any]:
        async with self._lock:
            if self._task and not self._task.done():
                raise HTTPException(status_code=409, detail="replay_already_running")
            self._paused = False
            self._step_tokens = 0
            self._status = {"state": "starting", "episode_task_id": str((episode_payload.get("episode") or {}).get("episode_task_id") or "")}
            self._task = asyncio.create_task(self._run(trace_dir=trace_dir, episode_payload=episode_payload))
            return self.status()

    async def pause(self) -> dict[str, Any]:
        self._paused = True
        self._status["state"] = "paused"
        return self.status()

    async def resume(self) -> dict[str, Any]:
        self._paused = False
        self._status["state"] = "running"
        return self.status()

    async def step_once(self) -> dict[str, Any]:
        self._paused = True
        self._step_tokens += 1
        return self.status()

    async def reset(self) -> dict[str, Any]:
        async with self._lock:
            if self._task and not self._task.done():
                self._task.cancel()
                with contextlib.suppress(Exception):
                    await self._task
            self._task = None
            if self._evaluator:
                with contextlib.suppress(Exception):
                    await self._evaluator.close()
            self._evaluator = None
            self._paused = False
            self._step_tokens = 0
            self._status = {"state": "idle"}
            return self.status()

    async def _wait_turn(self) -> None:
        while self._paused:
            if self._step_tokens > 0:
                self._step_tokens -= 1
                return
            await asyncio.sleep(0.1)

    async def _run(self, *, trace_dir: Path, episode_payload: dict[str, Any]) -> None:
        from autoppia_iwa.src.data_generation.tasks.classes import Task
        from autoppia_iwa.src.evaluation.stateful_evaluator import AsyncStatefulEvaluator
        from autoppia_iwa.src.execution.actions.base import BaseAction

        episode_meta = episode_payload.get("episode") or {}
        task_id = str(episode_meta.get("task_id") or "")
        web_agent_id = f"debug-replay-{int(time.time())}"

        try:
            # Load task from trace metadata
            task_data = episode_meta.get("task")
            if not isinstance(task_data, dict):
                raise RuntimeError(f"Episode trace missing 'task' field for task_id={task_id}")
            task = Task(**task_data)

            evaluator = AsyncStatefulEvaluator(task=task, web_agent_id=web_agent_id, headless=False)
            self._evaluator = evaluator
            step_result = await evaluator.reset()
            self._status.update({"state": "running", "current_url": step_result.snapshot.url})

            for idx, step in enumerate(episode_payload.get("steps") or []):
                await self._wait_turn()
                actions = step.get("actions") if isinstance(step, dict) else []
                self._status.update({"current_step": idx, "state": "running"})

                for action_item in actions if isinstance(actions, list) else []:
                    await self._wait_turn()
                    raw = (action_item.get("raw") if isinstance(action_item, dict) else None) or action_item
                    action = BaseAction.create_action(raw) if isinstance(raw, dict) else None
                    if action is None:
                        continue
                    step_result = await evaluator.step(action)
                    self._status["current_url"] = step_result.snapshot.url

                await asyncio.sleep(0.15)

            self._status["state"] = "completed"
        except asyncio.CancelledError:
            self._status["state"] = "cancelled"
        except Exception as e:
            self._status.update({"state": "error", "error": str(e)[:400]})
        finally:
            if self._evaluator:
                with contextlib.suppress(Exception):
                    await self._evaluator.close()
            self._evaluator = None


REPLAY = ReplayManager()


# ── Routes ──────────────────────────────────────────────────────────────


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/")
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/traces")
def api_traces():
    return JSONResponse(_jsonable({"items": _scan_trace_dirs(), "default_trace_dir": DEFAULT_TRACE_DIR}))


@app.get("/api/run")
def api_run(trace_dir: str | None = Query(default=None)):
    return JSONResponse(_jsonable(_load_trace_bundle(_resolve_trace_dir(trace_dir))))


@app.get("/api/episode/{episode_task_id}")
def api_episode(episode_task_id: str, trace_dir: str | None = Query(default=None)):
    return JSONResponse(_jsonable(_load_episode(_resolve_trace_dir(trace_dir), episode_task_id)))


@app.get("/api/replay/status")
def api_replay_status():
    return JSONResponse(_jsonable(REPLAY.status()))


@app.post("/api/replay/start")
async def api_replay_start(request: Request, trace_dir: str | None = Query(default=None)):
    path = _resolve_trace_dir(trace_dir)
    try:
        raw = await request.json()
    except json.JSONDecodeError:
        raw = {}
    payload = raw if isinstance(raw, dict) else {}
    eid = str(payload.get("episode_task_id") or "").strip()
    if not eid:
        raise HTTPException(status_code=400, detail="episode_task_id_required")
    ep = _load_episode(path, eid)
    return JSONResponse(_jsonable(await REPLAY.start(trace_dir=path, episode_payload=ep)))


@app.post("/api/replay/pause")
async def api_replay_pause():
    return JSONResponse(_jsonable(await REPLAY.pause()))


@app.post("/api/replay/resume")
async def api_replay_resume():
    return JSONResponse(_jsonable(await REPLAY.resume()))


@app.post("/api/replay/step")
async def api_replay_step():
    return JSONResponse(_jsonable(await REPLAY.step_once()))


@app.post("/api/replay/reset")
async def api_replay_reset():
    return JSONResponse(_jsonable(await REPLAY.reset()))


# ── CLI ─────────────────────────────────────────────────────────────────


def main():
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(prog="iwa debug", description="IWA Debugger — inspect benchmark traces")
    parser.add_argument("--trace-dir", "-t", type=str, default=None, help="Default trace directory to load")
    parser.add_argument("--port", "-p", type=int, default=8888, help="Server port")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    args = parser.parse_args()

    if args.trace_dir:
        os.environ["IWA_DEBUG_TRACE_DIR"] = args.trace_dir

    print(f"\nIWA Debugger running at http://{args.host}:{args.port}\n")
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
