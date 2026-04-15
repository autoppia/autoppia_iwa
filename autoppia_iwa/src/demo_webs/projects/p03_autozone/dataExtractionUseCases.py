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
    DataExtractionUseCaseDefinition(name="FIND_PRODUCT", description="Find a product name from its details."),
    DataExtractionUseCaseDefinition(name="FIND_PRICE", description="Find the price of a selected product."),
    DataExtractionUseCaseDefinition(name="FIND_BRAND", description="Find the brand of a selected product."),
    DataExtractionUseCaseDefinition(name="FIND_CATEGORY", description="Find the category of a selected product."),
]

CASE_CONFIGS: dict[str, DataExtractionCaseConfig] = {
    "FIND_PRODUCT": DataExtractionCaseConfig(
        answer_keys=("name", "title"),
        identifier_keys=("brand", "category", "price", "rating"),
        answer_label="product name",
        entity_label="product",
    ),
    "FIND_PRICE": DataExtractionCaseConfig(
        answer_keys=("price",),
        identifier_keys=("name", "title", "brand", "category"),
        answer_label="price",
        entity_label="product",
    ),
    "FIND_BRAND": DataExtractionCaseConfig(
        answer_keys=("brand",),
        identifier_keys=("name", "title", "category", "price"),
        answer_label="brand",
        entity_label="product",
    ),
    "FIND_CATEGORY": DataExtractionCaseConfig(
        answer_keys=("category",),
        identifier_keys=("name", "title", "brand", "price"),
        answer_label="category",
        entity_label="product",
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
            project_id="autozone",
            task_url=task_url,
            seed=int(seed),
            use_case_name=definition.name,
            row=row,
            config=CASE_CONFIGS[definition.name],
        )
        if task:
            tasks.append(task)

    return tasks
