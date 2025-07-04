import random

from .data import CLIENT_DATA, MATTERS_DATA


def replace_placeholders(
    text: str,
) -> str:
    """
    Replaces placeholders in a text string with data from RESTAURANT_DATA
    and other relevant mock data (dates, times, people counts).
    Recognizes placeholders like <restaurant_name>, <cuisine_type>, <location_hint>,
    <date_description>, <time_description>, <people_count>, <occasion_type>,
    <phone_number>, <email>, <special_request>, <direction>, <count>, <item_type>.
    """
    matters_data: list = MATTERS_DATA
    if not isinstance(text, str) or not matters_data:
        return text

    matter = random.choice(matters_data)
    client_data: list = CLIENT_DATA
    random.choice(client_data)
    # selected = random.choice(MATTERS_DATA)
    placeholder_replacements = {
        "<mattername>": lambda: matter["name"],
        "<clientname>": lambda: matter["client"],
        "<status>": lambda: matter["status"],
        "<updated>": lambda: matter["updated"],
        # email, status, matters placeholders
        "<matters>": lambda: matter["matters"],
        "<email>": lambda: matter["email"],
    }

    modified_text = text

    sorted_placeholders = sorted(placeholder_replacements.keys(), key=len, reverse=True)

    for placeholder in sorted_placeholders:
        if placeholder in modified_text:
            replacement_value = placeholder_replacements[placeholder]()
            modified_text = modified_text.replace(placeholder, str(replacement_value))

    return modified_text
