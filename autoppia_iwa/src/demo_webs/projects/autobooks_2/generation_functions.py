import random
from random import choice, randint, sample, uniform
from typing import Any

from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url

from ..criterion_helper import ComparisonOperator, CriterionValue, validate_criterion
from .data import FIELD_OPERATORS_MAP_ADD_COMMENT, FIELD_OPERATORS_MAP_CONTACT, FIELD_OPERATORS_MAP_EDIT_USER
from .data_utils import fetch_books_data


async def _get_data(seed_value: int | None = None, count: int = 100) -> list[dict]:
    return await fetch_books_data(seed_value=seed_value, count=count)


def generate_registration_constraints():
    """
    Generates constraints specifically for film-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import parse_constraints_str

    # Generar restricciones frescas basadas en los datos de películas
    constraints_str = "username equals newuser<web_agent_id> AND email equals newuser<web_agent_id>@gmail.com AND password equals PASSWORD"

    return parse_constraints_str(constraints_str)


def generate_login_constraints():
    """
    Generates constraints specifically for film-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import parse_constraints_str

    # Generar restricciones frescas basadas en los datos de películas

    constraints_str = "username equals <web_agent_id> AND password equals PASSWORD"

    return parse_constraints_str(constraints_str)


def generate_logout_constraints():
    """
    Generates constraints specifically for film-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import parse_constraints_str

    # Generar restricciones frescas basadas en los datos de películas
    constraints_str = "username equals <web_agent_id>"
    return parse_constraints_str(constraints_str)


async def generate_book_constraints(task_url: str | None = None, dataset: list[dict] | None = None):
    """
    Generates constraints specifically for book-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import build_constraints_info, parse_constraints_str

    # Generar restricciones frescas basadas en los datos de libros
    if dataset is None:
        v2_seed = get_seed_from_url(task_url)
        dataset = await _get_data(seed_value=v2_seed)
    constraints_str = build_constraints_info(dataset)

    # Convertir el string a la estructura de datos
    if constraints_str:
        return parse_constraints_str(constraints_str)
    return None


def generate_delete_book_constraints():
    """
    Generates constraints specifically for book-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import parse_constraints_str

    # Generar restricciones frescas basadas en los datos de películas
    constraints_str = "id equals <web_agent_id>"

    # Convertir el string a la estructura de datos
    if constraints_str:
        return parse_constraints_str(constraints_str)
    return None


async def generate_search_book_constraints(task_url: str | None = None, dataset: list[dict] | None = None):
    """
    Generates constraints specifically for film-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import parse_constraints_str

    if dataset is None:
        v2_seed = get_seed_from_url(task_url)
        dataset = await _get_data(seed_value=v2_seed)
    books_names = [book["name"] for book in dataset]
    operators = ["equals", "not_equals"]
    constraints_str = f"query {choice(operators)} {choice(books_names)}"
    return parse_constraints_str(constraints_str)


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


async def generate_book_filter_constraints(task_url: str | None = None, dataset: list[dict] | None = None):
    """
    Genera una combinación de constraints para filtrado de películas
    usando los años y géneros reales de las películas.
    """
    if dataset is None:
        v2_seed = get_seed_from_url(task_url)
        dataset = await _get_data(seed_value=v2_seed)
    existing_years = list(set(book["year"] for book in dataset))
    existing_genres = list(set(genre for book in dataset for genre in book["genres"]))

    generation_type = choice(["single_genre", "single_year", "genre_and_year"])

    constraints = []

    if generation_type == "single_genre":
        if existing_genres:
            constraints.append({"field": "genres", "operator": ComparisonOperator(ComparisonOperator.EQUALS), "value": choice(existing_genres)})

    elif generation_type == "single_year":
        if existing_years:
            constraints.append(
                {
                    "field": "year",
                    "operator": choice([ComparisonOperator(ComparisonOperator.EQUALS), ComparisonOperator(ComparisonOperator.GREATER_EQUAL), ComparisonOperator(ComparisonOperator.LESS_EQUAL)]),
                    "value": choice(existing_years),
                }
            )

    elif generation_type == "genre_and_year" and existing_genres and existing_years:
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


def generate_constraint_from_solution(book: dict, field: str, operator: ComparisonOperator, books_data: list[dict]) -> dict[str, Any]:
    """
    Genera un constraint para un campo y operador específicos que la película solución satisface.
    Utiliza el conjunto completo de películas para generar constraints más realistas.
    """
    constraint = {"field": field, "operator": operator}

    if field == "name" or field == "author" or field == "desc":
        if operator == ComparisonOperator.EQUALS:
            constraint["value"] = book[field]
        elif operator == ComparisonOperator.NOT_EQUALS:
            # Buscar un valor diferente de otra película
            other_values = [m[field] for m in books_data if m[field] != book[field]]
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

    elif field == "year" or field == "page_count" or field == "price":
        value = book[field]
        if operator == ComparisonOperator.EQUALS:
            constraint["value"] = value
        elif operator == ComparisonOperator.NOT_EQUALS:
            # Buscar un valor diferente de otra película
            other_values = [m[field] for m in books_data if m[field] != value]
            if other_values:
                constraint["value"] = random.choice(other_values)
            else:
                constraint["value"] = value + (1 if random.random() > 0.5 else -1)
        elif operator == ComparisonOperator.GREATER_THAN:
            # Encontrar un valor menor que el de la película
            lower_values = [m[field] for m in books_data if m[field] < value]
            if lower_values:
                constraint["value"] = random.choice(lower_values)
            else:
                constraint["value"] = value - 1
        elif operator == ComparisonOperator.LESS_THAN:
            # Encontrar un valor mayor que el de la película
            higher_values = [m[field] for m in books_data if m[field] > value]
            if higher_values:
                constraint["value"] = random.choice(higher_values)
            else:
                constraint["value"] = value + 1
        elif operator == ComparisonOperator.GREATER_EQUAL:
            # Podemos usar un valor igual o menor
            valid_values = [m[field] for m in books_data if m[field] <= value]
            if valid_values:
                constraint["value"] = random.choice(valid_values)
            else:
                constraint["value"] = value
        elif operator == ComparisonOperator.LESS_EQUAL:
            # Podemos usar un valor igual o mayor
            valid_values = [m[field] for m in books_data if m[field] >= value]
            if valid_values:
                constraint["value"] = random.choice(valid_values)
            else:
                constraint["value"] = value
        elif operator == ComparisonOperator.IN_LIST:
            # Incluir el valor de la película y posiblemente algunos otros valores
            other_values = [m[field] for m in books_data if m[field] != value]
            sample_size = min(2, len(other_values))
            if other_values and sample_size > 0:
                constraint["value"] = [value, *random.sample(other_values, sample_size)]
            else:
                constraint["value"] = [value]
        elif operator == ComparisonOperator.NOT_IN_LIST:
            # Encontrar valores que no incluyan el de la película
            other_values = [m[field] for m in books_data if m[field] != value]
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
            other_values = [m[field] for m in books_data if m[field] != value]
            if other_values:
                constraint["value"] = random.choice(other_values)
            else:
                # Asegurarse de que el valor alternativo esté en el rango 0-5
                constraint["value"] = max(0, min(5, value + (0.1 if random.random() > 0.5 else -0.1)))
        elif operator == ComparisonOperator.GREATER_THAN:
            # Encontrar un valor menor que el de la película
            lower_values = [m[field] for m in books_data if m[field] < value]
            if lower_values:
                constraint["value"] = random.choice(lower_values)
            else:
                # Asegurarse de que el valor sea positivo y menor que el original
                constraint["value"] = max(0, value - 0.1)
        elif operator == ComparisonOperator.LESS_THAN:
            # Encontrar un valor mayor que el de la película
            higher_values = [m[field] for m in books_data if m[field] > value]
            if higher_values:
                constraint["value"] = random.choice(higher_values)
            else:
                # Asegurarse de que el valor no exceda 5
                constraint["value"] = min(5, value + 0.1)
        elif operator == ComparisonOperator.GREATER_EQUAL:
            # Podemos usar un valor igual o menor
            valid_values = [m[field] for m in books_data if m[field] <= value]
            if valid_values:
                constraint["value"] = random.choice(valid_values)
            else:
                constraint["value"] = value
        elif operator == ComparisonOperator.LESS_EQUAL:
            # Podemos usar un valor igual o mayor
            valid_values = [m[field] for m in books_data if m[field] >= value]
            if valid_values:
                constraint["value"] = random.choice(valid_values)
            else:
                constraint["value"] = value
        elif operator == ComparisonOperator.IN_LIST:
            # Incluir el valor de la película y posiblemente algunos otros valores
            other_values = [m[field] for m in books_data if m[field] != value]
            sample_size = min(2, len(other_values))
            if other_values and sample_size > 0:
                constraint["value"] = [value, *random.sample(other_values, sample_size)]
            else:
                constraint["value"] = [value]
        elif operator == ComparisonOperator.NOT_IN_LIST:
            # Encontrar valores que no incluyan el de la película
            other_values = [m[field] for m in books_data if m[field] != value]
            if other_values:
                constraint["value"] = random.sample(other_values, min(3, len(other_values)))
            else:
                # Asegurarse de que los valores estén en el rango 0-5
                constraint["value"] = [max(0, min(5, value + 0.1)), max(0, min(5, value + 0.2))]

    elif field == "genres":
        if operator == ComparisonOperator.CONTAINS:
            if book[field]:
                constraint["value"] = random.choice(book[field])
            else:
                return None  # No se puede crear este constraint
        elif operator == ComparisonOperator.NOT_CONTAINS:
            # Encontrar un género que no esté en los géneros de la película
            all_genres = set()
            for m in books_data:
                all_genres.update(m["genres"])

            book_genres = set(book[field])
            available_genres = all_genres - book_genres

            if available_genres:
                constraint["value"] = random.choice(list(available_genres))
            else:
                constraint["value"] = "Non-existent genre"
        elif operator == ComparisonOperator.IN_LIST:
            if book[field]:
                # Tomar uno o más géneros de la película para la lista
                num_genres = min(len(book[field]), random.randint(1, 2))
                constraint["value"] = random.sample(book[field], num_genres)
            else:
                return None  # No se puede crear este constraint
        elif operator == ComparisonOperator.NOT_IN_LIST:
            # Similar a NOT_CONTAINS pero creando una lista
            all_genres = set()
            for m in books_data:
                all_genres.update(m["genres"])

            book_genres = set(book[field])
            available_genres = all_genres - book_genres

            if available_genres:
                num_genres = min(len(available_genres), random.randint(1, 3))
                constraint["value"] = random.sample(list(available_genres), num_genres)
            else:
                constraint["value"] = ["Non-existent genre"]

    if "value" not in constraint:
        return None

    # Verificar que el constraint generado es válido para la película solución
    criterion = CriterionValue(value=constraint["value"], operator=operator)
    if validate_criterion(book.get(field), criterion):
        return constraint

    # Si llegamos aquí, el constraint generado no es válido
    return None


async def generate_add_comment_constraints(task_url: str | None = None, dataset: list[dict] | None = None):
    """
    Genera combinaciones de constraints para añadir comentarios.
    """

    # Películas disponibles
    if dataset is None:
        v2_seed = get_seed_from_url(task_url)
        dataset = await _get_data(seed_value=v2_seed)
    books = [book["name"] for book in dataset]

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


async def generate_edit_book_constraints(task_url: str | None = None, dataset: list[dict] | None = None):
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

    if dataset is None:
        v2_seed = get_seed_from_url(task_url)
        dataset = await _get_data(seed_value=v2_seed)
    all_genres = list(set(genre for book in dataset for genre in book["genres"]))

    # Generar constraints
    constraints = []

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
                    "value": randint(50, 1080),
                }
            )
    return constraints


async def generate_add_book_constraints(task_url: str | None = None, dataset: list[dict] | None = None):
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

    if dataset is None:
        v2_seed = get_seed_from_url(task_url)
        dataset = await _get_data(seed_value=v2_seed)
    all_genres = list(set(genre for book in dataset for genre in book["genres"]))

    # Generar constraints
    constraints = []

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


async def generate_edit_profile_constraints(task_url: str | None = None, dataset: list[dict] | None = None):
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
        "Passionate about independent books and literary fiction.",
        "Avid reader with a love for classic literature.",
        "Book enthusiast exploring diverse genres and authors.",
        "Literary critic specializing in contemporary novels and poetry.",
        "Story lover and aspiring writer.",
    ]
    if dataset is None:
        v2_seed = get_seed_from_url(task_url)
        dataset = await _get_data(seed_value=v2_seed)
    all_genres = list(set(genre for book in dataset for genre in book["genres"]))

    # Generar constraints
    constraints = []

    # Select random fields to edit
    selected_fields = sample(editable_fields, k=choice([1, 2, 3]))
    if "website" not in selected_fields:
        selected_fields.append("website")
    for field in selected_fields:
        # Get valid operators for this field from the map
        valid_operators = FIELD_OPERATORS_MAP_EDIT_USER.get(field, [])

        if not valid_operators:
            continue

        # Convert string operator to ComparisonOperator instance
        operator_str = choice(valid_operators)
        operator = ComparisonOperator(operator_str)

        if field == "first_name" or field == "last_name":
            value = choice(random_names) if operator.name in [ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS] else choice(random_text_elements)
        elif field == "bio":
            # For bio, use CONTAINS or NOT_CONTAINS with a random text element
            value = choice(random_text_elements) if operator.name in [ComparisonOperator.CONTAINS, ComparisonOperator.NOT_CONTAINS] else choice(random_bios)
        elif field == "location":
            # For location, use EQUALS or NOT_EQUALS with a random location
            value = choice(random_text_elements) if operator.name in [ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS] else choice(random_locations)
        elif field == "website":
            # For website, use EQUALS or NOT_EQUALS with a random website
            value = choice(random_websites) if operator.name in [ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS] else choice(random_text_elements)
        elif field == "favorite_genres":
            # For favorite_genres, only use EQUALS with a single genre
            value = choice(all_genres)

        constraints.append({"field": field, "operator": operator, "value": value})

    return constraints
