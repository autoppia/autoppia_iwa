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
    generate_add_task_clicked_constraints,
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
CRITICAL REQUIREMENT:
1. The prompt must clearly indicate the user's intent to start creating a new task.
Use phrases like "add a task", "create a new task", or "new task".
2. The prompt should NOT contain any details or constraints about the task itself (e.g., name, description, date, priority). This use case is solely for clicking the button to open the task creation form.
"""

ADD_TASK_CLICKED_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a task list in the add task context (e.g., name, description, due date, priority, number of completed tasks, number of pending tasks).

Use natural language only. Do NOT use schema-style field names such as "name", "description", "due_date", "priority", "completed_task", "pending_task" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., task list name, description, due date, priority number, number of completed tasks, number of pending tasks).

Include all question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Add...", "Create...", or "Insert...".

Always end the question naturally with "so I can open a modal to add a new task."

SPECIAL RULES:
- If the verify field is completed_task or pending_task, ask only for the number of completed or pending tasks.
- Do NOT include completed tasks or pending tasks in examples for other verify fields.

For example, if the verify field is 'completed_task', format the question naturally:
- "Can you tell me the number of completed tasks, so I can open a modal to add a new task?"

For example, if the verify field is 'pending_task', format the question naturally:
- "Can you tell me the number of pending tasks, so I can open a modal to add a new task?"

Examples:
- "Can you tell me the description of the task whose name 'Shopping List', due date is '20 Jan 2025' and priority number is '4', so I can open a modal to add a new task?"
- "Can you tell me the due date of the task whose name 'Project Tasks', description is 'Complete project modules' and priority number is '2', so I can open a modal to add a new task?"
- "Can you tell me the priority number of the task whose name 'Fitness Plan', description is 'Workout schedule' and due date is '20 Jan 2025', so I can open a modal to add a new task?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only non-verify fields for identification.
- Always include all question fields with values in the question for precise identification.
- Do not include completed_task or pending_task in identification when they are not the verify field.

The output must be a single question asking only for the verify field value.
""".strip()

ADD_TASK_CLICKED_USE_CASE = UseCase(
    name="AUTOLIST_ADD_TASK_CLICKED",
    description="Triggered when the user clicks the button to add a new task.",
    event=AddTaskClickedEvent,
    event_source_code=AddTaskClickedEvent.get_source_code_of_class(),
    constraints_generator=generate_add_task_clicked_constraints,
    additional_prompt_info=ADD_TASK_CLICKED_INFO,
    additional_prompt_info_for_data_extraction_task=ADD_TASK_CLICKED_DATA_EXTRACTION_PROMPT_INFO,
    supports_data_extraction=True,
    examples=[
        {"prompt": "Click on the Add Task button to start.", "prompt_for_task_generation": "Click on the Add Task button to start."},
        {"prompt": "Please click the Add Task button.", "prompt_for_task_generation": "Please click the Add Task button."},
        {"prompt": "To begin, click the Add Task button.", "prompt_for_task_generation": "To begin, click the Add Task button."},
        {"prompt": "Start by clicking the Add Task button.", "prompt_for_task_generation": "Start by clicking the Add Task button."},
        {"prompt": "Click Add Task to initialize task creation.", "prompt_for_task_generation": "Click Add Task to initialize task creation."},
    ],
)

###############################################################################
# SELECT_DATE_FOR_TASK_USE_CASE
###############################################################################

SELECT_DATE_FOR_TASK_INFO = """
CRITICAL REQUIREMENT: The prompt must focus on selecting or changing a date for a task.
Use phrases like "set the date to", "pick a date", or "schedule it for".
"""

SELECT_DATE_FOR_TASK_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a task in the select date for task context (e.g., name, description, due date, priority).

Use natural language only. Do NOT use schema-style field names such as "name", "description", "due_date", "priority" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., task name, description, due date, priority number).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Select...", "Choose...", or "Pick...".

Always end the question naturally with "so I can edit its due date."

For example, if the verify field is 'due_date', format the question naturally:
- "Can you tell me the due date of the task whose name is 'Shopping List' and priority number is '4', so I can edit its due date?"

Examples:
- "Can you tell me the description of the task whose name is 'Shopping List', due date is '20 Jan 2025' and priority is '4', so I can edit its due date?"
- "Can you tell me the due date of the task whose name is 'Project Tasks', description is 'Complete project modules' and priority is '2', so I can edit its due date?"
- "Can you tell me the priority number of the task whose name is 'Fitness Plan', description is 'Workout schedule' and due date is '20 Jan 2025', so I can edit its due date?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
""".strip()

SELECT_DATE_FOR_TASK_USE_CASE = UseCase(
    name="AUTOLIST_SELECT_DATE_FOR_TASK",
    description="Triggered when the user selects a date for a task.",
    event=SelectDateForTaskEvent,
    event_source_code=SelectDateForTaskEvent.get_source_code_of_class(),
    constraints_generator=generate_select_date_for_task_constraints,
    additional_prompt_info=SELECT_DATE_FOR_TASK_INFO,
    additional_prompt_info_for_data_extraction_task=SELECT_DATE_FOR_TASK_DATA_EXTRACTION_PROMPT_INFO,
    supports_data_extraction=True,
    examples=[
        {"prompt": "Set the date for this task to tomorrow.", "prompt_for_task_generation": "Set the date for this task to tomorrow."},
        {"prompt": "I need to schedule this for June 5th.", "prompt_for_task_generation": "I need to schedule this for June 5th."},
        {"prompt": "Pick next Friday as the due date.", "prompt_for_task_generation": "Pick next Friday as the due date."},
        {"prompt": "Let's make the due date the end of the month.", "prompt_for_task_generation": "Let's make the due date the end of the month."},
        {"prompt": "Change the date to 2023-10-25.", "prompt_for_task_generation": "Change the date to 2023-10-25."},
    ],
)

###############################################################################
# SELECT_TASK_PRIORITY_USE_CASE
###############################################################################

SELECT_TASK_PRIORITY_INFO = """
CRITICAL REQUIREMENT:
1. The prompt must focus on setting or changing the priority level.
Use clear phrases such as "set priority to", "make this <priority_level> priority", or "change priority" ....
2. Do not mention the same constraint more than once in the prompt.
Example:
CORRECT: "Change the priority to 'Low'."
INCORRECT: "Change the priority to 'Low' where the label is equal to 'Low'."
""".strip()

SELECT_TASK_PRIORITY_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which is the priority of a task in the select task priority context.

Use natural language only. Do NOT use schema-style field names such as "name", "description", "due_date", "priority" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., task name, description, due date, priority number).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the priority.

Do NOT start questions with imperative phrasing like "Select...", "Choose...", or "Pick...".

Always end the question naturally with "so I can give the task an appropriate priority."

For example, format the question naturally:
- "Can you tell me the priority number of the task whose name is 'Shopping List', description is 'Buy groceries', and due date is '20 Jan 2025', so I can give the task an appropriate priority?"

Examples:
- "Can you tell me the priority number of the task whose name is 'Shopping List', description is 'Buy groceries', and due date is '20 Jan 2025', so I can give the task an appropriate priority?"
- "Can you tell me the priority number of the task whose name is 'Project Tasks', description is 'Complete project modules', and due date is '15 Feb 2025', so I can give the task an appropriate priority?"
- "Can you tell me the priority number of the task whose name is 'Fitness Plan', description is 'Workout schedule', and due date is '10 Mar 2025', so I can give the task an appropriate priority?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value (priority) itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the priority.
""".strip()

SELECT_TASK_PRIORITY_USE_CASE = UseCase(
    name="AUTOLIST_SELECT_TASK_PRIORITY",
    description="Triggered when the user selects a priority for a task.",
    event=SelectTaskPriorityEvent,
    event_source_code=SelectTaskPriorityEvent.get_source_code_of_class(),
    constraints_generator=generate_select_task_priority_constraints,
    additional_prompt_info=SELECT_TASK_PRIORITY_INFO,
    additional_prompt_info_for_data_extraction_task=SELECT_TASK_PRIORITY_DATA_EXTRACTION_PROMPT_INFO,
    supports_data_extraction=True,
    examples=[
        {"prompt": "Set the priority to high.", "prompt_for_task_generation": "Set the priority to high."},
        {"prompt": "Make this a low priority task.", "prompt_for_task_generation": "Make this a low priority task."},
        {"prompt": "Change the priority to medium.", "prompt_for_task_generation": "Change the priority to medium."},
        {"prompt": "This isn't urgent, set it to low priority.", "prompt_for_task_generation": "This isn't urgent, set it to low priority."},
        {"prompt": "This is critical, mark it as high priority.", "prompt_for_task_generation": "This is critical, mark it as high priority."},
    ],
)

###############################################################################
# TASK_ADDED_USE_CASE
###############################################################################

TASK_ADDED_INFO = """
CRITICAL REQUIREMENTS:
1. The request must start with one of the following: "Add a task ..."
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
4. Always use the exact field names, operators, and the complete values provided in the constraints.
5. You must preserve all special characters ((, ), ', ,, ", -, etc.) exactly as they appear in the value and must follow the below requirements:
    - Do not remove special characters ((, ), ', ,, ", -, etc.).
    - Do not replace special characters ((, ), ', ,, ", -, etc.).
    - Do not shorten, split, or partially match the values. For example, if the constraint is contains 'on re' OR 'ar on product', then the generated prompt must also say contains 'on re' OR 'ar on product' exactly, not just 're' OR 'ar'.
    - Use the full string exactly as provided.
6. Pay attention to the constraints:
Example:
constraint:
{"field": "name", "operator": "equals", "value": "Build CI/CD pipeline"},
{"field": "description", "operator": "equals", "value": "Write a detailed technical specification document for the upcoming 'Project X'."},
{"field": "date", "operator": "equals", "value": "2025-09-27"},
{"field": "priority", "operator": "equals", "value": "High"},

prompt:
CORRECT: 'Add a task whose name equals 'Build CI/CD pipeline' and description equals 'Write a detailed technical specification document for the upcoming 'Project X'' and date equals '2025-09-27' and priority equals 'High'.'
INCORRECT: 'Add a task name "Build CI/CD pipeline", date '2025-09-27'.'
""".strip()

TASK_ADDED_USE_CASE = UseCase(
    name="AUTOLIST_TASK_ADDED",
    description="Triggered when a task is added or updated.",
    event=TaskAddedEvent,
    event_source_code=TaskAddedEvent.get_source_code_of_class(),
    constraints_generator=generate_task_constraints,
    additional_prompt_info=TASK_ADDED_INFO,
    examples=[
        {
            "prompt": "Add a task whose name equals 'Design new homepage mockup'.",
            "prompt_for_task_generation": "Add a task whose name equals 'Design new homepage mockup'.",
        },
        {
            "prompt": "Add a task whose description equals 'Build a detailed financial projection for the proposed 'Project Titan'.' and date equals '2025-09-28'.",
            "prompt_for_task_generation": "Add a task whose description equals 'Build a detailed financial projection for the proposed 'Project Titan'.' and date equals '2025-09-28'.",
        },
        {
            "prompt": "Add a task whose name equals 'Update API documentation' and priority equals 'Low'.",
            "prompt_for_task_generation": "Add a task whose name equals 'Update API documentation' and priority equals 'Low'.",
        },
        {
            "prompt": "Add a task whose name equals 'Develop user profile page' and description equals 'Build the frontend and backend for the user's editable profile page' and priority equals 'Medium'.",
            "prompt_for_task_generation": "Add a task whose name equals 'Develop user profile page' and description equals 'Build the frontend and backend for the user's editable profile page' and priority equals 'Medium'.",
        },
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
    name="AUTOLIST_CANCEL_TASK_CREATION",
    description="Triggered when the user cancels task creation.",
    event=CancelTaskCreationEvent,
    event_source_code=CancelTaskCreationEvent.get_source_code_of_class(),
    constraints_generator=generate_task_constraints,
    additional_prompt_info=CANCEL_TASK_CREATION_INFO,
    examples=[
        {"prompt": "Cancel creating this task.", "prompt_for_task_generation": "Cancel creating this task."},
        {"prompt": "Never mind, don't add it.", "prompt_for_task_generation": "Never mind, don't add it."},
        {"prompt": "Exit without saving.", "prompt_for_task_generation": "Exit without saving."},
        {"prompt": "On second thought, let's not save this.", "prompt_for_task_generation": "On second thought, let's not save this."},
        {"prompt": "Discard changes.", "prompt_for_task_generation": "Discard changes."},
    ],
)

###############################################################################
# EDIT_TASK_MODAL_OPENED_USE_CASE
###############################################################################

EDIT_TASK_MODAL_OPENED_INFO = """
CRITICAL REQUIREMENTS:
1. The request must start with one of the following: "Edit task modal open ..."
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
4. Always use the exact field names, operators, and the complete values provided in the constraints.
5. You must preserve all special characters ((, ), ', ,, ", -, etc.) exactly as they appear in the value and must follow the below requirements:
    - Do not remove special characters ((, ), ', ,, ", -, etc.).
    - Do not replace special characters ((, ), ', ,, ", -, etc.).
    - Do not shorten, split, or partially match the values. For example, if the constraint is contains 'on re' OR 'ar on product', then the generated prompt must also say contains 'on re' OR 'ar on product' exactly, not just 're' OR 'ar'.
    - Use the full string exactly as provided.
6. Pay attention to the constraints:
Example:
constraint:
{"field": "name", "operator": "equals", "value": "Build CI/CD pipeline"},
{"field": "description", "operator": "equals", "value": "Write a detailed technical specification document for the upcoming 'Project X'."},
{"field": "date", "operator": "equals", "value": "2025-09-27"},
{"field": "priority", "operator": "equals", "value": "High"},

prompt:
CORRECT: 'Edit task modal open whose name equals 'Build CI/CD pipeline' and description equals 'Write a detailed technical specification document for the upcoming 'Project X'' and date equals '2025-09-27' and priority equals 'High'.'
INCORRECT: 'Edit task modal open name "Build CI/CD pipeline", date '2025-09-27'.'
""".strip()

EDIT_TASK_MODAL_OPENED_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a task in the edit task modal context (e.g., name, description, due date, priority).

Use natural language only. Do NOT use schema-style field names such as "name", "description", "due_date", "priority" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., task name, description, due date, priority number).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Edit...", "Update...", or "Modify...".

Always end the question naturally with "so I can edit it."

For example, if the verify field is 'description', format the question naturally:
- "Can you tell me the description of the task whose name is 'Shopping List', due date is '20 Jan 2025' and priority number is '4', so I can edit it?"

Examples:
- "Can you tell me the description of the task whose name is 'Project Tasks', due date is '15 Feb 2025' and priority is '2', so I can edit it?"
- "Can you tell me the due date of the task whose name is 'Fitness Plan', description is 'Workout schedule' and priority is '3', so I can edit it?"
- "Can you tell me the priority number of the task whose name is 'Daily Routine', description is 'Morning tasks' and due date is '10 Mar 2025', so I can edit it?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
""".strip()


EDIT_TASK_MODAL_OPENED_USE_CASE = UseCase(
    name="AUTOLIST_EDIT_TASK_MODAL_OPENED",
    description="Triggered when the edit task modal is opened.",
    event=EditTaskModalOpenedEvent,
    event_source_code=EditTaskModalOpenedEvent.get_source_code_of_class(),
    constraints_generator=generate_task_constraints,
    additional_prompt_info=EDIT_TASK_MODAL_OPENED_INFO,
    additional_prompt_info_for_data_extraction_task=EDIT_TASK_MODAL_OPENED_DATA_EXTRACTION_PROMPT_INFO,
    supports_data_extraction=True,
    examples=[
        {"prompt": "Edit task modal open whose name equals 'Design new homepage mockup'.", "prompt_for_task_generation": "Edit task modal open whose name equals 'Design new homepage mockup'."},
        {
            "prompt": "Edit task modal open whose description equals 'Build a detailed financial projection for the proposed 'Project Titan'.' and date equals '2025-09-28'.",
            "prompt_for_task_generation": "Edit task modal open whose description equals 'Build a detailed financial projection for the proposed 'Project Titan'.' and date equals '2025-09-28'.",
        },
        {
            "prompt": "Edit task modal open whose name equals 'Update API documentation' and priority equals 'Low'.",
            "prompt_for_task_generation": "Edit task modal open whose name equals 'Update API documentation' and priority equals 'Low'.",
        },
        {
            "prompt": "Edit task modal open whose name equals 'Develop user profile page' and description equals 'Build the frontend and backend for the user's editable profile page' and priority equals 'Medium'.",
            "prompt_for_task_generation": "Edit task modal open whose name equals 'Develop user profile page' and description equals 'Build the frontend and backend for the user's editable profile page' and priority equals 'Medium'.",
        },
    ],
)

###############################################################################
# COMPLETE_TASK_USE_CASE
###############################################################################

COMPLETE_TASK_INFO = """
CRITICAL REQUIREMENTS:
1. The request must start with one of the following: "Complete task ..."
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
4. Always use the exact field names, operators, and the complete values provided in the constraints.
5. You must preserve all special characters ((, ), ', ,, ", -, etc.) exactly as they appear in the value and must follow the below requirements:
    - Do not remove special characters ((, ), ', ,, ", -, etc.).
    - Do not replace special characters ((, ), ', ,, ", -, etc.).
    - Do not shorten, split, or partially match the values. For example, if the constraint is contains 'on re' OR 'ar on product', then the generated prompt must also say contains 'on re' OR 'ar on product' exactly, not just 're' OR 'ar'.
    - Use the full string exactly as provided.
6. Pay attention to the constraints:
Example:
constraint:
{"field": "name", "operator": "equals", "value": "Build CI/CD pipeline"},
{"field": "description", "operator": "equals", "value": "Write a detailed technical specification document for the upcoming 'Project X'."},
{"field": "date", "operator": "equals", "value": "2025-09-27"},
{"field": "priority", "operator": "equals", "value": "High"},

prompt:
CORRECT: 'Complete task whose name equals 'Build CI/CD pipeline' and description equals 'Write a detailed technical specification document for the upcoming 'Project X'' and date equals '2025-09-27' and priority equals 'High'.'
INCORRECT: 'Complete task name "Build CI/CD pipeline", date '2025-09-27'.'
""".strip()

COMPLETE_TASK_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a task in the complete task context (e.g., name, description, due date, priority).

Use natural language only. Do NOT use schema-style field names such as "name", "description", "due_date", "priority" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., task name, description, due date, priority number).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Complete...", "Mark...", or "Finish...".

Always end the question naturally with "so I can mark the task as completed."

For example, if the verify field is 'description', format the question naturally:
- "Can you tell me the description of the task whose name is 'Shopping List', due date is '20 Jan 2025' and priority number is '4', so I can mark the task as completed?"

Examples:
- "Can you tell me the description of the task whose name is 'Project Tasks', due date is '15 Feb 2025' and priority number is '2', so I can mark the task as completed?"
- "Can you tell me the due date of the task whose name is 'Fitness Plan', description is 'Workout schedule' and priority number is '3', so I can mark the task as completed?"
- "Can you tell me the priority number of the task whose name is 'Daily Routine', description is 'Morning tasks' and due date is '10 Mar 2025', so I can mark the task as completed?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
""".strip()


COMPLETE_TASK_USE_CASE = UseCase(
    name="AUTOLIST_COMPLETE_TASK",
    description="Triggered when a task is marked as complete.",
    event=CompleteTaskEvent,
    event_source_code=CompleteTaskEvent.get_source_code_of_class(),
    constraints_generator=generate_task_constraints,
    additional_prompt_info=COMPLETE_TASK_INFO,
    additional_prompt_info_for_data_extraction_task=COMPLETE_TASK_DATA_EXTRACTION_PROMPT_INFO,
    supports_data_extraction=True,
    examples=[
        {"prompt": "Complete task whose name equals 'Implement user authentication'.", "prompt_for_task_generation": "Complete task whose name equals 'Implement user authentication'."},
        {
            "prompt": "Complete task whose description equals 'Set up backend and frontend for user registration and login using JWT.' and date equals '2025-09-28'.",
            "prompt_for_task_generation": "Complete task whose description equals 'Set up backend and frontend for user registration and login using JWT.' and date equals '2025-09-28'.",
        },
        {
            "prompt": "Complete task whose name equals 'Draft Q3 marketing report' and priority equals 'Low'.",
            "prompt_for_task_generation": "Complete task whose name equals 'Draft Q3 marketing report' and priority equals 'Low'.",
        },
        {
            "prompt": "Complete task whose name equals 'Develop user profile page' and description equals 'Build the frontend and backend for the user's editable profile page' and priority equals 'Medium'.",
            "prompt_for_task_generation": "Complete task whose name equals 'Develop user profile page' and description equals 'Build the frontend and backend for the user's editable profile page' and priority equals 'Medium'.",
        },
    ],
)

###############################################################################
# DELETE_TASK_USE_CASE
###############################################################################

DELETE_TASK_INFO = """
CRITICAL REQUIREMENTS:
1. The request must start with one of the following: "Delete task ..."
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
4. Always use the exact field names, operators, and the complete values provided in the constraints.
5. You must preserve all special characters ((, ), ', ,, ", -, etc.) exactly as they appear in the value and must follow the below requirements:
    - Do not remove special characters ((, ), ', ,, ", -, etc.).
    - Do not replace special characters ((, ), ', ,, ", -, etc.).
    - Do not shorten, split, or partially match the values. For example, if the constraint is contains 'on re' OR 'ar on product', then the generated prompt must also say contains 'on re' OR 'ar on product' exactly, not just 're' OR 'ar'.
    - Use the full string exactly as provided.
6. Pay attention to the constraints:
Example:
constraint:
{"field": "name", "operator": "equals", "value": "Build CI/CD pipeline"},
{"field": "description", "operator": "equals", "value": "Write a detailed technical specification document for the upcoming 'Project X'."},
{"field": "date", "operator": "equals", "value": "2025-09-27"},
{"field": "priority", "operator": "equals", "value": "High"},

prompt:
CORRECT: 'Delete task whose name equals 'Build CI/CD pipeline' and description equals 'Write a detailed technical specification document for the upcoming 'Project X'' and date equals '2025-09-27' and priority equals 'High'.'
INCORRECT: 'Delete task name "Build CI/CD pipeline", date '2025-09-27'.'
""".strip()

DELETE_TASK_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a task in the delete task context (e.g., name, description, due date, priority).

Use natural language only. Do NOT use schema-style field names such as "name", "description", "due_date", "priority" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., task name, description, due date, priority number).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Delete...", "Remove...", or "Clear...".

Always end the question naturally with "so I can delete the task."

For example, if the verify field is 'description', format the question naturally:
- "Can you tell me the description of the task whose name is 'Shopping List', due date is '20 Jan 2025' and priority number is '4', so I can delete the task?"

Examples:
- "Can you tell me the description of the task whose name is 'Project Tasks', due date is '15 Feb 2025' and priority number is '2', so I can delete the task?"
- "Can you tell me the due date of the task whose name is 'Fitness Plan', description is 'Workout schedule' and priority number is '3', so I can delete the task?"
- "Can you tell me the priority number of the task whose name is 'Daily Routine', description is 'Morning tasks' and due date is '10 Mar 2025', so I can delete the task?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
""".strip()


DELETE_TASK_USE_CASE = UseCase(
    name="AUTOLIST_DELETE_TASK",
    description="Triggered when a task is deleted.",
    event=DeleteTaskEvent,
    event_source_code=DeleteTaskEvent.get_source_code_of_class(),
    constraints_generator=generate_task_constraints,
    additional_prompt_info=DELETE_TASK_INFO,
    additional_prompt_info_for_data_extraction_task=DELETE_TASK_DATA_EXTRACTION_PROMPT_INFO,
    supports_data_extraction=True,
    examples=[
        {"prompt": "Delete task whose name equals 'Fix login page CSS bug' from my list.", "prompt_for_task_generation": "Delete task whose name equals 'Fix login page CSS bug' from my list."},
        {"prompt": "Delete task whose name not equals 'Finish report' from my list.", "prompt_for_task_generation": "Delete task whose name not equals 'Finish report' from my list."},
        {
            "prompt": "Delete task whose description equals 'Set up backend and frontend for user registration and login using JWT.' and date equals '2025-09-28'.",
            "prompt_for_task_generation": "Delete task whose description equals 'Set up backend and frontend for user registration and login using JWT.' and date equals '2025-09-28'.",
        },
        {
            "prompt": "Delete task whose name equals 'Develop user profile page' and description equals 'Build the frontend and backend for the user's editable profile page' and priority equals 'Medium'.",
            "prompt_for_task_generation": "Delete task whose name equals 'Develop user profile page' and description equals 'Build the frontend and backend for the user's editable profile page' and priority equals 'Medium'.",
        },
    ],
)

###############################################################################
# ADD_TEAM_CLICKED_USE_CASE
###############################################################################

ADD_TEAM_CLICKED_INFO = """
CRITICAL REQUIREMENT:
1. The prompt must clearly indicate the user's intent to start creating a new team.
Use phrases like "add a team", "create a new team", or "new team".
2. The prompt should NOT contain any details or constraints about the team itself (e.g., team name, members, roles). This use case is solely for clicking the button to open the team creation form.
"""

ADD_TEAM_CLICKED_USE_CASE = UseCase(
    name="AUTOLIST_ADD_TEAM_CLICKED",
    description="Triggered when the user clicks the button to add a new team.",
    event=AddTeamClickedEvent,
    event_source_code=AddTeamClickedEvent.get_source_code_of_class(),
    constraints_generator=False,
    additional_prompt_info=ADD_TEAM_CLICKED_INFO,
    examples=[
        {"prompt": "Click on the Add Team button to start.", "prompt_for_task_generation": "Click on the Add Team button to start."},
        {"prompt": "Please click the Add Team button.", "prompt_for_task_generation": "Please click the Add Team button."},
        {"prompt": "To begin, click the Add Team button.", "prompt_for_task_generation": "To begin, click the Add Team button."},
        {"prompt": "Start by clicking the Add Team button.", "prompt_for_task_generation": "Start by clicking the Add Team button."},
        {"prompt": "Click Add Team to initialize team creation.", "prompt_for_task_generation": "Click Add Team to initialize team creation."},
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
    name="AUTOLIST_TEAM_MEMBERS_ADDED",
    description="Triggered when team members are added.",
    event=TeamMembersAddedEvent,
    event_source_code=TeamMembersAddedEvent.get_source_code_of_class(),
    constraints_generator=generate_team_members_added_constraints,
    additional_prompt_info=TEAM_MEMBERS_ADDED_INFO,
    examples=[
        {"prompt": "Add jane@example.com to the team.", "prompt_for_task_generation": "Add jane@example.com to the team."},
        {"prompt": "Invite alice@example.com and michael@example.com.", "prompt_for_task_generation": "Invite alice@example.com and michael@example.com."},
        {"prompt": "Add these members: jane@example.com, alice@example.com", "prompt_for_task_generation": "Add these members: jane@example.com, alice@example.com"},
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
    name="AUTOLIST_TEAM_ROLE_ASSIGNED",
    description="Triggered when a role is assigned to a team member.",
    event=TeamRoleAssignedEvent,
    event_source_code=TeamRoleAssignedEvent.get_source_code_of_class(),
    constraints_generator=generate_team_role_assigned_constraints,
    additional_prompt_info=TEAM_ROLE_ASSIGNED_INFO,
    examples=[
        {"prompt": "Assign the developer role to jane@example.com.", "prompt_for_task_generation": "Assign the developer role to jane@example.com."},
        {"prompt": "Make alice@example.com a tester.", "prompt_for_task_generation": "Make alice@example.com a tester."},
        {"prompt": "Set the role for michael@example.com to designer.", "prompt_for_task_generation": "Set the role for michael@example.com to designer."},
    ],
)

###############################################################################
# TEAM_CREATED_USE_CASE
###############################################################################

TEAM_CREATED_INFO = """
CRITICAL REQUIREMENTS:
1. The request must start with one of the following: "Create a team ..."
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
4. Always use the exact field names, operators, and the complete values provided in the constraints.
5. You must preserve all special characters ((, ), ', ,, ", -, etc.) exactly as they appear in the value and must follow the below requirements:
    - Do not remove special characters ((, ), ', ,, ", -, etc.).
    - Do not replace special characters ((, ), ', ,, ", -, etc.).
    - Do not shorten, split, or partially match the values. For example, if the constraint is contains 'on re' OR 'ar on product', then the generated prompt must also say contains 'on re' OR 'ar on product' exactly, not just 're' OR 'ar'.
    - Use the full string exactly as provided.
6. Pay attention to the constraints:
Example:
constraint:
{"field": "name", "operator": "equals", "value": "Core Platform"},
{"field": "description", "operator": "equals", "value": "Manages the core backend services, APIs, and infrastructure."},
{"field": "member", "operator": "equals", "value": "John Doe"},
{"field": "role", "operator": "equals", "value": "Developer"},

prompt:
CORRECT: 'Create a team whose name equals 'Core Platform' and description equals 'Manages the core backend services, APIs, and infrastructure.' and member equals 'John Doe' and role equals 'Developer'.'
INCORRECT: 'Create a team name "Core Platform".'
""".strip()

TEAM_CREATED_USE_CASE = UseCase(
    name="AUTOLIST_TEAM_CREATED",
    description="Triggered when a team is created.",
    event=TeamCreatedEvent,
    event_source_code=TeamCreatedEvent.get_source_code_of_class(),
    constraints_generator=generate_team_created_constraints,
    additional_prompt_info=TEAM_CREATED_INFO,
    examples=[
        {"prompt": "Create a team whose name equals 'Core Platform'.", "prompt_for_task_generation": "Create a team whose name equals 'Core Platform'."},
        {
            "prompt": "Create a team whose name equals 'Human Resources' and description equals 'Manages recruitment, employee relations, and company culture.'.",
            "prompt_for_task_generation": "Create a team whose name equals 'Human Resources' and description equals 'Manages recruitment, employee relations, and company culture.' and member equals 'John Doe' and role equals 'Developer'.'.",
        },
        {
            "prompt": "Create a team whose name equals 'Security Champions' and description equals 'Leads security initiatives, code reviews, and vulnerability management.'.",
            "prompt_for_task_generation": "Create a team whose name equals 'Security Champions' and description equals 'Leads security initiatives, code reviews, and vulnerability management.'.",
        },
        {"prompt": "Create a team whose name equals 'Mobile (Android)' and member equals 'Alice Williams' and role equals 'Tester'."},
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
