import random
from datetime import datetime, timedelta
from random import choice
from typing import Any

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data

from ..criterion_helper import ComparisonOperator
from ..shared_utils import create_constraint_dict
from .data import (
    FIELD_OPERATORS_APPLY_FOR_JOB_MAP,
    FIELD_OPERATORS_COMMENT_ON_POST_MAP,
    FIELD_OPERATORS_CONNECT_WITH_USER_MAP,
    FIELD_OPERATORS_FOLLOW_PAGE_MAP,
    FIELD_OPERATORS_LIKE_POST_MAP,
    FIELD_OPERATORS_POST_STATUS_MAP,
    FIELD_OPERATORS_SEARCH_JOBS_MAP,
    FIELD_OPERATORS_SEARCH_USERS_MAP,
    FIELD_OPERATORS_VIEW_JOB_MAP,
    FIELD_OPERATORS_VIEW_USER_PROFILE_MAP,
)
from .main import FRONTEND_PORT_INDEX, connect_project

PROJECT_KEY = f"web_{FRONTEND_PORT_INDEX + 1}_{connect_project.id}"


async def _get_data(entity_type: str, seed_value: int | None = None, count: int = 50) -> list[dict]:
    items = await load_dataset_data(
        backend_url=connect_project.backend_url,
        project_key=PROJECT_KEY,
        entity_type=entity_type,
        seed_value=seed_value if seed_value is not None else 0,
        limit=count,
        method="distribute",
    )
    if items:
        return items
    return []


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


def _generate_constraints(dataset: list[dict], field_operators: dict, field_map: dict | None = None, num_constraints: int | None = None, selected_fields: list | None = None) -> list[dict[str, Any]]:
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
        num_constraints = random.randint(1, len(possible_fields))

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
            if "." in new_field:
                # Handle nested fields
                field_value = _get_nested_value(sample_data, new_field)
                if field_value is None:
                    continue
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


def _get_nested_value(obj, dotted_key, default=None):
    keys = dotted_key.split(".")
    for key in keys:
        if isinstance(obj, dict) and key in obj:
            obj = obj[key]
        else:
            return default
    return obj


async def generate_view_user_profile_constraints() -> list[dict[str, Any]]:
    """
    Generates constraints for viewing a user profile based on the provided user profile data.
    """

    dataset = await _get_data("users")
    field_operators = FIELD_OPERATORS_VIEW_USER_PROFILE_MAP
    all_constraints = _generate_constraints(dataset, field_operators, num_constraints=1)

    return all_constraints


async def generate_connect_with_user_constraints() -> list[dict[str, Any]]:
    users = await _get_data("users")
    dataset = [u for u in users if u.get("username") != "alexsmith"]

    field_operators = FIELD_OPERATORS_CONNECT_WITH_USER_MAP
    field_map = {
        "target_name": "name",
    }
    all_constraints = _generate_constraints(dataset, field_operators, field_map, num_constraints=1)
    return all_constraints


async def generate_like_post_constraints():
    """
    Generates constraints for liking a post based on the provided post data.
    """
    dataset = await _get_data("posts")
    field_operators = FIELD_OPERATORS_LIKE_POST_MAP
    field_map = {"poster_content": "content", "poster_name": "name"}

    all_constraints = _generate_constraints(dataset, field_operators, field_map)
    return all_constraints


SAMPLE_COMMENTS = [
    "Congrats on the achievement!",
    "This is super inspiring",
    "Thanks for sharing this!",
    "Great job, keep it up!",
    "Very insightful post.",
    "Love your perspective on this.",
    "Wishing you all the best!",
    "Amazing update, well done",
    "Appreciate the transparency.",
    "This resonates with me a lot.",
    "Big fan of your work!",
    "Such a powerful message.",
    "Excited to see what's next!",
    "You've earned it, congrats!",
    "Impressive progress!",
    "Couldn't agree more.",
    "Really well said",
    "This made my day",
    "Well deserved recognition!",
    "Always learning something from you!",
]


async def generate_comment_on_post_constraints() -> list[dict[str, Any]]:
    """
    Generates constraints for commenting on a post based on the provided post data.
    """
    fixed_field = "comment_text"
    sample_comments = [{fixed_field: comment} for comment in SAMPLE_COMMENTS]
    field_operators = FIELD_OPERATORS_COMMENT_ON_POST_MAP.copy()

    operators = field_operators.pop(fixed_field)
    new_field_operators = {fixed_field: operators}
    all_constraints = _generate_constraints(sample_comments, new_field_operators)

    dataset = await _get_data("posts")
    field_map = {"poster_content": "content", "poster_name": "name"}
    constraints = _generate_constraints(dataset, field_operators, field_map)
    all_constraints.extend(constraints)

    return all_constraints


sample_post_contents = [
    "Excited to join LinkedIn Lite!",
    "Just released a minimal LinkedIn clone with Next.js and Tailwind CSS!",
    "Attended a fantastic webinar on remote team collaboration today! Highly recommend it.",
    "Started learning TypeScript this week. Any tips for a React dev?",
    "Just finished a 10k run for charity. Feeling accomplished!",
    "Reading 'Inspired' by Marty Cagan. Game changer for product managers!",
    "Just launched our summer brand campaign. Feeling proud of the team!",
    "Migrated 20+ services to Kubernetes today. DevOps win!",
    "Hosting our first DEI panel at PeopleFirst. Let's build inclusive cultures.",
    "Experimenting with fine-tuning LLMs on small domain datasets. Results look promising.",
    "We just hit 10K users on RemoteWorks! Thank you for believing in us.",
    "Published a new research paper on GNNs and edge inference. DM for collab.",
    "Launched our beta app today—can't wait for your feedback!",
    "Tried out the new GPT-4o model. Mind blown",
    "Remote work has changed how we build products. Flexibility = productivity.",
    "Had a great time mentoring at today's hackathon!",
    "Weekly reminder: take breaks, breathe, and trust your process.",
    "Redesigned our onboarding flow—conversion is up 18%!",
    "Learning Rust has been surprisingly fun and powerful.",
    "Attending React Summit next month—who else is going?",
]


async def generate_post_status_constraints() -> list[dict[str, Any]]:
    all_constraints = []
    field = "content"
    field_operators = FIELD_OPERATORS_POST_STATUS_MAP
    op = ComparisonOperator(choice(field_operators[field]))
    field_value = choice(sample_post_contents)
    dataset = [{"content": content} for content in sample_post_contents]

    value = _generate_constraint_value(op, field_value, field, dataset)
    constraint = create_constraint_dict(field, op, value)
    all_constraints.append(constraint)

    return all_constraints


async def generate_follow_page_constraints() -> list[dict[str, Any]]:
    """
    Generates constraints for following a company page based on the provided user profile data.
    """
    dataset = await _get_data("companies")
    field_operators = FIELD_OPERATORS_FOLLOW_PAGE_MAP
    field_map = {"company": "name"}
    all_constraints = _generate_constraints(dataset, field_operators, field_map)

    return all_constraints


async def generate_apply_for_job_constraints() -> list[dict[str, Any]]:
    dataset = await _get_data("jobs")

    field_map = {
        "job_title": "title",
    }

    field_operators = FIELD_OPERATORS_APPLY_FOR_JOB_MAP
    all_constraints = _generate_constraints(dataset, field_operators, field_map)

    return all_constraints


async def generate_search_users_constraints() -> list[dict[str, Any]]:
    """
    Generates constraints for searching users based on the provided user profile data.
    """
    dataset = await _get_data("users")
    field_operators = FIELD_OPERATORS_SEARCH_USERS_MAP
    field_map = {"query": ["name", "title"]}
    all_constraints = _generate_constraints(dataset, field_operators, field_map)

    return all_constraints


async def generate_search_jobs_constraints() -> list[dict[str, Any]]:
    """
    Generates constraints for searching jobs based on the provided job data.
    Replaces raw salary values with predefined filter options if applicable.
    """
    dataset = await _get_data("jobs")
    field_operators = FIELD_OPERATORS_SEARCH_JOBS_MAP
    field_map = {"query": ["title", "company"]}

    filter_options_data = {
        "experience": ["2+ years", "3+ years", "4+ years", "5+ years", "6+ years"],
        "salary": ["0-50000", "50000-75000", "75000-100000", "100000-125000", "125000-150000", "150000+"],
        "location": ["Austin, TX", "Boston, MA", "Chicago, IL", "Denver, CO", "Los Angeles, CA", "New York, NY", "Remote", "Remote (US)", "San Francisco, CA", "Seattle, WA"],
        "remote": [True, False],
    }

    all_constraints = _generate_constraints(dataset, field_operators, field_map)

    for constraint in all_constraints:
        if constraint["field"] == "salary":
            raw_value = str(constraint["value"])

            # Extract min salary
            cleaned = raw_value.replace("$", "").replace(",", "").strip()
            if "-" in cleaned:
                parts = cleaned.split("-")
                try:
                    min_salary = int(parts[0])
                except ValueError:
                    continue
            elif "+" in cleaned:
                parts = cleaned.split("+")
                try:
                    min_salary = int(parts[0])
                except ValueError:
                    continue
            else:
                try:
                    min_salary = int(cleaned)
                except ValueError:
                    continue

            # Match with filter option
            for option in filter_options_data["salary"]:
                if "-" in option:
                    start, end = map(int, option.split("-"))
                    if start <= min_salary <= end:
                        constraint["value"] = option
                        break
                elif "+" in option:
                    base = int(option.replace("+", ""))
                    if min_salary >= base:
                        constraint["value"] = option
                        break

    return all_constraints


async def generate_view_job_constraints() -> list[dict[str, Any]]:
    """
    Generates constraints for viewing a job based on the provided job data.
    """
    dataset = await _get_data("jobs")
    field_operators = FIELD_OPERATORS_VIEW_JOB_MAP
    field_map = {"job_title": "title"}
    all_constraints = _generate_constraints(dataset, field_operators, field_map)

    return all_constraints
