import contextlib
import random
from datetime import date, datetime, time, timedelta
from random import choice
from typing import Any

from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url

from ..criterion_helper import ComparisonOperator
from ..shared_utils import create_constraint_dict
from .data import (
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
from .data_utils import get_data, fetch_experts_data


async def _ensure_expert_dataset(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Ensure experts dataset is available."""
    if dataset is not None:
        return dataset
    seed = get_seed_from_url(task_url)
    return await get_data(seed_value=seed)


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
            subpart = field_value[start:end]
            return subpart.strip()
        return field_value

    if operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        for _ in range(100):
            test_str = "".join(random.choice(alphabet) for _ in range(3))
            if test_str.lower() not in field_value.lower():
                return test_str
        return "xyz"  # fallback

    if operator == ComparisonOperator.IN_LIST:
        all_values = list({v.get(field) for v in dataset if field in v and v.get(field) is not None})
        if not all_values:
            return [field_value]
        random.shuffle(all_values)
        subset = random.sample(all_values, min(2, len(all_values)))
        if field_value not in subset:
            subset.append(field_value)
        return list(set(subset))

    if operator == ComparisonOperator.NOT_IN_LIST:
        all_values = list({v.get(field) for v in dataset if field in v and v.get(field) is not None})
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
        delta = random.uniform(0.5, 2.0) if isinstance(field_value, float) else random.randint(1, 5)
        if operator == ComparisonOperator.GREATER_THAN:
            return round(field_value - delta, 2)
        if operator == ComparisonOperator.LESS_THAN:
            return round(field_value + delta, 2)
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
    if not dataset:
        print("[ERROR] No dataset provided")
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


async def generate_book_consultant_constraint(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    dataset = await _ensure_expert_dataset(task_url, dataset)
    field_operators = FIELD_OPERATORS_USER_BOOK_CONSULTANT_MAP
    selected_field = ["slug"]
    constraints_list = _generate_constraints(dataset, field_operators, min_constraints=2, selected_fields=selected_field)

    return constraints_list


async def generate_hire_button_clicked_constraint(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    dataset = await _ensure_expert_dataset(task_url, dataset)
    field_operators = FIELD_OPERATORS_MAP_HIRE_BUTTON
    selected_field = []
    constraints_list = _generate_constraints(dataset, field_operators, min_constraints=2, selected_fields=selected_field)

    return constraints_list


async def generate_content_expert_message_sent_constraint(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
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
    if value is None:
        constraint.append(create_constraint_dict(field, op, value))
    return constraint


async def generate_select_hiring_team_constraint(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    field_mapping = {
        "team": {"field": "team", "dataset": [{"team": t} for t in ["Microsoft", "Apple", "Google"]]},
    }
    dataset = await _ensure_expert_dataset(task_url, dataset)
    field_operators = FIELD_OPERATORS_MAP_HIRING_TEAM
    selected_fields = []
    constraints_list = _generate_constraints(dataset, field_operators, min_constraints=2, selected_fields=selected_fields, field_map=field_mapping)

    return constraints_list


async def generate_hire_consultation_constraint(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    field_mapping = {
        "increaseHowMuch": {"field": "increaseHowMuch", "dataset": [{"increaseHowMuch": p} for p in ["5%", "10%", "15%"]]},
        "increaseWhen": {"field": "increaseWhen", "dataset": [{"increaseWhen": p} for p in ["Never", "After 3 months", "After 6 months", "After 12 months"]]},
        "paymentType": {"field": "paymentType", "dataset": [{"paymentType": p} for p in ["fixed", "hourly"]]},
    }

    dataset = await _ensure_expert_dataset(task_url, dataset)
    field_operators = FIELD_OPERATORS_MAP_HIRING_CONSULTANT
    selected_fields = []
    constraints_list = _generate_constraints(dataset, field_operators, min_constraints=2, field_map=field_mapping, selected_fields=selected_fields)

    return constraints_list


async def generate_quick_hire_constraint(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    return await generate_book_consultant_constraint(task_url, dataset)


async def generate_cancel_hire_constraint(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    dataset = await _ensure_expert_dataset(task_url, dataset)
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


async def generate_budget_type_constraint() -> list[dict[str, Any]]:
    constraint = []
    field = "budget_type"
    allowed_ops = FIELD_OPERATORS_MAP_BUDGET_TYPE.get(field, None)
    op = ComparisonOperator(random.choice(allowed_ops))
    budget_type_data = ["hourly", "fixed"]
    field_value = random.choice(budget_type_data)
    budget_type_dataset = [{"budget_type": p} for p in budget_type_data]
    value = _generate_constraint_value(op, field_value, field, dataset=budget_type_dataset)
    constraint.append(create_constraint_dict(field, op, value))
    return constraint


async def generate_project_size_constraint() -> list[dict[str, Any]]:
    constraint = []
    field = "scope"
    scope_data = ["Small", "Medium", "Large"]
    allowed_ops = FIELD_OPERATORS_MAP_PROJECT_SIZE.get(field, None)
    op = ComparisonOperator(random.choice(allowed_ops))
    field_value = random.choice(scope_data)
    scope_dataset = [{"scope": s} for s in scope_data]
    value = _generate_constraint_value(op, field_value, field, dataset=scope_dataset)
    constraint.append(create_constraint_dict(field, op, value))
    return constraint


async def generate_timeline_constraint() -> list[dict[str, Any]]:
    constraint = []
    duration_data = ["3 to 6 months", "More than 6 months"]
    field = "duration"
    allowed_ops = FIELD_OPERATORS_MAP_TIMELINE.get(field, None)
    op = ComparisonOperator(random.choice(allowed_ops))
    field_value = random.choice(duration_data)
    scope_dataset = [{"duration": d} for d in duration_data]
    value = _generate_constraint_value(op, field_value, field, dataset=scope_dataset)
    constraint.append(create_constraint_dict(field, op, value))
    return constraint


async def generate_rate_range_constraint() -> list[dict[str, Any]]:
    constraints: list[dict[str, Any]] = []
    from_ops = FIELD_OPERATORS_MAP_RATE_RANGE["rate_from"]
    to_ops = FIELD_OPERATORS_MAP_RATE_RANGE["rate_to"]
    rate_constraints = generate_to_and_from_constraints(from_ops, to_ops)
    constraints.extend(rate_constraints)
    return constraints


async def generate_write_job_description_constraint() -> list[dict[str, Any]]:
    constraint = []
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
    field = "description"
    allowed_ops = FIELD_OPERATORS_MAP_JOB_DESCRIPTION.get(field, None)
    op = ComparisonOperator(random.choice(allowed_ops))
    field_value = random.choice(job_descriptions_data)
    scope_dataset = [{"description": d} for d in job_descriptions_data]
    value = _generate_constraint_value(op, field_value, field, dataset=scope_dataset)
    constraint.append(create_constraint_dict(field, op, value))
    return constraint


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


async def generate_favorite_expert_selected_constraint(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    dataset = await _ensure_expert_dataset(task_url, dataset)
    field_map = {"expert_name": "name", "expert_slug": "slug"}
    return _generate_constraints(dataset, FIELD_OPERATORS_MAP_FAVORITE_EXPERT, field_map=field_map)


async def generate_favorite_expert_removed_constraint(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    return await generate_favorite_expert_selected_constraint(task_url, dataset)


async def generate_browse_favorite_expert_constraint() -> list[dict[str, Any]]:
    dataset = [{"source": s} for s in ["favorites_empty_state", "favorites_page"]]
    return _generate_constraints(dataset, FIELD_OPERATORS_MAP_BROWSE_FAVORITE_EXPERT)


async def generate_edit_about_constraint() -> list[dict[str, Any]]:
    constraint_list = []
    about_data = [
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
    field = "value"
    allowed_ops = FIELD_OPERATORS_MAP_EDIT_PROFILE_FIELD[field]
    op = ComparisonOperator(random.choice(allowed_ops))
    field_value = random.choice(about_data)
    about_dataset = [{"about": n} for n in about_data]
    value = _generate_constraint_value(op, field_value, field, dataset=about_dataset)
    if value is None:
        constraint_list.append(create_constraint_dict(field, op, value))
    return constraint_list


async def generate_edit_profile_name_constraint() -> list[dict[str, Any]]:
    constraint_list = []
    user_names = [
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
    field = "value"
    allowed_ops = FIELD_OPERATORS_MAP_EDIT_PROFILE_FIELD[field]
    op = ComparisonOperator(random.choice(allowed_ops))
    field_value = random.choice(user_names)
    messages_dataset = [{"name": n} for n in user_names]
    value = _generate_constraint_value(op, field_value, field, dataset=messages_dataset)
    if value is None:
        constraint_list.append(create_constraint_dict(field, op, value))
    return constraint_list


async def generate_edit_profile_title_constraint() -> list[dict[str, Any]]:
    constraint_list = []
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
    field = "value"
    allowed_ops = FIELD_OPERATORS_MAP_EDIT_PROFILE_FIELD[field]
    op = ComparisonOperator(random.choice(allowed_ops))
    field_value = random.choice(title_data)
    title_dataset = [{"title": t} for t in title_data]
    value = _generate_constraint_value(op, field_value, field, dataset=title_dataset)
    if value is None:
        constraint_list.append(create_constraint_dict(field, op, value))
    return constraint_list


async def generate_edit_profile_location_constraint() -> list[dict[str, Any]]:
    constraint_list = []
    locations = [
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

    field = "value"
    allowed_ops = FIELD_OPERATORS_MAP_EDIT_PROFILE_FIELD[field]
    op = ComparisonOperator(random.choice(allowed_ops))
    field_value = random.choice(locations)
    location_dataset = [{"location": t} for t in locations]
    value = _generate_constraint_value(op, field_value, field, dataset=location_dataset)
    if value is None:
        constraint_list.append(create_constraint_dict(field, op, value))
    return constraint_list


async def generate_edit_profile_email_constraint() -> list[dict[str, Any]]:
    constraint_list = []
    emails = [
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
    field = "value"
    allowed_ops = FIELD_OPERATORS_MAP_EDIT_PROFILE_FIELD[field]
    op = ComparisonOperator(random.choice(allowed_ops))
    field_value = random.choice(emails)
    email_dataset = [{"email": e} for e in emails]
    value = _generate_constraint_value(op, field_value, field, dataset=email_dataset)
    if value is None:
        constraint_list.append(create_constraint_dict(field, op, value))
    return constraint_list


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
