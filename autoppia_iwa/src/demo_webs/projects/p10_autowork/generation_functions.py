import asyncio
import contextlib
import random
import re
from datetime import date, datetime, time
from random import choice
from typing import Any

from loguru import logger

from ...criterion_helper import ComparisonOperator
from ...shared_utils import (
    constraint_value_for_datetime_date,
    constraint_value_for_numeric,
    constraint_value_for_time,
    create_constraint_dict,
    pick_different_value_from_dataset,
    random_str_not_contained_in,
)
from .data import (
    FIELD_OPERATORS_CONTACT_FORM_SUBMITTED_MAP,
    FIELD_OPERATORS_CONTACT_PAGE_VIEWED_MAP,
    FIELD_OPERATORS_MAP_ADD_SKILL,
    FIELD_OPERATORS_MAP_BROWSE_FAVORITE_EXPERT,
    FIELD_OPERATORS_MAP_BUDGET_TYPE,
    FIELD_OPERATORS_MAP_CANCEL_HIRE,
    FIELD_OPERATORS_MAP_CLOSE_JOB_POSTING,
    FIELD_OPERATORS_MAP_CONTACT_EXPERT_MESSAGE_SENT,
    FIELD_OPERATORS_MAP_EDIT_PROFILE_FIELD,
    FIELD_OPERATORS_MAP_FAVORITE_EXPERT,
    FIELD_OPERATORS_MAP_HIRE_BUTTON,
    FIELD_OPERATORS_MAP_HIRING_CONSULTANT,
    FIELD_OPERATORS_MAP_HIRING_TEAM,
    FIELD_OPERATORS_MAP_JOB_DESCRIPTION,
    FIELD_OPERATORS_MAP_POSTING_A_JOB,
    FIELD_OPERATORS_MAP_PROJECT_SIZE,
    FIELD_OPERATORS_MAP_RATE_RANGE,
    FIELD_OPERATORS_MAP_SEARCH_SKILL,
    FIELD_OPERATORS_MAP_SUBMIT_JOB,
    FIELD_OPERATORS_MAP_TIMELINE,
    FIELD_OPERATORS_MAP_WRITING_A_JOB_TITLE,
    FIELD_OPERATORS_USER_BOOK_CONSULTANT_MAP,
    POPULAR_SKILLS,
)

# Constants for duplicated literals
JOB_TITLES = [
    "Web Developers Jobs",
    "AI/ML Engineers Jobs",
    "Front End Developers Jobs",
    "Backend Developers Jobs",
    "Laravel Developers Jobs",
    "DevOps Jobs",
    "Product Managers Jobs",
    "Project Managers Jobs",
    "Data Scientists Jobs",
    "Mobile App Developers Jobs",
    "UI/UX Designers Jobs",
    "Blockchain Developers Jobs",
    "Cloud Engineers Jobs",
    "Cybersecurity Analysts Jobs",
    "Game Developers Jobs",
    "Database Administrators Jobs",
    "Software Testers Jobs",
    "Embedded Systems Engineers Jobs",
]

JOB_DESCRIPTIONS = [
    "Design, develop, and maintain both client and server applications using modern frameworks.",
    "Analyze datasets to extract insights, build predictive models, and optimize decision-making.",
    "Create intuitive user interfaces and improve user experience through design prototypes.",
    "Automate CI/CD pipelines, monitor infrastructure, and ensure system scalability.",
    "Implement security measures to protect systems from cyber threats and data breaches.",
    "Manage product lifecycle from ideation to launch, coordinating with cross-functional teams.",
    "Develop mobile applications for iOS and Android with optimized performance.",
    "Design scalable and secure cloud solutions for enterprise and startup needs.",
    "Build and deploy machine learning models for real-world production environments.",
    "Write clear documentation, tutorials, and guides for technical and non-technical audiences.",
]

BUDGET_TYPES = ["hourly", "fixed"]
SCOPE_OPTIONS = ["Small", "Medium", "Large"]
DURATION_OPTIONS = ["3 to 6 months", "More than 6 months"]


def _build_data_extraction_result(
    selected_item: dict[str, Any],
    visible_fields: list[str],
    *,
    verify_field: str | None = None,
    question_fields_override: list[str] | None = None,
) -> dict[str, Any] | None:
    """Build constraints + question_fields_and_values for data_extraction_only; returns None on validation failure."""
    available_fields = [f for f in visible_fields if selected_item.get(f) is not None]
    if len(available_fields) < 2:
        return None

    question_fields: list[str]
    chosen_verify_field: str

    if question_fields_override:
        question_fields = [f for f in question_fields_override if f in available_fields and selected_item.get(f) is not None]
        if question_fields:
            remaining = [f for f in available_fields if f not in question_fields]
            if not remaining:
                return None
            chosen_verify_field = verify_field if verify_field is not None and verify_field in remaining else random.choice(remaining)
            # chosen_verify_field = "company"
            remaining_for_extra = [f for f in available_fields if f != chosen_verify_field and f not in question_fields]
            if len(remaining_for_extra) >= 2:
                num_extra = random.randint(1, len(remaining_for_extra))
                question_fields = question_fields + random.sample(remaining_for_extra, num_extra)
        else:
            question_fields = []
            chosen_verify_field = verify_field if verify_field is not None else random.choice(available_fields)
    else:
        chosen_verify_field = verify_field if verify_field is not None else random.choice(available_fields)
        question_fields = []

    if chosen_verify_field not in available_fields:
        return None
    verify_value = selected_item.get(chosen_verify_field)
    if verify_value is None:
        return None

    if question_fields:
        question_candidates = question_fields
    else:
        question_candidates = [f for f in available_fields if f != chosen_verify_field]
        if not question_candidates:
            return None
        num_question_fields = 1 if len(question_candidates) == 1 else 2
        question_candidates = random.sample(question_candidates, num_question_fields)

    question_fields_and_values: dict[str, Any] = {}
    for qf in question_candidates:
        val = selected_item.get(qf)
        if val is not None:
            question_fields_and_values[qf] = val
    if not question_fields_and_values:
        return None

    constraints = [create_constraint_dict(chosen_verify_field, ComparisonOperator.EQUALS, verify_value)]
    return {
        "constraints": constraints,
        "question_fields_and_values": question_fields_and_values,
    }


def _collect_field_values_from_dataset(dataset: list[dict[str, Any]], field: str) -> list[Any]:
    """Return unique non-None values for field across dataset rows."""
    return list({v.get(field) for v in dataset if field in v and v.get(field) is not None})


async def _get_experts_data(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None,
) -> list[dict[str, Any]]:
    """Fetch experts and return as list[dict]; empty list if wrong type or missing."""
    experts_data = await _ensure_dataset(task_url, dataset, entity_type="experts")
    if not isinstance(experts_data, list) or (experts_data and not isinstance(experts_data[0], dict)):
        return []
    return experts_data


async def _get_skills_list(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None,
) -> list[str]:
    """Fetch skills and return as list[str]; fallback to POPULAR_SKILLS if wrong format."""
    skills_list = await _ensure_dataset(task_url, dataset, entity_type="skills")
    if not isinstance(skills_list, list) or (skills_list and not isinstance(skills_list[0], str)):
        return list(POPULAR_SKILLS)
    return skills_list


def _list_to_field_dataset(items: list[Any], field_key: str) -> list[dict[str, Any]]:
    """Build list of single-key dicts for constraint dataset: [{"field_key": x} for x in items]."""
    return [{field_key: x} for x in items]


def _generate_single_field_constraint(
    field_name: str,
    options_list: list[Any],
    operators_map: dict[str, list],
    dataset_key: str | None = None,
) -> list[dict[str, Any]]:
    """Generate one constraint for a field with value from options_list."""
    dataset_key = dataset_key or field_name
    allowed_ops = operators_map.get(field_name)
    if not allowed_ops:
        return []
    op = ComparisonOperator(random.choice(allowed_ops))
    field_value = random.choice(options_list)
    dataset = _list_to_field_dataset(options_list, dataset_key)
    value = _generate_constraint_value(op, field_value, field_name, dataset)
    if value is None:
        return []
    return [create_constraint_dict(field_name, op, value)]


def _generate_edit_profile_value_constraint(options_list: list[Any]) -> list[dict[str, Any]]:
    """Generate one constraint for edit profile 'value' field from options_list."""
    return _generate_single_field_constraint("value", options_list, FIELD_OPERATORS_MAP_EDIT_PROFILE_FIELD, dataset_key="value")


async def _ensure_dataset(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None,
    *,
    entity_type: str,
) -> list[dict[str, Any]] | list[str]:
    """
    Extract entity data from the cache dataset, or fetch from server if not available.

    Args:
        task_url: URL to extract seed from
        dataset: Pre-loaded dataset dictionary (deprecated, kept for backward compatibility)
        entity_type: Type of entity to fetch ("experts" or "skills")

    Returns:
        For "experts": list[dict[str, Any]] of expert data
        For "skills": list[str] of skill names
    """
    _ = dataset  # Unused parameter kept for backward compatibility
    from autoppia_iwa.src.demo_webs.data_provider import get_seed_from_url

    from .data_utils import fetch_data

    seed = get_seed_from_url(task_url)
    fetched_data = await fetch_data(entity_type=entity_type, seed_value=seed)

    if not fetched_data:
        return []

    # For skills, convert to list of strings
    if entity_type == "skills":
        if isinstance(fetched_data[0], str):
            return fetched_data
        if isinstance(fetched_data[0], dict):
            # Extract "name" field from each dict
            return [skill.get("name") or str(skill) for skill in fetched_data if skill]
        return []

    # For experts, return list[dict]
    return fetched_data


def _generate_constraint_value(
    operator: ComparisonOperator,
    field_value: Any,
    field: str,
    dataset: list[dict[str, Any]],
) -> Any:
    """
    Generate a constraint value for a given operator, field, and dataset.
    Handles various data types and operators robustly.
    """
    if isinstance(field_value, datetime | date):
        return constraint_value_for_datetime_date(operator, field_value)

    if isinstance(field_value, time):
        return constraint_value_for_time(operator, field_value, field, dataset)

    if operator == ComparisonOperator.EQUALS:
        return field_value

    if operator == ComparisonOperator.NOT_EQUALS:
        return pick_different_value_from_dataset(dataset, field, field_value, None)

    if operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        if len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            subpart = field_value[start:end]
            return subpart.strip()
        return field_value

    if operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        return random_str_not_contained_in(field_value)

    if operator == ComparisonOperator.IN_LIST:
        all_values = _collect_field_values_from_dataset(dataset, field)
        if not all_values:
            return [field_value]
        random.shuffle(all_values)
        subset = random.sample(all_values, min(2, len(all_values)))
        if field_value not in subset:
            subset.append(field_value)
        return list(set(subset))

    if operator == ComparisonOperator.NOT_IN_LIST:
        all_values = _collect_field_values_from_dataset(dataset, field)
        if field_value in all_values:
            with contextlib.suppress(ValueError):
                all_values.remove(field_value)
        return random.sample(all_values, min(2, len(all_values))) if all_values else []

    if operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    } and isinstance(field_value, int | float):
        return constraint_value_for_numeric(operator, field_value, round_digits=2)

    return None


def _generate_constraints(
    dataset: list[dict], field_operators: dict, field_map: dict | None = None, min_constraints: int | None = 1, num_constraints: int | None = None, selected_fields: list | None = None
) -> list[dict[str, Any]]:
    """
    Generates constraints based on the dataset and field operator mapping.
    """
    all_constraints = []
    if not dataset:
        logger.error("No dataset provided")
        return all_constraints
    sample_data = choice(dataset)
    possible_fields = list(field_operators.keys())
    if selected_fields:
        possible_fields = [f for f in possible_fields if f not in selected_fields]
    else:
        selected_fields = []

    if num_constraints is None:
        num_constraints = random.randint(min_constraints, len(possible_fields))

    selected_fields.extend(random.sample(possible_fields, num_constraints))

    if field_map is None:
        field_map = {}

    for field in selected_fields:
        allowed_ops = field_operators.get(field, [])
        if not allowed_ops:
            continue

        op = ComparisonOperator(choice(allowed_ops))
        new_field = field_map.get(field, field)

        field_value = None
        constraint_value = None
        if isinstance(new_field, list):
            random.shuffle(new_field)
            for f in new_field:
                field_value = sample_data.get(f)
                new_field = f
                break
        elif isinstance(new_field, str):
            field_value = sample_data.get(new_field)
        elif isinstance(new_field, dict):
            custom_dataset = new_field.get("dataset", [])
            new_field = new_field.get("field", "")
            field_value = choice(custom_dataset).get(new_field)
            if new_field:
                constraint_value = _generate_constraint_value(op, field_value, new_field, dataset=custom_dataset)

        if field_value is None:
            continue

        if constraint_value is None:
            # Generate a constraint value based on the operator and field value
            constraint_value = _generate_constraint_value(op, field_value, new_field, dataset)

        if constraint_value is not None:
            constraint = create_constraint_dict(field, op, constraint_value)
            all_constraints.append(constraint)

    return all_constraints


async def generate_book_consultant_constraint(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    experts_data = await _get_experts_data(task_url, dataset)
    if test_types == "data_extraction_only":
        if not experts_data:
            return []
        selected = random.choice(experts_data)
        selected_item = {
            "name": selected.get("name"),
            "country": selected.get("country"),
            "role": selected.get("role"),
            "rating": selected.get("rating"),
            "consultation_fee": selected.get("consultation"),
        }
        visible_fields = ["name", "country", "role", "rating", "consultation_fee"]
        return (
            _build_data_extraction_result(
                selected_item,
                visible_fields,
                question_fields_override=["name"],
            )
            or []
        )

    field_operators = FIELD_OPERATORS_USER_BOOK_CONSULTANT_MAP
    selected_field = ["slug"]
    constraints_list = _generate_constraints(experts_data, field_operators, min_constraints=2, selected_fields=selected_field)

    return constraints_list


async def generate_hire_button_clicked_constraint(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    experts_data = await _get_experts_data(task_url, dataset)
    if test_types == "data_extraction_only":
        if not experts_data:
            return []
        selected = random.choice(experts_data)
        selected_item = {
            "name": selected.get("name"),
            "country": selected.get("country"),
            "role": selected.get("role"),
            "rating": selected.get("rating"),
            "jobs_completed": selected.get("jobs"),
            "total_earning": selected.get("stats").get("earnings"),
            "total_hours": selected.get("stats").get("hours"),
        }
        visible_fields = ["name", "country", "role", "rating", "jobs_completed", "total_earning", "total_hours"]
        return _build_data_extraction_result(selected_item, visible_fields, question_fields_override=["name"]) or []

    field_operators = FIELD_OPERATORS_MAP_HIRE_BUTTON
    selected_field = []
    constraints_list = _generate_constraints(experts_data, field_operators, min_constraints=2, selected_fields=selected_field)

    return constraints_list


async def generate_content_expert_message_sent_constraint(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None) -> list[dict[str, Any]]:
    constraint = await generate_hire_button_clicked_constraint(task_url, dataset)
    messages = [
        "Hi, I'd like to connect with you.",
        "Hello! I need your expert guidance.",
        "Hi, could you help me with this?",
        "Hello, I'd appreciate your advice.",
        "Hi, can we discuss this briefly?",
        "Hello! I have a quick question.",
        "Hi, I'm seeking your expertise.",
        "Hello, I'd value your insight.",
        "Hi, may I get your opinion?",
        "Hello! I'd love your guidance.",
        "Hi, can I consult you on this?",
        "Hello, I need expert input.",
        "Hi, I'm reaching out for advice.",
        "Hello! Could we connect?",
        "Hi, I'd like to ask something.",
        "Hello, I need your help.",
        "Hi, can you guide me?",
        "Hello! Quick help needed.",
        "Hi, seeking expert advice.",
        "Hello, can we connect briefly?",
    ]
    field = "message"
    allowed_ops = FIELD_OPERATORS_MAP_CONTACT_EXPERT_MESSAGE_SENT[field]
    op = ComparisonOperator(random.choice(allowed_ops))
    field_value = random.choice(messages)
    messages_dataset = [{"message": m} for m in messages]
    value = _generate_constraint_value(op, field_value, field, dataset=messages_dataset)
    if value is not None:
        constraint.append(create_constraint_dict(field, op, value))
    return constraint


async def generate_select_hiring_team_constraint(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None) -> list[dict[str, Any]]:
    field_mapping = {
        "team": {"field": "team", "dataset": _list_to_field_dataset(["Microsoft", "Apple", "Google"], "team")},
    }
    experts_data = await _get_experts_data(task_url, dataset)
    field_operators = FIELD_OPERATORS_MAP_HIRING_TEAM
    selected_fields = []
    constraints_list = _generate_constraints(experts_data, field_operators, min_constraints=2, selected_fields=selected_fields, field_map=field_mapping)

    return constraints_list


async def generate_hire_consultation_constraint(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    experts_data = await _get_experts_data(task_url, dataset)
    if test_types == "data_extraction_only":
        return await generate_hire_button_clicked_constraint(task_url, dataset, test_types=test_types)
    field_mapping = {
        "increaseHowMuch": {"field": "increaseHowMuch", "dataset": _list_to_field_dataset(["5%", "10%", "15%"], "increaseHowMuch")},
        "increaseWhen": {"field": "increaseWhen", "dataset": _list_to_field_dataset(["Never", "After 3 months", "After 6 months", "After 12 months"], "increaseWhen")},
        "paymentType": {"field": "paymentType", "dataset": _list_to_field_dataset(["fixed", "hourly"], "paymentType")},
    }
    field_operators = FIELD_OPERATORS_MAP_HIRING_CONSULTANT
    selected_fields = []
    constraints_list = _generate_constraints(experts_data, field_operators, min_constraints=2, field_map=field_mapping, selected_fields=selected_fields)

    return constraints_list


async def generate_quick_hire_constraint(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        return await generate_hire_button_clicked_constraint(task_url, dataset, test_types=test_types)
    return await generate_book_consultant_constraint(task_url, dataset, test_types=test_types)


async def generate_cancel_hire_constraint(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None) -> list[dict[str, Any]]:
    experts_data = await _get_experts_data(task_url, dataset)
    field_operators = FIELD_OPERATORS_MAP_CANCEL_HIRE
    fixed_fields = ["slug"]
    constraints_list = _generate_constraints(experts_data, field_operators, min_constraints=2, selected_fields=fixed_fields)

    return constraints_list


async def _generate_job_posting_constraint_async(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        jobs_data = await _ensure_dataset(task_url, dataset, entity_type="jobs")
        if not isinstance(jobs_data, list) or not jobs_data:
            return []
        jobs_completed = sum(1 for job in jobs_data if isinstance(job, dict) and job.get("status") == "Completed")
        jobs_in_progress = sum(1 for job in jobs_data if isinstance(job, dict) and job.get("status") == "In progress")
        selected = random.choice(jobs_data)
        if not isinstance(selected, dict):
            return []
        raw_time = selected.get("time") or ""
        raw_activity = selected.get("activity") or ""
        # Prefer parsing from "time", fallback to "activity"
        logged_time_match = re.search(r"(\d+:\d+\s*hrs)", raw_time) or re.search(r"(\d+:\d+\s*hrs)", raw_activity)
        logged_price_match = re.search(r"\((\$[\d,]+)\)", raw_time) or re.search(r"\((\$[\d,]+)\)", raw_activity)
        logged_time = logged_time_match.group(1) if logged_time_match else None
        logged_time_price = logged_price_match.group(1) if logged_price_match else None
        selected_item = {
            "title": selected.get("title"),
            "status": selected.get("status"),
            "start": selected.get("start"),
            "logged_time": logged_time,
            "logged_time_price": logged_time_price,
        }
        visible_fields = ["title", "status", "start", "logged_time", "logged_time_price"]
        available_fields = [f for f in visible_fields if selected_item.get(f) is not None]
        if len(available_fields) < 2:
            return []

        special_verify_values = {
            "jobs_completed": jobs_completed,
            "jobs_in_progress": jobs_in_progress,
        }
        verify_candidates = available_fields + list(special_verify_values.keys())
        chosen_verify_field = random.choice(verify_candidates)
        question_fields_override = ["title", "logged_time"] if chosen_verify_field == "logged_time_price" else ["title"]

        if chosen_verify_field in special_verify_values:
            return {"constraints": [create_constraint_dict(chosen_verify_field, ComparisonOperator.EQUALS, special_verify_values[chosen_verify_field])]}

        return (
            _build_data_extraction_result(
                selected_item,
                visible_fields,
                verify_field=chosen_verify_field,
                question_fields_override=question_fields_override,
            )
            or []
        )

    constraints_list = []
    possible_field = list(FIELD_OPERATORS_MAP_POSTING_A_JOB.keys())
    num_constraints = random.randint(1, len(possible_field))
    selected_fields = random.sample(possible_field, num_constraints)
    page = ["home"]
    source = ["button"]

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_POSTING_A_JOB.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)
        if field == "page":
            field_value = random.choice(page)
            page_dataset = [{"page": p} for p in page]
            value = _generate_constraint_value(operator, field_value, field, dataset=page_dataset)

        else:
            field_value = random.choice(source)
            source_dataset = [{"source": s} for s in source]
            value = _generate_constraint_value(operator, field_value, field, dataset=source_dataset)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


def generate_job_posting_constraint(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    coro = _generate_job_posting_constraint_async(task_url=task_url, dataset=dataset, test_types=test_types)
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    return coro


def generate_write_job_title_constraint() -> list[dict[str, Any]]:
    constraints_list = []
    possible_fields = ["query"]

    for field in possible_fields:
        allowed_ops = FIELD_OPERATORS_MAP_WRITING_A_JOB_TITLE.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)
        if field == "query":
            field_value = random.choice(JOB_TITLES)
            query_dataset = [{"query": q} for q in JOB_TITLES]
            value = _generate_constraint_value(operator, field_value, field, dataset=query_dataset)

            if value is not None:
                constraint = create_constraint_dict(field, operator, value)
                constraints_list.append(constraint)

    return constraints_list


async def generate_search_skill_constraint(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None) -> list[dict[str, Any]]:
    constraints_list = []
    possible_field = ["skill"]

    skills_list = await _get_skills_list(task_url, dataset)
    popular_skill_data = _list_to_field_dataset(skills_list, "skill")
    sample_skill = random.choice(popular_skill_data) if popular_skill_data else None
    if sample_skill is None:
        return constraints_list
    for field in possible_field:
        allowed_ops = FIELD_OPERATORS_MAP_SEARCH_SKILL.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)
        field_value = sample_skill.get(field)
        value = _generate_constraint_value(operator, field_value, field, dataset=popular_skill_data)
        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)
    return constraints_list


async def generate_add_skill_constraint(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None) -> list[dict[str, Any]]:
    constraints_list = []
    possible_field = list(FIELD_OPERATORS_MAP_ADD_SKILL.keys())
    num_constraints = random.randint(1, len(possible_field))
    selected_field = random.sample(possible_field, num_constraints)

    skills_list = await _get_skills_list(task_url, dataset)
    popular_skills_data = _list_to_field_dataset(skills_list, "skill")
    sample_skill = random.choice(popular_skills_data) if popular_skills_data else None
    if sample_skill is None:
        return constraints_list
    for field in selected_field:
        allowed_ops = FIELD_OPERATORS_MAP_ADD_SKILL.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)
        field_value = sample_skill.get(field, None)
        value = _generate_constraint_value(operator, field_value, field, dataset=popular_skills_data)
        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


async def generate_submit_job_constraint(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None) -> list[dict[str, Any]]:
    constraints_list = []
    possible_fields = list(FIELD_OPERATORS_MAP_SUBMIT_JOB.keys())
    num_constraints = random.randint(2, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    skills_list = await _get_skills_list(task_url, dataset)
    popular_skill_data = _list_to_field_dataset(skills_list, "skills")
    sample_skills = random.choice(popular_skill_data) if popular_skill_data else None
    if sample_skills is None:
        return constraints_list
    rate_constraints = []
    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_SUBMIT_JOB.get(field, [])
        if not allowed_ops:
            continue
        operator = ComparisonOperator(random.choice(allowed_ops))
        value = _value_for_job_form_field(
            field,
            operator,
            sample_skills,
            popular_skill_data,
            rate_constraints,
            constraints_list,
        )
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


def generate_budget_type_constraint() -> list[dict[str, Any]]:
    return _generate_single_field_constraint("budget_type", BUDGET_TYPES, FIELD_OPERATORS_MAP_BUDGET_TYPE)


def generate_project_size_constraint() -> list[dict[str, Any]]:
    return _generate_single_field_constraint("scope", SCOPE_OPTIONS, FIELD_OPERATORS_MAP_PROJECT_SIZE)


def generate_timeline_constraint() -> list[dict[str, Any]]:
    return _generate_single_field_constraint("duration", DURATION_OPTIONS, FIELD_OPERATORS_MAP_TIMELINE)


def generate_rate_range_constraint() -> list[dict[str, Any]]:
    constraints: list[dict[str, Any]] = []
    from_ops = FIELD_OPERATORS_MAP_RATE_RANGE["rate_from"]
    to_ops = FIELD_OPERATORS_MAP_RATE_RANGE["rate_to"]
    rate_constraints = generate_to_and_from_constraints(from_ops, to_ops)
    constraints.extend(rate_constraints)
    return constraints


def generate_write_job_description_constraint() -> list[dict[str, Any]]:
    return _generate_single_field_constraint("description", JOB_DESCRIPTIONS, FIELD_OPERATORS_MAP_JOB_DESCRIPTION)


def _value_for_job_form_field(
    field: str,
    operator: ComparisonOperator,
    sample_skills: dict[str, Any],
    popular_skill_data: list[dict[str, Any]],
    rate_constraints: list[dict[str, Any]],
    constraints_list: list[dict[str, Any]],
) -> Any:
    """Return constraint value for one job form field; may extend constraints_list with rate_constraints."""
    if field == "budgetType":
        return _generate_constraint_value(
            operator,
            random.choice(BUDGET_TYPES),
            field,
            dataset=_list_to_field_dataset(BUDGET_TYPES, "budgetType"),
        )
    if field == "description":
        return _generate_constraint_value(
            operator,
            random.choice(JOB_DESCRIPTIONS),
            field,
            dataset=_list_to_field_dataset(JOB_DESCRIPTIONS, "description"),
        )
    if field == "duration":
        return _generate_constraint_value(
            operator,
            random.choice(DURATION_OPTIONS),
            field,
            dataset=_list_to_field_dataset(DURATION_OPTIONS, "duration"),
        )
    if field in ["rate_from", "rate_to"]:
        if not rate_constraints:
            from_ops = FIELD_OPERATORS_MAP_SUBMIT_JOB["rate_from"]
            to_ops = FIELD_OPERATORS_MAP_SUBMIT_JOB["rate_to"]
            rate_constraints.extend(generate_to_and_from_constraints(from_ops, to_ops))
            constraints_list.extend(rate_constraints)
        return None
    if field == "scope":
        return _generate_constraint_value(
            operator,
            random.choice(SCOPE_OPTIONS),
            field,
            dataset=_list_to_field_dataset(SCOPE_OPTIONS, "scope"),
        )
    if field == "skills":
        return _generate_constraint_value(operator, sample_skills.get(field), field, dataset=popular_skill_data)
    return _generate_constraint_value(
        operator,
        random.choice(JOB_TITLES),
        field,
        dataset=_list_to_field_dataset(JOB_TITLES, "title"),
    )


async def generate_close_posting_job_constraint(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None) -> list[dict[str, Any]]:
    constraints_list = []
    possible_field = list(FIELD_OPERATORS_MAP_SUBMIT_JOB.keys())
    num_constraints = random.randint(2, len(possible_field))
    selected_field = random.sample(possible_field, num_constraints)

    skills_list = await _get_skills_list(task_url, dataset)
    popular_skill_data = _list_to_field_dataset(skills_list, "skills")
    sample_skills = random.choice(popular_skill_data) if popular_skill_data else None
    if sample_skills is None:
        return constraints_list
    rate_constraints = []
    for field in selected_field:
        allowed_ops = FIELD_OPERATORS_MAP_CLOSE_JOB_POSTING.get(field, [])
        if not allowed_ops:
            continue
        operator = ComparisonOperator(random.choice(allowed_ops))
        value = _value_for_job_form_field(
            field,
            operator,
            sample_skills,
            popular_skill_data,
            rate_constraints,
            constraints_list,
        )
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


async def generate_favorite_expert_selected_constraint(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None) -> list[dict[str, Any]]:
    experts_data = await _get_experts_data(task_url, dataset)
    field_map = {"expert_name": "name", "expert_slug": "slug"}
    return _generate_constraints(experts_data, FIELD_OPERATORS_MAP_FAVORITE_EXPERT, field_map=field_map)


async def generate_favorite_expert_removed_constraint(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None) -> list[dict[str, Any]]:
    return await generate_favorite_expert_selected_constraint(task_url, dataset)


def generate_browse_favorite_expert_constraint() -> list[dict[str, Any]]:
    dataset = [{"source": s} for s in ["favorites_empty_state", "favorites_page"]]
    return _generate_constraints(dataset, FIELD_OPERATORS_MAP_BROWSE_FAVORITE_EXPERT)


ABOUT_OPTIONS = [
    "Passionate software developer with 5 years of experience in web and mobile applications.",
    "Data scientist specializing in machine learning, AI, and big data analytics.",
    "Marketing professional with a focus on digital campaigns and brand strategy.",
    "UI/UX designer dedicated to creating intuitive and engaging user experiences.",
    "Project manager experienced in agile methodologies and cross-functional team leadership.",
    "Content writer with a love for storytelling and SEO optimization.",
    "Frontend developer skilled in React, Next.js, and responsive web design.",
    "Backend engineer experienced with Node.js, Python, and database management.",
    "Entrepreneur with experience in startups, product development, and business strategy.",
    "HR professional focused on talent acquisition, employee engagement, and culture building.",
    "Software engineer passionate about cloud computing, DevOps, and automation.",
    "Graphic designer specializing in branding, illustrations, and visual storytelling.",
    "AI researcher exploring NLP, computer vision, and deep learning models.",
    "Finance professional skilled in investment analysis, risk management, and budgeting.",
    "Educator with experience in curriculum development and online learning platforms.",
    "Full-stack developer with expertise in modern web technologies and APIs.",
    "Consultant providing strategic guidance in technology, operations, and management.",
    "Healthcare professional focusing on patient care, medical research, and wellness.",
    "Product manager experienced in market research, roadmap planning, and user insights.",
    "Blockchain developer exploring smart contracts, DeFi, and decentralized applications.",
]


def generate_edit_about_constraint() -> list[dict[str, Any]]:
    return _generate_edit_profile_value_constraint(ABOUT_OPTIONS)


PROFILE_NAME_OPTIONS = [
    "Emily Johnson",
    "Michael Brown",
    "Sarah Williams",
    "Daniel Smith",
    "Jessica Taylor",
    "David Miller",
    "Sophia Anderson",
    "James Wilson",
    "Olivia Martinez",
    "Robert Thompson",
    "Emma Davis",
    "John Harris",
    "Ava Clark",
    "William Lewis",
    "Mia Robinson",
    "Benjamin Walker",
    "Charlotte Young",
    "Lucas Hall",
    "Amelia King",
    "Ethan Wright",
]


def generate_edit_profile_name_constraint(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    _ = task_url, dataset
    if test_types == "data_extraction_only":
        value = "Alex Smith"
        return {"constraints": [create_constraint_dict("name", ComparisonOperator.EQUALS, value)]}
    return _generate_edit_profile_value_constraint(PROFILE_NAME_OPTIONS)


def generate_edit_profile_title_constraint(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    _ = task_url, dataset
    if test_types == "data_extraction_only":
        value = "Project Manager"
        return {"constraints": [create_constraint_dict("title", ComparisonOperator.EQUALS, value)]}
    return _generate_edit_profile_value_constraint(JOB_TITLES)


LOCATION_OPTIONS = [
    "New York, NY, USA",
    "San Francisco, CA, USA",
    "Los Angeles, CA, USA",
    "Chicago, IL, USA",
    "Austin, TX, USA",
    "Seattle, WA, USA",
    "Boston, MA, USA",
    "Denver, CO, USA",
    "Toronto, ON, Canada",
    "Vancouver, BC, Canada",
    "London, UK",
    "Manchester, UK",
    "Berlin, Germany",
    "Munich, Germany",
    "Paris, France",
    "Amsterdam, Netherlands",
    "Stockholm, Sweden",
    "Zurich, Switzerland",
    "Sydney, Australia",
    "Melbourne, Australia",
    "Dubai, UAE",
    "Abu Dhabi, UAE",
    "Singapore",
    "Tokyo, Japan",
    "Seoul, South Korea",
    "Karachi, Pakistan",
    "Lahore, Pakistan",
    "Islamabad, Pakistan",
    "Delhi, India",
    "Bangalore, India",
]


def generate_edit_profile_location_constraint(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    _ = task_url, dataset
    if test_types == "data_extraction_only":
        value = "San Francisco, CA"
        return {"constraints": [create_constraint_dict("location", ComparisonOperator.EQUALS, value)]}
    return _generate_edit_profile_value_constraint(LOCATION_OPTIONS)


PROFILE_EMAIL_OPTIONS = [
    "emily.johnson@example.com",
    "michael.brown@example.com",
    "sarah.williams@example.com",
    "daniel.smith@example.com",
    "jessica.taylor@example.com",
    "david.miller@example.com",
    "sophia.anderson@example.com",
    "james.wilson@example.com",
    "olivia.martinez@example.com",
    "robert.thompson@example.com",
    "emma.davis@example.com",
    "john.harris@example.com",
    "ava.clark@example.com",
    "william.lewis@example.com",
    "mia.robinson@example.com",
    "benjamin.walker@example.com",
    "charlotte.young@example.com",
    "lucas.hall@example.com",
    "amelia.king@example.com",
    "ethan.wright@example.com",
]


def generate_edit_profile_email_constraint(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]] | list[str]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    _ = task_url, dataset
    if test_types == "data_extraction_only":
        value = "alexsmith@autowork.com"
        return {"constraints": [create_constraint_dict("email", ComparisonOperator.EQUALS, value)]}
    return _generate_edit_profile_value_constraint(PROFILE_EMAIL_OPTIONS)


def generate_to_and_from_constraints(from_ops: list[int], to_ops: list[int]) -> Any:
    rate_from = "rate_from"
    rate_from_value = random.randint(10, 50)
    rate_from_op = ComparisonOperator(random.choice(from_ops))

    rate_to = "rate_to"
    rate_to_value = random.randint(rate_from_value + 1, rate_from_value + 51)
    rate_to_op = ComparisonOperator(random.choice(to_ops))
    all_constraints = []
    all_constraints.append(create_constraint_dict(rate_from, rate_from_op, rate_from_value))
    all_constraints.append(create_constraint_dict(rate_to, rate_to_op, rate_to_value))
    return all_constraints


def _contact_form_synthetic_dataset_autowork() -> list[dict[str, str]]:
    """Sample rows for AUTOWORK_CONTACT_FORM_SUBMITTED (web_10 autowork contact form)."""
    return [
        {
            "name": "Alex Morgan",
            "email": "alex@example.com",
            "subject": "Partnership inquiry",
            "message": "I would like to discuss a long-term collaboration on upcoming projects.",
        },
        {
            "name": "Jordan Lee",
            "email": "jordan@work.test",
            "subject": "Hiring question",
            "message": "Can you confirm your availability for a full-time remote role?",
        },
        {
            "name": "Sam Rivera",
            "email": "sam@mail.demo",
            "subject": "Project brief",
            "message": "Please review the attached scope and let me know your hourly rate.",
        },
        {
            "name": "Riley Chen",
            "email": "riley@example.org",
            "subject": "Consultation follow-up",
            "message": "Thank you for the call yesterday; I have a few more questions.",
        },
    ]


async def generate_autowork_contact_page_viewed_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Constraints for AUTOWORK_CONTACT_PAGE_VIEWED (``page`` in payload; web sends ``contact``).
    """
    _ = (task_url, dataset)
    if test_types == "data_extraction_only":
        return []

    field = "page"
    page_value = "contact"
    allowed_ops = FIELD_OPERATORS_CONTACT_PAGE_VIEWED_MAP[field]
    operator = ComparisonOperator(random.choice(allowed_ops))
    page_dataset = [{"page": "contact"}, {"page": "help"}, {"page": "support"}]
    value = _generate_constraint_value(operator, page_value, field, page_dataset)
    return [create_constraint_dict(field, operator, value)]


async def generate_autowork_contact_form_submitted_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Constraints for AUTOWORK_CONTACT_FORM_SUBMITTED (name, email, subject, message).
    """
    _ = (task_url, dataset)
    synth = _contact_form_synthetic_dataset_autowork()
    if test_types == "data_extraction_only":
        picked = random.choice(synth)
        visible = ["name", "email", "subject", "message"]
        verify_field = random.choice(visible)
        return _build_data_extraction_result(picked, visible, verify_field=verify_field) or []

    fields_pool = ["name", "email", "subject", "message"]
    num_fields = random.randint(1, min(3, len(fields_pool)))
    selected = random.sample(fields_pool, num_fields)
    sample_row = random.choice(synth)
    constraints: list[dict[str, Any]] = []
    for field in selected:
        allowed_ops = FIELD_OPERATORS_CONTACT_FORM_SUBMITTED_MAP[field]
        operator = ComparisonOperator(random.choice(allowed_ops))
        raw = sample_row[field]
        value = _generate_constraint_value(operator, raw, field, synth)
        if value is not None:
            constraints.append(create_constraint_dict(field, operator, value))
    return constraints
