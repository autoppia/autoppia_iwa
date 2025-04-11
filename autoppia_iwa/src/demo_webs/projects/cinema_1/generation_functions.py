import random
from typing import Any

from ..criterion_helper import ComparisonOperator, CriterionValue, validate_criterion
from .data import FIELD_OPERATORS_MAP_ADD_COMMENT, FIELD_OPERATORS_MAP_CONTACT, MOVIES_DATA


def generate_film_constraints():
    """
    Generates constraints specifically for film-related use cases.
    Returns the constraints as structured data.
    """
    from .utils import build_constraints_info, parse_constraints_str

    # Generate fresh constraints based on movie data
    constraints_str = build_constraints_info(MOVIES_DATA)

    # Convert string to data structure
    if constraints_str:
        return parse_constraints_str(constraints_str)
    return None


def generate_contact_constraints() -> list:
    """
    Generates a list of structured constraints for the contact form.
    Each constraint is a dictionary with the form:
       {"field": <field>, "operator": <ComparisonOperator>, "value": <value>}
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

        # Convert operator from string to ComparisonOperator instance
        possible_ops = FIELD_OPERATORS_MAP_CONTACT[field]
        operator_str = random.choice(possible_ops)
        operator = ComparisonOperator(operator_str)

        value = _generate_random_value_for_contact(field)
        constraint = {"field": field, "operator": operator, "value": value}
        constraints_list.append(constraint)

    return constraints_list


def generate_film_filter_constraints():
    """
    Generates a combination of constraints for filtering movies
    using the actual years and genres of the movies.
    """
    from random import choice

    existing_years = list(set(movie["year"] for movie in MOVIES_DATA))

    existing_genres = list(set(genre for movie in MOVIES_DATA for genre in movie["genres"]))

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


def generate_constraint_from_solution(movie: dict, field: str, operator: ComparisonOperator, movies_data: list[dict]) -> dict[str, Any]:
    """
    Generates a constraint for a specific field and operator that the solution movie satisfies.
    Uses the complete set of movies to generate more realistic constraints.
    """
    constraint = {"field": field, "operator": operator}

    if field in ["name", "director"]:
        if operator == ComparisonOperator.EQUALS:
            constraint["value"] = movie[field]
        elif operator == ComparisonOperator.NOT_EQUALS:
            # Look for a different value from another movie
            other_values = [m[field] for m in movies_data if m[field] != movie[field]]
            if other_values:
                constraint["value"] = random.choice(other_values)
            else:
                constraint["value"] = "Other_" + field
        elif operator == ComparisonOperator.CONTAINS:
            text = movie[field]

            if len(text) <= 3:
                constraint["value"] = text
            else:
                if random.random() < 0.5:
                    constraint["value"] = text[:3]
                else:
                    constraint["value"] = text[-3:]
        elif operator == ComparisonOperator.NOT_CONTAINS:
            alphabet = "abcdefghijklmnopqrstuvwxyz"
            while True:
                test_str = "".join(random.choice(alphabet) for _ in range(3))
                if test_str.lower() not in movie[field].lower():
                    constraint["value"] = test_str
                    break

    elif field in ["year", "duration"]:
        value = movie[field]
        if operator == ComparisonOperator.EQUALS:
            constraint["value"] = value
        elif operator == ComparisonOperator.NOT_EQUALS:
            other_values = [m[field] for m in movies_data if m[field] != value]
            if other_values:
                constraint["value"] = random.choice(other_values)
            else:
                # Fallback: add or subtract 1
                constraint["value"] = value + (1 if random.random() > 0.5 else -1)

        elif operator == ComparisonOperator.GREATER_THAN:
            # movie[field] > constraint_value => constraint_value < movie[field]
            smaller_values = [m[field] for m in movies_data if m[field] < value]
            if smaller_values:
                constraint["value"] = random.choice(smaller_values)
            else:
                constraint["value"] = value - 1  # Fallback

        elif operator == ComparisonOperator.LESS_THAN:
            # movie[field] < constraint_value => constraint_value > movie[field]
            bigger_values = [m[field] for m in movies_data if m[field] > value]
            if bigger_values:
                constraint["value"] = random.choice(bigger_values)
            else:
                constraint["value"] = value + 1  # Fallback

        elif operator == ComparisonOperator.GREATER_EQUAL:
            # movie[field] >= constraint_value => constraint_value <= movie[field]
            valid_values = [m[field] for m in movies_data if m[field] <= value]
            if valid_values:
                constraint["value"] = random.choice(valid_values)
            else:
                constraint["value"] = value

        elif operator == ComparisonOperator.LESS_EQUAL:
            # movie[field] <= constraint_value => constraint_value >= movie[field]
            valid_values = [m[field] for m in movies_data if m[field] >= value]
            if valid_values:
                constraint["value"] = random.choice(valid_values)
            else:
                constraint["value"] = value

        elif operator == ComparisonOperator.IN_LIST:
            # The base movie must be included => include 'value' in the list
            other_values = [m[field] for m in movies_data if m[field] != value]
            sample_size = min(2, len(other_values))
            if other_values and sample_size > 0:
                constraint["value"] = [value, *random.sample(other_values, sample_size)]
            else:
                constraint["value"] = [value]

        elif operator == ComparisonOperator.NOT_IN_LIST:
            # The base movie must NOT be included
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
            other_values = [m[field] for m in movies_data if m[field] != value]
            if other_values:
                constraint["value"] = random.choice(other_values)
            else:
                # Force a slight change
                new_val = value + (0.1 if random.random() > 0.5 else -0.1)
                constraint["value"] = max(0, min(5, new_val))

        elif operator == ComparisonOperator.GREATER_THAN:
            # movie[field] > constraint_value => constraint_value < movie[field]
            smaller_values = [m[field] for m in movies_data if m[field] < value]
            if smaller_values:
                constraint["value"] = random.choice(smaller_values)
            else:
                # Lower a bit, without going below 0
                constraint["value"] = max(0, value - 0.1)

        elif operator == ComparisonOperator.LESS_THAN:
            # movie[field] < constraint_value => constraint_value > movie[field]
            bigger_values = [m[field] for m in movies_data if m[field] > value]
            if bigger_values:
                constraint["value"] = random.choice(bigger_values)
            else:
                # Increase a bit, without exceeding 5
                constraint["value"] = min(5, value + 0.1)

        elif operator == ComparisonOperator.GREATER_EQUAL:
            # movie[field] >= constraint_value => constraint_value <= movie[field]
            valid_values = [m[field] for m in movies_data if m[field] <= value]
            if valid_values:
                constraint["value"] = random.choice(valid_values)
            else:
                constraint["value"] = value

        elif operator == ComparisonOperator.LESS_EQUAL:
            # movie[field] <= constraint_value => constraint_value >= movie[field]
            valid_values = [m[field] for m in movies_data if m[field] >= value]
            if valid_values:
                constraint["value"] = random.choice(valid_values)
            else:
                constraint["value"] = value

        elif operator == ComparisonOperator.IN_LIST:
            other_values = [m[field] for m in movies_data if m[field] != value]
            sample_size = min(2, len(other_values))
            if other_values and sample_size > 0:
                constraint["value"] = [value, *random.sample(other_values, sample_size)]
            else:
                constraint["value"] = [value]

        elif operator == ComparisonOperator.NOT_IN_LIST:
            other_values = [m[field] for m in movies_data if m[field] != value]
            if other_values:
                constraint["value"] = random.sample(other_values, min(3, len(other_values)))
            else:
                # Generate 2 values outside of 'value'
                val1 = max(0, min(5, value + 0.1))
                val2 = max(0, min(5, value + 0.2))
                constraint["value"] = [val1, val2]

    elif field == "genres":
        if operator == ComparisonOperator.CONTAINS:
            if movie[field]:
                constraint["value"] = random.choice(movie[field])
            else:
                return None
        elif operator == ComparisonOperator.NOT_CONTAINS:
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
            # Take one or more genres from the movie so that it's included in the list
            if movie[field]:
                num_genres = min(len(movie[field]), random.randint(1, 2))
                constraint["value"] = random.sample(movie[field], num_genres)
            else:
                return None

        elif operator == ComparisonOperator.NOT_IN_LIST:
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

    # Verify that the generated constraint is valid for the solution movie
    criterion = CriterionValue(value=constraint["value"], operator=operator)
    if validate_criterion(movie.get(field), criterion):
        return constraint

    # If we reach here, the generated constraint is not valid for the base movie
    return None


def generate_add_comment_constraints():
    """
    Generates combinations of constraints for adding comments.
    """
    from random import choice, sample

    # Available movies
    movies = [movie["name"] for movie in MOVIES_DATA]

    # Words and phrases to generate comments
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
        "mind-blowing cinematography",
        "perfect storytelling",
        "incredible character development",
        "visually spectacular",
        "deeply emotional journey",
        "groundbreaking narrative",
        "exceptional performances",
        "thought-provoking plot",
        "revolutionary filmmaking",
        "beautifully crafted",
        "complex narrative",
        "intricate storyline",
        "subtle character arcs",
        "nuanced performances",
        "stunning visual effects",
        "immersive soundtrack",
        "innovative cinematography",
        "masterful editing",
        "atmospheric sound design",
        "kept me on the edge of my seat",
        "couldn't look away",
        "completely absorbed",
        "emotionally powerful",
        "intellectually stimulating",
        "redefines the genre",
        "unlike anything I've seen before",
        "sets a new standard",
        "a true cinematic experience",
    ]

    # Names for commenter_name
    commenter_names = ["John", "Sarah", "Michael", "Emma", "David", "Lisa", "Alex", "Rachel", "Tom", "Emily"]

    # Definition of operators for each field

    # Generate constraints
    constraints = []

    # Choose random fields (1 or 2)
    selected_fields = sample(["movie_name", "commenter_name", "content"], k=choice([1, 2, 3]))
    for field in selected_fields:
        # Choose a random operator for the field
        operator = choice(FIELD_OPERATORS_MAP_ADD_COMMENT[field])

        # Select value based on the field
        if field == "movie_name":
            value = choice(movies)
        elif field == "commenter_name":
            value = choice(commenter_names)
        else:  # content
            value = choice(comment_keywords)

        constraints.append({"field": field, "operator": ComparisonOperator(operator), "value": value})

    return constraints


def generate_edit_film_constraints():
    """
    Generates constraints specifically for editing film-related use cases.
    Returns the constraints as structured data.
    """
    from random import choice, randint, sample, uniform

    # Get available movies
    movies = MOVIES_DATA

    # Editable fields (without name because we already have the movie)
    editable_fields = ["director", "year", "genres", "rating", "duration", "cast"]

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
        # Longer words
        "cinema",
        "movie",
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

    all_genres = ["Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama", "Fantasy", "Horror", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"]

    # Generate constraints
    constraints = []

    # Select base movie
    base_movie = choice(movies)
    constraints.append({"field": "name", "operator": ComparisonOperator(ComparisonOperator.EQUALS), "value": base_movie["name"]})

    # Select 1, 2, 3 or 4 fields to edit
    selected_fields = sample(editable_fields, k=choice([1, 2, 3, 4]))

    for field in selected_fields:
        if field == "director":
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
        elif field == "duration":
            constraints.append(
                {
                    "field": field,
                    "operator": choice([ComparisonOperator(ComparisonOperator.EQUALS), ComparisonOperator(ComparisonOperator.GREATER_EQUAL), ComparisonOperator(ComparisonOperator.LESS_EQUAL)]),
                    "value": randint(50, 180),
                }
            )
        elif field == "cast":
            constraints.append(
                {
                    "field": field,
                    "operator": choice([ComparisonOperator(ComparisonOperator.EQUALS), ComparisonOperator(ComparisonOperator.CONTAINS), ComparisonOperator(ComparisonOperator.NOT_CONTAINS)]),
                    "value": choice(random_words),
                }
            )

    return constraints


def generate_add_film_constraints():
    """
    Generates constraints specifically for editing film-related use cases.
    Returns the constraints as structured data.
    """
    from random import choice, randint, sample, uniform

    # Editable fields
    editable_fields = ["director", "year", "genres", "rating", "duration", "cast"]

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
        # Longer words
        "cinema",
        "movie",
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

    all_genres = ["Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama", "Fantasy", "Horror", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"]

    # Generate constraints
    constraints = []

    # Select 1, 2, 3 or 4 fields to edit
    selected_fields = sample(editable_fields, k=choice([1, 2, 3, 4]))

    for field in selected_fields:
        if field == "director":
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
        elif field == "duration":
            constraints.append(
                {
                    "field": field,
                    "operator": choice([ComparisonOperator(ComparisonOperator.EQUALS), ComparisonOperator(ComparisonOperator.GREATER_EQUAL), ComparisonOperator(ComparisonOperator.LESS_EQUAL)]),
                    "value": randint(50, 180),
                }
            )
        elif field == "cast":
            constraints.append(
                {
                    "field": field,
                    "operator": choice([ComparisonOperator(ComparisonOperator.EQUALS), ComparisonOperator(ComparisonOperator.CONTAINS), ComparisonOperator(ComparisonOperator.NOT_CONTAINS)]),
                    "value": choice(random_words),
                }
            )

    return constraints


def generate_edit_profile_constraints():
    """
    Generates constraints specifically for editing user profiles.
    Returns the constraints as structured data.
    """
    from random import choice, sample

    from .data import FIELD_OPERATORS_MAP_EDIT_USER

    # Editable profile fields (username and email are excluded as mentioned in requirements)
    editable_fields = ["first_name", "last_name", "bio", "location", "website", "favorite_genres"]

    # Short words, letters, and syllables for text fields (for CONTAINS operators)
    random_text_elements = [
        "e",
        "a",
        "o",
        "x",
        "z",  # Single letters
        "car",
        "star",
        "red",
        "blue",
        "green",  # Short words
        "cinema",
        "movie",
        "light",
        "shadow",
        "dream",  # Longer words
    ]

    # Sample data for generating realistic values
    random_names = ["John", "Emma", "Michael", "Sophia", "James", "Olivia", "William", "Ava", "Benjamin", "Isabella", "Lucas", "Mia", "Henry", "Charlotte", "Alexander"]

    random_locations = ["New York, USA", "London, UK", "Tokyo, Japan", "Paris, France", "Sydney, Australia", "Toronto, Canada", "Berlin, Germany", "Rome, Italy", "Madrid, Spain", "Seoul, South Korea"]

    random_websites = [
        "https://filmcritics.example.com",
        "https://moviereviews.example.net",
        "https://cinephileworld.example.org",
        "https://filmjournals.example.io",
        "https://moviefans.example.co",
        "https://filmmakers.example.site",
    ]

    random_bios = [
        "Passionate about independent films and documentaries.",
        "Film school graduate with a love for classic cinema.",
        "Movie enthusiast exploring international cinema.",
        "Film critic specializing in sci-fi and fantasy genres.",
        "Animation lover and aspiring filmmaker.",
    ]

    all_genres = ["Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama", "Fantasy", "Horror", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"]

    # Generate constraints
    constraints = []

    # Select random fields to edit
    selected_fields = sample(editable_fields, k=choice([1, 2, 3]))

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
            value = choice(random_bios) if operator.name in [ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS] else choice(random_text_elements)
        elif field == "location":
            value = choice(random_locations) if operator.name in [ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS] else choice(random_text_elements)
        elif field == "website":
            # Website only uses EQUALS operator
            value = choice(random_websites)
        elif field == "favorite_genres":
            # For favorite_genres, only use EQUALS with a single genre
            value = choice(all_genres)

        constraints.append({"field": field, "operator": operator, "value": value})

    return constraints
