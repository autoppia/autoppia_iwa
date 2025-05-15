import contextlib
import random
import traceback
from typing import Any

from ..criterion_helper import ComparisonOperator
from ..shared_data import FIELD_OPERATORS_MAP_PRODUCTS
from .data import PRODUCTS_DATA


def _parse_price_string(price_raw: str | float | int | None) -> float | None:
    """Helper to parse price string to float, handles None."""
    if price_raw is None:
        return None
    if isinstance(price_raw, str):
        try:
            # Remove currency symbols, commas, and whitespace
            cleaned_price = price_raw.replace("$", "").replace(",", "").strip()
            return float(cleaned_price)
        except (ValueError, AttributeError):
            print(f"Warning: Could not parse price string: '{price_raw}'")
            return None
    elif isinstance(price_raw, int | float):
        return float(price_raw)
    else:
        print(f"Warning: Unexpected price type: {type(price_raw)}. Value: {price_raw}")
        return None


def _create_constraint_dict(field: str, operator: ComparisonOperator, value: Any) -> dict[str, Any]:
    """Creates a single constraint dictionary in the list[dict] format."""
    return {"field": field, "operator": operator, "value": value}


def generate_constraint_value(field: str, operator: ComparisonOperator, product_data_source: dict[str, Any], all_products_data: list[dict[str, Any]] = PRODUCTS_DATA) -> Any:
    """
    Generates the value part for a single constraint based on field, operator, and data.
    Returns None if a value cannot be generated for the given criteria combination.
    """
    # --- Handle values for standard fields that map to {"field": ..., "operator": ..., "value": ...} ---
    source_value = product_data_source.get(field)
    generated_value = None  # Initialize generated value

    # Determine value pool based on field
    value_pool = []
    try:
        if field in ["id", "title", "category", "brand", "affiliation", "currency", "coupon"]:
            value_pool = [p.get(field) for p in all_products_data if isinstance(p.get(field), str) and p.get(field) is not None]
        elif field in ["price", "rating", "quantity", "items", "total_items", "total_amount", "tax", "shipping", "order_total", "previous_quantity", "new_quantity", "value"]:
            # For numeric fields, pool from relevant source (all products for item attributes, source data for totals)
            pool_source = all_products_data if field in ["price", "rating"] else [product_data_source]
            for item in pool_source:
                val = item.get(field)
                if field == "price" or field == "value" or field == "total_amount" or field == "tax" or field == "shipping" or field == "order_total":
                    parsed_val = _parse_price_string(val)
                    if parsed_val is not None:
                        value_pool.append(parsed_val)
                elif val is not None:
                    with contextlib.suppress(ValueError, TypeError):
                        value_pool.append(float(val))
            if field in ["quantity", "items", "total_items", "previous_quantity", "new_quantity"]:
                value_pool = [int(v) for v in value_pool if v is not None]  # Ensure integers for quantity/count fields
                if source_value is not None:
                    source_value = int(source_value)  # Also cast source value
        elif field in ["direction", "title", "query"]:  # Specific fields
            if field == "direction":
                value_pool = ["LEFT", "RIGHT"]
            elif field == "title":
                value_pool = ["Featured Products", "Best Sellers", "Electronics", "Kitchenware"]  # Carousel/List titles
            elif field == "query":
                all_terms_list = []
                for p in all_products_data:
                    all_terms_list.extend(str(p.get("title", "")).split())
                    category = p.get("category", "")
                    if isinstance(category, str) and category:
                        all_terms_list.append(category)
                    brand = p.get("brand", "")
                    if isinstance(brand, str) and brand:
                        all_terms_list.append(brand)
                value_pool = list(set(term for term in all_terms_list if term and isinstance(term, str)))  # Flat list of unique terms

    except Exception as e:
        print(f"Error building value pool for field '{field}': {e}")
        traceback.print_exc()
        return None  # Cannot generate value if pool fails

    valid_pool = [v for v in value_pool if v is not None]

    # --- Logic to generate value based on operator and source_value/pool ---

    if operator == ComparisonOperator.EQUALS:
        if source_value is not None:
            generated_value = source_value
        elif valid_pool:
            generated_value = random.choice(valid_pool)
        else:
            return None  # Cannot generate equals constraint without a value

    elif operator in [ComparisonOperator.NOT_EQUALS, ComparisonOperator.NOT_CONTAINS]:
        if source_value is not None:
            other_values = list(set(v for v in valid_pool if v != source_value))
            generated_value = random.choice(other_values) if other_values else "UnlikelyValue"  # Generate something different
        elif valid_pool:
            generated_value = random.choice(valid_pool)  # Pick any value if source is None
        else:
            generated_value = "SomeValue"  # Fallback

    elif operator in [ComparisonOperator.GREATER_THAN, ComparisonOperator.LESS_THAN, ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL]:
        if source_value is not None:
            try:
                num_source_value = float(source_value)  # Need numeric source for comparison
            except (ValueError, TypeError):
                return None
            numeric_pool = [float(v) for v in valid_pool if v is not None]

            if operator == ComparisonOperator.GREATER_THAN:
                candidates = [v for v in numeric_pool if v > num_source_value]
                generated_value = random.choice(candidates) if candidates else num_source_value + random.uniform(1, 10)
            elif operator == ComparisonOperator.LESS_THAN:
                candidates = [v for v in numeric_pool if v < num_source_value]
                generated_value = random.choice(candidates) if candidates else num_source_value - random.uniform(1, 10)
            elif operator == ComparisonOperator.GREATER_EQUAL:
                candidates = [v for v in numeric_pool if v >= num_source_value]
                generated_value = random.choice(candidates) if candidates else num_source_value
            elif operator == ComparisonOperator.LESS_EQUAL:
                candidates = [v for v in numeric_pool if v <= num_source_value]
                generated_value = random.choice(candidates) if candidates else num_source_value
            # Ensure integer for integer fields
            generated_value = int(generated_value) if field in ["quantity", "items", "total_items", "previous_quantity", "new_quantity"] else round(generated_value, 2)

    elif operator in [ComparisonOperator.CONTAINS, ComparisonOperator.NOT_CONTAINS]:
        if not isinstance(source_value, str) and source_value is not None:
            print(f"Warning: Source value for CONTAINS/NOT_CONTAINS operator is not a string: {source_value}")
            # Attempt to use a string from the pool as source if available
            source_value = random.choice([v for v in valid_pool if isinstance(v, str)]) if valid_pool else None
            if source_value is None:
                return None  # Cannot generate if no string source

        if operator == ComparisonOperator.CONTAINS:
            if source_value is not None and len(source_value) > 2:
                start = random.randint(0, len(source_value) - min(2, len(source_value)))
                end = random.randint(start + 1, len(source_value))
                generated_value = source_value[start:end] or source_value
            elif valid_pool:
                pool_string = random.choice([v for v in valid_pool if isinstance(v, str) and len(v) > 2]) if valid_pool else None
                if pool_string:
                    start = random.randint(0, len(pool_string) - min(2, len(pool_string)))
                    end = random.randint(start + 1, len(pool_string))
                    generated_value = pool_string[start:end] or pool_string
                else:
                    generated_value = "keyword"
            else:
                generated_value = "term"

        elif operator == ComparisonOperator.NOT_CONTAINS:
            if source_value is not None:
                generated_value = source_value + "XYZ" + str(random.randint(100, 999))
            elif valid_pool:
                pool_string = random.choice([v for v in valid_pool if isinstance(v, str)]) if valid_pool else ""
                generated_value = pool_string + "XYZ" + str(random.randint(100, 999))
            else:
                generated_value = "UnlikelyTerm"

    elif operator == ComparisonOperator.IN_LIST:
        if valid_pool:
            list_values = list(set(random.sample(valid_pool, random.randint(1, min(3, len(valid_pool))))))
            if source_value is not None and source_value not in list_values:
                list_values.append(source_value)
                random.shuffle(list_values)
            generated_value = list_values
        else:
            return None

    else:
        print(f"Warning: Operator {operator} not explicitly handled for field '{field}' in _generate_constraint_value")
        generated_value = source_value if source_value is not None else (random.choice(valid_pool) if valid_pool else None)
        if generated_value is None:
            print(f"Warning: Could not generate value for field '{field}' with operator '{operator}' using fallback.")
            return None

    if generated_value is None:
        print(f"Warning: Generated value is None for field '{field}' with operator '{operator}'.")
        return None

    return generated_value


# --- Specific Generation Functions (Now returning list[dict] format) ---


def generate_autozone_products_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    mappable_criteria_fields = ["item_name", "item_category", "item_brand", "item_rating", "item_price"]
    # Map criteria fields to the keys used in PRODUCTS_DATA
    criteria_to_product_key = {
        "item_name": "title",
        "item_category": "category",
        "item_brand": "brand",
        "item_rating": "rating",
        "item_price": "price",
    }

    all_criteria_fields = [*mappable_criteria_fields]

    # Determine which criteria fields we can generate constraints for based on PRODUCTS_DATA
    applicable_criteria_fields = [
        cf
        for cf in all_criteria_fields
        if PRODUCTS_DATA
        and (
            cf in criteria_to_product_key and criteria_to_product_key[cf] in PRODUCTS_DATA[0]  # Always applicable if PRODUCTS_DATA exists, need to check for 'id' key below
        )
    ]

    if not applicable_criteria_fields:
        return []

    selected_criteria_fields = random.sample(applicable_criteria_fields, random.randint(1, min(3, len(applicable_criteria_fields))))

    product = random.choice(PRODUCTS_DATA) if PRODUCTS_DATA else {}  # Pick a product to base constraints on

    for criteria_field in selected_criteria_fields:
        product_key = criteria_to_product_key.get(criteria_field)  # Get product key if exists

        # --- Operator Selection Logic using the map ---
        op = None
        if product_key and product_key in FIELD_OPERATORS_MAP_PRODUCTS:
            # If the product key is in the map, pick an operator from the allowed list
            allowed_operators = FIELD_OPERATORS_MAP_PRODUCTS[product_key]
            if allowed_operators:
                op_str = random.choice(allowed_operators)
                op = ComparisonOperator(op_str)
            else:
                print(f"Warning: No allowed operators defined for product key '{product_key}' in FIELD_OPERATORS_MAP_PRODUCTS.")
                continue
        if op:
            constraint_value = generate_constraint_value(product_key, op, product, all_products_data=PRODUCTS_DATA)

            if constraint_value is not None:
                # Create the constraint dictionary using the CRITERIA field name as the "field" key
                constraint_dict = _create_constraint_dict(criteria_field, op, constraint_value)
                constraints_list.append(constraint_dict)
        else:
            print(f"Warning: Could not select operator for criteria field '{criteria_field}'. Skipping constraint generation.")

    return constraints_list


def generate_search_query_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    query_operators = [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS]

    if query_operators:
        op = random.choice(query_operators)
        # Generate the value for the 'query' field (pool comes from all_products_data terms)
        constraint_value = generate_constraint_value("query", op, {}, all_products_data=PRODUCTS_DATA)
        if constraint_value is not None:
            # Create the constraint dictionary for the "query" field
            constraints_list.append(_create_constraint_dict("query", op, constraint_value))

    return constraints_list if constraints_list else [_create_constraint_dict("query", ComparisonOperator.CONTAINS, "products")]  # Fallback


def generate_cart_operation_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    product = random.choice(PRODUCTS_DATA) if PRODUCTS_DATA else {}
    if not product:
        return []

    item_identification_fields = ["name"]  # Use criterion aliases as fields
    # Map criterion alias to product key
    criterion_alias_to_product_key = {"name": "title"}

    selected_id_field = random.choice(item_identification_fields)
    product_key = criterion_alias_to_product_key.get(selected_id_field)

    if product_key and product_key in ([*list(product.keys()), "id"]):  # Ensure product key exists in product data or is 'id'
        op = None
        # Check the map for the corresponding product key (title or id)
        if product_key in FIELD_OPERATORS_MAP_PRODUCTS:
            allowed_operators = FIELD_OPERATORS_MAP_PRODUCTS[product_key]
            if allowed_operators:
                op_str = random.choice(allowed_operators)
                op = ComparisonOperator(op_str)

        if op:
            # Generate the value using the product key and the selected operator
            constraint_value = generate_constraint_value(product_key, op, product, all_products_data=PRODUCTS_DATA)
            if constraint_value is not None:
                # Create constraint dictionary using the criterion alias as the 'field'
                constraints_list.append(_create_constraint_dict(selected_id_field, op, constraint_value))
        else:
            print(f"Warning: Could not select operator for product key '{product_key}' in cart operation constraints.")

    else:
        return []  # Need at least name or id

    # Optional constraints based on item attributes (matching ValidationCriteria aliases)
    # Map criterion alias to product key
    criterion_alias_to_product_key_attributes = {
        "category": "category",
        "brand": "brand",
        "price": "price",
        "rating": "rating",
    }

    # Filter product keys based on presence in data and allowed operators map
    applicable_product_keys = [
        pk
        for pk in criterion_alias_to_product_key_attributes.values()
        if pk in product and pk in FIELD_OPERATORS_MAP_PRODUCTS  # Check if field is in the allowed map
    ]

    selected_product_keys = random.sample(applicable_product_keys, random.randint(0, min(2, len(applicable_product_keys))))

    for product_key in selected_product_keys:
        criterion_alias = next(alias for alias, key in criterion_alias_to_product_key_attributes.items() if key == product_key)  # Get the alias

        # Pick an allowed operator from the map for this product key
        allowed_operators = FIELD_OPERATORS_MAP_PRODUCTS[product_key]
        if not allowed_operators:
            continue

        op_str = random.choice(allowed_operators)
        op = ComparisonOperator(op_str)

        # Generate value using the product key
        constraint_value = generate_constraint_value(product_key, op, product, all_products_data=PRODUCTS_DATA)

        if constraint_value is not None:
            # Create constraint dictionary using the criterion alias as the 'field'
            constraints_list.append(_create_constraint_dict(criterion_alias, op, constraint_value))

    # Optional quantity constraint (maps to 'quantity' alias in ValidationCriteria)
    # Quantity operator is typically EQUALS, GREATER_EQUAL, LESS_EQUAL
    quantity_operators = [
        ComparisonOperator.EQUALS,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    ]
    if random.random() > 0.3 and quantity_operators:
        op = random.choice(quantity_operators)
        # Generate a plausible quantity value using _generate_constraint_value with a mock source
        quantity_value = generate_constraint_value("quantity", op, {"quantity": random.randint(1, 5)})
        if quantity_value is not None:
            constraints_list.append(_create_constraint_dict("quantity", op, quantity_value))

    return constraints_list


def generate_quantity_change_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    product = random.choice(PRODUCTS_DATA) if PRODUCTS_DATA else {}
    if not product:
        return []

    item_identification_fields = ["name"]  # Use criterion aliases as fields
    product_key_map = {"name": "title"}

    selected_id_field = random.choice(item_identification_fields)
    product_key = product_key_map.get(selected_id_field)

    if product_key and product_key in ([*list(product.keys())]):
        op = None
        # Check the map for the corresponding product key (title or id)
        if product_key in FIELD_OPERATORS_MAP_PRODUCTS:
            allowed_operators = FIELD_OPERATORS_MAP_PRODUCTS[product_key]
            if allowed_operators:
                op_str = random.choice(allowed_operators)
                op = ComparisonOperator(op_str)
        if op:
            # Generate the value using the product key and the selected operator
            constraint_value = generate_constraint_value(product_key, op, product, all_products_data=PRODUCTS_DATA)
            if constraint_value is not None:
                # Create constraint dictionary using the criterion alias as the 'field'
                constraints_list.append(_create_constraint_dict(selected_id_field, op, constraint_value))
        else:
            print(f"Warning: Could not select operator for product key '{product_key}' in quantity change constraints.")
    else:
        return []

    # Constraints on previous and new quantity (map to 'previous_quantity', 'new_quantity')
    # Operators are typically EQUALS, GREATER/LESS (EQUAL) or IN_RANGE for quantities
    quantity_operators = [
        ComparisonOperator.EQUALS,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    ]

    if quantity_operators:
        prev_qty = random.randint(1, 5)
        new_qty = prev_qty
        while new_qty == prev_qty:  # Ensure new_qty is different
            new_qty = random.randint(max(0, prev_qty - 2), prev_qty + 3)

        # Generate constraints for previous and new quantity
        op_prev = random.choice(quantity_operators)
        op_new = random.choice(quantity_operators)

        # Generate values based on the desired quantities using _generate_constraint_value with mock source
        constraint_value_prev = generate_constraint_value("quantity", op_prev, {"quantity": prev_qty})  # Use "quantity" field name for value generation logic
        constraint_value_new = generate_constraint_value("quantity", op_new, {"quantity": new_qty})  # Use "quantity" field name

        if constraint_value_prev is not None:
            constraints_list.append(_create_constraint_dict("previous_quantity", op_prev, constraint_value_prev))
        if constraint_value_new is not None:
            constraints_list.append(_create_constraint_dict("new_quantity", op_new, constraint_value_new))

    return constraints_list


def generate_checkout_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    total_items_operators = [ComparisonOperator.EQUALS, ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL]
    total_amount_operators = [ComparisonOperator.EQUALS, ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL]

    if random.random() > 0.3 and total_items_operators:
        op = random.choice(total_items_operators)
        total_items_value = random.randint(1, 10)
        # Generate constraint value using _generate_constraint_value with mock source
        constraint_value = generate_constraint_value("total_items", op, {"total_items": total_items_value})
        if constraint_value is not None:
            constraints_list.append(_create_constraint_dict("total_items", op, constraint_value))

    if random.random() > 0.3 and PRODUCTS_DATA and total_amount_operators:
        op = random.choice(total_amount_operators)
        min_price = min(_parse_price_string(p["price"]) or 0 for p in PRODUCTS_DATA) if PRODUCTS_DATA else 1.0
        max_price = max(_parse_price_string(p["price"]) or 100 for p in PRODUCTS_DATA) if PRODUCTS_DATA else 100.0
        plausible_amount = random.uniform(
            min_price * 1,
            max_price * (constraints_list[0]["value"] if constraints_list and constraints_list[0]["field"] == "total_items" and isinstance(constraints_list[0]["value"], int) else 5) / 2.0,
        )
        # Generate constraint value using _generate_constraint_value with mock source
        constraint_value = generate_constraint_value("total_amount", op, {"total_amount": round(plausible_amount, 2)})
        if constraint_value is not None:
            constraints_list.append(_create_constraint_dict("total_amount", op, constraint_value))

    return constraints_list


def generate_order_completion_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    # Fields available in ValidationCriteria and generators: order_id, affiliation, value, tax, shipping, order_total, currency, coupon
    available_fields = ["items", "order_total"]
    selected_fields = random.sample(available_fields, random.randint(1, min(3, len(available_fields))))

    order_numeric_operators = [
        ComparisonOperator.EQUALS,
        ComparisonOperator.NOT_EQUALS,
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    ]

    # Mock some plausible order data for calculations and generating values
    random.randint(1, 10)
    mock_subtotal = round(random.uniform(20.0, 1000.0), 2)
    mock_order_total = round(mock_subtotal, 2)
    mock_order_data = {
        "items": mock_subtotal,
        "order_total": mock_order_total,
    }

    for field in selected_fields:
        value = mock_order_data.get(field)  # Get value from mock data
        if value is None:
            continue  # Skip if mock data doesn't have it

        op = random.choice(order_numeric_operators)

        # Generate constraint value using the mock order data for the specific field
        constraint_value = generate_constraint_value(field, op, mock_order_data, all_products_data=PRODUCTS_DATA)
        if constraint_value is not None:
            constraints_list.append(_create_constraint_dict(field, op, constraint_value))  # Use the field name

    return constraints_list


def generate_carousel_scroll_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    # Fields available in ValidationCriteria and generators: direction, title
    available_fields = ["direction", "title"]
    selected_fields = random.sample(available_fields, random.randint(1, len(available_fields)))

    # Define allowed operators for these fields
    direction_operators = [ComparisonOperator.EQUALS]
    title_operators = [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS]

    mock_direction = random.choice(["LEFT", "RIGHT"])
    mock_title = random.choice(["Featured Products", "Best Sellers", "Electronics", "Kitchen"])
    mock_data = {"direction": mock_direction, "title": mock_title}

    for field in selected_fields:
        if field == "direction" and direction_operators:
            op = random.choice(direction_operators)
        elif field == "title" and title_operators:
            op = random.choice(title_operators)
        else:
            continue

        # Generate constraint value using the mock data for the specific field
        constraint_value = generate_constraint_value(field, op, mock_data)
        if constraint_value is not None:
            constraints_list.append(_create_constraint_dict(field, op, constraint_value))

    return constraints_list
