import random

from autoppia_iwa.src.web_agents.classes import DEFAULT_PASSWORD

from .data_utils import fetch_data


async def login_and_product_replace_func(
    text: str,
    seed_value: int | None = None,
    dataset: list | dict | None = None,
    constraints: list[dict] | None = None,
    **kwargs,
) -> str:
    """Apply login placeholders then film placeholders. Use for auth-required film use cases (EDIT_FILM, ADD_FILM, ADD_TO_WATCHLIST, REMOVE_FROM_WATCHLIST)."""
    text = login_replace_func(text, constraints=constraints, **kwargs)
    return await replace_products_placeholders(text, seed_value=seed_value, dataset=dataset)


def login_replace_func(text: str, constraints: list[dict] | None = None, **kwargs) -> str:
    if not isinstance(text, str):
        return text

    replacements = {"<username>": "user<web_agent_id>", "<password>": DEFAULT_PASSWORD}

    # Basic replacements
    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    # Generic replacements from constraints (for EDIT_USER profiles, etc.)
    if constraints:
        for c in constraints:
            field = c.get("field")
            value = c.get("value")
            if field and value is not None:
                placeholder = f"<{field}>"
                if placeholder in text:
                    text = text.replace(placeholder, str(value))

    return text


def register_replace_func(text: str, **kwargs) -> str:
    if not isinstance(text, str):
        return text

    replacements = {"<username>": "newuser<web_agent_id>", "<email>": "newuser<web_agent_id>@gmail.com", "<password>": DEFAULT_PASSWORD}

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text


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
