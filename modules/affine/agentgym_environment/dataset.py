from __future__ import annotations

import asyncio
import random
from collections.abc import Sequence
from dataclasses import dataclass

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.task_generation import generate_tasks_for_project, get_projects_by_ids

try:
    from autoppia_iwa.src.data_generation.tasks.classes import Task
    from autoppia_iwa.src.demo_webs.classes import WebProject
    from autoppia_iwa.src.demo_webs.config import demo_web_projects
except ModuleNotFoundError:  # pragma: no cover - source-tree fallback
    from autoppia_iwa.autoppia_iwa.src.data_generation.tasks.classes import Task
    from autoppia_iwa.autoppia_iwa.src.demo_webs.classes import WebProject
    from autoppia_iwa.autoppia_iwa.src.demo_webs.config import demo_web_projects

from .config import AffineEnvConfig


@dataclass(frozen=True)
class TaskEntry:
    """A single task mapped to an AgentGym-style numeric id."""

    affine_id: int
    task: Task
    project: WebProject


class AffineTaskDataset:
    """Loads and indexes cached tasks so Affine can request them by numeric id."""

    def __init__(self, config: AffineEnvConfig):
        self.config = config
        self._entries: list[TaskEntry] = []
        self._id_map: dict[int, TaskEntry] = {}
        self._lock = asyncio.Lock()
        self._rng = random.Random(config.dataset_seed)

    async def initialize(self) -> int:
        """Load (or generate) tasks for each configured project."""

        if self._entries:
            return len(self._entries)

        async with self._lock:
            if self._entries:
                return len(self._entries)

            logger.info("Preparing Affine task dataset (projects=%s)", self.config.project_ids)
            selected_projects = get_projects_by_ids(demo_web_projects, self.config.project_ids)

            idx = 0
            for project in selected_projects:
                tasks = await generate_tasks_for_project(
                    project=project,
                    use_cached=self.config.use_cached_tasks,
                    cache_dir=self.config.tasks_cache_dir,
                    prompts_per_use_case=self.config.prompts_per_use_case,
                    num_use_cases=self.config.num_use_cases,
                    use_cases=None,
                    enable_dynamic_html=self.config.enable_dynamic_html,
                )

                if not tasks:
                    logger.warning("No tasks returned for project %s (%s)", project.name, project.id)
                    continue

                for task in tasks:
                    entry = TaskEntry(affine_id=idx, task=task, project=project)
                    self._entries.append(entry)
                    self._id_map[idx] = entry
                    idx += 1

            if not self._entries:
                raise RuntimeError("Affine task dataset is empty. Pre-generate caches or review configuration.")

            logger.info("Affine task dataset ready with %d tasks across %d projects.", len(self._entries), len(selected_projects))
            return len(self._entries)

    @property
    def size(self) -> int:
        return len(self._entries)

    def available_ids(self) -> list[int]:
        return list(self._id_map.keys())

    def sample_ids(self, count: int) -> list[int]:
        if self.size == 0:
            raise RuntimeError("Dataset not initialized yet.")

        count = min(max(1, count), self.size)
        if count == self.size:
            return self.available_ids()

        ids = self.available_ids()
        # Deterministic sampling if dataset_seed is provided
        return self._rng.sample(ids, k=count) if count else []

    def get_entries(self, ids: Sequence[int]) -> list[TaskEntry]:
        if not ids:
            raise ValueError("At least one task id is required.")
        missing = [identifier for identifier in ids if identifier not in self._id_map]
        if missing:
            raise ValueError(f"Unknown task ids requested: {missing}")
        return [self._id_map[identifier] for identifier in ids]

    def normalize_ids(self, requested: Sequence[int] | None, fallback_count: int) -> list[int]:
        if requested:
            # Validation happens in get_entries; we simply return the requested ids afterwards
            self.get_entries(requested)
            return list(requested)
        return self.sample_ids(fallback_count)
