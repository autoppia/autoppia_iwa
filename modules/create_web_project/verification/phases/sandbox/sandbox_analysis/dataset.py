"""Dataset utilities for sandbox analytics."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from statistics import median
from typing import Any


@dataclass(slots=True)
class SolutionRecord:
    agent_id: str
    final_score: float
    actions: list[dict[str, Any]] | None = None
    action_count: int | None = None
    evaluation_time: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def resolved(self, success_threshold: float) -> bool:
        return self.final_score >= success_threshold

    def total_actions(self) -> int:
        if self.action_count is not None:
            return self.action_count
        if self.actions:
            return len(self.actions)
        return 0


@dataclass(slots=True)
class DatasetEntry:
    project_id: str
    use_case: str
    task_id: str
    prompt: str
    url: str
    seed: str | None
    solutions: list[SolutionRecord]
    task_payload: dict[str, Any] | None = None

    def success_rate(self, success_threshold: float) -> float:
        if not self.solutions:
            return 0.0
        successes = sum(sol.resolved(success_threshold) for sol in self.solutions)
        return successes / len(self.solutions)

    def median_actions(self) -> float:
        counts = [sol.total_actions() for sol in self.solutions if sol.total_actions() > 0]
        return float(median(counts)) if counts else 0.0


def _parse_seed(url: str) -> str | None:
    if "?seed=" in url:
        return url.split("?seed=", 1)[1].split("&", 1)[0]
    return None


def _load_json_records(data: Any) -> list[dict]:
    if isinstance(data, dict) and "entries" in data:
        return list(data["entries"])
    if isinstance(data, list):
        return data
    raise ValueError("Dataset JSON must be a list or contain an 'entries' field.")


def _load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def load_dataset(path: str | Path) -> list[DatasetEntry]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    try:
        text = path.read_text()
        data = json.loads(text)
        raw_records = _load_json_records(data)
    except json.JSONDecodeError:
        raw_records = _load_jsonl(path)

    entries: list[DatasetEntry] = []

    for raw in raw_records:
        solutions_raw: Iterable[dict[str, Any]] = raw.get("solutions") or raw.get("task_solutions") or []
        solutions = [
            SolutionRecord(
                agent_id=str(sol.get("agent_id", "unknown")),
                final_score=float(sol.get("final_score", sol.get("score", 0.0))),
                actions=sol.get("actions"),
                action_count=sol.get("action_count"),
                evaluation_time=sol.get("evaluation_time"),
                metadata={k: v for k, v in sol.items() if k not in {"agent_id", "final_score", "score", "actions", "action_count", "evaluation_time"}},
            )
            for sol in solutions_raw
        ]
        task_payload = raw.get("task") or raw.get("task_payload")
        url = raw.get("url") or (task_payload or {}).get("url") or ""
        prompt = raw.get("prompt") or (task_payload or {}).get("prompt") or ""
        task_id = raw.get("task_id") or (task_payload or {}).get("id") or "unknown"
        seed = raw.get("seed") or _parse_seed(url)

        entries.append(
            DatasetEntry(
                project_id=raw.get("project_id") or raw.get("web_project_id") or "unknown",
                use_case=raw.get("use_case") or (task_payload or {}).get("use_case") or "unknown",
                task_id=task_id,
                prompt=prompt,
                url=url,
                seed=seed,
                solutions=solutions,
                task_payload=task_payload,
            )
        )

    return entries
