from autoppia_iwa.src.demo_webs.projects.autocinema_1.data_utils import fetch_data


def _film_name_from_constraints(constraints: list[dict] | None) -> str | None:
    """
    Extract film name for <movie> placeholder from constraints so prompt matches validation.
    - field 'name': EDIT_FILM, FILM_DETAIL, etc.
    - field 'query': SEARCH_FILM (search query is the film title).
    """
    if not constraints:
        return None
    for c in constraints:
        field = c.get("field")
        if field == "name" or field == "query":
            val = c.get("value")
            if val is not None:
                return str(val)
    return None


async def replace_film_placeholders(
    text: str,
    seed_value: int | None = None,
    dataset: list[dict] | dict | None = None,
    constraints: list[dict] | None = None,
) -> str:
    if not isinstance(text, str):
        return text

    movies_data = dataset if dataset is not None else await fetch_data(seed_value=seed_value)
    if not movies_data:
        return text

    import random
    import re

    # Use film from constraints so prompt matches validation (e.g. EDIT_FILM name equals Gladiator)
    constraint_film_name = _film_name_from_constraints(constraints)
    movie = None
    if constraint_film_name:
        movie = next((m for m in movies_data if m.get("name") == constraint_film_name), None)
    if movie is None:
        movie = random.choice(movies_data)

    special_placeholders = {
        "<decade>": None,
    }
    all_placeholders = re.findall(r"<(\w+)>", text)

    if "decade" in all_placeholders:
        decades = set()
        for m in movies_data:
            if "year" in m:
                decade = (m["year"] // 10) * 10
                decades.add(decade)

        if decades:
            selected_decade = random.choice(list(decades))
            special_placeholders["<decade>"] = str(selected_decade // 10)

            decade_movies = [m for m in movies_data if m.get("year", 0) >= selected_decade and m.get("year", 0) < selected_decade + 10]
            if decade_movies:
                movies_data = decade_movies
                # Re-resolve movie if we narrowed the list and constraint film is in it
                if constraint_film_name:
                    movie = next((m for m in movies_data if m.get("name") == constraint_film_name), None)
                if movie is None:
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
        # Use constraint value so prompt matches validation (EDIT_FILM name, SEARCH_FILM query)
        text = text.replace("<movie>", constraint_film_name if constraint_film_name else movie["name"])

    if "<duration>" in text:
        text = text.replace("<duration>", str(movie.get("duration", "120")))

    return text
