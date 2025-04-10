def login_replace_func(text: str) -> str:
    if not isinstance(text, str):
        return text

    replacements = {"<username>": "user<web_agent_id>", "<password>": "password123"}

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text


def register_replace_func(text: str) -> str:
    if not isinstance(text, str):
        return text

    replacements = {"<username>": "newuser<web_agent_id>", "<email>": "newuser<web_agent_id>@gmail.com", "<password>": "password123"}

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text
