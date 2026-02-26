# autoppia_iwa/src/demo_webs/projects/autolist_12/generation_functions.py
import random
from datetime import date, datetime, timedelta
from typing import Any

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url
from autoppia_iwa.src.demo_webs.projects.shared_utils import create_constraint_dict

from .data import (
    DATES_QUICK_OPTIONS,
    FIELD_OPERATORS_SELECT_DATE_MAP,
    FIELD_OPERATORS_SELECT_PRIORITY_MAP,
    FIELD_OPERATORS_TASK_MAP,
    FIELD_OPERATORS_TEAM_CREATED_MAP,
    FIELD_OPERATORS_TEAM_MEMBERS_ADDED_MAP,
    FIELD_OPERATORS_TEAM_ROLE_ASSIGNED_MAP,
    PRIORITIES,
    ROLES,
    TEAM_MEMBERS_OPTIONS,
    TEAMS,
)
from .data_utils import fetch_data

# ============================================================================
# DATA FETCHING HELPERS
# ============================================================================
async def _ensure_task_dataset(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """Extract tasks data from the pre-loaded dataset, or fetch from server if not available."""
    # Fetch data if dataset is not provided or is empty
    if dataset is None or dataset == {}:
        seed = get_seed_from_url(task_url)
        tasks = await fetch_data(seed_value=seed)
        dataset = {"tasks": tasks}

    if dataset and "tasks" in dataset:
        return dataset["tasks"]
    return []


# ============================================================================
# CONSTRAINT VALUE GENERATION HELPERS
# ============================================================================
def _handle_datetime_constraint(operator: ComparisonOperator, field_value: datetime | date) -> datetime | date:
    """Handle constraint value generation for datetime/date types."""
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


def _handle_equals_operator(field_value: Any) -> Any:
    """Handle EQUALS operator."""
    return field_value


def _handle_not_equals_operator(field_value: Any, source_key: str, dataset: list[dict[str, Any]]) -> Any:
    """Handle NOT_EQUALS operator."""
    valid = [v[source_key] for v in dataset if v.get(source_key) and v.get(source_key) != field_value]
    return random.choice(valid) if valid else None


def _handle_contains_operator(field_value: str) -> str:
    """Handle CONTAINS operator for strings."""
    longest = max(field_value.split(), key=len)
    random_picker_start = random.randint(0, len(longest) - 1)

    if random_picker_start == len(longest) - 1:
        return longest[random_picker_start]  # just return last char
    random_picker_end = random.randint(random_picker_start + 1, len(longest))
    return longest[random_picker_start:random_picker_end]


def _handle_not_contains_operator(field_value: str) -> str:
    """Handle NOT_CONTAINS operator for strings."""
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for _ in range(100):
        test_str = "".join(random.choice(alphabet) for _ in range(3))
        if test_str.lower() not in field_value.lower():
            return test_str
    return "xyz"  # fallback


def _extract_all_values_from_dataset(source_key: str, dataset: list[dict[str, Any]]) -> list[Any]:
    """Extract all values for a given source_key from dataset, handling lists."""
    all_values = []
    for v in dataset:
        if source_key in v:
            val = v.get(source_key)
            if isinstance(val, list):
                all_values.extend(val)
            elif val is not None:
                all_values.append(val)
    return list(set(all_values))


def _handle_in_list_operator(field_value: Any, source_key: str, dataset: list[dict[str, Any]]) -> list[Any]:
    """Handle IN_LIST operator."""
    all_values = _extract_all_values_from_dataset(source_key, dataset)

    if not all_values:
        return [field_value]
    random.shuffle(all_values)
    subset = random.sample(all_values, min(2, len(all_values)))
    if field_value not in subset:
        subset.append(field_value)
    return list(set(subset))


def _handle_not_in_list_operator(field_value: Any, source_key: str, dataset: list[dict[str, Any]]) -> list[Any]:
    """Handle NOT_IN_LIST operator."""
    all_values = _extract_all_values_from_dataset(source_key, dataset)

    if field_value in all_values:
        all_values.remove(field_value)
    return random.sample(all_values, min(2, len(all_values))) if all_values else []


def _handle_numeric_comparison(operator: ComparisonOperator, field_value: int | float) -> int | float | None:
    """Handle numeric comparison operators."""
    delta = random.uniform(0.5, 2.0) if isinstance(field_value, float) else random.randint(1, 5)
    if operator == ComparisonOperator.GREATER_THAN:
        return field_value - delta
    if operator == ComparisonOperator.LESS_THAN:
        return field_value + delta
    if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
        return field_value
    return None


def _generate_constraint_value(operator: ComparisonOperator, field_value: Any, source_key: str, dataset: list[dict[str, Any]]) -> Any:
    """
    Generate a constraint value for a given operator, field, and dataset.
    """
    if isinstance(field_value, datetime | date):
        return _handle_datetime_constraint(operator, field_value)

    if operator == ComparisonOperator.EQUALS:
        return _handle_equals_operator(field_value)

    if operator == ComparisonOperator.NOT_EQUALS:
        return _handle_not_equals_operator(field_value, source_key, dataset)

    if operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        return _handle_contains_operator(field_value)

    if operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        return _handle_not_contains_operator(field_value)

    if operator == ComparisonOperator.IN_LIST:
        return _handle_in_list_operator(field_value, source_key, dataset)

    if operator == ComparisonOperator.NOT_IN_LIST:
        return _handle_not_in_list_operator(field_value, source_key, dataset)

    if isinstance(field_value, int | float):
        return _handle_numeric_comparison(operator, field_value)

    return None


# ============================================================================
# CONSTRAINT GENERATION HELPERS
# ============================================================================
def _calculate_date_range() -> tuple[datetime, int]:
    """Calculate date range for the current month."""
    today = datetime.today()
    start_of_month = today.replace(day=1)
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    days_in_month = (next_month - start_of_month).days
    return start_of_month, days_in_month


def _generate_random_date_in_month(start_of_month: datetime, days_in_month: int) -> datetime:
    """Generate a random date within the current month."""
    random_day = random.randint(1, days_in_month)
    return start_of_month + timedelta(days=random_day - 1)


def _adjust_date_for_operator(field_value: datetime, operator: ComparisonOperator, days_in_month: int) -> datetime:
    """Adjust date value based on comparison operator."""
    if operator == ComparisonOperator.GREATER_THAN:
        if field_value.day == days_in_month:
            return field_value - timedelta(days=5)
        min_day = min(field_value.day + 1, days_in_month)
        return field_value.replace(day=min_day)

    if operator == ComparisonOperator.LESS_THAN:
        if field_value.day == 1:
            return field_value + timedelta(days=5)
        max_day = max(field_value.day - 1, 1)
        return field_value.replace(day=max_day)

    if operator == ComparisonOperator.NOT_EQUALS:
        alt_day = field_value.day + 1 if field_value.day < days_in_month else field_value.day - 1
        return field_value.replace(day=alt_day)

    return field_value


def _process_date_field(operator: ComparisonOperator) -> date:
    """Process date field configuration and generate appropriate date value."""
    start_of_month, days_in_month = _calculate_date_range()
    field_value = _generate_random_date_in_month(start_of_month, days_in_month)
    field_value = _adjust_date_for_operator(field_value, operator, days_in_month)
    return field_value.date()


def _get_field_value_from_config(config: dict[str, Any], sample_data: dict[str, Any], source_key: str) -> Any:
    """Get field value from configuration, dataset, or random choice."""
    dataset = config.get("dataset", [])
    if dataset and all(not isinstance(item, dict) for item in dataset):
        dataset = [{source_key: item} for item in dataset]

    field_value = sample_data.get(source_key) or (random.choice(dataset)[source_key] if dataset else None)

    if field_value is None and "values" in config:
        field_value = random.choice(config["values"])

    return field_value


def _process_field_constraint(field: str, config: dict[str, Any], operators_map: dict[str, list], sample_data: dict[str, Any]) -> dict[str, Any] | None:
    """Process a single field constraint and return constraint dict if valid."""
    operator = ComparisonOperator(random.choice(operators_map[field]))
    source_key = config.get("source_key", field)
    dataset = config.get("dataset", [])

    if config.get("is_date"):
        value = _process_date_field(operator)
    else:
        field_value = _get_field_value_from_config(config, sample_data, source_key)
        if field_value is None:
            return None
        value = _generate_constraint_value(operator, field_value, source_key, dataset)

    if value:
        return create_constraint_dict(field, operator, value)
    return None


def _generate_constraints_for_event(field_map: dict[str, dict[str, Any]], operators_map: dict[str, list]) -> list[dict[str, Any]]:
    """Generic function to generate constraints based on a field map."""
    constraints_list = []
    sample_data = random.choice(field_map.get("_dataset", [{}]))

    for field, config in field_map.items():
        if field == "_dataset":
            continue

        constraint = _process_field_constraint(field, config, operators_map, sample_data)
        if constraint:
            constraints_list.append(constraint)

    return constraints_list


# ============================================================================
# CONSTRAINT GENERATION FUNCTIONS
# ============================================================================
# TASK CONSTRAINTS
async def generate_select_date_for_task_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Generate constraints for selecting a date for a task."""
    dataset = await _ensure_task_dataset(task_url, dataset)
    field_map = {"_dataset": dataset, "date": {"is_date": True}} if random.choice([True, False]) else {"_dataset": dataset, "quick_option": {"values": DATES_QUICK_OPTIONS}}
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_SELECT_DATE_MAP)


def generate_select_task_priority_constraints() -> list[dict[str, Any]]:
    """Generate constraints for selecting a task priority."""
    field_map = {
        "priority": {"dataset": PRIORITIES},
    }
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_SELECT_PRIORITY_MAP)


async def generate_task_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Generate constraints for adding or updating a task."""
    dataset = await _ensure_task_dataset(task_url, dataset)
    field_map = {
        "_dataset": dataset,
        "name": {"dataset": dataset},
        "description": {"dataset": dataset},
        "date": {"is_date": True},
        "priority": {"dataset": PRIORITIES},
    }
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_TASK_MAP)


# TEAM CONSTRAINTS
def generate_team_members_added_constraints() -> list[dict[str, Any]]:
    """Generate constraints for adding team members, including member_count and members."""
    num_members = random.randint(1, 3)
    selected_members = random.sample([m["label"] for m in TEAM_MEMBERS_OPTIONS], k=num_members)
    constraints_list = []

    operator = ComparisonOperator(random.choice(FIELD_OPERATORS_TEAM_MEMBERS_ADDED_MAP["members"]))
    constraints_list.append(create_constraint_dict("members", operator, selected_members))

    count_operator = ComparisonOperator(random.choice(FIELD_OPERATORS_TEAM_MEMBERS_ADDED_MAP["member_count"]))
    constraints_list.append(create_constraint_dict("member_count", count_operator, num_members))

    return constraints_list


def generate_team_role_assigned_constraints() -> list[dict[str, Any]]:
    """Generate constraints for assigning a role to a team member."""
    field_map = {
        "_dataset": TEAMS,
        "member": {"source_key": "label", "dataset": TEAM_MEMBERS_OPTIONS},
        "role": {"source_key": "label", "dataset": ROLES},
    }
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_TEAM_ROLE_ASSIGNED_MAP)


def generate_team_created_constraints() -> list[dict[str, Any]]:
    """Generate constraints for creating a team."""
    field_map = {
        "_dataset": TEAMS,
        "name": {"dataset": TEAMS},
        "description": {"dataset": TEAMS},
        "member": {"source_key": "label", "dataset": TEAM_MEMBERS_OPTIONS},
        "role": {"source_key": "label", "dataset": ROLES},
    }
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_TEAM_CREATED_MAP)
