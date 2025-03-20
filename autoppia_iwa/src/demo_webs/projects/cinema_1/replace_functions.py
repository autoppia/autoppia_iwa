def login_replace_func(text: str) -> str:
    """Replace username and password placeholders with web_agent_id"""
    if not isinstance(text, str):
        return text

    replacements = {"<username>": "user<web_agent_id>", "<password>": "password123"}

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text


def register_replace_func(text: str) -> str:
    """Replace username and password placeholders with web_agent_id"""
    if not isinstance(text, str):
        return text

    replacements = {"<username>": "newuser<web_agent_id>", "<email>": "newuser<web_agent_id>@gmail.com", "<password>": "password123"}

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text


def filter_film_replace_func(text: str) -> str:
    """Replace placeholders for year, genre, and movie name with web_agent_id"""
    if not isinstance(text, str):
        return text

    replacements = {
        "<year>": "2001",
        "<genre>": "Action",
        "<movie_name>": "The Lord of the Rings: The Fellowship of the Ring",
    }

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text


def view_film_detail_replace_func(text: str) -> str:
    """Replace placeholders for movie details with specific values."""
    if not isinstance(text, str):
        return text

    replacements = {
        "<movie_name>": "The Lord of the Rings: The Fellowship of the Ring",
        "<director>": "Peter Jackson",
        "<year>": "2001",
        "<genre>": "Action, Adventure, Fantasy",
        "<rating>": "4.6",
        "<duration>": "178",
        "<cast>": "Elijah Wood, Ian McKellen, Orlando Bloom",
    }

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text


def edit_film_replace_func(prompt: str) -> str:
    """
    Replaces placeholders in the prompt with hardcoded values.
    """
    replacements = {
        "<movie_id>": "101",
        "<new_movie_name>": "The Godfather: Remastered",
        "<new_director>": "Francis Ford Coppola",
        "<new_year>": "2024",
        "<new_rating>": "9.3",
        "<new_genre>": "Crime, Drama",
        "<new_duration>": "178",
        "<new_cast>": "Marlon Brando, Al Pacino, Robert De Niro",
    }

    for key, value in replacements.items():
        prompt = prompt.replace(key, value)

    return prompt


def add_film_replace_func(prompt: str) -> str:
    """
    Replace placeholders in the prompt with actual values from the given dictionary.
    """
    replacements = {
        "<movie_name>": "Mad Max: Fury Road",
        "<director>": "George Miller",
        "<year>": 2015,
        "<rating>": 8.1,
        "<genre>": "Action, Adventure",
        "<duration>": 120,
        "<cast>": "Tom Hardy, Charlize Theron, Nicholas Hoult",
    }

    for placeholder, replacement in replacements.items():
        if replacement:
            prompt = prompt.replace(placeholder, replacement)

    return prompt


def add_comment_replace_func(text: str) -> str:
    """Replace placeholders for comment content, commenter name, and movie name with specific values."""
    if not isinstance(text, str):
        return text

    replacements = {
        "<comment>": "This movie was amazing! Highly recommended.",
        "<commenter_name>": "MovieFan123",
        "<movie_name>": "Inception",
    }

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text


def contact_replace_func(text: str) -> str:
    """Replace placeholders for contact form fields with specific values."""
    if not isinstance(text, str):
        return text

    replacements = {
        "<name>": "John Doe",
        "<email>": "johndoe@example.com",
        "<subject>": "Inquiry about services",
        "<message>": "I would like more details about your offerings. Please get back to me soon.",
    }

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text


def edit_user_replace_func(text: str) -> str:
    """Replace placeholders for user profile fields with test values."""
    if not isinstance(text, str):
        return text

    replacements = {
        "<username>": "new_username",
        "<email>": "newemail@example.com",
        "<first_name>": "Alice",
        "<last_name>": "Smith",
        "<bio>": "Passionate about movies and music.",
        "<location>": "New York",
        "<website>": "https://aliceblog.com",
        "<favorite_genre>": "Science Fiction",
    }

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text
