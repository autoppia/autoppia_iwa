from ...classes import UseCase
from .events import (
    AddEventEvent,
    AddNewCalendarEvent,
    CancelAddEventEvent,
    CellClickedEvent,
    ChooseCalendarEvent,
    CreateCalendarEvent,
    DeleteAddedEventEvent,
    EventAddAttendeeEvent,
    EventAddReminderEvent,
    EventRemoveAttendeeEvent,
    EventRemoveReminderEvent,
    EventWizardOpenEvent,
    SearchSubmitEvent,
    SelectDayEvent,
    SelectFiveDaysEvent,
    SelectMonthEvent,
    SelectTodayEvent,
    SelectWeekEvent,
)
from .generation_functions import (
    generate_add_event_constraints,
    generate_cell_clicked_constraints,
    generate_choose_calendar_constraints,
    generate_create_calendar_constraints,
    generate_event_attendee_constraints,
    generate_event_reminder_constraints,
    generate_event_wizard_open_constraints,
    generate_search_submit_constraints,
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
1. Begin your prompt with "Switch to day view ..." or "Show me ...".
2. Focus only changing the calendar view to day view.
3. do not include any additional information like date and time.
"""

SELECT_DAY_USE_CASE = UseCase(
    name="SELECT_DAY",
    description="User switches to the day view in the calendar.",
    event=SelectDayEvent,
    event_source_code=SelectDayEvent.get_source_code_of_class(),
    constraints_generator=False,
    additional_prompt_info=SELECT_DAY_INFO,
    examples=[
        {"prompt": "Switch to day view please.", "prompt_for_task_generation": "Switch to day view please."},
        {"prompt": "Switch to day view in the calendar.", "prompt_for_task_generation": "Switch to day view in calendar."},
        {"prompt": "Show me day schedule in detail.", "prompt_for_task_generation": "Show me day schedule in detail."},
        {"prompt": "Show me the calendar to single day view.", "prompt_for_task_generation": "Show me calendar to single day view."},
        # {"prompt": "Can you zoom in to just show one day?", "prompt_for_task_generation": "Zoom to single day view."},
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
2. Start your request with "Create a new calendar" or similar phrases.
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
import json

from .data import EXISTING_CALENDAR_NAMES

CHOOSE_CALENDAR_INFO = f"""
CRITICAL REQUIREMENTS:
1. The prompt must focus on deselecting a calendar (the 'selected' constraint is always false).
2. Use the calendar name exactly as provided in the constraints (e.g., `Personal`, `Fitness`).
   Example: For {{'calendar_name': 'Personal', 'selected': False}} → "Unselect the 'Personal' calendar."
3. If the calendar name is not in the list of existing calendar names, or a substring of those, mention in the prompt to first create that calendar, then unselect it.
   Existing Calendar Names: {json.dumps(EXISTING_CALENDAR_NAMES)}
4. If the constraint uses an operator (e.g., 'contains'), clearly mention it in the prompt.
   Example: {{'calendar_name': {{'operator': 'contains', 'value': 've'}}, 'selected': False}}
   Correct: "Unselect the calendar that contains 've' in its name."
   Incorrect: "Unselect the calendar 've' name, but first create it if it doesn't exist." (constraint not mentioned)
5. **Do not** mention the constraint for 'selected' in the prompt.
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
        {"prompt": "Unselect the calendar that contains 've' in its name.", "prompt_for_task_generation": "Deselect any calendar whose name contains 've'."},
        {"prompt": "First create the 'Projects' calendar, then unselect it.", "prompt_for_task_generation": "Create 'Projects' calendar if missing, then deselect it."},
        {"prompt": "If the 'Events' calendar does not exist, create it, then hide it.", "prompt_for_task_generation": "Create 'Events' calendar if needed, then hide it."},
    ],
)

###############################################################################
# ADD_EVENT_USE_CASE
###############################################################################

ADD_EVENT_INFO = """
CRITICAL REQUIREMENT:
1. Include all event details: title, calendar, date, start time, and end time.
2. Start your request with "Add an event" or similar phrases.
3. Pay attention to the constraints, mentioning exact constraint operator is crucial,
Example:
constraint: {"field": "title", "operator": "not_equals", "value": "Team Meeting"}
prompt:
CORRECT: 'Add an event whose title is not "Team Meeting" to the "Work" calendar for tomorrow at 10:00 AM, ending at 11:00 AM.'
INCORRECT: 'Add an event "Team Meeting" to the "Work" calendar for tomorrow at 10:00 AM, ending at 11:00 AM.'
4. You may use synonyms for "add" such as "schedule", "create", "put", or "set up".
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
            "prompt": "Add an event 'Team Meeting' to the 'Work' calendar for tomorrow at 10:00 AM, ending at 11:00 AM.",
            "prompt_for_task_generation": "Create event 'Team Meeting' in 'Work' calendar for tomorrow, 10:00 AM to 11:00 AM.",
        },
        {
            "prompt": "Schedule 'Doctor Appointment' on the 'Personal' calendar for July 25th from 2:30 PM to 3:00 PM.",
            "prompt_for_task_generation": "Add event 'Doctor Appointment' to 'Personal' calendar on July 25th, 2:30 PM - 3:00 PM.",
        },
        {
            "prompt": "New event in 'Fitness' calendar: 'Gym Session', today from 18:00 to 19:30.",
            "prompt_for_task_generation": "Create event 'Gym Session' in 'Fitness' calendar, today, 18:00-19:30.",
        },
        {
            "prompt": "Add 'Family Dinner' to the 'Family' calendar for this Friday at 7 PM, lasting one hour.",
            "prompt_for_task_generation": "Add event 'Family Dinner' to 'Family' calendar, this Friday, 7:00 PM to 8:00 PM.",
        },
        {
            "prompt": "Put 'Project Deadline' on the 'Work' calendar for August 1st, starting at 9 AM and ending at 5 PM.",
            "prompt_for_task_generation": "Create event 'Project Deadline' in 'Work' calendar for August 1st, 9:00 AM - 5:00 PM.",
        },
    ],
)

###############################################################################
# CELL_CLICKED_USE_CASE
###############################################################################

CELL_CLICKED_INFO = """
CRITICAL REQUIREMENT:
1. Clearly indicate selecting a specific date or time slot in the calendar by starting the request with "Click on cell" or similar.
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
    constraints_generator=generate_add_event_constraints,
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
5. The event does not exists, mention to create an event first and then delete it.
"""

DELETE_ADDED_EVENT_USE_CASE = UseCase(
    name="DELETE_ADDED_EVENT",
    description="Triggered when the user deletes an existing calendar event.",
    event=DeleteAddedEventEvent,
    event_source_code=DeleteAddedEventEvent.get_source_code_of_class(),
    constraints_generator=generate_add_event_constraints,
    additional_prompt_info=DELETE_ADDED_EVENT_INFO,
    examples=[
        {"prompt": "Delete the 'Team Meeting' event from my calendar.", "prompt_for_task_generation": "Remove 'Team Meeting' event from calendar."},
        {"prompt": "Remove the 'Doctor appointment' on the 15th.", "prompt_for_task_generation": "Delete 'Doctor appointment' on the 15th."},
        {"prompt": "I want to delete the 'Lunch' event from my 'Personal' calendar.", "prompt_for_task_generation": "Delete 'Lunch' event from 'Personal' calendar."},
        {"prompt": "Please remove the 'Conference call' event.", "prompt_for_task_generation": "Delete the 'Conference call' event."},
        {"prompt": "Delete the event titled 'Workout' for today.", "prompt_for_task_generation": "Remove the 'Workout' event scheduled for today."},
    ],
)

###############################################################################
# EVENT_WIZARD_OPEN_USE_CASE
###############################################################################

EVENT_WIZARD_OPEN_INFO = """
CRITICAL REQUIREMENT:
1. The prompt must be about opening the event creation or editing form, starting the requests with phrases like "Open the form to add ..." or "Open the event ...".
2. Do not mention submitting or saving the event. The focus is on opening the wizard.
"""

EVENT_WIZARD_OPEN_USE_CASE = UseCase(
    name="EVENT_WIZARD_OPEN",
    description="Triggered when the user opens the event creation or editing wizard.",
    event=EventWizardOpenEvent,
    event_source_code=EventWizardOpenEvent.get_source_code_of_class(),
    constraints_generator=generate_event_wizard_open_constraints,
    additional_prompt_info=EVENT_WIZARD_OPEN_INFO,
    examples=[
        {"prompt": "Open the form to add a new event.", "prompt_for_task_generation": "Open the new event wizard."},
        {"prompt": "I want to edit the 'Team Meeting' event.", "prompt_for_task_generation": "Open the event wizard to edit 'Team Meeting'."},
        {"prompt": "Click the 'add event' button.", "prompt_for_task_generation": "Open the event creation form."},
        {"prompt": "Modify the details for the 'Doctor Appointment'.", "prompt_for_task_generation": "Open the event editor for 'Doctor Appointment'."},
        {"prompt": "Let's schedule a new event.", "prompt_for_task_generation": "Open the event wizard for a new event."},
    ],
)

###############################################################################
# SEARCH_SUBMIT_USE_CASE
###############################################################################

SEARCH_SUBMIT_INFO = """
CRITICAL REQUIREMENT:
1. The prompt must explicitly mention searching for something.
2. Include the search query in the prompt.
"""

SEARCH_SUBMIT_USE_CASE = UseCase(
    name="SEARCH_SUBMIT",
    description="Triggered when the user submits a search query.",
    event=SearchSubmitEvent,
    event_source_code=SearchSubmitEvent.get_source_code_of_class(),
    constraints_generator=generate_search_submit_constraints,
    additional_prompt_info=SEARCH_SUBMIT_INFO,
    examples=[
        {"prompt": "Search for 'work'", "prompt_for_task_generation": "Search for 'work'"},
        {"prompt": "Find events with 'meeting'", "prompt_for_task_generation": "Search for 'meeting'"},
        {"prompt": "Look up 'dentist appointment'", "prompt_for_task_generation": "Search for 'dentist appointment'"},
        {"prompt": "Show me all events related to 'project'", "prompt_for_task_generation": "Search for 'project'"},
        {"prompt": "Find 'lunch'", "prompt_for_task_generation": "Search for 'lunch'"},
    ],
)

###############################################################################
# EVENT_ADD_REMINDER_USE_CASE
###############################################################################

EVENT_ADD_REMINDER_INFO = """
CRITICAL REQUIREMENT:
1. The prompt must explicitly mention adding a reminder to an event.
2. Specify the time for the reminder in minutes. If the time is 60 minutes, mention the reminder as 1 hour; for 120 minutes, mention as 2 hours; for 1440 minutes, mention as 1 day.
3. Do not include other event details like title or date.
4. Do not mention the same constraint more than once in the prompt.
Examples:
Constraint: {'minutes': {'operator': 'greater_than', 'value': 59}}
CORRECT: "Please add a reminder to the event where the time in minutes is greater than 59."
CORRECT: "Please add a reminder to the event for 1 hour in advance."
INCORRECT: "Please add a reminder to the event for 1 hour in advance where the time in minutes is greater than 59."
"""

EVENT_ADD_REMINDER_USE_CASE = UseCase(
    name="EVENT_ADD_REMINDER",
    description="Triggered when a reminder is added to an event.",
    event=EventAddReminderEvent,
    event_source_code=EventAddReminderEvent.get_source_code_of_class(),
    constraints_generator=generate_event_reminder_constraints,
    additional_prompt_info=EVENT_ADD_REMINDER_INFO,
    examples=[
        {"prompt": "Add a 30-minute reminder to the event.", "prompt_for_task_generation": "Add a 30-minute reminder."},
        {"prompt": "Set a reminder for 10 minutes before.", "prompt_for_task_generation": "Add a 10-minute reminder."},
        {"prompt": "I need a reminder 1 hour before.", "prompt_for_task_generation": "Add a 60-minute reminder."},
        {"prompt": "Remind me 15 minutes prior.", "prompt_for_task_generation": "Add a 15-minute reminder."},
        {"prompt": "Add a 2-hour reminder.", "prompt_for_task_generation": "Add a 120-minute reminder."},
    ],
)

###############################################################################
# EVENT_REMOVE_REMINDER_USE_CASE
###############################################################################

EVENT_REMOVE_REMINDER_INFO = """
CRITICAL REQUIREMENT:
1. The prompt must explicitly mention removing or deleting a reminder from an event.
2. To remove a reminder, it must first exist. If the reminder to be removed does not exist, first add it, and then remove it.
3. Specify the time for the reminder in minutes. If the time is 60 minutes, mention the reminder as 1 hour; for 120 minutes, mention as 2 hours; for 1440 minutes, mention as 1 day.
4. Do not include other event details like title or date.
5. Do not mention the same constraint more than once in the prompt.
Examples:
Constraint: {'minutes': {'operator': 'greater_than', 'value': 59}}
CORRECT: "Please remove the reminder from the event where the time in minutes is greater than 59."
CORRECT: "Please remove the 1-hour reminder from the event. If it does not exist, add it first and then remove it."
INCORRECT: "Please remove the 1-hour reminder from the event where the time in minutes is greater than 59."
"""

EVENT_REMOVE_REMINDER_USE_CASE = UseCase(
    name="EVENT_REMOVE_REMINDER",
    description="Triggered when a reminder is removed from an event.",
    event=EventRemoveReminderEvent,
    event_source_code=EventRemoveReminderEvent.get_source_code_of_class(),
    constraints_generator=generate_event_reminder_constraints,
    additional_prompt_info=EVENT_REMOVE_REMINDER_INFO,
    examples=[
        {
            "prompt": "Remove the 30-minute reminder. If it's not there, add it first, then remove it.",
            "prompt_for_task_generation": "Remove the 30-minute reminder, creating it first if it does not exist.",
        },
        {
            "prompt": "Delete the 10-minute reminder. If it doesn't exist, create it and then delete it.",
            "prompt_for_task_generation": "Remove the 10-minute reminder, creating it first if it does not exist.",
        },
        {
            "prompt": "I don't need the 1-hour reminder anymore. Please remove it. If it's not set, add it and then remove it.",
            "prompt_for_task_generation": "Remove the 60-minute reminder, creating it first if it does not exist.",
        },
        {
            "prompt": "Get rid of the 15-minute reminder. If one isn't there, make one and then delete it.",
            "prompt_for_task_generation": "Remove the 15-minute reminder, creating it first if it does not exist.",
        },
        {
            "prompt": "Cancel the 2-hour reminder. If it doesn't exist, add it and then cancel it.",
            "prompt_for_task_generation": "Remove the 120-minute reminder, creating it first if it does not exist.",
        },
    ],
)

###############################################################################
# EVENT_ADD_ATTENDEE_USE_CASE
###############################################################################

EVENT_ADD_ATTENDEE_INFO = """
CRITICAL REQUIREMENT:
1. The prompt must explicitly mention adding an attendee to an event.
2. Specify the email address of the attendee to be added.
"""

EVENT_ADD_ATTENDEE_USE_CASE = UseCase(
    name="EVENT_ADD_ATTENDEE",
    description="Triggered when an attendee is added to an event.",
    event=EventAddAttendeeEvent,
    event_source_code=EventAddAttendeeEvent.get_source_code_of_class(),
    constraints_generator=generate_event_attendee_constraints,
    additional_prompt_info=EVENT_ADD_ATTENDEE_INFO,
    examples=[
        {"prompt": "Add 'test@example.com' as an attendee.", "prompt_for_task_generation": "Add attendee 'test@example.com'."},
        {"prompt": "Invite 'user1@work.com' to this event.", "prompt_for_task_generation": "Add attendee 'user1@work.com'."},
        {"prompt": "Include 'friend@email.net' in the guest list.", "prompt_for_task_generation": "Add attendee 'friend@email.net'."},
        {"prompt": "Add attendee with email 'contact@domain.org'.", "prompt_for_task_generation": "Add attendee 'contact@domain.org'."},
        {"prompt": "Put 'another.user@email.com' on the invite list.", "prompt_for_task_generation": "Add attendee 'another.user@email.com'."},
    ],
)

###############################################################################
# EVENT_REMOVE_ATTENDEE_USE_CASE
###############################################################################

EVENT_REMOVE_ATTENDEE_INFO = """
CRITICAL REQUIREMENT:
1. The prompt must explicitly mention removing an attendee from an event.
2. Specify the email address of the attendee to be removed.
"""

EVENT_REMOVE_ATTENDEE_USE_CASE = UseCase(
    name="EVENT_REMOVE_ATTENDEE",
    description="Triggered when an attendee is removed from an event.",
    event=EventRemoveAttendeeEvent,
    event_source_code=EventRemoveAttendeeEvent.get_source_code_of_class(),
    constraints_generator=generate_event_attendee_constraints,
    additional_prompt_info=EVENT_REMOVE_ATTENDEE_INFO,
    examples=[
        {"prompt": "Remove 'test@example.com' from the attendees.", "prompt_for_task_generation": "Remove attendee 'test@example.com'."},
        {"prompt": "Uninvite 'user1@work.com' from this event.", "prompt_for_task_generation": "Remove attendee 'user1@work.com'."},
        {"prompt": "Take 'friend@email.net' off the guest list.", "prompt_for_task_generation": "Remove attendee 'friend@email.net'."},
        {"prompt": "Remove attendee with email 'contact@domain.org'.", "prompt_for_task_generation": "Remove attendee 'contact@domain.org'."},
        {"prompt": "Delete 'another.user@email.com' from the invite list.", "prompt_for_task_generation": "Remove attendee 'another.user@email.com'."},
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
    SEARCH_SUBMIT_USE_CASE,
    EVENT_WIZARD_OPEN_USE_CASE,
    CELL_CLICKED_USE_CASE,
    ADD_EVENT_USE_CASE,
    CANCEL_ADD_EVENT_USE_CASE,
    DELETE_ADDED_EVENT_USE_CASE,
    EVENT_ADD_REMINDER_USE_CASE,
    EVENT_REMOVE_REMINDER_USE_CASE,
    EVENT_ADD_ATTENDEE_USE_CASE,
    EVENT_REMOVE_ATTENDEE_USE_CASE,
]
