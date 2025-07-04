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
    LogDelete,
    NewCalendarEventAdded,
    NewLogAdded,
    SearchClient,
    ViewClientDetails,
    ViewMatterDetails,
)
from .generation_functions import generate_add_matter_constraints, generate_view_matter_constraints
from .replace_functions import replace_placeholders

###############################################################################
# VIEW_USE_CASE
###############################################################################


VIEW_MATTER_USE_CASE = UseCase(
    name="VIEW_MATTER_USE_CASE",
    description="The user views the detail of different matters",
    event=ViewMatterDetails,
    event_source_code=ViewMatterDetails.get_source_code_of_class(),
    constraints_generator=generate_view_matter_constraints,
    examples=[
        {
            "prompt": "Go to the Matters page and click on 'Estate Planning' to view the details of that particular matter",
            "prompt_for_task_generation": "Go to the Matters page and click on <mattername> to view the details of that particular matter",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_MATTER_DETAILS",
                "event_criteria": {"name": {"value": "Estate Planning"}},
                "reasoning": "This test applies when the task requires to view the detail of a matter whose name is 'Estate Planning'",
            },
        },
        {
            "prompt": "View details of matter, whose client name is 'Jones Legal'",
            "prompt_for_task_generation": "View details of matter, whose client name is 'Jones Legal'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_MATTER_DETAILS",
                "event_criteria": {"client": {"value": "Jones Legal"}},
                "reasoning": "This test applies when the task requires to view the detail of a matter whose client name is 'Jones Legal'",
            },
        },
        {
            "prompt": "View matter details if its status is not updated Today",
            "prompt_for_task_generation": "View matter details if its status is not updated <status>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_MATTER_DETAILS",
                "event_criteria": {"updated": {"value": "Today", "operator": "not_equals"}},
                "reasoning": "This test applies when the task is to view matter details if its status is not updated Today",
            },
        },
        {
            "prompt": "view those matters for which the status is active",
            "prompt_for_task_generation": "view those matters for which the status is <status>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_MATTER_DETAILS",
                "event_criteria": {"status": {"value": "active"}},
                "reasoning": "This test applies when the task requires to view those matters for which the status is 'active'",
            },
        },
    ],
)

###############################################################################
# ADD_USE_CASE
###############################################################################


ADD_NEW_MATTER_USE_CASE = UseCase(
    name="ADD_NEW_MATTER_USE_CASE",
    description="The user adds a new matter, specifying details such as matter name, client name and status of matter",
    event=AddNewMatter,
    event_source_code=AddNewMatter.get_source_code_of_class(),
    constraints_generator=generate_add_matter_constraints,
    replace_func=replace_placeholders,
    examples=[
        {
            "prompt": "Click on 'New Matter' button to create new matter, add 'new', 'emma' and 'active'",
            "prompt_for_task_generation": "Click on 'New Matter' button to create new matter, add <mattername>, <clientname> and <status>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_NEW_MATTER",
                "event_criteria": {"name": {"value": "new", "operator": "equals"}, "client": {"value": "emma", "operator": "equals"}, "status": {"value": "active", "operator": "equals"}},
                "reasoning": "This test applies when the task requires to add a new matter with matter name as 'new', client name as 'emma' and status set as 'active'",
            },
        },
        {
            "prompt": "Create a new matter with matter name as 'dummy', client name as 'anonymus' and status as 'archived'",
            "prompt_for_task_generation": "Create a new matter with matter name as <mattername>, client name as <clientname> and status as <status>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_NEW_MATTER",
                "event_criteria": {"name": {"value": "new", "operator": "equals"}, "client": {"value": "emma", "operator": "equals"}, "status": {"value": "archived", "operator": "equals"}},
                "reasoning": "This test applies when the task requires to add a new matter with matter name as 'new', client name as 'emma' and status set as 'active'",
            },
        },
        {
            "prompt": "Add matter where the matter name is not equal to 'IP Filing' and client is 'Services & Co.'",
            "prompt_for_task_generation": "Add matter where the matter name is not equal to <mattername> and client is <clientname>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_NEW_MATTER",
                "event_criteria": {"name": {"value": "IP Filing", "operator": "not_equals"}, "client": {"value": "Services & Co.", "operator": "equals"}},
                "reasoning": "This test applies when the task requires to add matter where the matter name is not equal to 'IP Filing' and client is 'Services $ Co.'",
            },
        },
    ],
)


ARCHIVE_MATTER_USE_CASE = UseCase(
    name="ARCHIVE_MATTER_USE_CASE",
    description="The user archives a matter",
    event=ArchiveMatter,
    event_source_code=ArchiveMatter.get_source_code_of_class(),
    constraints_generator=generate_view_matter_constraints,
    replace_func=replace_placeholders,
    examples=[
        {
            "prompt": "archive the matter whose status is set to 'active'",
            "prompt_for_task_generation": "archive the matter whose status is set to <status>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ARCHIVE_MATTER",
                "event_criteria": {"status": {"value": "active"}},
                "reasoning": "This test applies when the task requires to archive the matter where status is set to 'active'",
            },
        },
        {
            "prompt": "archive the matter where status is set to 'active' and 'on hold'",
            "prompt_for_task_generation": "archive the matter whose status is set to <status> and <status>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ARCHIVE_MATTER",
                "event_criteria": {"status": {"value": ["active", "on hold"], "operator": "in_list"}},
                "reasoning": "This test applies when the task requires to archive the matter where status is set to 'active' and 'on hold'",
            },
        },
        {
            "prompt": "archive the 'Estate Planning' matter and its not updated 'now'",
            "prompt_for_task_generation": "archive the <mattername> matter and its not updated <updated>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ARCHIVE_MATTER",
                "event_criteria": {"name": {"value": "Estate Planning", "operator": "equals"}, "updated": {"value": "now", "operator": "not_equals"}},
                "reasoning": "This test applies when the task requires to archive the matter where matter name is 'Estate Planning' and its not updated 'now'",
            },
        },
        {
            "prompt": "archive the matter where matter name is 'dummy' or the client name is 'Smith & Co.'",
            "prompt_for_task_generation": "archive the matter where matter name is <mattername> or the client name is '<clientname>'>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ARCHIVE_MATTER",
                "event_criteria": {"name": {"value": "dummy", "operator": "equals"}, "client": {"value": "Smith & Co.", "operator": "equals"}},
                "reasoning": "This test applies when the task requires to archive the matter where matter name is 'dummy' or the client name is 'Smith & Co.'",
            },
        },
    ],
)

DELETE_MATTER_USE_CASE = UseCase(
    name="ARCHIVE_MATTER_USE_CASE",
    description="The user archives a matter",
    event=DeleteMatter,
    event_source_code=DeleteMatter.get_source_code_of_class(),
    constraints_generator=generate_view_matter_constraints,
    replace_func=replace_placeholders,
    examples=[
        {
            "prompt": "Delete the matter whose status is set to 'active'",
            "prompt_for_task_generation": "Delete the matter whose status is set to <status>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_MATTER",
                "event_criteria": {"status": {"value": "active"}},
                "reasoning": "This test applies when the task requires to delete the matter where status is set to 'active'",
            },
        },
        {
            "prompt": "Delete the matter where status is set to 'active' and 'on hold'",
            "prompt_for_task_generation": "Delete the matter whose status is set to <status> and <status>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_MATTER",
                "event_criteria": {"status": {"value": ["active", "on hold"], "operator": "in_list"}},
                "reasoning": "This test applies when the task requires to delete the matter where status is set to 'active' and 'on hold'",
            },
        },
        {
            "prompt": "Delete the 'Estate Planning' matter and its not updated 'now'",
            "prompt_for_task_generation": "Delete the <mattername> matter and its not updated <updated>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_MATTER",
                "event_criteria": {"name": {"value": "Estate Planning", "operator": "equals"}, "updated": {"value": "now", "operator": "not_equals"}},
                "reasoning": "This test applies when the task requires to delete the matter where matter name is 'Estate Planning' and its not updated 'now'",
            },
        },
        {
            "prompt": "Delete the matter where matter name is 'dummy' or the client name is 'Smith & Co.'",
            "prompt_for_task_generation": "Delete the matter where matter name is <mattername> or the client name is '<clientname>'>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_MATTER",
                "event_criteria": {"name": {"value": "dummy", "operator": "equals"}, "client": {"value": "Smith & Co.", "operator": "equals"}},
                "reasoning": "This test applies when the task requires to delete the matter where matter name is 'dummy' or the client name is 'Smith & Co.'",
            },
        },
        {
            "prompt": "Delete the matter where status is set to 'archived'",
            "prompt_for_task_generation": "Delete the matter whose status is set to <status> and <status>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_MATTER",
                "event_criteria": {"status": {"value": "archived", "operator": "equals"}},
                "reasoning": "This test applies when the task requires to delete the matter where status is set to 'archived'",
            },
        },
    ],
)
###############################################################################
# VIEW_CLIENT_DETAILS_USE_CASE
###############################################################################
VIEW_CLIENT_DETAILS_USE_CASE = UseCase(
    name="VIEW_CLIENT_DETAILS_USE_CASE",
    description="The user views the details of different clients.",
    event=ViewClientDetails,
    event_source_code=ViewClientDetails.get_source_code_of_class(),
    # constraints_generator=default_constraints_generator,
    examples=[
        {
            "prompt": "Go to the Clients page and click on 'Smith & Co.' to view their details.",
            "prompt_for_task_generation": "Go to the Clients page and click on <client_name> to view their details.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_CLIENT_DETAILS",
                "event_criteria": {"name": {"value": "Smith & Co."}},
                "reasoning": "This test applies when the task requires viewing details of the client 'Smith & Co.'.",
            },
        },
        {
            "prompt": "View details of the client with email 'legal@acmebio.com'.",
            "prompt_for_task_generation": "View details of the client with email <client_email>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_CLIENT_DETAILS",
                "event_criteria": {"email": {"value": "legal@acmebio.com", "operator": "equals"}},
                "reasoning": "This test applies when the task requires viewing details of a client by their email 'legal@acmebio.com'.",
            },
        },
        {
            "prompt": "Show me the client who has 4 matters.",
            "prompt_for_task_generation": "Show me the client who has <number> matters.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_CLIENT_DETAILS",
                "event_criteria": {"matters": {"value": 4, "operator": "equals"}},
                "reasoning": "This test applies when the task requires viewing details of a client who has exactly 4 matters, like Peak Ventures.",
            },
        },
    ],
)


###############################################################################
# SEARCH_CLIENT_USE_CASE
###############################################################################
SEARCH_CLIENT_USE_CASE = UseCase(
    name="SEARCH_CLIENT_USE_CASE",
    description="The user searches for clients using a query string.",
    event=SearchClient,
    event_source_code=SearchClient.get_source_code_of_class(),
    # constraints_generator=default_constraints_generator,
    examples=[
        {
            "prompt": "Search for clients named 'Smith'.",
            "prompt_for_task_generation": "Search for clients named <query>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_CLIENT",
                "event_criteria": {"query": {"value": "Smith", "operator": "equals"}},
                "reasoning": "This test applies when the task requires searching for clients with a specific query string like 'Smith'.",
            },
        },
        {
            "prompt": "Find any clients whose name contains 'Brown'.",
            "prompt_for_task_generation": "Find any clients whose name contains <query_part>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_CLIENT",
                "event_criteria": {"query": {"value": "Brown", "operator": "contains"}},
                "reasoning": "This test applies when the task requires searching for clients whose name contains 'Brown', like Jessica Brown.",
            },
        },
        {
            "prompt": "Search for clients, excluding those matching 'Ventures'.",
            "prompt_for_task_generation": "Search for clients, excluding those matching <excluded_query>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_CLIENT",
                "event_criteria": {"query": {"value": "Ventures", "operator": "not_equals"}},
                "reasoning": "This test applies when the task requires searching for clients with a query that excludes 'Ventures'.",
            },
        },
    ],
)


###############################################################################
# DOCUMENT_UPLOADED_USE_CASE
###############################################################################
DOCUMENT_UPLOADED_USE_CASE = UseCase(
    name="DOCUMENT_UPLOADED_USE_CASE",
    description="The user uploads a new document.",
    event=DocumentUploaded,
    event_source_code=DocumentUploaded.get_source_code_of_class(),
    # constraints_generator=default_constraints_generator,
    examples=[
        {
            "prompt": "Upload a document named 'New-Contract.pdf'.",
            "prompt_for_task_generation": "Upload a document named <document_name>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DOCUMENT_UPLOADED",
                "event_criteria": {"name": {"value": "New-Contract.pdf", "operator": "equals"}},
                "reasoning": "This test applies when the task requires uploading a document with the name 'New-Contract.pdf'.",
            },
        },
        {
            "prompt": "Upload a document that is smaller than 100 KB and has a 'Draft' status.",
            "prompt_for_task_generation": "Upload a document that is smaller than <size> and has a <status> status.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DOCUMENT_UPLOADED",
                "event_criteria": {"size": {"value": "100 KB", "operator": "less_than"}, "status": {"value": "Draft", "operator": "equals"}},
                "reasoning": "This test applies when the task requires uploading a document that is less than 100KB and in 'Draft' status.",
            },
        },
        {
            "prompt": "Upload a document with a 'Signed' status.",
            "prompt_for_task_generation": "Upload a document with a <status> status.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DOCUMENT_UPLOADED",
                "event_criteria": {"status": {"value": "Signed", "operator": "equals"}},
                "reasoning": "This test applies when the task requires uploading a document with a 'Signed' status.",
            },
        },
    ],
)


###############################################################################
# DOCUMENT_DELETED_USE_CASE
###############################################################################
DOCUMENT_DELETED_USE_CASE = UseCase(
    name="DOCUMENT_DELETED_USE_CASE",
    description="The user deletes an existing document.",
    event=DocumentDeleted,
    event_source_code=DocumentDeleted.get_source_code_of_class(),
    # constraints_generator=default_constraints_generator,
    examples=[
        {
            "prompt": "Delete the document named 'Retainer-Agreement.pdf'.",
            "prompt_for_task_generation": "Delete the document named <document_name>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DOCUMENT_DELETED",
                "event_criteria": {"name": {"value": "Retainer-Agreement.pdf", "operator": "equals"}},
                "reasoning": "This test applies when the task requires deleting the document 'Retainer-Agreement.pdf'.",
            },
        },
        {
            "prompt": "Remove any document that is marked as 'Draft'.",
            "prompt_for_task_generation": "Remove any document that is marked as <status>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DOCUMENT_DELETED",
                "event_criteria": {"status": {"value": "Draft", "operator": "equals"}},
                "reasoning": "This test applies when the task requires deleting documents with a 'Draft' status, like 'Client-Onboarding.docx'.",
            },
        },
        {
            "prompt": "Delete the document 'Patent-Application.pdf' if its status is 'Submitted'.",
            "prompt_for_task_generation": "Delete the document <document_name> if its status is <status>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DOCUMENT_DELETED",
                "event_criteria": {"name": {"value": "Patent-Application.pdf", "operator": "equals"}, "status": {"value": "Submitted", "operator": "equals"}},
                "reasoning": "This test applies when the task requires conditional deletion of 'Patent-Application.pdf' if it's 'Submitted'.",
            },
        },
    ],
)


###############################################################################
# NEW_CALENDAR_EVENT_ADDED_USE_CASE
###############################################################################
NEW_CALENDAR_EVENT_ADDED_USE_CASE = UseCase(
    name="NEW_CALENDAR_EVENT_ADDED_USE_CASE",
    description="The user adds a new event to the calendar.",
    event=NewCalendarEventAdded,
    event_source_code=NewCalendarEventAdded.get_source_code_of_class(),
    # constraints_generator=default_constraints_generator,
    examples=[
        {
            "prompt": "Add a new calendar event for May 13, 9 AM, labeled 'Team Sync' and colored 'blue'.",
            "prompt_for_task_generation": "Add a new calendar event for <date>, <time>, labeled <label> and colored <color>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "NEW_CALENDAR_EVENT_ADDED",
                "event_criteria": {"date": {"value": "2025-05-13", "operator": "equals"}, "time": {"value": "09:00am", "operator": "equals"}, "color": {"value": "blue", "operator": "equals"}},
                "reasoning": "This test applies when the task requires adding a calendar event on May 13, 9 AM, with a blue color.",
            },
        },
        {
            "prompt": "Schedule an event for May 7th at 2:30 PM, with an 'indigo' highlight.",
            "prompt_for_task_generation": "Schedule an event for <date> at <time>, with an <color> highlight.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "NEW_CALENDAR_EVENT_ADDED",
                "event_criteria": {"date": {"value": "2025-05-07", "operator": "equals"}, "time": {"value": "2:30pm", "operator": "equals"}, "color": {"value": "indigo", "operator": "equals"}},
                "reasoning": "This test applies when the task requires adding a calendar event on May 7th, 2:30 PM, with an indigo color.",
            },
        },
        {
            "prompt": "Create a calendar event for May 22nd with a 'zinc' color, any time.",
            "prompt_for_task_generation": "Create a calendar event for <date> with a <color> color, any time.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "NEW_CALENDAR_EVENT_ADDED",
                "event_criteria": {"date": {"value": "2025-05-22", "operator": "equals"}, "color": {"value": "zinc", "operator": "equals"}},
                "reasoning": "This test applies when the task requires adding a calendar event for May 22nd with a zinc color.",
            },
        },
    ],
)


###############################################################################
# NEW_LOG_ADDED_USE_CASE
###############################################################################
NEW_LOG_ADDED_USE_CASE = UseCase(
    name="NEW_LOG_ADDED_USE_CASE",
    description="The user adds a new time log entry.",
    event=NewLogAdded,
    event_source_code=NewLogAdded.get_source_code_of_class(),
    # constraints_generator=default_constraints_generator,
    examples=[
        {
            "prompt": "Add a new time log for 'Estate Planning' matter, 2 hours, marked as 'Billable'.",
            "prompt_for_task_generation": "Add a new time log for <matter_name> matter, <hours> hours, marked as <status>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "NEW_LOG_ADDED",
                "event_criteria": {"matter": {"value": "Estate Planning", "operator": "equals"}, "hours": {"value": 2.0, "operator": "equals"}, "status": {"value": "Billable", "operator": "equals"}},
                "reasoning": "This test applies when the task requires adding a time log for 'Estate Planning' with 2 hours and 'Billable' status.",
            },
        },
        {
            "prompt": "Log 1.5 hours for 'IP Filing' activity with Acme Biotech, with a 'Billed' status.",
            "prompt_for_task_generation": "Log <hours> hours for <matter> activity with <client>, with a <status> status.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "NEW_LOG_ADDED",
                "event_criteria": {
                    "hours": {"value": 1.5, "operator": "equals"},
                    "matter": {"value": "IP Filing", "operator": "equals"},
                    "client": {"value": "Acme Biotech", "operator": "equals"},
                    "status": {"value": "Billed", "operator": "equals"},
                },
                "reasoning": "This test applies when the task requires adding a specific time log for 'IP Filing' with Acme Biotech.",
            },
        },
        {
            "prompt": "Create a time log entry with more than 2 hours for 'Peak Ventures'.",
            "prompt_for_task_generation": "Create a time log entry with more than <hours> hours for <client>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "NEW_LOG_ADDED",
                "event_criteria": {"hours": {"value": 2.0, "operator": "greater_than"}, "client": {"value": "Peak Ventures", "operator": "equals"}},
                "reasoning": "This test applies when the task requires adding a time log for 'Peak Ventures' with hours greater than 2.",
            },
        },
    ],
)


###############################################################################
# LOG_DELETE_USE_CASE
###############################################################################
LOG_DELETE_USE_CASE = UseCase(
    name="LOG_DELETE_USE_CASE",
    description="The user deletes an existing time log entry.",
    event=LogDelete,
    event_source_code=LogDelete.get_source_code_of_class(),
    # constraints_generator=default_constraints_generator,
    examples=[
        {
            "prompt": "Delete the time log for 'Estate Planning' that recorded 2 hours.",
            "prompt_for_task_generation": "Delete the time log for <matter> that recorded <hours> hours.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOG_DELETE",
                "event_criteria": {"matter": {"value": "Estate Planning", "operator": "equals"}, "hours": {"value": 2.0, "operator": "equals"}},
                "reasoning": "This test applies when the task requires deleting the time log for 'Estate Planning' with 2 hours.",
            },
        },
        {
            "prompt": "Remove any time log that is currently 'Billed'.",
            "prompt_for_task_generation": "Remove any time log that is currently <status>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOG_DELETE",
                "event_criteria": {"status": {"value": "Billed", "operator": "equals"}},
                "reasoning": "This test applies when the task requires deleting time logs with a 'Billed' status, like the 'IP Filing' log.",
            },
        },
        {
            "prompt": "Delete time logs for 'Peak Ventures' with 3 hours and 'Billable' status.",
            "prompt_for_task_generation": "Delete time logs for <client> with <hours> hours and <status> status.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOG_DELETE",
                "event_criteria": {"client": {"value": "Peak Ventures", "operator": "equals"}, "hours": {"value": 3.0, "operator": "equals"}, "status": {"value": "Billable", "operator": "equals"}},
                "reasoning": "This test applies when the task requires deleting time logs for 'Peak Ventures' with 3 hours and 'Billable' status.",
            },
        },
    ],
)


###############################################################################
# CHANGE_USER_NAME_USE_CASE
###############################################################################
CHANGE_USER_NAME_USE_CASE = UseCase(
    name="CHANGE_USER_NAME_USE_CASE",
    description="The user changes their name in the application.",
    event=ChangeUserName,
    event_source_code=ChangeUserName.get_source_code_of_class(),
    # constraints_generator=default_constraints_generator,
    examples=[
        {
            "prompt": "Change my user name to 'Muhammad Ali'.",
            "prompt_for_task_generation": "Change my user name to <new_name>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CHANGE_USER_NAME",
                "event_criteria": {"name": {"value": "Muhammad Ali", "operator": "equals"}},
                "reasoning": "This test applies when the task requires changing the user's name to 'Muhammad Ali'.",
            },
        },
        {
            "prompt": "Update my display name to 'Aisha Khan'.",
            "prompt_for_task_generation": "Update my display name to <new_name>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CHANGE_USER_NAME",
                "event_criteria": {"name": {"value": "Aisha Khan", "operator": "equals"}},
                "reasoning": "This test applies when the task requires updating the display name to 'Aisha Khan'.",
            },
        },
        {
            "prompt": "Set my user name to something that is not 'Guest User'.",
            "prompt_for_task_generation": "Set my user name to something that is not <forbidden_name>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CHANGE_USER_NAME",
                "event_criteria": {"name": {"value": "Guest User", "operator": "not_equals"}},
                "reasoning": "This test applies when the task requires changing the user's name to anything but 'Guest User'.",
            },
        },
    ],
)
###############################################################################
# FINAL LIST: ALL_USE_CASES
###############################################################################
ALL_USE_CASES = [
    ADD_NEW_MATTER_USE_CASE,
    DELETE_MATTER_USE_CASE,
    ARCHIVE_MATTER_USE_CASE,
    VIEW_MATTER_USE_CASE,
    SEARCH_CLIENT_USE_CASE,
    VIEW_CLIENT_DETAILS_USE_CASE,
    DOCUMENT_UPLOADED_USE_CASE,
    DOCUMENT_DELETED_USE_CASE,
    NEW_CALENDAR_EVENT_ADDED_USE_CASE,
    NEW_LOG_ADDED_USE_CASE,
    LOG_DELETE_USE_CASE,
    CHANGE_USER_NAME_USE_CASE,
]
