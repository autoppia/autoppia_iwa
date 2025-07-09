from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import ViewEmailEvent
from .replace_functions import replace_email_placeholders

VIEW_EMAIL_USE_CASE = UseCase(
    name="VIEW_EMAIL",
    description="The user selects an email to open and read its contents.",
    event=ViewEmailEvent,
    event_source_code=ViewEmailEvent.get_source_code_of_class(),
    replace_func=replace_email_placeholders,
    additional_prompt_info="You are viewing an email with a specific subject, sender, or ID.",
    examples=[
        {
            "prompt": "Open the email from <from_email> with subject '<subject>'",
            "prompt_for_task_generation": "Open the email from <from_email> with subject '<subject>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_EMAIL",
                "event_criteria": {"subject": {"value": "<subject>", "operator": "equals"}, "from_email": {"value": "<from_email>", "operator": "equals"}},
                "reasoning": "Validates that the user viewed the correct email based on sender and subject.",
            },
        },
        {
            "prompt": "View the message from <from_email>",
            "prompt_for_task_generation": "View the message from <from_email>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_EMAIL",
                "event_criteria": {"from_email": {"value": "<from_email>", "operator": "equals"}},
                "reasoning": "Validates the user opened an email sent by a specific user.",
            },
        },
        {
            "prompt": "Read the email with subject '<subject>'",
            "prompt_for_task_generation": "Read the email with subject '<subject>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_EMAIL",
                "event_criteria": {"subject": {"value": "<subject>", "operator": "equals"}},
                "reasoning": "Applies when the task involves opening an email based on its subject.",
            },
        },
        {
            "prompt": "Access the email with ID <email_id>",
            "prompt_for_task_generation": "Access the email with ID <email_id>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_EMAIL",
                "event_criteria": {"email_id": {"value": "<email_id>", "operator": "equals"}},
                "reasoning": "Used when the email is uniquely identified by its ID.",
            },
        },
    ],
)


###############################################################################
# FINAL LIST: ALL_USE_CASES
###############################################################################
ALL_USE_CASES = [VIEW_EMAIL_USE_CASE]
