from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.utils.task_generation import (
    filter_tasks_by_use_cases,
    load_tasks_from_json,
    save_tasks_to_json,
)
from autoppia_iwa.src.data_generation.data_extraction.pipeline import (
    DataExtractionTaskGenerationPipeline,
)
from autoppia_iwa.src.data_generation.tasks.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.data_generation.tasks.pipeline import TaskGenerationPipeline
from autoppia_iwa.src.demo_webs.classes import WebProject


@dataclass(frozen=True, slots=True)
class EventTaskStrategy:
    name: str = "event"
    cache_subdir: str = "tasks"

    def get_selected_use_cases(self, config: BenchmarkConfig) -> list[str] | None:
        return config.use_cases

    def get_cache_dir(self, config: BenchmarkConfig) -> str:
        cache_root = Path(config.base_dir) / "benchmark-output" / "cache"
        return str(cache_root / self.cache_subdir)

    async def load_or_generate_tasks(self, project: WebProject, config: BenchmarkConfig) -> list[Task]:
        cache_dir = self.get_cache_dir(config)
        selected_use_cases = self.get_selected_use_cases(config)

        if getattr(config, "use_cached_tasks", False):
            cached_tasks = await load_tasks_from_json(project, cache_dir)
            if cached_tasks:
                filtered = filter_tasks_by_use_cases(cached_tasks, selected_use_cases)
                logger.info(f"[{self.name}] Using {len(filtered)} cached tasks for '{project.name}'")
                return filtered
            logger.info(f"[{self.name}] No cached tasks found for '{project.name}', generating new tasks...")

        task_config = TaskGenerationConfig(
            prompts_per_use_case=config.prompts_per_use_case,
            use_cases=selected_use_cases,
            dynamic=config.dynamic,
            test_types="event_only",
            data_extraction_use_cases=None,
        )
        pipeline = TaskGenerationPipeline(web_project=project, config=task_config)
        tasks = await pipeline.generate()
        if tasks:
            await save_tasks_to_json(tasks, project, cache_dir)
            logger.info(f"[{self.name}] Saved {len(tasks)} generated tasks for '{project.name}' to cache")
        return tasks


@dataclass(frozen=True, slots=True)
class DataExtractionTaskStrategy:
    name: str = "data_extraction"
    cache_subdir: str = "DataExtraction"

    def get_selected_use_cases(self, config: BenchmarkConfig) -> list[str] | None:
        return config.data_extraction_use_cases

    def get_cache_dir(self, config: BenchmarkConfig) -> str:
        cache_root = Path(config.base_dir) / "benchmark-output" / "cache"
        return str(cache_root / self.cache_subdir)

    async def load_or_generate_tasks(self, project: WebProject, config: BenchmarkConfig) -> list[Task]:
        cache_dir = self.get_cache_dir(config)
        selected_use_cases = self.get_selected_use_cases(config)

        if getattr(config, "use_cached_tasks", False):
            cached_tasks = await load_tasks_from_json(project, cache_dir)
            if cached_tasks:
                filtered = filter_tasks_by_use_cases(cached_tasks, selected_use_cases)
                logger.info(f"[{self.name}] Using {len(filtered)} cached tasks for '{project.name}'")
                return filtered
            logger.info(f"[{self.name}] No cached tasks found for '{project.name}', generating new tasks...")

        task_config = TaskGenerationConfig(
            prompts_per_use_case=config.prompts_per_use_case,
            use_cases=selected_use_cases,
            dynamic=config.dynamic,
            test_types="data_extraction_only",
            data_extraction_use_cases=selected_use_cases,
        )
        pipeline = DataExtractionTaskGenerationPipeline(web_project=project, config=task_config)
        tasks = await pipeline.generate()
        if tasks:
            await save_tasks_to_json(tasks, project, cache_dir)
            logger.info(f"[{self.name}] Saved {len(tasks)} generated tasks for '{project.name}' to cache")
        return tasks
