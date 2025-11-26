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
    DocumentUploaded,
    FilterMatterStatus,
    LogDelete,
    LogEdited,
    NewCalendarEventAdded,
    NewLogAdded,
    SearchClient,
    SearchMatter,
    SortMatterByCreatedAt,
    UpdateMatter,
    ViewClientDetails,
    ViewMatterDetails,
    ViewPendingEvents,
)
from .generation_functions import (
    generate_add_matter_constraints,
    generate_change_user_name_constraints,
    generate_delete_log_constraints,
    generate_document_deleted_constraints,
    generate_document_uploaded_constraints,
    generate_filter_matter_status_constraints,
    generate_new_calendar_event_constraints,
    generate_new_log_added_constraints,
    generate_search_client_constraints,
    generate_search_matter_constraints,
    generate_sort_matter_constraints,
    generate_update_matter_constraints,
    generate_view_client_constraints,
    generate_view_matter_constraints,
    generate_view_pending_events_constraints,
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
# SEARCH_MATTER_USE_CASE
###############################################################################
SEARCH_MATTER_USE_CASE = UseCase(
    name="SEARCH_MATTER",
    description="The user searches for matters using a query string.",
    event=SearchMatter,
    event_source_code=SearchMatter.get_source_code_of_class(),
    constraints_generator=generate_search_matter_constraints,
    examples=[
        {
            "prompt": "Search for matters that include 'Estate' in the title.",
            "prompt_for_task_generation": "Search for matters that include 'Estate' in the title.",
        },
        {
            "prompt": "Find matters whose name does NOT contain 'Archived'.",
            "prompt_for_task_generation": "Find matters whose name does NOT contain 'Archived'.",
        },
        {
            "prompt": "Search for matters where the name contains 'Review'.",
            "prompt_for_task_generation": "Search for matters where the name contains 'Review'.",
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
# FILTER_MATTER_STATUS_USE_CASE
###############################################################################
FILTER_MATTER_STATUS_USE_CASE = UseCase(
    name="FILTER_MATTER_STATUS",
    description="The user filters matters by status.",
    event=FilterMatterStatus,
    event_source_code=FilterMatterStatus.get_source_code_of_class(),
    constraints_generator=generate_filter_matter_status_constraints,
    examples=[
        {
            "prompt": "Filter matters to only show those with status 'Active'.",
            "prompt_for_task_generation": "Filter matters to only show those with status 'Active'.",
        },
        {
            "prompt": "Filter matters to exclude status 'Archived'.",
            "prompt_for_task_generation": "Filter matters to exclude status 'Archived'.",
        },
        {
            "prompt": "Show matters that are either 'Active' or 'On Hold'.",
            "prompt_for_task_generation": "Show matters that are either 'Active' or 'On Hold'.",
        },
    ],
)

###############################################################################
# SORT_MATTER_BY_CREATED_AT_USE_CASE
###############################################################################
SORT_MATTER_BY_CREATED_AT_USE_CASE = UseCase(
    name="SORT_MATTER_BY_CREATED_AT",
    description="The user sorts matters by created date.",
    event=SortMatterByCreatedAt,
    event_source_code=SortMatterByCreatedAt.get_source_code_of_class(),
    constraints_generator=generate_sort_matter_constraints,
    examples=[
        {
            "prompt": "Sort matters by newest first.",
            "prompt_for_task_generation": "Sort matters by newest first.",
        },
        {
            "prompt": "Sort matters so the oldest ones appear on top.",
            "prompt_for_task_generation": "Sort matters so the oldest ones appear on top.",
        },
    ],
)

###############################################################################
# UPDATE_MATTER_USE_CASE
###############################################################################
UPDATE_MATTER_USE_CASE = UseCase(
    name="UPDATE_MATTER",
    description="The user updates an existing matter.",
    event=UpdateMatter,
    event_source_code=UpdateMatter.get_source_code_of_class(),
    constraints_generator=generate_update_matter_constraints,
    examples=[
        {
            "prompt": "Edit the matter 'Estate Planning' to change status to 'On Hold'.",
            "prompt_for_task_generation": "Edit the matter 'Estate Planning' to change status to 'On Hold'.",
        },
        {
            "prompt": "Update the matter named 'Contract Review' so the client is 'Jones Legal'.",
            "prompt_for_task_generation": "Update the matter named 'Contract Review' so the client is 'Jones Legal'.",
        },
        {
            "prompt": "Update any matter whose updated date is not 'Today'.",
            "prompt_for_task_generation": "Update any matter whose updated date is not 'Today'.",
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
            "prompt_for_task_generation": "Search for clients named 'Smith'.",
        },
        {
            "prompt": "Find any clients whose name contains 'Brown'.",
            "prompt_for_task_generation": "Find any clients whose name contains 'Brown'.",
        },
        {
            "prompt": "Search for clients, excluding those matching 'Ventures'.",
            "prompt_for_task_generation": "Search for clients, excluding those matching 'Ventures'.",
        },
    ],
)

DOCUMENT_DELETED_EXTRA_INFO = """
Critical Requirements:
1. Make sure to mention **all** the constraints in the prompt accurately.
2. Do not specify more than one constraint for the same field — name, size, version, status, or updated — in a single request.
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
            "prompt": "Delete the document 'Patent-Application.pdf' if its status is 'Submitted'.",
            "prompt_for_task_generation": "Delete the document 'Patent-Application.pdf' if its status is 'Submitted'.",
        },
        {
            "prompt": "Delete the document with version equal to 'v3' and status equal to 'Submitted' and whose name does not contain 'Expert-Testimony.pdf' and whose size equals '1.4 MB'",
            "prompt_for_task_generation": "Delete the document with version equal to 'v3' and status equal to 'Submitted' and whose name does not contain 'Expert-Testimony.pdf' and whose size equals '1.4 MB'",
        },
        {
            "prompt": "Delete the document with status equal to 'Submitted' and version equal to 'v5' and size less than or equal to '843 KB'.",
            "prompt_for_task_generation": "Delete the document with status equal to 'Submitted' and version equal to 'v5' and size less than or equal to '843 KB'.",
        },
        {
            "prompt": "Delete the document whose name does NOT contain 'Litigation-Plan.pdf' and whose size is equal to '98 KB' and whose version is NOT equal to 'v2'",
            "prompt_for_task_generation": "Delete the document whose name does NOT contain 'Litigation-Plan.pdf' and whose size is equal to '98 KB' and whose version is NOT equal to 'v2'",
        },
    ],
)

###############################################################################
# DOCUMENT_UPLOADED_USE_CASE
###############################################################################
DOCUMENT_UPLOADED_USE_CASE = UseCase(
    name="DOCUMENT_UPLOADED",
    description="The user uploads a new document.",
    event=DocumentUploaded,
    event_source_code=DocumentUploaded.get_source_code_of_class(),
    constraints_generator=generate_document_uploaded_constraints,
    examples=[
        {
            "prompt": "Upload a document named 'Retainer-Agreement.pdf'.",
            "prompt_for_task_generation": "Upload a document named 'Retainer-Agreement.pdf'.",
        },
        {
            "prompt": "Upload a file 'Patent-Application.pdf' with version 'v1'.",
            "prompt_for_task_generation": "Upload a file 'Patent-Application.pdf' with version 'v1'.",
        },
        {
            "prompt": "Upload a document whose size is around '100 KB' and status 'Draft'.",
            "prompt_for_task_generation": "Upload a document whose size is around '100 KB' and status 'Draft'.",
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

###############################################################################
# VIEW_PENDING_EVENTS_USE_CASE
###############################################################################
VIEW_PENDING_EVENTS_USE_CASE = UseCase(
    name="VIEW_PENDING_EVENTS",
    description="The user views pending calendar events.",
    event=ViewPendingEvents,
    event_source_code=ViewPendingEvents.get_source_code_of_class(),
    constraints_generator=generate_view_pending_events_constraints,
    examples=[
        {
            "prompt": "Open the pending events list on the calendar page.",
            "prompt_for_task_generation": "Open the pending events list on the calendar page.",
        },
        {
            "prompt": "Show pending events and note the earliest upcoming date.",
            "prompt_for_task_generation": "Show pending events and note the earliest upcoming date.",
        },
        {
            "prompt": "View pending events and report how many upcoming events there are.",
            "prompt_for_task_generation": "View pending events and report how many upcoming events there are.",
        },
    ],
)

ADD_NEW_LOG_EXTRA_INFO = """
Critical Requirements:
!. Must mention all the constraints in the prompt accurately.
2. Do not specify more than one constraint for the same field — matter, description, or hours — in a single request.
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
            "prompt": "Add a time log with matter 'Trademark Filing', description 'Prepare documents', and hours '2.5'.",
            "prompt_for_task_generation": "Add a time log with matter 'Trademark Filing', description 'Prepare documents', and hours '2.5'.",
        },
        {
            "prompt": "Add a time log with matter 'M&A Advice', description 'Negotiation call', and hours '3'.",
            "prompt_for_task_generation": "Add a time log with matter 'M&A Advice', description 'Negotiation call', and hours '3'.",
        },
        {
            "prompt": "Create a new time log with matter 'Startup Incorporation', description 'Setup docs', and hours greater than '3'.",
            "prompt_for_task_generation": "Create a new time log with matter 'Startup Incorporation', description 'Setup docs', and hours greater than '3'.",
        },
        {
            "prompt": "Add a time log with matter 'Tax Advisory', description 'Tax analysis', and hours not equal to '2.5'.",
            "prompt_for_task_generation": "Add a time log with matter 'Tax Advisory', description 'Tax analysis', and hours not equal to '2.5'.",
        },
        {
            "prompt": "Create a time log with matter 'Trademark Renewal', description 'Online filing', and hours less than '1'.",
            "prompt_for_task_generation": "Create a time log with matter 'Trademark Renewal', description 'Online filing', and hours less than '1'.",
        },
    ],
)

LOG_EDITED_EXTRA_INFO = """
Critical Requirements:
1. Use at most one constraint per field: matter, description, hours, client, or status.
""".strip()

###############################################################################
# LOG_EDITED_USE_CASE
###############################################################################
LOG_EDITED_USE_CASE = UseCase(
    name="LOG_EDITED",
    description="The user edits an existing time log entry.",
    event=LogEdited,
    event_source_code=LogEdited.get_source_code_of_class(),
    constraints_generator=generate_log_edited_constraints,
    additional_prompt_info=LOG_EDITED_EXTRA_INFO,
    examples=[
        {
            "prompt": "Edit the time log for 'Estate Planning' to change hours to 2.5.",
            "prompt_for_task_generation": "Edit the time log for 'Estate Planning' to change hours to 2.5.",
        },
        {
            "prompt": "Update the description of the log for 'Trademark Filing' to 'Prepare documents'.",
            "prompt_for_task_generation": "Update the description of the log for 'Trademark Filing' to 'Prepare documents'.",
        },
        {
            "prompt": "Edit any time log so its status becomes 'Billed'.",
            "prompt_for_task_generation": "Edit any time log so its status becomes 'Billed'.",
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
    SEARCH_MATTER_USE_CASE,
    FILTER_MATTER_STATUS_USE_CASE,
    SORT_MATTER_BY_CREATED_AT_USE_CASE,
    UPDATE_MATTER_USE_CASE,
    DELETE_MATTER_USE_CASE,
    ARCHIVE_MATTER_USE_CASE,
    VIEW_CLIENT_DETAILS_USE_CASE,
    SEARCH_CLIENT_USE_CASE,
    DOCUMENT_DELETED_USE_CASE,
    DOCUMENT_UPLOADED_USE_CASE,
    NEW_CALENDAR_EVENT_ADDED_USE_CASE,
    VIEW_PENDING_EVENTS_USE_CASE,
    NEW_LOG_ADDED_USE_CASE,
    LOG_EDITED_USE_CASE,
    LOG_DELETE_USE_CASE,
    CHANGE_USER_NAME_USE_CASE,
]
