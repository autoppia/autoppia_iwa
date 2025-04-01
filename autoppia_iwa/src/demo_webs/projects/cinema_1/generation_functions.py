import random
from typing import Any

from ..criterion_helper import ComparisonOperator, CriterionValue, validate_criterion
from .data import FIELD_OPERATORS_MAP_CONTACT, MOVIES_DATA


def generate_film_constraints():
    """
    Generates constraints specifically for film-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import build_constraints_info, parse_constraints_str

    # Generar restricciones frescas basadas en los datos de películas
    constraints_str = build_constraints_info(MOVIES_DATA)

    # Convertir el string a la estructura de datos
    if constraints_str:
        return parse_constraints_str(constraints_str)
    return None


def generate_contact_constraints() -> list:
    """
    Genera una lista de constraints estructurados para el formulario de contacto.
    Cada constraint es un diccionario con la forma:
       {"field": <campo>, "operator": <ComparisonOperator>, "value": <valor>}
    """

    def _generate_random_value_for_contact(field: str) -> str:
        if field == "name":
            return random.choice(["Alice", "Bob", "John", "Maria", "TestUser", "Peter", "Susan", "Robert", "Linda", "Michael", "Jessica", "William", "Karen", "David", "Lisa"])
        elif field == "email":
            return random.choice(
                [
                    "test@example.com",
                    "info@example.org",
                    "user@yahoo.com",
                    "admin@domain.com",
                    "contact@site.com",
                    "noreply@domain.com",
                    "service@provider.com",
                    "hello@world.com",
                    "support@company.com",
                    "sales@business.com",
                    "user1@site.com",
                    "example@mail.com",
                    "foo@bar.com",
                    "john@doe.com",
                    "jane@doe.com",
                ]
            )
        elif field == "subject":
            return random.choice(
                ["Feedback", "Inquiry", "Question", "Collaboration", "Request", "Complaint", "Suggestion", "Appointment", "Meeting", "Proposal", "Support", "Information", "Order", "Refund", "Other"]
            )
        elif field == "message":
            return random.choice(
                [
                    "Hello, I'd like more info",
                    "Need further details please",
                    "Just a quick question",
                    "Hello, I'm interested in your services",
                    "I have a query regarding your service",
                    "Could you provide more details?",
                    "I need assistance with my order",
                    "I'm having an issue with the product",
                    "Please contact me regarding my inquiry",
                    "I want to learn more about your services",
                    "Could you help me with my account?",
                    "I'm writing to request support",
                    "Please provide me with more information",
                    "I would like to discuss a potential project",
                    "I am interested in collaborating with you",
                ]
            )
        return "TestValue"

    num_constraints = random.randint(1, 4)
    fields = list(FIELD_OPERATORS_MAP_CONTACT.keys())  # ["name", "email", "subject", "message"]
    constraints_list = []

    for _ in range(num_constraints):
        if not fields:
            break
        field = random.choice(fields)
        fields.remove(field)

        # Convertimos el operador de string a instancia de ComparisonOperator
        possible_ops = FIELD_OPERATORS_MAP_CONTACT[field]
        operator_str = random.choice(possible_ops)
        operator = ComparisonOperator(operator_str)

        value = _generate_random_value_for_contact(field)
        constraint = {"field": field, "operator": operator, "value": value}
        constraints_list.append(constraint)

    return constraints_list


def generate_constraint_from_solution(movie: dict, field: str, operator: ComparisonOperator, movies_data: list[dict]) -> dict[str, Any]:
    """
    Genera un constraint para un campo y operador específicos que la película solución satisface.
    Utiliza el conjunto completo de películas para generar constraints más realistas.
    """
    constraint = {"field": field, "operator": operator}

    if field == "name" or field == "director":
        if operator == ComparisonOperator.EQUALS:
            constraint["value"] = movie[field]
        elif operator == ComparisonOperator.NOT_EQUALS:
            # Buscar un valor diferente de otra película
            other_values = [m[field] for m in movies_data if m[field] != movie[field]]
            if other_values:
                constraint["value"] = random.choice(other_values)
            else:
                constraint["value"] = "Other " + field
        elif operator == ComparisonOperator.CONTAINS:
            if len(movie[field]) > 3:
                start = random.randint(0, len(movie[field]) - 3)
                length = random.randint(2, min(5, len(movie[field]) - start))
                constraint["value"] = movie[field][start : start + length]
            else:
                constraint["value"] = movie[field]
        elif operator == ComparisonOperator.NOT_CONTAINS:
            # Esto es más complejo - encontrar una subcadena que no esté en el campo de la película
            alphabet = "abcdefghijklmnopqrstuvwxyz"
            while True:
                test_str = "".join(random.choice(alphabet) for _ in range(3))
                if test_str.lower() not in movie[field].lower():
                    constraint["value"] = test_str
                    break

    elif field == "year" or field == "duration":
        value = movie[field]
        if operator == ComparisonOperator.EQUALS:
            constraint["value"] = value
        elif operator == ComparisonOperator.NOT_EQUALS:
            # Buscar un valor diferente de otra película
            other_values = [m[field] for m in movies_data if m[field] != value]
            if other_values:
                constraint["value"] = random.choice(other_values)
            else:
                constraint["value"] = value + (1 if random.random() > 0.5 else -1)
        elif operator == ComparisonOperator.GREATER_THAN:
            # Encontrar un valor menor que el de la película
            lower_values = [m[field] for m in movies_data if m[field] < value]
            if lower_values:
                constraint["value"] = random.choice(lower_values)
            else:
                constraint["value"] = value - 1
        elif operator == ComparisonOperator.LESS_THAN:
            # Encontrar un valor mayor que el de la película
            higher_values = [m[field] for m in movies_data if m[field] > value]
            if higher_values:
                constraint["value"] = random.choice(higher_values)
            else:
                constraint["value"] = value + 1
        elif operator == ComparisonOperator.GREATER_EQUAL:
            # Podemos usar un valor igual o menor
            valid_values = [m[field] for m in movies_data if m[field] <= value]
            if valid_values:
                constraint["value"] = random.choice(valid_values)
            else:
                constraint["value"] = value
        elif operator == ComparisonOperator.LESS_EQUAL:
            # Podemos usar un valor igual o mayor
            valid_values = [m[field] for m in movies_data if m[field] >= value]
            if valid_values:
                constraint["value"] = random.choice(valid_values)
            else:
                constraint["value"] = value
        elif operator == ComparisonOperator.IN_LIST:
            # Incluir el valor de la película y posiblemente algunos otros valores
            other_values = [m[field] for m in movies_data if m[field] != value]
            sample_size = min(2, len(other_values))
            if other_values and sample_size > 0:
                constraint["value"] = [value, *random.sample(other_values, sample_size)]
            else:
                constraint["value"] = [value]
        elif operator == ComparisonOperator.NOT_IN_LIST:
            # Encontrar valores que no incluyan el de la película
            other_values = [m[field] for m in movies_data if m[field] != value]
            if other_values:
                constraint["value"] = random.sample(other_values, min(3, len(other_values)))
            else:
                constraint["value"] = [value + 1, value + 2]

    elif field == "rating":
        value = movie[field]
        if operator == ComparisonOperator.EQUALS:
            constraint["value"] = value
        elif operator == ComparisonOperator.NOT_EQUALS:
            # Buscar un valor diferente de otra película
            other_values = [m[field] for m in movies_data if m[field] != value]
            if other_values:
                constraint["value"] = random.choice(other_values)
            else:
                # Asegurarse de que el valor alternativo esté en el rango 0-5
                constraint["value"] = max(0, min(5, value + (0.1 if random.random() > 0.5 else -0.1)))
        elif operator == ComparisonOperator.GREATER_THAN:
            # Encontrar un valor menor que el de la película
            lower_values = [m[field] for m in movies_data if m[field] < value]
            if lower_values:
                constraint["value"] = random.choice(lower_values)
            else:
                # Asegurarse de que el valor sea positivo y menor que el original
                constraint["value"] = max(0, value - 0.1)
        elif operator == ComparisonOperator.LESS_THAN:
            # Encontrar un valor mayor que el de la película
            higher_values = [m[field] for m in movies_data if m[field] > value]
            if higher_values:
                constraint["value"] = random.choice(higher_values)
            else:
                # Asegurarse de que el valor no exceda 5
                constraint["value"] = min(5, value + 0.1)
        elif operator == ComparisonOperator.GREATER_EQUAL:
            # Podemos usar un valor igual o menor
            valid_values = [m[field] for m in movies_data if m[field] <= value]
            if valid_values:
                constraint["value"] = random.choice(valid_values)
            else:
                constraint["value"] = value
        elif operator == ComparisonOperator.LESS_EQUAL:
            # Podemos usar un valor igual o mayor
            valid_values = [m[field] for m in movies_data if m[field] >= value]
            if valid_values:
                constraint["value"] = random.choice(valid_values)
            else:
                constraint["value"] = value
        elif operator == ComparisonOperator.IN_LIST:
            # Incluir el valor de la película y posiblemente algunos otros valores
            other_values = [m[field] for m in movies_data if m[field] != value]
            sample_size = min(2, len(other_values))
            if other_values and sample_size > 0:
                constraint["value"] = [value, *random.sample(other_values, sample_size)]
            else:
                constraint["value"] = [value]
        elif operator == ComparisonOperator.NOT_IN_LIST:
            # Encontrar valores que no incluyan el de la película
            other_values = [m[field] for m in movies_data if m[field] != value]
            if other_values:
                constraint["value"] = random.sample(other_values, min(3, len(other_values)))
            else:
                # Asegurarse de que los valores estén en el rango 0-5
                constraint["value"] = [max(0, min(5, value + 0.1)), max(0, min(5, value + 0.2))]

    elif field == "genres":
        if operator == ComparisonOperator.CONTAINS:
            if movie[field]:
                constraint["value"] = random.choice(movie[field])
            else:
                return None  # No se puede crear este constraint
        elif operator == ComparisonOperator.NOT_CONTAINS:
            # Encontrar un género que no esté en los géneros de la película
            all_genres = set()
            for m in movies_data:
                all_genres.update(m["genres"])

            movie_genres = set(movie[field])
            available_genres = all_genres - movie_genres

            if available_genres:
                constraint["value"] = random.choice(list(available_genres))
            else:
                constraint["value"] = "Non-existent genre"
        elif operator == ComparisonOperator.IN_LIST:
            if movie[field]:
                # Tomar uno o más géneros de la película para la lista
                num_genres = min(len(movie[field]), random.randint(1, 2))
                constraint["value"] = random.sample(movie[field], num_genres)
            else:
                return None  # No se puede crear este constraint
        elif operator == ComparisonOperator.NOT_IN_LIST:
            # Similar a NOT_CONTAINS pero creando una lista
            all_genres = set()
            for m in movies_data:
                all_genres.update(m["genres"])

            movie_genres = set(movie[field])
            available_genres = all_genres - movie_genres

            if available_genres:
                num_genres = min(len(available_genres), random.randint(1, 3))
                constraint["value"] = random.sample(list(available_genres), num_genres)
            else:
                constraint["value"] = ["Non-existent genre"]

    # Verificar que el constraint generado es válido para la película solución
    criterion = CriterionValue(value=constraint["value"], operator=operator)
    if validate_criterion(movie.get(field), criterion):
        return constraint

    # Si llegamos aquí, el constraint generado no es válido
    return None
