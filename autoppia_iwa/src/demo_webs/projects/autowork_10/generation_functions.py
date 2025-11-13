import random
from datetime import date, datetime, time, timedelta
from random import choice
from typing import Any

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data

from ..criterion_helper import ComparisonOperator
from ..shared_utils import create_constraint_dict
from .data import (
    EXPERTS_DATA_MODIFIED,
    FIELD_OPERATORS_MAP_ADD_SKILL,
    FIELD_OPERATORS_MAP_CANCEL_HIRE,
    FIELD_OPERATORS_MAP_CLOSE_JOB_POSTING,
    FIELD_OPERATORS_MAP_HIRE_BUTTON,
    FIELD_OPERATORS_MAP_HIRING_CONSULTANT,
    FIELD_OPERATORS_MAP_HIRING_TEAM,
    FIELD_OPERATORS_MAP_POSTING_A_JOB,
    FIELD_OPERATORS_MAP_SEARCH_SKILL,
    FIELD_OPERATORS_MAP_SUBMIT_JOB,
    FIELD_OPERATORS_MAP_WRITING_A_JOB_TITLE,
    FIELD_OPERATORS_USER_BOOK_CONSULTANT_MAP,
    POPULAR_SKILLS,
)
from .main import FRONTEND_PORT_INDEX, work_project

PROJECT_KEY = f"web_{FRONTEND_PORT_INDEX + 1}_{work_project.id}"


async def _get_data(entity_type: str = "experts", seed_value: int | None = None, count: int = 200) -> list[dict]:
    items = await load_dataset_data(
        backend_url=work_project.backend_url,
        project_key=PROJECT_KEY,
        entity_type=entity_type,
        seed_value=seed_value if seed_value is not None else 0,
        limit=count,
        method="distribute",
    )
    if items:
        return items
    if entity_type == "experts":
        return EXPERTS_DATA_MODIFIED
    return []


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
        delta_days = random.randint(1, 5)
        if operator == ComparisonOperator.GREATER_THAN:
            return field_value - timedelta(days=delta_days)
        if operator == ComparisonOperator.LESS_THAN:
            return field_value + timedelta(days=delta_days)
        if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL, ComparisonOperator.EQUALS}:
            return field_value
        if operator == ComparisonOperator.NOT_EQUALS:
            return field_value + timedelta(days=delta_days + 1)

    if isinstance(field_value, time):
        delta_minutes = random.choice([5, 10, 15, 30, 60])

        def add_minutes(t, mins):
            full_dt = datetime.combine(date.today(), t) + timedelta(minutes=mins)
            return full_dt.time()

        if operator == ComparisonOperator.GREATER_THAN:
            return add_minutes(field_value, -delta_minutes)
        if operator == ComparisonOperator.LESS_THAN:
            return add_minutes(field_value, delta_minutes)
        if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL, ComparisonOperator.EQUALS}:
            return field_value
        if operator == ComparisonOperator.NOT_EQUALS:
            valid = [v[field] for v in dataset if v.get(field) and v.get(field) != field_value]
            return random.choice(valid) if valid else add_minutes(field_value, delta_minutes + 5)

    if operator == ComparisonOperator.EQUALS:
        return field_value

    if operator == ComparisonOperator.NOT_EQUALS:
        valid = [v[field] for v in dataset if v.get(field) and v.get(field) != field_value]
        return random.choice(valid) if valid else None

    if operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        if len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            return field_value[start:end]
        return field_value

    if operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        for _ in range(100):
            test_str = "".join(random.choice(alphabet) for _ in range(3))
            if test_str.lower() not in field_value.lower():
                return test_str
        return "xyz"  # fallback

    if operator == ComparisonOperator.IN_LIST:
        all_values = list({v.get(field) for v in dataset if field in v})
        if not all_values:
            return [field_value]
        random.shuffle(all_values)
        subset = random.sample(all_values, min(2, len(all_values)))
        if field_value not in subset:
            subset.append(field_value)
        return list(set(subset))

    if operator == ComparisonOperator.NOT_IN_LIST:
        all_values = list({v.get(field) for v in dataset if field in v})
        if field_value in all_values:
            all_values.remove(field_value)
        return random.sample(all_values, min(2, len(all_values))) if all_values else []

    if operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    } and isinstance(field_value, int | float):
        delta = random.uniform(0.5, 2.0) if isinstance(field_value, float) else random.randint(1, 5)
        if operator == ComparisonOperator.GREATER_THAN:
            return field_value - delta
        if operator == ComparisonOperator.LESS_THAN:
            return field_value + delta
        if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
            return field_value

    return None


def _generate_constraints(
    dataset: list[dict], field_operators: dict, field_map: dict | None = None, min_constraints: int | None = 1, num_constraints: int | None = None, selected_fields: list | None = None
) -> list[dict[str, Any]]:
    """
    Generates constraints based on the dataset and field operator mapping.
    """
    all_constraints = []
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


async def generate_book_consultant_constraint() -> list[dict[str, Any]]:
    dataset = await _get_data("experts")
    field_operators = FIELD_OPERATORS_USER_BOOK_CONSULTANT_MAP
    selected_field = ["slug"]
    constraints_list = _generate_constraints(dataset, field_operators, min_constraints=2, selected_fields=selected_field)

    return constraints_list


async def generate_hire_button_clicked_constraint() -> list[dict[str, Any]]:
    dataset = await _get_data("experts")
    field_operators = FIELD_OPERATORS_MAP_HIRE_BUTTON
    selected_field = []
    constraints_list = _generate_constraints(dataset, field_operators, min_constraints=2, selected_fields=selected_field)

    return constraints_list


async def generate_select_hiring_team_constraint() -> list[dict[str, Any]]:
    field_mapping = {
        "team": {"field": "team", "dataset": [{"team": t} for t in ["Microsoft", "Apple", "Google"]]},
    }
    dataset = await _get_data("experts")
    field_operators = FIELD_OPERATORS_MAP_HIRING_TEAM
    selected_fields = []
    constraints_list = _generate_constraints(dataset, field_operators, min_constraints=2, selected_fields=selected_fields, field_map=field_mapping)

    return constraints_list


async def generate_hire_consultation_constraint() -> list[dict[str, Any]]:
    field_mapping = {
        "increaseHowMuch": {"field": "increaseHowMuch", "dataset": [{"increaseHowMuch": p} for p in ["5%", "10%", "15%"]]},
        "increaseWhen": {"field": "increaseWhen", "dataset": [{"increaseWhen": p} for p in ["Never", "After 3 months", "After 6 months", "After 12 months"]]},
        "paymentType": {"field": "paymentType", "dataset": [{"paymentType": p} for p in ["fixed", "hourly"]]},
    }

    dataset = await _get_data("experts")
    field_operators = FIELD_OPERATORS_MAP_HIRING_CONSULTANT
    selected_fields = []
    constraints_list = _generate_constraints(dataset, field_operators, min_constraints=2, field_map=field_mapping, selected_fields=selected_fields)

    return constraints_list


async def generate_cancel_hire_constraint() -> list[dict[str, Any]]:
    dataset = await _get_data("experts")
    field_operators = FIELD_OPERATORS_MAP_CANCEL_HIRE
    fixed_fields = ["slug"]
    constraints_list = _generate_constraints(dataset, field_operators, min_constraints=2, selected_fields=fixed_fields)

    return constraints_list


async def generate_job_posting_constraint() -> list[dict[str, Any]]:
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


async def generate_write_job_title_constraint() -> list[dict[str, Any]]:
    constraints_list = []
    possible_fields = ["query"]
    query = [
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

    for field in possible_fields:
        allowed_ops = FIELD_OPERATORS_MAP_WRITING_A_JOB_TITLE.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)
        if field == "query":
            field_value = random.choice(query)
            query_dataset = [{"query": q} for q in query]
            value = _generate_constraint_value(operator, field_value, field, dataset=query_dataset)

            if value is not None:
                constraint = create_constraint_dict(field, operator, value)
                constraints_list.append(constraint)

    return constraints_list


async def generate_search_skill_constraint() -> list[dict[str, Any]]:
    constraints_list = []
    possible_field = ["skill"]
    popular_skill_data = [{"skill": q} for q in POPULAR_SKILLS]
    sample_skill = random.choice(popular_skill_data)
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


async def generate_add_skill_constraint() -> list[dict[str, Any]]:
    constraints_list = []
    possible_field = list(FIELD_OPERATORS_MAP_ADD_SKILL.keys())
    num_constraints = random.randint(1, len(possible_field))
    selected_field = random.sample(possible_field, num_constraints)
    popular_skills_data = [{"skill": q} for q in POPULAR_SKILLS]
    sample_skill = random.choice(popular_skills_data)
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


async def generate_submit_job_constraint() -> list[dict[str, Any]]:
    constraints_list = []
    possible_fields = list(FIELD_OPERATORS_MAP_SUBMIT_JOB.keys())
    num_constraints = random.randint(2, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)
    popular_skill_data = [{"skills": s} for s in POPULAR_SKILLS]
    sample_skills = random.choice(popular_skill_data)
    title_data = [
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
    scope_data = ["Small", "Medium", "Large"]
    duration_data = ["3 to 6 months", "More than 6 months"]
    budget_type_data = ["hourly", "fixed"]
    job_descriptions_data = [
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
    rate_constraints = []
    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_SUBMIT_JOB.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)
        value = None

        if field == "budgetType":
            field_value = random.choice(budget_type_data)
            budget_type_dataset = [{"budgetType": p} for p in budget_type_data]
            value = _generate_constraint_value(operator, field_value, field, dataset=budget_type_dataset)

        elif field == "description":
            field_value = random.choice(job_descriptions_data)
            job_descriptions_dataset = [{"description": d} for d in job_descriptions_data]
            value = _generate_constraint_value(operator, field_value, field, dataset=job_descriptions_dataset)

        elif field == "duration":
            field_value = random.choice(duration_data)
            duration_dataset = [{"duration": d} for d in duration_data]
            value = _generate_constraint_value(operator, field_value, field, dataset=duration_dataset)

        elif field in ["rate_from", "rate_to"]:
            if not rate_constraints:
                from_ops = FIELD_OPERATORS_MAP_SUBMIT_JOB["rate_from"]
                to_ops = FIELD_OPERATORS_MAP_SUBMIT_JOB["rate_to"]
                rate_constraints = generate_to_and_from_constraints(from_ops, to_ops)
                constraints_list.extend(rate_constraints)

        elif field == "scope":
            field_value = random.choice(scope_data)
            scope_dataset = [{"scope": s} for s in scope_data]
            value = _generate_constraint_value(operator, field_value, field, dataset=scope_dataset)

        elif field == "skills":
            field_value = sample_skills.get(field, None)
            value = _generate_constraint_value(operator, field_value, field, dataset=popular_skill_data)

        else:
            field_value = random.choice(title_data)
            title_dataset = [{"title": t} for t in title_data]
            value = _generate_constraint_value(operator, field_value, field, dataset=title_dataset)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


async def generate_close_posting_job_constraint() -> list[dict[str, Any]]:
    constraints_list = []
    possible_field = list(FIELD_OPERATORS_MAP_SUBMIT_JOB.keys())
    num_constraints = random.randint(2, len(possible_field))
    selected_field = random.sample(possible_field, num_constraints)
    popular_skill_data = [{"skills": s} for s in POPULAR_SKILLS]
    sample_skills = random.choice(popular_skill_data)
    title_data = [
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
    scope_data = ["Small", "Medium", "Large"]
    duration_data = ["3 to 6 months", "More than 6 months"]
    budget_type_data = ["hourly", "fixed"]
    job_descriptions_data = [
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
    rate_constraints = []
    for field in selected_field:
        allowed_ops = FIELD_OPERATORS_MAP_CLOSE_JOB_POSTING.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)
        value = None

        if field == "budgetType":
            field_value = random.choice(budget_type_data)
            budget_type_dataset = [{"budgetType": p} for p in budget_type_data]
            value = _generate_constraint_value(operator, field_value, field, dataset=budget_type_dataset)

        elif field == "description":
            field_value = random.choice(job_descriptions_data)
            job_descriptions_dataset = [{"description": d} for d in job_descriptions_data]
            value = _generate_constraint_value(operator, field_value, field, dataset=job_descriptions_dataset)

        elif field == "duration":
            field_value = random.choice(duration_data)
            duration_dataset = [{"duration": d} for d in duration_data]
            value = _generate_constraint_value(operator, field_value, field, dataset=duration_dataset)

        elif field in ["rate_from", "rate_to"]:
            if not rate_constraints:
                from_ops = FIELD_OPERATORS_MAP_SUBMIT_JOB["rate_from"]
                to_ops = FIELD_OPERATORS_MAP_SUBMIT_JOB["rate_to"]
                rate_constraints = generate_to_and_from_constraints(from_ops, to_ops)
                constraints_list.extend(rate_constraints)

        elif field == "scope":
            field_value = random.choice(scope_data)
            scope_dataset = [{"scope": s} for s in scope_data]
            value = _generate_constraint_value(operator, field_value, field, dataset=scope_dataset)

        elif field == "skills":
            field_value = sample_skills.get(field, None)
            value = _generate_constraint_value(operator, field_value, field, dataset=popular_skill_data)

        else:
            field_value = random.choice(title_data)
            title_dataset = [{"title": t} for t in title_data]
            value = _generate_constraint_value(operator, field_value, field, dataset=title_dataset)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


def generate_to_and_from_constraints(from_op: ComparisonOperator, to_op: ComparisonOperator) -> Any:
    rate_from = "rate_from"
    rate_from_value = random.randint(10, 50)
    rate_from_op = ComparisonOperator(random.choice(from_op))

    rate_to = "rate_to"
    rate_to_value = random.randint(rate_from_value + 1, rate_from_value + 51)
    rate_to_op = ComparisonOperator(random.choice(to_op))
    all_constraints = []
    all_constraints.append(create_constraint_dict(rate_from, rate_from_op, rate_from_value))
    all_constraints.append(create_constraint_dict(rate_to, rate_to_op, rate_to_value))
    return all_constraints
