import random

from .data import PRODUCTS_DATA


def replace_products_placeholders(
    text: str,
) -> str:
    """
    Replaces placeholders in a text string with data from PRODUCTS_DATA.
    Recognizes placeholders like <title>, <category>, <brand>, <price>,
    as well as generic ones like <product_name>, <product_variant>.
    """
    products_data: list = PRODUCTS_DATA
    if not isinstance(text, str) or not products_data:
        return text

    product = random.choice(products_data)

    placeholder_to_key = {
        "<id>": "id",
        "<title>": "title",
        "<product_name>": "title",
        "<product_variant>": "title",
        "<price>": "price",
        "<category>": "category",
        "<product_category>": "category",
        "<rating>": "rating",
        "<brand>": "brand",
    }

    modified_text = text

    for placeholder, key in placeholder_to_key.items():
        if placeholder in modified_text and key in product:
            value = product[key]
            replacement = str(value)
            modified_text = modified_text.replace(placeholder, replacement)

    return modified_text
