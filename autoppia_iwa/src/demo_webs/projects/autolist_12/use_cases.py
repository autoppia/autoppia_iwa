# autoppia_iwa/src/demo_webs/projects/autolist_12/use_cases.py

from ...classes import UseCase
from .events import (
    AddTaskClickedEvent,
    AddTeamClickedEvent,
    CancelTaskCreationEvent,
    CompleteTaskEvent,
    DeleteTaskEvent,
    EditTaskModalOpenedEvent,
    SelectDateForTaskEvent,
    SelectTaskPriorityEvent,
    TaskAddedEvent,
    TeamCreatedEvent,
    TeamMembersAddedEvent,
    TeamRoleAssignedEvent,
)
from .generation_functions import (
    generate_select_date_for_task_constraints,
    generate_select_task_priority_constraints,
    generate_task_constraints,
    generate_team_created_constraints,
    generate_team_members_added_constraints,
    generate_team_role_assigned_constraints,
)

###############################################################################
# ADD_TASK_CLICKED_USE_CASE
###############################################################################

ADD_TASK_CLICKED_INFO = """
CRITICAL REQUIREMENT: The prompt must clearly indicate the user's intent to start creating a new task.
Use phrases like "add a task", "create a new task", or "new task".
"""

ADD_TASK_CLICKED_USE_CASE = UseCase(
    name="ADD_TASK_CLICKED",
    description="Triggered when the user clicks the button to add a new task.",
    event=AddTaskClickedEvent,
    event_source_code=AddTaskClickedEvent.get_source_code_of_class(),
    constraints_generator=False,
    additional_prompt_info=ADD_TASK_CLICKED_INFO,
    examples=[
        {"prompt": "I want to add a new task.", "prompt_for_task_generation": "Add a new task."},
        {"prompt": "Create a task.", "prompt_for_task_generation": "Create a new task."},
        {"prompt": "Let's add something to my to-do list.", "prompt_for_task_generation": "Add a new task."},
        {"prompt": "New task button.", "prompt_for_task_generation": "Click the new task button."},
        {"prompt": "Time to add another item.", "prompt_for_task_generation": "Add a new item to the list."},
    ],
)

###############################################################################
# SELECT_DATE_FOR_TASK_USE_CASE
###############################################################################

SELECT_DATE_FOR_TASK_INFO = """
CRITICAL REQUIREMENT: The prompt must focus on selecting or changing a date for a task.
Use phrases like "set the date to", "pick a date", or "schedule it for".
"""

SELECT_DATE_FOR_TASK_USE_CASE = UseCase(
    name="SELECT_DATE_FOR_TASK",
    description="Triggered when the user selects a date for a task.",
    event=SelectDateForTaskEvent,
    event_source_code=SelectDateForTaskEvent.get_source_code_of_class(),
    constraints_generator=generate_select_date_for_task_constraints,
    additional_prompt_info=SELECT_DATE_FOR_TASK_INFO,
    examples=[
        {"prompt": "Set the date for this task to tomorrow.", "prompt_for_task_generation": "Set task date to tomorrow."},
        {"prompt": "I need to schedule this for June 5th.", "prompt_for_task_generation": "Set task date to June 5th."},
        {"prompt": "Pick next Friday as the due date.", "prompt_for_task_generation": "Set task date to next Friday."},
        {"prompt": "Let's make the due date the end of the month.", "prompt_for_task_generation": "Set task due date to the end of the month."},
        {"prompt": "Change the date to 2023-10-25.", "prompt_for_task_generation": "Change the task date to 2023-10-25."},
    ],
)

###############################################################################
# SELECT_TASK_PRIORITY_USE_CASE
###############################################################################

SELECT_TASK_PRIORITY_INFO = """
CRITICAL REQUIREMENT: The prompt must be about setting or changing the priority level of a task.
Use phrases like "set priority to", "make this high priority", or "change priority".
"""

SELECT_TASK_PRIORITY_USE_CASE = UseCase(
    name="SELECT_TASK_PRIORITY",
    description="Triggered when the user selects a priority for a task.",
    event=SelectTaskPriorityEvent,
    event_source_code=SelectTaskPriorityEvent.get_source_code_of_class(),
    constraints_generator=generate_select_task_priority_constraints,
    additional_prompt_info=SELECT_TASK_PRIORITY_INFO,
    examples=[
        {"prompt": "Set the priority to high.", "prompt_for_task_generation": "Set task priority to high."},
        {"prompt": "Make this a low priority task.", "prompt_for_task_generation": "Set task priority to low."},
        {"prompt": "Change the priority to medium.", "prompt_for_task_generation": "Change task priority to medium."},
        {"prompt": "This isn't urgent, set it to low priority.", "prompt_for_task_generation": "Set task priority to low."},
        {"prompt": "This is critical, mark it as high priority.", "prompt_for_task_generation": "Set task priority to high."},
    ],
)

###############################################################################
# TASK_ADDED_USE_CASE
###############################################################################

TASK_ADDED_INFO = """
CRITICAL REQUIREMENT: The prompt must confirm the creation or update of a task with its details.
Use phrases like "add task", "save task", or "confirm task" and include details like name, description, date, and priority.
"""

TASK_ADDED_USE_CASE = UseCase(
    name="TASK_ADDED",
    description="Triggered when a task is added or updated.",
    event=TaskAddedEvent,
    event_source_code=TaskAddedEvent.get_source_code_of_class(),
    constraints_generator=generate_task_constraints,
    additional_prompt_info=TASK_ADDED_INFO,
    examples=[
        {
            "prompt": "Add a task named 'Buy groceries' with description 'Milk, Bread, Eggs' for tomorrow, priority high.",
            "prompt_for_task_generation": "Add task '<name>' with description '<description>' for <date> with <priority> priority.",
        },
        {
            "prompt": "Save the task 'Finish report' for this Friday.",
            "prompt_for_task_generation": "Save task '<name>' for <date>.",
        },
        {
            "prompt": "Confirm the task: 'Call John', medium priority.",
            "prompt_for_task_generation": "Confirm task '<name>' with <priority> priority.",
        },
        {"prompt": "Update task 'Team Meeting' with description 'Discuss Q3 results'.", "prompt_for_task_generation": "Update task '<name>' with description '<description>'."},
        {"prompt": "Save new task: 'Book flights', no due date, low priority.", "prompt_for_task_generation": "Save task '<name>' with <priority> priority."},
    ],
)

###############################################################################
# CANCEL_TASK_CREATION_USE_CASE
###############################################################################

CANCEL_TASK_CREATION_INFO = """
CRITICAL REQUIREMENT: The prompt must clearly indicate the user's intent to cancel the task creation or editing process.
Use phrases like "cancel", "never mind", "don't save".
"""

CANCEL_TASK_CREATION_USE_CASE = UseCase(
    name="CANCEL_TASK_CREATION",
    description="Triggered when the user cancels task creation.",
    event=CancelTaskCreationEvent,
    event_source_code=CancelTaskCreationEvent.get_source_code_of_class(),
    constraints_generator=generate_task_constraints,
    additional_prompt_info=CANCEL_TASK_CREATION_INFO,
    examples=[
        {"prompt": "Cancel creating this task.", "prompt_for_task_generation": "Cancel task creation."},
        {"prompt": "Never mind, don't add it.", "prompt_for_task_generation": "Cancel task creation."},
        {"prompt": "Exit without saving.", "prompt_for_task_generation": "Cancel task creation."},
        {"prompt": "On second thought, let's not save this.", "prompt_for_task_generation": "Cancel task creation."},
        {"prompt": "Discard changes.", "prompt_for_task_generation": "Cancel task editing."},
    ],
)

###############################################################################
# EDIT_TASK_MODAL_OPENED_USE_CASE
###############################################################################

EDIT_TASK_MODAL_OPENED_INFO = """
CRITICAL REQUIREMENT: The prompt must indicate the user's intent to edit an existing task.
Use phrases like "edit the task", "I want to change this task", "open for editing".
"""

EDIT_TASK_MODAL_OPENED_USE_CASE = UseCase(
    name="EDIT_TASK_MODAL_OPENED",
    description="Triggered when the edit task modal is opened.",
    event=EditTaskModalOpenedEvent,
    event_source_code=EditTaskModalOpenedEvent.get_source_code_of_class(),
    constraints_generator=generate_task_constraints,
    additional_prompt_info=EDIT_TASK_MODAL_OPENED_INFO,
    examples=[
        {"prompt": "I need to edit the 'Buy groceries' task.", "prompt_for_task_generation": "Edit task '<name>'."},
        {"prompt": "Let me change the details for the 'Finish report' task.", "prompt_for_task_generation": "Edit task '<name>'."},
        {"prompt": "Open the 'Call John' task for editing.", "prompt_for_task_generation": "Edit task '<name>'."},
        {"prompt": "I want to modify the 'Plan vacation' task.", "prompt_for_task_generation": "Edit task '<name>'."},
        {"prompt": "Click the edit icon on the 'Pay bills' task.", "prompt_for_task_generation": "Edit task '<name>'."},
    ],
)

###############################################################################
# COMPLETE_TASK_USE_CASE
###############################################################################

COMPLETE_TASK_INFO = """
CRITICAL REQUIREMENT: The prompt must clearly indicate that a task is being marked as complete.
Use phrases like "mark as complete", "task done", "I finished this".
"""

COMPLETE_TASK_USE_CASE = UseCase(
    name="COMPLETE_TASK",
    description="Triggered when a task is marked as complete.",
    event=CompleteTaskEvent,
    event_source_code=CompleteTaskEvent.get_source_code_of_class(),
    constraints_generator=generate_task_constraints,
    additional_prompt_info=COMPLETE_TASK_INFO,
    examples=[
        {"prompt": "Mark 'Buy groceries' as complete.", "prompt_for_task_generation": "Mark task '<name>' as complete."},
        {"prompt": "The 'Finish report' task is done.", "prompt_for_task_generation": "Mark task '<name>' as complete."},
        {"prompt": "I've finished calling John.", "prompt_for_task_generation": "Mark task '<name>' as complete."},
        {"prompt": "Check off 'Send email to client'.", "prompt_for_task_generation": "Mark task '<name>' as complete."},
        {"prompt": "This one is finished.", "prompt_for_task_generation": "Mark the current task as complete."},
    ],
)

###############################################################################
# DELETE_TASK_USE_CASE
###############################################################################

DELETE_TASK_INFO = """
CRITICAL REQUIREMENT: The prompt must clearly indicate the user's intent to delete a task permanently.
Use phrases like "delete this task", "remove this task", "get rid of this".
"""

DELETE_TASK_USE_CASE = UseCase(
    name="DELETE_TASK",
    description="Triggered when a task is deleted.",
    event=DeleteTaskEvent,
    event_source_code=DeleteTaskEvent.get_source_code_of_class(),
    constraints_generator=generate_task_constraints,
    additional_prompt_info=DELETE_TASK_INFO,
    examples=[
        {"prompt": "Delete the 'Buy groceries' task.", "prompt_for_task_generation": "Delete task '<name>'."},
        {"prompt": "Remove 'Finish report' from my list.", "prompt_for_task_generation": "Delete task '<name>'."},
        {"prompt": "Get rid of the 'Call John' task.", "prompt_for_task_generation": "Delete task '<name>'."},
        {"prompt": "I don't need this task anymore, remove it.", "prompt_for_task_generation": "Delete task '<name>'."},
        {"prompt": "Trash the 'Old project notes' task.", "prompt_for_task_generation": "Delete task '<name>'."},
    ],
)

###############################################################################
# ADD_TEAM_CLICKED_USE_CASE
###############################################################################

ADD_TEAM_CLICKED_INFO = """
CRITICAL REQUIREMENT: The prompt must clearly indicate the user's intent to start creating a new team.
Use phrases like "add a team", "create a new team", or "new team".
"""

ADD_TEAM_CLICKED_USE_CASE = UseCase(
    name="ADD_TEAM_CLICKED",
    description="Triggered when the user clicks the button to add a new team.",
    event=AddTeamClickedEvent,
    event_source_code=AddTeamClickedEvent.get_source_code_of_class(),
    constraints_generator=False,
    additional_prompt_info=ADD_TEAM_CLICKED_INFO,
    examples=[
        {"prompt": "I want to add a new team.", "prompt_for_task_generation": "Add a new team."},
        {"prompt": "Create a team.", "prompt_for_task_generation": "Create a new team."},
        {"prompt": "Let's make a new team.", "prompt_for_task_generation": "Create a new team."},
    ],
)

###############################################################################
# TEAM_MEMBERS_ADDED_USE_CASE
###############################################################################

TEAM_MEMBERS_ADDED_INFO = """
CRITICAL REQUIREMENT: The prompt must be about adding members to a team.
Use phrases like "add members", "invite to team", and list the member identifiers (e.g., emails).
"""

TEAM_MEMBERS_ADDED_USE_CASE = UseCase(
    name="TEAM_MEMBERS_ADDED",
    description="Triggered when team members are added.",
    event=TeamMembersAddedEvent,
    event_source_code=TeamMembersAddedEvent.get_source_code_of_class(),
    constraints_generator=generate_team_members_added_constraints,
    additional_prompt_info=TEAM_MEMBERS_ADDED_INFO,
    examples=[
        {"prompt": "Add jane@example.com to the team.", "prompt_for_task_generation": "Add member '<email>' to the team."},
        {"prompt": "Invite alice@example.com and michael@example.com.", "prompt_for_task_generation": "Invite members '<email1>' and '<email2>' to the team."},
        {"prompt": "Add these members: jane@example.com, alice@example.com", "prompt_for_task_generation": "Add members '<email1>', '<email2>' to the team."},
    ],
)

###############################################################################
# TEAM_ROLE_ASSIGNED_USE_CASE
###############################################################################

TEAM_ROLE_ASSIGNED_INFO = """
CRITICAL REQUIREMENT: The prompt must be about assigning a specific role to a team member.
Use phrases like "assign role", "make [member] a [role]", "set role for".
"""

TEAM_ROLE_ASSIGNED_USE_CASE = UseCase(
    name="TEAM_ROLE_ASSIGNED",
    description="Triggered when a role is assigned to a team member.",
    event=TeamRoleAssignedEvent,
    event_source_code=TeamRoleAssignedEvent.get_source_code_of_class(),
    constraints_generator=generate_team_role_assigned_constraints,
    additional_prompt_info=TEAM_ROLE_ASSIGNED_INFO,
    examples=[
        {"prompt": "Assign the developer role to jane@example.com.", "prompt_for_task_generation": "Assign role '<role>' to member '<email>'."},
        {"prompt": "Make alice@example.com a tester.", "prompt_for_task_generation": "Make member '<email>' a '<role>'."},
        {"prompt": "Set the role for michael@example.com to designer.", "prompt_for_task_generation": "Set role for member '<email>' to '<role>'."},
    ],
)

###############################################################################
# TEAM_CREATED_USE_CASE
###############################################################################

TEAM_CREATED_INFO = """
CRITICAL REQUIREMENT: The prompt must confirm the creation of a team with a specific name.
Use phrases like "create team", "name the team", "confirm team creation".
"""

TEAM_CREATED_USE_CASE = UseCase(
    name="TEAM_CREATED",
    description="Triggered when a team is created.",
    event=TeamCreatedEvent,
    event_source_code=TeamCreatedEvent.get_source_code_of_class(),
    constraints_generator=generate_team_created_constraints,
    additional_prompt_info=TEAM_CREATED_INFO,
    examples=[
        {"prompt": "Create the team and name it 'Gul Shair'.", "prompt_for_task_generation": "Create team with name '<team_name>'."},
        {"prompt": "Let's name the team 'Project Phoenix'.", "prompt_for_task_generation": "Name the team '<team_name>'."},
        {"prompt": "Confirm team creation with the name 'Marketing'.", "prompt_for_task_generation": "Create team with name '<team_name>'."},
    ],
)

ALL_USE_CASES = [
    ADD_TASK_CLICKED_USE_CASE,
    SELECT_DATE_FOR_TASK_USE_CASE,
    SELECT_TASK_PRIORITY_USE_CASE,
    TASK_ADDED_USE_CASE,
    CANCEL_TASK_CREATION_USE_CASE,
    EDIT_TASK_MODAL_OPENED_USE_CASE,
    COMPLETE_TASK_USE_CASE,
    DELETE_TASK_USE_CASE,
    ADD_TEAM_CLICKED_USE_CASE,
    TEAM_MEMBERS_ADDED_USE_CASE,
    TEAM_ROLE_ASSIGNED_USE_CASE,
    TEAM_CREATED_USE_CASE,
]
