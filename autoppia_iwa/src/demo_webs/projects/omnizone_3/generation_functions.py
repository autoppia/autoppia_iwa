import random
from typing import Any

from ..books_2.utils import parse_constraints_str
from ..criterion_helper import ComparisonOperator, CriterionValue, validate_criterion
from .data import PRODUCTS_DATA


def generate_omnizone_products_constraints():
    """
    Generates constraints specifically for book-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import build_constraints_info

    # Generar restricciones frescas basadas en los datos de películas
    constraints_str = build_constraints_info(PRODUCTS_DATA)

    # Convertir el string a la estructura de datos
    if constraints_str:
        return parse_constraints_str(constraints_str)
    return None


def generate_constraint_from_solution(product: dict, field: str, operator: ComparisonOperator) -> dict[str, Any]:
    """
    Generates a constraint for a field and operator specific to a solution product.
    Utilizes the complete set of products to generate more realistic constraints.
    """
    constraint = {"field": field, "operator": operator}
    value = product.get(field)

    if field in ["title", "category", "brand"]:
        if operator == ComparisonOperator.EQUALS:
            constraint["value"] = value
        elif operator == ComparisonOperator.NOT_EQUALS:
            other_values = list(set(p[field] for p in PRODUCTS_DATA if p.get(field) != value))
            constraint["value"] = random.choice(other_values) if other_values else "SomeOtherValue"
        elif operator == ComparisonOperator.CONTAINS:
            if isinstance(value, str) and len(value) > 3:
                start = random.randint(0, len(value) - 3)
                length = random.randint(2, min(5, len(value) - start))
                constraint["value"] = value[start : start + length]
            else:
                constraint["value"] = value if value else ""  # Handle empty/non-string values
        elif operator == ComparisonOperator.NOT_CONTAINS:
            alphabet = "abcdefghijklmnopqrstuvwxyz"
            while True:
                test_str = "".join(random.choice(alphabet) for _ in range(3))
                if (isinstance(value, str) and test_str.lower() not in value.lower()) or not isinstance(value, str):
                    constraint["value"] = test_str
                    break

    elif field == "price":
        # Need to convert price string "$X.XX" to float for comparison
        price_float = float(value.replace("$", "")) if isinstance(value, str) and value.startswith("$") else None
        all_prices = [float(p["price"].replace("$", "").replace(",", "")) for p in PRODUCTS_DATA if isinstance(p.get("price"), str) and p["price"].startswith("$")]
        if price_float is None or not all_prices:
            return None  # Cannot generate price constraint if data is bad

        if operator == ComparisonOperator.EQUALS:
            constraint["value"] = price_float
        elif operator == ComparisonOperator.NOT_EQUALS:
            other_values = list(set(p for p in all_prices if p != price_float))
            constraint["value"] = random.choice(other_values) if other_values else round(price_float + (10 if random.random() > 0.5 else -10), 2)
        elif operator == ComparisonOperator.GREATER_THAN:
            lower_values = [p for p in all_prices if p < price_float]
            constraint["value"] = random.choice(lower_values) if lower_values else round(price_float - 10, 2)
        elif operator == ComparisonOperator.LESS_THAN:
            higher_values = [p for p in all_prices if p > price_float]
            constraint["value"] = random.choice(higher_values) if higher_values else round(price_float + 10, 2)
        elif operator == ComparisonOperator.GREATER_EQUAL:
            valid_values = [p for p in all_prices if p <= price_float]
            constraint["value"] = random.choice(valid_values) if valid_values else price_float
        elif operator == ComparisonOperator.LESS_EQUAL:
            valid_values = [p for p in all_prices if p >= price_float]
            constraint["value"] = random.choice(valid_values) if valid_values else price_float
        elif operator == ComparisonOperator.IN_LIST:
            other_values = list(set(p for p in all_prices if p != price_float))
            sample_size = min(2, len(other_values))
            constraint["value"] = [price_float, *random.sample(other_values, sample_size)] if other_values else [price_float]
        elif operator == ComparisonOperator.NOT_IN_LIST:
            other_values = list(set(p for p in all_prices if p != price_float))
            if other_values:
                constraint["value"] = random.sample(other_values, min(3, len(other_values)))
            else:
                constraint["value"] = [round(price_float + 10, 2), round(price_float + 20, 2)]  # Generate values outside

    elif field == "rating":
        if operator == ComparisonOperator.EQUALS:
            constraint["value"] = value
        elif operator == ComparisonOperator.NOT_EQUALS:
            other_values = list(set(p["rating"] for p in PRODUCTS_DATA if p.get("rating") != value and isinstance(p.get("rating"), int | float)))
            constraint["value"] = random.choice(other_values) if other_values else round(max(0, min(5, value + (0.5 if random.random() > 0.5 else -0.5))), 1)
        elif operator == ComparisonOperator.GREATER_THAN:
            lower_values = [p["rating"] for p in PRODUCTS_DATA if isinstance(p.get("rating"), int | float) and p["rating"] < value]
            constraint["value"] = random.choice(lower_values) if lower_values else max(0.0, value - 0.1)
        elif operator == ComparisonOperator.LESS_THAN:
            higher_values = [p["rating"] for p in PRODUCTS_DATA if isinstance(p.get("rating"), int | float) and p["rating"] > value]
            constraint["value"] = random.choice(higher_values) if higher_values else min(5.0, value + 0.1)
        elif operator == ComparisonOperator.GREATER_EQUAL:
            valid_values = [p["rating"] for p in PRODUCTS_DATA if isinstance(p.get("rating"), int | float) and p["rating"] <= value]
            constraint["value"] = random.choice(valid_values) if valid_values else value
        elif operator == ComparisonOperator.LESS_EQUAL:
            valid_values = [p["rating"] for p in PRODUCTS_DATA if isinstance(p.get("rating"), int | float) and p["rating"] >= value]
            constraint["value"] = random.choice(valid_values) if valid_values else value
        elif operator == ComparisonOperator.IN_LIST:
            other_values = list(set(p["rating"] for p in PRODUCTS_DATA if isinstance(p.get("rating"), int | float) and p["rating"] != value))
            sample_size = min(2, len(other_values))
            constraint["value"] = [value, *random.sample(other_values, sample_size)] if other_values else [value]
        elif operator == ComparisonOperator.NOT_IN_LIST:
            other_values = list(set(p["rating"] for p in PRODUCTS_DATA if isinstance(p.get("rating"), int | float) and p["rating"] != value))
            if other_values:
                constraint["value"] = random.sample(other_values, min(3, len(other_values)))
            else:
                constraint["value"] = [max(0, min(5, value + 0.5)), max(0, min(5, value + 1.0))]  # Generate values outside

    # Check if the generated constraint is valid for the solution product
    criterion = CriterionValue(value=constraint["value"], operator=operator)
    if validate_criterion(product.get(field), criterion):
        return constraint

    # If we reach here, the generated constraint is not valid
    return None


# def generate_omnizone_products_constraints() -> list[dict[str, Any]]:
#     """
#     Generates constraints for product-related use cases (like viewing details)
#     based on the PRODUCTS_DATA.
#     Returns the constraints as structured data (list of dictionaries).
#     """
#     if not PRODUCTS_DATA:
#         return []
#
#     # Pick a random product to base the constraints on (ensures the product exists)
#     solution_product = random.choice(PRODUCTS_DATA)
#
#     constraints = []
#
#     # Randomly choose a field and operator to generate a constraint
#     # Prioritize fields that are commonly filtered (title, category, brand, price, rating)
#     possible_fields = ["title", "category", "brand", "price", "rating"]
#     field = random.choice(possible_fields)
#
#     if field in ["title", "category", "brand"]:
#         possible_operators = [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS]  # Simple operators for string fields
#         operator = random.choice(possible_operators)
#         constraint = generate_constraint_from_solution(solution_product, field, operator)
#         if constraint:
#             constraints.append(constraint)
#
#     elif field == "price":
#         possible_operators = [ComparisonOperator.LESS_THAN, ComparisonOperator.GREATER_THAN, ComparisonOperator.LESS_EQUAL, ComparisonOperator.GREATER_EQUAL]  # Range operators for price
#         operator = random.choice(possible_operators)
#         # For price ranges, we might need two constraints.
#         # Let's generate one constraint relative to the solution product's price.
#         constraint1 = generate_constraint_from_solution(solution_product, field, operator)
#         if constraint1:
#             constraints.append(constraint1)
#             # Optionally, add a second constraint to form a range
#             if operator in [ComparisonOperator.GREATER_THAN, ComparisonOperator.GREATER_EQUAL]:
#                 # If constraint1 was > or >=, add a < or <= constraint
#                 constraint2 = generate_constraint_from_solution(solution_product, field, random.choice([ComparisonOperator.LESS_THAN, ComparisonOperator.LESS_EQUAL]))
#                 # Ensure constraint2 doesn't contradict constraint1
#                 if constraint2 and validate_criterion(solution_product.get(field), CriterionValue(value=constraint2["value"], operator=constraint2["operator"])):
#                     constraints.append(constraint2)
#
#     elif field == "rating":
#         possible_operators = [ComparisonOperator.GREATER_THAN, ComparisonOperator.GREATER_EQUAL]  # Ratings are often filtered by minimum
#         operator = random.choice(possible_operators)
#         constraint = generate_constraint_from_solution(solution_product, field, operator)
#         if constraint:
#             constraints.append(constraint)
#
#     # Can add more constraints here, e.g., combine category and rating, or brand and price
#
#     # Ensure the generated constraints actually match the solution product (redundant if generate_constraint_from_solution is perfect, but good safeguard)
#     valid_constraints = [c for c in constraints if validate_criterion(solution_product.get(c["field"]), CriterionValue(value=c["value"], operator=c["operator"]))]
#
#     return valid_constraints


def generate_search_query_constraints() -> list[dict[str, Any]]:
    """
    Generates constraints for product search queries.
    Returns constraints as structured data (list of dictionaries).
    """
    search_terms = [
        "kitchen appliances",
        "electronics",
        "Espresso Machine",
        "Wireless Earbuds",
        "Stand Mixer",
        "Portable Bluetooth Speaker",
        "cookware",
        "blender",
        "smart watch",
        "noise cancelling headphones",
        "by KitchenAid",
        "ChefPlus products",
    ]
    query = random.choice(search_terms)
    return [{"field": "query", "operator": ComparisonOperator.EQUALS, "value": query}]


def generate_cart_operation_constraints() -> list[dict[str, Any]]:
    """
    Generates constraints for adding items to the cart.
    Includes product identifier and quantity.
    Returns constraints as structured data (list of dictionaries).
    """
    if not PRODUCTS_DATA:
        return []

    # Pick a random product to add
    product_to_add = random.choice(PRODUCTS_DATA)

    constraints = []
    # Choose whether to refer by name or ID
    if random.random() > 0.5:
        constraints.append({"field": "item_name", "operator": ComparisonOperator.EQUALS, "value": product_to_add["title"]})
    else:
        constraints.append({"field": "item_id", "operator": ComparisonOperator.EQUALS, "value": product_to_add["id"]})

    # Add a quantity constraint (randomly between 1 and 5)
    quantity = random.randint(1, 5)
    constraints.append({"field": "quantity", "operator": ComparisonOperator.EQUALS, "value": quantity})

    return constraints


def generate_view_cart_constraints() -> list[dict[str, Any]]:
    """
    Generates constraints for viewing the cart.
    This action typically doesn't have constraints on cart contents itself.
    Returns an empty list.
    """
    return []  # Viewing the cart usually doesn't require specific constraints


def generate_checkout_constraints() -> list[dict[str, Any]]:
    """
    Generates constraints for initiating or proceeding to checkout.
    May include constraints on total items or total amount.
    Returns constraints as structured data (list of dictionaries).
    """
    constraints = []
    # These constraints often reflect the state of the cart at checkout.
    # Generating realistic values here would require knowing the cart state,
    # but for simple example generation, we can generate plausible values.

    # Randomly decide whether to include total item count constraint
    if random.random() > 0.5:
        total_items = random.randint(1, 10)  # Plausible number of items
        constraints.append({"field": "total_items", "operator": ComparisonOperator.EQUALS, "value": total_items})

    # Randomly decide whether to include total amount constraint
    if random.random() > 0.5:
        # Generate a plausible total amount based on some random products/quantities
        if PRODUCTS_DATA:
            sample_size = random.randint(1, min(5, len(PRODUCTS_DATA)))
            sample_products = random.sample(PRODUCTS_DATA, sample_size)
            # Calculate a dummy total amount
            dummy_total = sum(float(p["price"].replace("$", "")) * random.randint(1, 3) for p in sample_products if isinstance(p.get("price"), str) and p["price"].startswith("$"))
            constraints.append({"field": "total_amount", "operator": ComparisonOperator.EQUALS, "value": round(dummy_total, 2)})
        else:
            constraints.append({"field": "total_amount", "operator": ComparisonOperator.GREATER_THAN, "value": 50.00})  # Or a simple minimum

    return constraints


def generate_order_completion_constraints() -> list[dict[str, Any]]:
    """
    Generates constraints for completing an order.
    May include payment method, shipping details, or order reference.
    Returns constraints as structured data (list of dictionaries).
    """
    payment_methods = ["Credit Card", "PayPal", "Google Pay", "Apple Pay", "Saved Payment Method"]
    shipping_methods = ["standard", "express", "2-day", "next-day"]

    constraints = []

    # Randomly include payment method constraint
    if random.random() > 0.4:
        method = random.choice(payment_methods)
        constraints.append({"field": "payment_method", "operator": ComparisonOperator.EQUALS, "value": method})

    # Randomly include shipping method/speed constraint
    if random.random() > 0.4:
        method = random.choice(shipping_methods)
        constraints.append({"field": "shipping_method", "operator": ComparisonOperator.EQUALS, "value": method})

    # Randomly include an order ID constraint (if confirming a specific order)
    if random.random() > 0.8:  # Less frequent, as it's post-checkout
        dummy_order_id = str(random.randint(10000, 99999))
        constraints.append({"field": "order_id", "operator": ComparisonOperator.EQUALS, "value": dummy_order_id})

    return constraints


def generate_quantity_change_constraints() -> list[dict[str, Any]]:
    """
    Generates constraints for changing the quantity of an item in the cart.
    Includes product identifier and details about the quantity change.
    Returns constraints as structured data (list of dictionaries).
    """
    if not PRODUCTS_DATA:
        return []

    # Pick a random product that could be in the cart
    product_to_change = random.choice(PRODUCTS_DATA)

    constraints = []

    # Choose whether to refer by name or ID
    if random.random() > 0.5:
        constraints.append({"field": "item_name", "operator": ComparisonOperator.EQUALS, "value": product_to_change["title"]})
    else:
        constraints.append({"field": "item_id", "operator": ComparisonOperator.EQUALS, "value": product_to_change["id"]})

    # Determine the type of quantity change constraint
    change_type = random.choice(["new_quantity", "delta", "previous_and_new"])

    if change_type == "new_quantity":
        new_qty = random.randint(1, 5)
        constraints.append({"field": "new_quantity", "operator": ComparisonOperator.EQUALS, "value": new_qty})
    elif change_type == "delta":
        delta = random.randint(-2, 2)  # Can be increase or decrease
        if delta == 0:
            delta = 1  # Avoid zero change
        constraints.append({"field": "quantity_delta", "operator": ComparisonOperator.EQUALS, "value": delta})
    elif change_type == "previous_and_new":
        prev_qty = random.randint(1, 3)
        # Ensure new_qty is different from prev_qty
        new_qty = prev_qty
        while new_qty == prev_qty:
            new_qty = random.randint(1, 5)
        constraints.append({"field": "previous_quantity", "operator": ComparisonOperator.EQUALS, "value": prev_qty})
        constraints.append({"field": "new_quantity", "operator": ComparisonOperator.EQUALS, "value": new_qty})

    return constraints


def generate_carousel_scroll_constraints() -> list[dict[str, Any]]:
    """
    Generates constraints for scrolling a product carousel.
    Includes direction and carousel title.
    Returns constraints as structured data (list of dictionaries).
    """
    carousel_titles = ["Kitchen Appliances", "Electronics", "Best Sellers", "New Arrivals", "Recommended For You", "Trending Now"]
    directions = ["LEFT", "RIGHT"]

    constraints = []

    # Always include a title constraint
    title = random.choice(carousel_titles)
    constraints.append({"field": "title", "operator": ComparisonOperator.EQUALS, "value": title})

    # Randomly include a direction constraint
    if random.random() > 0.3:  # Include direction constraint about 70% of the time
        direction = random.choice(directions)
        constraints.append({"field": "direction", "operator": ComparisonOperator.EQUALS, "value": direction})

    return constraints
