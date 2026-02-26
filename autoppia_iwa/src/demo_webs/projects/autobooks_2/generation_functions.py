import random
from random import choice, randint, sample, uniform
from typing import Any

from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url

from ..criterion_helper import ComparisonOperator, CriterionValue, validate_criterion
from .data import FIELD_OPERATORS_MAP_ADD_COMMENT, FIELD_OPERATORS_MAP_CONTACT, FIELD_OPERATORS_MAP_EDIT_USER
from .data_utils import fetch_data

# Constants for constraint placeholders
USERNAME_PLACEHOLDER = "<username>"
PASSWORD_PLACEHOLDER = "<password>"


def generate_registration_constraints():
    """
    Generates constraints specifically for film-related use cases.
    Returns the constraints as structured data.
    """

    from .utils import parse_constraints_str

    # Generar restricciones frescas basadas en los datos de películas
    # Note: "<signup_password>" is a placeholder for constraint generation, not a hard-coded credential
    constraints_str = "username equals <signup_username> AND email equals <signup_email> AND password equals <signup_password>"

    return parse_constraints_str(constraints_str)


def generate_login_constraints():
    """
    Generates constraints specifically for film-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import parse_constraints_str

    # Generar restricciones frescas basadas en los datos de películas

    constraints_str = f"username equals {USERNAME_PLACEHOLDER} AND password equals {PASSWORD_PLACEHOLDER}"

    return parse_constraints_str(constraints_str)


def generate_logout_constraints():
    """
    Generates constraints specifically for film-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import parse_constraints_str

    # Generar restricciones frescas basadas en los datos de películas
    constraints_str = f"username equals {USERNAME_PLACEHOLDER} AND password equals {PASSWORD_PLACEHOLDER}"
    return parse_constraints_str(constraints_str)


async def generate_book_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """
    Generates constraints specifically for book-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import build_constraints_info, parse_constraints_str

    constraints = []

    # Fetch data if dataset is not provided or is empty
    if not dataset:
        seed = get_seed_from_url(task_url)
        books = await fetch_data(seed_value=seed)
        dataset = {"books": books}

    # Extract books from dataset
    books = dataset.get("books", []) if dataset else []
    if not books:
        return None

    constraints_str = build_constraints_info(books)

    # Convertir el string a la estructura de datos
    if constraints_str:
        constraints = parse_constraints_str(constraints_str)
        # Login constraints use placeholders; replaced at validation time in base_events (same as in actions).
        constraints.append({"field": "username", "operator": ComparisonOperator(ComparisonOperator.EQUALS), "value": USERNAME_PLACEHOLDER})
        constraints.append({"field": "password", "operator": ComparisonOperator(ComparisonOperator.EQUALS), "value": PASSWORD_PLACEHOLDER})

        return constraints

    return None


async def generate_book_details_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """
    Generates constraints specifically for book-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import build_constraints_info, parse_constraints_str

    constraints = []

    # Fetch data if dataset is not provided or is empty
    if not dataset:
        seed = get_seed_from_url(task_url)
        books = await fetch_data(seed_value=seed)
        dataset = {"books": books}

    # Extract books from dataset
    books = dataset.get("books", []) if dataset else []
    if not books:
        return None

    constraints_str = build_constraints_info(books)

    # Convertir el string a la estructura de datos
    if constraints_str:
        constraints = parse_constraints_str(constraints_str)
        constraints.append({"field": "username", "operator": ComparisonOperator(ComparisonOperator.EQUALS), "value": USERNAME_PLACEHOLDER})
        constraints.append({"field": "password", "operator": ComparisonOperator(ComparisonOperator.EQUALS), "value": PASSWORD_PLACEHOLDER})
        return constraints

    return None


def generate_delete_book_constraints():
    """
    Generates constraints specifically for book-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import parse_constraints_str

    # Generar restricciones frescas basadas en los datos de películas
    constraints_str = f"username equals {USERNAME_PLACEHOLDER} AND password equals {PASSWORD_PLACEHOLDER} AND id equals <web_agent_id>"

    # Convertir el string a la estructura de datos
    if constraints_str:
        return parse_constraints_str(constraints_str)
    return None


async def generate_search_book_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """
    Generates constraints specifically for book-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import parse_constraints_str

    # Fetch data if dataset is not provided or is empty
    if not dataset:
        seed = get_seed_from_url(task_url)
        books = await fetch_data(seed_value=seed)
        dataset = {"books": books}

    # Extract books from dataset
    books = dataset.get("books", []) if dataset else []
    if not books:
        return None

    books_names = [book["name"] for book in books]
    operators = ["equals", "not_equals"]
    # Security Hotspot: random.choice is used for non-security purposes (test data generation)
    # This is safe as it's only used to generate random constraints for testing, not for security-sensitive operations
    constraints_str = f"query {choice(operators)} {choice(books_names)}"
    return parse_constraints_str(constraints_str)


def generate_contact_constraints() -> list:
    """
    Genera una lista de constraints estructurados para el formulario de contacto.
    Cada constraint es un diccionario con la forma:
       {"field": <campo>, "operator": <ComparisonOperator>, "value": <valor>}
    """

    def _generate_random_value_for_contact(field: str) -> str:
        # Security Hotspot: random.choice is used for non-security purposes (test data generation)
        if field == "name":
            return random.choice(["Alice", "Bob", "John", "Maria", "TestUser", "Peter", "Susan", "Robert", "Linda", "Michael", "Jessica", "William", "Karen", "David", "Lisa"])
        if field == "email":
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
        if field == "subject":
            return random.choice(
                ["Feedback", "Inquiry", "Question", "Collaboration", "Request", "Complaint", "Suggestion", "Appointment", "Meeting", "Proposal", "Support", "Information", "Order", "Refund", "Other"]
            )
        if field == "message":
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

    # Security Hotspot: random.randint and random.choice are used for non-security purposes (test data generation)
    num_constraints = random.randint(1, 4)
    # ["name", "email", "subject", "message"]
    fields = list(FIELD_OPERATORS_MAP_CONTACT.keys())
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


async def generate_book_filter_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """
    Genera una combinación de constraints para filtrado de libros
    usando los años y géneros reales de los libros.
    """
    # Fetch data if dataset is not provided or is empty
    if not dataset:
        seed = get_seed_from_url(task_url)
        books = await fetch_data(seed_value=seed)
        dataset = {"books": books}

    # Extract books from dataset
    books = dataset.get("books", []) if dataset else []
    if not books:
        return []

    existing_years = list({book["year"] for book in books})
    existing_genres = list({genre for book in books for genre in book["genres"]})

    # Security Hotspot: random.choice is used for non-security purposes (test data generation)
    generation_type = choice(["single_genre", "single_year", "genre_and_year"])

    constraints = []

    if generation_type == "single_genre":
        if existing_genres:
            # Security Hotspot: random.choice is used for non-security purposes (test data generation)
            constraints.append({"field": "genres", "operator": ComparisonOperator(ComparisonOperator.EQUALS), "value": choice(existing_genres)})

    elif generation_type == "single_year":
        if existing_years:
            # Security Hotspot: random.choice is used for non-security purposes (test data generation)
            constraints.append(
                {
                    "field": "year",
                    "operator": choice([ComparisonOperator(ComparisonOperator.EQUALS), ComparisonOperator(ComparisonOperator.GREATER_EQUAL), ComparisonOperator(ComparisonOperator.LESS_EQUAL)]),
                    "value": choice(existing_years),
                }
            )

    elif generation_type == "genre_and_year" and existing_genres and existing_years:
        # Security Hotspot: random.choice is used for non-security purposes (test data generation)
        constraints.extend(
            [
                {"field": "genres", "operator": ComparisonOperator(ComparisonOperator.EQUALS), "value": choice(existing_genres)},
                {
                    "field": "year",
                    "operator": choice([ComparisonOperator(ComparisonOperator.EQUALS), ComparisonOperator(ComparisonOperator.GREATER_EQUAL), ComparisonOperator(ComparisonOperator.LESS_EQUAL)]),
                    "value": choice(existing_years),
                },
            ]
        )

    return constraints


def _generate_string_field_constraint(book: dict, field: str, operator: ComparisonOperator, books_data: list[dict]) -> str | None:
    """Generate constraint value for string fields (name, author, desc)."""
    if operator == ComparisonOperator.EQUALS:
        return book[field]
    if operator == ComparisonOperator.NOT_EQUALS:
        other_values = [m[field] for m in books_data if m[field] != book[field]]
        return random.choice(other_values) if other_values else f"Other {field}"
    if operator == ComparisonOperator.CONTAINS:
        if len(book[field]) > 3:
            # Security Hotspot: random.randint is used for non-security purposes (test data generation)
            start = random.randint(0, len(book[field]) - 3)
            length = random.randint(2, min(5, len(book[field]) - start))
            return book[field][start : start + length]
        return book[field]
    if operator == ComparisonOperator.NOT_CONTAINS:
        # Security Hotspot: random.choice is used for non-security purposes (test data generation)
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        while True:
            test_str = "".join(random.choice(alphabet) for _ in range(3))
            if test_str.lower() not in book[field].lower():
                return test_str
    return None


def _generate_numeric_field_constraint(book: dict, field: str, operator: ComparisonOperator, books_data: list[dict]) -> Any:
    """Generate constraint value for numeric fields (year, page_count, price)."""
    value = book[field]
    if operator == ComparisonOperator.EQUALS:
        return value
    if operator == ComparisonOperator.NOT_EQUALS:
        other_values = [m[field] for m in books_data if m[field] != value]
        if other_values:
            return random.choice(other_values)
        # Security Hotspot: random.random is used for non-security purposes (test data generation)
        return value + (1 if random.random() > 0.5 else -1)
    if operator == ComparisonOperator.GREATER_THAN:
        lower_values = [m[field] for m in books_data if m[field] < value]
        return random.choice(lower_values) if lower_values else value - 1
    if operator == ComparisonOperator.LESS_THAN:
        higher_values = [m[field] for m in books_data if m[field] > value]
        return random.choice(higher_values) if higher_values else value + 1
    if operator == ComparisonOperator.GREATER_EQUAL:
        valid_values = [m[field] for m in books_data if m[field] <= value]
        return random.choice(valid_values) if valid_values else value
    if operator == ComparisonOperator.LESS_EQUAL:
        valid_values = [m[field] for m in books_data if m[field] >= value]
        return random.choice(valid_values) if valid_values else value
    if operator == ComparisonOperator.IN_LIST:
        other_values = [m[field] for m in books_data if m[field] != value]
        sample_size = min(2, len(other_values))
        if other_values and sample_size > 0:
            # Security Hotspot: random.sample is used for non-security purposes (test data generation)
            return [value, *random.sample(other_values, sample_size)]
        return [value]
    if operator == ComparisonOperator.NOT_IN_LIST:
        other_values = [m[field] for m in books_data if m[field] != value]
        if other_values:
            # Security Hotspot: random.sample is used for non-security purposes (test data generation)
            return random.sample(other_values, min(3, len(other_values)))
        return [value + 1, value + 2]
    return None


def _generate_rating_field_constraint(book: dict, operator: ComparisonOperator, books_data: list[dict]) -> Any:
    """Generate constraint value for rating field."""
    value = book["rating"]
    if operator == ComparisonOperator.EQUALS:
        return value
    if operator == ComparisonOperator.NOT_EQUALS:
        other_values = [m["rating"] for m in books_data if m["rating"] != value]
        if other_values:
            return random.choice(other_values)
        # Security Hotspot: random.random is used for non-security purposes (test data generation)
        return max(0, min(5, value + (0.1 if random.random() > 0.5 else -0.1)))
    if operator == ComparisonOperator.GREATER_THAN:
        lower_values = [m["rating"] for m in books_data if m["rating"] < value]
        return random.choice(lower_values) if lower_values else max(0, value - 0.1)
    if operator == ComparisonOperator.LESS_THAN:
        higher_values = [m["rating"] for m in books_data if m["rating"] > value]
        return random.choice(higher_values) if higher_values else min(5, value + 0.1)
    if operator == ComparisonOperator.GREATER_EQUAL:
        valid_values = [m["rating"] for m in books_data if m["rating"] <= value]
        return random.choice(valid_values) if valid_values else value
    if operator == ComparisonOperator.LESS_EQUAL:
        valid_values = [m["rating"] for m in books_data if m["rating"] >= value]
        return random.choice(valid_values) if valid_values else value
    if operator == ComparisonOperator.IN_LIST:
        other_values = [m["rating"] for m in books_data if m["rating"] != value]
        sample_size = min(2, len(other_values))
        if other_values and sample_size > 0:
            # Security Hotspot: random.sample is used for non-security purposes (test data generation)
            return [value, *random.sample(other_values, sample_size)]
        return [value]
    if operator == ComparisonOperator.NOT_IN_LIST:
        other_values = [m["rating"] for m in books_data if m["rating"] != value]
        if other_values:
            # Security Hotspot: random.sample is used for non-security purposes (test data generation)
            return random.sample(other_values, min(3, len(other_values)))
        return [max(0, min(5, value + 0.1)), max(0, min(5, value + 0.2))]
    return None


def _generate_genre_field_constraint(book: dict, operator: ComparisonOperator, books_data: list[dict]) -> Any:
    """Generate constraint value for genres field."""
    if operator == ComparisonOperator.CONTAINS:
        if book["genres"]:
            # Security Hotspot: random.choice is used for non-security purposes (test data generation)
            return random.choice(book["genres"])
        return None
    if operator == ComparisonOperator.NOT_CONTAINS:
        all_genres = {genre for m in books_data for genre in m["genres"]}
        book_genres = set(book["genres"])
        available_genres = all_genres - book_genres
        if available_genres:
            # Security Hotspot: random.choice is used for non-security purposes (test data generation)
            return random.choice(list(available_genres))
        return "Non-existent genre"
    if operator == ComparisonOperator.IN_LIST:
        if book["genres"]:
            # Security Hotspot: random.randint and random.sample are used for non-security purposes (test data generation)
            num_genres = min(len(book["genres"]), random.randint(1, 2))
            return random.sample(book["genres"], num_genres)
        return None
    if operator == ComparisonOperator.NOT_IN_LIST:
        all_genres = {genre for m in books_data for genre in m["genres"]}
        book_genres = set(book["genres"])
        available_genres = all_genres - book_genres
        if available_genres:
            # Security Hotspot: random.randint and random.sample are used for non-security purposes (test data generation)
            num_genres = min(len(available_genres), random.randint(1, 3))
            return random.sample(list(available_genres), num_genres)
        return ["Non-existent genre"]
    return None


def generate_constraint_from_solution(book: dict, field: str, operator: ComparisonOperator, books_data: list[dict]) -> dict[str, Any] | None:
    """
    Genera un constraint para un campo y operador específicos que la película solución satisface.
    Utiliza el conjunto completo de películas para generar constraints más realistas.
    """
    constraint = {"field": field, "operator": operator}

    if field in ("name", "author", "desc"):
        constraint_value = _generate_string_field_constraint(book, field, operator, books_data)
    elif field in ("year", "page_count", "price"):
        constraint_value = _generate_numeric_field_constraint(book, field, operator, books_data)
    elif field == "rating":
        constraint_value = _generate_rating_field_constraint(book, operator, books_data)
    elif field == "genres":
        constraint_value = _generate_genre_field_constraint(book, operator, books_data)
    else:
        return None

    if constraint_value is None:
        return None

    constraint["value"] = constraint_value

    # Verificar que el constraint generado es válido para la película solución
    criterion = CriterionValue(value=constraint["value"], operator=operator)
    if validate_criterion(book.get(field), criterion):
        return constraint

    return None


async def generate_add_comment_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """
    Genera combinaciones de constraints para añadir comentarios.
    """
    # Fetch data if dataset is not provided or is empty
    if not dataset:
        seed = get_seed_from_url(task_url)
        books = await fetch_data(seed_value=seed)
        dataset = {"books": books}

    # Extract books from dataset
    books_data = dataset.get("books", []) if dataset else []
    if not books_data:
        return []

    books = [book["name"] for book in books_data]

    # Palabras y frases para generar comentarios
    comment_keywords = [
        "amazing",
        "stunning",
        "great",
        "awesome",
        "fantastic",
        "brilliant",
        "incredible",
        "genius",
        "classic",
        "masterpiece",
        "captivating storytelling",
        "perfectly paced",
        "incredible character development",
        "vividly descriptive",
        "deeply emotional journey",
        "groundbreaking narrative",
        "exceptional writing",
        "thought-provoking plot",
        "beautifully written",
        "complex narrative",
        "intricate storyline",
        "subtle character arcs",
        "nuanced prose",
        "immersive world-building",
        "hauntingly beautiful",
        "innovative structure",
        "masterful use of language",
        "atmospheric setting",
        "kept me on the edge of my seat",
        "couldn't put it down",
        "completely absorbed",
        "emotionally powerful",
        "intellectually stimulating",
        "redefines the genre",
        "unlike anything I've read before",
        "sets a new standard",
        "a true literary experience",
    ]

    # Nombres para commenter_name
    commenter_names = ["John", "Sarah", "Michael", "Emma", "David", "Lisa", "Alex", "Rachel", "Tom", "Emily"]

    # Definición de operadores para cada campo

    # Generar constraints
    constraints = []

    # Elegir campos aleatorios (1 o 2)
    selected_fields = sample(["book_name", "commenter_name", "content"], k=choice([1, 2, 3]))
    for field in selected_fields:
        # Elegir un operador aleatorio para el campo
        operator = choice(FIELD_OPERATORS_MAP_ADD_COMMENT[field])

        # Seleccionar valor basado en el campo
        if field == "book_name":
            value = choice(books)
        elif field == "commenter_name":
            value = choice(commenter_names)
        else:  # content
            value = choice(comment_keywords)

        constraints.append({"field": field, "operator": ComparisonOperator(operator), "value": value})

    return constraints


async def generate_edit_book_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """
    Generates constraints specifically for editing book-related use cases.
    Returns the constraints as structured data.
    """

    # Campos editables (sin name porque ya tenemos la película)
    editable_fields = ["author", "year", "genres", "rating", "page_count"]

    random_words = [
        "car",
        "star",
        "red",
        "blue",
        "green",
        "e",
        "a",
        "o",
        "x",
        "z",
        # Palabras más largas
        "cinema",
        "book",
        "light",
        "shadow",
        "dream",
        "story",
        "heart",
        "vision",
        "gold",
        "silver",
        "thunder",
        "wind",
        "quantum",
        "stellar",
        "cosmic",
        "rhythm",
        "echo",
        "spark",
        "rebel",
        "sage",
    ]

    # Fetch data if dataset is not provided or is empty
    if not dataset:
        seed = get_seed_from_url(task_url)
        books = await fetch_data(seed_value=seed)
        dataset = {"books": books}
    all_genres = list({genre for book in dataset.get("books", []) for genre in book["genres"]})

    # Generar constraints
    constraints = []

    # Always add username and password constraints explicitly
    constraints.append({"field": "username", "operator": ComparisonOperator(ComparisonOperator.EQUALS), "value": "<username>"})
    constraints.append({"field": "password", "operator": ComparisonOperator(ComparisonOperator.EQUALS), "value": "<password>"})

    # Seleccionar 1, 2, 3 o 4 campos para editar
    # Security Hotspot: random.sample and random.choice are used for non-security purposes (test data generation)
    selected_fields = sample(editable_fields, k=choice([1, 2, 3, 4]))

    for field in selected_fields:
        if field == "author":
            constraints.append(
                {
                    "field": field,
                    "operator": choice([ComparisonOperator(ComparisonOperator.EQUALS), ComparisonOperator(ComparisonOperator.CONTAINS), ComparisonOperator(ComparisonOperator.NOT_CONTAINS)]),
                    "value": choice(random_words),
                }
            )
        elif field == "year":
            # Security Hotspot: random.randint is used for non-security purposes (test data generation)
            constraints.append(
                {
                    "field": field,
                    "operator": choice([ComparisonOperator(ComparisonOperator.EQUALS), ComparisonOperator(ComparisonOperator.GREATER_EQUAL), ComparisonOperator(ComparisonOperator.LESS_EQUAL)]),
                    "value": randint(1950, 2024),
                }
            )
        elif field == "genres":
            constraints.append({"field": field, "operator": ComparisonOperator(ComparisonOperator.EQUALS), "value": choice(all_genres)})
        elif field == "rating":
            # Security Hotspot: random.uniform is used for non-security purposes (test data generation)
            rating_value = round(uniform(0, 5), 1)
            constraints.append(
                {
                    "field": field,
                    "operator": choice([ComparisonOperator(ComparisonOperator.EQUALS), ComparisonOperator(ComparisonOperator.GREATER_EQUAL), ComparisonOperator(ComparisonOperator.LESS_EQUAL)]),
                    "value": rating_value,
                }
            )
        elif field == "page_count":
            # Security Hotspot: random.randint is used for non-security purposes (test data generation)
            constraints.append(
                {
                    "field": field,
                    "operator": choice([ComparisonOperator(ComparisonOperator.EQUALS), ComparisonOperator(ComparisonOperator.GREATER_EQUAL), ComparisonOperator(ComparisonOperator.LESS_EQUAL)]),
                    "value": randint(50, 1080),
                }
            )
    return constraints


async def generate_add_book_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """
    Generates constraints specifically for editing book-related use cases.
    Returns the constraints as structured data.
    """

    # Campos editables
    editable_fields = ["author", "year", "genres", "rating", "page_count"]

    random_words = [
        "car",
        "star",
        "red",
        "blue",
        "green",
        "e",
        "a",
        "o",
        "x",
        "z",
        # Palabras más largas
        "cinema",
        "book",
        "light",
        "shadow",
        "dream",
        "story",
        "heart",
        "vision",
        "gold",
        "silver",
        "thunder",
        "wind",
        "quantum",
        "stellar",
        "cosmic",
        "rhythm",
        "echo",
        "spark",
        "rebel",
        "sage",
    ]

    # Fetch data if dataset is not provided or is empty
    if not dataset:
        seed = get_seed_from_url(task_url)
        books = await fetch_data(seed_value=seed)
        dataset = {"books": books}
    all_genres = list({genre for book in dataset.get("books", []) for genre in book["genres"]})

    # Generar constraints
    constraints = []

    # Always add username and password constraints explicitly
    constraints.append({"field": "username", "operator": ComparisonOperator(ComparisonOperator.EQUALS), "value": "<username>"})
    constraints.append({"field": "password", "operator": ComparisonOperator(ComparisonOperator.EQUALS), "value": "<password>"})

    # Seleccionar 1, 2, 3 o 4 campos para editar
    selected_fields = sample(editable_fields, k=choice([1, 2, 3, 4]))

    for field in selected_fields:
        if field == "author":
            constraints.append(
                {
                    "field": field,
                    "operator": choice([ComparisonOperator(ComparisonOperator.EQUALS), ComparisonOperator(ComparisonOperator.CONTAINS), ComparisonOperator(ComparisonOperator.NOT_CONTAINS)]),
                    "value": choice(random_words),
                }
            )
        elif field == "year":
            constraints.append(
                {
                    "field": field,
                    "operator": choice([ComparisonOperator(ComparisonOperator.EQUALS), ComparisonOperator(ComparisonOperator.GREATER_EQUAL), ComparisonOperator(ComparisonOperator.LESS_EQUAL)]),
                    "value": randint(1950, 2024),
                }
            )
        elif field == "genres":
            constraints.append({"field": field, "operator": ComparisonOperator(ComparisonOperator.EQUALS), "value": choice(all_genres)})
        elif field == "rating":
            rating_value = round(uniform(0, 5), 1)
            constraints.append(
                {
                    "field": field,
                    "operator": choice([ComparisonOperator(ComparisonOperator.EQUALS), ComparisonOperator(ComparisonOperator.GREATER_EQUAL), ComparisonOperator(ComparisonOperator.LESS_EQUAL)]),
                    "value": rating_value,
                }
            )
        elif field == "page_count":
            constraints.append(
                {
                    "field": field,
                    "operator": choice([ComparisonOperator(ComparisonOperator.EQUALS), ComparisonOperator(ComparisonOperator.GREATER_EQUAL), ComparisonOperator(ComparisonOperator.LESS_EQUAL)]),
                    "value": randint(50, 1800),
                }
            )

    return constraints


def _generate_edit_profile_field_constraint(
    field: str,
    random_names: list[str],
    random_text_elements: list[str],
    random_bios: list[str],
    random_locations: list[str],
    random_websites: list[str],
    all_genres: list[str],
) -> dict[str, Any] | None:
    """Generate constraint for a single profile field."""
    valid_operators = FIELD_OPERATORS_MAP_EDIT_USER.get(field, [])
    if not valid_operators:
        return None

    # Security Hotspot: random.choice is used for non-security purposes (test data generation)
    operator_str = choice(valid_operators)
    operator = ComparisonOperator(operator_str)

    if field in ("first_name", "last_name"):
        value = choice(random_names) if operator.name in (ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS) else choice(random_text_elements)
    elif field == "bio":
        value = choice(random_text_elements) if operator.name in (ComparisonOperator.CONTAINS, ComparisonOperator.NOT_CONTAINS) else choice(random_bios)
    elif field == "location":
        value = choice(random_text_elements) if operator.name in (ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS) else choice(random_locations)
    elif field == "website":
        value = choice(random_websites) if operator.name in (ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS) else choice(random_text_elements)
    elif field == "favorite_genres":
        value = choice(all_genres)
    else:
        return None

    return {"field": field, "operator": operator, "value": value}


async def generate_edit_profile_constraints(task_url: str | None = None, dataset: dict[str, list[dict]] | None = None):
    """
    Generates constraints specifically for editing user profiles.
    Returns the constraints as structured data.
    """

    # Editable profile fields (username and email are excluded as mentioned in requirements)
    editable_fields = ["first_name", "last_name", "bio", "location", "website", "favorite_genres"]

    # Short words, letters, and syllables for text fields (for CONTAINS operators)
    random_text_elements = [
        "el",
        "al",
        "ol",
        "xa",
        "z",  # Single letters
        "car",
        "star",
        "red",
        "blue",
        "green",  # Short words
        "cinema",
        "book",
        "light",
        "shadow",
        "dream",  # Longer words
    ]

    # Sample data for generating realistic values
    random_names = ["John", "Emma", "Michael", "Sophia", "James", "Olivia", "William", "Ava", "Benjamin", "Isabella", "Lucas", "Mia", "Henry", "Charlotte", "Alexander"]

    random_locations = ["New York, USA", "London, UK", "Tokyo, Japan", "Paris, France", "Sydney, Australia", "Toronto, Canada", "Berlin, Germany", "Rome, Italy", "Madrid, Spain", "Seoul, South Korea"]

    random_websites = [
        "https://bookcritics.example.com",
        "https://bookreviews.example.net",
        "https://cinephileworld.example.org",
        "https://bookjournals.example.io",
        "https://bookfans.example.co",
        "https://bookmakers.example.site",
    ]

    random_bios = [
        "Passionate about independent books and literary fiction",
        "Avid reader with a love for classic literature",
        "Book enthusiast exploring diverse genres and authors",
        "Literary critic specializing in contemporary novels and poetry",
        "Story lover and aspiring writer",
    ]
    # Fetch data if dataset is not provided or is empty
    if not dataset:
        seed = get_seed_from_url(task_url)
        books = await fetch_data(seed_value=seed)
        dataset = {"books": books}
    all_genres = list({genre for book in dataset.get("books", []) for genre in book["genres"]})

    # Generar constraints
    constraints = []

    # Always add username and password constraints explicitly
    constraints.append({"field": "username", "operator": ComparisonOperator(ComparisonOperator.EQUALS), "value": USERNAME_PLACEHOLDER})
    constraints.append({"field": "password", "operator": ComparisonOperator(ComparisonOperator.EQUALS), "value": PASSWORD_PLACEHOLDER})

    # Select random fields to edit
    # Security Hotspot: random.sample and random.choice are used for non-security purposes (test data generation)
    selected_fields = sample(editable_fields, k=choice([1, 2, 3]))
    if "website" not in selected_fields:
        selected_fields.append("website")

    for field in selected_fields:
        constraint = _generate_edit_profile_field_constraint(field, random_names, random_text_elements, random_bios, random_locations, random_websites, all_genres)
        if constraint:
            constraints.append(constraint)

    return constraints
