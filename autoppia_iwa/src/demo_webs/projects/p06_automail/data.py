from copy import deepcopy
from datetime import UTC, datetime, timedelta

from ..operators import CONTAINS, EQUALS, NOT_CONTAINS, NOT_EQUALS


def transform_email_data(email: dict) -> dict:
    """
    Transform email data by flattening nested structures and adding computed fields.

    This function:
    1. Flattens the "from" dictionary by prefixing keys with "from_"
    2. Extracts the first email from the "to" array
    3. Adds an "is_spam" field based on labels
    4. Adds "date" (e.g. "Dec 1") from "timestamp" to match typical inbox list UI
    5. Adds "date_detail" (e.g. "12/10/2025 12:15:00 AM") for detail-style extraction

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

    # Each email is expected to have exactly one label.
    # Expose it as `label_name` so prompts and extraction can refer to it directly.
    label_name = None
    labels = email.get("labels")
    if isinstance(labels, list) and labels:
        first = labels[0]
        if isinstance(first, dict):
            label_name = first.get("name")
    email["label_name"] = label_name

    # Parse server timestamp once and convert to fixed UI timezone (UTC+5) for aligned formatting.
    dt_ui = None
    ts = email.get("timestamp")
    if isinstance(ts, str) and ts.strip():
        try:
            dt_utc = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(UTC)
            dt_ui = dt_utc + timedelta(hours=5)
        except (ValueError, TypeError, OSError):
            dt_ui = None

    # UI-style list date (e.g. "Dec 1") for search/list views.
    date = f"{dt_ui.strftime('%b')} {dt_ui.day}" if dt_ui else None
    email["date"] = date

    # Detail-style date string from ISO timestamp (e.g. "12/10/2025 12:15:00 AM").
    date_detail = None
    if dt_ui:
        hour12 = dt_ui.strftime("%I").lstrip("0") or "0"
        date_detail = f"{dt_ui.month}/{dt_ui.day}/{dt_ui.year} {hour12}:{dt_ui.strftime('%M:%S %p')}"
    email["date_detail"] = date_detail

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

# Body field: only contains and not_contains (no equals/not_equals) for reliable verification.
BODY_OPERATORS = [CONTAINS, NOT_CONTAINS]


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
    "body": BODY_OPERATORS,
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
    "body": BODY_OPERATORS,
}
FIELD_OPERATORS_TEMPLATE_SENT_MAP = {
    **FIELD_OPERATORS_TEMPLATE_BODY_EDITED_MAP,
    "to": STRING_OPERATORS,
}

# Visible fields used for synthetic data-extraction questions.
# Keep this list small and text-based to maximize extraction reliability.
VISIBLE_FIELDS_EMAIL_DETAIL = ["from_email", "subject", "from_name", "label_name", "body", "date_detail"]
VISIBLE_FIELDS_EMAIL_SEARCH = ["subject", "from_name", "label_name", "date"]
VISIBLE_FIELDS_TEMPLATE_DETAIL = ["name", "subject", "body"]
