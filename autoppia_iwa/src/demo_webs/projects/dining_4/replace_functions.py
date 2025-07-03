import random

from ..shared_utils import generate_mock_date_strings, generate_mock_dates
from .data import RESTAURANT_DATA, RESTAURANT_PEOPLE_COUNTS, RESTAURANT_TIMES, SCROLL_DIRECTIONS


def replace_restaurant_placeholders(
    text: str,
) -> str:
    """
    Replaces placeholders in a text string with data from RESTAURANT_DATA
    and other relevant mock data (dates, times, people counts).
    Recognizes placeholders like <restaurant_name>, <cuisine_type>, <location_hint>,
    <date_description>, <time_description>, <people_count>, <occasion_type>,
    <phone_number>, <email>, <special_request>, <direction>, <count>, <item_type>.
    """
    restaurants_data: list = RESTAURANT_DATA
    if not isinstance(text, str) or not restaurants_data:
        return text

    restaurant = random.choice(restaurants_data)

    placeholder_replacements = {
        # Restaurant-specific placeholders
        "<restaurant_id>": lambda: restaurant["id"],
        "<restaurant_name>": lambda: restaurant["name"],
        "<cuisine_type>": lambda: random.choice(restaurant.get("cuisine", ["generic"])),
        "<rating>": lambda: str(restaurant.get("rating", random.randint(3, 5))),
        "<price_range>": lambda: restaurant.get("price_range", "moderate"),
        # Date, Time, People placeholders
        "<time_description>": lambda: random.choice(RESTAURANT_TIMES) if RESTAURANT_TIMES else "02:00 PM",
        "<selected_time>": lambda: random.choice(RESTAURANT_TIMES) if RESTAURANT_TIMES else "02:00 PM",
        "<people_count>": lambda: str(random.choice(RESTAURANT_PEOPLE_COUNTS)) if RESTAURANT_PEOPLE_COUNTS else "2",
        "<date_description>": lambda: generate_mock_date_strings(generate_mock_dates()),
        "<selected_date>": lambda: generate_mock_date_strings(generate_mock_dates()),
        # Scroll view placeholders
        "<direction>": lambda: random.choice(SCROLL_DIRECTIONS),
        "<count>": lambda: str(random.choice(RESTAURANT_PEOPLE_COUNTS)),
    }

    modified_text = text

    sorted_placeholders = sorted(placeholder_replacements.keys(), key=len, reverse=True)

    for placeholder in sorted_placeholders:
        if placeholder in modified_text:
            replacement_value = placeholder_replacements[placeholder]()
            modified_text = modified_text.replace(placeholder, str(replacement_value))

    return modified_text
