from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Iterable
from urllib.parse import urlsplit

from .dataset import DatasetEntry, SolutionRecord


def compute_project_metrics(entries: Iterable[DatasetEntry], success_threshold: float = 0.99) -> dict:
    projects: dict[str, dict] = {}
    grouped: dict[tuple[str, str], list[DatasetEntry]] = defaultdict(list)
    for entry in entries:
        grouped[(entry.project_id, entry.use_case)].append(entry)

    for (project_id, use_case), items in grouped.items():
        total_tasks = len(items)
        total_solutions = sum(len(item.solutions) for item in items)
        success_rates = [item.success_rate(success_threshold) for item in items if item.solutions]
        avg_success = mean(success_rates) if success_rates else 0.0
        avg_actions = mean(item.median_actions() for item in items if item.solutions) if items else 0.0
        project_block = projects.setdefault(
            project_id,
            {
                "use_cases": {},
                "totals": {"tasks": 0, "solutions": 0},
            },
        )
        project_block["use_cases"][use_case] = {
            "tasks": total_tasks,
            "solutions": total_solutions,
            "avg_success_rate": round(avg_success, 3),
            "median_actions": round(avg_actions, 2),
        }
        project_block["totals"]["tasks"] += total_tasks
        project_block["totals"]["solutions"] += total_solutions
    return projects


def find_unresolved_tasks(entries: Iterable[DatasetEntry], success_threshold: float = 0.99) -> list[DatasetEntry]:
    return [entry for entry in entries if entry.success_rate(success_threshold) == 0]


def find_trivial_tasks(
    entries: Iterable[DatasetEntry],
    success_threshold: float = 0.99,
    min_action_count: int = 3,
) -> list[DatasetEntry]:
    trivial: list[DatasetEntry] = []
    for entry in entries:
        if not entry.solutions:
            continue
        if entry.success_rate(success_threshold) >= 0.98 and entry.median_actions() <= min_action_count:
            trivial.append(entry)
    return trivial


def detect_agent_memorization(entries: Iterable[DatasetEntry]) -> dict[str, dict]:
    from hashlib import sha256
    import json

    agent_hashes: dict[str, set[str]] = defaultdict(set)
    agent_counts: dict[str, int] = defaultdict(int)

    for entry in entries:
        for sol in entry.solutions:
            agent_counts[sol.agent_id] += 1
            if not sol.actions:
                continue
            serialized = json.dumps(sol.actions, sort_keys=True)
            digest = sha256(serialized.encode()).hexdigest()
            agent_hashes[sol.agent_id].add(digest)

    findings: dict[str, dict] = {}
    for agent, total in agent_counts.items():
        unique = len(agent_hashes.get(agent, set()))
        ratio = unique / total if total else 0
        findings[agent] = {
            "solutions": total,
            "unique_action_sequences": unique,
            "diversity_ratio": round(ratio, 3),
            "flagged": total >= 20 and ratio < 0.2,
        }
    return findings


@dataclass(slots=True)
class SeedVariability:
    project_id: str
    basis: str
    seed_success: dict[str, float]
    variance: float


def _strip_seed(url: str) -> str:
    parsed = urlsplit(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def compute_seed_variability(entries: Iterable[DatasetEntry], success_threshold: float = 0.99) -> list[SeedVariability]:
    grouped: dict[tuple[str, str], list[DatasetEntry]] = defaultdict(list)
    for entry in entries:
        basis = _strip_seed(entry.url) if entry.url else entry.task_id
        grouped[(entry.project_id, basis)].append(entry)

    findings: list[SeedVariability] = []
    for (project_id, basis), items in grouped.items():
        per_seed = defaultdict(list)
        for entry in items:
            per_seed[entry.seed or "none"].append(entry.success_rate(success_threshold))
        if len(per_seed) < 2:
            continue
        seed_success = {seed: mean(rates) for seed, rates in per_seed.items()}
        values = list(seed_success.values())
        variance = pstdev(values) if len(values) >= 2 else 0.0
        findings.append(
            SeedVariability(
                project_id=project_id,
                basis=basis,
                seed_success={k: round(v, 3) for k, v in seed_success.items()},
                variance=variance,
            )
        )
    return findings
