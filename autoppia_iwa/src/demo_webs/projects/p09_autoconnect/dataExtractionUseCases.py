from __future__ import annotations

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.projects.data_extraction_use_cases_common import (
    DataExtractionCaseConfig,
    DataExtractionUseCaseDefinition,
    build_de_task,
    keep_non_empty_rows,
    normalize_selected_use_cases,
    pick_row,
)

from .data_utils import fetch_data

DATA_EXTRACTION_USE_CASES: list[DataExtractionUseCaseDefinition] = [
    DataExtractionUseCaseDefinition(name="FIND_PERSON", description="Find a person from AutoConnect data."),
    DataExtractionUseCaseDefinition(name="FIND_POST", description="Find a post from AutoConnect data."),
    DataExtractionUseCaseDefinition(name="FIND_RECOMMENDATION", description="Find a recommendation from AutoConnect data."),
]

CASE_CONFIGS: dict[str, DataExtractionCaseConfig] = {
    "FIND_PERSON": DataExtractionCaseConfig(
        answer_keys=("name", "username", "full_name"),
        identifier_keys=("title", "bio", "location", "email"),
        answer_label="person",
        entity_label="profile",
    ),
    "FIND_POST": DataExtractionCaseConfig(
        answer_keys=("content", "text", "title"),
        identifier_keys=("poster_name", "name", "username", "created_at"),
        answer_label="post",
        entity_label="post",
    ),
    "FIND_RECOMMENDATION": DataExtractionCaseConfig(
        answer_keys=("recommendation", "name", "title"),
        identifier_keys=("category", "description", "source"),
        answer_label="recommendation",
        entity_label="recommendation",
    ),
}


async def _load_rows_for_use_case(*, seed: int, use_case_name: str) -> list[dict]:
    if use_case_name == "FIND_POST":
        return await fetch_data(entity_type="posts", method="select", seed_value=int(seed), count=80)
    if use_case_name == "FIND_RECOMMENDATION":
        return await fetch_data(entity_type="recommendations", method="select", seed_value=int(seed), count=80)
    return await fetch_data(entity_type="users", method="select", seed_value=int(seed), count=80)


async def generate_de_tasks(
    *,
    seed: int,
    task_url: str,
    selected_use_cases: set[str] | None = None,
) -> list[Task]:
    selected = normalize_selected_use_cases(selected_use_cases, DATA_EXTRACTION_USE_CASES)
    tasks: list[Task] = []

    for offset, definition in enumerate(DATA_EXTRACTION_USE_CASES, start=1):
        if definition.name not in selected:
            continue

        rows = keep_non_empty_rows(await _load_rows_for_use_case(seed=int(seed), use_case_name=definition.name))
        if not rows:
            continue

        row = pick_row(rows=rows, seed=int(seed), offset=offset)
        task = build_de_task(
            project_id="autoconnect",
            task_url=task_url,
            seed=int(seed),
            use_case_name=definition.name,
            row=row,
            config=CASE_CONFIGS[definition.name],
        )
        if task:
            tasks.append(task)

    return tasks
