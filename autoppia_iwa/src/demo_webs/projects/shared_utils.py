import datetime
from typing import Any

from loguru import logger

from .criterion_helper import ComparisonOperator, CriterionValue, validate_criterion


def constraints_exist_in_db(data: list[dict], constraints: list[dict]) -> bool:
    """
    Returns True if *at least* one item satisfies ALL constraints.
    """
    matching_items = [item for item in data if item_matches_all_constraints(item, constraints)]
    return len(matching_items) > 0


def item_matches_all_constraints(item: dict, constraints: list[dict]) -> bool:
    """
    Returns True if the item satisfies *all* the given constraints.
    Each constraint is a dict with keys: field, operator, value.
    """
    for c in constraints:
        field = c["field"]
        operator = c["operator"]
        value = c["value"]
        actual_value = item.get(field)

        # Create CriterionValue to use validate_criterion
        criterion = CriterionValue(value=value, operator=operator)

        if not validate_criterion(actual_value, criterion):
            return False
    return True


def parse_price(price_raw: Any) -> float | None:
    """
    Helper function to parse price data, handling strings with currency symbols
    and commas, as well as direct numbers. Returns float or None if parsing fails.
    """
    if price_raw is None:
        return None
    try:
        if isinstance(price_raw, str):
            price_str = price_raw.replace("$", "").replace(",", "").strip()
            if not price_str:
                return None
            return float(price_str)
        elif isinstance(price_raw, int | float):
            return float(price_raw)
        else:
            logger.debug(f"Price data is not a string, int, or float: {type(price_raw)}")
            return None
    except (ValueError, TypeError) as e:
        logger.debug(f"Could not parse price data '{price_raw}'. Error: {e}")
        return None


def create_constraint_dict(field: str, operator: ComparisonOperator, value: Any) -> dict[str, Any]:
    """Creates a single constraint dictionary in the list[dict] format."""
    return {"field": field, "operator": operator, "value": value}


def generate_mock_dates():
    """
    Generates a list of mock dates strictly in the future within the same month,
    with time set to 19:00.
    """
    today = datetime.datetime.now(datetime.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    current_month = today.month
    mock_dates_raw = []

    # Add future dates starting from tomorrow
    for i in range(1, 15):  # next 14 days
        future_date = today + datetime.timedelta(days=i)
        if future_date.month == current_month:
            mock_dates_raw.append(future_date.replace(hour=19, minute=0, second=0, microsecond=0))

    return sorted(list(set(mock_dates_raw)))


def generate_mock_date_strings(dates: list):
    """
    Converts list of datetime objects to unique, sorted strings like "Jul 18".
    """
    date_strings = []
    for d in dates:
        if isinstance(d, datetime.datetime | datetime.date):
            date_strings.append(d.strftime("%b %d"))
    return sorted(list(set(date_strings)))
