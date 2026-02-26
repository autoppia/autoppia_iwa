import random
from datetime import datetime, timedelta
from random import choice
from typing import Any

from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url

from ..criterion_helper import ComparisonOperator
from ..shared_utils import create_constraint_dict
from .data import (
    FIELD_OPERATORS_APPLY_FOR_JOB_MAP,
    FIELD_OPERATORS_BACK_TO_ALL_JOBS_MAP,
    FIELD_OPERATORS_COMMENT_ON_POST_MAP,
    FIELD_OPERATORS_CONNECT_WITH_USER_MAP,
    FIELD_OPERATORS_EDIT_EXPERIENCE_MAP,
    FIELD_OPERATORS_EDIT_PROFILE_MAP,
    FIELD_OPERATORS_FILTER_JOBS_MAP,
    FIELD_OPERATORS_FOLLOW_PAGE_MAP,
    FIELD_OPERATORS_LIKE_POST_MAP,
    FIELD_OPERATORS_POST_STATUS_MAP,
    FIELD_OPERATORS_SAVE_POST_MAP,
    FIELD_OPERATORS_SEARCH_JOBS_MAP,
    FIELD_OPERATORS_SEARCH_USERS_MAP,
    FIELD_OPERATORS_VIEW_JOB_MAP,
    FIELD_OPERATORS_VIEW_USER_PROFILE_MAP,
)
from .data_utils import fetch_data


def _extract_entity_dataset(dataset: Any, entity_type: str) -> list[dict[str, Any]] | None:
    if dataset is None:
        return None
    if isinstance(dataset, list):
        return dataset
    if isinstance(dataset, dict):
        value = dataset.get(entity_type)
        if isinstance(value, list):
            return value
    return None


async def _ensure_entity_dataset(
    task_url: str | None,
    dataset: dict[str, list[dict[str, Any]]] | None,
    *,
    entity_type: str,
    method: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Extract entity data from the cache dataset, or fetch from server if not available.

    """

    # Otherwise, fetch the specific entity type dynamically using the provided parameters
    seed = get_seed_from_url(task_url)

    fetched_dataset = await fetch_data(
        entity_type=entity_type,
        method=method if method else "select",
        seed_value=seed,
    )

    # Return as dictionary with entity_type as key
    return {entity_type: fetched_dataset}


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
    dataset: list[dict],
    field_operators: dict,
    field_map: dict | None = None,
    num_constraints: int | None = None,
    selected_fields: list | None = None,
    use_first_sample: bool = False,
    sample_index: int | None = None,
) -> list[dict[str, Any]]:
    """
    Generates constraints based on the dataset and field operator mapping.
    use_first_sample: if True, use dataset[0] for field values.
    sample_index: if set and dataset has enough elements, use dataset[sample_index]; else fallback.
    """
    all_constraints = []
    if not dataset:
        print("[ERROR] No dataset provided")
        return all_constraints
    if sample_index is not None and len(dataset) > sample_index:
        sample_data = dataset[sample_index]
    elif use_first_sample:
        sample_data = dataset[0]
    else:
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


# User index used by the web for profile/experience use cases (0-based).
USER_INDEX_FOR_WEB = 2


def _normalize_constraint_string(s: str) -> str:
    """Normalize so value matches heuristic: no newlines, collapsed spaces, stripped (prompt text is normalized similarly)."""
    s = s.replace("\r", " ").replace("\n", " ")
    s = " ".join(s.split())
    return s.strip()


def _single_word_for_contains(value: str) -> str:
    """Use a single word so the prompt is likely to quote it in full (heuristic value-in-prompt check). Only for contains."""
    words = [w for w in value.split() if w]
    return max(words, key=len) if words else value.strip()


def _normalize_constraint_value(
    value: Any,
    trim_leading_single_letter: bool = False,
) -> Any:
    """
    Normalize string constraint values (newlines -> space, collapse spaces, strip).
    No truncation: equals/not_equals require full value for exact match.
    trim_leading_single_letter: for contains only, remove leading single letter + space (e.g. 'e yesterday' -> 'yesterday').
    """
    if not isinstance(value, str):
        return value
    value = _normalize_constraint_string(value)
    if trim_leading_single_letter and len(value) > 2 and value[0].isalpha() and value[1:2] == " ":
        value = value[2:].lstrip()
    return value


async def generate_view_user_profile_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """
    Generates constraints for viewing a user profile based on the provided user profile data.
    Uses first user (index 0) to align with web implementation.
    """
    dataset_dict = await _ensure_entity_dataset(task_url, dataset, entity_type="users")
    dataset = dataset_dict.get("users", [])
    field_operators = FIELD_OPERATORS_VIEW_USER_PROFILE_MAP
    all_constraints = _generate_constraints(dataset, field_operators, num_constraints=1, sample_index=USER_INDEX_FOR_WEB)
    return all_constraints


async def generate_connect_with_user_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    users_dict = await _ensure_entity_dataset(task_url, dataset, entity_type="users")
    users = users_dict.get("users", [])
    dataset = [u for u in users if u.get("username") != "alexsmith"]

    field_operators = FIELD_OPERATORS_CONNECT_WITH_USER_MAP
    field_map = {
        "target_name": "name",
    }
    all_constraints = _generate_constraints(dataset, field_operators, field_map, num_constraints=1)
    return all_constraints


async def generate_like_post_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None):
    """
    Generates constraints for liking a post based on the provided post data.
    """
    dataset_dict = await _ensure_entity_dataset(task_url, dataset, entity_type="posts")
    dataset = dataset_dict.get("posts", [])
    field_operators = FIELD_OPERATORS_LIKE_POST_MAP
    field_map = {"poster_content": "content", "poster_name": "name"}

    all_constraints = _generate_constraints(dataset, field_operators, field_map)
    for c in all_constraints:
        if c.get("field") == "poster_content" and isinstance(c.get("value"), str):
            c["value"] = _normalize_constraint_value(c["value"], trim_leading_single_letter=True)
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


async def generate_comment_on_post_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """
    Generates constraints for commenting on a post based on the provided post data.
    """
    fixed_field = "comment_text"
    sample_comments = [{fixed_field: comment} for comment in SAMPLE_COMMENTS]
    field_operators = FIELD_OPERATORS_COMMENT_ON_POST_MAP.copy()

    operators = field_operators.pop(fixed_field)
    new_field_operators = {fixed_field: operators}
    all_constraints = _generate_constraints(sample_comments, new_field_operators)

    dataset_dict = await _ensure_entity_dataset(task_url, dataset, entity_type="posts")
    dataset = dataset_dict.get("posts", [])
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


async def generate_follow_page_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """
    Generates constraints for following a company page based on the provided user profile data.
    """

    dataset_dict = await _ensure_entity_dataset(task_url, dataset, entity_type="recommendations")
    dataset = dataset_dict.get("recommendations", [])
    field_operators = FIELD_OPERATORS_FOLLOW_PAGE_MAP
    field_map = {"recommendation": "title"}
    all_constraints = _generate_constraints(dataset, field_operators, field_map)

    return all_constraints


async def generate_unfollow_page_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """
    Generates constraints for unfollowing a company page.
    """
    constraints = await generate_follow_page_constraints(task_url, dataset)
    # Single-token value so prompt "containing 'X'" matches heuristic (value must appear in prompt)
    for c in constraints:
        if c.get("field") == "recommendation" and c.get("operator") == "contains" and isinstance(c.get("value"), str) and " " in c["value"]:
            c["value"] = _single_word_for_contains(c["value"])
    return constraints


async def generate_apply_for_job_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    dataset_dict = await _ensure_entity_dataset(task_url, dataset, entity_type="jobs")
    dataset = dataset_dict.get("jobs", [])

    field_map = {
        "job_title": "title",
    }

    field_operators = FIELD_OPERATORS_APPLY_FOR_JOB_MAP
    all_constraints = _generate_constraints(dataset, field_operators, field_map)

    return all_constraints


async def generate_search_users_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """
    Generates constraints for searching users based on the provided user profile data.
    """
    dataset_dict = await _ensure_entity_dataset(task_url, dataset, entity_type="users")
    dataset = dataset_dict.get("users", [])
    field_operators = FIELD_OPERATORS_SEARCH_USERS_MAP
    field_map = {"query": ["name", "title"]}
    all_constraints = _generate_constraints(dataset, field_operators, field_map)

    return all_constraints


async def generate_search_jobs_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """
    Generates constraints for searching jobs based on the provided job data.
    Replaces raw salary values with predefined filter options if applicable.
    """
    dataset_dict = await _ensure_entity_dataset(task_url, dataset, entity_type="jobs")
    dataset = dataset_dict.get("jobs", [])
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


async def generate_view_job_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """
    Generates constraints for viewing a job based on the provided job data.
    """
    dataset_dict = await _ensure_entity_dataset(task_url, dataset, entity_type="jobs")
    dataset = dataset_dict.get("jobs", [])
    field_operators = FIELD_OPERATORS_VIEW_JOB_MAP
    field_map = {"job_title": "title"}
    all_constraints = _generate_constraints(dataset, field_operators, field_map)

    return all_constraints


async def generate_filter_jobs_constraints() -> list[dict[str, Any]]:
    """
    Generates constraints for filtering jobs based on current filters/result counts.
    """
    constraints_list = []
    filter_options_data = {
        "experience": ["2+ years", "3+ years", "4+ years", "5+ years", "6+ years"],
        "salary": ["0-50000", "50000-75000", "75000-100000", "100000-125000", "125000-150000", "150000+"],
        "location": ["Austin, TX", "Boston, MA", "Chicago, IL", "Denver, CO", "Los Angeles, CA", "New York, NY", "Remote", "Remote (US)", "San Francisco, CA", "Seattle, WA"],
        "remote": [True, False],
    }

    possible_fields = ["experience", "salary", "location", "remote"]
    selected_fields = random.sample(possible_fields, random.randint(1, len(possible_fields)))
    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_FILTER_JOBS_MAP.get(field, [])
        op = ComparisonOperator(random.choice(allowed_ops))
        if field == "experience":
            field_value = random.choice(filter_options_data["experience"])
            value = _generate_constraint_value(op, field_value, field, [{"experience": e} for e in filter_options_data["experience"]])
            constraint = create_constraint_dict(field, op, value)
            constraints_list.append(constraint)
        if field == "salary":
            field_value = random.choice(filter_options_data["salary"])
            value = _generate_constraint_value(op, field_value, field, [{"salary": s} for s in filter_options_data["salary"]])
            constraint = create_constraint_dict(field, op, value)
            constraints_list.append(constraint)
        if field == "remote":
            field_value = random.choice(filter_options_data["remote"])
            value = field_value  # boolean True/False to match web and events.py
            constraint = create_constraint_dict(field, op, value)
            constraints_list.append(constraint)
        if field == "location":
            field_value = random.choice(filter_options_data["location"])
            value = _generate_constraint_value(op, field_value, field, [{"location": e} for e in filter_options_data["location"]])
            constraint = create_constraint_dict(field, op, value)
            constraints_list.append(constraint)

    for constraint in constraints_list:
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

    return constraints_list


async def generate_back_to_all_jobs_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """
    Generates constraints for navigating back to the jobs list.
    """
    constraints_list = []
    dataset_dict = await _ensure_entity_dataset(task_url, dataset, entity_type="jobs")
    dataset = dataset_dict.get("jobs", [])
    if not dataset:
        return constraints_list
    job = random.choice(dataset)
    possible_fields = ["location", "title", "company"]
    selected_fields = random.sample(possible_fields, random.randint(1, len(possible_fields)))
    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_BACK_TO_ALL_JOBS_MAP.get(field, [])
        op = ComparisonOperator(random.choice(allowed_ops))
        if field == "location":
            field_value = job[field]
            value = _generate_constraint_value(op, field_value, field, dataset)
            constraint = create_constraint_dict(field, op, value)
            constraints_list.append(constraint)
        if field == "title":
            field_value = job[field]
            value = _generate_constraint_value(op, field_value, field, dataset)
            constraint = create_constraint_dict(field, op, value)
            constraints_list.append(constraint)
        if field == "company":
            field_value = job[field]
            value = _generate_constraint_value(op, field_value, field, dataset)
            constraint = create_constraint_dict(field, op, value)
            constraints_list.append(constraint)

    return constraints_list


async def generate_save_post_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints_list = []
    dataset_dict = await _ensure_entity_dataset(task_url=task_url, dataset=dataset, entity_type="posts")
    dataset = dataset_dict.get("posts", [])

    transformed_posts = []
    for post in dataset:
        new_post = {}
        for key, value in post.items():
            if key == "user" and isinstance(value, dict):
                # Flatten user fields with prefix
                for u_key, u_value in value.items():
                    new_post[f"user_{u_key}"] = u_value
            else:
                new_post[key] = value
        transformed_posts.append(new_post)

    if not transformed_posts:
        return constraints_list
    post = random.choice(transformed_posts)
    possible_fields = ["author", "content"]
    for field in possible_fields:
        allowed_op = FIELD_OPERATORS_SAVE_POST_MAP.get(field, [])
        op = ComparisonOperator(random.choice(allowed_op))
        if field == "author":
            field_value = post["user_name"]
            value = _generate_constraint_value(op, field_value, field, transformed_posts)
            if value is not None:
                constraint = create_constraint_dict(field, op, value)
                constraints_list.append(constraint)

        if field == "content":
            field_value = post[field]
            value = _generate_constraint_value(op, field_value, field, transformed_posts)
            if value is not None:
                constraint = create_constraint_dict(field, op, value)
                constraints_list.append(constraint)

    return constraints_list


async def generate_cancel_application_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints = await generate_apply_for_job_constraints(task_url, dataset)
    return constraints


async def generate_edit_profile_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraint_list = []
    dataset_dict = await _ensure_entity_dataset(task_url=task_url, dataset=dataset, entity_type="users")
    dataset = dataset_dict.get("users", [])
    if not dataset:
        return constraint_list
    possible_fields = ["name", "bio", "about", "title"]
    selected_fields = random.sample(possible_fields, random.randint(1, len(possible_fields)))
    first_user = dataset[USER_INDEX_FOR_WEB] if len(dataset) > USER_INDEX_FOR_WEB else dataset[0]
    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_EDIT_PROFILE_MAP.get(field, [])
        op = ComparisonOperator(random.choice(allowed_ops))
        if field == "name":
            field_value = first_user[field]
            value = _generate_constraint_value(op, field_value, field, dataset)
            # Single-word value so prompt "include 'X'" matches heuristic (value must appear in prompt)
            if isinstance(value, str) and op == ComparisonOperator.CONTAINS and " " in value:
                value = _single_word_for_contains(value)
            constraint = create_constraint_dict(field, op, value)
            constraint_list.append(constraint)
        if field == "bio":
            field_value = first_user[field]
            value = _generate_constraint_value(op, field_value, field, dataset)
            value = _normalize_constraint_value(value)
            constraint = create_constraint_dict(field, op, value)
            constraint_list.append(constraint)
        if field == "about":
            field_value = first_user[field]
            value = _generate_constraint_value(op, field_value, field, dataset)
            value = _normalize_constraint_value(value)
            constraint = create_constraint_dict(field, op, value)
            constraint_list.append(constraint)
        if field == "title":
            field_value = first_user[field]
            value = _generate_constraint_value(op, field_value, field, dataset)
            constraint = create_constraint_dict(field, op, value)
            constraint_list.append(constraint)

    return constraint_list


def _get_experience_data_for_user(user: dict) -> list[dict[str, Any]]:
    return [
        {
            "title": experience.get("title"),  # will resume here
            "duration": experience.get("duration"),
            "description": experience.get("description"),
            "company": experience.get("company"),
            "location": experience.get("location"),
            "restaurant": user.get("name"),
        }
        for experience in user.get("experience", [])
    ]


async def generate_edit_experience_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraint_list = []
    dataset_dict = await _ensure_entity_dataset(task_url=task_url, dataset=dataset, entity_type="users")
    dataset = dataset_dict.get("users", [])
    if not dataset:
        return constraint_list

    possible_fields = ["company", "duration", "title", "location", "description"]
    # First user with experience (index 0 in filtered list) to align with web implementation
    users_with_experience = [u for u in dataset if (u.get("experience") or []) and len(u.get("experience", [])) > 0]
    if not users_with_experience:
        return constraint_list
    first_user = users_with_experience[USER_INDEX_FOR_WEB] if len(users_with_experience) > USER_INDEX_FOR_WEB else users_with_experience[0]
    experiences = first_user.get("experience", []) or []
    picked_exp = experiences[0] if experiences else None
    if picked_exp is None:
        return constraint_list

    selected_fields = random.sample(possible_fields, random.randint(1, len(possible_fields)))
    for field in selected_fields:
        field_value = picked_exp.get(field)
        if field_value is None:
            continue
        allowed_ops = FIELD_OPERATORS_EDIT_EXPERIENCE_MAP.get(field, [])
        if not allowed_ops:
            continue
        op = ComparisonOperator(random.choice(allowed_ops))
        value = _generate_constraint_value(op, field_value, field, dataset)
        if value is None:
            continue
        if field == "description" and isinstance(value, str):
            value = _normalize_constraint_value(value)
        constraint = create_constraint_dict(field, op, value)
        constraint_list.append(constraint)

    return constraint_list


async def generate_remove_post_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints = await generate_save_post_constraints(task_url, dataset)
    return constraints


async def generate_unhide_post_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints = await generate_save_post_constraints(task_url, dataset)
    return constraints


async def generate_add_experience_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraint_list = []
    dataset_dict = await _ensure_entity_dataset(task_url=task_url, dataset=dataset, entity_type="users")
    dataset = dataset_dict.get("users", [])
    if not dataset:
        return constraint_list
    possible_fields = ["company", "duration", "title", "location", "description"]
    first_user = dataset[USER_INDEX_FOR_WEB] if len(dataset) > USER_INDEX_FOR_WEB else dataset[0]
    experiences = first_user.get("experience", []) or []
    picked_exp = experiences[0] if experiences else None
    if picked_exp is None:
        return constraint_list

    for field in possible_fields:
        field_value = picked_exp.get(field)
        if field_value is None:
            continue
        allowed_ops = FIELD_OPERATORS_EDIT_EXPERIENCE_MAP.get(field, [])
        if not allowed_ops:
            continue
        op = ComparisonOperator(random.choice(allowed_ops))
        value = _generate_constraint_value(op, field_value, field, dataset)
        if value is None:
            continue
        # Strip duration so prompt text "Present •" matches (heuristic); cap long description
        if field == "duration" and isinstance(value, str):
            value = value.strip()
        if field == "description" and isinstance(value, str):
            value = _normalize_constraint_value(value)
        constraint = create_constraint_dict(field, op, value)
        constraint_list.append(constraint)

    return constraint_list
