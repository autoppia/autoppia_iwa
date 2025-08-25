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
    Generates a list of mock dates strictly in the future for the next 20 days,
    with time set to 19:00. Dates may cross into the next month.
    """
    today = datetime.datetime.now(datetime.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    mock_dates_raw = []

    for i in range(1, 21):  # next 20 days
        future_date = today + datetime.timedelta(days=i)
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


def validate_date_field(field_value, criterion):
    """
    Validates a date field against a criterion, independent of any class context.
    Handles ComparisonOperator and CriterionValue, and supports string, date, and datetime inputs.
    Returns True if the field matches the criterion, False otherwise.
    """
    from datetime import date, datetime

    from .criterion_helper import ComparisonOperator, CriterionValue

    comp_table = {
        ComparisonOperator.EQUALS: lambda s, c: s == c,
        ComparisonOperator.NOT_EQUALS: lambda s, c: s != c,
        ComparisonOperator.GREATER_THAN: lambda s, c: s > c,
        ComparisonOperator.GREATER_EQUAL: lambda s, c: s >= c,
        ComparisonOperator.LESS_THAN: lambda s, c: s < c,
        ComparisonOperator.LESS_EQUAL: lambda s, c: s <= c,
    }

    def to_date(val):
        if isinstance(val, str):
            try:
                return datetime.fromisoformat(val).date() if "T" in val else date.fromisoformat(val)
            except Exception:
                return None
        elif isinstance(val, datetime):
            return val.date()
        elif isinstance(val, date):
            return val
        return None

    if isinstance(criterion, CriterionValue):
        op = criterion.operator
        comp_date = to_date(criterion.value)
        field_date = to_date(field_value)
        if comp_date is None or field_date is None:
            return False
        try:
            return comp_table[op](field_date, comp_date)
        except KeyError:
            logger.error("Unknown comparison operator for date field: %s", op)
            return False
        except Exception as e:
            logger.error(f"Error validating date field: {e}")
            return False
    elif isinstance(criterion, datetime) and isinstance(field_value, datetime):
        if (field_value.tzinfo is not None) != (criterion.tzinfo is not None):
            field_dt = field_value.replace(tzinfo=None)
            crit_dt = criterion.replace(tzinfo=None)
            return comp_table[ComparisonOperator.EQUALS](field_dt, crit_dt)
        return comp_table[ComparisonOperator.EQUALS](field_value, criterion)
    elif isinstance(criterion, date) and isinstance(field_value, datetime):
        return comp_table[ComparisonOperator.EQUALS](field_value.date(), criterion)
    elif isinstance(criterion, datetime) and isinstance(field_value, date):
        return comp_table[ComparisonOperator.EQUALS](field_value, criterion.date())
    else:
        return criterion is None or field_value == criterion


def validate_time_field(field_value, criterion):
    """
    Validates a time field against a criterion, independent of any class context.
    Handles ComparisonOperator and CriterionValue, and supports string, time, and datetime inputs.
    Returns True if the field matches the criterion, False otherwise.
    """
    from datetime import datetime, time

    from .criterion_helper import ComparisonOperator, CriterionValue

    comp_table = {
        ComparisonOperator.EQUALS: lambda s, c: s == c,
        ComparisonOperator.NOT_EQUALS: lambda s, c: s != c,
        ComparisonOperator.GREATER_THAN: lambda s, c: s > c,
        ComparisonOperator.GREATER_EQUAL: lambda s, c: s >= c,
        ComparisonOperator.LESS_THAN: lambda s, c: s < c,
        ComparisonOperator.LESS_EQUAL: lambda s, c: s <= c,
    }

    def to_time(val):
        if isinstance(val, str):
            try:
                # Accepts "HH:MM[:SS[.ffffff]]"
                return time.fromisoformat(val)
            except Exception:
                return None
        elif isinstance(val, datetime):
            return val.time()
        elif isinstance(val, time):
            return val
        return None

    if isinstance(criterion, CriterionValue):
        op = criterion.operator
        comp_time = to_time(criterion.value)
        field_time = to_time(field_value)
        if comp_time is None or field_time is None:
            return False
        try:
            return comp_table[op](field_time, comp_time)
        except KeyError:
            logger.error("Unknown comparison operator for time field: %s", op)
            return False
        except Exception as e:
            logger.error(f"Error validating time field: {e}")
            return False
    elif isinstance(criterion, datetime) and isinstance(field_value, datetime):
        return comp_table[ComparisonOperator.EQUALS](field_value.time(), criterion.time())
    elif isinstance(criterion, time) and isinstance(field_value, datetime):
        return comp_table[ComparisonOperator.EQUALS](field_value.time(), criterion)
    elif isinstance(criterion, datetime) and isinstance(field_value, time):
        return comp_table[ComparisonOperator.EQUALS](field_value, criterion.time())
    else:
        return criterion is None or field_value == criterion
