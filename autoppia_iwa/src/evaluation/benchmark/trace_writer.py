"""
Writes per-step trace data for the debugger to consume.

Trace format:
    traces/<run_id>/
        trace_index.json          — run metadata + episode list
        episodes/
            <episode_task_id>.json — per-episode detail with steps

Each step captures: before/after snapshots (url, score, html, screenshot),
agent decision (actions, reasoning, done), and execution result.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from loguru import logger


class TraceWriter:
    """Accumulates trace data during a benchmark run and flushes to disk."""

    def __init__(self, trace_dir: Path, run_metadata: dict[str, Any] | None = None):
        self.trace_dir = trace_dir
        self.episodes_dir = trace_dir / "episodes"
        self.episodes_dir.mkdir(parents=True, exist_ok=True)
        self._episodes_index: list[dict[str, Any]] = []
        self._run_metadata = run_metadata or {}

    def start_episode(self, episode_task_id: str, task_id: str, use_case: str, task_data: dict[str, Any] | None = None) -> "EpisodeTrace":
        return EpisodeTrace(
            writer=self,
            episode_task_id=episode_task_id,
            task_id=task_id,
            use_case=use_case,
            task_data=task_data,
        )

    def _register_episode(self, summary: dict[str, Any]) -> None:
        self._episodes_index.append(summary)

    def flush(self) -> Path:
        """Write trace_index.json with all registered episodes."""
        index = {
            "created_at_utc": datetime.now(UTC).isoformat(),
            **self._run_metadata,
            "episodes": self._episodes_index,
        }
        path = self.trace_dir / "trace_index.json"
        path.write_text(json.dumps(index, indent=2, ensure_ascii=False, default=str))
        logger.info(f"Trace index written: {path} ({len(self._episodes_index)} episodes)")
        return path


class EpisodeTrace:
    """Accumulates steps for a single episode and writes to disk on close."""

    def __init__(self, writer: TraceWriter, episode_task_id: str, task_id: str, use_case: str, task_data: dict[str, Any] | None = None):
        self._writer = writer
        self.episode_task_id = episode_task_id
        self.task_id = task_id
        self.use_case = use_case
        self._task_data = task_data
        self._steps: list[dict[str, Any]] = []
        self._meta: dict[str, Any] = {}

    def record_step(
        self,
        step_index: int,
        *,
        before_url: str = "",
        before_html: str = "",
        before_score: float = 0.0,
        before_success: bool = False,
        before_screenshot: str | None = None,
        after_url: str = "",
        after_html: str = "",
        after_score: float = 0.0,
        after_success: bool = False,
        after_screenshot: str | None = None,
        actions: list[dict[str, Any]] | None = None,
        reasoning: str | None = None,
        done: bool = False,
        exec_ok: bool = True,
        error: str | None = None,
    ) -> None:
        self._steps.append(
            {
                "step_index": step_index,
                "before": {
                    "url": before_url,
                    "score": before_score,
                    "success": before_success,
                    "html": before_html,
                    "screenshot": before_screenshot,
                },
                "after": {
                    "url": after_url,
                    "score": after_score,
                    "success": after_success,
                    "html": after_html,
                    "screenshot": after_screenshot,
                },
                "agent": {
                    "done": done,
                    "reasoning": reasoning,
                },
                "actions": actions or [],
                "execution": {
                    "executed": True,
                    "exec_ok": exec_ok,
                    "error": error,
                },
            }
        )

    def close(self, *, success: bool, score: float, total_steps: int, evaluation_time: float = 0.0, **extra_meta) -> None:
        """Write episode JSON and register in the trace index."""
        filename = f"{self.episode_task_id}.json"
        episode_data = {
            "episode": {
                "task_id": self.task_id,
                "episode_task_id": self.episode_task_id,
                "use_case": self.use_case,
                "success": success,
                "score": score,
                "steps": total_steps,
                "evaluation_time": round(evaluation_time, 4),
                "task": self._task_data,
                **extra_meta,
            },
            "steps": self._steps,
        }
        path = self._writer.episodes_dir / filename
        path.write_text(json.dumps(episode_data, indent=2, ensure_ascii=False, default=str))

        self._writer._register_episode(
            {
                "episode_task_id": self.episode_task_id,
                "task_id": self.task_id,
                "use_case": self.use_case,
                "success": success,
                "score": score,
                "steps": total_steps,
                "file": f"episodes/{filename}",
            }
        )
