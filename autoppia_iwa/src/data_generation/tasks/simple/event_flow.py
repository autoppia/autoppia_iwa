from autoppia_iwa.src.demo_webs.classes import UseCase

from .prompts import GLOBAL_TASK_GENERATION_PROMPT


def build_event_generation_prompt(use_case: UseCase, constraints_info: str) -> str:
    """Build the LLM prompt for regular event-based task generation."""
    return GLOBAL_TASK_GENERATION_PROMPT.format(
        use_case_name=use_case.name,
        use_case_description=use_case.description,
        additional_prompt_info=use_case.additional_prompt_info,
        constraints_info=constraints_info,
    )
