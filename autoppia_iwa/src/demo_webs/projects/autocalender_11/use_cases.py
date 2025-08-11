from ...classes import UseCase
from .events import (
    AddEventEvent,
    AddNewCalendarEvent,
    CancelAddEventEvent,
    CellClickedEvent,
    ChooseCalendarEvent,
    CreateCalendarEvent,
    DeleteAddedEventEvent,
    SelectDayEvent,
    SelectFiveDaysEvent,
    SelectMonthEvent,
    SelectTodayEvent,
    SelectWeekEvent,
)
from .generation_functions import (
    generate_add_event_constraints,
    generate_cancel_add_event_constraints,
    generate_cell_clicked_constraints,
    generate_choose_calendar_constraints,
    generate_create_calendar_constraints,
    generate_delete_event_constraints,
)

###############################################################################
# SELECT_MONTH_USE_CASE
###############################################################################

SELECT_MONTH_INFO = """
CRITICAL REQUIREMENT:
1. Begin your prompt with "Switch to month view" or similar phrases.
2. Only mention changing the calendar view to month view.
3. Do not include other calendar interactions like adding events or selecting specific dates.
"""

SELECT_MONTH_USE_CASE = UseCase(
    name="SELECT_MONTH",
    description="Triggered when the user switches to the month view in the calendar.",
    event=SelectMonthEvent,
    event_source_code=SelectMonthEvent.get_source_code_of_class(),
    constraints_generator=False,
    additional_prompt_info=SELECT_MONTH_INFO,
    examples=[
        {"prompt": "Switch to month view please.", "prompt_for_task_generation": "Switch to month view."},
        {"prompt": "I want to see the calendar in month view.", "prompt_for_task_generation": "Change to month view."},
        {"prompt": "Show me the entire month on the calendar.", "prompt_for_task_generation": "Display calendar in month view."},
        {"prompt": "Change the calendar to display by month.", "prompt_for_task_generation": "Change calendar to month view."},
        {"prompt": "Can you expand the view to show the full month?", "prompt_for_task_generation": "Expand to full month view."},
    ],
)

###############################################################################
# SELECT_WEEK_USE_CASE
###############################################################################

SELECT_WEEK_INFO = """
CRITICAL REQUIREMENT:
1. Begin your prompt with "Switch to week view" or similar phrases.
2. Only mention changing the calendar view to week view.
3. Do not include other calendar interactions like adding events or selecting specific dates.
"""

SELECT_WEEK_USE_CASE = UseCase(
    name="SELECT_WEEK",
    description="Triggered when the user switches to the week view in the calendar.",
    event=SelectWeekEvent,
    event_source_code=SelectWeekEvent.get_source_code_of_class(),
    constraints_generator=False,
    additional_prompt_info=SELECT_WEEK_INFO,
    examples=[
        {"prompt": "Switch to week view please.", "prompt_for_task_generation": "Switch to week view."},
        {"prompt": "I want to see the calendar in week view.", "prompt_for_task_generation": "Change to week view."},
        {"prompt": "Show me this week's schedule.", "prompt_for_task_generation": "Show calendar in week view."},
        {"prompt": "Change the calendar to display by week.", "prompt_for_task_generation": "Change calendar to week view."},
        {"prompt": "Can you show me the weekly calendar view?", "prompt_for_task_generation": "Display weekly calendar view."},
    ],
)

###############################################################################
# SELECT_FIVE_DAYS_USE_CASE
###############################################################################

SELECT_FIVE_DAYS_INFO = """
CRITICAL REQUIREMENT:
1. Begin your prompt with "Switch to 5-day view" or similar phrases.
2. Only mention changing the calendar view to 5-day view.
3. Do not include other calendar interactions like adding events or selecting specific dates.
"""

SELECT_FIVE_DAYS_USE_CASE = UseCase(
    name="SELECT_FIVE_DAYS",
    description="Triggered when the user switches to the 5-day view in the calendar.",
    event=SelectFiveDaysEvent,
    event_source_code=SelectFiveDaysEvent.get_source_code_of_class(),
    constraints_generator=False,
    additional_prompt_info=SELECT_FIVE_DAYS_INFO,
    examples=[
        {"prompt": "Switch to 5-day view please.", "prompt_for_task_generation": "Switch to 5-day view."},
        {"prompt": "I want to see the calendar in 5-day view.", "prompt_for_task_generation": "Change to 5-day view."},
        {"prompt": "Show me the 5-day schedule.", "prompt_for_task_generation": "Show calendar in 5-day view."},
        {"prompt": "Change the calendar to display five days at once.", "prompt_for_task_generation": "Change calendar to 5-day view."},
        {"prompt": "Can you display the workweek view?", "prompt_for_task_generation": "Display 5-day workweek view."},
    ],
)

###############################################################################
# SELECT_DAY_USE_CASE
###############################################################################

SELECT_DAY_INFO = """
CRITICAL REQUIREMENT:
1. Begin your prompt with "Switch to day view" or similar phrases.
2. Only mention changing the calendar view to single day view.
3. Do not include other calendar interactions like adding events or selecting specific dates.
"""

SELECT_DAY_USE_CASE = UseCase(
    name="SELECT_DAY",
    description="Triggered when the user switches to the day view in the calendar.",
    event=SelectDayEvent,
    event_source_code=SelectDayEvent.get_source_code_of_class(),
    constraints_generator=False,
    additional_prompt_info=SELECT_DAY_INFO,
    examples=[
        {"prompt": "Switch to day view please.", "prompt_for_task_generation": "Switch to day view."},
        {"prompt": "I want to see the calendar in daily view.", "prompt_for_task_generation": "Change to day view."},
        {"prompt": "Show me today's schedule in detail.", "prompt_for_task_generation": "Show calendar in day view."},
        {"prompt": "Change the calendar to display a single day.", "prompt_for_task_generation": "Change calendar to single day view."},
        {"prompt": "Can you zoom in to just show one day?", "prompt_for_task_generation": "Zoom to single day view."},
    ],
)

###############################################################################
# SELECT_TODAY_USE_CASE
###############################################################################

SELECT_TODAY_INFO = """
CRITICAL REQUIREMENT:
1. Begin your prompt with phrases like "Go to today" or "Jump to today's date".
2. Focus only on navigating to today's date in the calendar.
3. Do not include other calendar interactions like adding events or changing views.
"""

SELECT_TODAY_USE_CASE = UseCase(
    name="SELECT_TODAY",
    description="Triggered when the user jumps to today's date in the calendar.",
    event=SelectTodayEvent,
    event_source_code=SelectTodayEvent.get_source_code_of_class(),
    constraints_generator=False,
    additional_prompt_info=SELECT_TODAY_INFO,
    examples=[
        {"prompt": "Go to today's date.", "prompt_for_task_generation": "Navigate to today in the calendar."},
        {"prompt": "Show me today in the calendar.", "prompt_for_task_generation": "Jump to today's date."},
        {"prompt": "Jump to today please.", "prompt_for_task_generation": "Go to today in the calendar."},
        {"prompt": "Reset the calendar to today.", "prompt_for_task_generation": "Reset to today's date."},
        {"prompt": "I want to see what's scheduled for today.", "prompt_for_task_generation": "Navigate to today to see today's schedule."},
    ],
)

###############################################################################
# ADD_NEW_CALENDAR_USE_CASE
###############################################################################

ADD_NEW_CALENDAR_INFO = """
CRITICAL REQUIREMENT:
1. The prompt must only mention clicking the add calendar button or icon.
2. Do not include any other actions or details about calendar creation.
"""

ADD_NEW_CALENDAR_USE_CASE = UseCase(
    name="ADD_NEW_CALENDAR",
    description="Triggered when the user opens the modal to add a new calendar.",
    event=AddNewCalendarEvent,
    event_source_code=AddNewCalendarEvent.get_source_code_of_class(),
    constraints_generator=False,
    additional_prompt_info=ADD_NEW_CALENDAR_INFO,
    examples=[
        {"prompt": "Click the add calendar button.", "prompt_for_task_generation": "Click add calendar."},
        {"prompt": "Press the button to add a calendar.", "prompt_for_task_generation": "Click add calendar button."},
        {"prompt": "Select the option to add a calendar.", "prompt_for_task_generation": "Click add calendar option."},
        {"prompt": "Click to add a new calendar.", "prompt_for_task_generation": "Click add calendar."},
        {"prompt": "Tap the add calendar icon.", "prompt_for_task_generation": "Click add calendar icon."},
    ],
)

###############################################################################
# CREATE_CALENDAR_USE_CASE
###############################################################################

CREATE_CALENDAR_INFO = """
CRITICAL REQUIREMENT:
1. Include specific calendar details: name and description.
2. The prompt should express completion of calendar creation with these details.
3. Do not mention color, as it is not part of the generated constraints.
"""

CREATE_CALENDAR_USE_CASE = UseCase(
    name="CREATE_CALENDAR",
    description="Triggered when the user completes creation of a new calendar with details.",
    event=CreateCalendarEvent,
    event_source_code=CreateCalendarEvent.get_source_code_of_class(),
    constraints_generator=generate_create_calendar_constraints,
    additional_prompt_info=CREATE_CALENDAR_INFO,
    examples=[
        {
            "prompt": "Create a 'Projects' calendar for my job-related events.",
            "prompt_for_task_generation": "Create calendar named 'Projects' with a description for job events.",
        },
        {
            "prompt": "Make a new 'Holidays' calendar to track family vacations.",
            "prompt_for_task_generation": "Create 'Holidays' calendar for family vacations.",
        },
        {
            "prompt": "Set up a 'Fitness' calendar for my workout schedule.",
            "prompt_for_task_generation": "Create 'Fitness' calendar for workout tracking.",
        },
        {"prompt": "Create a 'Travel' calendar to plan my trips.", "prompt_for_task_generation": "Create 'Travel' calendar for trip planning."},
        {
            "prompt": "Make a 'Study' calendar for my classes and assignments.",
            "prompt_for_task_generation": "Create 'Study' calendar for academic planning.",
        },
    ],
)

###############################################################################
# CHOOSE_CALENDAR_USE_CASE
###############################################################################

CHOOSE_CALENDAR_INFO = """
CRITICAL REQUIREMENT:
1. The prompt must be about hiding or deselecting a calendar, as the 'selected' constraint is always false.
2. Use the calendar name exactly as provided in the constraints (e.g., 'Personal', 'Fitness').
3. Do not mention color.
Example for {'calendar_name': 'Personal', 'selected': false} -> "Unselect the 'Personal' calendar."
"""

CHOOSE_CALENDAR_USE_CASE = UseCase(
    name="CHOOSE_CALENDAR",
    description="Triggered when the user deselects a calendar from the sidebar.",
    event=ChooseCalendarEvent,
    event_source_code=ChooseCalendarEvent.get_source_code_of_class(),
    constraints_generator=generate_choose_calendar_constraints,
    additional_prompt_info=CHOOSE_CALENDAR_INFO,
    examples=[
        {"prompt": "Hide the Personal calendar.", "prompt_for_task_generation": "Deselect the Personal calendar."},
        {"prompt": "I don't want to see the Fitness calendar right now.", "prompt_for_task_generation": "Hide the Fitness calendar."},
        {"prompt": "Unselect the 'Study' calendar.", "prompt_for_task_generation": "Deselect the Study calendar."},
        {"prompt": "Remove the 'Travel' calendar from view.", "prompt_for_task_generation": "Hide the Travel calendar."},
        {"prompt": "Deselect the 'Holidays' calendar.", "prompt_for_task_generation": "Deselect the Holidays calendar."},
    ],
)

###############################################################################
# ADD_EVENT_USE_CASE
###############################################################################

ADD_EVENT_INFO = """
CRITICAL REQUIREMENT:
1. Include all event details: title, calendar, date, start time, and end time.
2. Format times as hours and minutes (e.g., "5:30 PM", "17:30").
3. Specify which calendar the event should be added to.
4. Do not mention color.
"""

ADD_EVENT_USE_CASE = UseCase(
    name="ADD_EVENT",
    description="Triggered when the user creates a new event in the calendar.",
    event=AddEventEvent,
    event_source_code=AddEventEvent.get_source_code_of_class(),
    constraints_generator=generate_add_event_constraints,
    additional_prompt_info=ADD_EVENT_INFO,
    examples=[
        {
            "prompt": "Add 'Doctor appointment' to my 'Personal' calendar for tomorrow at 10:00 AM, ending at 10:30 AM.",
            "prompt_for_task_generation": "Create event 'Doctor appointment' in 'Personal' calendar for tomorrow from 10:00 to 10:30.",
        },
        {
            "prompt": "Schedule a 'Conference call' in the 'Projects' calendar for next Monday from 15:00 to 16:00.",
            "prompt_for_task_generation": "Add 'Conference call' to 'Projects' calendar on next Monday, 15:00-16:00.",
        },
        {
            "prompt": "Put 'Workout' on the 'Fitness' calendar for today at 6:00 PM, lasting one hour.",
            "prompt_for_task_generation": "Add 'Workout' to 'Fitness' calendar today from 6:00 PM to 7:00 PM.",
        },
        {
            "prompt": "Add a 'Study session' to the 'Study' calendar for this Friday from 9:00 AM to 11:30 AM.",
            "prompt_for_task_generation": "Create 'Study session' in 'Study' calendar this Friday, 9:00 AM to 11:30 AM.",
        },
        {
            "prompt": "I have a 'Lunch' meeting, please add it to my 'Personal' calendar for today at 12:30 PM for 30 minutes.",
            "prompt_for_task_generation": "Add 'Lunch' to 'Personal' calendar today from 12:30 PM to 1:00 PM.",
        },
    ],
)

###############################################################################
# CELL_CLICKED_USE_CASE
###############################################################################

CELL_CLICKED_INFO = """
CRITICAL REQUIREMENT:
1. Clearly indicate selecting a specific date or time slot in the calendar.
2. Specify the view type (Month, Week, Day, 5 days) where the selection is happening.
3. For week, day, or 5-day views, include the specific hour if available in constraints.
"""

CELL_CLICKED_USE_CASE = UseCase(
    name="CELL_CLICKED",
    description="Triggered when the user clicks on a specific date or time cell in the calendar.",
    event=CellClickedEvent,
    event_source_code=CellClickedEvent.get_source_code_of_class(),
    constraints_generator=generate_cell_clicked_constraints,
    additional_prompt_info=CELL_CLICKED_INFO,
    examples=[
        {"prompt": "Select July 23rd in the month view.", "prompt_for_task_generation": "Click on July 23 cell in month view."},
        {"prompt": "In the week view, click on Wednesday at 3 PM.", "prompt_for_task_generation": "Click on Wednesday 3 PM slot in week view."},
        {"prompt": "I want to select 10 AM on the current day in the day view.", "prompt_for_task_generation": "Select 10 AM in the day view."},
        {"prompt": "Click on the 15th of next month from the month view.", "prompt_for_task_generation": "Click on the 15th of next month in month view."},
        {"prompt": "In the 5-day view, select Friday at noon.", "prompt_for_task_generation": "Click on Friday 12:00 PM in 5-day view."},
    ],
)

###############################################################################
# CANCEL_ADD_EVENT_USE_CASE
###############################################################################

CANCEL_ADD_EVENT_INFO = """
CRITICAL REQUIREMENT:
1. Explicitly mention canceling or abandoning event creation.
2. If a title or date is specified in the constraints, include that information.
3. Make it clear that the user is stopping the event creation process.
"""

CANCEL_ADD_EVENT_USE_CASE = UseCase(
    name="CANCEL_ADD_EVENT",
    description="Triggered when the user cancels adding a new event.",
    event=CancelAddEventEvent,
    event_source_code=CancelAddEventEvent.get_source_code_of_class(),
    constraints_generator=generate_cancel_add_event_constraints,
    additional_prompt_info=CANCEL_ADD_EVENT_INFO,
    examples=[
        {"prompt": "Cancel creating this event.", "prompt_for_task_generation": "Cancel the event creation process."},
        {"prompt": "Never mind, don't add the 'Meeting' event.", "prompt_for_task_generation": "Cancel adding the 'Meeting' event."},
        {"prompt": "I made a mistake, cancel the event for tomorrow.", "prompt_for_task_generation": "Cancel creating the event for tomorrow."},
        {"prompt": "Close the event creation dialog without saving.", "prompt_for_task_generation": "Cancel event creation."},
        {"prompt": "Actually, don't create that event.", "prompt_for_task_generation": "Abandon event creation."},
    ],
)
###############################################################################
# DELETE_ADDED_EVENT_USE_CASE
###############################################################################

DELETE_ADDED_EVENT_INFO = """
CRITICAL REQUIREMENT:
1. Explicitly mention deleting or removing an existing event from the calendar.
2. Include the event title if specified in constraints.
3. Optionally mention the date or calendar name if specified in constraints.
4. Make it clear that the user is removing an already created event, not canceling its creation.
"""

DELETE_ADDED_EVENT_USE_CASE = UseCase(
    name="DELETE_ADDED_EVENT",
    description="Triggered when the user deletes an existing calendar event.",
    event=DeleteAddedEventEvent,
    event_source_code=DeleteAddedEventEvent.get_source_code_of_class(),
    constraints_generator=generate_delete_event_constraints,
    additional_prompt_info=DELETE_ADDED_EVENT_INFO,
    examples=[
        {"prompt": "Delete the 'Team Meeting' event from my calendar.", "prompt_for_task_generation": "Remove 'Team Meeting' event from calendar."},
        {"prompt": "Remove the 'Doctor appointment' on the 15th.", "prompt_for_task_generation": "Delete 'Doctor appointment' on the 15th."},
        {"prompt": "I want to delete the 'Lunch' event from my 'Personal' calendar.", "prompt_for_task_generation": "Delete 'Lunch' event from 'Personal' calendar."},
        {"prompt": "Please remove the 'Conference call' event.", "prompt_for_task_generation": "Delete the 'Conference call' event."},
        {"prompt": "Delete the event titled 'Workout' for today.", "prompt_for_task_generation": "Remove the 'Workout' event scheduled for today."},
    ],
)
ALL_USE_CASES = [
    # SELECT_MONTH_USE_CASE,
    # SELECT_WEEK_USE_CASE,
    # SELECT_FIVE_DAYS_USE_CASE,
    # SELECT_DAY_USE_CASE,
    # SELECT_TODAY_USE_CASE,
    # ADD_NEW_CALENDAR_USE_CASE,
    CREATE_CALENDAR_USE_CASE,
    # CHOOSE_CALENDAR_USE_CASE,
    # ADD_EVENT_USE_CASE,
    # CELL_CLICKED_USE_CASE,
    # CANCEL_ADD_EVENT_USE_CASE,
    # DELETE_ADDED_EVENT_USE_CASE,
]
