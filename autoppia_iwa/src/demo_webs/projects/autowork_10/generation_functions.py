import random
from datetime import datetime, timedelta
from random import choice
from typing import Any

from ..criterion_helper import ComparisonOperator
from ..shared_utils import create_constraint_dict
from .data import (
    EXPERTS,
    EXPERTS_DATA_MODIFIED,
    FIELD_OPERATORS_MAP_ADD_SKILL,
    FIELD_OPERATORS_MAP_CANCEL_HIRE_CONSULTANT,
    FIELD_OPERATORS_MAP_CLOSE_JOB_POSTING,
    FIELD_OPERATORS_MAP_HIRE_BUTTON,
    FIELD_OPERATORS_MAP_HIRING_CONSULTANT,
    FIELD_OPERATORS_MAP_HIRING_TEAM,
    FIELD_OPERATORS_MAP_POSTING_A_JOB,
    FIELD_OPERATORS_MAP_REMOVE_SKILL,
    FIELD_OPERATORS_MAP_SEARCH_SKILL,
    FIELD_OPERATORS_MAP_SUBMIT_JOB,
    FIELD_OPERATORS_MAP_WRITING_A_JOB_TITLE,
    FIELD_OPERATORS_USER_BOOK_CONSULTANT_MAP,
    POPULAR_SKILLS,
)


def _generate_constraint_value(operator: ComparisonOperator, field_value: Any, field: str, dataset: list[dict[str, Any]]) -> Any:
    value = None

    # Handle datetime comparisons
    if isinstance(field_value, datetime):
        delta_days = random.randint(1, 5)
        if operator == ComparisonOperator.GREATER_THAN:
            return field_value - timedelta(days=delta_days)
        elif operator == ComparisonOperator.LESS_THAN:
            return field_value + timedelta(days=delta_days)
        elif operator == ComparisonOperator.GREATER_EQUAL or operator == ComparisonOperator.LESS_EQUAL or operator == ComparisonOperator.EQUALS:
            return field_value
        elif operator == ComparisonOperator.NOT_EQUALS:
            return field_value + timedelta(days=delta_days + 1)

    if operator == ComparisonOperator.EQUALS:
        return field_value

    elif operator == ComparisonOperator.NOT_EQUALS:
        if isinstance(field_value, str):
            valid = [v[field] for v in dataset if v.get(field) and v.get(field) != field_value]
            return random.choice(valid) if valid else None
        elif isinstance(field_value, list):
            valid = [v[f] for v in dataset for f in field_value if v.get(f) and v.get(f) != field_value]
            return random.choice(valid) if valid else None

    elif operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        if len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            return field_value[start:end]
        return field_value

    elif operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        while True:
            test_str = "".join(random.choice(alphabet) for _ in range(3))
            if test_str.lower() not in field_value.lower():
                return test_str

    elif operator == ComparisonOperator.IN_LIST:
        all_values = []
        for v in dataset:
            if field in v:
                val = v.get(field)
                if isinstance(val, list):
                    all_values.extend(val)
                elif val is not None:
                    all_values.append(val)
        all_values = list(set(all_values))

        if not all_values:
            return [field_value]
        random.shuffle(all_values)
        subset = random.sample(all_values, min(2, len(all_values)))
        if field_value not in subset:
            subset.append(field_value)
        return list(set(subset))

    elif operator == ComparisonOperator.NOT_IN_LIST:
        all_values = []
        for v in dataset:
            if field in v:
                val = v.get(field)
                if isinstance(val, list):
                    all_values.extend(val)
                elif val is not None:
                    all_values.append(val)
        all_values = list(set(all_values))

        if field_value in all_values:
            all_values.remove(field_value)
        return random.sample(all_values, min(2, len(all_values))) if all_values else []

    elif operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    }:
        numeric_values = [v.get(field) for v in dataset if isinstance(v.get(field), int | float)]
        if numeric_values:
            base = random.choice(numeric_values)
            delta = random.uniform(1, 3)
            if operator == ComparisonOperator.GREATER_THAN:
                return round(base - delta, 2)
            elif operator == ComparisonOperator.LESS_THAN:
                return round(base + delta, 2)
            elif operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
                return round(base, 2)

    return value


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
        if isinstance(new_field, list):
            random.shuffle(new_field)
            for f in new_field:
                field_value = sample_data.get(f)
                new_field = f
                break
        else:
            field_value = sample_data.get(new_field)

        if field_value is None:
            continue

        # Generate a constraint value based on the operator and field value
        constraint_value = _generate_constraint_value(op, field_value, new_field, dataset)

        if constraint_value is not None:
            constraint = create_constraint_dict(field, op, constraint_value)
            all_constraints.append(constraint)

    return all_constraints


def generate_book_consultant_constraint() -> list[dict[str, Any]]:
    dataset = EXPERTS_DATA_MODIFIED
    field_operators = FIELD_OPERATORS_USER_BOOK_CONSULTANT_MAP
    constraints_list = _generate_constraints(dataset, field_operators, min_constraints=2)

    return constraints_list


def generate_hire_button_clicked_constraint() -> list[dict[str, Any]]:
    dataset = EXPERTS_DATA_MODIFIED
    field_operators = FIELD_OPERATORS_MAP_HIRE_BUTTON
    constraints_list = _generate_constraints(dataset, field_operators, min_constraints=2)

    return constraints_list


def generate_select_hiring_team_constraint() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    field_mapping = {
        "expertName": "name",
        "expertSlug": "slug",
    }
    possible_fields = list(FIELD_OPERATORS_MAP_HIRING_TEAM.keys())
    num_constraints = random.randint(2, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)
    sample_expert = random.choice(EXPERTS)

    team = ["Microsoft", "Apple", "Google"]

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_HIRING_TEAM.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)
        if field == "team":
            field_value = choice(team)
            dataset = [{"team": t} for t in team]
            value = _generate_constraint_value(operator, field_value, field, dataset=dataset)
        else:
            new_field = field_mapping.get(field, field)
            field_value = sample_expert.get(new_field)
            value = _generate_constraint_value(operator, field_value, new_field, dataset=EXPERTS)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


def generate_hire_consultation_constraint() -> list[dict[str, Any]]:
    constraints_list = []
    field_mapping = {
        "country": "country",
        "expertName": "name",
        "expertSlug": "slug",
        "role": "role",
        "increaseHowMuch": "increaseHowMuch",
        "increaseWhen": "increaseWhen",
        "paymentType": "paymentType",
        "rate": "lastReviewRate",
    }
    possible_fields = list(FIELD_OPERATORS_MAP_HIRING_CONSULTANT.keys())
    num_constraints = random.randint(2, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)
    payment_type = ["fixed", "hourly"]
    increase_how_much = ["5%", "10%", "15%"]
    increase_when = ["Never", "After 3 months", "After 6 months", "After 12 months"]
    random.choice(EXPERTS_DATA_MODIFIED)
    sample_expert = random.choice(EXPERTS_DATA_MODIFIED)
    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_HIRING_CONSULTANT.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)
        if field == "paymentType":
            field_value = random.choice(payment_type)
            payment_dataset = [{"paymentType": p} for p in payment_type]
            value = _generate_constraint_value(operator, field_value, field, dataset=payment_dataset)

        elif field == "increaseHowMuch":
            field_value = random.choice(increase_how_much)
            increase_when_dataset = [{"increaseWhen": p} for p in increase_how_much]
            value = _generate_constraint_value(operator, field_value, field, dataset=increase_when_dataset)

        elif field == "increaseWhen":
            field_value = random.choice(increase_when)
            increase_when_dataset = [{"increaseWhen": p} for p in increase_when]
            value = _generate_constraint_value(operator, field_value, field, dataset=increase_when_dataset)

        else:
            new_field = field_mapping.get(field, field)
            field_value = sample_expert.get(new_field)
            value = _generate_constraint_value(operator, field_value, new_field, dataset=EXPERTS_DATA_MODIFIED)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


def generate_cancel_hire_consultation_constraint() -> list[dict[str, Any]]:
    dataset = EXPERTS_DATA_MODIFIED
    field_operators = FIELD_OPERATORS_MAP_CANCEL_HIRE_CONSULTANT
    constraints_list = _generate_constraints(dataset, field_operators, min_constraints=2)

    return constraints_list


def generate_job_posting_constraint() -> list[dict[str, Any]]:
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


def generate_write_job_title_constraint() -> list[dict[str, Any]]:
    constraints_list = []
    possible_fields = ["query", "step"]
    # num_constraints= random.randint(1, len(possible_fields))
    # selected_fields = random.sample(possible_field, num_constraints)
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
    # step = [1]

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

            # else:
            #     field_value = random.choice(step)
            #     step_dataset = [{'step': s} for s in step]
            #     value = _generate_constraint_value(operator, field_value, field, dataset=step_dataset)

            if value is not None:
                constraint = create_constraint_dict(field, operator, value)
                constraints_list.append(constraint)

    return constraints_list


def generate_search_skill_constraint() -> list[dict[str, Any]]:
    constraints_list = []
    possible_field = ["query"]

    popular_skill_data = [{"query": q} for q in POPULAR_SKILLS]
    sample_skill = random.choice(popular_skill_data)
    for field in possible_field:
        allowed_ops = FIELD_OPERATORS_MAP_SEARCH_SKILL.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)
        field_value = sample_skill.get(field, None)
        value = _generate_constraint_value(operator, field_value, field, dataset=popular_skill_data)
        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)
    return constraints_list


def generate_add_skill_constraint() -> list[dict[str, Any]]:
    constraints_list = []
    possible_field = list(FIELD_OPERATORS_MAP_ADD_SKILL.keys())
    num_constraints = random.randint(1, len(possible_field))
    selected_field = random.sample(possible_field, num_constraints)
    popular_skills_data = [{"query": q} for q in POPULAR_SKILLS]
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


def generate_remove_skill_constraint() -> list[dict[str, Any]]:
    constraints_list = []
    possible_field = list(FIELD_OPERATORS_MAP_REMOVE_SKILL.keys())
    num_constraints = random.randint(1, len(possible_field))
    selected_field = random.sample(possible_field, num_constraints)
    popular_skills_data = [{"query": q} for q in POPULAR_SKILLS]
    sample_skill = random.choice(popular_skills_data)
    for field in selected_field:
        allowed_ops = FIELD_OPERATORS_MAP_REMOVE_SKILL.get(field, [])
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


# def generate_attach_file_constraint() -> list[dict[str, Any]]:
#     constraints_list = []
#     possible_fields= list(FIELD_OPERATORS_MAP_ATTACH_FILE.keys())
#     num_constraints = random.randint(2, len(possible_fields))
#     selected_field = random.sample(possible_fields, num_constraints)
#


def generate_submit_job_constraint() -> list[dict[str, Any]]:
    constraints_list = []
    possible_field = list(FIELD_OPERATORS_MAP_SUBMIT_JOB.keys())
    num_constraints = random.randint(2, len(possible_field))
    selected_field = random.sample(possible_field, num_constraints)
    popular_skill_data = [{"query": q} for q in POPULAR_SKILLS]
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
    # rate_to_data = list(range(0,1001)) for integers
    rate_to_data = []
    i = 0.0
    while i <= 1000:
        rate_to_data.append(i, 1)
        i += 0.1

    # rate_from_data = list(range(0,1001))

    rate_from_data = []
    i = 0.0
    while i <= 1000:
        rate_from_data.append(i, 1)
        i += 0.1

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
        allowed_ops = FIELD_OPERATORS_MAP_SUBMIT_JOB.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

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


def generate_close_posting_job_constraint() -> list[dict[str, Any]]:
    constraints_list = []
    possible_field = list(FIELD_OPERATORS_MAP_SUBMIT_JOB.keys())
    num_constraints = random.randint(2, len(possible_field))
    selected_field = random.sample(possible_field, num_constraints)
    popular_skill_data = [{"query": q} for q in POPULAR_SKILLS]
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
