import random

from .data_utils import fetch_data


async def replace_products_placeholders(
    text: str,
    seed_value: int | None = None,
    dataset: list[dict] | None = None,
) -> str:
    """
    Replaces placeholders in a text string with data from API.
    Recognizes placeholders like <title>, <category>, <brand>, <price>,
    as well as generic ones like <product_name>, <product_variant>.
    """
    if not isinstance(text, str):
        return text

    products_data = dataset if dataset is not None else await fetch_data(seed_value=seed_value)
    if not products_data:
        return text

    product = random.choice(products_data)

    placeholder_to_key = {
        "<id>": "id",
        "<product_id>": "id",
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
