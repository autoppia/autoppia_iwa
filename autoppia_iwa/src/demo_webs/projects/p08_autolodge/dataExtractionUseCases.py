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
    DataExtractionUseCaseDefinition(name="FIND_HOTEL", description="Find a hotel name from listing details."),
    DataExtractionUseCaseDefinition(name="FIND_RATING", description="Find the rating of a selected hotel."),
    DataExtractionUseCaseDefinition(name="FIND_PRICING", description="Find the pricing value of a selected hotel."),
    DataExtractionUseCaseDefinition(name="FIND_REVIEWS", description="Find reviews count information for a selected hotel."),
]

CASE_CONFIGS: dict[str, DataExtractionCaseConfig] = {
    "FIND_HOTEL": DataExtractionCaseConfig(
        answer_keys=("title", "name"),
        identifier_keys=("location", "region", "rating", "price"),
        answer_label="hotel name",
        entity_label="hotel",
    ),
    "FIND_RATING": DataExtractionCaseConfig(
        answer_keys=("rating",),
        identifier_keys=("title", "name", "location", "price"),
        answer_label="rating",
        entity_label="hotel",
    ),
    "FIND_PRICING": DataExtractionCaseConfig(
        answer_keys=("price", "priceSubtotal", "pricing"),
        identifier_keys=("title", "name", "location", "rating"),
        answer_label="pricing",
        entity_label="hotel",
    ),
    "FIND_REVIEWS": DataExtractionCaseConfig(
        answer_keys=("reviews", "review_count"),
        identifier_keys=("title", "name", "location", "rating"),
        answer_label="reviews",
        entity_label="hotel",
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
            project_id="autolodge",
            task_url=task_url,
            seed=int(seed),
            use_case_name=definition.name,
            row=row,
            config=CASE_CONFIGS[definition.name],
        )
        if task:
            tasks.append(task)

    return tasks
