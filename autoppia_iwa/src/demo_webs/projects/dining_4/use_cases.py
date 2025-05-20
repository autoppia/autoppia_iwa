from datetime import UTC, date, datetime

from ...classes import UseCase
from .events import (
    BookRestaurantEvent,
    CollapseMenuEvent,
    CountrySelectedEvent,
    DateDropdownOpenedEvent,
    OccasionSelectedEvent,
    PeopleDropdownOpenedEvent,
    ReservationCompleteEvent,
    ScrollViewEvent,
    SearchRestaurantEvent,
    TimeDropdownOpenedEvent,
    ViewFullMenuEvent,
    ViewRestaurantEvent,
)
from .generation_functions import (
    generate_book_restaurant_constraints,
    generate_collapse_menu_constraints,
    generate_country_selected_constraints,
    generate_date_dropdown_opened_constraints,
    generate_occasion_selected_constraints,
    generate_people_dropdown_opened_constraints,
    generate_reservation_complete_constraints,
    generate_scroll_view_constraints,
    generate_search_restaurant_constraints,
    generate_time_dropdown_opened_constraints,
    generate_view_full_menu_constraints,
    generate_view_restaurant_constraints,
)
from .replace_functions import replace_restaurant_placeholders

###############################################################################
# DATE_DROPDOWN_OPENED_USE_CASE
###############################################################################

DATE_DROPDOWN_OPENED_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Indicate interaction with a date selection UI element (e.g., "Open date picker", "Focus on the date field").
2. The event captures the date displayed/selected when the interaction occurs.
3. The prompt should lead to the DATE_DROPDOWN_OPENED event.
"""

DATE_DROPDOWN_OPENED_USE_CASE = UseCase(
    name="DATE_DROPDOWN_OPENED",
    description="User interacts with (opens or focuses on) a date selection dropdown/input, which is often pre-filled.",
    event=DateDropdownOpenedEvent,
    event_source_code=DateDropdownOpenedEvent.get_source_code_of_class(),
    additional_prompt_info=DATE_DROPDOWN_OPENED_INFO,
    constraints_generator=generate_date_dropdown_opened_constraints,
    examples=[
        {
            "prompt": "Open the date selector for my booking.",
            "prompt_for_task_generation": "Open the date selector for my booking.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DATE_DROPDOWN_OPENED",
                "event_criteria": {"selected_date": {"value": datetime(2025, 4, 30, 19, 0, 0, tzinfo=UTC), "operator": "equals"}},
                "reasoning": "User opens the date picker, which shows a default/current date.",
            },
        },
        {
            "prompt": "Click on the calendar icon to select a date after June 15th.",
            "prompt_for_task_generation": "Click on the calendar icon to select a date after <date>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DATE_DROPDOWN_OPENED",
                "event_criteria": {"selected_date": {"value": datetime(2025, 6, 15, 0, 0, 0, tzinfo=UTC), "operator": "greater_than"}},
                "reasoning": "User opens date picker with intention to select a future date.",
            },
        },
    ],
)

###############################################################################
# TIME_DROPDOWN_OPENED_USE_CASE
###############################################################################

TIME_DROPDOWN_OPENED_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Indicate interaction with a time selection UI element.
2. The event captures the time displayed/selected upon interaction.
3. The prompt should lead to the TIME_DROPDOWN_OPENED event.
"""

TIME_DROPDOWN_OPENED_USE_CASE = UseCase(
    name="TIME_DROPDOWN_OPENED",
    description="User interacts with (opens or focuses on) a time selection dropdown/input.",
    event=TimeDropdownOpenedEvent,
    event_source_code=TimeDropdownOpenedEvent.get_source_code_of_class(),
    additional_prompt_info=TIME_DROPDOWN_OPENED_INFO,
    constraints_generator=generate_time_dropdown_opened_constraints,
    replace_func=replace_restaurant_placeholders,
    examples=[
        {
            "prompt": "Click on the time field to choose a reservation time.",
            "prompt_for_task_generation": "Click on the time field to choose a reservation time.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "TIME_DROPDOWN_OPENED",
                "event_criteria": {"selected_time": {"value": "12:30 PM", "operator": "equals"}},
                "reasoning": "User opens the time picker, which shows a default/current time.",
            },
        }
    ],
)

###############################################################################
# PEOPLE_DROPDOWN_OPENED_USE_CASE
###############################################################################

PEOPLE_DROPDOWN_OPENED_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Indicate interaction with a 'number of people' or 'guests' selection UI element.
2. The event captures the count displayed/selected upon interaction.
3. The prompt should lead to the PEOPLE_DROPDOWN_OPENED event.
"""

PEOPLE_DROPDOWN_OPENED_USE_CASE = UseCase(
    name="PEOPLE_DROPDOWN_OPENED",
    description="User interacts with (opens or focuses on) a dropdown to select the number of people/guests.",
    event=PeopleDropdownOpenedEvent,
    event_source_code=PeopleDropdownOpenedEvent.get_source_code_of_class(),
    additional_prompt_info=PEOPLE_DROPDOWN_OPENED_INFO,
    constraints_generator=generate_people_dropdown_opened_constraints,
    replace_func=replace_restaurant_placeholders,
    examples=[
        {
            "prompt": "Open the guest number selection for my table.",
            "prompt_for_task_generation": "Open the guest number selection for my table.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "PEOPLE_DROPDOWN_OPENED",
                "event_criteria": {"people_count": {"value": 4, "operator": "equals"}},
                "reasoning": "User opens the people picker, showing a default/current count.",
            },
        },
        {
            "prompt": "Select the party size dropdown for a group larger than 6 people.",
            "prompt_for_task_generation": "Select the party size dropdown for a group larger than <count> people.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "PEOPLE_DROPDOWN_OPENED",
                "event_criteria": {
                    "people_count": {"value": 6, "operator": "greater_than"},
                    "reasoning": "User opens people picker looking for large group options.",
                },
            },
        },
    ],
)

###############################################################################
# SEARCH_RESTAURANT_USE_CASE
###############################################################################

SEARCH_RESTAURANT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Make it EXPLICIT that this is a SEARCH for RESTAURANTS using clear terms like:
    - "Search for restaurants..."
    - "Find restaurants..."
    - "Look up places to eat..."
2. Include ONLY the search query for the restaurant or cuisine type.
3. DO NOT include any other filters like date/time/people in this specific search action.
"""

SEARCH_RESTAURANT_USE_CASE = UseCase(
    name="SEARCH_RESTAURANT",
    description="The user searches for restaurants using a search query.",
    event=SearchRestaurantEvent,
    event_source_code=SearchRestaurantEvent.get_source_code_of_class(),
    constraints_generator=generate_search_restaurant_constraints,
    additional_prompt_info=SEARCH_RESTAURANT_INFO,
    examples=[
        {
            "prompt": "Search for 'italian restaurants in downtown'",
            "prompt_for_task_generation": "Search for 'italian restaurants in downtown'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_RESTAURANT",
                "event_criteria": {"query": {"value": "italian restaurants in downtown", "operator": "equals"}},
                "reasoning": "Explicit search for restaurants matching cuisine and location hint.",
            },
        },
        {
            "prompt": "Find restaurants named 'The Royal Dine'",
            "prompt_for_task_generation": "Find restaurants named '<query>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_RESTAURANT",
                "event_criteria": {"query": {"value": "The Royal Dine", "operator": "equals"}},
                "reasoning": "Search for a specific restaurant name.",
            },
        },
        {
            "prompt": "Look up places to eat that serve vegan food",
            "prompt_for_task_generation": "Look up places to eat that serve <query> food",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_RESTAURANT",
                "event_criteria": {"query": {"value": "vegan", "operator": "contains"}},
                "reasoning": "Search for restaurants with specific dietary options.",
            },
        },
        {
            "prompt": "Search for restaurants with outdoor seating in midtown",
            "prompt_for_task_generation": "Search for restaurants with <query> in midtown",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_RESTAURANT",
                "event_criteria": {"query": {"value": "outdoor seating", "operator": "contains"}},
                "reasoning": "Search for restaurants with specific features.",
            },
        },
    ],
)

###############################################################################
# VIEW_RESTAURANT_USE_CASE
###############################################################################

VIEW_RESTAURANT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Be phrased as a request to **view details** of a specific restaurant (use phrases like "Show details for...", "View restaurant page for...", etc.)
2. Only use restaurant attributes like name or ID if provided in constraints.
3. Lead to the VIEW_RESTAURANT event.
"""

VIEW_RESTAURANT_USE_CASE = UseCase(
    name="VIEW_RESTAURANT",
    description="The user explicitly requests to view the details page of a specific restaurant.",
    event=ViewRestaurantEvent,
    event_source_code=ViewRestaurantEvent.get_source_code_of_class(),
    constraints_generator=generate_view_restaurant_constraints,
    additional_prompt_info=VIEW_RESTAURANT_INFO,
    replace_func=replace_restaurant_placeholders,
    examples=[
        {
            "prompt": "Show me details for 'The Royal Dine'",
            "prompt_for_task_generation": "Show me details for '<restaurant_name>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_RESTAURANT",
                "event_criteria": {
                    "restaurant_name": {"value": "The Royal Dine", "operator": "equals"},
                    "restaurant_id": {"value": "royal-dine", "operator": "equals"},  # Based on your JSON
                },
                "reasoning": "Explicitly requests to view details for a specific restaurant by name.",
            },
        },
        {
            "prompt": "View restaurant page for ID 'royal-dine'",
            "prompt_for_task_generation": "View restaurant page for ID '<restaurant_id>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_RESTAURANT",
                "event_criteria": {"restaurant_id": {"value": "royal-dine", "operator": "equals"}},
                "reasoning": "Requests to view restaurant details using its ID.",
            },
        },
        {
            "prompt": "Show me the page for a restaurant with rating above 4.5",
            "prompt_for_task_generation": "Show me the page for a restaurant with rating above <rating>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_RESTAURANT",
                "event_criteria": {"rating": {"value": 4.5, "operator": "greater_than"}},
                "reasoning": "Requests to view highly-rated restaurants.",
            },
        },
        {
            "prompt": "View details for restaurants that serve sushi",
            "prompt_for_task_generation": "View details for restaurants that serve <cuisine>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_RESTAURANT",
                "event_criteria": {"cuisine": {"value": "sushi", "operator": "contains"}},
                "reasoning": "Requests to view restaurants serving specific cuisine.",
            },
        },
    ],
)

###############################################################################
# VIEW_FULL_MENU_USE_CASE
###############################################################################

VIEW_FULL_MENU_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Clearly ask to see the **full menu** for a specified restaurant.
2. May include contextual information like preferred date, time, and number of people if these affect menu availability or display.
3. Lead to the VIEW_FULL_MENU event.
"""

VIEW_FULL_MENU_USE_CASE = UseCase(
    name="VIEW_FULL_MENU",
    description="User requests to view the full menu of a specific restaurant, possibly with booking context.",
    event=ViewFullMenuEvent,
    event_source_code=ViewFullMenuEvent.get_source_code_of_class(),
    additional_prompt_info=VIEW_FULL_MENU_INFO,
    constraints_generator=generate_view_full_menu_constraints,
    examples=[
        {
            "prompt": "Show the full menu for 'The Royal Dine' for 2 people for dinner on July 18.",
            "prompt_for_task_generation": "Show the full menu for '<restaurant_name>' for <people_count> people for <meal_time> on <date_description>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_FULL_MENU",
                "event_criteria": {
                    "restaurant_name": {"value": "The Royal Dine", "operator": "equals"},
                    "people": {"value": 2, "operator": "equals"},
                    "selected_date": {"value": date(2024, 7, 18), "operator": "equals"},
                    "time": {"value": "1:00 PM", "operator": "equals"},
                },
                "reasoning": "Requests full menu with booking context (people, date, time).",
            },
        },
        {
            "prompt": "Display the complete menu for lunch at 'Sushi Palace'",
            "prompt_for_task_generation": "Display the complete menu for <meal_time> at '<restaurant_name>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_FULL_MENU",
                "event_criteria": {"restaurant_name": {"value": "Sushi Palace", "operator": "equals"}},
                "time": {"value": "12:00 PM", "operator": "contains"},
            },
            "reasoning": "Requests menu for specific meal time.",
        },
        {
            "prompt": "View the full dinner menu for restaurants with vegan options",
            "prompt_for_task_generation": "View the full <meal_time> menu for restaurants with <dietary_requirement> options",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_FULL_MENU",
                "event_criteria": {
                    "dietary_restrictions": {"value": "vegan", "operator": "contains"},
                    "time": {"value": "6:00 PM", "operator": "contains"},
                },
                "reasoning": "Requests menu filtered by dietary requirements.",
            },
        },
    ],
)

###############################################################################
# COLLAPSE_MENU_USE_CASE
###############################################################################

COLLAPSE_MENU_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Indicate an action to **hide or collapse** an expanded menu view.
2. Refer to the menu of a specific restaurant if contextually necessary.
3. Lead to the COLLAPSE_MENU event.
"""

COLLAPSE_MENU_USE_CASE = UseCase(
    name="COLLAPSE_MENU",
    description="User collapses a previously expanded full menu view for a restaurant.",
    event=CollapseMenuEvent,
    event_source_code=CollapseMenuEvent.get_source_code_of_class(),
    additional_prompt_info=COLLAPSE_MENU_INFO,
    constraints_generator=generate_collapse_menu_constraints,
    examples=[
        {
            "prompt": "Hide the menu for 'The Royal Dine'.",
            "prompt_for_task_generation": "Hide the menu for '<restaurant_name>'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "COLLAPSE_MENU",
                "event_criteria": {"restaurant_name": {"value": "The Royal Dine", "operator": "equals"}, "action": {"value": "collapse_menu", "operator": "equals"}},
                "reasoning": "User explicitly requests to collapse/hide the menu.",
            },
        }
    ],
)

###############################################################################
# BOOK_RESTAURANT_USE_CASE
###############################################################################

BOOK_RESTAURANT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Clearly state the intention to **book a table** or make a reservation.
2. Include the restaurant name (or ID).
3. Specify the desired date, time, and number of guests for the booking.
4. Lead to the BOOK_RESTAURANT event, which signifies initiating this step.
"""

BOOK_RESTAURANT_USE_CASE = UseCase(
    name="BOOK_RESTAURANT",
    description="User initiates a booking for a restaurant with specific details (date, time, people).",
    event=BookRestaurantEvent,
    event_source_code=BookRestaurantEvent.get_source_code_of_class(),
    constraints_generator=generate_book_restaurant_constraints,
    additional_prompt_info=BOOK_RESTAURANT_INFO,
    examples=[
        {
            "prompt": "I'd like to book a table at 'The Royal Dine' for 2 people on May 16th at 1:30 PM.",
            "prompt_for_task_generation": "I'd like to book a table at '<restaurant_name>' for <people_count> people on <date_description> at <time_description>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "BOOK_RESTAURANT",
                "event_criteria": {
                    "restaurant_name": {"value": "The Royal Dine", "operator": "equals"},
                    "people": {"value": 2, "operator": "equals"},
                    "selected_date": {"value": date(2025, 5, 16), "operator": "equals"},
                    "time": {"value": "1:30 PM", "operator": "equals"},
                },
                "reasoning": "User provides all necessary details to book a restaurant.",
            },
        },
    ],
)

###############################################################################
# COUNTRY_SELECTED_USE_CASE
###############################################################################

COUNTRY_SELECTED_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Indicate the action of **selecting a country** from a list or dropdown.
2. Specify the country name or code being selected.
3. Be part of a larger form-filling process, typically for user details or reservation completion.
4. Lead to the COUNTRY_SELECTED event.
"""

COUNTRY_SELECTED_USE_CASE = UseCase(
    name="COUNTRY_SELECTED",
    description="User selects a country, often as part of filling out contact or payment details for a reservation.",
    event=CountrySelectedEvent,
    event_source_code=CountrySelectedEvent.get_source_code_of_class(),
    constraints_generator=generate_country_selected_constraints,
    additional_prompt_info=COUNTRY_SELECTED_INFO,
    examples=[
        {
            "prompt": "Select 'India' as the country for my phone number.",
            "prompt_for_task_generation": "Select '<country_name>' as the country for my phone number.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "COUNTRY_SELECTED",
                "event_criteria": {"country_code": {"value": "IN", "operator": "equals"}, "country_name": {"value": "India", "operator": "equals"}},
                "reasoning": "User selects a country from a list.",
            },
        },
        {
            "prompt": "Choose a country other than United States for my reservation details",
            "prompt_for_task_generation": "Choose a country other than <country_name> for my reservation details",
            "test": {
                "type": "CheckEventTest",
                "event_name": "COUNTRY_SELECTED",
                "event_criteria": {"country_name": {"value": "United States", "operator": "not_equals"}},
                "reasoning": "User selects any country except the specified one.",
            },
        },
        {
            "prompt": "Set my country to one in Europe for the billing address",
            "prompt_for_task_generation": "Set my country to one in <region> for the billing address",
            "test": {
                "type": "CheckEventTest",
                "event_name": "COUNTRY_SELECTED",
                "event_criteria": {"region": {"value": "Europe", "operator": "equals"}},
                "reasoning": "User selects country from specific region.",
            },
        },
    ],
)

###############################################################################
# OCCASION_SELECTED_USE_CASE
###############################################################################

OCCASION_SELECTED_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Indicate the action of **selecting a special occasion** for a booking.
2. Specify the type of occasion (e.g., "birthday", "anniversary").
3. Lead to the OCCASION_SELECTED event.
"""

OCCASION_SELECTED_USE_CASE = UseCase(
    name="OCCASION_SELECTED",
    description="User selects a special occasion for their restaurant reservation.",
    event=OccasionSelectedEvent,
    event_source_code=OccasionSelectedEvent.get_source_code_of_class(),
    constraints_generator=generate_occasion_selected_constraints,
    additional_prompt_info=OCCASION_SELECTED_INFO,
    examples=[
        {
            "prompt": "This reservation is for a 'birthday'.",
            "prompt_for_task_generation": "This reservation is for a '<occasion_type>'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "OCCASION_SELECTED",
                "event_criteria": {"occasion": {"value": "birthday", "operator": "equals"}},
                "reasoning": "User specifies an occasion for the booking.",
            },
        },
        {
            "prompt": "Mark this booking as a special occasion (not anniversary)",
            "prompt_for_task_generation": "Mark this booking as a special occasion (not <occasion_type>)",
            "test": {
                "type": "CheckEventTest",
                "event_name": "OCCASION_SELECTED",
                "event_criteria": {"occasion": {"value": "anniversary", "operator": "not_equals"}},
                "reasoning": "User indicates special occasion while excluding specific type.",
            },
        },
        {
            "prompt": "Select 'business dinner' as the occasion type",
            "prompt_for_task_generation": "Select '<occasion_type>' as the occasion type",
            "test": {
                "type": "CheckEventTest",
                "event_name": "OCCASION_SELECTED",
                "event_criteria": {"occasion": {"value": "business dinner", "operator": "equals"}},
                "reasoning": "User selects specific business-related occasion.",
            },
        },
    ],
)

###############################################################################
# RESERVATION_COMPLETE_USE_CASE
###############################################################################

RESERVATION_COMPLETE_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Clearly indicate the **final confirmation or completion** of a restaurant reservation.
2. May involve providing final details like contact information (email, phone) or special requests if these are part of the final step.
3. Lead to the RESERVATION_COMPLETE event.
"""

RESERVATION_COMPLETE_USE_CASE = UseCase(
    name="RESERVATION_COMPLETE",
    description="User finalizes and completes their restaurant reservation, providing all necessary information.",
    event=ReservationCompleteEvent,
    event_source_code=ReservationCompleteEvent.get_source_code_of_class(),
    additional_prompt_info=RESERVATION_COMPLETE_INFO,
    constraints_generator=generate_reservation_complete_constraints,
    examples=[
        {
            "prompt": "Complete my reservation for 'The Royal Dine' on July 18th at 1:30 PM for 2 people. My email is user_name@gmail.com, phone is 123, it's for a birthday, and special request is 'a quiet table'.",
            "prompt_for_task_generation": "Complete my reservation for '<restaurant_name>' on <date> at <time> for <people_count>. My email is <email>, phone is <phone_number>, it's for a <occasion>, and special request is '<special_request>'.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "RESERVATION_COMPLETE",
                "event_criteria": {
                    "restaurant_id": {"value": "royal-dine", "operator": "equals"},
                    "reservation_date_str": {"value": "Jul 18", "operator": "equals"},
                    "reservation_time": {"value": "1:30 PM", "operator": "equals"},
                    "people_count_str": {"value": "2 people", "operator": "equals"},
                    "email": {"value": "user_name@gmail.com", "operator": "equals"},
                    "occasion": {"value": "birthday", "operator": "equals"},
                    "phone_number": {"value": "123", "operator": "equals"},
                    "special_request": {"value": "the", "operator": "equals"},
                },
                "reasoning": "User provides all final details to complete the reservation.",
            },
        },
        {
            "prompt": "Finalize booking with email containing 'company.com' and phone number starting with '+1'",
            "prompt_for_task_generation": "Finalize booking with email containing '<email_fragment>' and phone number starting with '<phone_prefix>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "RESERVATION_COMPLETE",
                "event_criteria": {
                    "email": {"value": "company.com", "operator": "contains"},
                    "phone_number": {"value": "+1", "operator": "starts_with"},
                },
                "reasoning": "User completes reservation with specific email and phone patterns.",
            },
        },
        {
            "prompt": "Confirm reservation with special dietary requirements (vegan and gluten-free)",
            "prompt_for_task_generation": "Confirm reservation with special dietary requirements (<requirement1> and <requirement2>)",
            "test": {
                "type": "CheckEventTest",
                "event_name": "RESERVATION_COMPLETE",
                "event_criteria": {
                    "dietary_restrictions": {"value": ["vegan", "gluten-free"], "operator": "contains_all"},
                },
                "reasoning": "User completes reservation with multiple dietary requirements.",
            },
        },
    ],
)

###############################################################################
# SCROLL_VIEW_USE_CASE
###############################################################################

SCROLL_VIEW_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Explicitly mention **scrolling or navigating** a generic list or page section.
2. Specify the direction of scroll (e.g., "right", "left", "down", "up") if applicable.
3. May mention the number of items now visible if that's a direct consequence of the scroll action being described.
4. Lead to the SCROLL_VIEW event.
"""

SCROLL_VIEW_USE_CASE = UseCase(
    name="SCROLL_VIEW",
    description="User scrolls a generic view, list, or page.",
    event=ScrollViewEvent,
    event_source_code=ScrollViewEvent.get_source_code_of_class(),
    additional_prompt_info=SCROLL_VIEW_INFO,
    constraints_generator=generate_scroll_view_constraints,
    examples=[
        {
            "prompt": "Scroll right to see more available time slots.",
            "prompt_for_task_generation": "Scroll <direction> to see more <content_description>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SCROLL_VIEW",
                "event_criteria": {
                    "direction": {"value": "right", "operator": "equals"},
                    # "visible_count" is optional in event, so may not always be in criteria
                    # "visible_count": {"value": 7, "operator": "equals"} # From your JSON example if applicable
                },
                "reasoning": "User scrolls a view to see more options.",
            },
        },
        {
            "prompt": "Navigate to the next set of 7 restaurants by scrolling right.",
            "prompt_for_task_generation": "Navigate to the next set of <count> <item_type> by scrolling <direction>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SCROLL_VIEW",
                "event_criteria": {"direction": {"value": "right", "operator": "equals"}, "visible_count": {"value": 7, "operator": "equals"}},
                "reasoning": "User scrolls a view, and a specific number of items become visible.",
            },
        },
        {
            "prompt": "Scroll not right repeatedly to load more search results",
            "prompt_for_task_generation": "Scroll <direction> repeatedly to load more search results",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SCROLL_VIEW",
                "event_criteria": {"direction": {"value": "right", "operator": "not_equals"}},
                "reasoning": "User scrolls to load more content.",
            },
        },
        {
            "prompt": "Swipe left to view additional restaurant photos",
            "prompt_for_task_generation": "Swipe <direction> to view additional <content_type>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SCROLL_VIEW",
                "event_criteria": {"direction": {"value": "left", "operator": "equals"}},
                "reasoning": "User swipes to see more content.",
            },
        },
    ],
)


###############################################################################
# UPDATED FINAL LIST: ALL_USE_CASES
###############################################################################

ALL_USE_CASES = [
    DATE_DROPDOWN_OPENED_USE_CASE,
    TIME_DROPDOWN_OPENED_USE_CASE,
    PEOPLE_DROPDOWN_OPENED_USE_CASE,
    SEARCH_RESTAURANT_USE_CASE,
    VIEW_RESTAURANT_USE_CASE,
    VIEW_FULL_MENU_USE_CASE,
    COLLAPSE_MENU_USE_CASE,
    BOOK_RESTAURANT_USE_CASE,
    COUNTRY_SELECTED_USE_CASE,
    OCCASION_SELECTED_USE_CASE,
    RESERVATION_COMPLETE_USE_CASE,
    SCROLL_VIEW_USE_CASE,
]
