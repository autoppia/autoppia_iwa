from .data import MOVIES_DATA


def login_replace_func(text: str) -> str:
    if not isinstance(text, str):
        return text

    replacements = {"<username>": "user<web_agent_id>", "<password>": "password123"}

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text


def register_replace_func(text: str) -> str:
    if not isinstance(text, str):
        return text

    replacements = {"<username>": "newuser<web_agent_id>", "<email>": "newuser<web_agent_id>@gmail.com", "<password>": "password123"}

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text


def replace_film_placeholders(text: str, movies_data: list) -> str:
    """Replaces placeholders in the text with values from a random movie in the dataset."""
    if not isinstance(text, str) or not movies_data:
        return text
    import random

    movie = random.choice(movies_data)
    # Replace placeholders dynamically
    for key, value in movie.items():
        placeholder = f"<{key}>"
        if placeholder in text:
            text = text.replace(placeholder, str(value))

    if "<movie>" in text:
        text = text.replace("<movie>", movie["name"])

    return text


def replace_film_placeholders_func(text: str) -> str:
    return replace_film_placeholders(text, MOVIES_DATA)
