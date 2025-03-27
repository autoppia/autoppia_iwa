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


def replace_film_placeholders(
    text: str,
) -> str:
    movies_data: list = MOVIES_DATA
    if not isinstance(text, str) or not movies_data:
        return text

    import random
    import re

    special_placeholders = {
        "<decade>": None,
    }
    all_placeholders = re.findall(r"<(\w+)>", text)

    if "decade" in all_placeholders:
        decades = set()
        for movie in movies_data:
            if "year" in movie:
                decade = (movie["year"] // 10) * 10
                decades.add(decade)

        if decades:
            selected_decade = random.choice(list(decades))
            special_placeholders["<decade>"] = str(selected_decade // 10)

            decade_movies = [m for m in movies_data if m.get("year", 0) >= selected_decade and m.get("year", 0) < selected_decade + 10]
            if decade_movies:
                movies_data = decade_movies

    movie = random.choice(movies_data)

    for placeholder, value in special_placeholders.items():
        if value and placeholder in text:
            text = text.replace(placeholder, value)

    for key, value in movie.items():
        placeholder = f"<{key}>"
        if placeholder in text:
            text = text.replace(placeholder, random.choice(value)) if isinstance(value, list) and value else text.replace(placeholder, str(value))

    if "<genre>" in text and movie.get("genres"):
        text = text.replace("<genre>", random.choice(movie["genres"]))

    if "<movie>" in text:
        text = text.replace("<movie>", movie["name"])

    if "<duration>" in text:
        text = text.replace("<duration>", str(movie.get("duration", "120")))

    return text
