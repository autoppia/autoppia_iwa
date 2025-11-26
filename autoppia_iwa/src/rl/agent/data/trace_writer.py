from __future__ import annotations

import json
import time
from collections.abc import Iterable
from pathlib import Path

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.execution.classes import ActionExecutionResult


class EvaluationTraceWriter:
    """Persist evaluation traces (DOM + JS events) to JSONL for offline training."""

    def __init__(self, base_dir: Path | str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write_episode(
        self,
        project: WebProject,
        task: Task,
        agent_id: str,
        action_results: Iterable[ActionExecutionResult],
    ) -> Path:
        timestamp = int(time.time())
        episode_dir = self.base_dir / project.id / task.id
        episode_dir.mkdir(parents=True, exist_ok=True)
        output_path = episode_dir / f"{agent_id}_{timestamp}.jsonl"

        with output_path.open("w", encoding="utf-8") as fp:
            for idx, result in enumerate(action_results):
                row = {
                    "project_id": project.id,
                    "task_id": task.id,
                    "web_agent_id": agent_id,
                    "action_index": idx,
                    "action": result.action.model_dump(),
                    "success": result.successfully_executed,
                    "error": result.error,
                    "execution_time": result.execution_time,
                    "browser_snapshot": result.browser_snapshot.model_dump() if result.browser_snapshot else None,
                }
                fp.write(json.dumps(row, ensure_ascii=False) + "\n")

        return output_path
