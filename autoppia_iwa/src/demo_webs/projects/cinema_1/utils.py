from typing import Any

from ..criterion_helper import ComparisonOperator, CriterionValue, validate_criterion


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
        # Remove the numeric prefix (e.g., "1) ")
        clean_part = part.split(") ", 1)[1] if ") " in part else part

        # Split into field, operator, and value
        field, rest = clean_part.split(" ", 1)
        op_value = rest.split(" ", 1)
        op = op_value[0]
        value_str = op_value[1]

        # Convert value based on type
        if field in ["year", "duration"]:
            # For integer numeric fields
            value = [int(item) for item in value_str.strip("[]").split(", ")] if "[" in value_str and "]" in value_str else int(value_str)
        elif field == "rating":
            # For float numeric fields
            value = [float(item) for item in value_str.strip("[]").split(", ")] if "[" in value_str and "]" in value_str else float(value_str)
        elif field == "genres":
            # For list fields
            value = value_str.strip("[]").split(", ") if "[" in value_str and "]" in value_str else value_str
        else:
            # For text fields
            value = value_str

        constraints.append({"field": field, "operator": ComparisonOperator(op), "value": value})

    return constraints


def generate_and_add_constraints_to_use_case(use_case, data: list[dict], constraints_generator=None):
    """
    Generates constraints and adds them to a use case.

    Args:
        use_case: The use case to add constraints to
        data: The data to use for constraint generation (movies, products, etc.)
        constraints_generator: Custom constraint generator function (optional)

    Returns:
        The same use case, now with constraints
    """

    # If no generator is provided, use the default one
    if constraints_generator is None:
        constraints_generator = build_constraints_info

    # Generate the constraints string
    constraints_str = constraints_generator(data)

    if constraints_str:
        # Parse the constraints string into structured data
        constraints = parse_constraints_str(constraints_str)

        # Add the constraints to the use case
        use_case.add_constraints(constraints)

    return use_case


def constraints_exist_in_db(data: list[dict], constraints: list[dict]) -> bool:
    """
    Returns True if *at least* one item satisfies ALL constraints.
    """
    matching_items = [item for item in data if item_matches_all_constraints(item, constraints)]
    return len(matching_items) > 0


def item_matches_all_constraints(item: dict, constraints: list[dict]) -> bool:
    """
    Returns True if the item satisfies *all* the given constraints.
    Each constraint is a dict with keys: field, operator, value.
    """
    for c in constraints:
        field = c["field"]
        operator = c["operator"]
        value = c["value"]
        actual_value = item.get(field)

        # Create CriterionValue to use validate_criterion
        criterion = CriterionValue(value=value, operator=operator)

        if not validate_criterion(actual_value, criterion):
            return False
    return True


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

    # Decidir cuántos constraints generar (1-3)
    num_constraints = random.randint(1, 3)

    # Seleccionar campos aleatorios para los constraints
    available_fields = list(FIELD_OPERATORS_MAP_FILM.keys())
    selected_fields = random.sample(available_fields, min(num_constraints, len(available_fields)))

    constraint_list = []

    for field in selected_fields:
        # Obtener operadores válidos para este campo
        valid_operators = FIELD_OPERATORS_MAP_FILM[field]
        # Elegir un operador aleatorio
        operator = random.choice(valid_operators)

        # Generar un constraint basado en el campo, operador y la película solución
        constraint = generate_constraint_from_solution(solution_movie, field, ComparisonOperator(operator), data)

        if constraint:
            constraint_list.append(constraint)

    # Verificar que hay al menos un constraint y que existan películas que cumplan todos
    if constraint_list and constraints_exist_in_db(data, constraint_list):
        # Construir un string que describa cada constraint
        parts = []
        for idx, constraint in enumerate(constraint_list, start=1):
            f = constraint["field"]
            op = constraint["operator"]
            v = constraint["value"]

            # Formateo especial para listas
            v_str = f"[{', '.join(map(str, v))}]" if isinstance(v, list) else v

            parts.append(f"{idx}) {f} {op.value} {v_str}")

        # Crear el string de restricciones
        constraints_str = " AND ".join(parts)

        # Mostrar todas las películas que satisfacen las restricciones (solo para debug)
        [movie for movie in data if item_matches_all_constraints(movie, constraint_list)]

        # for movie in matching_movies:
        #     print(
        #         f"  - {movie['name']} ({movie['year']}) - Director: {movie['director']}")

        # Retornar solo el string de restricciones sin información adicional
        return constraints_str

    # Si no se pudo crear constraints válidos, intentar de nuevo
    return build_constraints_info(data, max_attempts - 1) if max_attempts > 1 else None
