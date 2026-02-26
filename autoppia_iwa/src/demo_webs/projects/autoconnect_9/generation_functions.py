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


# =============================================================================
#                            HELPER FUNCTIONS
# =============================================================================

# --------------------------------------------------------------------- #
#  CONSTRAINT VALUE GENERATION HELPERS
# ---------------------------------------------------------------------


def _handle_datetime_constraint(operator: ComparisonOperator, field_value: datetime) -> datetime:
    """Handle datetime constraint value generation."""
    delta_days = random.randint(1, 5)
    if operator == ComparisonOperator.GREATER_THAN:
        return field_value - timedelta(days=delta_days)
    if operator == ComparisonOperator.LESS_THAN:
        return field_value + timedelta(days=delta_days)
    if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL, ComparisonOperator.EQUALS}:
        return field_value
    if operator == ComparisonOperator.NOT_EQUALS:
        return field_value + timedelta(days=delta_days + 1)
    return field_value


def _handle_not_equals_string(field_value: str, field: str, dataset: list[dict[str, Any]]) -> Any:
    """Handle NOT_EQUALS operator for string values."""
    valid = [v[field] for v in dataset if v.get(field) and v.get(field) != field_value]
    return random.choice(valid) if valid else None


def _handle_not_equals_list(field_value: list, dataset: list[dict[str, Any]]) -> Any:
    """Handle NOT_EQUALS operator for list values."""
    valid = [v[f] for v in dataset for f in field_value if v.get(f) and v.get(f) != field_value]
    return random.choice(valid) if valid else None


def _handle_not_equals_operator(field_value: Any, field: str, dataset: list[dict[str, Any]]) -> Any:
    """Handle NOT_EQUALS operator."""
    if isinstance(field_value, str):
        return _handle_not_equals_string(field_value, field, dataset)
    if isinstance(field_value, list):
        return _handle_not_equals_list(field_value, dataset)
    return None


def _handle_contains_string(field_value: str) -> str:
    """Handle CONTAINS operator for string values."""
    if len(field_value) > 2:
        start = random.randint(0, max(0, len(field_value) - 2))
        end = random.randint(start + 1, len(field_value))
        return field_value[start:end]
    return field_value


def _handle_not_contains_string(field_value: str) -> str:
    """Handle NOT_CONTAINS operator for string values."""
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    while True:
        test_str = "".join(random.choice(alphabet) for _ in range(3))
        if test_str.lower() not in field_value.lower():
            return test_str


def _extract_all_field_values(field: str, dataset: list[dict[str, Any]]) -> list[Any]:
    """Extract all values for a field from dataset, handling lists."""
    all_values = []
    for v in dataset:
        if field in v:
            val = v.get(field)
            if isinstance(val, list):
                all_values.extend(val)
            elif val is not None:
                all_values.append(val)
    return list(set(all_values))


def _handle_in_list_operator(field_value: Any, field: str, dataset: list[dict[str, Any]]) -> list[Any]:
    """Handle IN_LIST operator."""
    all_values = _extract_all_field_values(field, dataset)
    if not all_values:
        return [field_value]
    random.shuffle(all_values)
    subset = random.sample(all_values, min(2, len(all_values)))
    if field_value not in subset:
        subset.append(field_value)
    return list(set(subset))


def _handle_not_in_list_operator(field_value: Any, field: str, dataset: list[dict[str, Any]]) -> list[Any]:
    """Handle NOT_IN_LIST operator."""
    all_values = _extract_all_field_values(field, dataset)
    if field_value in all_values:
        all_values.remove(field_value)
    return random.sample(all_values, min(2, len(all_values))) if all_values else []


def _handle_numeric_comparison(operator: ComparisonOperator, field: str, dataset: list[dict[str, Any]]) -> float | None:
    """Handle numeric comparison operators."""
    numeric_values = [v.get(field) for v in dataset if isinstance(v.get(field), int | float)]
    if not numeric_values:
        return None
    base = random.choice(numeric_values)
    delta = random.uniform(1, 3)
    if operator == ComparisonOperator.GREATER_THAN:
        return round(base - delta, 2)
    if operator == ComparisonOperator.LESS_THAN:
        return round(base + delta, 2)
    if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
        return round(base, 2)
    return None


def _generate_constraint_value(operator: ComparisonOperator, field_value: Any, field: str, dataset: list[dict[str, Any]]) -> Any:
    """Generate a constraint value for a given operator, field, and dataset."""
    # Handle datetime comparisons
    if isinstance(field_value, datetime):
        return _handle_datetime_constraint(operator, field_value)

    if operator == ComparisonOperator.EQUALS:
        return field_value

    if operator == ComparisonOperator.NOT_EQUALS:
        return _handle_not_equals_operator(field_value, field, dataset)

    if operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        return _handle_contains_string(field_value)

    if operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        return _handle_not_contains_string(field_value)

    if operator == ComparisonOperator.IN_LIST:
        return _handle_in_list_operator(field_value, field, dataset)

    if operator == ComparisonOperator.NOT_IN_LIST:
        return _handle_not_in_list_operator(field_value, field, dataset)

    if operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    }:
        return _handle_numeric_comparison(operator, field, dataset)

    return None


# --------------------------------------------------------------------- #
#  CONSTRAINT GENERATION HELPERS
# ---------------------------------------------------------------------


def _select_sample_data(dataset: list[dict], use_first_sample: bool, sample_index: int | None) -> dict:
    """Select sample data from dataset based on parameters."""
    if sample_index is not None and len(dataset) > sample_index:
        return dataset[sample_index]
    if use_first_sample:
        return dataset[0]
    return choice(dataset)


def _select_possible_fields(field_operators: dict, selected_fields: list | None) -> tuple[list, list]:
    """Select and filter possible fields."""
    possible_fields = list(field_operators.keys())
    if selected_fields:
        possible_fields = [f for f in possible_fields if f not in selected_fields]
        return possible_fields, selected_fields
    return possible_fields, []


def _get_field_value_from_mapping(new_field: Any, sample_data: dict) -> tuple[Any, str | None]:
    """Get field value from field mapping, handling lists and nested fields."""
    if isinstance(new_field, list):
        random.shuffle(new_field)
        for f in new_field:
            field_value = sample_data.get(f)
            if field_value is not None:
                return field_value, f
        return None, None
    
    if "." in new_field:
        # Handle nested fields
        field_value = _get_nested_value(sample_data, new_field)
        return field_value, new_field if field_value is not None else None
    
    field_value = sample_data.get(new_field)
    return field_value, new_field


def _process_field_constraint(
    field: str,
    field_operators: dict,
    field_map: dict,
    sample_data: dict,
    dataset: list[dict],
) -> dict[str, Any] | None:
    """Process a single field constraint."""
    allowed_ops = field_operators.get(field, [])
    if not allowed_ops:
        return None
    
    op = ComparisonOperator(choice(allowed_ops))
    new_field = field_map.get(field, field)
    
    field_value, resolved_field = _get_field_value_from_mapping(new_field, sample_data)
    if field_value is None or resolved_field is None:
        return None
    
    # Generate a constraint value based on the operator and field value
    constraint_value = _generate_constraint_value(op, field_value, resolved_field, dataset)
    if constraint_value is not None:
        return create_constraint_dict(field, op, constraint_value)
    return None


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
    if not dataset:
        print("[ERROR] No dataset provided")
        return []
    
    sample_data = _select_sample_data(dataset, use_first_sample, sample_index)
    possible_fields, initial_selected = _select_possible_fields(field_operators, selected_fields)
    
    if num_constraints is None:
        num_constraints = random.randint(1, len(possible_fields))
    
    final_selected_fields = initial_selected + random.sample(possible_fields, num_constraints)
    
    if field_map is None:
        field_map = {}
    
    all_constraints = []
    for field in final_selected_fields:
        constraint = _process_field_constraint(field, field_operators, field_map, sample_data, dataset)
        if constraint:
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


# --------------------------------------------------------------------- #
#  SALARY PROCESSING HELPERS
# ---------------------------------------------------------------------


def _extract_min_salary(raw_value: str) -> int | None:
    """Extract minimum salary from raw value string."""
    cleaned = raw_value.replace("$", "").replace(",", "").strip()
    if "-" in cleaned:
        parts = cleaned.split("-")
        try:
            return int(parts[0])
        except ValueError:
            return None
    if "+" in cleaned:
        parts = cleaned.split("+")
        try:
            return int(parts[0])
        except ValueError:
            return None
    try:
        return int(cleaned)
    except ValueError:
        return None


def _map_salary_to_filter_option(min_salary: int, salary_options: list[str]) -> str | None:
    """Map minimum salary to a filter option."""
    for option in salary_options:
        if "-" in option:
            start, end = map(int, option.split("-"))
            if start <= min_salary <= end:
                return option
        elif "+" in option:
            base = int(option.replace("+", ""))
            if min_salary >= base:
                return option
    return None


def _normalize_salary_constraint(constraint: dict[str, Any], salary_options: list[str]) -> None:
    """Normalize salary constraint value to match filter options."""
    if constraint["field"] != "salary":
        return
    raw_value = str(constraint["value"])
    min_salary = _extract_min_salary(raw_value)
    if min_salary is not None:
        mapped_option = _map_salary_to_filter_option(min_salary, salary_options)
        if mapped_option:
            constraint["value"] = mapped_option


# --------------------------------------------------------------------- #
#  CONSTANTS
# ---------------------------------------------------------------------

# User index used by the web for profile/experience use cases (0-based).
USER_INDEX_FOR_WEB = 2

# Filter options data for jobs
FILTER_OPTIONS_DATA = {
    "experience": ["2+ years", "3+ years", "4+ years", "5+ years", "6+ years"],
    "salary": ["0-50000", "50000-75000", "75000-100000", "100000-125000", "125000-150000", "150000+"],
    "location": ["Austin, TX", "Boston, MA", "Chicago, IL", "Denver, CO", "Los Angeles, CA", "New York, NY", "Remote", "Remote (US)", "San Francisco, CA", "Seattle, WA"],
    "remote": [True, False],
}


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


# =============================================================================
#                            DATA FETCHING HELPERS
# =============================================================================


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


# =============================================================================
#                            PUBLIC FUNCTIONS
# =============================================================================

# --------------------------------------------------------------------- #
#  USER PROFILE CONSTRAINTS
# ---------------------------------------------------------------------


async def generate_view_user_profile_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """
    Generates constraints for viewing a user profile based on the provided user profile data.
    Uses first user (index 0) to align with web implementation.
    """
    dataset_dict = await _ensure_entity_dataset(task_url, entity_type="users")
    users_data = dataset_dict.get("users", [])
    field_operators = FIELD_OPERATORS_VIEW_USER_PROFILE_MAP
    all_constraints = _generate_constraints(users_data, field_operators, num_constraints=1, sample_index=USER_INDEX_FOR_WEB)
    return all_constraints


async def generate_connect_with_user_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    users_dict = await _ensure_entity_dataset(task_url, entity_type="users")
    users = users_dict.get("users", [])
    filtered_users = [u for u in users if u.get("username") != "alexsmith"]

    field_operators = FIELD_OPERATORS_CONNECT_WITH_USER_MAP
    field_map = {
        "target_name": "name",
    }
    all_constraints = _generate_constraints(filtered_users, field_operators, field_map, num_constraints=1)
    return all_constraints


# --------------------------------------------------------------------- #
#  POST CONSTRAINTS
# ---------------------------------------------------------------------


async def generate_like_post_constraints(task_url: str | None = None):
    """
    Generates constraints for liking a post based on the provided post data.
    """
    dataset_dict = await _ensure_entity_dataset(task_url, entity_type="posts")
    posts_data = dataset_dict.get("posts", [])
    field_operators = FIELD_OPERATORS_LIKE_POST_MAP
    field_map = {"poster_content": "content", "poster_name": "name"}

    all_constraints = _generate_constraints(posts_data, field_operators, field_map)
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


async def generate_comment_on_post_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """
    Generates constraints for commenting on a post based on the provided post data.
    """
    fixed_field = "comment_text"
    sample_comments = [{fixed_field: comment} for comment in SAMPLE_COMMENTS]
    field_operators = FIELD_OPERATORS_COMMENT_ON_POST_MAP.copy()

    operators = field_operators.pop(fixed_field)
    new_field_operators = {fixed_field: operators}
    all_constraints = _generate_constraints(sample_comments, new_field_operators)

    dataset_dict = await _ensure_entity_dataset(task_url, entity_type="posts")
    posts_data = dataset_dict.get("posts", [])
    field_map = {"poster_content": "content", "poster_name": "name"}
    constraints = _generate_constraints(posts_data, field_operators, field_map)
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


def generate_post_status_constraints() -> list[dict[str, Any]]:
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


async def generate_follow_page_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """
    Generates constraints for following a company page based on the provided user profile data.
    """

    dataset_dict = await _ensure_entity_dataset(task_url, entity_type="recommendations")
    recommendations_data = dataset_dict.get("recommendations", [])
    field_operators = FIELD_OPERATORS_FOLLOW_PAGE_MAP
    field_map = {"recommendation": "title"}
    all_constraints = _generate_constraints(recommendations_data, field_operators, field_map)

    return all_constraints


async def generate_unfollow_page_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """
    Generates constraints for unfollowing a company page.
    """
    constraints = await generate_follow_page_constraints(task_url)
    # Single-token value so prompt "containing 'X'" matches heuristic (value must appear in prompt)
    for c in constraints:
        if c.get("field") == "recommendation" and c.get("operator") == "contains" and isinstance(c.get("value"), str) and " " in c["value"]:
            c["value"] = _single_word_for_contains(c["value"])
    return constraints


# --------------------------------------------------------------------- #
#  JOB CONSTRAINTS
# ---------------------------------------------------------------------


async def generate_apply_for_job_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    dataset_dict = await _ensure_entity_dataset(task_url, entity_type="jobs")
    jobs_data = dataset_dict.get("jobs", [])

    field_map = {
        "job_title": "title",
    }

    field_operators = FIELD_OPERATORS_APPLY_FOR_JOB_MAP
    all_constraints = _generate_constraints(jobs_data, field_operators, field_map)

    return all_constraints


async def generate_search_users_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """
    Generates constraints for searching users based on the provided user profile data.
    """
    dataset_dict = await _ensure_entity_dataset(task_url, entity_type="users")
    users_data = dataset_dict.get("users", [])
    field_operators = FIELD_OPERATORS_SEARCH_USERS_MAP
    field_map = {"query": ["name", "title"]}
    all_constraints = _generate_constraints(users_data, field_operators, field_map)

    return all_constraints


async def generate_search_jobs_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """
    Generates constraints for searching jobs based on the provided job data.
    Replaces raw salary values with predefined filter options if applicable.
    """
    dataset_dict = await _ensure_entity_dataset(task_url, entity_type="jobs")
    jobs_data = dataset_dict.get("jobs", [])
    field_operators = FIELD_OPERATORS_SEARCH_JOBS_MAP
    field_map = {"query": ["title", "company"]}

    all_constraints = _generate_constraints(jobs_data, field_operators, field_map)

    for constraint in all_constraints:
        _normalize_salary_constraint(constraint, FILTER_OPTIONS_DATA["salary"])

    return all_constraints


async def generate_view_job_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """
    Generates constraints for viewing a job based on the provided job data.
    """
    dataset_dict = await _ensure_entity_dataset(task_url, entity_type="jobs")
    jobs_data = dataset_dict.get("jobs", [])
    field_operators = FIELD_OPERATORS_VIEW_JOB_MAP
    field_map = {"job_title": "title"}
    all_constraints = _generate_constraints(jobs_data, field_operators, field_map)

    return all_constraints


# --------------------------------------------------------------------- #
#  FILTER JOBS HELPERS
# ---------------------------------------------------------------------


def _generate_filter_field_constraint(field: str, filter_options_data: dict[str, Any]) -> dict[str, Any] | None:
    """Generate constraint for a single filter field."""
    allowed_ops = FIELD_OPERATORS_FILTER_JOBS_MAP.get(field, [])
    if not allowed_ops:
        return None
    
    op = ComparisonOperator(random.choice(allowed_ops))
    field_value = random.choice(filter_options_data[field])
    
    if field == "remote":
        # boolean True/False to match web and events.py
        value = field_value
    else:
        dataset = [{field: val} for val in filter_options_data[field]]
        value = _generate_constraint_value(op, field_value, field, dataset)
    
    return create_constraint_dict(field, op, value)


def generate_filter_jobs_constraints() -> list[dict[str, Any]]:
    """
    Generates constraints for filtering jobs based on current filters/result counts.
    """
    possible_fields = ["experience", "salary", "location", "remote"]
    selected_fields = random.sample(possible_fields, random.randint(1, len(possible_fields)))
    
    constraints_list = []
    for field in selected_fields:
        constraint = _generate_filter_field_constraint(field, FILTER_OPTIONS_DATA)
        if constraint:
            constraints_list.append(constraint)
    
    # Normalize salary constraints
    for constraint in constraints_list:
        _normalize_salary_constraint(constraint, FILTER_OPTIONS_DATA["salary"])
    
    return constraints_list


# --------------------------------------------------------------------- #
#  BACK TO ALL JOBS HELPERS
# ---------------------------------------------------------------------


def _generate_back_to_jobs_field_constraint(field: str, job: dict, dataset: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Generate constraint for a single field in back to all jobs."""
    allowed_ops = FIELD_OPERATORS_BACK_TO_ALL_JOBS_MAP.get(field, [])
    if not allowed_ops:
        return None
    
    op = ComparisonOperator(random.choice(allowed_ops))
    field_value = job[field]
    value = _generate_constraint_value(op, field_value, field, dataset)
    if value is not None:
        return create_constraint_dict(field, op, value)
    return None


async def generate_back_to_all_jobs_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """
    Generates constraints for navigating back to the jobs list.
    """
    dataset_dict = await _ensure_entity_dataset(task_url, entity_type="jobs")
    jobs_data = dataset_dict.get("jobs", [])
    if not jobs_data:
        return []
    
    job = random.choice(jobs_data)
    possible_fields = ["location", "title", "company"]
    selected_fields = random.sample(possible_fields, random.randint(1, len(possible_fields)))
    
    constraints_list = []
    for field in selected_fields:
        constraint = _generate_back_to_jobs_field_constraint(field, job, jobs_data)
        if constraint:
            constraints_list.append(constraint)
    
    return constraints_list


# --------------------------------------------------------------------- #
#  SAVE POST HELPERS
# ---------------------------------------------------------------------


def _transform_post_data(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Transform posts by flattening user fields with prefix."""
    transformed_posts = []
    for post in posts:
        new_post = {}
        for key, value in post.items():
            if key == "user" and isinstance(value, dict):
                # Flatten user fields with prefix
                for u_key, u_value in value.items():
                    new_post[f"user_{u_key}"] = u_value
            else:
                new_post[key] = value
        transformed_posts.append(new_post)
    return transformed_posts


def _generate_save_post_field_constraint(field: str, post: dict, transformed_posts: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Generate constraint for a single field in save post."""
    allowed_op = FIELD_OPERATORS_SAVE_POST_MAP.get(field, [])
    if not allowed_op:
        return None
    
    op = ComparisonOperator(random.choice(allowed_op))
    
    if field == "author":
        field_value = post["user_name"]
    else:
        field_value = post[field]
    
    value = _generate_constraint_value(op, field_value, field, transformed_posts)
    if value is not None:
        return create_constraint_dict(field, op, value)
    return None


async def generate_save_post_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    dataset_dict = await _ensure_entity_dataset(task_url=task_url, entity_type="posts")
    posts_data = dataset_dict.get("posts", [])
    
    transformed_posts = _transform_post_data(posts_data)
    if not transformed_posts:
        return []
    
    post = random.choice(transformed_posts)
    possible_fields = ["author", "content"]
    
    constraints_list = []
    for field in possible_fields:
        constraint = _generate_save_post_field_constraint(field, post, transformed_posts)
        if constraint:
            constraints_list.append(constraint)
    
    return constraints_list


async def generate_cancel_application_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    constraints = await generate_apply_for_job_constraints(task_url)
    return constraints


# --------------------------------------------------------------------- #
#  PROFILE/EXPERIENCE CONSTRAINTS
# ---------------------------------------------------------------------


def _process_profile_field_constraint(field: str, field_value: Any, op: ComparisonOperator, dataset: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Process a single profile field constraint with appropriate normalization."""
    value = _generate_constraint_value(op, field_value, field, dataset)
    if value is None:
        return None
    
    # Apply field-specific normalization
    if field == "name" and isinstance(value, str) and op == ComparisonOperator.CONTAINS and " " in value:
        # Single-word value so prompt "include 'X'" matches heuristic
        value = _single_word_for_contains(value)
    elif field in ["bio", "about"]:
        value = _normalize_constraint_value(value)
    
    return create_constraint_dict(field, op, value)


async def generate_edit_profile_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    dataset_dict = await _ensure_entity_dataset(task_url=task_url, entity_type="users")
    users_data = dataset_dict.get("users", [])
    if not users_data:
        return []
    
    possible_fields = ["name", "bio", "about", "title"]
    selected_fields = random.sample(possible_fields, random.randint(1, len(possible_fields)))
    first_user = users_data[USER_INDEX_FOR_WEB] if len(users_data) > USER_INDEX_FOR_WEB else users_data[0]
    
    constraint_list = []
    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_EDIT_PROFILE_MAP.get(field, [])
        if not allowed_ops:
            continue
        
        op = ComparisonOperator(random.choice(allowed_ops))
        field_value = first_user[field]
        constraint = _process_profile_field_constraint(field, field_value, op, users_data)
        if constraint:
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


# --------------------------------------------------------------------- #
#  EXPERIENCE HELPERS
# ---------------------------------------------------------------------


def _get_user_with_experience(dataset: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Get first user with experience from dataset."""
    users_with_experience = [u for u in dataset if (u.get("experience") or []) and len(u.get("experience", [])) > 0]
    if not users_with_experience:
        return None
    return users_with_experience[USER_INDEX_FOR_WEB] if len(users_with_experience) > USER_INDEX_FOR_WEB else users_with_experience[0]


def _get_first_experience(user: dict[str, Any]) -> dict[str, Any] | None:
    """Get first experience from user."""
    experiences = user.get("experience", []) or []
    return experiences[0] if experiences else None


def _process_experience_field_constraint(
    field: str,
    field_value: Any,
    op: ComparisonOperator,
    dataset: list[dict[str, Any]],
    normalize_duration: bool = False,
) -> dict[str, Any] | None:
    """Process a single experience field constraint with appropriate normalization."""
    value = _generate_constraint_value(op, field_value, field, dataset)
    if value is None:
        return None
    
    # Apply field-specific normalization
    if field == "duration" and isinstance(value, str) and normalize_duration:
        value = value.strip()
    elif field == "description" and isinstance(value, str):
        value = _normalize_constraint_value(value)
    
    return create_constraint_dict(field, op, value)


async def generate_edit_experience_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    dataset_dict = await _ensure_entity_dataset(task_url=task_url, entity_type="users")
    users_data = dataset_dict.get("users", [])
    if not users_data:
        return []
    
    first_user = _get_user_with_experience(users_data)
    if not first_user:
        return []
    
    picked_exp = _get_first_experience(first_user)
    if not picked_exp:
        return []
    
    possible_fields = ["company", "duration", "title", "location", "description"]
    selected_fields = random.sample(possible_fields, random.randint(1, len(possible_fields)))
    
    constraint_list = []
    for field in selected_fields:
        field_value = picked_exp.get(field)
        if field_value is None:
            continue
        
        allowed_ops = FIELD_OPERATORS_EDIT_EXPERIENCE_MAP.get(field, [])
        if not allowed_ops:
            continue
        
        op = ComparisonOperator(random.choice(allowed_ops))
        constraint = _process_experience_field_constraint(field, field_value, op, users_data, normalize_duration=False)
        if constraint:
            constraint_list.append(constraint)
    
    return constraint_list


async def generate_remove_post_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    constraints = await generate_save_post_constraints(task_url)
    return constraints


async def generate_unhide_post_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    constraints = await generate_save_post_constraints(task_url)
    return constraints


async def generate_add_experience_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    dataset_dict = await _ensure_entity_dataset(task_url=task_url, entity_type="users")
    users_data = dataset_dict.get("users", [])
    if not users_data:
        return []
    
    first_user = users_data[USER_INDEX_FOR_WEB] if len(users_data) > USER_INDEX_FOR_WEB else users_data[0]
    picked_exp = _get_first_experience(first_user)
    if not picked_exp:
        return []
    
    possible_fields = ["company", "duration", "title", "location", "description"]
    
    constraint_list = []
    for field in possible_fields:
        field_value = picked_exp.get(field)
        if field_value is None:
            continue
        
        allowed_ops = FIELD_OPERATORS_EDIT_EXPERIENCE_MAP.get(field, [])
        if not allowed_ops:
            continue
        
        op = ComparisonOperator(random.choice(allowed_ops))
        # Strip duration so prompt text "Present •" matches (heuristic)
        constraint = _process_experience_field_constraint(field, field_value, op, users_data, normalize_duration=True)
        if constraint:
            constraint_list.append(constraint)
    
    return constraint_list
