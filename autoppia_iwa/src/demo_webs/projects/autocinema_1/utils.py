from typing import Any

from ..criterion_helper import ComparisonOperator
from ..operators import CONTAINS, EQUALS, IN_LIST, NOT_CONTAINS, NOT_EQUALS, NOT_IN_LIST
from ..shared_utils import constraints_exist_in_db, item_matches_all_constraints

# =============================================================================
#                            HELPER FUNCTIONS
# =============================================================================

# --------------------------------------------------------------------- #
#  VALUE CONVERSION HELPERS
# ---------------------------------------------------------------------


def _parse_integer_value(value_str: str) -> int | list[int]:
    """Parse integer value, handling both single values and lists."""
    if "[" in value_str and "]" in value_str:
        return [int(item) for item in value_str.strip("[]").split(", ")]
    return int(value_str)


def _parse_float_value(value_str: str) -> float | list[float]:
    """Parse float value, handling both single values and lists."""
    if "[" in value_str and "]" in value_str:
        return [float(item) for item in value_str.strip("[]").split(", ")]
    return float(value_str)


def _parse_list_value(value_str: str) -> str | list[str]:
    """Parse list value, handling both single values and lists."""
    if "[" in value_str and "]" in value_str:
        return value_str.strip("[]").split(", ")
    return value_str


def _convert_value_by_field_type(field: str, value_str: str) -> Any:
    """Convert value string to appropriate type based on field."""
    if field in ["year", "duration"]:
        return _parse_integer_value(value_str)
    if field == "rating":
        return _parse_float_value(value_str)
    if field == "genres":
        return _parse_list_value(value_str)
    return value_str


def _parse_constraint_part(part: str) -> dict[str, Any]:
    """Parse a single constraint part into a dictionary."""
    # Remove the numeric prefix (e.g., "1) ")
    clean_part = part.split(") ", 1)[1] if ") " in part else part

    # Split into field, operator, and value
    field, rest = clean_part.split(" ", 1)
    op_value = rest.split(" ", 1)
    op = op_value[0]
    value_str = op_value[1]

    # Convert value based on type
    value = _convert_value_by_field_type(field, value_str)

    return {"field": field, "operator": ComparisonOperator(op), "value": value}


# =============================================================================
#                            MAIN FUNCTIONS
# =============================================================================


def parse_constraints_str(constraints_str: str) -> list[dict[str, Any]]:
    """
    Parses the constraints string into a list of dictionaries.
    Example input: "1) year equals 2014 AND 2) genres contains Sci-Fi"
    """
    if not constraints_str:
        return []

    constraints = []
    parts = constraints_str.split(" AND ")

    for part in parts:
        constraint = _parse_constraint_part(part)
        constraints.append(constraint)

    return constraints


# --------------------------------------------------------------------- #
#  CONSTRAINT STRING BUILDING HELPERS
# ---------------------------------------------------------------------


def _format_constraint_value(value: Any) -> str:
    """Format constraint value for string representation."""
    if isinstance(value, list):
        return f"[{', '.join(map(str, value))}]"
    return str(value)


def _build_constraints_string(constraint_list: list[dict[str, Any]]) -> str:
    """Build constraints string from constraint list."""
    parts = []
    for idx, constraint in enumerate(constraint_list, start=1):
        field = constraint["field"]
        operator = constraint["operator"]
        value = constraint["value"]
        value_str = _format_constraint_value(value)
        parts.append(f"{idx}) {field} {operator.value} {value_str}")
    return " AND ".join(parts)


def _get_valid_operators_for_director(field: str, solution_movie: dict, valid_operators: list) -> list:
    """Get valid operators for director field based on data type."""
    if field != "director":
        return valid_operators
    
    # Check if director is a list (multiple directors) or string (single director)
    if isinstance(solution_movie.get(field), list):
        # Multiple directors: use list operators
        return [op for op in valid_operators if op in [IN_LIST, NOT_IN_LIST]]
    # Single director: use string operators
    return [op for op in valid_operators if op in [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]]


def _generate_constraints_for_fields(
    solution_movie: dict,
    selected_fields: list[str],
    data: list[dict],
) -> list[dict[str, Any]]:
    """Generate constraints for selected fields."""
    import random
    
    from .data import FIELD_OPERATORS_MAP_FILM
    from .generation_functions import generate_constraint_from_solution
    
    constraint_list = []
    
    for field in selected_fields:
        # Obtener operadores válidos para este campo
        valid_operators = FIELD_OPERATORS_MAP_FILM[field]
        
        # Special handling for director: select operators based on data type
        valid_operators = _get_valid_operators_for_director(field, solution_movie, valid_operators)
        
        # Elegir un operador aleatorio
        if not valid_operators:
            continue  # Skip if no valid operators
        operator = random.choice(valid_operators)
        
        # Generar un constraint basado en el campo, operador y la película solución
        constraint = generate_constraint_from_solution(solution_movie, field, ComparisonOperator(operator), data)
        
        if constraint:
            constraint_list.append(constraint)
    
    return constraint_list


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

    # Elegir una película aleatoria como punto de partida
    solution_movie = random.choice(data)
    # print(f"Película inicial seleccionada: {solution_movie['name']}")

    # Decidir cuántos constraints generar (1-3)
    num_constraints = random.randint(1, 3)

    # Seleccionar campos aleatorios para los constraints
    available_fields = list(FIELD_OPERATORS_MAP_FILM.keys())
    selected_fields = random.sample(available_fields, min(num_constraints, len(available_fields)))

    # Generar constraints para los campos seleccionados
    constraint_list = _generate_constraints_for_fields(solution_movie, selected_fields, data)

    # Verificar que hay al menos un constraint y que existan películas que cumplan todos
    if constraint_list and constraints_exist_in_db(data, constraint_list):
        # Construir un string que describa cada constraint
        constraints_str = _build_constraints_string(constraint_list)

        # Mostrar todas las películas que satisfacen las restricciones (solo para debug)
        # print(f"Restricciones generadas: {constraints_str}")
        # print(f"Películas que satisfacen las restricciones ({len(matching_movies)}):")
        # for movie in matching_movies:
        #     print(f"  - {movie['name']} ({movie['year']}) - Director: {movie['director']}")

        # Retornar solo el string de restricciones sin información adicional
        return constraints_str

    # Si no se pudo crear constraints válidos, intentar de nuevo
    return build_constraints_info(data, max_attempts - 1) if max_attempts > 1 else None
