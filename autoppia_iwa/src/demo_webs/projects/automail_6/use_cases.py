from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    AddLabelEvent,
    ArchiveEmailEvent,
    ClearSelectionEvent,
    CreateLabelEvent,
    DeleteEmailEvent,
    EditDraftEmailEvent,
    EmailSaveAsDraftEvent,
    EmailsNextPageEvent,
    EmailsPrevPageEvent,
    ForwardEmailEvent,
    MarkAsSpamEvent,
    MarkAsUnreadEvent,
    MarkEmailAsImportantEvent,
    ReplyEmailEvent,
    SearchEmailEvent,
    SendEmailEvent,
    StarEmailEvent,
    TemplateBodyEditedEvent,
    TemplateCanceledEvent,
    TemplateSavedDraftEvent,
    TemplateSelectedEvent,
    TemplateSentEvent,
    TemplatesViewedEvent,
    ThemeChangedEvent,
    ViewEmailEvent,
)
from .generation_functions import (
    generate_add_label_constraints,
    generate_archive_email_constraints,
    generate_create_label_constraints,
    generate_is_important_constraints,
    generate_is_read_constraints,
    generate_is_spam_constraints,
    generate_is_starred_constraints,
    generate_save_as_draft_send_email_constraints,
    generate_search_email_constraints,
    generate_sent_template_constraints,
    generate_template_body_constraints,
    generate_template_selection_constraints,
    generate_theme_changed_constraints,
    generate_view_email_constraints,
)

VIEW_EMAIL_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with one of the following: "View the email...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
4. Pay attention to the constraints:
Example:
constraints: {'subject': {'operator': 'equals', 'value': 'Win a Free Vacation!'}, 'from_email': {'operator': 'equals', 'value': 'spam@unknown.com'}}
Correct:
"View the email where subject equals 'Win a Free Vacation!' and email_from equals 'spam@unknown.com'."
Incorrect:
"View for spam@unknown.com email and Win a Free Vacation! subject."
""".strip()

VIEW_EMAIL_USE_CASE = UseCase(
    name="VIEW_EMAIL",
    description="The user selects an email to view and read its contents.",
    event=ViewEmailEvent,
    event_source_code=ViewEmailEvent.get_source_code_of_class(),
    constraints_generator=generate_view_email_constraints,
    additional_prompt_info=VIEW_EMAIL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "View the email where email_from equals 'alice.smith@company.com' and subject equals 'Project Kickoff Meeting'",
            "prompt_for_task_generation": "View the email where email_from equals 'alice.smith@company.com' and subject equals 'Project Kickoff Meeting'",
        },
        {
            "prompt": "View the email where email_from not equals 'bob.johnson@tech.org'",
            "prompt_for_task_generation": "View the email where email_from not equals 'bob.johnson@tech.org'",
        },
        {
            "prompt": "View the email where subject equals 'Newsletter Subscription'",
            "prompt_for_task_generation": "View the email where subject equals 'Newsletter Subscription'",
        },
        {
            "prompt": "View the email where subject contains 'Update'",
            "prompt_for_task_generation": "View the email where subject contains 'Update'",
        },
    ],
)

STAR_EMAIL_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with one of the following: "Star the email...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
4. Pay attention to the constraints:
Example:
constraints: {'subject': {'operator': 'equals', 'value': 'Budget Approval Request'}, 'from_email': {'operator': 'equals', 'value': 'nico.wells@org.com'}, 'is_starred': {'operator': 'equals', 'value': False}}
Correct:
"Star the email where subject equals 'Budget Approval Request' and from_email equals 'nico.wells@org.com' and is_starred equals False."
""".strip()

STAR_EMAIL_USE_CASE = UseCase(
    name="STAR_AN_EMAIL",
    description="The user stars or unstar, marks or unmarks an email as important visually using the star icon.",
    event=StarEmailEvent,
    event_source_code=StarEmailEvent.get_source_code_of_class(),
    constraints_generator=generate_is_starred_constraints,
    additional_prompt_info=STAR_EMAIL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Star the email where from_email equals 'grace.lee@company.com' and subject equals 'Team Outing Plan'",
            "prompt_for_task_generation": "Star the email where from_email equals 'grace.lee@company.com' and subject equals 'Team Outing Plan'",
        },
        {
            "prompt": "Star the email where from_email equals 'bob.johnson@tech.org' and is_starred equals 'False'",
            "prompt_for_task_generation": "Star the email where from_email equals 'bob.johnson@tech.org' and is_starred equals 'False'",
        },
        {
            "prompt": "Star the email where subject equals 'Re: Lunch Plans' and is_starred equals 'False'",
            "prompt_for_task_generation": "Star the email where subject equals 'Re: Lunch Plans' and is_starred equals 'False'",
        },
        {
            "prompt": "Star the email with ID 'email7'",
            "prompt_for_task_generation": "Star the email with ID 'email7'",
        },
    ],
)

MARK_EMAIL_AS_IMPORTANT_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with one of the following: "Mark the email as important...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
4. Pay attention to the constraints:
Example:
constraints: {'from_email': {'operator': 'equals', 'value': 'me@gmail.com'}, 'subject': {'operator': 'equals', 'value': 'Feature Request Feedback'}, 'is_important': {'operator': 'equals', 'value': True}}}
Correct:
"Mark the email where from equals 'me@gmail.com' and subject equals 'Feature Request Feedback' and is_important equals 'True'."
""".strip()


MARK_EMAIL_AS_IMPORTANT_USE_CASE = UseCase(
    name="MARK_EMAIL_AS_IMPORTANT",
    description="The user flags an email as important or gives it high priority.",
    event=MarkEmailAsImportantEvent,
    event_source_code=MarkEmailAsImportantEvent.get_source_code_of_class(),
    constraints_generator=generate_is_important_constraints,
    additional_prompt_info=MARK_EMAIL_AS_IMPORTANT_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Mark the email important where from equals 'david.brown@company.com' and subject equals 'Q2 Report Feedback' and is_important equals 'True'.",
            "prompt_for_task_generation": "Mark the email important where from equals 'david.brown@company.com' and subject equals 'Q2 Report Feedback' and is_important equals 'True'.",
        },
        {
            "prompt": "Mark the email important where from equals 'promo.bot@scam.com' and subject equals 'Amazing Deal Awaits!' and is_important equals 'False'.",
            "prompt_for_task_generation": "Mark the email important where from equals 'promo.bot@scam.com' and subject equals 'Amazing Deal Awaits!' and is_important equals 'False'.",
        },
        {
            "prompt": "Mark the email with ID 'email25' as important",
            "prompt_for_task_generation": "Mark the email with ID 'email25' as important",
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

2. Mention the Subject, Email ID, or Sender if available.
3. Vary wording across prompts but keep meaning intact.
4. Make sure the constraints for the fields are mentioned like contains, not_contains, equals, not_equals, etc.
5. Include ALL constraints in the prompt, including is_read.
Examples:
CORRECT: Mark the email unread where from email equals 'emma.davis@yahoo.com' and subject equals 'Community Forum Update' and is_read equals false.
INCORRECT: Mark the email unread 'emma.davis@yahoo.com'.
"""

MARK_AS_UNREAD_USE_CASE = UseCase(
    name="MARK_AS_UNREAD",
    description="The user marks an already read email as unread.",
    event=MarkAsUnreadEvent,
    event_source_code=MarkAsUnreadEvent.get_source_code_of_class(),
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
   Note: DO NOT mention action in the prompt instead start your prompt with the action verb directly like 'Add', 'Remove' etc.

2. Wording can vary (e.g., "Tag", "Categorize", "Untag", "Remove the label"), but it must follow the above structure and remain natural.

✅ Correct:
- Add the label 'Finance' to the email from 'john.doe@corp.com'
- Remove the label 'Travel' from the email with subject 'Trip Plan'
- Categorize the email from 'nina@design.io' with the 'Project' label

❌ Incorrect:
- Add label to an email where the action equals 'added'
- Remove label where subject is 'Meeting Notes'
- Apply the label_name not equal to 'Updates'

3. Do not mention any constraint twice in a single request:

Correct:  Remove the label from the email with subject 'Lunch Plans', the label_name is NOT 'Work', the body contains 'k''
Correct:  Remove the label from the email that is NOT 'Work', the body contains 'k', and the subject equals 'Lunch Plans'
Incorrect:  Remove the label from the email with subject 'Lunch Plans' where the action is 'removed', the label_name is NOT 'Work', the body contains 'k', and the subject equals 'Lunch Plans' (Mentioned subject twice, and mentioned 'where the action is 'Removed'.)
""".strip()

ADD_LABEL_USE_CASE = UseCase(
    name="ADD_LABEL",
    description="The user adds a label to an email to categorize or organize it.",
    event=AddLabelEvent,
    event_source_code=AddLabelEvent.get_source_code_of_class(),
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
    constraints_generator=generate_save_as_draft_send_email_constraints,
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
    constraints_generator=generate_save_as_draft_send_email_constraints,
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

EDIT_DRAFT_EMAIL_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with edit draft, open draft, or revise draft.
2. Include ALL given constraints in the prompt.
3. Make sure the constraints for the fields are mentioned like contains, not_contains, equals, not_equals, etc.
4. Do not mention a single constraint more than once in the request.
5. Do not add additional information in the prompt that is not mentioned in the constraints.
Examples:
    Correct: Edit the draft email where to equals 'jane.doe@example.com' and subject equals 'Budget Review Meeting'.
    Correct: Open the draft where to contains 'jane.doe' and subject not contains 'Training Workshop'.
    Incorrect: Edit the draft email where to equals 'jane.doe@example.com' and to equals 'jane.doe@example.com' (mentioned to twice).
""".strip()

EDIT_DRAFT_EMAIL_USE_CASE = UseCase(
    name="EDIT_DRAFT_EMAIL",
    description="The user opens and edits an existing draft email.",
    event=EditDraftEmailEvent,
    event_source_code=EditDraftEmailEvent.get_source_code_of_class(),
    constraints_generator=generate_save_as_draft_send_email_constraints,
    additional_prompt_info=EDIT_DRAFT_EMAIL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Edit the draft email where to equals 'jane.doe@example.com' and subject equals 'Client Proposal Updates'.",
            "prompt_for_task_generation": "Edit the draft email where to equals 'jane.doe@example.com' and subject equals 'Client Proposal Updates'.",
        },
        {
            "prompt": "Open the draft where to equals 'jane.doe@example.com' and revise it.",
            "prompt_for_task_generation": "Open the draft where to equals 'jane.doe@example.com' and revise it.",
        },
        {
            "prompt": "Edit the draft email where to contains 'jane.doe' and body contains 'Please review'.",
            "prompt_for_task_generation": "Edit the draft email where to contains 'jane.doe' and body contains 'Please review'.",
        },
    ],
)
ARCHIVE_EMAIL_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with Archive the email... or similar phrasing.
Examples:
CORRECT: "Archive the email whose from email equals 'alice.smith@company.com' and subject equals 'Project Kickoff Meeting'."
2. Include ALL given constraints in the prompt.
3. Maintain natural and varied user language.
"""

ARCHIVE_EMAIL_USE_CASE = UseCase(
    name="ARCHIVE_EMAIL",
    description="The user archives an email to remove it from the inbox.",
    event=ArchiveEmailEvent,
    event_source_code=ArchiveEmailEvent.get_source_code_of_class(),
    constraints_generator=generate_archive_email_constraints,
    additional_prompt_info=ARCHIVE_EMAIL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Archive the email whose from email equals 'alice.smith@company.com' and subject equals 'Project Kickoff Meeting'.",
            "prompt_for_task_generation": "Archive the email whose from email equals 'alice.smith@company.com' and subject equals 'Project Kickoff Meeting'.",
        },
        {
            "prompt": "Archive the email whose from email contains 'company.com' and subject not equals 'Project Kickoff Meeting'.",
            "prompt_for_task_generation": "Archive the email whose from email contains 'company.com' and subject not equals 'Project Kickoff Meeting'.",
        },
        {
            "prompt": "Archive the email whose from email not contains 'alice' and subject contains 'Project'.",
            "prompt_for_task_generation": "Archive the email whose from email not contains 'alice' and subject contains 'Project'.",
        },
    ],
)

REPLY_EMAIL_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with reply, reply all, or respond.
2. Include ALL given constraints in the prompt.
3. Make sure the constraints for the fields are mentioned like contains, not_contains, equals, not_equals, etc.
4. Do not mention a single constraint more than once in the request.
5. Do not add additional information in the prompt that is not mentioned in the constraints.
Examples:
    Correct: Reply to the email where from_email equals 'bob.johnson@tech.org' and subject equals 'Lunch Plans'.
    Correct: Reply all to the email where from_email contains 'bob' and subject contains 'Meeting'.
    Incorrect: Reply to the email where from_email equals 'bob.johnson@tech.org' and from_email contains 'bob' (mentioned from_email twice).
""".strip()

REPLY_EMAIL_USE_CASE = UseCase(
    name="REPLY_EMAIL",
    description="The user replies to an email.",
    event=ReplyEmailEvent,
    event_source_code=ReplyEmailEvent.get_source_code_of_class(),
    constraints_generator=generate_save_as_draft_send_email_constraints,
    additional_prompt_info=REPLY_EMAIL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Reply to the email where from_email equals 'bob.johnson@tech.org' and subject equals 'Lunch Plans'.",
            "prompt_for_task_generation": "Reply to the email where from_email equals 'bob.johnson@tech.org' and subject equals 'Lunch Plans'.",
        },
        {
            "prompt": "Reply all to the email where subject equals 'Project Kickoff Meeting'.",
            "prompt_for_task_generation": "Reply all to the email where subject equals 'Project Kickoff Meeting'.",
        },
        {
            "prompt": "Reply to the email where from_email contains 'bob' and to equals 'alice@company.com'.",
            "prompt_for_task_generation": "Reply to the email where from_email contains 'bob' and to equals 'alice@company.com'.",
        },
    ],
)

FORWARD_EMAIL_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with forward, send forward, or share.
2. Include ALL given constraints in the prompt.
3. Make sure the constraints for the fields are mentioned like contains, not_contains, equals, not_equals, etc.
4. Do not mention a single constraint more than once in the request.
5. Do not add additional information in the prompt that is not mentioned in the constraints.
Examples:
    Correct: Forward the email where subject equals 'Q2 Report Feedback' and to equals 'john.doe@gmail.com'.
    Correct: Forward the email where from_email equals 'alice.smith@company.com' and subject contains 'Report'.
    Incorrect: Forward the email where subject equals 'Q2 Report Feedback' and subject contains 'Report' (mentioned subject twice).
""".strip()

FORWARD_EMAIL_USE_CASE = UseCase(
    name="FORWARD_EMAIL",
    description="The user forwards an email to new recipients.",
    event=ForwardEmailEvent,
    event_source_code=ForwardEmailEvent.get_source_code_of_class(),
    constraints_generator=generate_save_as_draft_send_email_constraints,
    additional_prompt_info=FORWARD_EMAIL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Forward the email where subject equals 'Q2 Report Feedback' and to equals 'john.doe@gmail.com'.",
            "prompt_for_task_generation": "Forward the email where subject equals 'Q2 Report Feedback' and to equals 'john.doe@gmail.com'.",
        },
        {
            "prompt": "Forward the email where from_email equals 'alice.smith@company.com' and subject equals 'Project Update'.",
            "prompt_for_task_generation": "Forward the email where from_email equals 'alice.smith@company.com' and subject equals 'Project Update'.",
        },
        {
            "prompt": "Forward the email where from_email contains 'alice' and to contains 'john'.",
            "prompt_for_task_generation": "Forward the email where from_email contains 'alice' and to contains 'john'.",
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
2. Clearly describe the search target in a natural way.
"""

SEARCH_EMAIL_USE_CASE = UseCase(
    name="SEARCH_EMAIL",
    description="The user performs a search query to locate emails based on specific keywords, sender, subject, or label.",
    event=SearchEmailEvent,
    event_source_code=SearchEmailEvent.get_source_code_of_class(),
    constraints_generator=generate_search_email_constraints,
    additional_prompt_info=SEARCH_EMAIL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Search for query containing 'Weekly Newsletter'",
            "prompt_for_task_generation": "Search for query containing 'Weekly Newsletter'",
        },
        {
            "prompt": "Find emails from 'levi.brooks@org.com'",
            "prompt_for_task_generation": "Find emails from 'levi.brooks@org.com'",
        },
        {
            "prompt": "Look up messages containing 'Team Feedback Request'",
            "prompt_for_task_generation": "Look up messages containing 'Team Feedback Request'",
        },
        {
            "prompt": "Search for emails mentioning 'system upgrade is scheduled'",
            "prompt_for_task_generation": "Search for emails mentioning 'system upgrade is scheduled'",
        },
        {
            "prompt": "Find email from 'asher.gordon@org.com'.",
            "prompt_for_task_generation": "Find email from 'asher.gordon@org.com'.",
        },
    ],
)

# CLEAR_SELECTION (no constraints)
CLEAR_SELECTION_USE_CASE = UseCase(
    name="CLEAR_SELECTION",
    description="The user clears all selected emails.",
    event=ClearSelectionEvent,
    event_source_code=ClearSelectionEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {
            "prompt": "Clear the current selection.",
            "prompt_for_task_generation": "Clear the current selection.",
        }
    ],
)

EMAILS_NEXT_PAGE_USE_CASE = UseCase(
    name="EMAILS_NEXT_PAGE",
    description="The user paginates to the next set of emails.",
    event=EmailsNextPageEvent,
    event_source_code=EmailsNextPageEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {
            "prompt": "Go to the next page of emails.",
            "prompt_for_task_generation": "Go to the next page of emails.",
        },
        {
            "prompt": "See emails that are on next page.",
            "prompt_for_task_generation": "See emails that are on next page.",
        },
        {
            "prompt": "Move forward to the next page of emails.",
            "prompt_for_task_generation": "Move forward to the next page of emails.",
        },
    ],
)

EMAILS_PREV_PAGE_USE_CASE = UseCase(
    name="EMAILS_PREV_PAGE",
    description="The user paginates back to the previous set of emails.",
    event=EmailsPrevPageEvent,
    event_source_code=EmailsPrevPageEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {
            "prompt": "Go back to the previous page of emails.",
            "prompt_for_task_generation": "Go back to the previous page of emails.",
        },
        {
            "prompt": "Move backward to view emails that are on earlier page.",
            "prompt_for_task_generation": "Move backward to view emails that are on earlier page.",
        },
        {
            "prompt": "See emails that are on previous page.",
            "prompt_for_task_generation": "See emails that are on previous page.",
        },
    ],
)

VIEW_TEMPLATES_USE_CASE = UseCase(
    name="VIEW_TEMPLATES",
    description="The user opens the email templates section.",
    event=TemplatesViewedEvent,
    event_source_code=TemplatesViewedEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {
            "prompt": "Open the email templates page.",
            "prompt_for_task_generation": "Open the email templates section.",
        },
        {
            "prompt": "Go to the email templates page.",
            "prompt_for_task_generation": "Go to the email templates page.",
        },
        {
            "prompt": "View the email templates.",
            "prompt_for_task_generation": "View the email templates.",
        },
    ],
)

TEMPLATE_SELECTED_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with select template, choose template, or pick template.
2. Include ALL given constraints in the prompt.
3. Make sure the constraints for the fields are mentioned like contains, not_contains, equals, not_equals, etc.
4. Do not mention a single constraint more than once in the request.
5. Do not add additional information in the prompt that is not mentioned in the constraints.
Examples:
    Correct: Select the template where template_name equals 'Warm Introduction' and subject equals 'Introduction & Next Steps'.
    Correct: Choose the template where subject contains 'Next Steps'.
    Incorrect: Select the template where template_name equals 'Warm Introduction' and name equals 'Warm Introduction' (mentioned template_name twice).
""".strip()

TEMPLATE_SELECTED_USE_CASE = UseCase(
    name="TEMPLATE_SELECTED",
    description="The user chooses a specific email template to work with.",
    event=TemplateSelectedEvent,
    event_source_code=TemplateSelectedEvent.get_source_code_of_class(),
    constraints_generator=generate_template_selection_constraints,
    additional_prompt_info=TEMPLATE_SELECTED_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Select the template where template_name equals 'Meeting Recap'.",
            "prompt_for_task_generation": "Select the template where template_name equals 'Meeting Recap'.",
        },
        {
            "prompt": "Select the template where subject equals 'Introduction & Next Steps'.",
            "prompt_for_task_generation": "Select the template where subject equals 'Introduction & Next Steps'.",
        },
        {
            "prompt": "Select the template where template_name equals 'Friendly Follow Up' and subject contains 'follow-up'.",
            "prompt_for_task_generation": "Select the template where template_name equals 'Friendly Follow Up' and subject contains 'follow-up'.",
        },
    ],
)

TEMPLATE_BODY_EDITED_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with edit template body, update template body, or modify template content.
2. Include ALL given constraints in the prompt.
3. Make sure the constraints for the fields are mentioned like contains, not_contains, equals, not_equals, etc.
4. Do not mention a single constraint more than once in the request.
5. Do not add additional information in the prompt that is not mentioned in the constraints.

⚠️ CRITICAL: PRESERVE PLACEHOLDERS ⚠️
If a constraint value contains placeholders like <name>, <date>, <email>, you MUST keep them EXACTLY as they appear.
DO NOT remove them. DO NOT replace them with actual values. DO NOT add spaces where they were.
Example: If body equals 'Hi <name>, welcome!' then the prompt MUST include 'Hi <name>, welcome!' with <name> intact.

Examples:
    Correct: Update the body text of the template where template_name equals 'Warm Introduction' and subject equals 'Introduction & Next Steps'.
    Correct: Edit the body of the template where template_name contains 'Introduction'.
    Correct: Edit the body where body equals 'Hi <name>, welcome!' (placeholder preserved).
    Incorrect: Update the body text of the template where template_name equals 'Warm Introduction' and name equals 'Warm Introduction' (mentioned template_name twice).
    Incorrect: Edit the body where body equals 'Hi , welcome!' (placeholder removed - WRONG!).
""".strip()

TEMPLATE_BODY_EDITED_USE_CASE = UseCase(
    name="TEMPLATE_BODY_EDITED",
    description="The user edits the body of a selected template.",
    event=TemplateBodyEditedEvent,
    event_source_code=TemplateBodyEditedEvent.get_source_code_of_class(),
    constraints_generator=generate_template_body_constraints,
    additional_prompt_info=TEMPLATE_BODY_EDITED_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Update the body text of the template where template_name equals 'Warm Introduction'.",
            "prompt_for_task_generation": "Update the body text of the template where template_name equals 'Warm Introduction'.",
        },
        {
            "prompt": "Update the body text of the template where subject equals 'Thank you for your time'.",
            "prompt_for_task_generation": "Update the body text of the template where subject equals 'Thank you for your time'.",
        },
        {
            "prompt": "Edit the body of the template where body equals 'Hi <name>, thank you for connecting!'.",
            "prompt_for_task_generation": "Edit the body of the template where body equals 'Hi <name>, thank you for connecting!'.",
        },
    ],
)

TEMPLATE_SENT_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with send template, send email using template, or dispatch template.
2. Include ALL given constraints in the prompt.
3. Make sure the constraints for the fields are mentioned like contains, not_contains, equals, not_equals, etc.
4. Do not mention a single constraint more than once in the request.
5. Do not add additional information in the prompt that is not mentioned in the constraints.

⚠️ CRITICAL: PRESERVE PLACEHOLDERS ⚠️
If a constraint value contains placeholders like <name>, <date>, <email>, you MUST keep them EXACTLY as they appear.
DO NOT remove them. DO NOT replace them with actual values. DO NOT add spaces where they were.
Example: If body equals 'Hello <name>, welcome!' then the prompt MUST include 'Hello <name>, welcome!' with <name> intact.

Examples:
    Correct: Send an email using the template where template_name equals 'Friendly Follow Up' and to equals 'john.doe@gmail.com'.
    Correct: Send the template where subject contains 'follow-up' and to contains 'john'.
    Correct: Send the template where body equals 'Hello <name>, welcome!' (placeholder preserved).
    Incorrect: Send an email using the template where template_name equals 'Friendly Follow Up' and name equals 'Friendly Follow Up' (mentioned template_name twice).
    Incorrect: Send the template where body equals 'Hello , welcome!' (placeholder removed - WRONG!).
""".strip()

TEMPLATE_SENT_USE_CASE = UseCase(
    name="TEMPLATE_SENT",
    description="The user sends an email from a template.",
    event=TemplateSentEvent,
    event_source_code=TemplateSentEvent.get_source_code_of_class(),
    constraints_generator=generate_sent_template_constraints,
    additional_prompt_info=TEMPLATE_SENT_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Send an email using the template where template_name equals 'Friendly Follow Up'.",
            "prompt_for_task_generation": "Send an email using the template where template_name equals 'Friendly Follow Up'.",
        },
        {
            "prompt": "Send an email using the template where template_name equals 'Warm Introduction' and to equals 'alice@company.com'.",
            "prompt_for_task_generation": "Send an email using the template where template_name equals 'Warm Introduction' and to equals 'alice@company.com'.",
        },
        {
            "prompt": "Send the template where body equals 'Hello <name>, I hope this message finds you well!'.",
            "prompt_for_task_generation": "Send the template where body equals 'Hello <name>, I hope this message finds you well!'.",
        },
    ],
)

TEMPLATE_SAVED_DRAFT_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with save template as draft, keep template as draft, or store template draft.
2. Include ALL given constraints in the prompt.
3. Make sure the constraints for the fields are mentioned like contains, not_contains, equals, not_equals, etc.
4. Do not mention a single constraint more than once in the request.
5. Do not add additional information in the prompt that is not mentioned in the constraints.

⚠️ CRITICAL: PRESERVE PLACEHOLDERS ⚠️
If a constraint value contains placeholders like <name>, <date>, <email>, you MUST keep them EXACTLY as they appear.
DO NOT remove them. DO NOT replace them with actual values. DO NOT add spaces where they were.
Example: If body equals 'Hello <name>, welcome!' then the prompt MUST include 'Hello <name>, welcome!' with <name> intact.

Examples:
    Correct: Save the template as draft where template_name equals 'Warm Introduction' and to equals 'john.doe@gmail.com'.
    Correct: Keep the template as draft where subject contains 'follow-up'.
    Correct: Save template as draft where body equals 'Hello <name>, welcome!' (placeholder preserved).
    Incorrect: Save the template as draft where template_name equals 'Warm Introduction' and name equals 'Warm Introduction' (mentioned template_name twice).
    Incorrect: Save template as draft where body equals 'Hello , welcome!' (placeholder removed - WRONG!).
""".strip()

TEMPLATE_SAVED_DRAFT_USE_CASE = UseCase(
    name="TEMPLATE_SAVED_DRAFT",
    description="The user saves an email template as a draft.",
    event=TemplateSavedDraftEvent,
    event_source_code=TemplateSavedDraftEvent.get_source_code_of_class(),
    constraints_generator=generate_sent_template_constraints,
    additional_prompt_info=TEMPLATE_SAVED_DRAFT_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Save the template as draft where template_name equals 'Warm Introduction'.",
            "prompt_for_task_generation": "Save the template as draft where template_name equals 'Warm Introduction'.",
        },
        {
            "prompt": "Save the template as draft where template_name equals 'Meeting Recap' and to equals 'alice@company.com'.",
            "prompt_for_task_generation": "Save the template as draft where template_name equals 'Meeting Recap' and to equals 'alice@company.com'.",
        },
        {
            "prompt": "Keep the template as draft where body equals 'Dear <name>, thank you for your time!'.",
            "prompt_for_task_generation": "Keep the template as draft where body equals 'Dear <name>, thank you for your time!'.",
        },
    ],
)

TEMPLATE_CANCELED_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with cancel template, discard template changes, or reset template.
2. Include ALL given constraints in the prompt.
3. Make sure the constraints for the fields are mentioned like contains, not_contains, equals, not_equals, etc.
4. Do not mention a single constraint more than once in the request.
5. Do not add additional information in the prompt that is not mentioned in the constraints.

⚠️ CRITICAL: PRESERVE PLACEHOLDERS ⚠️
If a constraint value contains placeholders like <name>, <date>, <email>, you MUST keep them EXACTLY as they appear.
DO NOT remove them. DO NOT replace them with actual values. DO NOT add spaces where they were.
Example: If body equals 'Hi <name>, thank you!' then the prompt MUST include 'Hi <name>, thank you!' with <name> intact.

Examples:
    Correct: Cancel changes on the template where template_name equals 'Thank You' and subject equals 'Thank you for your time'.
    Correct: Discard changes to the template where template_name contains 'Follow Up'.
    Correct: Cancel template where body equals 'Hi <name>, thank you!' (placeholder preserved).
    Incorrect: Cancel changes on the template where template_name equals 'Thank You' and name equals 'Thank You' (mentioned template_name twice).
    Incorrect: Cancel template where body equals 'Hi , thank you!' (placeholder removed - WRONG!).
""".strip()

TEMPLATE_CANCELED_USE_CASE = UseCase(
    name="TEMPLATE_CANCELED",
    description="The user cancels working on a template and resets changes.",
    event=TemplateCanceledEvent,
    event_source_code=TemplateCanceledEvent.get_source_code_of_class(),
    constraints_generator=generate_sent_template_constraints,
    additional_prompt_info=TEMPLATE_CANCELED_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Cancel changes on the template where template_name equals 'Thank You'.",
            "prompt_for_task_generation": "Cancel changes on the template where template_name equals 'Thank You'.",
        },
        {
            "prompt": "Cancel changes on the template where template_name equals 'Meeting Recap' and subject contains 'Recap'.",
            "prompt_for_task_generation": "Cancel changes on the template where template_name equals 'Meeting Recap' and subject contains 'Recap'.",
        },
        {
            "prompt": "Discard changes to the template where body equals 'Hi <name>, looking forward to our meeting!'.",
            "prompt_for_task_generation": "Discard changes to the template where body equals 'Hi <name>, looking forward to our meeting!'.",
        },
    ],
)

###############################################################################
# FINAL LIST: ALL_USE_CASES
###############################################################################
ALL_USE_CASES = [
    SEARCH_EMAIL_USE_CASE,
    CLEAR_SELECTION_USE_CASE,
    EMAILS_NEXT_PAGE_USE_CASE,
    EMAILS_PREV_PAGE_USE_CASE,
    VIEW_TEMPLATES_USE_CASE,
    TEMPLATE_SELECTED_USE_CASE,
    TEMPLATE_BODY_EDITED_USE_CASE,
    TEMPLATE_SENT_USE_CASE,
    TEMPLATE_SAVED_DRAFT_USE_CASE,
    TEMPLATE_CANCELED_USE_CASE,
    VIEW_EMAIL_USE_CASE,
    ARCHIVE_EMAIL_USE_CASE,
    STAR_EMAIL_USE_CASE,
    MARK_EMAIL_AS_IMPORTANT_USE_CASE,
    MARK_AS_UNREAD_USE_CASE,
    DELETE_EMAIL_USE_CASE,
    MARK_AS_SPAM_USE_CASE,
    ADD_LABEL_USE_CASE,
    CREATE_LABEL_USE_CASE,
    SEND_EMAIL_USE_CASE,
    EMAIL_SAVE_AS_DRAFT_USE_CASE,
    EDIT_DRAFT_EMAIL_USE_CASE,
    REPLY_EMAIL_USE_CASE,
    FORWARD_EMAIL_USE_CASE,
    THEME_CHANGED_USE_CASE,
]
