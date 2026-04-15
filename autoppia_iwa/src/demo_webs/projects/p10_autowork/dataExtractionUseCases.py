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
    DataExtractionUseCaseDefinition(name="FIND_JOB", description="Find a job from job listings."),
    DataExtractionUseCaseDefinition(name="FIND_EXPERT", description="Find an expert profile from listings."),
    DataExtractionUseCaseDefinition(name="FIND_PRICING", description="Find pricing information from expert profiles."),
    DataExtractionUseCaseDefinition(name="FIND_RATING", description="Find rating information from expert profiles."),
    DataExtractionUseCaseDefinition(name="FIND_HIRE", description="Find who should be hired based on profile details."),
]

CASE_CONFIGS: dict[str, DataExtractionCaseConfig] = {
    "FIND_JOB": DataExtractionCaseConfig(
        answer_keys=("title", "job_title", "name"),
        identifier_keys=("scope", "budget_type", "rate_from", "rate_to", "description"),
        answer_label="job",
        entity_label="job listing",
    ),
    "FIND_EXPERT": DataExtractionCaseConfig(
        answer_keys=("name", "expert_name"),
        identifier_keys=("role", "country", "rating", "jobs", "total_jobs"),
        answer_label="expert",
        entity_label="expert profile",
    ),
    "FIND_PRICING": DataExtractionCaseConfig(
        answer_keys=("rate", "consultation", "lastReviewPrice", "stats", "total_earning", "rate_from", "rate_to", "pricing"),
        identifier_keys=("name", "role", "country", "rating"),
        answer_label="pricing",
        entity_label="expert profile",
    ),
    "FIND_RATING": DataExtractionCaseConfig(
        answer_keys=("rating",),
        identifier_keys=("name", "role", "country", "total_earning"),
        answer_label="rating",
        entity_label="expert profile",
    ),
    "FIND_HIRE": DataExtractionCaseConfig(
        answer_keys=("name", "expert_name"),
        identifier_keys=("role", "country", "rating", "jobs"),
        answer_label="expert to hire",
        entity_label="expert profile",
    ),
}


async def _load_rows_for_use_case(*, seed: int, use_case_name: str) -> list[dict]:
    if use_case_name == "FIND_JOB":
        jobs = await fetch_data(entity_type="jobs", method="select", seed_value=int(seed), count=80)
        if jobs:
            return jobs
    return await fetch_data(entity_type="experts", method="select", seed_value=int(seed), count=80)


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
            project_id="autowork",
            task_url=task_url,
            seed=int(seed),
            use_case_name=definition.name,
            row=row,
            config=CASE_CONFIGS[definition.name],
        )
        if task:
            tasks.append(task)

    return tasks
