from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    AttendanceCreateEvent,
    AttendanceDeleteEvent,
    AttendanceUpdateEvent,
    DepartmentCreateEvent,
    DepartmentDeleteEvent,
    DepartmentUpdateEvent,
    EmployeeCreateEvent,
    EmployeeDeleteEvent,
    EmployeeUpdateEvent,
    PayrollCreateEvent,
    PayrollDeleteEvent,
    PayrollUpdateEvent,
    PositionCreateEvent,
    PositionDeleteEvent,
    PositionUpdateEvent,
    UserRedirectEvent,
    UserUpdateEvent,
    UserViewEvent,
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
# ATTENDANCE_UPDATE_USE_CASE
###############################################################################
ATTENDANCE_UPDATE_USE_CASE = UseCase(
    name="Update Attendance Record",
    description="The HR manager updates an existing attendance record for an employee.",
    event=AttendanceUpdateEvent,
    event_source_code=AttendanceUpdateEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Update attendance record A1001 for employee E2001 to mark as present",
            "prompt_for_task_generation": "Update attendance record <attendance_id> for employee <employee_id> to mark as present",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ATTENDANCE_UPDATE",
                "event_criteria": {"attendance_id": {"value": "A1001"}, "employee_id": {"value": "E2001"}},
                "reasoning": "Ensures that updating an attendance record triggers the correct event with proper IDs.",
            },
        },
        {
            "prompt": "Change attendance status for John Doe (ID: E2045) to sick leave",
            "prompt_for_task_generation": "Change attendance status for <employee_name> (ID: <employee_id>) to sick leave",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ATTENDANCE_UPDATE",
                "event_criteria": {"employee_id": {"value": "E2045"}},
                "reasoning": "Validates that attendance updates work with both employee name and ID.",
            },
        },
    ],
)

###############################################################################
# ATTENDANCE_DELETE_USE_CASE
###############################################################################
ATTENDANCE_DELETE_USE_CASE = UseCase(
    name="Delete Attendance Record",
    description="The HR manager deletes an attendance record from the system.",
    event=AttendanceDeleteEvent,
    event_source_code=AttendanceDeleteEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Delete attendance record A1005 for employee E3002",
            "prompt_for_task_generation": "Delete attendance record <attendance_id> for employee <employee_id>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ATTENDANCE_DELETE",
                "event_criteria": {"attendance_id": {"value": "A1005"}, "employee_id": {"value": "E3002"}},
                "reasoning": "Ensures that deleting an attendance record triggers the correct event with proper IDs.",
            },
        },
        {
            "prompt": "Remove invalid attendance entry ID A1010",
            "prompt_for_task_generation": "Remove invalid attendance entry ID <attendance_id>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ATTENDANCE_DELETE",
                "event_criteria": {"attendance_id": {"value": "A1010"}},
                "reasoning": "Validates that attendance records can be deleted by ID alone.",
            },
        },
    ],
)

###############################################################################
# DEPARTMENT_UPDATE_USE_CASE
###############################################################################
DEPARTMENT_UPDATE_USE_CASE = UseCase(
    name="Update Department",
    description="The admin updates an existing department's information.",
    event=DepartmentUpdateEvent,
    event_source_code=DepartmentUpdateEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Rename department D100 from 'IT Support' to 'Technology Services'",
            "prompt_for_task_generation": "Rename department <department_id> from <old_name> to <new_name>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DEPARTMENT_UPDATE",
                "event_criteria": {"department_id": {"value": "D100"}, "department_name": {"value": "Technology Services"}},
                "reasoning": "Ensures that department name changes are properly recorded.",
            },
        },
        {
            "prompt": "Update department D200 with new manager information",
            "prompt_for_task_generation": "Update department <department_id> with new manager information",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DEPARTMENT_UPDATE",
                "event_criteria": {"department_id": {"value": "D200"}},
                "reasoning": "Validates that department updates are captured even when specific changes aren't named.",
            },
        },
    ],
)

###############################################################################
# DEPARTMENT_DELETE_USE_CASE
###############################################################################
DEPARTMENT_DELETE_USE_CASE = UseCase(
    name="Delete Department",
    description="The admin removes a department from the system.",
    event=DepartmentDeleteEvent,
    event_source_code=DepartmentDeleteEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Delete the temporary department D300",
            "prompt_for_task_generation": "Delete the temporary department <department_id>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DEPARTMENT_DELETE",
                "event_criteria": {"department_id": {"value": "D300"}},
                "reasoning": "Ensures that department deletion triggers the correct event.",
            },
        },
        {
            "prompt": "Remove the discontinued 'Legacy Support' department (ID: D305)",
            "prompt_for_task_generation": "Remove the discontinued <department_name> department (ID: <department_id>)",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DEPARTMENT_DELETE",
                "event_criteria": {"department_id": {"value": "D305"}},
                "reasoning": "Validates that departments can be deleted by both name and ID.",
            },
        },
    ],
)

###############################################################################
# EMPLOYEE_UPDATE_USE_CASE
###############################################################################
EMPLOYEE_UPDATE_USE_CASE = UseCase(
    name="Update Employee",
    description="The HR manager updates an employee's information.",
    event=EmployeeUpdateEvent,
    event_source_code=EmployeeUpdateEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Update employee E4001's position to Senior Developer",
            "prompt_for_task_generation": "Update employee <employee_id>'s position to <new_position>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EMPLOYEE_UPDATE",
                "event_criteria": {"employee_id": {"value": "E4001"}, "employee_name": {"value": "Senior Developer", "operator": "not_equals"}},
                "reasoning": "Ensures that employee position updates are properly recorded.",
            },
        },
        {
            "prompt": "Change Sarah Johnson's (ID: E2045) department to Marketing",
            "prompt_for_task_generation": "Change <employee_name>'s (ID: <employee_id>) department to <new_department>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EMPLOYEE_UPDATE",
                "event_criteria": {"employee_id": {"value": "E2045"}},
                "reasoning": "Validates that department transfers are captured in the system.",
            },
        },
    ],
)

###############################################################################
# EMPLOYEE_DELETE_USE_CASE
###############################################################################
EMPLOYEE_DELETE_USE_CASE = UseCase(
    name="Delete Employee",
    description="The HR manager removes an employee from the system.",
    event=EmployeeDeleteEvent,
    event_source_code=EmployeeDeleteEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Terminate employee E5001 from the system",
            "prompt_for_task_generation": "Terminate employee <employee_id> from the system",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EMPLOYEE_DELETE",
                "event_criteria": {"employee_id": {"value": "E5001"}},
                "reasoning": "Ensures that employee termination triggers the correct event.",
            },
        },
        {
            "prompt": "Remove John Smith (ID: E5002) from our records",
            "prompt_for_task_generation": "Remove <employee_name> (ID: <employee_id>) from our records",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EMPLOYEE_DELETE",
                "event_criteria": {"employee_id": {"value": "E5002"}},
                "reasoning": "Validates that employee deletion works with both name and ID.",
            },
        },
    ],
)

###############################################################################
# PAYROLL_UPDATE_USE_CASE
###############################################################################
PAYROLL_UPDATE_USE_CASE = UseCase(
    name="Update Payroll",
    description="The HR manager updates an employee's payroll information.",
    event=PayrollUpdateEvent,
    event_source_code=PayrollUpdateEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Update payroll P2001 for employee E3002 with new salary",
            "prompt_for_task_generation": "Update payroll <payroll_id> for employee <employee_id> with new salary",
            "test": {
                "type": "CheckEventTest",
                "event_name": "PAYROLL_UPDATE",
                "event_criteria": {"payroll_id": {"value": "P2001"}, "employee_id": {"value": "E3002"}},
                "reasoning": "Ensures that payroll updates are properly recorded with both payroll and employee IDs.",
            },
        },
        {
            "prompt": "Adjust tax information for Michael Brown's payroll (ID: P2005)",
            "prompt_for_task_generation": "Adjust tax information for <employee_name>'s payroll (ID: <payroll_id>)",
            "test": {
                "type": "CheckEventTest",
                "event_name": "PAYROLL_UPDATE",
                "event_criteria": {"payroll_id": {"value": "P2005"}},
                "reasoning": "Validates that specific payroll adjustments are captured.",
            },
        },
    ],
)

###############################################################################
# PAYROLL_DELETE_USE_CASE
###############################################################################
PAYROLL_DELETE_USE_CASE = UseCase(
    name="Delete Payroll",
    description="The HR manager removes a payroll record from the system.",
    event=PayrollDeleteEvent,
    event_source_code=PayrollDeleteEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Delete payroll record P2010 for employee E4005",
            "prompt_for_task_generation": "Delete payroll record <payroll_id> for employee <employee_id>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "PAYROLL_DELETE",
                "event_criteria": {"payroll_id": {"value": "P2010"}, "employee_id": {"value": "E4005"}},
                "reasoning": "Ensures that payroll deletion triggers the correct event with proper IDs.",
            },
        },
        {
            "prompt": "Remove incorrect payroll entry P2015",
            "prompt_for_task_generation": "Remove incorrect payroll entry <payroll_id>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "PAYROLL_DELETE",
                "event_criteria": {"payroll_id": {"value": "P2015"}},
                "reasoning": "Validates that payroll records can be deleted by ID alone.",
            },
        },
    ],
)

###############################################################################
# POSITION_CREATE_USE_CASE
###############################################################################
POSITION_CREATE_USE_CASE = UseCase(
    name="Create Position",
    description="The admin creates a new job position in the organization.",
    event=PositionCreateEvent,
    event_source_code=PositionCreateEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Create new position 'Data Analyst' with position code PA100",
            "prompt_for_task_generation": "Create new position <position_name> with position code <position_code>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "POSITION_CREATE",
                "event_criteria": {"position_name": {"value": "Data Analyst"}, "position_id": {"value": "PA100"}},
                "reasoning": "Ensures that creating a new position triggers the correct event with all required fields.",
            },
        },
        {
            "prompt": "Add new Senior Developer position to the system",
            "prompt_for_task_generation": "Add new <position_name> position to the system",
            "test": {
                "type": "CheckEventTest",
                "event_name": "POSITION_CREATE",
                "event_criteria": {"position_name": {"value": "Senior Developer"}},
                "reasoning": "Validates that position creation works even when ID is automatically generated.",
            },
        },
    ],
)

###############################################################################
# POSITION_UPDATE_USE_CASE
###############################################################################
POSITION_UPDATE_USE_CASE = UseCase(
    name="Update Position",
    description="The admin updates an existing job position's information.",
    event=PositionUpdateEvent,
    event_source_code=PositionUpdateEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Update position PA100 to change title to 'Senior Data Analyst'",
            "prompt_for_task_generation": "Update position <position_id> to change title to <new_title>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "POSITION_UPDATE",
                "event_criteria": {"position_id": {"value": "PA100"}, "position_name": {"value": "Senior Data Analyst"}},
                "reasoning": "Ensures that position title updates are properly recorded.",
            },
        },
        {
            "prompt": "Modify salary range for position PS200 (Senior Developer)",
            "prompt_for_task_generation": "Modify salary range for position <position_id> (<position_name>)",
            "test": {
                "type": "CheckEventTest",
                "event_name": "POSITION_UPDATE",
                "event_criteria": {"position_id": {"value": "PS200"}},
                "reasoning": "Validates that position updates are captured even when specific changes aren't named.",
            },
        },
    ],
)

###############################################################################
# POSITION_DELETE_USE_CASE
###############################################################################
POSITION_DELETE_USE_CASE = UseCase(
    name="Delete Position",
    description="The admin removes a job position from the system.",
    event=PositionDeleteEvent,
    event_source_code=PositionDeleteEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Delete position PT300 (Junior Tester)",
            "prompt_for_task_generation": "Delete position <position_id> (<position_name>)",
            "test": {
                "type": "CheckEventTest",
                "event_name": "POSITION_DELETE",
                "event_criteria": {"position_id": {"value": "PT300"}},
                "reasoning": "Ensures that position deletion triggers the correct event.",
            },
        },
        {
            "prompt": "Remove obsolete 'Legacy Support' position (ID: PL400)",
            "prompt_for_task_generation": "Remove obsolete <position_name> position (ID: <position_id>)",
            "test": {
                "type": "CheckEventTest",
                "event_name": "POSITION_DELETE",
                "event_criteria": {"position_id": {"value": "PL400"}},
                "reasoning": "Validates that positions can be deleted by both name and ID.",
            },
        },
    ],
)

###############################################################################
# USER_VIEW_USE_CASE
###############################################################################
USER_VIEW_USE_CASE = UseCase(
    name="View User Information",
    description="The user views information in the system.",
    event=UserViewEvent,
    event_source_code=UserViewEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "View my profile information",
            "prompt_for_task_generation": "View my profile information",
            "test": {
                "type": "CheckEventTest",
                "event_name": "USER_VIEW",
                "event_criteria": {"viewed_item": {"contains": "profile"}},
                "reasoning": "Ensures that viewing user profile information is properly tracked.",
            },
        },
        {
            "prompt": "Show my attendance records",
            "prompt_for_task_generation": "Show my attendance records",
            "test": {
                "type": "CheckEventTest",
                "event_name": "USER_VIEW",
                "event_criteria": {"viewed_item": {"contains": "attendance"}},
                "reasoning": "Validates that viewing attendance records triggers the view event.",
            },
        },
        {
            "prompt": "Display payroll details",
            "prompt_for_task_generation": "Display payroll details",
            "test": {
                "type": "CheckEventTest",
                "event_name": "USER_VIEW",
                "event_criteria": {"viewed_item": {"contains": "payroll"}},
                "reasoning": "Confirms that accessing payroll information is recorded.",
            },
        },
    ],
)
###############################################################################
# FINAL LIST: ALL_USE_CASES
###############################################################################
ALL_USE_CASES = [
    ATTENDANCE_CREATE_USE_CASE,
    ATTENDANCE_UPDATE_USE_CASE,
    ATTENDANCE_DELETE_USE_CASE,
    DEPARTMENT_CREATE_USE_CASE,
    DEPARTMENT_UPDATE_USE_CASE,
    DEPARTMENT_DELETE_USE_CASE,
    EMPLOYEE_CREATE_USE_CASE,
    EMPLOYEE_UPDATE_USE_CASE,
    EMPLOYEE_DELETE_USE_CASE,
    PAYROLL_CREATE_USE_CASE,
    PAYROLL_UPDATE_USE_CASE,
    PAYROLL_DELETE_USE_CASE,
    POSITION_CREATE_USE_CASE,
    POSITION_UPDATE_USE_CASE,
    POSITION_DELETE_USE_CASE,
    USER_VIEW_USE_CASE,
    USER_UPDATE_USE_CASE,
    USER_REDIRECT_USE_CASE,
]
