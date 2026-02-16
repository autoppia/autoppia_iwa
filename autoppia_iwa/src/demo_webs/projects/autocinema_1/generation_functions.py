import random
from random import choice, sample
from typing import Any

from autoppia_iwa.src.demo_webs.projects.data_provider import resolve_v2_seed_from_url

from ..criterion_helper import ComparisonOperator, CriterionValue, validate_criterion
from ..shared_utils import create_constraint_dict
from .data import (
    ALL_GENRES,
    COMMENT_KEYWORDS,
    COMMENTER_NAMES,
    CONTACT_EMAILS,
    CONTACT_MESSAGES,
    CONTACT_NAMES,
    CONTACT_SUBJECTS,
    FIELD_OPERATORS_MAP_ADD_COMMENT,
    FIELD_OPERATORS_MAP_ADD_FILM,
    FIELD_OPERATORS_MAP_CONTACT,
    FIELD_OPERATORS_MAP_EDIT_FILM,
    FIELD_OPERATORS_MAP_EDIT_USER,
    FIELD_OPERATORS_MAP_FILM,
    FIELD_OPERATORS_MAP_FILTER_FILM,
    FIELD_OPERATORS_MAP_SEARCH_FILM,
    PROFILE_BIOS,
    PROFILE_LOCATIONS,
    PROFILE_NAMES,
    PROFILE_WEBSITES,
)
from .data_utils import fetch_data


async def _ensure_dataset(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None) -> dict:
    """Fetch full dataset if not provided or empty. Single source of truth for data loading."""
    if dataset is None or dataset == {}:
        seed = await resolve_v2_seed_from_url(task_url) if task_url else None
        return await fetch_data(seed_value=seed) or {}
    return dataset


async def _get_films_data(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None) -> list[dict]:
    """Extract films from the pre-loaded dataset, or fetch from server if not available."""
    data = await _ensure_dataset(task_url, dataset)
    if data and "films" in data:
        return data["films"]
    return []


def _generate_constraint_value(
    operator: ComparisonOperator,
    field_value: Any,
    field: str,
    dataset: list[dict],
) -> Any:
    """
    Generate a constraint value for a given operator, field, and dataset.
    Handles str, int, float, list (genres) for film/profile/contact data.
    """
    if operator == ComparisonOperator.EQUALS:
        if isinstance(field_value, list) and field_value:
            return choice(field_value)
        if isinstance(field_value, str):
            return field_value.strip()
        return field_value

    if operator == ComparisonOperator.NOT_EQUALS:
        if isinstance(field_value, int | float):
            others = [d.get(field) for d in dataset if d.get(field) is not None and d.get(field) != field_value]
            return choice(others) if others else (field_value + 1 if isinstance(field_value, int) else field_value + 0.1)
        if isinstance(field_value, str):
            field_value = field_value.strip()
            others = [d.get(field) for d in dataset if d.get(field) and d.get(field) != field_value]
            return choice(others) if others else (field_value + "x" if field_value else "other")
        return field_value

    if operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        field_value = field_value.strip()
        # Ensure substring has at least 2 chars for meaningful constraints (avoid "i", "e", etc.)
        min_len = 2
        if len(field_value) >= min_len:
            max_start = max(0, len(field_value) - min_len)
            start = random.randint(0, max_start)
            end = random.randint(start + min_len, len(field_value))
            return field_value[start:end]
        return field_value

    if operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        field_value = field_value.strip()
        for _ in range(100):
            test_str = "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(3))
            if test_str.lower() not in (field_value or "").lower():
                return test_str
        return "xyz"

    if operator == ComparisonOperator.CONTAINS and isinstance(field_value, list) and field_value:
        item = choice(field_value)
        return item.get("name", item) if isinstance(item, dict) else item

    if operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, list):
        all_vals = []
        for d in dataset:
            v = d.get(field)
            if isinstance(v, list):
                for x in v:
                    all_vals.append(x.get("name", x) if isinstance(x, dict) else x)
            elif v is not None:
                all_vals.append(v.get("name", v) if isinstance(v, dict) else v)
        field_set = {x.get("name", x) if isinstance(x, dict) else x for x in field_value}
        remaining = [v for v in all_vals if v not in field_set]
        return choice(remaining) if remaining else None

    if operator in (ComparisonOperator.GREATER_THAN, ComparisonOperator.LESS_THAN, ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL):
        if isinstance(field_value, int | float):
            delta = random.uniform(0.5, 2.0) if isinstance(field_value, float) else random.randint(1, 5)
            if operator == ComparisonOperator.GREATER_THAN:
                raw = field_value - delta
            elif operator == ComparisonOperator.LESS_THAN:
                raw = field_value + delta
            else:
                raw = field_value
            # Rating is 0-5 stars in autocinema: clamp so constraint is meaningful
            if field == "rating":
                raw = max(0.0, min(5.0, float(raw)))
            # Round floats to 1 decimal for readable constraints (avoid 6.180065492855112)
            if isinstance(raw, float):
                raw = round(raw, 1)
            return raw
        return field_value

    if operator == ComparisonOperator.IN_LIST and isinstance(field_value, list):
        all_vals = list({v for d in dataset for v in (d.get(field) if isinstance(d.get(field), list) else [])})
        if not all_vals:
            return [field_value[0]] if field_value else []
        random.shuffle(all_vals)
        subset = random.sample(all_vals, min(2, len(all_vals)))
        if field_value and field_value[0] not in subset:
            subset.append(field_value[0])
        return list(set(subset))

    if operator == ComparisonOperator.NOT_IN_LIST and isinstance(field_value, list):
        all_vals = list({v for d in dataset for v in (d.get(field) if isinstance(d.get(field), list) else [])})
        if field_value:
            all_vals = [v for v in all_vals if v not in field_value]
        return random.sample(all_vals, min(2, len(all_vals))) if all_vals else []

    return None


def _generate_constraints(
    dataset: list[dict],
    field_operators: dict,
    field_map: dict | None = None,
    min_constraints: int = 1,
    num_constraints: int | None = None,
    selected_fields: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Generates constraints based on the dataset and field operator mapping.
    DB first: dataset must contain valid entities; empty dataset returns no constraints.
    """
    if not dataset:
        return []
    all_constraints = []
    sample_data = choice(dataset)
    possible_fields = list(field_operators.keys())
    if selected_fields:
        possible_fields = [f for f in possible_fields if f in selected_fields]
    if not possible_fields:
        possible_fields = list(field_operators.keys())
    if num_constraints is not None:
        n = min(num_constraints, len(possible_fields))
        possible_fields = list(random.sample(possible_fields, n))
    if field_map is None:
        field_map = {}

    for field in possible_fields:
        allowed_ops = field_operators.get(field, [])
        if not allowed_ops:
            continue
        op = ComparisonOperator(choice(allowed_ops))
        new_field = field_map.get(field, field)
        field_value = None
        constraint_value = None
        if isinstance(new_field, dict):
            custom_dataset = new_field.get("dataset", [])
            new_field = new_field.get("field", field)
            if custom_dataset:
                field_value = choice(custom_dataset).get(new_field)
                if field_value is not None and new_field:
                    constraint_value = _generate_constraint_value(op, field_value, new_field, custom_dataset)
        else:
            lookup = new_field if isinstance(new_field, str) else field
            field_value = sample_data.get(lookup)
            if field_value is not None and constraint_value is None:
                constraint_value = _generate_constraint_value(op, field_value, lookup, dataset)

        if constraint_value is not None:
            all_constraints.append(create_constraint_dict(field, op, constraint_value))

    return all_constraints


def generate_registration_constraints(dataset: list[dict]):
    """
    Generates constraints specifically for film-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import parse_constraints_str

    constraints_str = "username equals newuser<web_agent_id> AND email equals newuser<web_agent_id>@gmail.com AND password equals password123"

    return parse_constraints_str(constraints_str)


def generate_login_constraints(dataset: list[dict]):
    """
    Generates constraints specifically for film-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import parse_constraints_str

    # Generar restricciones frescas basadas en los datos de películas
    constraints_str = "username equals <web_agent_id> AND password equals password123"

    return parse_constraints_str(constraints_str)


def generate_logout_constraints(dataset: list[dict]):
    """
    Generates constraints specifically for film-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import parse_constraints_str

    # Generar restricciones frescas basadas en los datos de películas
    constraints_str = "username equals <web_agent_id> AND password equals password123"
    return parse_constraints_str(constraints_str)


async def generate_search_film_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """Generate constraints for SEARCH_FILM: query equals/not_equals film name from DB."""
    from .utils import parse_constraints_str

    try:
        films = await _get_films_data(task_url, dataset)
        if not films:
            data = await _ensure_dataset(task_url, dataset)
            films = data.get("films", []) if data else []
            if not films:
                return parse_constraints_str("query equals The Matrix")
        search_dataset = [{"query": m["name"]} for m in films]
        constraints_list = _generate_constraints(search_dataset, FIELD_OPERATORS_MAP_SEARCH_FILM, num_constraints=1, selected_fields=["query"])
        return constraints_list if constraints_list else parse_constraints_str("query equals The Matrix")
    except Exception:
        return parse_constraints_str("query equals The Matrix")


# Core film fields for view/share/trailer/watchlist/delete use cases (DB first, semantic constraints)
FILM_CORE_FIELDS = ["name", "director", "year", "rating", "duration", "genres"]


async def generate_film_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """
    Generates constraints for generic film-related use cases using dynamic generation.
    Returns the constraints as structured data.
    """
    films = await _get_films_data(task_url, dataset)
    if not films:
        return []
    num_constraints = random.randint(1, 3)
    return _generate_constraints(films, FIELD_OPERATORS_MAP_FILM, num_constraints=num_constraints)


async def generate_film_detail_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """Generate constraints for FILM_DETAIL: film fields from DB (name, director, year, rating, duration, genres)."""
    films = await _get_films_data(task_url, dataset)
    if not films:
        return []
    num_constraints = random.randint(1, 3)
    return _generate_constraints(films, FIELD_OPERATORS_MAP_FILM, num_constraints=num_constraints, selected_fields=FILM_CORE_FIELDS)


async def generate_add_to_watchlist_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """Generate constraints for ADD_TO_WATCHLIST: film fields from DB (name, director, year, rating, duration, genres)."""
    films = await _get_films_data(task_url, dataset)
    if not films:
        return []
    num_constraints = random.randint(1, 3)
    return _generate_constraints(films, FIELD_OPERATORS_MAP_FILM, num_constraints=num_constraints, selected_fields=FILM_CORE_FIELDS)


async def generate_remove_from_watchlist_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """Generate constraints for REMOVE_FROM_WATCHLIST: film fields from DB (name, director, year, rating, duration, genres)."""
    films = await _get_films_data(task_url, dataset)
    if not films:
        return []
    num_constraints = random.randint(1, 3)
    return _generate_constraints(films, FIELD_OPERATORS_MAP_FILM, num_constraints=num_constraints, selected_fields=FILM_CORE_FIELDS)


async def generate_share_film_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """Generate constraints for SHARE_MOVIE: film fields from DB (name, director, year, rating, duration, genres)."""
    films = await _get_films_data(task_url, dataset)
    if not films:
        return []
    num_constraints = random.randint(1, 3)
    return _generate_constraints(films, FIELD_OPERATORS_MAP_FILM, num_constraints=num_constraints, selected_fields=FILM_CORE_FIELDS)


async def generate_watch_trailer_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """Generate constraints for WATCH_TRAILER: film fields from DB (name, director, year, rating, duration, genres)."""
    films = await _get_films_data(task_url, dataset)
    if not films:
        return []
    num_constraints = random.randint(1, 3)
    return _generate_constraints(films, FIELD_OPERATORS_MAP_FILM, num_constraints=num_constraints, selected_fields=FILM_CORE_FIELDS)


async def generate_delete_film_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """Generate constraints for DELETE_FILM: film fields from DB (name, director, year, rating, duration, genres)."""
    films = await _get_films_data(task_url, dataset)
    if not films:
        return []
    num_constraints = random.randint(1, 3)
    return _generate_constraints(films, FIELD_OPERATORS_MAP_FILM, num_constraints=num_constraints, selected_fields=FILM_CORE_FIELDS)


def generate_contact_constraints() -> list:
    """Generate constraints for CONTACT from map and synthetic dataset (data.py pools)."""
    contact_dataset = [
        {
            "name": choice(CONTACT_NAMES),
            "email": choice(CONTACT_EMAILS),
            "subject": choice(CONTACT_SUBJECTS),
            "message": choice(CONTACT_MESSAGES),
        }
        for _ in range(15)
    ]
    return _generate_constraints(contact_dataset, FIELD_OPERATORS_MAP_CONTACT, num_constraints=random.randint(1, 4))


def _build_filter_film_dataset(films: list[dict]) -> list[dict]:
    """Build dataset for FILTER_FILM: one row per (genre_name, year) to match FilterFilmEvent payload."""
    rows = []
    for f in films:
        year = f.get("year")
        if year is None:
            continue
        for g in f.get("genres") or []:
            name = g if isinstance(g, str) else (g.get("name") if isinstance(g, dict) else None)
            if name:
                rows.append({"genre_name": name, "year": year})
    return rows if rows else [{"genre_name": "Drama", "year": 2020}]


async def generate_film_filter_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """Generate constraints for FILTER_FILM: genre_name and/or year (aligned with FilterFilmEvent)."""
    films = await _get_films_data(task_url, dataset)
    if not films:
        return []
    filter_dataset = _build_filter_film_dataset(films)
    generation_type = choice(["single_genre", "single_year", "genre_and_year"])
    if generation_type == "single_genre":
        return _generate_constraints(filter_dataset, FIELD_OPERATORS_MAP_FILTER_FILM, num_constraints=1, selected_fields=["genre_name"])
    if generation_type == "single_year":
        return _generate_constraints(filter_dataset, FIELD_OPERATORS_MAP_FILTER_FILM, num_constraints=1, selected_fields=["year"])
    return _generate_constraints(filter_dataset, FIELD_OPERATORS_MAP_FILTER_FILM, num_constraints=2, selected_fields=["genre_name", "year"])


def generate_constraint_from_solution(movie: dict, field: str, operator: ComparisonOperator, movies_data: list[dict]) -> dict[str, Any] | None:
    """
    Generate one constraint (field, operator, value) that the solution movie satisfies.
    Delegates value generation to _generate_constraint_value (map-driven, no hardcoded fields).
    """
    field_value = movie.get(field)
    value = _generate_constraint_value(operator, field_value, field, movies_data)
    if value is None:
        return None
    constraint = {"field": field, "operator": operator, "value": value}
    criterion = CriterionValue(value=value, operator=operator)
    if validate_criterion(movie.get(field), criterion):
        return constraint
    return None


async def generate_add_comment_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """Generate constraints for ADD_COMMENT from map and dataset (movie_name from films, others from data.py pools)."""
    films = await _get_films_data(task_url, dataset)
    if not films:
        return []
    comment_dataset = [
        {
            "movie_name": m["name"],
            "commenter_name": choice(COMMENTER_NAMES),
            "content": choice(COMMENT_KEYWORDS),
        }
        for m in films
    ]
    n = min(choice([1, 2, 3]), len(FIELD_OPERATORS_MAP_ADD_COMMENT))
    return _generate_constraints(comment_dataset, FIELD_OPERATORS_MAP_ADD_COMMENT, num_constraints=n)


async def generate_edit_film_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """Generate constraints for EDIT_FILM: name from base movie + 1-4 editable fields from map (DB first)."""
    try:
        films = await _get_films_data(task_url, dataset)
        if not films:
            data = await _ensure_dataset(task_url, dataset)
            films = data.get("films", []) if data else []
            if not films:
                return [create_constraint_dict("name", ComparisonOperator.EQUALS, "The Matrix")]
        base_movie = choice(films)
        constraints = [create_constraint_dict("name", ComparisonOperator.EQUALS, base_movie["name"])]
        editable_fields = list(FIELD_OPERATORS_MAP_EDIT_FILM.keys())
        n = min(choice([1, 2, 3, 4]), len(editable_fields))
        selected = list(sample(editable_fields, n))
        extra = _generate_constraints([base_movie], FIELD_OPERATORS_MAP_EDIT_FILM, num_constraints=n, selected_fields=selected)
        constraints.extend(extra)
        return constraints
    except Exception:
        return [create_constraint_dict("name", ComparisonOperator.EQUALS, "The Matrix")]


def generate_add_film_constraints(dataset: list[dict]):
    """Generate constraints for ADD_FILM: 1-4 fields from map, values from dataset (sync; no task_url)."""
    if not dataset or not isinstance(dataset, dict):
        return _generate_constraints([], FIELD_OPERATORS_MAP_ADD_FILM, num_constraints=1) or [create_constraint_dict("genres", ComparisonOperator.EQUALS, choice(ALL_GENRES))]
    films = dataset.get("films", [])
    if not films:
        return _generate_constraints([], FIELD_OPERATORS_MAP_ADD_FILM, num_constraints=1) or [create_constraint_dict("genres", ComparisonOperator.EQUALS, choice(ALL_GENRES))]
    n = min(choice([1, 2, 3, 4]), len(FIELD_OPERATORS_MAP_ADD_FILM))
    return _generate_constraints(films, FIELD_OPERATORS_MAP_ADD_FILM, num_constraints=n)


def generate_edit_profile_constraints(dataset: list[dict]):
    """Generate constraints for EDIT_USER: fixed username/password + profile fields from map (data.py pools)."""
    profile_dataset = [
        {
            "first_name": choice(PROFILE_NAMES),
            "last_name": choice(PROFILE_NAMES),
            "bio": choice(PROFILE_BIOS),
            "location": choice(PROFILE_LOCATIONS),
            "website": choice(PROFILE_WEBSITES),
            "favorite_genres": choice(ALL_GENRES),
        }
        for _ in range(12)
    ]
    editable_fields = list(FIELD_OPERATORS_MAP_EDIT_USER.keys())
    n = min(choice([1, 2, 3]), len(editable_fields))
    selected = list(sample(editable_fields, n))
    if "website" not in selected:
        selected.append("website")
    profile_constraints = _generate_constraints(profile_dataset, FIELD_OPERATORS_MAP_EDIT_USER, num_constraints=len(selected), selected_fields=selected)
    return [create_constraint_dict("username", ComparisonOperator.EQUALS, "<web_agent_id>"), create_constraint_dict("password", ComparisonOperator.EQUALS, "password123"), *profile_constraints]
