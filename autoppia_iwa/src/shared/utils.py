import random
import string


def generate_random_web_agent_id(length: int = 16) -> str:
    """
    Generates a random alphanumeric string for the web_agent ID.
    """
    letters_and_digits = string.ascii_letters + string.digits
    return "".join(random.choice(letters_and_digits) for _ in range(length))
