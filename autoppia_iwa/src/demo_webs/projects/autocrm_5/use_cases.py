# -----------------------------------------------------------------------------
# use_cases.py
# -----------------------------------------------------------------------------
from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    AddNewMatter,
    ArchiveMatter,
    ChangeUserName,
    DeleteMatter,
    DocumentDeleted,
    LogDelete,
    NewCalendarEventAdded,
    NewLogAdded,
    SearchClient,
    ViewClientDetails,
    ViewMatterDetails,
)
from .generation_functions import (
    generate_add_matter_constraints,
    generate_change_user_name_constraints,
    generate_delete_log_constraints,
    generate_document_deleted_constraints,
    generate_new_calendar_event_constraints,
    generate_new_log_added_constraints,
    generate_search_client_constraints,
    generate_view_client_constraints,
    generate_view_matter_constraints,
)

###############################################################################
# VIEW_USE_CASE
###############################################################################


VIEW_MATTER_USE_CASE = UseCase(
    name="VIEW_MATTER_DETAILS",
    description="The user views the detail of different matters",
    event=ViewMatterDetails,
    event_source_code=ViewMatterDetails.get_source_code_of_class(),
    constraints_generator=generate_view_matter_constraints,
    examples=[
        {
            "prompt": "Go to the Matters page and click on 'Estate Planning' to view the details of that particular matter",
            "prompt_for_task_generation": "Go to the Matters page and click on 'Estate Planning' to view the details of that particular matter",
        },
        {
            "prompt": "View details of the matter whose client name is 'Jones Legal'",
            "prompt_for_task_generation": "View details of the matter whose client name is 'Jones Legal'",
        },
        {
            "prompt": "View matter details if its updated date is not 'Today'",
            "prompt_for_task_generation": "View matter details if its updated date is not 'Today'",
        },
        {
            "prompt": "View those matters for which the status is 'Active'",
            "prompt_for_task_generation": "View those matters for which the status is 'Active'",
        },
        {
            "prompt": "View matter details for any of the following statuses: 'Active', 'On Hold'",
            "prompt_for_task_generation": "View matter details for any of the following statuses: 'Active', 'On Hold'",
        },
        {
            "prompt": "View matter details excluding matters with status 'Archived' or 'On Hold'",
            "prompt_for_task_generation": "View matter details excluding matters with status 'Archived' or 'On Hold'",
        },
    ],
)

###############################################################################
# ADD_USE_CASE
###############################################################################
ADD_NEW_MATTER_EXTRA_INFO = """
Critical Requirements:
1. Do not specify more than one constraint for the same field — name, status, or client — in a single request.

✔️ CORRECT: Create a matter with the name 'New Matter', with client 'John Doe', and status that is NOT in the list ['Archived'].
✔️ CORRECT: Create a matter with the name that is NOT 'Acquisition Deal', with client 'John Doe', and status that is NOT in the list ['Archived'].
✔️ CORRECT: Create a matter with the name that is NOT 'Acquisition Deal', status that is NOT in the list ['Archived'], and client that does NOT contain 'Client'.
❌ INCORRECT: Create a matter with the name 'New Matter' that is NOT 'Acquisition Deal', with client 'John Doe', and status that is NOT in the list ['Archived'], and where the client does NOT contain 'Confidential Client'. (Multiple constraints for the same fields)
""".strip()

ADD_NEW_MATTER_USE_CASE = UseCase(
    name="ADD_NEW_MATTER",
    description="The user adds a new matter, specifying details such as matter name, client name and status of matter",
    event=AddNewMatter,
    event_source_code=AddNewMatter.get_source_code_of_class(),
    constraints_generator=generate_add_matter_constraints,
    additional_prompt_info=ADD_NEW_MATTER_EXTRA_INFO,
    examples=[
        {
            "prompt": "Create a matter named 'New Matter', with client 'Acme Co.' and status 'Active'.",
            "prompt_for_task_generation": "Create a matter named 'New Matter', with client 'Acme Co.' and status 'Active'.",
        },
        {
            "prompt": "Create a matter with the name that contains 'Alpha', client 'Robert Miles', and status NOT 'Archived'.",
            "prompt_for_task_generation": "Create a matter with the name 'Case Alpha', client 'Robert Miles', and status 'Archived'.",
        },
        {
            "prompt": "Add a new matter where the name is not 'Employment Agreement' and the client is 'Delta Partners'.",
            "prompt_for_task_generation": "Add a new matter where the name is not 'Employment Agreement' and the client is 'Delta Partners'.",
        },
    ],
)


ARCHIVE_MATTER_USE_CASE = UseCase(
    name="ARCHIVE_MATTER",
    description="The user archives a matter",
    event=ArchiveMatter,
    event_source_code=ArchiveMatter.get_source_code_of_class(),
    constraints_generator=generate_view_matter_constraints,
    examples=[
        {
            "prompt": "Archive the matter whose status is set to 'Active'",
            "prompt_for_task_generation": "Archive the matter whose status is set to 'Active'",
        },
        {
            "prompt": "Archive the matter where status is set to either 'Active' or 'On Hold'",
            "prompt_for_task_generation": "Archive the matter where status is set to either 'Active' or 'On Hold'",
        },
        {
            "prompt": "Archive the 'Estate Planning' matter if it was not updated 'Today'",
            "prompt_for_task_generation": "Archive the 'Estate Planning' matter if it was not updated 'Today'",
        },
        {
            "prompt": "Archive the matter where matter name is 'Contract Review' and the client name is 'Jones Legal'",
            "prompt_for_task_generation": "Archive the matter where matter name is 'Contract Review' or the client name is 'Jones Legal'",
        },
        {
            "prompt": "Archive the matter titled 'Real Estate Purchase' if the client is not 'Mohammed Anwar'",
            "prompt_for_task_generation": "Archive the matter titled 'Real Estate Purchase' if the client is not 'Mohammed Anwar'",
        },
    ],
)

DELETE_MATTER_USE_CASE = UseCase(
    name="DELETE_MATTER",
    description="The user deletes a matter",
    event=DeleteMatter,
    event_source_code=DeleteMatter.get_source_code_of_class(),
    constraints_generator=generate_view_matter_constraints,
    examples=[
        {
            "prompt": "Delete the matter whose status is set to 'Active'",
            "prompt_for_task_generation": "Delete the matter whose status is set to 'Active'",
        },
        {
            "prompt": "Delete the matter where status is set to 'Active' and 'On Hold'",
            "prompt_for_task_generation": "Delete the matter where status is set to 'Active' and 'On Hold'",
        },
        {
            "prompt": "Delete the 'Estate Planning' matter if it was not updated 'Today'",
            "prompt_for_task_generation": "Delete the 'Estate Planning' matter if it was not updated 'Today'",
        },
        {
            "prompt": "Delete the matter where matter name is 'Contract Review' and the client name is 'Jones Legal'",
            "prompt_for_task_generation": "Delete the matter where matter name is 'Contract Review' and the client name is 'Jones Legal'",
        },
        {
            "prompt": "Delete the matter where status is set to 'Archived'",
            "prompt_for_task_generation": "Delete the matter where status is set to 'Archived'",
        },
        {
            "prompt": "Delete the matter titled 'IP Litigation' if its client is not 'Zara Sheikh'",
            "prompt_for_task_generation": "Delete the matter titled 'IP Litigation' if its client is not 'Zara Sheikh'",
        },
    ],
)
###############################################################################
# VIEW_CLIENT_DETAILS_USE_CASE
###############################################################################
VIEW_CLIENT_DETAILS_USE_CASE = UseCase(
    name="VIEW_CLIENT_DETAILS",
    description="The user views the detail of different clients",
    event=ViewClientDetails,
    event_source_code=ViewClientDetails.get_source_code_of_class(),
    constraints_generator=generate_view_client_constraints,
    examples=[
        {
            "prompt": "View details of client, whose client name is 'jessica brown' and email is 'jbrown@samplemail.com'",
            "prompt_for_task_generation": "View details of client, whose client name is 'jessica brown' and email is 'jbrown@samplemail.com'",
        },
        {
            "prompt": "View client details if its status is 'active', its email is 'team@smithco.com' and matters are not '3'",
            "prompt_for_task_generation": "View client details if its status is 'active', its email is 'team@smithco.com' and matters are not '3'",
        },
    ],
)


###############################################################################
# SEARCH_CLIENT_USE_CASE
###############################################################################
SEARCH_CLIENT_USE_CASE = UseCase(
    name="SEARCH_CLIENT",
    description="The user searches for clients using a query string.",
    event=SearchClient,
    event_source_code=SearchClient.get_source_code_of_class(),
    constraints_generator=generate_search_client_constraints,
    examples=[
        {
            "prompt": "Search for clients named 'Smith'.",
            "prompt_for_task_generation": "Search for clients named <query>.",
        },
        {
            "prompt": "Find any clients whose name contains 'Brown'.",
            "prompt_for_task_generation": "Find any clients whose name contains <query_part>.",
        },
        {
            "prompt": "Search for clients, excluding those matching 'Ventures'.",
            "prompt_for_task_generation": "Search for clients, excluding those matching <query>.",
        },
    ],
)

DOCUMENT_DELETED_EXTRA_INFO = """
Critical Requirements:
1. Mention all the constraint in the prompt accurately.
2. Do not specify more than one constraint for the same field — name, size, version, status, or updated — in a single request.

✔️ CORRECT: Delete the document named 'Retainer-Agreement.pdf'.
✔️ CORRECT: Remove the document whose status is 'Draft' and whose name contains 'Proposal'.
✔️ CORRECT: Delete the document if its version is not 'v1.0' and its size is greater than '100 KB'.
❌ INCORRECT: Delete the document named 'Patent-Application.pdf' and also where the name contains 'Application'. (Multiple constraints for the same field: name)
❌ INCORRECT: Remove any document with size greater than '100 KB' and size less than '1 MB'. (Multiple constraints for the same field: size)
""".strip()

###############################################################################
# DOCUMENT_DELETED_USE_CASE
###############################################################################
DOCUMENT_DELETED_USE_CASE = UseCase(
    name="DOCUMENT_DELETED",
    description="The user deletes an existing document.",
    event=DocumentDeleted,
    event_source_code=DocumentDeleted.get_source_code_of_class(),
    constraints_generator=generate_document_deleted_constraints,
    additional_prompt_info=DOCUMENT_DELETED_EXTRA_INFO,
    examples=[
        {
            "prompt": "Delete the document named 'Retainer-Agreement.pdf'.",
            "prompt_for_task_generation": "Delete the document named 'Retainer-Agreement.pdf'.",
        },
        {
            "prompt": "Remove any document that is marked as 'Draft'.",
            "prompt_for_task_generation": "Remove any document that is marked as 'Draft'.",
        },
        {
            "prompt": "Delete the document 'Patent-Application.pdf' if its status is 'Submitted'.",
            "prompt_for_task_generation": "Delete the document '<document_name>' if its status is 'Submitted'.",
        },
    ],
)
NEW_CALENDER_EVENT_EXTRA_INFO = """
Critical Requirements:
1. Do not specify more than one constraint for the same field — label, time, date, or event_type — in a single request.

✔️ CORRECT: Add a new calendar event on '2025-05-13' at '9:00am' called 'Team Sync' with an event type 'Filing'.
✔️ CORRECT: Schedule an event with label that CONTAINS 'Review' at time '2:30pm' and type that is NOT 'Other'.
✔️ CORRECT: Create a calendar event on a date that is GREATER THAN '2025-05-10' with time that is LESS THAN '3:00pm' and event type 'Internal'.
❌ INCORRECT: Add a new calendar event on '2025-05-12' at '4:00pm' called 'Project Update' with an event type that CONTAINS 'Internal' and is NOT equal to 'Marketing Campaign Review', scheduled for a date that is GREATER THAN or EQUAL to '2025-05-10' and a time that is GREATER THAN or EQUAL to '3:00pm'. (Multiple constraints for the same fields)
""".strip()


###############################################################################
# NEW_CALENDAR_EVENT_ADDED_USE_CASE
###############################################################################
NEW_CALENDAR_EVENT_ADDED_USE_CASE = UseCase(
    name="NEW_CALENDAR_EVENT_ADDED",
    description="The user adds a new event to the calendar.",
    event=NewCalendarEventAdded,
    event_source_code=NewCalendarEventAdded.get_source_code_of_class(),
    constraints_generator=generate_new_calendar_event_constraints,
    additional_prompt_info=NEW_CALENDER_EVENT_EXTRA_INFO,
    examples=[
        {
            "prompt": "Add a new calendar event on 2025-05-13 at 9:00am called 'Team Sync' with a Filing type.",
            "prompt_for_task_generation": "Add a new calendar event on 2025-05-13 at 9:00am called 'Team Sync' with a Filing type.",
        },
        {
            "prompt": "Schedule an Internal event on 2025-05-07 at 2:30pm titled 'Internal Review'.",
            "prompt_for_task_generation": "Schedule an Internal event on 2025-05-07 at 2:30pm titled 'Internal Review'.",
        },
        {
            "prompt": "Create a calendar event on 2025-05-22 named 'Staff Meeting' with a Matter/Event color.",
            "prompt_for_task_generation": "Create a calendar event on 2025-05-22 named 'Staff Meeting' with a Matter/Event color.",
        },
    ],
)

ADD_NEW_LOG_EXTRA_INFO = """
Critical Requirements:
1. Do not specify more than one constraint for the same field — matter, description, or hours — in a single request.

✔️ CORRECT: Add a time log for 'Trademark Filing' with hours NOT EQUAL to '2.5' and a description that is NOT 'Negotiation call'.
✔️ CORRECT: Add a time log for 'Trademark Filing' with a description that is NOT 'Negotiation call' while ensuring the total hours are less than or equal to '4.5'.
❌ INCORRECT: Add a time log for 'Trademark Filing' with hours NOT EQUAL to '2.5' and a description that is NOT 'Negotiation call' while ensuring the total hours are less than or equal to '4.5'.
""".strip()

###############################################################################
# NEW_LOG_ADDED_USE_CASE
###############################################################################
NEW_LOG_ADDED_USE_CASE = UseCase(
    name="NEW_LOG_ADDED",
    description="The user adds a new time log entry.",
    event=NewLogAdded,
    event_source_code=NewLogAdded.get_source_code_of_class(),
    constraints_generator=generate_new_log_added_constraints,
    additional_prompt_info=ADD_NEW_LOG_EXTRA_INFO,
    examples=[
        {
            "prompt": "Add a time log for 'Trademark Filing' with 2.5 hours for 'Prepare documents'.",
            "prompt_for_task_generation": "Add a time log for 'Trademark Filing' with '2.5' hours for 'Prepare documents'.",
        },
        {
            "prompt": "Log 3 hours for 'M&A Advice' to record 'Negotiation call'.",
            "prompt_for_task_generation": "Log 3 hours for 'M&A Advice' to record 'Negotiation call'.",
        },
        {
            "prompt": "Create a new log for 'Startup Incorporation' with more than 3 hours for 'Setup docs'.",
            "prompt_for_task_generation": "Create a new log for 'Startup Incorporation' with more than '3' hours for 'Setup docs'.",
        },
        {
            "prompt": "Log time for 'Tax Advisory' but make sure the hours are not 2.5, use 'Tax analysis' as description.",
            "prompt_for_task_generation": "Log time for 'Tax Advisory' with hours not equal to '2.5' and description 'Tax analysis'.",
        },
        {
            "prompt": "Create a log for 'Trademark Renewal' for less than 1 hour, describing it as 'Online filing'.",
            "prompt_for_task_generation": "Create a log for 'Trademark Renewal' with less than '1' hour and description 'Online filing'.",
        },
    ],
)


LOG_DELETE_EXTRA_INFO = """
Critical Requirements:
1. Use at most one constraint per field: `matter`, `description`, or `hours`.
2. Mirror the constraint operator and the value exactly in the generated prompt. Do not paraphrase operators (e.g. use the specified negation).

Example constraint (Python dict):
constraint: {'matter': {'operator': 'not_equals', 'value': 'Court Filing'}, 'hours': {'operator': 'not_equals', 'value': 2.3}, 'client': {'operator': 'not_contains', 'value': 'CoreConnect'}, 'status': {'operator': 'in_list', 'value': ['Billed', 'Billable']}}

Prompts:
✔️ CORRECT: Delete the time log where matter is NOT equal to 'Court Filing', hours is NOT equal to 2.3, client does NOT CONTAIN 'CoreConnect', and status is in the list ['Billed', 'Billable'].
❌ INCORRECT: Delete the time log for 'Court Filing' that recorded hours NOT EQUAL to 2.3, where the client does NOT CONTAIN 'CoreConnect' and the status is in the list ['Billed', 'Billable'].

Explanation: The incorrect prompt does not reflect the specified operator for `matter` (`not_equals`) — it uses a positive equality instead of the required negation. Use the exact operators and value formats shown in the constraint.
""".strip()

###############################################################################
# LOG_DELETE_USE_CASE
###############################################################################
LOG_DELETE_USE_CASE = UseCase(
    name="LOG_DELETE",
    description="The user deletes an existing time log entry.",
    event=LogDelete,
    event_source_code=LogDelete.get_source_code_of_class(),
    constraints_generator=generate_delete_log_constraints,
    additional_prompt_info=LOG_DELETE_EXTRA_INFO,
    examples=[
        {
            "prompt": "Delete the time log for 'Estate Planning' that recorded 2 hours.",
            "prompt_for_task_generation": "Delete the time log for 'Estate Planning' that recorded 2 hours.",
        },
        {
            "prompt": "Remove any time log that is currently 'Billed'.",
            "prompt_for_task_generation": "Remove any time log that is currently 'Billed'.",
        },
        {
            "prompt": "Delete time logs for 'Peak Ventures' with 3 hours and 'Billable' status.",
            "prompt_for_task_generation": "Delete time logs for 'Peak Ventures' with 3 hours and 'Billable' status.",
        },
        {
            "prompt": "Delete any log where hours are not equal to 2.5.",
            "prompt_for_task_generation": "Delete any log where hours are not equal to 2.5.",
        },
        {
            "prompt": "Delete all logs where the description contains 'memo'.",
            "prompt_for_task_generation": "Delete all logs where the description contains 'memo'.",
        },
        {
            "prompt": "Delete logs where the hours are greater than 4.",
            "prompt_for_task_generation": "Delete logs where the hours are greater than 4.",
        },
        {
            "prompt": "Delete time logs with less than 1.5 hours for 'LabelLine'.",
            "prompt_for_task_generation": "Delete time logs with less than 1.5 hours for 'LabelLine'.",
        },
        {
            "prompt": "Remove time logs for the matter 'Startup Pitch Deck' where the client is not 'LaunchLeap'.",
            "prompt_for_task_generation": "Remove time logs for the matter 'Startup Pitch Deck' where the client is not 'LaunchLeap'.",
        },
    ],
)

CHANGE_USER_NAME_EXTRA_INFO = """
Critical Requirements:
1. Do not specify more than one constraint for the same field — 'name' — in a single request.

Examples:
- CORRECT: "Change my user name to 'Muhammad Ali'"
- INCORRECT: "Change my user name to 'Muhammad Ali' that does NOT contain 'Doe'"
- CORRECT: "Change my user name to 'Emily Rose'"
- CORRECT: "Change my user name that does NOT contain 'Evans'"
- INCORRECT: "Change my user name to 'Emily Rose' that does NOT contain 'Evans'"
""".strip()

###############################################################################
# CHANGE_USER_NAME_USE_CASE
###############################################################################
CHANGE_USER_NAME_USE_CASE = UseCase(
    name="CHANGE_USER_NAME",
    description="The user changes their name in the application.",
    event=ChangeUserName,
    event_source_code=ChangeUserName.get_source_code_of_class(),
    constraints_generator=generate_change_user_name_constraints,
    additional_prompt_info=CHANGE_USER_NAME_EXTRA_INFO,
    examples=[
        {
            "prompt": "Change my user name to 'Muhammad Ali'.",
            "prompt_for_task_generation": "Change my user name to 'Muhammad Ali'.",
        },
        {
            "prompt": "Update my display name to 'Aisha Khan'.",
            "prompt_for_task_generation": "Update my display name to 'Aisha Khan'.",
        },
        {
            "prompt": "Set my user name to something that is not 'Guest User'.",
            "prompt_for_task_generation": "Set my user name to something that is not 'Guest User'.",
        },
    ],
)
###############################################################################
# FINAL LIST: ALL_USE_CASES
###############################################################################
ALL_USE_CASES = [
    ADD_NEW_MATTER_USE_CASE,
    VIEW_MATTER_USE_CASE,
    DELETE_MATTER_USE_CASE,
    ARCHIVE_MATTER_USE_CASE,
    VIEW_CLIENT_DETAILS_USE_CASE,
    SEARCH_CLIENT_USE_CASE,
    DOCUMENT_DELETED_USE_CASE,
    NEW_CALENDAR_EVENT_ADDED_USE_CASE,
    NEW_LOG_ADDED_USE_CASE,
    LOG_DELETE_USE_CASE,
    CHANGE_USER_NAME_USE_CASE,
]
