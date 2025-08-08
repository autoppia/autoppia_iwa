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
1. Begin your prompt with "Switch to month view" or similar phrases
2. Only mention changing the calendar view to month view
3. Do not include other calendar interactions like adding events or selecting specific dates
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
1. Begin your prompt with "Switch to week view" or similar phrases
2. Only mention changing the calendar view to week view
3. Do not include other calendar interactions like adding events or selecting specific dates
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
1. Begin your prompt with "Switch to 5-day view" or similar phrases
2. Only mention changing the calendar view to 5-day view
3. Do not include other calendar interactions like adding events or selecting specific dates
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
1. Begin your prompt with "Switch to day view" or similar phrases
2. Only mention changing the calendar view to single day view
3. Do not include other calendar interactions like adding events or selecting specific dates
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
1. Begin your prompt with phrases like "Go to today" or "Jump to today's date"
2. Focus only on navigating to today's date in the calendar
3. Do not include other calendar interactions like adding events or changing views
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
1. Begin your prompt with phrases like "Create a new calendar" or "Add a calendar"
2. Only focus on initiating the calendar creation process
3. Do not include details about calendar settings, those come in the CREATE_CALENDAR event
"""

ADD_NEW_CALENDAR_USE_CASE = UseCase(
    name="ADD_NEW_CALENDAR",
    description="Triggered when the user opens the modal to add a new calendar.",
    event=AddNewCalendarEvent,
    event_source_code=AddNewCalendarEvent.get_source_code_of_class(),
    constraints_generator=False,
    additional_prompt_info=ADD_NEW_CALENDAR_INFO,
    examples=[
        {"prompt": "I want to add a new calendar.", "prompt_for_task_generation": "Open the add new calendar modal."},
        {"prompt": "Create a new calendar for me.", "prompt_for_task_generation": "Open interface to create new calendar."},
        {"prompt": "Add another calendar to my account.", "prompt_for_task_generation": "Add new calendar to the sidebar."},
        {"prompt": "I need a new calendar category.", "prompt_for_task_generation": "Create new calendar category."},
        {"prompt": "Open the dialog to add a new calendar.", "prompt_for_task_generation": "Open add calendar dialog."},
    ],
)

###############################################################################
# CREATE_CALENDAR_USE_CASE
###############################################################################

CREATE_CALENDAR_INFO = """
CRITICAL REQUIREMENT:
1. Include specific calendar details: name, description, and color
2. The prompt should express completion of calendar creation with these details
3. Be sure to mention the calendar color using the exact hex code if specified in constraints
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
            "prompt": "Create a 'Work' calendar with blue color (#2196F3) for my job-related events.",
            "prompt_for_task_generation": "Create calendar named 'Work' with blue color (#2196F3) and description for job events.",
        },
        {
            "prompt": "Make a new 'Family' calendar in red (#E53935) to track family activities.",
            "prompt_for_task_generation": "Create 'Family' calendar with red color (#E53935) for family activities.",
        },
        {
            "prompt": "Set up a 'Fitness' calendar in green (#4CAF50) for my workout schedule.",
            "prompt_for_task_generation": "Create 'Fitness' calendar with green color (#4CAF50) for workout tracking.",
        },
        {"prompt": "Create a 'Travel' calendar with purple (#9C27B0) to plan my trips.", "prompt_for_task_generation": "Create 'Travel' calendar with purple color (#9C27B0) for trip planning."},
        {
            "prompt": "Make a 'Study' calendar with yellow (#FDD835) for my classes and assignments.",
            "prompt_for_task_generation": "Create 'Study' calendar with yellow color (#FDD835) for academic planning.",
        },
    ],
)

###############################################################################
# CHOOSE_CALENDAR_USE_CASE
###############################################################################

CHOOSE_CALENDAR_INFO = """
CRITICAL REQUIREMENT:
1. Clearly state whether you want to show or hide a specific calendar.
2. Use the calendar name exactly as provided in the constraints.
3. If the calendar name is not 'Work' or 'Family', first request to create the calendar, then request to select or unselect it.
Examples:
{'calendar_name': 'Work', 'selected': false} -> "Unselect the 'Work' calendar."
{'calendar_name': 'Personal', 'selected': false} -> "First, create a new calendar named 'Personal', then unselect it."
"""

CHOOSE_CALENDAR_USE_CASE = UseCase(
    name="CHOOSE_CALENDAR",
    description="Triggered when the user selects or deselects a calendar from the sidebar.",
    event=ChooseCalendarEvent,
    event_source_code=ChooseCalendarEvent.get_source_code_of_class(),
    constraints_generator=generate_choose_calendar_constraints,
    additional_prompt_info=CHOOSE_CALENDAR_INFO,
    examples=[
        {"prompt": "Show my Family calendar with red color (#E53935).", "prompt_for_task_generation": "Select the Family calendar with red color (#E53935)."},
        {"prompt": "Hide the Work calendar.", "prompt_for_task_generation": "Deselect the Work calendar."},
        {"prompt": "Make the blue Personal calendar visible.", "prompt_for_task_generation": "Show the Personal calendar with blue color."},
        {"prompt": "I don't want to see the Study calendar right now.", "prompt_for_task_generation": "Hide the Study calendar."},
        {"prompt": "Display the yellow Holiday calendar (#FDD835).", "prompt_for_task_generation": "Select the Holiday calendar with yellow color (#FDD835)."},
    ],
)

###############################################################################
# ADD_EVENT_USE_CASE
###############################################################################

ADD_EVENT_INFO = """
CRITICAL REQUIREMENT:
1. Include all event details: title, calendar, date, start time, end time
2. Format times as hours and minutes (e.g., "5:30 PM", "17:30")
3. Specify which calendar the event should be added to
4. If color is specified in constraints, mention it using the exact hex code
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
            "prompt": "Add a meeting titled 'Team Sync' to my Work calendar on August 10th from 2:00 PM to 3:00 PM.",
            "prompt_for_task_generation": "Add 'Team Sync' event to Work calendar on August 10 from 14:00 to 15:00.",
        },
        {
            "prompt": "Create a 'Doctor Appointment' in my Personal calendar for July 15th at 10:30 AM lasting 1 hour.",
            "prompt_for_task_generation": "Add 'Doctor Appointment' to Personal calendar on July 15 at 10:30 for 1 hour.",
        },
        {
            "prompt": "Schedule 'Dinner with Friends' in my Social calendar on Friday at 7:00 PM until 9:00 PM.",
            "prompt_for_task_generation": "Add 'Dinner with Friends' to Social calendar on Friday from 19:00 to 21:00.",
        },
        {
            "prompt": "Add 'Gym Session' to my Fitness calendar tomorrow morning from 6:30 AM to 7:30 AM.",
            "prompt_for_task_generation": "Schedule 'Gym Session' in Fitness calendar tomorrow 6:30-7:30.",
        },
        {
            "prompt": "Create a 'Project Deadline' event in my Work calendar (blue color) on August 25th all day.",
            "prompt_for_task_generation": "Add all-day 'Project Deadline' event to Work calendar (blue) on August 25.",
        },
    ],
)

###############################################################################
# CELL_CLICKED_USE_CASE
###############################################################################

CELL_CLICKED_INFO = """
CRITICAL REQUIREMENT:
1. Clearly indicate selecting a specific date or time slot in the calendar
2. Specify the view type (Month, Week, Day) where the selection is happening
3. For week or day views, include the specific hour if available in constraints
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
        {"prompt": "Click on the 3 PM time slot for Wednesday in week view.", "prompt_for_task_generation": "Select Wednesday at 15:00 in week view."},
        {"prompt": "I want to check August 7th in the calendar.", "prompt_for_task_generation": "Click on August 7 in the calendar."},
        {"prompt": "Select 9:00 AM on Monday in day view.", "prompt_for_task_generation": "Click Monday 9:00 AM slot in day view."},
        {"prompt": "Navigate to next Tuesday's afternoon slot around 2 PM.", "prompt_for_task_generation": "Select Tuesday at 14:00 in the calendar."},
    ],
)

###############################################################################
# CANCEL_ADD_EVENT_USE_CASE
###############################################################################

CANCEL_ADD_EVENT_INFO = """
CRITICAL REQUIREMENT:
1. Explicitly mention canceling or abandoning event creation
2. If title or date is specified in constraints, include that information
3. Make clear that the user is stopping the event creation process
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
        {"prompt": "I changed my mind, don't add the 'Meeting' event.", "prompt_for_task_generation": "Cancel adding the 'Meeting' event."},
        {"prompt": "Close the event form without saving.", "prompt_for_task_generation": "Close event form without creating the event."},
        {"prompt": "Discard the event scheduled for August 7th.", "prompt_for_task_generation": "Cancel the event creation for August 7th."},
        {"prompt": "Exit event creation. I don't want to add this anymore.", "prompt_for_task_generation": "Exit the event creation modal without saving."},
    ],
)
###############################################################################
# DELETE_ADDED_EVENT_USE_CASE
###############################################################################

DELETE_ADDED_EVENT_INFO = """
CRITICAL REQUIREMENT:
1. Explicitly mention deleting or removing an existing event from the calendar
2. Include the event title if specified in constraints
3. Optionally mention the date or calendar name if specified in constraints
4. Make clear that the user is removing an already created event (not canceling event creation)
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
        {"prompt": "Remove my dentist appointment scheduled on August 15th.", "prompt_for_task_generation": "Delete dentist appointment event from August 15."},
        {"prompt": "I need to delete the 'Conference Call' from my Work calendar.", "prompt_for_task_generation": "Delete 'Conference Call' event from Work calendar."},
        {"prompt": "Please remove the lunch meeting I scheduled for tomorrow.", "prompt_for_task_generation": "Delete lunch meeting event scheduled for tomorrow."},
        {"prompt": "Delete the 'Project Review' event from my calendar.", "prompt_for_task_generation": "Remove 'Project Review' event from calendar."},
    ],
)
ALL_USE_CASES = [
    SELECT_MONTH_USE_CASE,
    SELECT_WEEK_USE_CASE,
    SELECT_FIVE_DAYS_USE_CASE,
    SELECT_DAY_USE_CASE,
    SELECT_TODAY_USE_CASE,
    ADD_NEW_CALENDAR_USE_CASE,
    CREATE_CALENDAR_USE_CASE,
    CHOOSE_CALENDAR_USE_CASE,
    ADD_EVENT_USE_CASE,
    CELL_CLICKED_USE_CASE,
    CANCEL_ADD_EVENT_USE_CASE,
    DELETE_ADDED_EVENT_USE_CASE,
]
