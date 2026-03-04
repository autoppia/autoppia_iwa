from collections.abc import Callable
from typing import Any

from ..criterion_helper import ComparisonOperator
from ..operators import CONTAINS, EQUALS, IN_LIST, NOT_CONTAINS, NOT_EQUALS, NOT_IN_LIST
from ..shared_utils import constraints_exist_in_db


def _parse_bracketed_or_single(value_str: str, parse_item: Callable[[str], Any]) -> Any:
    """Parse 'value' or '[a, b, c]' format: if bracketed return list of parse_item results, else single parse_item result."""
    if "[" in value_str and "]" in value_str:
        return [parse_item(item.strip()) for item in value_str.strip("[]").split(", ")]
    return parse_item(value_str.strip())


def _parse_integer_value(value_str: str) -> int | list[int]:
    """Parse integer value, handling both single values and list format (e.g. '[1, 2, 3]')."""
    return _parse_bracketed_or_single(value_str, int)


def _parse_float_value(value_str: str) -> float | list[float]:
    """Parse float value, handling both single values and list format."""
    return _parse_bracketed_or_single(value_str, float)


def _parse_list_value(value_str: str) -> list[str] | str:
    """Parse list value, handling list format or plain string."""
    return _parse_bracketed_or_single(value_str, lambda x: x)


# Director field: filter operators by data type (list vs string)
_DIRECTOR_LIST_OPS = (IN_LIST, NOT_IN_LIST)
_DIRECTOR_STRING_OPS = (EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS)


def _valid_operators_for_field(field: str, valid_operators: list, solution_movie: dict) -> list:
    """Return valid operators for field; for 'director' filter by list vs string type."""
    if field != "director":
        return valid_operators
    if isinstance(solution_movie.get(field), list):
        return [op for op in valid_operators if op in _DIRECTOR_LIST_OPS]
    return [op for op in valid_operators if op in _DIRECTOR_STRING_OPS]


def _convert_value_by_field_type(field: str, value_str: str) -> Any:
    """Convert value string to the appropriate type for the field. Centralizes constraint value parsing."""
    if field in ["year", "duration"]:
        return _parse_integer_value(value_str)
    if field == "rating":
        return _parse_float_value(value_str)
    if field == "genres":
        return _parse_list_value(value_str)
    return value_str


def _parse_constraint_part(part: str) -> dict[str, Any]:
    """Parse a single constraint part (e.g. '1) year equals 2014') into a dict with field, operator, value."""
    clean_part = part.split(") ", 1)[1] if ") " in part else part
    field, rest = clean_part.split(" ", 1)
    op_value = rest.split(" ", 1)
    op = op_value[0]
    value_str = op_value[1]
    value = _convert_value_by_field_type(field, value_str)
    return {"field": field, "operator": ComparisonOperator(op), "value": value}


def parse_constraints_str(constraints_str: str) -> list[dict[str, Any]]:
    """
    Parses the constraints string into a list of dictionaries.
    Example input: "1) year equals 2014 AND 2) genres contains Sci-Fi"
    """
    if not constraints_str:
        return []
    return [_parse_constraint_part(part) for part in constraints_str.split(" AND ")]


def _format_constraint_value(value: Any) -> str:
    """Format a constraint value for string representation (list as '[a, b, c]', else str)."""
    if isinstance(value, list):
        return f"[{', '.join(map(str, value))}]"
    return str(value)


def _constraint_to_part(idx: int, constraint: dict[str, Any]) -> str:
    """Format a single constraint dict as 'idx) field operator value'."""
    field = constraint["field"]
    operator = constraint["operator"]
    value_str = _format_constraint_value(constraint["value"])
    return f"{idx}) {field} {operator.value} {value_str}"


def _build_constraints_string(constraint_list: list[dict[str, Any]]) -> str:
    """Build the constraint string from a list of constraint dicts (e.g. '1) year equals 2014 AND 2) genres contains Sci-Fi')."""
    return " AND ".join(_constraint_to_part(idx, c) for idx, c in enumerate(constraint_list, start=1))


def build_constraints_info(data: list[dict], max_attempts: int = 10) -> str | None:
    """
    Genera 1..3 constraints que existan en la base de películas
    partiendo de una película aleatoria, pero permitiendo múltiples soluciones.
    Retorna un texto que describe esas constraints.

    Ejemplo de retorno:
    "1) year equals 2014"
    """
    import random

    from .data import FIELD_OPERATORS_MAP_FILM
    from .generation_functions import generate_constraint_from_solution

    # Elegir una película aleatoria como punto de partida
    solution_movie = random.choice(data)
    # print(f"Película inicial seleccionada: {solution_movie['name']}")

    # Decidir cuántos constraints generar (1-3)
    num_constraints = random.randint(1, 3)

    # Seleccionar campos aleatorios para los constraints
    available_fields = list(FIELD_OPERATORS_MAP_FILM.keys())
    selected_fields = random.sample(available_fields, min(num_constraints, len(available_fields)))

    constraint_list = []

    for field in selected_fields:
        valid_operators = _valid_operators_for_field(field, FIELD_OPERATORS_MAP_FILM[field], solution_movie)
        if not valid_operators:
            continue  # Skip if no valid operators
        operator = random.choice(valid_operators)

        # Generar un constraint basado en el campo, operador y la película solución
        constraint = generate_constraint_from_solution(solution_movie, field, ComparisonOperator(operator), data)

        if constraint:
            constraint_list.append(constraint)

    # Verificar que hay al menos un constraint y que existan películas que cumplan todos
    if constraint_list and constraints_exist_in_db(data, constraint_list):
        return _build_constraints_string(constraint_list)

    # Si no se pudo crear constraints válidos, intentar de nuevo
    return build_constraints_info(data, max_attempts - 1) if max_attempts > 1 else None
