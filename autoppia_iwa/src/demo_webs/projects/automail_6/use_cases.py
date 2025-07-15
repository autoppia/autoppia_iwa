from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    AddLabelEvent,
    ComposeEmailEvent,
    DeleteEmailEvent,
    EmailSaveAsDraftEvent,
    MarkAsSpamEvent,
    MarkAsUnreadEvent,
    MarkEmailAsImportantEvent,
    SearchEmailEvent,
    SendEmailEvent,
    StarEmailEvent,
    ThemeChangedEvent,
    ViewEmailEvent,
)
from .generation_functions import generate_is_important_constraints, generate_is_read_constraints, generate_is_spam_constraints, generate_is_starred_constraints, generate_view_email_constraints
from .replace_functions import replace_email_placeholders

VIEW_EMAIL_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. All prompt must start with view.
2. Must mention Subject and Email ID if its available.
ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""
VIEW_EMAIL_USE_CASE = UseCase(
    name="VIEW_EMAIL",
    description="The user selects an email to view and read its contents.",
    event=ViewEmailEvent,
    event_source_code=ViewEmailEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    constraints_generator=generate_view_email_constraints,
    additional_prompt_info=VIEW_EMAIL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "View the email from <from_email> with subject '<subject>'",
            "prompt_for_task_generation": "View the email from <from_email> with subject '<subject>'",
        },
        {
            "prompt": "View the message from <from_email>",
            "prompt_for_task_generation": "View the message from <from_email>",
        },
        {
            "prompt": "View the email with subject '<subject>'",
            "prompt_for_task_generation": "View the email with subject '<subject>'",
        },
        {
            "prompt": "View the email with ID <email_id>",
            "prompt_for_task_generation": "View the email with ID <email_id>",
        },
        {
            "prompt": "View the email that subject is about <subject>",
            "prompt_for_task_generation": "View the email that subject is about <subject>",
        },
    ],
)

STAR_EMAIL_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1.  Use clear action phrases such as:
   - "mark as starred"
   - "flag as starred"
   - "add to favorite"

2. Mention Subject, Email ID, or Sender if available.
3. Examples:
    Correct: "Mark the email with Subject containing 'g Workshop' as starred."
    Incorrect: "Mark the email with Subject containing 'g Workshop' as starred where isStarred is NOT equal to True.".
4. IMPORTANT: Do **NOT** mention isStarred in the prompt.
5. Only use natural phrasing and vary wording across prompts.
"""

STAR_EMAIL_USE_CASE = UseCase(
    name="STAR_AN_EMAIL",
    description="The user stars or unstar, marks or unmarks an email as important visually using the star icon.",
    event=StarEmailEvent,
    event_source_code=StarEmailEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    constraints_generator=generate_is_starred_constraints,
    additional_prompt_info=STAR_EMAIL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Star the email from <from_email> with subject '<subject>'",
            "prompt_for_task_generation": "Star the email from <from_email> with subject '<subject>'",
        },
        {
            "prompt": "Mark the email from <from_email> as starred",
            "prompt_for_task_generation": "Mark the email from <from_email> as starred",
        },
        {
            "prompt": "Mark the email titled '<subject>' as unstarred",
            "prompt_for_task_generation": "Mark the email titled '<subject>' as unstarred",
        },
        {
            "prompt": "Star the email with ID <email_id>",
            "prompt_for_task_generation": "Star the email with ID <email_id>",
        },
        {
            "prompt": "Mark the message about <subject> as favorite",
            "prompt_for_task_generation": "Mark the message about <subject> as favorite",
        },
    ],
)

MARK_EMAIL_AS_IMPORTANT_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENTS: Every prompt you generate MUST follow these rules:

1. Use clear action phrases such as:
   - "mark as important"
   - "flag as important"
   - "set as high priority"

2. Include at least one identifier for the email:
   - Subject
   - Email ID
   - Sender (from email)

3. Examples:
    Correct: "Mark the email with Subject containing 'g Workshop' as important."
    Incorrect: "Mark the email with Subject containing 'g Workshop' as important where isImportant is NOT equal to True."
4. IMPORTANT: Do **NOT** mention isImportant in the prompt.
5. Phrase each prompt naturally and vary the wording, but keep the user intent consistent.
"""


MARK_EMAIL_AS_IMPORTANT_USE_CASE = UseCase(
    name="MARK_EMAIL_AS_IMPORTANT",
    description="The user flags an email as important or gives it high priority.",
    event=MarkEmailAsImportantEvent,
    event_source_code=MarkEmailAsImportantEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    constraints_generator=generate_is_important_constraints,
    additional_prompt_info=MARK_EMAIL_AS_IMPORTANT_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Mark the email from <from_email> with subject '<subject>' as important",
            "prompt_for_task_generation": "Mark the email from <from_email> with subject '<subject>' as important",
        },
        {
            "prompt": "Flag the email from <from_email> as important",
            "prompt_for_task_generation": "Flag the email from <from_email> as important",
        },
        {
            "prompt": "Set the message with subject '<subject>' to high priority",
            "prompt_for_task_generation": "Set the message with subject '<subject>' to high priority",
        },
        {
            "prompt": "Mark the email with ID <email_id> as important",
            "prompt_for_task_generation": "Mark the email with ID <email_id> as important",
        },
        {
            "prompt": "Mark the message about <subject> as high priority",
            "prompt_for_task_generation": "Mark the message about <subject> as high priority",
        },
    ],
)

MARK_AS_UNREAD_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Start with 'mark as unread', 'set as unread', or equivalent natural phrasing.
2. Mention the Subject, Email ID, or Sender if available.
3. Vary wording across prompts but keep meaning intact.
"""

MARK_AS_UNREAD_USE_CASE = UseCase(
    name="MARK_AS_UNREAD",
    description="The user marks an already read email as unread.",
    event=MarkAsUnreadEvent,
    event_source_code=MarkAsUnreadEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    constraints_generator=generate_is_read_constraints,
    additional_prompt_info=MARK_AS_UNREAD_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Mark the email from <from_email> with subject '<subject>' as unread",
            "prompt_for_task_generation": "Mark the email from <from_email> with subject '<subject>' as unread",
        },
        {
            "prompt": "Set the message from <from_email> as unread",
            "prompt_for_task_generation": "Set the message from <from_email> as unread",
        },
        {
            "prompt": "Mark the email titled '<subject>' as unread",
            "prompt_for_task_generation": "Mark the email titled '<subject>' as unread",
        },
        {
            "prompt": "Mark the email with ID <email_id> as unread",
            "prompt_for_task_generation": "Mark the email with ID <email_id> as unread",
        },
        {
            "prompt": "Set the email about <subject> back to unread",
            "prompt_for_task_generation": "Set the email about <subject> back to unread",
        },
    ],
)

DELETE_EMAIL_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with delete, remove, or trash.
2. Include Subject, Email ID, or Sender when available.
3. Phrasing should remain natural and realistic for users.
"""

DELETE_EMAIL_USE_CASE = UseCase(
    name="DELETE_EMAIL",
    description="The user deletes an email, sending it to the trash or bin.",
    event=DeleteEmailEvent,
    event_source_code=DeleteEmailEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    constraints_generator=generate_view_email_constraints,
    additional_prompt_info=DELETE_EMAIL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Delete the email from <from_email> with subject '<subject>'",
            "prompt_for_task_generation": "Delete the email from <from_email> with subject '<subject>'",
        },
        {
            "prompt": "Remove the message from <from_email>",
            "prompt_for_task_generation": "Remove the message from <from_email>",
        },
        {
            "prompt": "Trash the email titled '<subject>'",
            "prompt_for_task_generation": "Trash the email titled '<subject>'",
        },
        {
            "prompt": "Delete the email with ID <email_id>",
            "prompt_for_task_generation": "Delete the email with ID <email_id>",
        },
        {
            "prompt": "Remove the message about <subject>",
            "prompt_for_task_generation": "Remove the message about <subject>",
        },
    ],
)

MARK_AS_SPAM_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Start with mark as spam, report as junk, move to spam, etc.
2. Always include either Subject, Email ID, or Sender.
3. Maintain natural, varied phrasing while preserving intent.
"""

MARK_AS_SPAM_USE_CASE = UseCase(
    name="MARK_AS_SPAM",
    description="The user flags an email as spam or junk to move it out of the inbox.",
    event=MarkAsSpamEvent,
    event_source_code=MarkAsSpamEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    constraints_generator=generate_is_spam_constraints,
    additional_prompt_info=MARK_AS_SPAM_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Mark the email from <from_email> with subject '<subject>' as spam",
            "prompt_for_task_generation": "Mark the email from <from_email> with subject '<subject>' as spam",
        },
        {
            "prompt": "Report the message from <from_email> as junk",
            "prompt_for_task_generation": "Report the message from <from_email> as junk",
        },
        {
            "prompt": "Move the email titled '<subject>' to spam",
            "prompt_for_task_generation": "Move the email titled '<subject>' to spam",
        },
        {
            "prompt": "Mark the email with ID <email_id> as junk",
            "prompt_for_task_generation": "Mark the email with ID <email_id> as junk",
        },
        {
            "prompt": "Flag the message about <subject> as spam",
            "prompt_for_task_generation": "Flag the message about <subject> as spam",
        },
    ],
)

ADD_LABEL_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with phrases like add label, categorize, or tag.
2. Must include label name AND either Subject, Email ID, or Sender.
3. Wording can vary, but the action and identifiers must remain consistent.
"""

ADD_LABEL_USE_CASE = UseCase(
    name="ADD_LABEL",
    description="The user adds a label to an email to categorize or organize it.",
    event=AddLabelEvent,
    event_source_code=AddLabelEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    # constraints_generator=generate_add_label_constraints,
    additional_prompt_info=ADD_LABEL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Add the label '<label>' to the email from <from_email> with subject '<subject>'",
            "prompt_for_task_generation": "Add the label '<label>' to the email from <from_email> with subject '<subject>'",
        },
        {
            "prompt": "Tag the email from <from_email> with the '<label>' label",
            "prompt_for_task_generation": "Tag the email from <from_email> with the '<label>' label",
        },
        {
            "prompt": "Add the '<label>' label to the message titled '<subject>'",
            "prompt_for_task_generation": "Add the '<label>' label to the message titled '<subject>'",
        },
        {
            "prompt": "Categorize the email with ID <email_id> under the '<label>' label",
            "prompt_for_task_generation": "Categorize the email with ID <email_id> under the '<label>' label",
        },
        {
            "prompt": "Add the '<label>' tag to the message about <subject>",
            "prompt_for_task_generation": "Add the '<label>' tag to the message about <subject>",
        },
    ],
)

COMPOSE_EMAIL_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Start with compose, write, draft, or create a new email.
2. Include at least recipient email (to_email), and optionally subject or body.
3. Vary language naturally while preserving structure.
"""

COMPOSE_EMAIL_USE_CASE = UseCase(
    name="COMPOSE_EMAIL",
    description="The user starts composing a new email, filling in recipient, subject, or body.",
    event=ComposeEmailEvent,
    event_source_code=ComposeEmailEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    # constraints_generator=generate_compose_email_constraints,
    additional_prompt_info=COMPOSE_EMAIL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Compose an email to <to_email> with subject '<subject>' and message '<body>'",
            "prompt_for_task_generation": "Compose an email to <to_email> with subject '<subject>' and message '<body>'",
        },
        {
            "prompt": "Write a new message to <to_email> with subject '<subject>'",
            "prompt_for_task_generation": "Write a new message to <to_email> with subject '<subject>'",
        },
        {
            "prompt": "Create a draft email to <to_email>",
            "prompt_for_task_generation": "Create a draft email to <to_email>",
        },
        {
            "prompt": "Compose a message to <to_email> with the body '<body>'",
            "prompt_for_task_generation": "Compose a message to <to_email> with the body '<body>'",
        },
        {
            "prompt": "Draft an email for <to_email> about '<subject>'",
            "prompt_for_task_generation": "Draft an email for <to_email> about '<subject>'",
        },
    ],
)

SEND_EMAIL_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with send, submit, or dispatch an email.
2. Include at least the recipient email (to_email) and one of subject or body.
3. Phrasing must vary while keeping clear user intent to send.
"""

SEND_EMAIL_USE_CASE = UseCase(
    name="SEND_EMAIL",
    description="The user sends an email that has been composed, with the provided recipient, subject, and/or body.",
    event=SendEmailEvent,
    event_source_code=SendEmailEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    # constraints_generator=generate_send_email_constraints,
    additional_prompt_info=SEND_EMAIL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Send the email to <to_email> with subject '<subject>' and body '<body>'",
            "prompt_for_task_generation": "Send the email to <to_email> with subject '<subject>' and body '<body>'",
        },
        {
            "prompt": "Submit the email to <to_email> with subject '<subject>'",
            "prompt_for_task_generation": "Submit the email to <to_email> with subject '<subject>'",
        },
        {
            "prompt": "Send a message to <to_email> saying '<body>'",
            "prompt_for_task_generation": "Send a message to <to_email> saying '<body>'",
        },
        {
            "prompt": "Dispatch the email to <to_email>",
            "prompt_for_task_generation": "Dispatch the email to <to_email>",
        },
        {
            "prompt": "Send a note to <to_email> regarding '<subject>'",
            "prompt_for_task_generation": "Send a note to <to_email> regarding '<subject>'",
        },
    ],
)

SAVE_AS_DRAFT_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with save as draft, keep as draft, or similar phrasing.
2. Include recipient (to_email), and optionally subject or body.
3. Maintain natural and varied user language.
"""

EMAIL_SAVE_AS_DRAFT_USE_CASE = UseCase(
    name="EMAIL_SAVE_AS_DRAFT",
    description="The user saves a composed email as a draft without sending it.",
    event=EmailSaveAsDraftEvent,
    event_source_code=EmailSaveAsDraftEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    # constraints_generator=generate_save_draft_constraints,
    additional_prompt_info=SAVE_AS_DRAFT_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Save the email to <to_email> with subject '<subject>' and message '<body>' as draft",
            "prompt_for_task_generation": "Save the email to <to_email> with subject '<subject>' and message '<body>' as draft",
        },
        {
            "prompt": "Keep the email for <to_email> with subject '<subject>' as a draft",
            "prompt_for_task_generation": "Keep the email for <to_email> with subject '<subject>' as a draft",
        },
        {
            "prompt": "Save a message to <to_email> as a draft",
            "prompt_for_task_generation": "Save a message to <to_email> as a draft",
        },
        {
            "prompt": "Save a draft to <to_email> with body '<body>'",
            "prompt_for_task_generation": "Save a draft to <to_email> with body '<body>'",
        },
        {
            "prompt": "Keep a draft email for <to_email> about '<subject>'",
            "prompt_for_task_generation": "Keep a draft email for <to_email> about '<subject>'",
        },
    ],
)

THEME_CHANGED_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Clearly indicate a change in theme (e.g., switch to dark/light/system).
2. Mention the specific theme being applied.
3. Phrasing can vary but must reflect intent to change appearance.
"""

THEME_CHANGED_USE_CASE = UseCase(
    name="THEME_CHANGED",
    description="The user changes the application theme (e.g., dark, light, system default).",
    event=ThemeChangedEvent,
    event_source_code=ThemeChangedEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    # constraints_generator=generate_theme_changed_constraints,
    additional_prompt_info=THEME_CHANGED_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Switch to dark theme",
            "prompt_for_task_generation": "Switch to dark theme",
        },
        {
            "prompt": "Change the theme to light",
            "prompt_for_task_generation": "Change the theme to light",
        },
        {
            "prompt": "Enable system default theme",
            "prompt_for_task_generation": "Enable system default theme",
        },
        {
            "prompt": "Switch from light to dark theme",
            "prompt_for_task_generation": "Switch from light to dark theme",
        },
        {
            "prompt": "Apply dark mode appearance",
            "prompt_for_task_generation": "Apply dark mode appearance",
        },
    ],
)

SEARCH_EMAIL_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Indicate a search or lookup (e.g., search for, find, look up).
2. Must include keywords from subject, sender, or label.
3. Clearly describe the search target in a natural way.
"""

SEARCH_EMAIL_USE_CASE = UseCase(
    name="SEARCH_EMAIL",
    description="The user performs a search query to locate emails based on specific keywords, sender, subject, or label.",
    event=SearchEmailEvent,
    event_source_code=SearchEmailEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    # constraints_generator=generate_search_email_constraints,
    additional_prompt_info=SEARCH_EMAIL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Search for emails with subject containing '<keyword>'",
            "prompt_for_task_generation": "Search for emails with subject containing '<keyword>'",
        },
        {
            "prompt": "Find emails from <from_email>",
            "prompt_for_task_generation": "Find emails from <from_email>",
        },
        {
            "prompt": "Look up messages labeled '<label>'",
            "prompt_for_task_generation": "Look up messages labeled '<label>'",
        },
        {
            "prompt": "Search for emails mentioning '<body_keyword>'",
            "prompt_for_task_generation": "Search for emails mentioning '<body_keyword>'",
        },
        {
            "prompt": "Find all emails from <from_email> with subject about '<keyword>'",
            "prompt_for_task_generation": "Find all emails from <from_email> with subject about '<keyword>'",
        },
    ],
)

###############################################################################
# FINAL LIST: ALL_USE_CASES
###############################################################################
ALL_USE_CASES = [
    # VIEW_EMAIL_USE_CASE,
    # STAR_EMAIL_USE_CASE,
    # MARK_EMAIL_AS_IMPORTANT_USE_CASE,
    # MARK_AS_UNREAD_USE_CASE,
    # DELETE_EMAIL_USE_CASE,
    MARK_AS_SPAM_USE_CASE,
    # ADD_LABEL_USE_CASE,
    # COMPOSE_EMAIL_USE_CASE,
    # SEND_EMAIL_USE_CASE,
    # EMAIL_SAVE_AS_DRAFT_USE_CASE,
    # THEME_CHANGED_USE_CASE,
    # SEARCH_EMAIL_USE_CASE,
]
