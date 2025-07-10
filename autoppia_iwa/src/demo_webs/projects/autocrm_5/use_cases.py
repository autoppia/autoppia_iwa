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
from .replace_functions import replace_placeholders

###############################################################################
# VIEW_USE_CASE
###############################################################################


VIEW_MATTER_USE_CASE = UseCase(
    name="VIEW_MATTER_DETAILS",
    description="The user views the detail of different matters",
    event=ViewMatterDetails,
    event_source_code=ViewMatterDetails.get_source_code_of_class(),
    constraints_generator=generate_view_matter_constraints,
    # replace_func=replace_placeholders,
    examples=[
        {
            "prompt": "Go to the Matters page and click on 'Estate Planning' to view the details of that particular matter",
            "prompt_for_task_generation": "Go to the Matters page and click on 'Estate Planning' to view the details of that particular matter",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_MATTER_DETAILS",
                "event_criteria": {"name": {"value": "Estate Planning"}},
                "reasoning": "This test applies when the task requires viewing the detail of a matter whose name is 'Estate Planning'.",
            },
        },
        {
            "prompt": "View details of the matter whose client name is 'Jones Legal'",
            "prompt_for_task_generation": "View details of the matter whose client name is 'Jones Legal'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_MATTER_DETAILS",
                "event_criteria": {"client": {"value": "Jones Legal"}},
                "reasoning": "This test applies when the task requires viewing the detail of a matter whose client is 'Jones Legal'.",
            },
        },
        {
            "prompt": "View matter details if its updated date is not 'Today'",
            "prompt_for_task_generation": "View matter details if its updated date is not 'Today'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_MATTER_DETAILS",
                "event_criteria": {"updated": {"value": "Today", "operator": "not_equals"}},
                "reasoning": "This test applies when the task is to view matter details that were not updated today.",
            },
        },
        {
            "prompt": "View those matters for which the status is 'Active'",
            "prompt_for_task_generation": "View those matters for which the status is 'Active'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_MATTER_DETAILS",
                "event_criteria": {"status": {"value": "Active"}},
                "reasoning": "This test applies when the task requires viewing matters that are marked as 'Active'.",
            },
        },
        {
            "prompt": "View matter details for any of the following statuses: 'Active', 'On Hold'",
            "prompt_for_task_generation": "View matter details for any of the following statuses: 'Active', 'On Hold'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_MATTER_DETAILS",
                "event_criteria": {"status": {"value": ["Active", "On Hold"], "operator": "in_list"}},
                "reasoning": "This test applies when the task is to view matters with status either 'Active' or 'On Hold'.",
            },
        },
        {
            "prompt": "View matter details excluding matters with status 'Archived' or 'On Hold'",
            "prompt_for_task_generation": "View matter details excluding matters with status 'Archived' or 'On Hold'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_MATTER_DETAILS",
                "event_criteria": {"status": {"value": ["Archived", "On Hold"], "operator": "not_in_list"}},
                "reasoning": "This test applies when the task is to exclude matters with status 'Archived' or 'On Hold'.",
            },
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
    # replace_func=replace_placeholders,
    additional_prompt_info=ADD_NEW_MATTER_EXTRA_INFO,
    examples=[
        {
            "prompt": "Create a matter named 'New Matter', with client 'Acme Co.' and status 'Active'.",
            "prompt_for_task_generation": "Create a matter named 'New Matter', with client 'Acme Co.' and status 'Active'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_NEW_MATTER",
                "event_criteria": {
                    "name": {"value": "New Matter", "operator": "equals"},
                    "client": {"value": "Acme Co.", "operator": "equals"},
                    "status": {"value": "Active", "operator": "equals"},
                },
                "reasoning": "This test applies when the task requires adding a new matter named 'New Matter', with client 'Acme Co.', and status set to 'Active'.",
            },
        },
        {
            "prompt": "Create a matter with the name that contains 'Alpha', client 'Robert Miles', and status NOT 'Archived'.",
            "prompt_for_task_generation": "Create a matter with the name 'Case Alpha', client 'Robert Miles', and status 'Archived'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_NEW_MATTER",
                "event_criteria": {
                    "name": {"value": "Alpha", "operator": "contains"},
                    "client": {"value": "Robert Miles", "operator": "equals"},
                    "status": {"value": "Archived", "operator": "not_equals"},
                },
                "reasoning": "This test applies when the task requires adding a new matter with a name containing 'Alpha', client 'Robert Miles', and status not equal to 'Archived'.",
            },
        },
        {
            "prompt": "Add a new matter where the name is not 'Employment Agreement' and the client is 'Delta Partners'.",
            "prompt_for_task_generation": "Add a new matter where the name is not 'Employment Agreement' and the client is 'Delta Partners'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_NEW_MATTER",
                "event_criteria": {
                    "name": {"value": "Employment Agreement", "operator": "not_equals"},
                    "client": {"value": "Delta Partners", "operator": "equals"},
                },
                "reasoning": "This test applies when the task requires adding a matter where the name is not 'Employment Agreement' and the client is 'Delta Partners'.",
            },
        },
    ],
)


ARCHIVE_MATTER_USE_CASE = UseCase(
    name="ARCHIVE_MATTER",
    description="The user archives a matter",
    event=ArchiveMatter,
    event_source_code=ArchiveMatter.get_source_code_of_class(),
    constraints_generator=generate_view_matter_constraints,
    # replace_func=replace_placeholders,
    examples=[
        {
            "prompt": "Archive the matter whose status is set to 'Active'",
            "prompt_for_task_generation": "Archive the matter whose status is set to 'Active'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ARCHIVE_MATTER",
                "event_criteria": {"status": {"value": "Active"}},
                "reasoning": "This test applies when the task requires archiving a matter where the status is 'Active'.",
            },
        },
        {
            "prompt": "Archive the matter where status is set to either 'Active' or 'On Hold'",
            "prompt_for_task_generation": "Archive the matter where status is set to either 'Active' or 'On Hold'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ARCHIVE_MATTER",
                "event_criteria": {"status": {"value": ["Active", "On Hold"], "operator": "in_list"}},
                "reasoning": "This test applies when the task requires archiving a matter with status either 'Active' or 'On Hold'.",
            },
        },
        {
            "prompt": "Archive the 'Estate Planning' matter if it was not updated 'Today'",
            "prompt_for_task_generation": "Archive the 'Estate Planning' matter if it was not updated 'Today'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ARCHIVE_MATTER",
                "event_criteria": {"name": {"value": "Estate Planning", "operator": "equals"}, "updated": {"value": "Today", "operator": "not_equals"}},
                "reasoning": "This test applies when the task requires archiving the matter named 'Estate Planning' that was not updated today.",
            },
        },
        {
            "prompt": "Archive the matter where matter name is 'Contract Review' and the client name is 'Jones Legal'",
            "prompt_for_task_generation": "Archive the matter where matter name is 'Contract Review' or the client name is 'Jones Legal'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ARCHIVE_MATTER",
                "event_criteria": {"name": {"value": "Contract Review", "operator": "equals"}, "client": {"value": "Jones Legal", "operator": "equals"}},
                "reasoning": "This test applies when the task requires archiving a matter either named 'Contract Review' and associated with client 'Jones Legal'.",
            },
        },
        {
            "prompt": "Archive the matter titled 'Real Estate Purchase' if the client is not 'Mohammed Anwar'",
            "prompt_for_task_generation": "Archive the matter titled 'Real Estate Purchase' if the client is not 'Mohammed Anwar'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ARCHIVE_MATTER",
                "event_criteria": {"name": {"value": "Real Estate Purchase", "operator": "equals"}, "client": {"value": "Mohammed Anwar", "operator": "not_equals"}},
                "reasoning": "This test applies when archiving the matter named 'Real Estate Purchase' only if the client is not 'Mohammed Anwar'.",
            },
        },
    ],
)

DELETE_MATTER_USE_CASE = UseCase(
    name="DELETE_MATTER",
    description="The user deletes a matter",
    event=DeleteMatter,
    event_source_code=DeleteMatter.get_source_code_of_class(),
    constraints_generator=generate_view_matter_constraints,
    # replace_func=replace_placeholders,
    examples=[
        {
            "prompt": "Delete the matter whose status is set to 'Active'",
            "prompt_for_task_generation": "Delete the matter whose status is set to 'Active'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_MATTER",
                "event_criteria": {"status": {"value": "Active"}},
                "reasoning": "This test applies when the task requires deleting a matter where status is 'Active'.",
            },
        },
        {
            "prompt": "Delete the matter where status is set to 'Active' and 'On Hold'",
            "prompt_for_task_generation": "Delete the matter where status is set to 'Active' and 'On Hold'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_MATTER",
                "event_criteria": {"status": {"value": ["Active", "On Hold"], "operator": "in_list"}},
                "reasoning": "This test applies when the task requires deleting a matter with status 'Active' or 'On Hold'.",
            },
        },
        {
            "prompt": "Delete the 'Estate Planning' matter if it was not updated 'Today'",
            "prompt_for_task_generation": "Delete the 'Estate Planning' matter if it was not updated 'Today'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_MATTER",
                "event_criteria": {
                    "name": {"value": "Estate Planning", "operator": "equals"},
                    "updated": {"value": "Today", "operator": "not_equals"},
                },
                "reasoning": "This test applies when the task requires deleting the matter 'Estate Planning' only if it wasn't updated today.",
            },
        },
        {
            "prompt": "Delete the matter where matter name is 'Contract Review' and the client name is 'Jones Legal'",
            "prompt_for_task_generation": "Delete the matter where matter name is 'Contract Review' and the client name is 'Jones Legal'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_MATTER",
                "event_criteria": {
                    "name": {"value": "Contract Review", "operator": "equals"},
                    "client": {"value": "Jones Legal", "operator": "equals"},
                },
                "reasoning": "This test applies when the task requires deleting either the matter named 'Contract Review' and a matter with client 'Jones Legal'.",
            },
        },
        {
            "prompt": "Delete the matter where status is set to 'Archived'",
            "prompt_for_task_generation": "Delete the matter where status is set to 'Archived'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_MATTER",
                "event_criteria": {"status": {"value": "Archived", "operator": "equals"}},
                "reasoning": "This test applies when the task requires deleting a matter with status 'Archived'.",
            },
        },
        {
            "prompt": "Delete the matter titled 'IP Litigation' if its client is not 'Zara Sheikh'",
            "prompt_for_task_generation": "Delete the matter titled 'IP Litigation' if its client is not 'Zara Sheikh'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_MATTER",
                "event_criteria": {
                    "name": {"value": "IP Litigation", "operator": "equals"},
                    "client": {"value": "Zara Sheikh", "operator": "not_equals"},
                },
                "reasoning": "This test applies when the task is to delete the matter named 'IP Litigation' only if it's not associated with 'Zara Sheikh'.",
            },
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
    replace_func=replace_placeholders,
    examples=[
        {
            "prompt": "View details of client, whose client name is 'jessica brown' and email is 'jbrown@samplemail.com'",
            "prompt_for_task_generation": "View details of client, whose client name is '<client_name>' and email is '<client_email>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_CLIENT_DETAILS",
                "event_criteria": {"name": {"value": "jessica brown"}, "email": {"value": "jbrown@samplemail.com"}},
                "reasoning": "This test applies when the task requires to view the detail of a client whose name is 'jessica brown",
            },
        },
        {
            "prompt": "View client details if its status is 'active', its email is 'team@smithco.com' and matters are not '3'",
            "prompt_for_task_generation": "View client details if its status is '<client_status>', its email is '<client_email>' and matters are '<client_matter>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_CLIENT_DETAILS",
                "event_criteria": {
                    "status": {"value": "active", "operator": "equals"},
                    "email": {"value": "team@smithco.com", "operator": "equals"},
                    "matters": {"value": "3", "operator": "not_equals"},
                },
                "reasoning": "This test applies when the task is to view client details if its status is 'active', its email is 'team@smithco.com' and matters are not '3'",
            },
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
            "prompt_for_task_generation": "Search for clients, excluding those matching <query>.",
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
# DOCUMENT_DELETED_USE_CASE
###############################################################################
DOCUMENT_DELETED_USE_CASE = UseCase(
    name="DOCUMENT_DELETED",
    description="The user deletes an existing document.",
    event=DocumentDeleted,
    event_source_code=DocumentDeleted.get_source_code_of_class(),
    constraints_generator=generate_document_deleted_constraints,
    replace_func=replace_placeholders,
    examples=[
        {
            "prompt": "Delete the document named 'Retainer-Agreement.pdf'.",
            "prompt_for_task_generation": "Delete the document named '<document_name>'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DOCUMENT_DELETED",
                "event_criteria": {"name": {"value": "Retainer-Agreement.pdf", "operator": "equals"}},
                "reasoning": "This test applies when the task requires deleting the document 'Retainer-Agreement.pdf'.",
            },
        },
        {
            "prompt": "Remove any document that is marked as 'Draft'.",
            "prompt_for_task_generation": "Remove any document that is marked as '<document_status>'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DOCUMENT_DELETED",
                "event_criteria": {"status": {"value": "Draft", "operator": "equals"}},
                "reasoning": "This test applies when the task requires deleting documents with a 'Draft' status, like 'Client-Onboarding.docx'.",
            },
        },
        {
            "prompt": "Delete the document 'Patent-Application.pdf' if its status is 'Submitted'.",
            "prompt_for_task_generation": "Delete the document '<document_name>' if its status is '<document_status>'.",
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
    name="NEW_CALENDAR_EVENT_ADDED",
    description="The user adds a new event to the calendar.",
    event=NewCalendarEventAdded,
    event_source_code=NewCalendarEventAdded.get_source_code_of_class(),
    constraints_generator=generate_new_calendar_event_constraints,
    replace_func=replace_placeholders,
    examples=[
        {
            "prompt": "Add a new calendar event for May 13, 9 AM, labeled 'Team Sync' and event type 'Filing'.",
            "prompt_for_task_generation": "Add a new calendar event for '<event_date>', '<event_time>', labeled '<event_label'> and colored <'event_type>'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "NEW_CALENDAR_EVENT_ADDED",
                "event_criteria": {"date": {"value": "2025-05-13", "operator": "equals"}, "time": {"value": "09:00am", "operator": "equals"}, "event_type": {"value": "Filing", "operator": "equals"}},
                "reasoning": "This test applies when the task requires adding a calendar event on May 13, 9 AM, with a blue color.",
            },
        },
        {
            "prompt": "Schedule an event for May 7th at 2:30 PM, with an 'Internal' highlight.",
            "prompt_for_task_generation": "Schedule an event for '<event_date>' at '<event_time>', with an '<event_type>' highlight.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "NEW_CALENDAR_EVENT_ADDED",
                "event_criteria": {"date": {"value": "2025-05-07", "operator": "equals"}, "time": {"value": "2:30pm", "operator": "equals"}, "event_type": {"value": "Internal", "operator": "equals"}},
                "reasoning": "This test applies when the task requires adding a calendar event on May 7th, 2:30 PM, with an indigo color.",
            },
        },
        {
            "prompt": "Create a calendar event for May 22nd with a 'Matter/Event' color, any time.",
            "prompt_for_task_generation": "Create a calendar event for '<event_date>' with a '<event_type>' color, any time.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "NEW_CALENDAR_EVENT_ADDED",
                "event_criteria": {"date": {"value": "2025-05-22", "operator": "equals"}, "event_type": {"value": "Matter/Event", "operator": "equals"}},
                "reasoning": "This test applies when the task requires adding a calendar event for May 22nd with a zinc color.",
            },
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
    # replace_func=replace_placeholders,
    additional_prompt_info=ADD_NEW_LOG_EXTRA_INFO,
    examples=[
        {
            "prompt": "Add a time log for 'Trademark Filing' with 2.5 hours for 'Prepare documents'.",
            "prompt_for_task_generation": "Add a time log for 'Trademark Filing' with '2.5' hours for 'Prepare documents'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "NEW_LOG_ADDED",
                "event_criteria": {
                    "matter": {"value": "Trademark Filing", "operator": "equals"},
                    "hours": {"value": 2.5, "operator": "equals"},
                    "description": {"value": "Prepare documents", "operator": "equals"},
                },
                "reasoning": "This test applies when the task requires logging 2.5 hours for 'Trademark Filing' with the description 'Prepare documents'.",
            },
        },
        {
            "prompt": "Log 3 hours for 'M&A Advice' to record 'Negotiation call'.",
            "prompt_for_task_generation": "Log 3 hours for 'M&A Advice' to record 'Negotiation call'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "NEW_LOG_ADDED",
                "event_criteria": {
                    "matter": {"value": "M&A Advice", "operator": "equals"},
                    "hours": {"value": 3.0, "operator": "equals"},
                    "description": {"value": "Negotiation call", "operator": "equals"},
                },
                "reasoning": "This test applies when logging 3 hours for 'M&A Advice' for a negotiation call.",
            },
        },
        {
            "prompt": "Create a new log for 'Startup Incorporation' with more than 3 hours for 'Setup docs'.",
            "prompt_for_task_generation": "Create a new log for 'Startup Incorporation' with more than '3' hours for 'Setup docs'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "NEW_LOG_ADDED",
                "event_criteria": {
                    "matter": {"value": "Startup Incorporation", "operator": "equals"},
                    "hours": {"value": 3.0, "operator": "greater_than"},
                    "description": {"value": "Setup docs", "operator": "equals"},
                },
                "reasoning": "This test applies when the task requires logging more than 3 hours for 'Startup Incorporation' with description 'Setup docs'.",
            },
        },
        {
            "prompt": "Log time for 'Tax Advisory' but make sure the hours are not 2.5, use 'Tax analysis' as description.",
            "prompt_for_task_generation": "Log time for 'Tax Advisory' with hours not equal to '2.5' and description 'Tax analysis'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "NEW_LOG_ADDED",
                "event_criteria": {
                    "matter": {"value": "Tax Advisory", "operator": "equals"},
                    "hours": {"value": 2.5, "operator": "not_equals"},
                    "description": {"value": "Tax analysis", "operator": "equals"},
                },
                "reasoning": "This test applies when the task requires logging hours for 'Tax Advisory' but not exactly 2.5, with description 'Tax analysis'.",
            },
        },
        {
            "prompt": "Create a log for 'Trademark Renewal' for less than 1 hour, describing it as 'Online filing'.",
            "prompt_for_task_generation": "Create a log for 'Trademark Renewal' with less than '1' hour and description 'Online filing'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "NEW_LOG_ADDED",
                "event_criteria": {
                    "matter": {"value": "Trademark Renewal", "operator": "equals"},
                    "hours": {"value": 1.0, "operator": "less_than"},
                    "description": {"value": "Online filing", "operator": "equals"},
                },
                "reasoning": "This test applies when the task requires logging less than 1 hour for 'Trademark Renewal' with description 'Online filing'.",
            },
        },
    ],
)


###############################################################################
# LOG_DELETE_USE_CASE
###############################################################################
LOG_DELETE_USE_CASE = UseCase(
    name="LOG_DELETE",
    description="The user deletes an existing time log entry.",
    event=LogDelete,
    event_source_code=LogDelete.get_source_code_of_class(),
    constraints_generator=generate_delete_log_constraints,
    # replace_func=replace_placeholders,
    examples=[
        {
            "prompt": "Delete the time log for 'Estate Planning' that recorded 2 hours.",
            "prompt_for_task_generation": "Delete the time log for 'Estate Planning' that recorded 2 hours.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOG_DELETE",
                "event_criteria": {"matter": {"value": "Estate Planning", "operator": "equals"}, "hours": {"value": 2.0, "operator": "equals"}},
                "reasoning": "This test applies when the task requires deleting the time log for 'Estate Planning' with 2 hours.",
            },
        },
        {
            "prompt": "Remove any time log that is currently 'Billed'.",
            "prompt_for_task_generation": "Remove any time log that is currently 'Billed'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOG_DELETE",
                "event_criteria": {"status": {"value": "Billed", "operator": "equals"}},
                "reasoning": "This test applies when the task requires deleting time logs with a 'Billed' status, like the 'IP Filing' log.",
            },
        },
        {
            "prompt": "Delete time logs for 'Peak Ventures' with 3 hours and 'Billable' status.",
            "prompt_for_task_generation": "Delete time logs for 'Peak Ventures' with 3 hours and 'Billable' status.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOG_DELETE",
                "event_criteria": {"client": {"value": "Peak Ventures", "operator": "equals"}, "hours": {"value": 3.0, "operator": "equals"}, "status": {"value": "Billable", "operator": "equals"}},
                "reasoning": "This test applies when the task requires deleting time logs for 'Peak Ventures' with 3 hours and 'Billable' status.",
            },
        },
        {
            "prompt": "Delete any log where hours are not equal to 2.5.",
            "prompt_for_task_generation": "Delete any log where hours are not equal to 2.5.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOG_DELETE",
                "event_criteria": {
                    "hours": {"value": 2.5, "operator": "not_equals"},
                },
                "reasoning": "This test applies when the task requires deleting time logs where the hours are not 2.5.",
            },
        },
        {
            "prompt": "Delete all logs where the description contains 'memo'.",
            "prompt_for_task_generation": "Delete all logs where the description contains 'memo'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOG_DELETE",
                "event_criteria": {"description": {"value": "memo", "operator": "contains"}},
                "reasoning": "This test applies when the task targets logs whose description contains 'memo'.",
            },
        },
        {
            "prompt": "Delete logs where the hours are greater than 4.",
            "prompt_for_task_generation": "Delete logs where the hours are greater than 4.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOG_DELETE",
                "event_criteria": {"hours": {"value": 4.0, "operator": "greater_than"}},
                "reasoning": "This test applies when the task filters logs with more than 4 hours for deletion.",
            },
        },
        {
            "prompt": "Delete time logs with less than 1.5 hours for 'LabelLine'.",
            "prompt_for_task_generation": "Delete time logs with less than 1.5 hours for 'LabelLine'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOG_DELETE",
                "event_criteria": {
                    "client": {"value": "LabelLine", "operator": "equals"},
                    "hours": {"value": 1.5, "operator": "less_than"},
                },
                "reasoning": "This test applies when the task requires deleting logs with less than 1.5 hours for the 'LabelLine' client.",
            },
        },
        {
            "prompt": "Remove time logs for the matter 'Startup Pitch Deck' where the client is not 'LaunchLeap'.",
            "prompt_for_task_generation": "Remove time logs for the matter 'Startup Pitch Deck' where the client is not 'LaunchLeap'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOG_DELETE",
                "event_criteria": {
                    "matter": {"value": "Startup Pitch Deck", "operator": "equals"},
                    "client": {"value": "LaunchLeap", "operator": "not_equals"},
                },
                "reasoning": "This test applies when the client does not match the expected name, for the specific matter.",
            },
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
    replace_func=replace_placeholders,
    additional_prompt_info=CHANGE_USER_NAME_EXTRA_INFO,
    examples=[
        {
            "prompt": "Change my user name to 'Muhammad Ali'.",
            "prompt_for_task_generation": "Change my user name to '<new_name>'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CHANGE_USER_NAME",
                "event_criteria": {"name": {"value": "Muhammad Ali", "operator": "equals"}},
                "reasoning": "This test applies when the task requires changing the user's name to 'Muhammad Ali'.",
            },
        },
        {
            "prompt": "Update my display name to 'Aisha Khan'.",
            "prompt_for_task_generation": "Update my display name to '<new_name>'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CHANGE_USER_NAME",
                "event_criteria": {"name": {"value": "Aisha Khan", "operator": "equals"}},
                "reasoning": "This test applies when the task requires updating the display name to 'Aisha Khan'.",
            },
        },
        {
            "prompt": "Set my user name to something that is not 'Guest User'.",
            "prompt_for_task_generation": "Set my user name to something that is not '<forbidden_name>'.",
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
    # ADD_NEW_MATTER_USE_CASE,
    # VIEW_MATTER_USE_CASE,
    # DELETE_MATTER_USE_CASE,
    # ARCHIVE_MATTER_USE_CASE,
    # VIEW_CLIENT_DETAILS_USE_CASE,
    # SEARCH_CLIENT_USE_CASE,
    # DOCUMENT_DELETED_USE_CASE,
    # NEW_CALENDAR_EVENT_ADDED_USE_CASE,
    # NEW_LOG_ADDED_USE_CASE,
    LOG_DELETE_USE_CASE,
    # CHANGE_USER_NAME_USE_CASE,
]
