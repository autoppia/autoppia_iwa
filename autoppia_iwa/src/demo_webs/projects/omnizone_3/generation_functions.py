import random
from typing import Any

from ..books_2.utils import parse_constraints_str
from ..criterion_helper import ComparisonOperator, CriterionValue, validate_criterion
from .data import PRODUCTS_DATA


def generate_omnizone_products_constraints():
    """
    Generates constraints specifically for book-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import build_constraints_info

    # Generar restricciones frescas basadas en los datos de películas
    constraints_str = build_constraints_info(PRODUCTS_DATA)

    # Convertir el string a la estructura de datos
    if constraints_str:
        return parse_constraints_str(constraints_str)
    return None


def generate_constraint_from_solution(book: dict, field: str, operator: ComparisonOperator, PRODUCTS_DATA: list[dict]) -> dict[str, Any]:
    """
    Genera un constraint para un campo y operador específicos que la película solución satisface.
    Utiliza el conjunto completo de películas para generar constraints más realistas.
    """
    constraint = {"field": field, "operator": operator}

    if field in ["title", "category", "brand"]:
        if operator == ComparisonOperator.EQUALS:
            constraint["value"] = book[field]
        elif operator == ComparisonOperator.NOT_EQUALS:
            # Buscar un valor diferente de otra película
            other_values = [m[field] for m in PRODUCTS_DATA if m[field] != book[field]]
            if other_values:
                constraint["value"] = random.choice(other_values)
            else:
                constraint["value"] = "Other " + field
        elif operator == ComparisonOperator.CONTAINS:
            if len(book[field]) > 3:
                start = random.randint(0, len(book[field]) - 3)
                length = random.randint(2, min(5, len(book[field]) - start))
                constraint["value"] = book[field][start : start + length]
            else:
                constraint["value"] = book[field]
        elif operator == ComparisonOperator.NOT_CONTAINS:
            # Esto es más complejo - encontrar una subcadena que no esté en el campo de la película
            alphabet = "abcdefghijklmnopqrstuvwxyz"
            while True:
                test_str = "".join(random.choice(alphabet) for _ in range(3))
                if test_str.lower() not in book[field].lower():
                    constraint["value"] = test_str
                    break

    elif field == "price":
        value = book[field]
        if operator == ComparisonOperator.EQUALS:
            constraint["value"] = value
        elif operator == ComparisonOperator.NOT_EQUALS:
            # Buscar un valor diferente de otra película
            other_values = [m[field] for m in PRODUCTS_DATA if m[field] != value]
            if other_values:
                constraint["value"] = random.choice(other_values)
            else:
                constraint["value"] = value + (1 if random.random() > 0.5 else -1)
        elif operator == ComparisonOperator.GREATER_THAN:
            # Encontrar un valor menor que el de la película
            lower_values = [m[field] for m in PRODUCTS_DATA if m[field] < value]
            if lower_values:
                constraint["value"] = random.choice(lower_values)
            else:
                constraint["value"] = value - 1
        elif operator == ComparisonOperator.LESS_THAN:
            # Encontrar un valor mayor que el de la película
            higher_values = [m[field] for m in PRODUCTS_DATA if m[field] > value]
            if higher_values:
                constraint["value"] = random.choice(higher_values)
            else:
                constraint["value"] = value + 1
        elif operator == ComparisonOperator.GREATER_EQUAL:
            # Podemos usar un valor igual o menor
            valid_values = [m[field] for m in PRODUCTS_DATA if m[field] <= value]
            if valid_values:
                constraint["value"] = random.choice(valid_values)
            else:
                constraint["value"] = value
        elif operator == ComparisonOperator.LESS_EQUAL:
            # Podemos usar un valor igual o mayor
            valid_values = [m[field] for m in PRODUCTS_DATA if m[field] >= value]
            if valid_values:
                constraint["value"] = random.choice(valid_values)
            else:
                constraint["value"] = value
        elif operator == ComparisonOperator.IN_LIST:
            # Incluir el valor de la película y posiblemente algunos otros valores
            other_values = [m[field] for m in PRODUCTS_DATA if m[field] != value]
            sample_size = min(2, len(other_values))
            if other_values and sample_size > 0:
                constraint["value"] = [value, *random.sample(other_values, sample_size)]
            else:
                constraint["value"] = [value]
        elif operator == ComparisonOperator.NOT_IN_LIST:
            # Encontrar valores que no incluyan el de la película
            other_values = [m[field] for m in PRODUCTS_DATA if m[field] != value]
            if other_values:
                constraint["value"] = random.sample(other_values, min(3, len(other_values)))
            else:
                constraint["value"] = [value + 1, value + 2]

    elif field == "rating":
        value = book[field]
        if operator == ComparisonOperator.EQUALS:
            constraint["value"] = value
        elif operator == ComparisonOperator.NOT_EQUALS:
            # Buscar un valor diferente de otra película
            other_values = [m[field] for m in PRODUCTS_DATA if m[field] != value]
            if other_values:
                constraint["value"] = random.choice(other_values)
            else:
                # Asegurarse de que el valor alternativo esté en el rango 0-5
                constraint["value"] = max(0, min(5, value + (0.1 if random.random() > 0.5 else -0.1)))
        elif operator == ComparisonOperator.GREATER_THAN:
            # Encontrar un valor menor que el de la película
            lower_values = [m[field] for m in PRODUCTS_DATA if m[field] < value]
            if lower_values:
                constraint["value"] = random.choice(lower_values)
            else:
                # Asegurarse de que el valor sea positivo y menor que el original
                constraint["value"] = max(0, value - 0.1)
        elif operator == ComparisonOperator.LESS_THAN:
            # Encontrar un valor mayor que el de la película
            higher_values = [m[field] for m in PRODUCTS_DATA if m[field] > value]
            if higher_values:
                constraint["value"] = random.choice(higher_values)
            else:
                # Asegurarse de que el valor no exceda 5
                constraint["value"] = min(5, value + 0.1)
        elif operator == ComparisonOperator.GREATER_EQUAL:
            # Podemos usar un valor igual o menor
            valid_values = [m[field] for m in PRODUCTS_DATA if m[field] <= value]
            if valid_values:
                constraint["value"] = random.choice(valid_values)
            else:
                constraint["value"] = value
        elif operator == ComparisonOperator.LESS_EQUAL:
            # Podemos usar un valor igual o mayor
            valid_values = [m[field] for m in PRODUCTS_DATA if m[field] >= value]
            if valid_values:
                constraint["value"] = random.choice(valid_values)
            else:
                constraint["value"] = value
        elif operator == ComparisonOperator.IN_LIST:
            # Incluir el valor de la película y posiblemente algunos otros valores
            other_values = [m[field] for m in PRODUCTS_DATA if m[field] != value]
            sample_size = min(2, len(other_values))
            if other_values and sample_size > 0:
                constraint["value"] = [value, *random.sample(other_values, sample_size)]
            else:
                constraint["value"] = [value]
        elif operator == ComparisonOperator.NOT_IN_LIST:
            # Encontrar valores que no incluyan el de la película
            other_values = [m[field] for m in PRODUCTS_DATA if m[field] != value]
            if other_values:
                constraint["value"] = random.sample(other_values, min(3, len(other_values)))
            else:
                # Asegurarse de que los valores estén en el rango 0-5
                constraint["value"] = [max(0, min(5, value + 0.1)), max(0, min(5, value + 0.2))]

    # Verificar que el constraint generado es válido para la película solución
    criterion = CriterionValue(value=constraint["value"], operator=operator)
    if validate_criterion(book.get(field), criterion):
        return constraint

    # Si llegamos aquí, el constraint generado no es válido
    return None
