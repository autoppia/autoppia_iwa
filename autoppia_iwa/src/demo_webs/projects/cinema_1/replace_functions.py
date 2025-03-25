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


def replace_film_func(text: str) -> str:
    if not isinstance(text, str):
        return text

    import random

    idx = random.randint(0, len(MOVIES_DATA) - 1)

    # Aseguramos que el índice esté dentro de los límites
    idx = idx % len(MOVIES_DATA)

    text = text.replace("<movie>", MOVIES_DATA[idx]["name"])

    return text
