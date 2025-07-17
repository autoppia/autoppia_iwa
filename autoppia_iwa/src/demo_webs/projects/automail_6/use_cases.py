from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    AddLabelEvent,
    CreateLabelEvent,
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
from .generation_functions import (
    generate_add_label_constraints,
    generate_create_label_constraints,
    generate_is_important_constraints,
    generate_is_read_constraints,
    generate_is_spam_constraints,
    generate_is_starred_constraints,
    generate_save_as_draft_constraints,
    generate_search_email_constraints,
    generate_send_email_constraints,
    generate_theme_changed_constraints,
    generate_view_email_constraints,
)
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
            "prompt": "View the email from 'alice.smith@company.com' with subject 'Project Kickoff Meeting'",
            "prompt_for_task_generation": "View the email from 'alice.smith@company.com' with subject 'Project Kickoff Meeting'",
        },
        {
            "prompt": "View the message from 'bob.johnson@tech.org'",
            "prompt_for_task_generation": "View the message from 'bob.johnson@tech.org'",
        },
        {
            "prompt": "View the email with subject 'Newsletter Subscription'",
            "prompt_for_task_generation": "View the email with subject 'Newsletter Subscription'",
        },
        {
            "prompt": "View the email with ID 'email4'",
            "prompt_for_task_generation": "View the email with ID 'email4'",
        },
        {
            "prompt": "View the email that subject is about 'Community Forum Update'",
            "prompt_for_task_generation": "View the email that subject is about 'Community Forum Update'",
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
            "prompt": "Star the email from 'grace.lee@company.com' with subject 'Team Outing Plan'",
            "prompt_for_task_generation": "Star the email from 'grace.lee@company.com' with subject 'Team Outing Plan'",
        },
        {
            "prompt": "Mark the email from 'bob.johnson@tech.org' as starred",
            "prompt_for_task_generation": "Mark the email from 'bob.johnson@tech.org' as starred",
        },
        {
            "prompt": "Mark the email titled 'Newsletter Subscription' as unstarred",
            "prompt_for_task_generation": "Mark the email titled 'Newsletter Subscription' as unstarred",
        },
        {
            "prompt": "Star the email with ID 'email7'",
            "prompt_for_task_generation": "Star the email with ID 'email7'",
        },
        {
            "prompt": "Mark the message about 'Lunch Plans' as favorite",
            "prompt_for_task_generation": "Mark the message about 'Lunch Plans' as favorite",
        },
    ],
)

MARK_EMAIL_AS_IMPORTANT_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENTS: Every prompt you generate MUST follow these rules:

1. Use clear action phrases such as:
   - "mark as important" or "mark as not important"
   - "flag as important or not important"
   - "set as high priority"

 The **is_important** MUST be reflected explicitly:
    IMPORTANT:
   - Use phrases like: "mark as important", or "flag as important", ONLY when 'is_important' is True.
   - Use phrases like: "mark as not important", ONLY when 'is_important' is False.

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
            "prompt": "Mark the email from 'david.brown@company.com' with subject 'Q2 Report Feedback' as important",
            "prompt_for_task_generation": "Mark the email from 'david.brown@company.com' with subject 'Q2 Report Feedback' as important",
        },
        {
            "prompt": "Flag the email from 'alice.smith@company.com' as important",
            "prompt_for_task_generation": "Flag the email from 'alice.smith@company.com' as important",
        },
        {
            "prompt": "Set the message with subject 'Project Status Update' to high priority",
            "prompt_for_task_generation": "Set the message with subject 'Project Status Update' to high priority",
        },
        {
            "prompt": "Mark the email with ID 'email25' as important",
            "prompt_for_task_generation": "Mark the email with ID 'email25' as important",
        },
        {
            "prompt": "Mark the message about 'Client Proposal Review' as high priority",
            "prompt_for_task_generation": "Mark the message about 'Client Proposal Review' as high priority",
        },
    ],
)

MARK_AS_UNREAD_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Start with 'mark as read', 'mark as unread', or equivalent natural phrasing.

 The **is_read** MUST be reflected explicitly:
    IMPORTANT:
   - Use phrases like: "mark as read", or "flag as read", ONLY when 'is_read' is True.
   - Use phrases like: "mark as unread", ONLY when 'is_read' is False.

2. Do **NOT** mention is_read in the prompt.

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
            "prompt": "Mark the email from 'emma.davis@yahoo.com' with subject 'Community Forum Update' as unread",
            "prompt_for_task_generation": "Mark the email from 'emma.davis@yahoo.com' with subject 'Community Forum Update' as unread",
        },
        {
            "prompt": "Set the message from 'carol.white@outlook.com' as unread",
            "prompt_for_task_generation": "Set the message from 'carol.white@outlook.com' as unread",
        },
        {
            "prompt": "Mark the email titled 'Support Ticket #1234' as unread",
            "prompt_for_task_generation": "Mark the email titled 'Support Ticket #1234' as unread",
        },
        {
            "prompt": "Mark the email with ID 'email8' as unread",
            "prompt_for_task_generation": "Mark the email with ID 'email8' as unread",
        },
        {
            "prompt": "Set the email about 'Exclusive Offer: 20% Off' back to unread",
            "prompt_for_task_generation": "Set the email about 'Exclusive Offer: 20% Off' back to unread",
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
            "prompt": "Delete the email from 'alice.smith@company.com' with subject 'Project Kickoff Meeting'",
            "prompt_for_task_generation": "Delete the email from 'alice.smith@company.com' with subject 'Project Kickoff Meeting'",
        },
        {
            "prompt": "Remove the message from 'alice.smith@company.com'",
            "prompt_for_task_generation": "Remove the message from 'alice.smith@company.com'",
        },
        {
            "prompt": "Trash the email titled 'Project Kickoff Meeting'",
            "prompt_for_task_generation": "Trash the email titled 'Project Kickoff Meeting'",
        },
        {
            "prompt": "Delete the email with ID 'email1'",
            "prompt_for_task_generation": "Delete the email with ID 'email1'",
        },
        {
            "prompt": "Remove the message about 'Project Kickoff Meeting'",
            "prompt_for_task_generation": "Remove the message about 'Project Kickoff Meeting'",
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
            "prompt": "Mark the email from 'alice.smith@company.com' with subject 'Project Kickoff Meeting' as spam",
            "prompt_for_task_generation": "Mark the email from 'alice.smith@company.com' with subject 'Project Kickoff Meeting' as spam",
        },
        {
            "prompt": "Report the message from 'alice.smith@company.com' as junk",
            "prompt_for_task_generation": "Report the message from 'alice.smith@company.com' as junk",
        },
        {
            "prompt": "Move the email titled 'Project Kickoff Meeting' to spam",
            "prompt_for_task_generation": "Move the email titled 'Project Kickoff Meeting' to spam",
        },
        {
            "prompt": "Mark the email with ID 'email1' as junk",
            "prompt_for_task_generation": "Mark the email with ID 'email1' as junk",
        },
        {
            "prompt": "Flag the message about 'Project Kickoff Meeting' as spam",
            "prompt_for_task_generation": "Flag the message about 'Project Kickoff Meeting' as spam",
        },
    ],
)
ADD_LABEL_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENTS: EVERY prompt you generate MUST follow these rules:

1. The **action** MUST be reflected explicitly:
    IMPORTANT: Do **NOT** mention 'action equal added' or 'action equals removed' in the prompt, instead use:
   - Use phrases like: "Add label", "Tag", or "Categorize" ONLY when action 'added'.
   - Use phrases like: "Remove label", "Untag", or "Uncategorize" ONLY when action is 'removed'.

2. Wording can vary (e.g., "Tag", "Categorize", "Untag", "Remove the label"), but it must follow the above structure and remain natural.

✅ Correct:
- Add the label 'Finance' to the email from 'john.doe@corp.com'
- Remove the label 'Travel' from the email with subject 'Trip Plan'
- Categorize the email from 'nina@design.io' with the 'Project' label

❌ Incorrect:
- Add label to an email where the action equals 'added'
- Remove label where subject is 'Meeting Notes'
- Apply the label_name not equal to 'Updates'
"""

ADD_LABEL_USE_CASE = UseCase(
    name="ADD_LABEL",
    description="The user adds a label to an email to categorize or organize it.",
    event=AddLabelEvent,
    event_source_code=AddLabelEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    constraints_generator=generate_add_label_constraints,
    additional_prompt_info=ADD_LABEL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Add the label 'Work' to the email from 'alice.smith@company.com'",
            "prompt_for_task_generation": "Add the label 'Work' to the email from 'alice.smith@company.com'",
        },
        {
            "prompt": "Remove the label 'Finance' from the email from 'henry.moore@tech.org'",
            "prompt_for_task_generation": "Remove the label 'Finance' from the email from 'henry.moore@tech.org'",
        },
        {
            "prompt": "Tag the email from 'john.doe@office.com' with the 'Project' label",
            "prompt_for_task_generation": "Tag the email from 'john.doe@office.com' with the 'Project' label",
        },
        {
            "prompt": "Uncategorize the email with subject 'Travel Itinerary' by removing the label 'Travel'",
            "prompt_for_task_generation": "Uncategorize the email with subject 'Travel Itinerary' by removing the label 'Travel'",
        },
        {
            "prompt": "Categorize the email from 'nina.chen@design.io' with the label 'Updates'",
            "prompt_for_task_generation": "Categorize the email from 'nina.chen@design.io' with the label 'Updates'",
        },
    ],
)

CREATE_LABEL_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Start with phrases like create label, add label, or make a new label.
2. Include the label name and optionally the color.
3. Use natural and varied language for user instructions.
"""

CREATE_LABEL_USE_CASE = UseCase(
    name="CREATE_LABEL",
    description="The user creates a new label with a specific name and optional color.",
    event=CreateLabelEvent,
    event_source_code=CreateLabelEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    constraints_generator=generate_create_label_constraints,
    additional_prompt_info=CREATE_LABEL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Create a label named 'Work' with color 'blue'",
            "prompt_for_task_generation": "Create a label named 'Work' with color 'blue'",
        },
        {
            "prompt": "Add a new label called 'Personal' and make it green",
            "prompt_for_task_generation": "Add a new label called 'Personal' and make it green",
        },
        {
            "prompt": "Make a label titled 'Finance' using the color yellow",
            "prompt_for_task_generation": "Make a label titled 'Finance' using the color yellow",
        },
        {
            "prompt": "Create a tag labeled 'Important' in red",
            "prompt_for_task_generation": "Create a tag labeled 'Important' in red",
        },
        {
            "prompt": "Add the label 'Travel' with a purple color",
            "prompt_for_task_generation": "Add the label 'Travel' with a purple color",
        },
    ],
)

# COMPOSE_EMAIL_ADDITIONAL_PROMPT_INFO = """
# CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
# 1. Start with compose, write, draft, or create a new email.
# 2. Include at least recipient email (to_email), and optionally subject or body.
# 3. Vary language naturally while preserving structure.
# """
#
# COMPOSE_EMAIL_USE_CASE = UseCase(
#     name="COMPOSE_EMAIL",
#     description="The user starts composing a new email, filling in recipient, subject, or body.",
#     event=ComposeEmailEvent,
#     event_source_code=ComposeEmailEvent.get_source_code_of_class(),
#     replace_func=replace_email_placeholders,
#     # constraints_generator=generate_compose_email_constraints,
#     additional_prompt_info=COMPOSE_EMAIL_ADDITIONAL_PROMPT_INFO,
#     examples=[
#         {
#             "prompt": "Compose an email to <to_email> with subject '<subject>' and message '<body>'",
#             "prompt_for_task_generation": "Compose an email to <to_email> with subject '<subject>' and message '<body>'",
#         },
#         {
#             "prompt": "Write a new message to <to_email> with subject '<subject>'",
#             "prompt_for_task_generation": "Write a new message to <to_email> with subject '<subject>'",
#         },
#         {
#             "prompt": "Create a draft email to <to_email>",
#             "prompt_for_task_generation": "Create a draft email to <to_email>",
#         },
#         {
#             "prompt": "Compose a message to <to_email> with the body '<body>'",
#             "prompt_for_task_generation": "Compose a message to <to_email> with the body '<body>'",
#         },
#         {
#             "prompt": "Draft an email for <to_email> about '<subject>'",
#             "prompt_for_task_generation": "Draft an email for <to_email> about '<subject>'",
#         },
#     ],
# )

SEND_EMAIL_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with send, submit, or dispatch an email.
2. Examples:
    Incorrect: Send an email to 'emma.watson@school.edu', ensuring the recipient does NOT equal 'emma.watson@school.edu'.
    Correct: Send an email to 'emma.watson@school.edu', ensuring the recipient does NOT equal 'john.wick@school.edu'.
    Correct: Send an email to 'emma.watson@school.edu'.

3. Phrasing must vary while keeping clear user intent to send.
"""

SEND_EMAIL_USE_CASE = UseCase(
    name="SEND_EMAIL",
    description="The user sends an email that has been composed, with the provided recipient, subject, and/or body.",
    event=SendEmailEvent,
    event_source_code=SendEmailEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    constraints_generator=generate_send_email_constraints,
    additional_prompt_info=SEND_EMAIL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Send the email to john.doe@gmail.com with subject 'Project Timeline Update'",
            "prompt_for_task_generation": "Send the email to john.doe@gmail.com with subject 'Project Timeline Update'",
        },
        {
            "prompt": "Submit the email to john.doe@gmail.com with subject 'Project Timeline Update'",
            "prompt_for_task_generation": "Submit the email to john.doe@gmail.com with subject 'Project Timeline Update'",
        },
        {
            "prompt": "Send a message to john.doe@gmail.com",
            "prompt_for_task_generation": "Send a message to john.doe@gmail.com",
        },
        {
            "prompt": "Dispatch the email to john.doe@gmail.com",
            "prompt_for_task_generation": "Dispatch the email to john.doe@gmail.com",
        },
        {
            "prompt": "Send a note to john.doe@gmail.com regarding 'Project Timeline Update'",
            "prompt_for_task_generation": "Send a note to john.doe@gmail.com regarding 'Project Timeline Update'",
        },
    ],
)

SAVE_AS_DRAFT_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with save as draft, keep as draft, or similar phrasing.
Examples:
    Incorrect: Save the email as a draft addressed to 'recipient@example.com' with the subject does NOT contain 'Training Workshop' and the recipient does NOT contain 'liam.johnson@business.co'.
    Correct: Save the email as a draft addressed to 'recipient@example.com' with the subject does NOT contain 'Training Workshop' and the recipient does NOT contain 'liam.johnson@business.co'.
    Correct: Save the email as a draft where email equal to 'recipient@example.com' with the subject does NOT contain 'Training Workshop'.

2. Include recipient (to_email), and optionally subject or body.
3. Maintain natural and varied user language.
"""

EMAIL_SAVE_AS_DRAFT_USE_CASE = UseCase(
    name="EMAIL_SAVE_AS_DRAFT",
    description="The user saves a composed email as a draft without sending it.",
    event=EmailSaveAsDraftEvent,
    event_source_code=EmailSaveAsDraftEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    constraints_generator=generate_save_as_draft_constraints,
    additional_prompt_info=SAVE_AS_DRAFT_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Save the email as draft where email equals jane.doe@example.com",
            "prompt_for_task_generation": "Save the email as draft where email equals jane.doe@example.com",
        },
        {
            "prompt": "Save the email as draft where subject contains 'Budget Review Meeting'",
            "prompt_for_task_generation": "Save the email as draft where subject contains 'Budget Review Meeting'",
        },
        {
            "prompt": "Keep the email as draft where email not equals jane.doe@example.com",
            "prompt_for_task_generation": "Keep the email as draft where email not equals jane.doe@example.com",
        },
        {
            "prompt": "Save the email as draft where body contains 'Please review the attached budget document.'",
            "prompt_for_task_generation": "Save the email as draft where body contains 'Please review the attached budget document.'",
        },
        {
            "prompt": "Keep the email as draft where email equals jane.doe@example.com and subject equals 'Budget Review Meeting'",
            "prompt_for_task_generation": "Keep the email as draft where email equals jane.doe@example.com and subject equals 'Budget Review Meeting'",
        },
        {
            "prompt": "Save the email as draft where subject not contains 'Budget Review Meeting'",
            "prompt_for_task_generation": "Save the email as draft where subject not contains 'Budget Review Meeting'",
        },
        {
            "prompt": "Keep the email as draft where body not contains 'Please review the attached budget document.'",
            "prompt_for_task_generation": "Keep the email as draft where body not contains 'Please review the attached budget document.'",
        },
        {
            "prompt": "Save the draft where email contains jane.doe@example.com and body contains 'Please review the attached budget document.'",
            "prompt_for_task_generation": "Save the draft where email contains jane.doe@example.com and body contains 'Please review the attached budget document.'",
        },
        {
            "prompt": "Save as draft any email where recipient contains jane.doe@example.com",
            "prompt_for_task_generation": "Save as draft any email where recipient contains jane.doe@example.com",
        },
        {
            "prompt": "Keep a draft of the message where subject equals 'Budget Review Meeting' and recipient equals jane.doe@example.com",
            "prompt_for_task_generation": "Keep a draft of the message where subject equals 'Budget Review Meeting' and recipient equals jane.doe@example.com",
        },
    ],
)

THEME_CHANGED_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Clearly indicate a change in theme (e.g., switch to dark/light/system).
2. IMPORTANT: Use ONE THEME NAME and mention ONLY ONCE.
 Examples:
    Correct: Change the application theme to 'system'.
    Correct: Change the application theme equal to 'system'.
    Correct: Apply the application theme NOT equal to 'dark'.
    Incorrect: Change the application theme to 'system' where the theme is equal to 'system'.
    Incorrect: Apply the application theme to 'system' where the theme is not equal to 'dark'.
"""

THEME_CHANGED_USE_CASE = UseCase(
    name="THEME_CHANGED",
    description="The user changes the application theme (e.g., dark, light, system default).",
    event=ThemeChangedEvent,
    event_source_code=ThemeChangedEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    constraints_generator=generate_theme_changed_constraints,
    additional_prompt_info=THEME_CHANGED_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Switch to dark theme",
            "prompt_for_task_generation": "Switch to dark theme",
        },
        {
            "prompt": "Change the application theme other than 'dark'",
            "prompt_for_task_generation": "Change the application theme other than 'dark'",
        },
        {
            "prompt": "Enable system default theme",
            "prompt_for_task_generation": "Enable system default theme",
        },
        {
            "prompt": "Change the application theme NOT equal to 'system'",
            "prompt_for_task_generation": "Change the application theme NOT equal to 'system'",
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
    constraints_generator=generate_search_email_constraints,
    additional_prompt_info=SEARCH_EMAIL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Search for emails with subject containing '<keyword>'",
            "prompt_for_task_generation": "Search for emails with subject containing '<keyword>'",
        },
        {
            "prompt": "Find emails from 'alice.smith@company.com'",
            "prompt_for_task_generation": "Find emails from 'alice.smith@company.com'",
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
            "prompt": "Find all emails from 'alice.smith@company.com' with subject about '<keyword>'",
            "prompt_for_task_generation": "Find all emails from 'alice.smith@company.com' with subject about '<keyword>'",
        },
    ],
)

###############################################################################
# FINAL LIST: ALL_USE_CASES
###############################################################################
ALL_USE_CASES = [
    SEARCH_EMAIL_USE_CASE,
    # VIEW_EMAIL_USE_CASE,
    # STAR_EMAIL_USE_CASE,
    # MARK_EMAIL_AS_IMPORTANT_USE_CASE,
    # MARK_AS_UNREAD_USE_CASE,
    # DELETE_EMAIL_USE_CASE,
    # MARK_AS_SPAM_USE_CASE,
    # ADD_LABEL_USE_CASE,
    # CREATE_LABEL_USE_CASE,
    # COMPOSE_EMAIL_USE_CASE,
    # SEND_EMAIL_USE_CASE,
    # EMAIL_SAVE_AS_DRAFT_USE_CASE,
    # THEME_CHANGED_USE_CASE,
]
