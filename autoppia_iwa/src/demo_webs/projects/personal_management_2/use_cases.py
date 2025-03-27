from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    AttendanceCreateEvent,
    DepartmentCreateEvent,
    EmployeeCreateEvent,
    PayrollCreateEvent,
    UserRedirectEvent,
    UserUpdateEvent,
)

###############################################################################
# ATTENDANCE_CREATE_USE_CASE
###############################################################################
ATTENDANCE_CREATE_USE_CASE = UseCase(
    name="Create Attendance Record",
    description="The HR manager creates a new attendance record for an employee.",
    event=AttendanceCreateEvent,
    event_source_code=AttendanceCreateEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Create attendance record for employee ID E1001",
            "prompt_for_task_generation": "Create attendance record for employee ID <employee_id>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ATTENDANCE_CREATE",
                "event_criteria": {"employee_id": {"value": "E1001"}},
                "reasoning": "Ensures that creating an attendance record for an employee triggers the correct event.",
            },
        },
        {
            "prompt": "Mark attendance for John Doe (ID: E2045)",
            "prompt_for_task_generation": "Mark attendance for <employee_name> (ID: <employee_id>)",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ATTENDANCE_CREATE",
                "event_criteria": {"employee_id": {"value": "E2045"}},
                "reasoning": "Validates that attendance creation works with both employee name and ID.",
            },
        },
    ],
)

###############################################################################
# DEPARTMENT_CREATE_USE_CASE
###############################################################################
DEPARTMENT_CREATE_USE_CASE = UseCase(
    name="Create Department",
    description="The admin creates a new department in the organization.",
    event=DepartmentCreateEvent,
    event_source_code=DepartmentCreateEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Create new department named 'Research & Development'",
            "prompt_for_task_generation": "Create new department named <department_name>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DEPARTMENT_CREATE",
                "event_criteria": {"department_name": {"value": "Research & Development"}},
                "reasoning": "Ensures that creating a new department triggers the correct event with the proper name.",
            },
        },
        {
            "prompt": "Add a new Marketing department to the system",
            "prompt_for_task_generation": "Add a new <department_name> department to the system",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DEPARTMENT_CREATE",
                "event_criteria": {"department_name": {"value": "Marketing"}},
                "reasoning": "Validates that department creation works with different naming formats.",
            },
        },
    ],
)

###############################################################################
# EMPLOYEE_CREATE_USE_CASE
###############################################################################
EMPLOYEE_CREATE_USE_CASE = UseCase(
    name="Create Employee",
    description="The HR manager adds a new employee to the system.",
    event=EmployeeCreateEvent,
    event_source_code=EmployeeCreateEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Add new employee John Smith with ID E5001",
            "prompt_for_task_generation": "Add new employee <employee_name> with ID <employee_id>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EMPLOYEE_CREATE",
                "event_criteria": {"employee_id": {"value": "E5001"}, "employee_name": {"value": "John Smith"}},
                "reasoning": "Ensures that creating a new employee record triggers the correct event with all required fields.",
            },
        },
        {
            "prompt": "Register new employee Sarah Johnson in the system",
            "prompt_for_task_generation": "Register new employee <employee_name> in the system",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EMPLOYEE_CREATE",
                "event_criteria": {"employee_name": {"value": "Sarah Johnson"}},
                "reasoning": "Validates that employee creation works even when ID is automatically generated.",
            },
        },
    ],
)

###############################################################################
# PAYROLL_CREATE_USE_CASE
###############################################################################
PAYROLL_CREATE_USE_CASE = UseCase(
    name="Create Payroll",
    description="The HR manager creates a payroll record for an employee.",
    event=PayrollCreateEvent,
    event_source_code=PayrollCreateEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Create payroll for employee ID E3002",
            "prompt_for_task_generation": "Create payroll for employee ID <employee_id>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "PAYROLL_CREATE",
                "event_criteria": {"employee_id": {"value": "E3002"}},
                "reasoning": "Ensures that payroll creation for an employee triggers the correct event.",
            },
        },
        {
            "prompt": "Generate payroll record for Michael Brown (ID: E4005)",
            "prompt_for_task_generation": "Generate payroll record for <employee_name> (ID: <employee_id>)",
            "test": {
                "type": "CheckEventTest",
                "event_name": "PAYROLL_CREATE",
                "event_criteria": {"employee_id": {"value": "E4005"}},
                "reasoning": "Validates that payroll creation works with both employee name and ID.",
            },
        },
    ],
)

###############################################################################
# USER_UPDATE_USE_CASE
###############################################################################
USER_UPDATE_USE_CASE = UseCase(
    name="Update User Profile",
    description="The user updates their profile information.",
    event=UserUpdateEvent,
    event_source_code=UserUpdateEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Update my email address to newemail@company.com",
            "prompt_for_task_generation": "Update my email address to <new_email>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "USER_UPDATE",
                "event_criteria": {"updated_fields": {"contains": "email"}},
                "reasoning": "Ensures that updating email address triggers the user update event.",
            },
        },
        {
            "prompt": "Change my password to a more secure one",
            "prompt_for_task_generation": "Change my password to a more secure one",
            "test": {
                "type": "CheckEventTest",
                "event_name": "USER_UPDATE",
                "event_criteria": {"updated_fields": {"contains": "password"}},
                "reasoning": "Validates that password changes are properly recorded.",
            },
        },
    ],
)

###############################################################################
# USER_REDIRECT_USE_CASE
###############################################################################
USER_REDIRECT_USE_CASE = UseCase(
    name="User Redirect",
    description="The system redirects the user to a different page.",
    event=UserRedirectEvent,
    event_source_code=UserRedirectEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Redirect from dashboard to attendance page",
            "prompt_for_task_generation": "Redirect from <from_path> to <to_path>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "USER_REDIRECT",
                "event_criteria": {"from_path": {"value": "/dashboard"}, "to_path": {"value": "/attendance"}},
                "reasoning": "Ensures that user redirections between pages are properly tracked.",
            },
        },
        {
            "prompt": "Navigate from payroll to employee directory",
            "prompt_for_task_generation": "Navigate from <from_path> to <to_path>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "USER_REDIRECT",
                "event_criteria": {"from_path": {"value": "/payroll"}, "to_path": {"value": "/employees"}},
                "reasoning": "Validates that navigation between different sections is recorded.",
            },
        },
    ],
)

###############################################################################
# FINAL LIST: ALL_USE_CASES
###############################################################################
ALL_USE_CASES = [
    ATTENDANCE_CREATE_USE_CASE,
    # ATTENDANCE_UPDATE_USE_CASE,
    # ATTENDANCE_DELETE_USE_CASE,
    DEPARTMENT_CREATE_USE_CASE,
    # DEPARTMENT_UPDATE_USE_CASE,
    # DEPARTMENT_DELETE_USE_CASE,
    EMPLOYEE_CREATE_USE_CASE,
    # EMPLOYEE_UPDATE_USE_CASE,
    # EMPLOYEE_DELETE_USE_CASE,
    PAYROLL_CREATE_USE_CASE,
    # PAYROLL_UPDATE_USE_CASE,
    # PAYROLL_DELETE_USE_CASE,
    # POSITION_CREATE_USE_CASE,
    # POSITION_UPDATE_USE_CASE,
    # POSITION_DELETE_USE_CASE,
    # USER_VIEW_USE_CASE,
    USER_UPDATE_USE_CASE,
    USER_REDIRECT_USE_CASE,
]
