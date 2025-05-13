from ..criterion_helper import ComparisonOperator
from ..shared_utils import constraints_exist_in_db


def build_constraints_info(data: list[dict], max_attempts: int = 10) -> str | None:
    """
    Genera 1..3 constraints que existan en la base de películas
    partiendo de una película aleatoria, pero permitiendo múltiples soluciones.
    Retorna un texto que describe esas constraints.

    Ejemplo de retorno:
    "1) year equals 2014"
    """
    import random

    from ..shared_data import FIELD_OPERATORS_MAP_PRODUCTS
    from .generation_functions import generate_constraint_from_solution

    # Elegir una película aleatoria como punto de partida
    solution_book = random.choice(data)
    # print(f"Película inicial seleccionada: {solution_book['name']}")

    # Decidir cuántos constraints generar (1-3)
    num_constraints = random.randint(1, 3)

    # Seleccionar campos aleatorios para los constraints
    available_fields = list(FIELD_OPERATORS_MAP_PRODUCTS.keys())
    selected_fields = random.sample(available_fields, min(num_constraints, len(available_fields)))

    constraint_list = []

    for field in selected_fields:
        # Obtener operadores válidos para este campo
        valid_operators = FIELD_OPERATORS_MAP_PRODUCTS[field]
        # Elegir un operador aleatorio
        operator = random.choice(valid_operators)

        # Generar un constraint basado en el campo, operador y la película solución
        constraint = generate_constraint_from_solution(solution_book, field, ComparisonOperator(operator))

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
        # matching_books = [book for book in data if item_matches_all_constraints(book, constraint_list)]
        # print(f"Constraints generated: {constraints_str}")
        # print(f"Books that satisfy constraints ({len(matching_books)}):")
        # for book in matching_books:
        #     print(f"  - {book['name']} ({book['year']}) - Author: {book['author']}")

        # Retornar solo el string de restricciones sin información adicional
        return constraints_str

    # Si no se pudo crear constraints válidos, intentar de nuevo
    return build_constraints_info(data, max_attempts - 1) if max_attempts > 1 else None
