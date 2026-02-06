"""
Central definition of field–operator maps and value pools for autocinema.
Constraint generation uses these maps (no hardcoded operators in generation_functions).
"""
from ..operators import (
    CONTAINS,
    EQUALS,
    GREATER_EQUAL,
    GREATER_THAN,
    IN_LIST,
    LESS_EQUAL,
    LESS_THAN,
    NOT_CONTAINS,
    NOT_EQUALS,
    NOT_IN_LIST,
)

# Reusable operator groups (same pattern as autohealth)
STRING_OPERATORS = [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]
NUMERIC_OPERATORS = [EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL]
LIST_OPERATORS = [CONTAINS, NOT_CONTAINS, IN_LIST, NOT_IN_LIST]
EQUALITY_OPERATORS = [EQUALS, NOT_EQUALS]

# ---------------------------------------------------------------------------
# ADD_COMMENT
# ---------------------------------------------------------------------------
FIELD_OPERATORS_MAP_ADD_COMMENT = {
<<<<<<< HEAD
    "movie_name": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "commenter_name": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "content": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
}
FIELD_OPERATORS_MAP_FILM = {
    "name": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "director": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS, IN_LIST, NOT_IN_LIST],
    "year": [EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL],
    "rating": [EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL],
    "duration": [EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL],
    "genres": [CONTAINS, NOT_CONTAINS, IN_LIST, NOT_IN_LIST],
}
# Common Operators with Fields
FIELD_OPERATORS_MAP_CONTACT = {
    "name": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "email": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "subject": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "message": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
=======
    "movie_name": STRING_OPERATORS,
    "commenter_name": STRING_OPERATORS,
    "content": STRING_OPERATORS,
>>>>>>> b56bc1c4 (refactor: Enhance autocinema constraint generation)
}

# ---------------------------------------------------------------------------
# FILM (generic: FILM_DETAIL, DELETE_FILM, WATCH_TRAILER, etc. via build_constraints_info)
# ---------------------------------------------------------------------------
FIELD_OPERATORS_MAP_FILM = {
    "name": STRING_OPERATORS,
    "director": STRING_OPERATORS + [IN_LIST, NOT_IN_LIST],
    "year": NUMERIC_OPERATORS + [IN_LIST, NOT_IN_LIST],
    "rating": NUMERIC_OPERATORS,
    "duration": NUMERIC_OPERATORS,
    "genres": LIST_OPERATORS,
}

# ---------------------------------------------------------------------------
# SEARCH_FILM
# ---------------------------------------------------------------------------
FIELD_OPERATORS_MAP_SEARCH_FILM = {
    "query": EQUALITY_OPERATORS,
}

# ---------------------------------------------------------------------------
# EDIT_FILM (name is set separately from base movie; these are editable fields)
# ---------------------------------------------------------------------------
FIELD_OPERATORS_MAP_EDIT_FILM = {
    "director": STRING_OPERATORS,
    "year": [EQUALS, GREATER_EQUAL, LESS_EQUAL],
    "genres": [EQUALS],
    "rating": [EQUALS, GREATER_EQUAL, LESS_EQUAL],
    "duration": [EQUALS, GREATER_EQUAL, LESS_EQUAL],
    "cast": STRING_OPERATORS,
}

# ---------------------------------------------------------------------------
# ADD_FILM (same editable fields as EDIT_FILM, no name)
# ---------------------------------------------------------------------------
FIELD_OPERATORS_MAP_ADD_FILM = {
    "director": STRING_OPERATORS,
    "year": [EQUALS, GREATER_EQUAL, LESS_EQUAL],
    "genres": [EQUALS],
    "rating": [EQUALS, GREATER_EQUAL, LESS_EQUAL],
    "duration": [EQUALS, GREATER_EQUAL, LESS_EQUAL],
    "cast": STRING_OPERATORS,
}

# ---------------------------------------------------------------------------
# FILTER_FILM (field names must match FilterFilmEvent: genre_name, year)
# ---------------------------------------------------------------------------
FIELD_OPERATORS_MAP_FILTER_FILM = {
    "genre_name": [EQUALS],
    "year": [EQUALS, GREATER_EQUAL, LESS_EQUAL],
}

# ---------------------------------------------------------------------------
# CONTACT
# ---------------------------------------------------------------------------
FIELD_OPERATORS_MAP_CONTACT = {
    "name": STRING_OPERATORS,
    "email": STRING_OPERATORS,
    "subject": STRING_OPERATORS,
    "message": STRING_OPERATORS,
}

# ---------------------------------------------------------------------------
# EDIT_USER (profile fields only; username/password added in generator)
# ---------------------------------------------------------------------------
FIELD_OPERATORS_MAP_EDIT_USER = {
    "first_name": STRING_OPERATORS,
    "last_name": STRING_OPERATORS,
    "bio": [EQUALS, CONTAINS, NOT_EQUALS, NOT_CONTAINS],
    "location": STRING_OPERATORS,
    "website": [NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "favorite_genres": [IN_LIST, NOT_IN_LIST],
}

# Value pools for fields not coming from DB (contact form, profile edit)
CONTACT_NAMES = [
    "Alice", "Bob", "John", "Maria", "TestUser", "Peter", "Susan", "Robert",
    "Linda", "Michael", "Jessica", "William", "Karen", "David", "Lisa",
]
CONTACT_EMAILS = [
    "test@example.com", "info@example.org", "user@yahoo.com", "admin@domain.com",
    "contact@site.com", "noreply@domain.com", "service@provider.com", "hello@world.com",
    "support@company.com", "sales@business.com", "user1@site.com", "example@mail.com",
    "foo@bar.com", "john@doe.com", "jane@doe.com",
]
CONTACT_SUBJECTS = [
    "Feedback", "Inquiry", "Question", "Collaboration", "Request", "Complaint",
    "Suggestion", "Appointment", "Meeting", "Proposal", "Support", "Information", "Order", "Refund", "Other",
]
CONTACT_MESSAGES = [
    "Hello, I'd like more info", "Need further details please", "Just a quick question",
    "Hello, I'm interested in your services", "I have a query regarding your service",
    "Could you provide more details?", "I need assistance with my order", "I'm having an issue with the product",
    "Please contact me regarding my inquiry", "I want to learn more about your services",
    "Could you help me with my account?", "I'm writing to request support",
    "Please provide me with more information", "I would like to discuss a potential project",
    "I am interested in collaborating with you",
]
PROFILE_NAMES = [
    "John", "Emma", "Michael", "Sophia", "James", "Olivia", "William", "Ava",
    "Benjamin", "Isabella", "Lucas", "Mia", "Henry", "Charlotte", "Alexander",
]
PROFILE_LOCATIONS = [
    "New York, USA", "London, UK", "Tokyo, Japan", "Paris, France", "Sydney, Australia",
    "Toronto, Canada", "Berlin, Germany", "Rome, Italy", "Madrid, Spain", "Seoul, South Korea",
]
PROFILE_WEBSITES = [
    "https://filmcritics.example.com", "https://moviereviews.example.net",
    "https://cinephileworld.example.org", "https://filmjournals.example.io",
    "https://moviefans.example.co", "https://filmmakers.example.site",
]
PROFILE_BIOS = [
    "Passionate about independent films and documentaries.",
    "Film school graduate with a love for classic cinema.",
    "Movie enthusiast exploring international cinema.",
    "Film critic specializing in sci-fi and fantasy genres.",
    "Animation lover and aspiring filmmaker.",
]
PROFILE_TEXT_ELEMENTS = ["e", "a", "o", "x", "z", "car", "star", "red", "blue", "green", "cinema", "movie", "light", "shadow", "dream"]
ALL_GENRES = [
    "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama",
    "Fantasy", "Horror", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western",
]
FILM_RANDOM_WORDS = [
    "car", "star", "red", "blue", "green", "e", "a", "o", "x", "z",
    "cinema", "movie", "light", "shadow", "dream", "story", "heart", "vision",
    "gold", "silver", "thunder", "wind", "quantum", "stellar", "cosmic", "rhythm", "echo", "spark", "rebel", "sage",
]

# ADD_COMMENT value pools
COMMENTER_NAMES = ["John", "Sarah", "Michael", "Emma", "David", "Lisa", "Alex", "Rachel", "Tom", "Emily"]
COMMENT_KEYWORDS = [
    "amazing", "stunning", "great", "awesome", "fantastic", "brilliant", "incredible", "genius", "classic", "masterpiece",
    "mind-blowing cinematography", "perfect storytelling", "incredible character development", "visually spectacular",
    "deeply emotional journey", "groundbreaking narrative", "exceptional performances", "thought-provoking plot",
    "revolutionary filmmaking", "beautifully crafted", "emotionally powerful", "couldn't look away",
]
