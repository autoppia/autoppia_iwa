from autoppia_iwa.src.demo_webs.projects.autocinema_1.data_utils import fetch_data


async def login_and_film_replace_func(
    text: str,
    seed_value: int | None = None,
    dataset: list | dict | None = None,
    constraints: list[dict] | None = None,
    **kwargs,
) -> str:
    """Apply login placeholders then film placeholders. Use for auth-required film use cases (EDIT_FILM, ADD_FILM, ADD_TO_WATCHLIST, REMOVE_FROM_WATCHLIST)."""
    text = login_replace_func(text, constraints=constraints, **kwargs)
    return await replace_film_placeholders(text, seed_value=seed_value, dataset=dataset, constraints=constraints, **kwargs)


def login_replace_func(text: str, constraints: list[dict] | None = None, **kwargs) -> str:
    if not isinstance(text, str):
        return text

    replacements = {"<username>": "user<web_agent_id>", "<password>": "password123"}

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

    replacements = {"<username>": "newuser<web_agent_id>", "<email>": "newuser<web_agent_id>@gmail.com", "<password>": "password123"}

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text


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


# =============================================================================
#                            HELPER FUNCTIONS
# =============================================================================

# --------------------------------------------------------------------- #
#  DATA LOADING HELPERS
# ---------------------------------------------------------------------


async def _load_movies_data(seed_value: int | None, dataset: list[dict] | dict | None) -> list[dict]:
    """Load movies data from dataset or fetch from server."""
    if dataset is not None:
        # Task generator passes full project dict {"movies": [...], "users": [...]} (API key); use movies list
        return dataset.get("movies", []) if isinstance(dataset, dict) else dataset
    return await fetch_data(seed_value=seed_value) or []


# --------------------------------------------------------------------- #
#  MOVIE SELECTION HELPERS
# ---------------------------------------------------------------------


def _select_movie_from_constraints(movies_data: list[dict], constraint_film_name: str | None) -> dict | None:
    """Select movie matching constraint film name if available."""
    if not constraint_film_name:
        return None
    return next((m for m in movies_data if m.get("name") == constraint_film_name), None)


def _select_movie(movies_data: list[dict], constraint_film_name: str | None) -> dict:
    """Select movie from constraints or randomly."""
    import random
    
    movie = _select_movie_from_constraints(movies_data, constraint_film_name)
    if movie is None:
        movie = random.choice(movies_data)
    return movie


# --------------------------------------------------------------------- #
#  DECADE HANDLING HELPERS
# ---------------------------------------------------------------------


def _extract_decades(movies_data: list[dict]) -> set[int]:
    """Extract unique decades from movies data."""
    decades = set()
    for m in movies_data:
        if "year" in m:
            decade = (m["year"] // 10) * 10
            decades.add(decade)
    return decades


def _filter_movies_by_decade(movies_data: list[dict], selected_decade: int) -> list[dict]:
    """Filter movies by selected decade."""
    return [
        m for m in movies_data
        if m.get("year", 0) >= selected_decade and m.get("year", 0) < selected_decade + 10
    ]


def _handle_decade_placeholder(
    text: str,
    movies_data: list[dict],
) -> tuple[str, list[dict], dict]:
    """Handle decade placeholder and filter movies accordingly."""
    import random
    import re
    
    all_placeholders = re.findall(r"<(\w+)>", text)
    if "decade" not in all_placeholders:
        return text, movies_data, {}
    
    decades = _extract_decades(movies_data)
    if not decades:
        return text, movies_data, {}
    
    selected_decade = random.choice(list(decades))
    decade_value = str(selected_decade // 10)
    
    decade_movies = _filter_movies_by_decade(movies_data, selected_decade)
    if not decade_movies:
        return text, movies_data, {"<decade>": decade_value}
    
    return text, decade_movies, {"<decade>": decade_value}


# --------------------------------------------------------------------- #
#  PLACEHOLDER REPLACEMENT HELPERS
# ---------------------------------------------------------------------


def _replace_movie_field_placeholders(text: str, movie: dict) -> str:
    """Replace movie field placeholders in text."""
    import random
    
    for key, value in movie.items():
        placeholder = f"<{key}>"
        if placeholder in text:
            if isinstance(value, list) and value:
                text = text.replace(placeholder, random.choice(value))
            else:
                text = text.replace(placeholder, str(value))
    return text


def _replace_special_placeholders(text: str, movie: dict, constraint_film_name: str | None) -> str:
    """Replace special placeholders like genre, movie, duration."""
    import random
    
    if "<genre>" in text and movie.get("genres"):
        text = text.replace("<genre>", random.choice(movie["genres"]))
    
    if "<movie>" in text:
        # Use constraint value so prompt matches validation (EDIT_FILM name, SEARCH_FILM query)
        movie_name = constraint_film_name if constraint_film_name else movie["name"]
        text = text.replace("<movie>", movie_name)
    
    if "<duration>" in text:
        text = text.replace("<duration>", str(movie.get("duration", "120")))
    
    return text


# =============================================================================
#                            MAIN FUNCTION
# =============================================================================


async def replace_film_placeholders(
    text: str,
    seed_value: int | None = None,
    dataset: list[dict] | dict | None = None,
    constraints: list[dict] | None = None,
) -> str:
    """Replace film-related placeholders in text with actual movie data."""
    if not isinstance(text, str):
        return text

    movies_data = await _load_movies_data(seed_value, dataset)
    if not movies_data:
        return text

    # Use film from constraints so prompt matches validation (e.g. EDIT_FILM name equals Gladiator)
    constraint_film_name = _film_name_from_constraints(constraints)
    
    # Handle decade placeholder if present
    text, filtered_movies, special_placeholders = _handle_decade_placeholder(text, movies_data)
    
    # Select movie from filtered list
    movie = _select_movie(filtered_movies, constraint_film_name)
    
    # Replace special placeholders
    for placeholder, value in special_placeholders.items():
        if value and placeholder in text:
            text = text.replace(placeholder, value)
    
    # Replace movie field placeholders
    text = _replace_movie_field_placeholders(text, movie)
    
    # Replace special placeholders (genre, movie, duration)
    text = _replace_special_placeholders(text, movie, constraint_film_name)

    return text
