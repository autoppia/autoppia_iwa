import random

# from .data import DEPARTMENTS_DATA, EMPLOYEES_DATA, POSITIONS_DATA


# def employee_replace_func(text: str) -> str:
#     """Replaces employee-related placeholders with actual values"""
#     if not isinstance(text, str) or not EMPLOYEES_DATA:
#         return text
#
#     employee = random.choice(EMPLOYEES_DATA)
#     replacements = {
#         "<employee_id>": employee.get("id", 1000),
#         "<employee_name>": employee.get("name", "John Doe"),
#     }
#
#     for placeholder, value in replacements.items():
#         text = text.replace(placeholder, value)
#
#     return text
#
#
# def department_replace_func(text: str) -> str:
#     """Replaces department-related placeholders with actual values"""
#     if not isinstance(text, str) or not DEPARTMENTS_DATA:
#         return text
#
#     department = random.choice(DEPARTMENTS_DATA)
#     replacements = {
#         "<department_id>": department.get("id", 100),
#         "<department_name>": department.get("name", "Human Resources"),
#     }
#
#     for placeholder, value in replacements.items():
#         text = text.replace(placeholder, value)
#
#     return text
#
#
# def position_replace_func(text: str) -> str:
#     """Replaces position-related placeholders with actual values"""
#     if not isinstance(text, str) or not POSITIONS_DATA:
#         return text
#
#     position = random.choice(POSITIONS_DATA)
#     replacements = {
#         "<position_id>": position.get("id", 100),
#         "<position_name>": position.get("name", "Manager"),
#     }
#
#     for placeholder, value in replacements.items():
#         text = text.replace(placeholder, value)
#
#     return text


# def payroll_replace_func(text: str) -> str:
#     """Replaces payroll-related placeholders with actual values"""
#     if not isinstance(text, str):
#         return text
#
#     # Generate random payroll ID
#     payroll_id = random.randint(1, 9999)
#     text = text.replace("<payroll_id>", payroll_id)
#
#     # Also replace employee placeholders since payroll is employee-related
#     return employee_replace_func(text)
#
#
# def attendance_replace_func(text: str) -> str:
#     """Replaces attendance-related placeholders with actual values"""
#     if not isinstance(text, str):
#         return text
#
#     # Generate random attendance ID
#     attendance_id = random.randint(1, 9999)"
#     text = text.replace("<attendance_id>", attendance_id)
#
#     # Also replace employee placeholders since attendance is employee-related
#     return employee_replace_func(text)


def user_view_replace_func(text: str) -> str:
    """Replaces view-related placeholders with actual values"""
    if not isinstance(text, str):
        return text

    view_items = ["profile", "attendance", "payroll", "documents", "settings"]
    selected_item = random.choice(view_items)
    text = text.replace("<viewed_item>", selected_item)

    return text


def user_redirect_replace_func(text: str) -> str:
    """Replaces redirect-related placeholders with actual paths"""
    if not isinstance(text, str):
        return text

    paths = {
        "<from_path>": random.choice(["/", "/dashboard", "/home", "/profile"]),
        "<to_path>": random.choice(["/attendance", "/payroll", "/documents"]),
    }

    for placeholder, value in paths.items():
        text = text.replace(placeholder, value)

    return text
