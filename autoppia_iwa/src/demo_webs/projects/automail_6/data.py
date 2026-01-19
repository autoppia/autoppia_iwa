from copy import deepcopy

from ..operators import CONTAINS, EQUALS, NOT_CONTAINS, NOT_EQUALS


def transform_email_data(email: dict) -> dict:
    """
    Transform email data by flattening nested structures and adding computed fields.

    This function:
    1. Flattens the "from" dictionary by prefixing keys with "from_"
    2. Extracts the first email from the "to" array
    3. Adds an "is_spam" field based on labels

    The function creates a deep copy of the input email, so the original is not modified.

    Args:
        email: Email dictionary to transform

    Returns:
        Transformed email dictionary (new copy, original unchanged)
    """
    # Create a copy to avoid modifying the original
    email = deepcopy(email)

    # Flatten "from" dictionary
    if email.get("from"):
        new_dict = {}
        for k, v in email["from"].items():
            new_dict["from_" + k] = v
        email.pop("from")
        email.update(new_dict)

    # Extract first email from "to" array
    if email.get("to") and isinstance(email["to"], list) and len(email["to"]) > 0:
        first_to = email["to"][0]
        if isinstance(first_to, dict):
            email["to"] = first_to.get("email", "")
        else:
            email["to"] = first_to

    # Add is_spam field based on labels
    email["is_spam"] = False
    for lbl in email.get("labels", []):
        if isinstance(lbl, dict) and lbl.get("id") == "spam":
            email["is_spam"] = True
            break

    return email


def transform_emails_list(emails: list[dict]) -> list[dict]:
    """
    Transform a list of email dictionaries.

    Args:
        emails: List of email dictionaries to transform

    Returns:
        List of transformed email dictionaries
    """
    return [transform_email_data(email) for email in emails]


def get_all_email_words(email_data):
    words = set()
    for email in email_data:
        if email.get("subject"):
            words.update(email["subject"].split())
        if email.get("from_email"):
            words.add(email["from_email"])
        if email.get("body"):
            words.update(email["body"].split())
    return list(words)


STRING_OPERATORS = [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]


FIELD_OPERATORS_VIEW_EMAIL_MAP = {
    "from_email": STRING_OPERATORS,
    "subject": STRING_OPERATORS,
}

FLAGGED_VARIABLES_OPERATORS = [EQUALS]

FIELD_OPERATORS_STARRED_MAP = {
    **FIELD_OPERATORS_VIEW_EMAIL_MAP,
    "is_starred": FLAGGED_VARIABLES_OPERATORS,
}

FIELD_OPERATORS_IMPORTANT_MAP = {
    **FIELD_OPERATORS_VIEW_EMAIL_MAP,
    "is_important": FLAGGED_VARIABLES_OPERATORS,
}

FIELD_OPERATORS_IS_READ_MAP = {
    **FIELD_OPERATORS_VIEW_EMAIL_MAP,
    "is_read": FLAGGED_VARIABLES_OPERATORS,
}

FIELD_OPERATORS_IS_SPAM_MAP = {
    **FIELD_OPERATORS_VIEW_EMAIL_MAP,
    "is_spam": FLAGGED_VARIABLES_OPERATORS,
}

FIELD_OPERATORS_SEARCH_MAP = {"query": STRING_OPERATORS}

FIELD_OPERATORS_SEND_OR_DRAFT_EMAIL_MAP = {
    "to": STRING_OPERATORS,
    "subject": STRING_OPERATORS,
    "body": STRING_OPERATORS,
}

FIELD_OPERATORS_CREATE_LABEL_MAP = {"label_name": STRING_OPERATORS, "label_color": STRING_OPERATORS}

FIELD_OPERATORS_ADD_LABEL_MAP = {
    "label_name": [EQUALS, NOT_EQUALS],
    "subject": STRING_OPERATORS,
    "body": [CONTAINS, NOT_CONTAINS],
    # "action": [EQUALS],
}

FIELD_OPERATORS_TEMPLATE_SELECTED_MAP = {
    "subject": STRING_OPERATORS,
    "template_name": STRING_OPERATORS,
}
FIELD_OPERATORS_TEMPLATE_BODY_EDITED_MAP = {
    **FIELD_OPERATORS_TEMPLATE_SELECTED_MAP,
    "body": STRING_OPERATORS,
}
FIELD_OPERATORS_TEMPLATE_SENT_MAP = {
    **FIELD_OPERATORS_TEMPLATE_BODY_EDITED_MAP,
    "to": STRING_OPERATORS,
}
