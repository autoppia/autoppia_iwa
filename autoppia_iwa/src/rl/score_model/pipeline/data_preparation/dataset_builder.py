"""Utilities for flattening leaderboard API responses into training samples."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from typing import Any, ClassVar

from loguru import logger

from .leaderboard_ingest import LeaderboardRecord


@dataclass
class LeaderboardSample:
    task_id: str
    task_created_at: str | None
    website: str | None
    use_case: str | None
    intent: str | None
    start_url: str | None
    required_url: str | None
    solution_id: str | None
    agent_run_id: str | None
    miner_uid: int | None
    validator_uid: int | None
    score: float | None
    passed: bool | None
    num_actions: int
    actions: list[dict[str, Any]]
    trajectory: list[Any]
    fetched_at: str
    filters: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LeaderboardDatasetBuilder:
    """Turn leaderboard API rows into deduplicated samples."""

    VALID_STRATEGIES: ClassVar = {"task_solution", "task_agent", "task"}

    def __init__(self, dedupe_strategy: str = "task_solution") -> None:
        if dedupe_strategy not in self.VALID_STRATEGIES:
            raise ValueError(f"Unknown dedupe_strategy '{dedupe_strategy}'")
        self.dedupe_strategy = dedupe_strategy

    def _make_key(self, entry: dict[str, Any]) -> str | None:
        task = entry.get("task") or {}
        solution = entry.get("solution") or {}
        agent_run = entry.get("agentRun") or {}

        task_id = task.get("taskId")
        solution_id = solution.get("taskSolutionId")
        miner_uid = agent_run.get("minerUid")

        if self.dedupe_strategy == "task_solution":
            if task_id and solution_id:
                return f"{task_id}:{solution_id}"
            return solution_id or task_id
        if self.dedupe_strategy == "task_agent":
            if task_id and miner_uid is not None:
                return f"{task_id}:{miner_uid}"
            return task_id
        return task_id

    def build(self, records: Iterable[LeaderboardRecord]) -> list[LeaderboardSample]:
        samples: list[LeaderboardSample] = []
        seen: set[str | None] = set()
        for record in records:
            entry = record.entry
            key = self._make_key(entry)
            if key and key in seen:
                continue
            if key:
                seen.add(key)
            task = entry.get("task") or {}
            solution = entry.get("solution") or {}
            evaluation = entry.get("evaluation") or {}
            agent_run = entry.get("agentRun") or {}
            actions = solution.get("actions") or []
            trajectory = solution.get("trajectory") or []
            sample = LeaderboardSample(
                task_id=task.get("taskId"),
                task_created_at=task.get("createdAt"),
                website=task.get("website"),
                use_case=task.get("useCase"),
                intent=task.get("intent"),
                start_url=task.get("startUrl"),
                required_url=task.get("requiredUrl"),
                solution_id=solution.get("taskSolutionId"),
                agent_run_id=agent_run.get("agentRunId"),
                miner_uid=agent_run.get("minerUid"),
                validator_uid=agent_run.get("validatorUid"),
                score=evaluation.get("score"),
                passed=evaluation.get("passed"),
                num_actions=len(actions),
                actions=actions,
                trajectory=trajectory,
                fetched_at=record.fetched_at,
                filters=record.filter_params,
            )
            if not sample.task_id:
                logger.debug("Skipping row without task_id: {}", entry)
                continue
            samples.append(sample)
        return samples

    @staticmethod
    def summarize(samples: list[LeaderboardSample]) -> dict[str, Any]:
        total = len(samples)
        website_counter = Counter(sample.website for sample in samples if sample.website)
        use_case_counter = Counter(sample.use_case for sample in samples if sample.use_case)
        pass_counter = Counter(sample.passed for sample in samples if sample.passed is not None)
        return {
            "total": total,
            "websites": dict(website_counter),
            "use_cases": dict(use_case_counter),
            "pass_counts": {str(key): value for key, value in pass_counter.items()},
            "avg_actions": sum(sample.num_actions for sample in samples) / total if total else 0.0,
        }
