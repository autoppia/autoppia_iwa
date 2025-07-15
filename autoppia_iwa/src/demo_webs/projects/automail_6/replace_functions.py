from autoppia_iwa.src.demo_webs.projects.automail_6.data import EMAILS_DATA_MODIFIED


def replace_email_placeholders(text: str) -> str:
    emails_data: list = EMAILS_DATA_MODIFIED
    if not isinstance(text, str) or not emails_data:
        return text

    import random

    email = random.choice(emails_data)

    if "<subject>" in text:
        text = text.replace("<subject>", email["subject"])

    if "<from_email>" in text:
        text = text.replace("<from_email>", email["from"]["email"])

    if "<to_email>" in text:
        text = text.replace("<to_email>", email["to"][0]["email"] if email.get("to") else None)

    return text
