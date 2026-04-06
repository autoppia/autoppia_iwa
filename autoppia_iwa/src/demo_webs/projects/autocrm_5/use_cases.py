# -----------------------------------------------------------------------------
# use_cases.py
# -----------------------------------------------------------------------------
from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    AddClientEvent,
    AddNewMatter,
    ArchiveMatter,
    BillingSearchEvent,
    ChangeUserName,
    DeleteClientEvent,
    DeleteMatter,
    DocumentDeleted,
    DocumentRenamedEvent,
    FilterClientsEvent,
    FilterMatterStatus,
    HelpViewedEvent,
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
    generate_add_client_constraints,
    generate_add_matter_constraints,
    generate_billing_search_constraints,
    generate_change_user_name_constraints,
    generate_delete_client_constraints,
    generate_delete_log_constraints,
    generate_document_deleted_constraints,
    generate_document_renamed_constraints,
    generate_filter_clients_constraints,
    generate_filter_matter_status_constraints,
    generate_log_edited_constraints,
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

VIEW_MATTER_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of the matter (e.g. name, client, status, updated).

Use natural language only. Do NOT use schema-style field names such as "name", "client", "status", "updated", or any names with underscores (_).

Always refer to fields using simple phrasing (e.g. matter name, client name, status, updated).

Identify the matter using the provided visible field values (e.g. matter name, client, status, updated), then ask for the verify field value naturally.

Do NOT start questions with imperative phrasing like "Navigate...", "Show details...", "View...", or "Open...".

For the updated field specifically, format the question in a conditional style:
- "When was the matter named 'Estate Planning' with status 'Archived' updated?"

Every generated question MUST include a subtle confirmation context at the end, such as "Please confirm the value after viewing the detail" or "Confirm the value after viewing the detail". This must appear at the end of the question.

Examples:
- "What is the client name of the matter 'Estate Planning'? Please confirm the value after viewing the detail."
- "What is the status of the matter whose client is 'Jones Legal'? Confirm the value after viewing the detail."
- "When was the matter named 'Estate Planning' with status 'Archived' updated? Please confirm the value after viewing the detail."
- "What is the name of the matter assigned to client 'Smith & Co'? Confirm the value after viewing the detail."

The output must be a single question asking only for the verify field value and must include the confirmation phrase at the end.
""".strip()

VIEW_MATTER_USE_CASE = UseCase(
    name="VIEW_MATTER_DETAILS",
    description="The user views the detail of different matters",
    event=ViewMatterDetails,
    event_source_code=ViewMatterDetails.get_source_code_of_class(),
    constraints_generator=generate_view_matter_constraints,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=VIEW_MATTER_DATA_EXTRACTION_PROMPT_INFO,
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
            "prompt": "View matter details for matters with status 'Active'",
            "prompt_for_task_generation": "View matter details for matters with status 'Active'",
        },
        {
            "prompt": "View matter details excluding matters with status 'Archived'",
            "prompt_for_task_generation": "View matter details excluding matters with status 'Archived'",
        },
    ],
)

###############################################################################
# SEARCH_MATTER_USE_CASE
###############################################################################

SEARCH_MATTER_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of the matter (e.g. name, client, status, updated).

Use natural language only. Do NOT use schema-style field names such as "name", "client", "status", "updated", or any names with underscores (_).

Always refer to fields using simple phrasing (e.g. matter name, client name, status, updated).

Identify the matter using the provided visible field values (e.g. matter name, client, status, updated), then ask for the verify field value naturally.

Do NOT start the question with phrases like "Search for...", "Find...", or "Look for...".

For the updated field specifically, format the question in a conditional style:
- "When was the matter named 'Estate Planning' with status 'Archived' updated?"

Examples:
- "What is the client name of the matter that contains 'Estate' in the title?"
- "What is the status of the matter named 'Compliance Review'?"
- "What is the name of the matter with client 'Acme Co.' and status 'Active'?"
- "When was the matter named 'Estate Planning' with status 'Archived' updated?"

The output must be a single question asking only for the verify field value.
""".strip()

SEARCH_MATTER_USE_CASE = UseCase(
    name="SEARCH_MATTER",
    description="The user searches for matters using a query string.",
    event=SearchMatter,
    event_source_code=SearchMatter.get_source_code_of_class(),
    constraints_generator=generate_search_matter_constraints,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=SEARCH_MATTER_DATA_EXTRACTION_PROMPT_INFO,
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

✔️ CORRECT: Create a matter with the name 'New Matter', with client 'John Doe', and status that is NOT equal to 'Archived'.
✔️ CORRECT: Create a matter with the name that is NOT 'Acquisition Deal', with client 'John Doe', and status that is NOT equal to 'Archived'.
✔️ CORRECT: Create a matter with the name that is NOT 'Acquisition Deal', status that is NOT equal to 'Archived', and client that does NOT contain 'Client'.
❌ INCORRECT: Create a matter with the name 'New Matter' that is NOT 'Acquisition Deal', with client 'John Doe', and status that is NOT equal to 'Archived', and where the client does NOT contain 'Confidential Client'. (Multiple constraints for the same fields)
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
ARCHIVE_MATTER_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with one of the following: "Archive the matter...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

ARCHIVE_MATTER_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of the matter (e.g. name, client, status, updated).

Use natural language only. Do NOT use schema-style field names such as "name", "client", "status", "updated", or any names with underscores (_).

Always refer to fields using simple phrasing (e.g. matter name, client name, status, updated).

Identify the matter using the provided visible field values (e.g. matter name, client, status, updated), then ask for the verify field value naturally.

Do NOT start questions with imperative phrasing like "Archive...", "Delete...", or "Open...".

For the updated field specifically, format the question in a conditional style:
- "When was the matter named 'Estate Planning' with status 'Archived' updated?"

Every generated question MUST include a subtle confirmation context at the end, such as "Please confirm the value before archiving" or "Confirm the value before archiving". This must appear at the end of the question.

Examples:
- "What is the client name of the matter 'Estate Planning'? Please confirm the value before archiving."
- "What is the status of the matter whose client is 'Jones Legal'? Confirm the value before archiving."
- "When was the matter named 'Estate Planning' with status 'Archived' updated? Please confirm the value before archiving."
- "What is the name of the matter assigned to client 'Smith & Co'? Confirm the value before archiving."

The output must be a single question asking only for the verify field value and must include the confirmation phrase at the end.
""".strip()

ARCHIVE_MATTER_USE_CASE = UseCase(
    name="ARCHIVE_MATTER",
    description="The user archives a matter",
    event=ArchiveMatter,
    event_source_code=ArchiveMatter.get_source_code_of_class(),
    constraints_generator=generate_view_matter_constraints,
    additional_prompt_info=ARCHIVE_MATTER_ADDITIONAL_PROMPT_INFO,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=ARCHIVE_MATTER_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "Archive the matter whose status is set to 'Active'",
            "prompt_for_task_generation": "Archive the matter whose status is set to 'Active'",
        },
        {
            "prompt": "Archive the matter where status is set to 'Active'",
            "prompt_for_task_generation": "Archive the matter where status is set to 'Active'",
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
DELETE_MATTER_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with one of the following: "Delete the matter...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

DELETE_MATTER_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of the matter (e.g. name, client, status, updated).

Use natural language only. Do NOT use schema-style field names such as "name", "client", "status", "updated", or any names with underscores (_).

Always refer to fields using simple phrasing (e.g. matter name, client name, status, updated).

Identify the matter using the provided visible field values (e.g. matter name, client, status, updated), then ask for the verify field value naturally.

Do NOT start questions with imperative phrasing like "Delete...", "Archive...", or "Open...".

For the updated field specifically, format the question in a conditional style:
- "When was the matter named 'Estate Planning' with status 'Archived' updated?"

Every generated question MUST include a subtle confirmation context at the end, such as "Please confirm the value before deletion" or "Confirm the value before deletion". This must appear at the end of the question.

Examples:
- "What is the client name of the matter 'Estate Planning'? Please confirm the value before deletion."
- "What is the status of the matter whose client is 'Jones Legal'? Confirm the value before deletion."
- "When was the matter named 'Estate Planning' with status 'Archived' updated? Please confirm the value before deletion."
- "What is the name of the matter assigned to client 'Smith & Co'? Confirm the value before deletion."

The output must be a single question asking only for the verify field value and must include the confirmation phrase at the end.
""".strip()

DELETE_MATTER_USE_CASE = UseCase(
    name="DELETE_MATTER",
    description="The user deletes a matter",
    event=DeleteMatter,
    event_source_code=DeleteMatter.get_source_code_of_class(),
    constraints_generator=generate_view_matter_constraints,
    additional_prompt_info=DELETE_MATTER_ADDITIONAL_PROMPT_INFO,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=DELETE_MATTER_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "Delete the matter whose status is set to 'Active'",
            "prompt_for_task_generation": "Delete the matter whose status is set to 'Active'",
        },
        {
            "prompt": "Delete the matter where status is set to 'Active'",
            "prompt_for_task_generation": "Delete the matter where status is set to 'Active'",
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
FILTER_MATTER_STATUS_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for matters based on their status or other visible attributes (e.g. name, client, status, updated).

Use natural language only. Do NOT use schema-style field names such as "name", "client", "status", "updated", or any names with underscores (_).

Always refer to fields using simple phrasing (e.g. matter name, client name, status, updated).

Identify the matter using the provided visible field values (e.g. matter name, client, status, updated), then ask for matters filtered by the status naturally.

Do NOT start questions with imperative phrasing like "Delete...", "Archive...", or "Open...".

For the updated field specifically, format the question in a conditional style:
- "When was the matter named 'Estate Planning' with status 'Archived' updated"

Every generated question MUST include a subtle confirmation context at the end, such as "Please confirm the value before filtration" or "Confirm the value before filtration". This must appear at the end of the question.

Examples:
- "What is the client name of the matter 'Estate Planning'? Please confirm the value before filtration."
- "What is the status of the matter whose client is 'Jones Legal'? Confirm the value before filtration."
- "When was the matter named 'Estate Planning' with status 'Archived' updated? Please confirm the value before filtration."
- "What is the name of the matter assigned to client 'Smith & Co'? Confirm the value before filtration."

The output must be a single question asking only for matters filtered by status and must include the confirmation phrase at the end.
""".strip()

FILTER_MATTER_STATUS_USE_CASE = UseCase(
    name="FILTER_MATTER_STATUS",
    description="The user filters matters by status.",
    event=FilterMatterStatus,
    event_source_code=FilterMatterStatus.get_source_code_of_class(),
    constraints_generator=generate_filter_matter_status_constraints,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=FILTER_MATTER_STATUS_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "Filter matters to only show those with status 'Active' or as similar.",
            "prompt_for_task_generation": "Filter matters to only show those with status 'Active' or as similar.",
        },
        {
            "prompt": "Filter matters to exclude status 'Archived' or as similar.",
            "prompt_for_task_generation": "Filter matters to exclude status 'Archived' or as similar.",
        },
        {
            "prompt": "Show matters that have status 'Active' or as similar.",
            "prompt_for_task_generation": "Show matters that have status 'Active' or as similar.",
        },
    ],
)

###############################################################################
# SORT_MATTER_BY_CREATED_AT_USE_CASE
###############################################################################
SORT_MATTER_BY_CREATED_AT_USE_CASE = UseCase(
    name="SORT_MATTER_BY_CREATED_AT",
    description="The user sorts matters by created date in ascending and descending order direction.",
    event=SortMatterByCreatedAt,
    event_source_code=SortMatterByCreatedAt.get_source_code_of_class(),
    constraints_generator=generate_sort_matter_constraints,
    examples=[
        {
            "prompt": "Sort matters by latest first.",
            "prompt_for_task_generation": "Sort matters by latest first.",
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

UPDATE_MATTER_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of the matter (e.g. name, client, status, updated).

Use natural language only. Do NOT use schema-style field names such as "name", "client", "status", "updated", or any names with underscores (_).

Always refer to fields using simple phrasing (e.g. matter name, client name, status, updated).

Identify the matter using the provided visible field values (e.g. matter name, client, status, updated), then ask for the verify field value naturally.

Do NOT start questions with imperative phrasing like "Update...", "Edit...", or "Open...".

For the updated field specifically, format the question in a conditional style:
- "When was the matter named 'Estate Planning' with status 'Archived' updated?"

Every generated question MUST include a subtle confirmation context at the end, such as "Please confirm the value before updating" or "Confirm the value before updating". This must appear at the end of the question.

Examples:
- "What is the client name of the matter 'Estate Planning'? Please confirm the value before updating."
- "What is the status of the matter whose client is 'Jones Legal'? Confirm the value before updating."
- "When was the matter named 'Estate Planning' with status 'Archived' updated? Please confirm the value before updating."
- "What is the name of the matter assigned to client 'Smith & Co'? Confirm the value before updating."

The output must be a single question asking only for the verify field value and must include the confirmation phrase at the end.
""".strip()

UPDATE_MATTER_USE_CASE = UseCase(
    name="UPDATE_MATTER",
    description="The user updates an existing matter.",
    event=UpdateMatter,
    event_source_code=UpdateMatter.get_source_code_of_class(),
    constraints_generator=generate_update_matter_constraints,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=UPDATE_MATTER_DATA_EXTRACTION_PROMPT_INFO,
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

VIEW_CLIENT_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of the client (e.g. name, email, status, matters count).

Use natural language only. Do NOT use schema-style field names such as "name", "email", "status", "matters", or any names with underscores (_).

Always refer to fields using simple phrasing (e.g. client name, email, status, number of matters).

Identify the client using the provided visible field values (e.g. client name, email, status), then ask for the verify field value naturally.

Do NOT start questions with imperative phrasing like "Navigate...", "Show details...", "View...", or "Open...".

For the matters field, ask naturally as a count:
- "How many matters does the client 'Acme Co.' have?"

Every generated question MUST include a subtle confirmation context at the end, such as "Please confirm the value after viewing the detail" or "Confirm the value after viewing the detail". This must appear at the end of the question.

Examples:
- "What is the email of the client 'Jessica Brown'? Please confirm the value after viewing the detail."
- "What is the status of the client whose email is 'team@smithco.com'? Confirm the value after viewing the detail."
- "How many matters does the client 'Acme Co.' have? Please confirm the value after viewing the detail."

The output must be a single question asking only for the verify field value and must include the confirmation phrase at the end.
""".strip()

VIEW_CLIENT_DETAILS_USE_CASE = UseCase(
    name="VIEW_CLIENT_DETAILS",
    description="The user views the detail of different clients",
    event=ViewClientDetails,
    event_source_code=ViewClientDetails.get_source_code_of_class(),
    constraints_generator=generate_view_client_constraints,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=VIEW_CLIENT_DATA_EXTRACTION_PROMPT_INFO,
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

SEARCH_CLIENT_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of the client (e.g. name, email, status, number of matters).

Use natural language only. Do NOT use schema-style field names such as "name", "email", "status", "matters", or any names with underscores (_).

Always refer to fields using simple phrasing (e.g. client name, email, status, number of matters).

Identify the client using the provided visible field values (e.g. client name, email, status), then ask for the verify field value naturally.

Do NOT start questions with phrases like "Search for...", "Find...", or "Look for...".

For the matters field, ask naturally as a count:
- "How many matters does the client 'Acme Co.' have?"

Examples:
- "What is the email of the client named 'Smith'?"
- "What is the status of the client whose name contains 'Brown'?"
- "What is the name of the client with email 'jbrown@samplemail.com'?"
- "How many matters does the client 'Acme Co.' have?"

The output must be a single question asking only for the verify field value.
""".strip()
SEARCH_CLIENT_USE_CASE = UseCase(
    name="SEARCH_CLIENT",
    description="The user searches for clients using a query string.",
    event=SearchClient,
    event_source_code=SearchClient.get_source_code_of_class(),
    constraints_generator=generate_search_client_constraints,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=SEARCH_CLIENT_DATA_EXTRACTION_PROMPT_INFO,
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

DOCUMENT_DELETED_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of the document (e.g. name, size, version, status, updated).

Use natural language only. Do NOT use schema-style field names such as "name", "size", "version", "status", "updated", or any names with underscores (_).

Always refer to fields using simple phrasing (e.g. document name, size, version, status, updated).

Identify the document using the provided visible field values (e.g. document name, size, version, status, updated), then ask for the verify field value naturally.

Do NOT start questions with imperative phrasing like "Delete...", "Remove...", or "Open...".

For the updated field specifically, format the question in a conditional style:
- "When was the document named 'Contract-Terms-2025.pdf' with version 'v2' updated?"

Every generated question MUST include a subtle confirmation context at the end, such as "Please confirm the value before deletion" or "Confirm the value before deletion". This must appear at the end of the question.

Examples:
- "What is the size of the document 'Project Plan'? Please confirm the value before deletion."
- "What is the version of the document whose name is 'Budget Report'? Confirm the value before deletion."
- "What is the status of the document with version 'v2'? Please confirm the value before deletion."
- "When was the document named 'Contract-Terms-2025.pdf' with version 'v2' updated? Confirm the value before deletion."

The output must be a single question asking only for the verify field value and must include the confirmation phrase at the end.
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
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=DOCUMENT_DELETED_DATA_EXTRACTION_PROMPT_INFO,
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

DOCUMENT_RENAMED_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of the document (e.g. name, size, version, status, updated).

Use natural language only. Do NOT use schema-style field names such as "name", "size", "version", "status", "updated", or any names with underscores (_).

Always refer to fields using simple phrasing (e.g. document name, size, version, status, updated).

Identify the document using the provided visible field values (e.g. document name, size, version, status, updated), then ask for the verify field value naturally.

Do NOT start questions with imperative phrasing like "Rename...", "Update...", or "Open...".

For the updated field specifically, format the question in a conditional style:
- "When was the document named 'Estate Planning' with version 'v3' updated?"

Every generated question MUST include a subtle confirmation context at the end, such as "Please confirm the value before renaming" or "Confirm the value before renaming". This must appear at the end of the question.

Examples:
- "What is the size of the document 'Project Plan'? Please confirm the value before renaming."
- "What is the version of the document whose name is 'Budget Report'? Confirm the value before renaming."
- "What is the status of the document with version 'v2.1'? Please confirm the value before renaming."
- "When was the document named 'Retainer-Agreement.pdf' with version 'v3' updated? Confirm the value before renaming."

The output must be a single question asking only for the verify field value and must include the confirmation phrase at the end.
""".strip()

DOCUMENT_RENAMED_USE_CASE = UseCase(
    name="DOCUMENT_RENAMED",
    description="The user renames an existing document.",
    event=DocumentRenamedEvent,
    event_source_code=DocumentRenamedEvent.get_source_code_of_class(),
    constraints_generator=generate_document_renamed_constraints,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=DOCUMENT_RENAMED_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "Rename the document 'Retainer-Agreement.pdf' to 'Retainer-Agreement-final.pdf'.",
            "prompt_for_task_generation": "Rename the document 'Retainer-Agreement.pdf' to 'Retainer-Agreement-final.pdf'.",
        },
        {
            "prompt": "Update the file name of NDA-Sample.docx to NDA-Sample-v2.docx.",
            "prompt_for_task_generation": "Update the file name of NDA-Sample.docx to NDA-Sample-v2.docx.",
        },
    ],
)
NEW_CALENDAR_EVENT_EXTRA_INFO = """
Critical requirements:
1. The request must start with one of the following: "Add a new calendar event...".
2. Include ALL mentioned constraints in the prompt.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
4. All constraint values must be copied exactly as provided, character-for-character.
5. Do NOT reformat, normalize, paraphrase, or adjust any values (including time, date, capitalization, spacing, or punctuation).
6. If a time is given as "3:30pm", it must appear exactly as "3:30pm" in the prompt — not "3:30 PM", "15:30", or any other variation.
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
    additional_prompt_info=NEW_CALENDAR_EVENT_EXTRA_INFO,
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
Critical requirements:
1. The request must start with one of the following: "Add log...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
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
            "prompt": "Add log with matter 'Trademark Filing', description 'Prepare documents', and hours '2.5'.",
            "prompt_for_task_generation": "Add log with matter 'Trademark Filing', description 'Prepare documents', and hours '2.5'.",
        },
        {
            "prompt": "Add log with matter 'M&A Advice', description 'Negotiation call', and hours '3'.",
            "prompt_for_task_generation": "Add log with matter 'M&A Advice', description 'Negotiation call', and hours '3'.",
        },
        {
            "prompt": "Add log with matter 'Startup Incorporation', description 'Setup docs', and hours greater than '3'.",
            "prompt_for_task_generation": "Add log with matter 'Startup Incorporation', description 'Setup docs', and hours greater than '3'.",
        },
        {
            "prompt": "Add log with matter 'Tax Advisory', description 'Tax analysis', and hours not equal to '2.5'.",
            "prompt_for_task_generation": "Add log with matter 'Tax Advisory', description 'Tax analysis', and hours not equal to '2.5'.",
        },
        {
            "prompt": "Add log with matter 'Trademark Renewal', description 'Online filing', and hours less than '1'.",
            "prompt_for_task_generation": "Add log with matter 'Trademark Renewal', description 'Online filing', and hours less than '1'.",
        },
    ],
)

LOG_EDITED_EXTRA_INFO = """
Critical requirements:
1. The request must start with one of the following: "Edit log...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

LOG_EDITED_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of the time log (e.g. matter, client, hours, status, description, date).

Use natural language only. Do NOT use schema-style field names such as "matter", "client", "hours", "status", "description", "date", or any names with underscores (_).

Always refer to fields using simple phrasing (e.g. matter name, client name, hours, status, description, date).

Identify the log using the provided visible field values (e.g. matter name, client, hours, status, date), then ask for the verify field value naturally.

Do NOT start questions with imperative phrasing like "Edit...", "Update...", or "Open...".

For the date field specifically, format the question in a conditional style:
- "What is the date when the log with matter 'Estate Planning' and hours '5h' recorded?"

For the hours field, ask naturally as a value:
- "How many hours are recorded for the log with matter 'Estate Planning'?"

Every generated question MUST include a subtle confirmation context at the end, such as "Please confirm the value before editing" or "Confirm the value before editing". This must appear at the end of the question.

Examples:
- "What is the client name of the log for matter 'Estate Planning'? Please confirm the value before editing."
- "What is the status of the log with description 'Initial consultation'? Confirm the value before editing."
- "How many hours are recorded for the log with matter 'Estate Planning'? Please confirm the value before editing."
- "What is the date when the log with matter 'Estate Planning' and hours '5h' recorded? Confirm the value before editing."

The output must be a single question asking only for the verify field value and must include the confirmation phrase at the end.
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
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=LOG_EDITED_DATA_EXTRACTION_PROMPT_INFO,
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
1. Use at most one constraint per field: `matter`, `description`, `hours`, `client`, or `status`.
2. Mirror the constraint operator and the value exactly in the generated prompt. Do not paraphrase operators (e.g. use the specified negation).

Example constraint (Python dict):
constraint: {'matter': {'operator': 'not_equals', 'value': 'Court Filing'}, 'hours': {'operator': 'not_equals', 'value': 2.3}, 'client': {'operator': 'not_contains', 'value': 'CoreConnect'}, 'status': {'operator': 'equals', 'value': 'Billed'}}

Prompts:
✔️ CORRECT: Delete the time log where matter is NOT equal to 'Court Filing', hours is NOT equal to 2.3, client does NOT CONTAIN 'CoreConnect', and status is equal to 'Billed'.
❌ INCORRECT: Delete the time log for 'Court Filing' that recorded hours NOT EQUAL to 2.3, where the client does NOT CONTAIN 'CoreConnect' and the status is equal to 'Billed'.

Explanation: The incorrect prompt does not reflect the specified operator for `matter` (`not_equals`) — it uses a positive equality instead of the required negation. Use the exact operators and value formats shown in the constraint.
""".strip()

LOG_DELETE_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of the time log (e.g. matter, client, hours, status, description, date).

Use natural language only. Do NOT use schema-style field names such as "matter", "client", "hours", "status", "description", "date", or any names with underscores (_).

Always refer to fields using simple phrasing (e.g. matter name, client name, hours, status, description, date).

Identify the log using the provided visible field values (e.g. matter name, client, hours, status, date), then ask for the verify field value naturally.

Do NOT start questions with imperative phrasing like "Delete...", "Remove...", or "Open...".

For the date field specifically, format the question in a conditional style:
- "What is the date when the log with matter 'Estate Planning' and hours '5h' recorded?"

For the hours field, ask naturally as a value:
- "How many hours are recorded for the log with matter 'Estate Planning'?"

Every generated question MUST include a subtle confirmation context at the end, such as "Please confirm the value before deletion" or "Confirm the value before deletion". This must appear at the end of the question.

Examples:
- "What is the client name of the log for matter 'Estate Planning'? Please confirm the value before deletion."
- "What is the status of the log with description 'Initial consultation'? Confirm the value before deletion."
- "How many hours are recorded for the log with matter 'Estate Planning'? Please confirm the value before deletion."
- "What is the date when the log with matter 'Estate Planning' and hours '5h' recorded? Confirm the value before deletion."

The output must be a single question asking only for the verify field value and must include the confirmation phrase at the end.
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
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=LOG_DELETE_DATA_EXTRACTION_PROMPT_INFO,
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

BILLING_SEARCH_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for billing or time log entries based on their attributes or other visible values (e.g. matter, client, hours, status, description, date).

Use natural language only. Do NOT use schema-style field names such as "matter", "client", "hours", "status", "description", "date", or any names with underscores (_).

Always refer to fields using simple phrasing (e.g. matter name, client name, hours, status, description, date).

Identify the log entry using the provided visible field values (e.g. matter name, client, hours, status, date), then ask for the verify field value naturally.

Do NOT start questions with imperative phrasing like "Search...", "Filter...", or "Open...".

For the hours field, ask naturally as a value (e.g. "How many hours are recorded for the log with matter 'X'?").
For the date field, format in a conditional style (e.g. "What is the date when the log for matter 'X' was recorded?").

Examples:
- "What is the client name for the billing entry of matter 'Estate Planning'?"
- "How many hours are recorded for the log with matter 'Jones Legal'?"
- "What is the status of the billing entry for matter 'Estate Planning'?"
- "What is the date when the log for matter 'Smith & Co' was recorded?"

The output must be a single question asking only for the verify field value and must include the confirmation phrase at the end.
""".strip()

BILLING_SEARCH_USE_CASE = UseCase(
    name="BILLING_SEARCH",
    description="Search or filter billing entries by text or date range.",
    event=BillingSearchEvent,
    event_source_code=BillingSearchEvent.get_source_code_of_class(),
    constraints_generator=generate_billing_search_constraints,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=BILLING_SEARCH_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "Search billing entries for 'contract' from this week.",
            "prompt_for_task_generation": "Search billing entries for 'contract' from this week.",
        },
        {
            "prompt": "Filter time logs to only today for matter review.",
            "prompt_for_task_generation": "Filter time logs to only today.",
        },
    ],
)

CHANGE_USER_NAME_EXTRA_INFO = """
Critical Requirements:
1. Do not specify more than one constraint for the same field — 'name' — in a single request.

Examples:
- CORRECT: "Change user name to 'Muhammad Ali'"
- INCORRECT: "Change user name to name that does NOT contain 'Doe'"
- CORRECT: "Change user name to 'Emily Rose'"
- CORRECT: "Change user name to name that does NOT contain 'Evans'"
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
            "prompt": "Change user name to 'Muhammad Ali'.",
            "prompt_for_task_generation": "Change user name to 'Muhammad Ali'.",
        },
        {
            "prompt": "Change user name to name that contains 'Ali'.",
            "prompt_for_task_generation": "Change user name to name that contains 'Ali'.",
        },
        {
            "prompt": "Change user name to name that not contains 'Joy'.",
            "prompt_for_task_generation": "Change user name to name that not contains 'Joy'.",
        },
        {
            "prompt": "Change user name to name that not equals 'Ali'.",
            "prompt_for_task_generation": "Change user name to name that not equals 'Ali'..",
        },
        {
            "prompt": "Update display name to 'Aisha Khan'.",
            "prompt_for_task_generation": "Update display name to 'Aisha Khan'.",
        },
        {
            "prompt": "Set my user name to something that is not 'Guest User'.",
            "prompt_for_task_generation": "Set my user name to something that is not 'Guest User'.",
        },
    ],
)

ADD_CLIENT_USE_CASE = UseCase(
    name="ADD_CLIENT",
    description="The user adds a new client record.",
    event=AddClientEvent,
    event_source_code=AddClientEvent.get_source_code_of_class(),
    constraints_generator=generate_add_client_constraints,
    examples=[
        {
            "prompt": "Add a new client named 'Nova Labs' with status Active.",
            "prompt_for_task_generation": "Add a new client named 'Nova Labs' with status Active.",
        },
        {"prompt": "Add a new client named 'Orion Tech Solutions' with status Archived.", "prompt_for_task_generation": "Add a new client named 'Orion Tech Solutions' with status Archived."},
        {
            "prompt": "Add a new client named not equals 'Quantum Edge Industries' with status Pending.",
            "prompt_for_task_generation": "Add a new client named not equals 'Quantum Edge Industries' with status Pending.",
        },
        {"prompt": "Add a new client named contains 'Vertex' with status Inactive.", "prompt_for_task_generation": "Add a new client named contains 'Vertex' with status Inactive."},
    ],
)

DELETE_CLIENT_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of the client (e.g. name, email, status, number of matters).

Use natural language only. Do NOT use schema-style field names such as "name", "email", "status", "matters", or any names with underscores (_).

Always refer to fields using simple phrasing (e.g. client name, email, status, number of matters).

Identify the client using the provided visible field values (e.g. client name, email, status), then ask for the verify field value naturally.

Do NOT start questions with imperative phrasing like "Delete...", "Remove...", or "Open...".

For the matters field, ask naturally as a count:
- "How many matters does the client 'Acme Co.' have?"

Every generated question MUST include a subtle confirmation context at the end, such as "Please confirm the value before deletion" or "Confirm the value before deletion". This must appear at the end of the question.

Examples:
- "What is the email of the client 'Jessica Brown'? Please confirm the value before deletion."
- "What is the status of the client whose email is 'team@smithco.com'? Confirm the value before deletion."
- "How many matters does the client 'Acme Co.' have? Please confirm the value before deletion."
- "What is the name of the client with email 'jbrown@samplemail.com'? Confirm the value before deletion."

The output must be a single question asking only for the verify field value and must include the confirmation phrase at the end.
""".strip()

DELETE_CLIENT_USE_CASE = UseCase(
    name="DELETE_CLIENT",
    description="The user deletes a client record.",
    event=DeleteClientEvent,
    event_source_code=DeleteClientEvent.get_source_code_of_class(),
    constraints_generator=generate_delete_client_constraints,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=DELETE_CLIENT_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "Delete the client 'Nova Labs'.",
            "prompt_for_task_generation": "Delete the client 'Nova Labs'.",
        },
        {"prompt": "Delete the client named not equals 'Orion Tech Solutions'.", "prompt_for_task_generation": "Delete the client named not equals 'Orion Tech Solutions'."},
        {"prompt": "Delete the client named contains 'Quantum'.", "prompt_for_task_generation": "Delete the client named contains 'Quantum'."},
        {"prompt": "Delete the client not contains 'Partners'.", "prompt_for_task_generation": "Delete the client named not contains 'Partners'."},
    ],
)

FILTER_CLIENTS_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of the client (e.g. name, email, status, number of matters).

Use natural language only. Do NOT use schema-style field names such as "name", "email", "status", "matters", or any names with underscores (_).

Always refer to fields using simple phrasing (e.g. client name, email, status, number of matters).

Identify the client using the provided visible field values (e.g. client name, email, status), then ask for the verify field value naturally.

Do NOT start questions with imperative phrasing like "Filter...", "Show...", or "Open...".

For the matters field, ask naturally as a count:
- "How many matters does the client 'Acme Co.' have?"

Every generated question MUST include a subtle confirmation context at the end, such as "Please confirm the value before applying filter" or "Confirm the value before applying filter". This must appear at the end of the question.

Examples:
- "What is the email of the client 'Jessica Brown'? Please confirm the value before applying filter."
- "What is the status of the client whose email is 'team@smithco.com'? Confirm the value before applying filter."
- "How many matters does the client 'Acme Co.' have? Please confirm the value before applying filter."
- "What is the name of the client with email 'jbrown@samplemail.com'? Confirm the value before applying filter."

The output must be a single question asking only for the verify field value and must include the confirmation phrase at the end.
""".strip()

FILTER_CLIENTS_USE_CASE = UseCase(
    name="FILTER_CLIENTS",
    description="Filter clients by status, matter count, or search text.",
    event=FilterClientsEvent,
    event_source_code=FilterClientsEvent.get_source_code_of_class(),
    constraints_generator=generate_filter_clients_constraints,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=FILTER_CLIENTS_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "Filter clients to status Active with 3-4 matters.",
            "prompt_for_task_generation": "Filter clients to status Active with 3-4 matters.",
        },
        {"prompt": "Filter clients to status Pending with 1-2 matters.", "prompt_for_task_generation": "Filter clients to status Pending with 1-2 matters."},
        {"prompt": "Filter clients to status Inactive with 5+ matters.", "prompt_for_task_generation": "Filter clients to status Inactive with 5+ matters."},
    ],
)

HELP_VIEWED_USE_CASE = UseCase(
    name="HELP_VIEWED",
    description="The user opens the help/FAQ page.",
    event=HelpViewedEvent,
    event_source_code=HelpViewedEvent.get_source_code_of_class(),
    constraints_generator=None,
    examples=[
        {
            "prompt": "Open the help center.",
            "prompt_for_task_generation": "Open the help center.",
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
    ###############################################################################
    # NEWLY ADDED USE CASES
    ###############################################################################
    SEARCH_MATTER_USE_CASE,
    ADD_CLIENT_USE_CASE,
    DELETE_CLIENT_USE_CASE,
    FILTER_CLIENTS_USE_CASE,
    FILTER_MATTER_STATUS_USE_CASE,
    SORT_MATTER_BY_CREATED_AT_USE_CASE,
    UPDATE_MATTER_USE_CASE,
    VIEW_PENDING_EVENTS_USE_CASE,
    DOCUMENT_RENAMED_USE_CASE,
    LOG_EDITED_USE_CASE,
    BILLING_SEARCH_USE_CASE,
    HELP_VIEWED_USE_CASE,
]
