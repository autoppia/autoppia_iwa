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
    DataExtractionUseCaseDefinition(name="FIND_RESTAURANT", description="Find a restaurant name from its details."),
    DataExtractionUseCaseDefinition(name="FIND_RATING", description="Find the rating of a selected restaurant."),
    DataExtractionUseCaseDefinition(name="FIND_LOCATION", description="Find the location of a selected restaurant."),
    DataExtractionUseCaseDefinition(name="FIND_PLATE", description="Find one plate from a selected restaurant."),
    DataExtractionUseCaseDefinition(name="FIND_CUISINE", description="Find the cuisine of a selected restaurant."),
]

CASE_CONFIGS: dict[str, DataExtractionCaseConfig] = {
    "FIND_RESTAURANT": DataExtractionCaseConfig(
        answer_keys=("name",),
        identifier_keys=("cuisine", "area", "rating", "reviews"),
        answer_label="restaurant name",
        entity_label="restaurant",
    ),
    "FIND_RATING": DataExtractionCaseConfig(
        answer_keys=("rating",),
        identifier_keys=("name", "cuisine", "area"),
        answer_label="rating",
        entity_label="restaurant",
    ),
    "FIND_LOCATION": DataExtractionCaseConfig(
        answer_keys=("area", "location", "address"),
        identifier_keys=("name", "cuisine", "rating"),
        answer_label="location",
        entity_label="restaurant",
    ),
    "FIND_PLATE": DataExtractionCaseConfig(
        answer_keys=("names_of_menu_items", "menu", "name"),
        identifier_keys=("name", "cuisine", "area"),
        answer_label="plate",
        entity_label="restaurant",
    ),
    "FIND_CUISINE": DataExtractionCaseConfig(
        answer_keys=("cuisine",),
        identifier_keys=("name", "area", "rating"),
        answer_label="cuisine",
        entity_label="restaurant",
    ),
}


async def _load_rows_for_use_case(*, seed: int, use_case_name: str) -> list[dict]:
    return await fetch_data(seed_value=int(seed), count=80)


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
            project_id="autodining",
            task_url=task_url,
            seed=int(seed),
            use_case_name=definition.name,
            row=row,
            config=CASE_CONFIGS[definition.name],
        )
        if task:
            tasks.append(task)

    return tasks
