import random

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


async def _get_products_data(seed_value: int | None = None, count: int = 100) -> list[dict]:
    """Fetch products data from API."""
    from .main import FRONTEND_PORT_INDEX, omnizone_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{omnizone_project.id}"

    items = await load_dataset_data(
        backend_url=omnizone_project.backend_url,
        project_key=project_key,
        entity_type="products",
        seed_value=seed_value if seed_value is not None else 1,
        limit=count,
    )
    if items:
        return items
    return []


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

    products_data = dataset if dataset is not None else await _get_products_data(seed_value=seed_value)
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
