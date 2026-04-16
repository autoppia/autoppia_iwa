import importlib
import inspect
from collections.abc import Callable

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url

from .prompts import (
    DATA_EXTRACTION_TASK_GENERATION_PROMPT_VERIFY_FIELD_ONLY,
    DATA_EXTRACTION_TASK_GENERATION_PROMPT_WITH_QUESTION_FIELDS,
)


def build_data_extraction_generation_prompt(use_case: UseCase) -> str | None:
    """Build the LLM prompt for data-extraction task generation."""
    qfav = getattr(use_case, "question_fields_and_values", None)
    constraints_list = use_case.constraints or []
    if not constraints_list:
        return None

    if qfav and isinstance(qfav, dict) and qfav:
        question_fields_info = "\n".join(f"- {k} = {v}" for k, v in qfav.items())
        verify_field = constraints_list[0].get("field") if len(constraints_list) == 1 else None
        if verify_field is not None and not isinstance(verify_field, str):
            verify_field = getattr(verify_field, "value", str(verify_field))
        verify_field = verify_field or "the requested field"
        return DATA_EXTRACTION_TASK_GENERATION_PROMPT_WITH_QUESTION_FIELDS.format(
            use_case_name=use_case.name,
            use_case_description=use_case.description,
            additional_prompt_info=use_case.additional_prompt_info or "",
            question_fields_info=question_fields_info,
            verify_field=verify_field,
        )

    verify_field = constraints_list[0].get("field")
    if verify_field is not None and not isinstance(verify_field, str):
        verify_field = getattr(verify_field, "value", str(verify_field))
    verify_field = verify_field or "the requested field"
    return DATA_EXTRACTION_TASK_GENERATION_PROMPT_VERIFY_FIELD_ONLY.format(
        use_case_name=use_case.name,
        use_case_description=use_case.description,
        additional_prompt_info=use_case.additional_prompt_info or "",
        verify_field=verify_field,
    )


async def generate_tasks_from_project_data_extraction_use_cases(
    *,
    web_project: WebProject,
    prompts_per_use_case: int,
    dynamic: bool,
    data_extraction_use_cases: list[str] | None,
    get_project_module_name: Callable[[], str | None],
    build_task_url_with_seed: Callable[[bool], str],
) -> list[Task] | None:
    """Generate DE tasks from the optional project-level `dataExtractionUseCases.py` module."""
    project_module_name = get_project_module_name()
    if not project_module_name:
        return None

    module_path = f"autoppia_iwa.src.demo_webs.projects.{project_module_name}.dataExtractionUseCases"
    try:
        de_module = importlib.import_module(module_path)
    except ImportError:
        return None

    generate_fn = getattr(de_module, "generate_de_tasks", None)
    if not callable(generate_fn):
        return None

    selected_use_cases = {name.strip().upper() for name in data_extraction_use_cases or [] if str(name).strip()}
    selected_use_cases = selected_use_cases or None

    iterations = int(prompts_per_use_case) if prompts_per_use_case and int(prompts_per_use_case) > 0 else 1
    tasks: list[Task] = []
    for _ in range(iterations):
        task_url = build_task_url_with_seed(dynamic)
        seed = get_seed_from_url(task_url) if dynamic else 1
        generated = generate_fn(
            seed=seed,
            task_url=task_url,
            selected_use_cases=selected_use_cases,
        )
        de_tasks = await generated if inspect.isawaitable(generated) else generated
        if isinstance(de_tasks, list):
            tasks.extend([task for task in de_tasks if isinstance(task, Task)])

    return tasks
