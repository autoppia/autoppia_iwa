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

    replacements = {"<username>": "newuser<web_agent_id>", "<password>": "password123"}

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text
