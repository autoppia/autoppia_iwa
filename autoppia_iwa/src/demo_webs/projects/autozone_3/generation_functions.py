import contextlib
import random
import traceback
from typing import Any

from loguru import logger

from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url

from ..criterion_helper import ComparisonOperator
from ..shared_utils import create_constraint_dict, parse_price
from .data import FIELD_OPERATORS_MAP_PRODUCTS
from .data_utils import fetch_data


# ============================================================================
# DATA FETCHING HELPERS
# ============================================================================

async def _ensure_products_dataset(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """Extract products data from the pre-loaded dataset, or fetch from server if not available."""
    # Fetch data if dataset is not provided or is empty
    if dataset is None or dataset == {}:
        seed = get_seed_from_url(task_url)
        products = await fetch_data(seed_value=seed)
        dataset = {"products": products}

    if dataset and "products" in dataset:
        return dataset["products"]
    return []


# ============================================================================
# VALUE POOL BUILDING HELPERS
# ============================================================================

def _build_string_field_pool(field: str, all_products_data: list[dict[str, Any]]) -> list[str]:
    """Build value pool for string fields."""
    return [p.get(field) for p in all_products_data if isinstance(p.get(field), str) and p.get(field) is not None]


def _process_price_field_value(val: Any) -> float | None:
    """Process price-related field value."""
    parsed_val = parse_price(str(val)) if val is not None else None
    return parsed_val


def _process_numeric_field_value(field: str, val: Any) -> float | None:
    """Process numeric field value."""
    if field in ["price", "value", "total_amount", "tax", "shipping", "order_total", "rating"]:
        return _process_price_field_value(val)
    if val is not None:
        with contextlib.suppress(ValueError, TypeError):
            return float(val)
    return None


def _normalize_quantity_field(value_pool: list[Any], source_value: Any) -> tuple[list[int], Any]:
    """Normalize quantity fields to integers."""
    normalized_pool = [int(v) for v in value_pool if v is not None]
    normalized_source = None
    if source_value is not None:
        try:
            normalized_source = int(source_value)
        except (ValueError, TypeError):
            normalized_source = None
    return normalized_pool, normalized_source


def _build_numeric_field_pool(field: str, product_data_source: dict[str, Any], all_products_data: list[dict[str, Any]]) -> tuple[list[Any], Any]:
    """Build value pool for numeric fields and return pool and source_value."""
    pool_source = all_products_data if field in ["price", "rating"] else [product_data_source]
    value_pool = []
    source_value = product_data_source.get(field)
    
    for item in pool_source:
        val = item.get(field)
        processed_val = _process_numeric_field_value(field, val)
        if processed_val is not None:
            value_pool.append(processed_val)

    if field in ["quantity", "items", "total_items", "previous_quantity", "new_quantity"]:
        value_pool, source_value = _normalize_quantity_field(value_pool, source_value)
    
    return value_pool, source_value


def _build_query_field_pool(product_data_source: dict[str, Any], all_products_data: list[dict[str, Any]]) -> tuple[list[str], str | None]:
    """Build value pool for query field."""
    source_value = product_data_source.get("title")
    all_terms_list = []
    for p in all_products_data:
        all_terms_list.extend(str(p.get("title", "")).split())
        category = p.get("category", "")
        if isinstance(category, str) and category:
            all_terms_list.append(category)
        brand = p.get("brand", "")
        if isinstance(brand, str) and brand:
            all_terms_list.append(brand)
    value_pool = list({term for term in all_terms_list if term and isinstance(term, str)})
    return value_pool, source_value


# ============================================================================
# CONSTRAINT VALUE GENERATION HELPERS - OPERATORS
# ============================================================================

def _handle_equals_operator(source_value: Any, valid_pool: list[Any]) -> Any:
    """Handle EQUALS operator."""
    if source_value is not None:
        return source_value
    if valid_pool:
        return random.choice(valid_pool)
    return None


def _handle_not_equals_operator(source_value: Any, valid_pool: list[Any]) -> Any:
    """Handle NOT_EQUALS operator."""
    if source_value is not None:
        other_values = list({v for v in valid_pool if v != source_value})
        return random.choice(other_values) if other_values else None
    if valid_pool:
        return random.choice(valid_pool)
    return None


def _calculate_numeric_delta(num_source_value: float) -> float:
    """Calculate delta for numeric comparison operators."""
    if num_source_value > 10:
        return random.uniform(1, min(10, num_source_value / 2))
    if num_source_value > 1:
        return random.uniform(0.1, min(1, num_source_value / 2))
    return random.uniform(0.01, max(0.05, num_source_value / 2))


def _handle_numeric_comparison_operator(operator: ComparisonOperator, num_source_value: float, delta: float) -> float:
    """Handle numeric comparison operators (GREATER_THAN, LESS_THAN, etc.)."""
    if operator == ComparisonOperator.GREATER_THAN:
        return max(0.01, num_source_value - delta)
    if operator == ComparisonOperator.LESS_THAN:
        return num_source_value + delta
    if operator in [ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL]:
        return num_source_value
    return num_source_value


def _format_numeric_value(generated_value: float, field: str) -> float | int:
    """Format numeric value based on field type."""
    if field in ["quantity", "items", "total_items", "previous_quantity", "new_quantity"]:
        return max(1, round(generated_value))
    return round(generated_value, 2)


def _handle_numeric_operators(operator: ComparisonOperator, source_value: Any, valid_pool: list[Any], field: str) -> Any:
    """Handle numeric comparison operators."""
    if source_value is not None:
        try:
            num_source_value = float(source_value)
        except (ValueError, TypeError):
            return None

        delta = _calculate_numeric_delta(num_source_value)
        generated_value = _handle_numeric_comparison_operator(operator, num_source_value, delta)
        return _format_numeric_value(generated_value, field)

    if valid_pool and all(isinstance(v, int | float) for v in valid_pool):
        generated_value = random.choice([float(v) for v in valid_pool])
        return _format_numeric_value(generated_value, field)

    return None


def _handle_contains_operator(string_source: str) -> str:
    """Handle CONTAINS operator."""
    if len(string_source) > 2:
        min_len = min(2, len(string_source))
        start = random.randint(0, len(string_source) - min_len)
        end = random.randint(start + min_len, len(string_source))
        generated_value = string_source[start:end]
    else:
        generated_value = string_source
    
    if not generated_value:
        generated_value = "keyword"
    
    return generated_value


def _handle_string_operators(operator: ComparisonOperator, source_value: Any, valid_pool: list[Any]) -> Any:
    """Handle CONTAINS and NOT_CONTAINS operators."""
    string_source = None
    if isinstance(source_value, str):
        string_source = source_value
    elif valid_pool:
        string_source = random.choice([v for v in valid_pool if isinstance(v, str) and len(v) > 0])

    if string_source is None:
        return None

    if operator == ComparisonOperator.CONTAINS:
        return _handle_contains_operator(string_source)
    
    if operator == ComparisonOperator.NOT_CONTAINS:
        return string_source + "XYZ" + str(random.randint(100, 999))
    
    return None


def _handle_in_list_operator(source_value: Any, valid_pool: list[Any]) -> list[Any] | None:
    """Handle IN_LIST operator."""
    if not valid_pool:
        return None

    num_elements = random.randint(1, min(3, len(valid_pool)))
    list_values = random.sample(valid_pool, num_elements)
    if source_value is not None and source_value not in list_values:
        list_values.append(source_value)
        random.shuffle(list_values)
    return list_values


# ============================================================================
# MAIN CONSTRAINT VALUE GENERATOR
# ============================================================================

def _build_value_pool(field: str, product_data_source: dict[str, Any], all_products_data: list[dict[str, Any]]) -> tuple[list[Any], Any]:
    """Build value pool based on field type."""
    source_value = product_data_source.get(field)
    if field == "price":
        source_value = parse_price(source_value)

    if field in ["id", "title", "category", "brand", "affiliation", "currency", "coupon"]:
        value_pool = _build_string_field_pool(field, all_products_data)
    elif field in ["price", "rating", "quantity", "items", "total_items", "total_amount", "tax", "shipping", "order_total", "previous_quantity", "new_quantity", "value"]:
        value_pool, source_value = _build_numeric_field_pool(field, product_data_source, all_products_data)
    elif field == "query":
        value_pool, source_value = _build_query_field_pool(product_data_source, all_products_data)
    else:
        value_pool = []
    
    return value_pool, source_value


def _generate_value_by_operator(operator: ComparisonOperator, source_value: Any, valid_pool: list[Any], field: str) -> Any:
    """Generate value based on operator type."""
    if operator == ComparisonOperator.EQUALS:
        return _handle_equals_operator(source_value, valid_pool)
    if operator == ComparisonOperator.NOT_EQUALS:
        return _handle_not_equals_operator(source_value, valid_pool)
    if operator in [ComparisonOperator.GREATER_THAN, ComparisonOperator.LESS_THAN, ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL]:
        return _handle_numeric_operators(operator, source_value, valid_pool, field)
    if operator in [ComparisonOperator.CONTAINS, ComparisonOperator.NOT_CONTAINS]:
        return _handle_string_operators(operator, source_value, valid_pool)
    if operator == ComparisonOperator.IN_LIST:
        return _handle_in_list_operator(source_value, valid_pool)
    return _handle_fallback_operator(operator, field, source_value, valid_pool)


def generate_constraint_value(field: str, operator: ComparisonOperator, product_data_source: dict[str, Any], all_products_data: list[dict[str, Any]] | None = None) -> Any:
    """
    Generates the value part for a single constraint based on field, operator, and data.
    Returns None if a value cannot be generated for the given criteria combination.
    """
    if all_products_data is None:
        return None

    try:
        value_pool, source_value = _build_value_pool(field, product_data_source, all_products_data)
    except Exception as e:
        logger.error(f"Error building value pool for field '{field}': {e}")
        traceback.print_exc()
        return None

    valid_pool = [v for v in value_pool if v is not None]
    generated_value = _generate_value_by_operator(operator, source_value, valid_pool, field)

    if generated_value is None and operator != ComparisonOperator.EQUALS and operator != ComparisonOperator.NOT_EQUALS:
        return None

    return generated_value if generated_value is not None else None


def _handle_fallback_operator(operator: ComparisonOperator, field: str, source_value: Any, valid_pool: list[Any]) -> Any:
    """Handle fallback for unhandled operators."""
    logger.warning(f"Operator {operator} not explicitly handled for field '{field}' in _generate_constraint_value")
    if source_value is not None:
        return source_value
    if valid_pool:
        return random.choice(valid_pool)
    logger.warning(f"Could not generate value for field '{field}' with operator '{operator}' using fallback.")
    return None


# ============================================================================
# CONSTRAINT GENERATION FUNCTIONS
# ============================================================================

# PRODUCT CONSTRAINTS
async def generate_autozone_products_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints_list = []
    fields = ["title", "category", "brand", "rating", "price"]
    data_items = await _ensure_products_dataset(task_url, dataset)
    if not data_items:
        return []

    selected_criteria_fields = random.sample(fields, random.randint(1, min(3, len(fields))))
    product = random.choice(data_items)

    for criteria_field in selected_criteria_fields:
        allowed_operators = FIELD_OPERATORS_MAP_PRODUCTS[criteria_field]
        op = ComparisonOperator(random.choice(allowed_operators))
        constraint_value = generate_constraint_value(criteria_field, op, product, all_products_data=data_items)
        if constraint_value is not None:
            constraint_dict = create_constraint_dict(criteria_field, op, constraint_value)
            constraints_list.append(constraint_dict)
        else:
            logger.warning(f"Could not select operator for criteria field '{criteria_field}'. Skipping constraint generation.")

    return constraints_list


# SEARCH CONSTRAINTS
async def generate_search_query_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints_list = []
    query_operators = [
        ComparisonOperator.EQUALS,
        ComparisonOperator.CONTAINS,
    ]

    op = random.choice(query_operators)
    # Pass a mock product_data_source even if not directly used, as generate_constraint_value expects it
    data_items = await _ensure_products_dataset(task_url, dataset)
    product = random.choice(data_items)
    constraint_value = generate_constraint_value("query", op, product, all_products_data=data_items)
    if constraint_value is not None:
        constraints_list.append(create_constraint_dict("query", op, constraint_value))

    # Fallback
    return constraints_list if constraints_list else [create_constraint_dict("query", ComparisonOperator.CONTAINS, "products")]


# QUANTITY CHANGE CONSTRAINTS
def _generate_quantity_threshold(operator: ComparisonOperator) -> int:
    """Generate threshold value for quantity operators."""
    if operator == ComparisonOperator.EQUALS:
        return random.randint(1, 10)
    if operator == ComparisonOperator.GREATER_EQUAL:
        return random.randint(1, 9)
    if operator == ComparisonOperator.LESS_EQUAL:
        return random.randint(2, 10)
    if operator == ComparisonOperator.GREATER_THAN:
        return random.randint(1, 9)
    if operator == ComparisonOperator.LESS_THAN:
        return random.randint(2, 10)
    return random.randint(1, 10)


def _add_product_constraint(constraints_list: list[dict[str, Any]], product_key: str, product: dict[str, Any], data_items: list[dict[str, Any]]) -> None:
    """Add product constraint to constraints list."""
    allowed_operators = FIELD_OPERATORS_MAP_PRODUCTS[product_key]
    op = ComparisonOperator(random.choice(allowed_operators))
    constraint_value = generate_constraint_value(product_key, op, product, all_products_data=data_items)
    if constraint_value is not None:
        constraints_list.append(create_constraint_dict(product_key, op, constraint_value))


def _add_quantity_constraint(constraints_list: list[dict[str, Any]]) -> None:
    """Add quantity constraint to constraints list."""
    quantity_operators = [
        ComparisonOperator.EQUALS,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_THAN,
    ]
    op = random.choice(quantity_operators)
    threshold = _generate_quantity_threshold(op)

    if 1 <= threshold <= 10:
        constraints_list.append(create_constraint_dict("new_quantity", op, threshold))
    else:
        logger.warning(f"Invalid quantity generated: {threshold} with operator {op}")


async def generate_quantity_change_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints_list = []
    data_items = await _ensure_products_dataset(task_url, dataset)
    if not data_items:
        return []

    product = random.choice(data_items)
    product_key = "title"

    _add_product_constraint(constraints_list, product_key, product, data_items)
    _add_quantity_constraint(constraints_list)

    return constraints_list


# CHECKOUT CONSTRAINTS
async def generate_checkout_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Generate randomized checkout constraints based on product data."""
    constraints: list[dict[str, Any]] = []
    field = "total_amount"
    operators = [ComparisonOperator.EQUALS, ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL]
    data_items = await _ensure_products_dataset(task_url, dataset)
    if not data_items:
        return constraints

    try:
        product = random.choice(data_items)
        price_str = product["price"]
        price = parse_price(price_str)

        operator = random.choice(operators)
        value = generate_constraint_value(field, operator, {field: price}, data_items)

        if value is not None:
            constraints.append(create_constraint_dict(field, operator, value))

    except (KeyError, IndexError, TypeError, ValueError) as e:
        logger.warning(f"Failed to generate checkout constraint: {e}")

    return constraints


# ORDER CONSTRAINTS
async def generate_order_completed_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """
    Generate constraints for the ORDER_COMPLETED event,
    focused on the `items` list with ProductSummary fields like title, id, and quantity.
    """
    constraints_list = []
    data_items = await _ensure_products_dataset(task_url, dataset)
    if not data_items:
        return []

    product = random.choice(data_items)

    # Choose one or more fields from ProductSummary to apply as criteria
    product_fields = ["title", "quantity"]

    for field in product_fields:
        # Map field to appropriate operators
        allowed_ops = FIELD_OPERATORS_MAP_PRODUCTS.get(field, [ComparisonOperator.EQUALS])
        op = ComparisonOperator(random.choice(allowed_ops))

        val = generate_constraint_value(field, op, product, all_products_data=data_items)
        if val is not None:
            constraints_list.append(create_constraint_dict(field, op, val))

    return constraints_list


# CAROUSEL CONSTRAINTS
def generate_carousel_scroll_constraints() -> list[dict[str, Any]]:
    constraints_list = []

    selected_fields = random.choice([["direction"], ["title"], ["direction", "title"]])

    direction_operators = [ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS]
    title_operators = [ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS]
    if "direction" not in selected_fields:
        selected_fields.append("direction")

    for field in selected_fields:
        if field == "direction":
            op = random.choice(direction_operators)
            constraint_value = random.choice(["LEFT", "RIGHT"])
        elif field == "title":
            op = random.choice(title_operators)
            title = random.choice(["Technology", "Home", "Electronics", "Kitchen", "Fitness"])
            constraint_value = f"Top Sellers In {title}"
        else:
            continue

        constraints_list.append(create_constraint_dict(field, op, constraint_value))

    return constraints_list


# FILTER CONSTRAINTS
async def generate_category_filter_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints: list[dict[str, Any]] = []
    data_items = await _ensure_products_dataset(task_url, dataset)
    if not data_items:
        return constraints

    allowed_categories = {"all", "kitchen", "technology", "home", "electronics", "fitness"}
    categories = sorted({str(item.get("category", "")).lower() for item in data_items if item.get("category") and str(item.get("category", "")).lower() in allowed_categories})
    if not categories:
        # Fallback to "all" if dataset categories don't match allowed values
        categories = ["all"]

    selected_category = random.choice(categories)
    constraints.append(create_constraint_dict("category", ComparisonOperator.EQUALS, selected_category))

    return constraints
