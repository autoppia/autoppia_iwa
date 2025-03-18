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
        "<year>": "20<web_agent_id>",
        "<genre>": "Genre<web_agent_id>",
        "<movie_name>": "Movie<web_agent_id>",
    }

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text
