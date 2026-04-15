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

from .data_utils import (
    fetch_data,
    transform_appointments_to_modified,
    transform_doctors_to_modified,
    transform_medical_records_to_modified,
    transform_prescriptions_to_modified,
)

DATA_EXTRACTION_USE_CASES: list[DataExtractionUseCaseDefinition] = [
    DataExtractionUseCaseDefinition(name="FIND_DOCTOR", description="Find a doctor from healthcare data."),
    DataExtractionUseCaseDefinition(name="FIND_APPOITNMENT", description="Find appointment information from healthcare data."),
    DataExtractionUseCaseDefinition(name="FIND_PRESCRIPTION", description="Find prescription information from healthcare data."),
    DataExtractionUseCaseDefinition(name="FIND_ANALYSIS", description="Find medical analysis information from healthcare data."),
    DataExtractionUseCaseDefinition(name="FIND_ESPECIALITY", description="Find doctor speciality information from healthcare data."),
    DataExtractionUseCaseDefinition(name="FIND_RATING", description="Find doctor rating information from healthcare data."),
]

CASE_CONFIGS: dict[str, DataExtractionCaseConfig] = {
    "FIND_DOCTOR": DataExtractionCaseConfig(
        answer_keys=("doctor_name", "name"),
        identifier_keys=("speciality", "rating", "consultation_fee", "primary_language"),
        answer_label="doctor name",
        entity_label="doctor profile",
    ),
    "FIND_APPOITNMENT": DataExtractionCaseConfig(
        answer_keys=("date", "time", "doctor_name"),
        identifier_keys=("doctor_name", "speciality", "patient_name"),
        answer_label="appointment",
        entity_label="appointment",
    ),
    "FIND_PRESCRIPTION": DataExtractionCaseConfig(
        answer_keys=("medicine_name", "doctor_name"),
        identifier_keys=("start_date", "status", "category", "dosage"),
        answer_label="prescription",
        entity_label="prescription",
    ),
    "FIND_ANALYSIS": DataExtractionCaseConfig(
        answer_keys=("record_title", "record_type"),
        identifier_keys=("doctor_name", "record_date"),
        answer_label="analysis",
        entity_label="medical analysis",
    ),
    "FIND_ESPECIALITY": DataExtractionCaseConfig(
        answer_keys=("speciality",),
        identifier_keys=("doctor_name", "rating", "consultation_fee"),
        answer_label="speciality",
        entity_label="doctor profile",
    ),
    "FIND_RATING": DataExtractionCaseConfig(
        answer_keys=("rating",),
        identifier_keys=("doctor_name", "speciality", "consultation_fee"),
        answer_label="rating",
        entity_label="doctor profile",
    ),
}


async def _load_rows_for_use_case(*, seed: int, use_case_name: str) -> list[dict]:
    if use_case_name in {"FIND_DOCTOR", "FIND_ESPECIALITY", "FIND_RATING"}:
        rows = await fetch_data(entity_type="doctors", method="select", filter_key="specialty", seed_value=int(seed), count=80)
        return transform_doctors_to_modified(rows)
    if use_case_name == "FIND_APPOITNMENT":
        rows = await fetch_data(entity_type="appointments", method="select", filter_key="specialty", seed_value=int(seed), count=80)
        return transform_appointments_to_modified(rows)
    if use_case_name == "FIND_PRESCRIPTION":
        rows = await fetch_data(entity_type="prescriptions", method="select", filter_key="category", seed_value=int(seed), count=80)
        return transform_prescriptions_to_modified(rows)
    rows = await fetch_data(entity_type="medical-records", method="select", filter_key="type", seed_value=int(seed), count=80)
    return transform_medical_records_to_modified(rows)


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
            project_id="autohealth",
            task_url=task_url,
            seed=int(seed),
            use_case_name=definition.name,
            row=row,
            config=CASE_CONFIGS[definition.name],
        )
        if task:
            tasks.append(task)

    return tasks
