from autoppia_iwa.src.demo_webs.classes import UseCase

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

DATE_DROPDOWN_OPENED_USE_CASE = UseCase(
    name="DATE_DROPDOWN_OPENED",
    description="Interact with the date picker.",
    event=DateDropdownOpenedEvent,
    event_source_code=DateDropdownOpenedEvent.get_source_code_of_class(),
    constraints_generator=generate_date_dropdown_opened_constraints,
    additional_prompt_info="""CRITICAL REQUIREMENT: Prompts must mention the date selector explicitly and indicate a desired date.""",
    examples=[
        {"prompt": "Open the date selector for my booking.", "prompt_for_task_generation": "Open the date selector for my booking."},
        {"prompt": "Click the calendar icon to select a date after June 15th.", "prompt_for_task_generation": "Click the calendar icon to select a date after <date>."},
    ],
)

TIME_DROPDOWN_OPENED_USE_CASE = UseCase(
    name="TIME_DROPDOWN_OPENED",
    description="Interact with the time picker.",
    event=TimeDropdownOpenedEvent,
    event_source_code=TimeDropdownOpenedEvent.get_source_code_of_class(),
    constraints_generator=generate_time_dropdown_opened_constraints,
    examples=[{"prompt": "Click on the time field to choose a reservation time.", "prompt_for_task_generation": "Click on the time field to choose a reservation time."}],
)

PEOPLE_DROPDOWN_OPENED_USE_CASE = UseCase(
    name="PEOPLE_DROPDOWN_OPENED",
    description="Open the guest selector.",
    event=PeopleDropdownOpenedEvent,
    event_source_code=PeopleDropdownOpenedEvent.get_source_code_of_class(),
    constraints_generator=generate_people_dropdown_opened_constraints,
    examples=[
        {"prompt": "Open the guest number selection for my table.", "prompt_for_task_generation": "Open the guest number selection for my table."},
        {"prompt": "Select the party size dropdown for a group larger than 6 people.", "prompt_for_task_generation": "Select the party size dropdown for a group larger than <people_count> people."},
    ],
)

SEARCH_RESTAURANT_USE_CASE = UseCase(
    name="SEARCH_RESTAURANT",
    description="Perform a restaurant search by name or cuisine.",
    event=SearchRestaurantEvent,
    event_source_code=SearchRestaurantEvent.get_source_code_of_class(),
    constraints_generator=generate_search_restaurant_constraints,
    additional_prompt_info="""Prompts must clearly mention searching for restaurants, not booking or filtering.""",
    examples=[
        {"prompt": "Search for 'italian restaurants in downtown'", "prompt_for_task_generation": "Search for '<query>'"},
        {"prompt": "Find restaurants named 'The Royal Dine'", "prompt_for_task_generation": "Find restaurants named '<query>'"},
    ],
)

VIEW_RESTAURANT_USE_CASE = UseCase(
    name="VIEW_RESTAURANT",
    description="Open a restaurant detail page.",
    event=ViewRestaurantEvent,
    event_source_code=ViewRestaurantEvent.get_source_code_of_class(),
    constraints_generator=generate_view_restaurant_constraints,
    examples=[
        {"prompt": "Show me details for 'The Royal Dine'", "prompt_for_task_generation": "Show me details for '<restaurant_name>'"},
        {"prompt": "View restaurant page for ID 'royal-dine'", "prompt_for_task_generation": "View restaurant page for ID '<restaurant_id>'"},
    ],
)

VIEW_FULL_MENU_USE_CASE = UseCase(
    name="VIEW_FULL_MENU",
    description="Expand the full menu for an active restaurant card.",
    event=ViewFullMenuEvent,
    event_source_code=ViewFullMenuEvent.get_source_code_of_class(),
    constraints_generator=generate_view_full_menu_constraints,
    examples=[
        {"prompt": "Show the full menu for the restaurant I'm viewing.", "prompt_for_task_generation": "Show the full menu for '<restaurant_name>'."},
        {"prompt": "Expand the menu for our 8:00 PM reservation.", "prompt_for_task_generation": "Expand the menu for our <time> reservation."},
    ],
)

COLLAPSE_MENU_USE_CASE = UseCase(
    name="COLLAPSE_MENU",
    description="Collapse the expanded menu view.",
    event=CollapseMenuEvent,
    event_source_code=CollapseMenuEvent.get_source_code_of_class(),
    constraints_generator=generate_collapse_menu_constraints,
    examples=[{"prompt": "Hide the full menu after reviewing it.", "prompt_for_task_generation": "Hide the full menu after reviewing it."}],
)

BOOK_RESTAURANT_USE_CASE = UseCase(
    name="BOOK_RESTAURANT",
    description="Trigger the book CTA before confirmation.",
    event=BookRestaurantEvent,
    event_source_code=BookRestaurantEvent.get_source_code_of_class(),
    constraints_generator=generate_book_restaurant_constraints,
    examples=[
        {"prompt": "Click the book button for this restaurant.", "prompt_for_task_generation": "Click the book button for '<restaurant_name>'."},
        {"prompt": "Book a table for 4 at 8:30 PM.", "prompt_for_task_generation": "Book a table for <people> people at <time>."},
    ],
)

COUNTRY_SELECTED_USE_CASE = UseCase(
    name="COUNTRY_SELECTED",
    description="Select a country in the reservation form.",
    event=CountrySelectedEvent,
    event_source_code=CountrySelectedEvent.get_source_code_of_class(),
    constraints_generator=generate_country_selected_constraints,
    examples=[
        {"prompt": "Set the country to India in the phone field.", "prompt_for_task_generation": "Set the country to <country_name> in the phone field."},
        {"prompt": "Choose country code +1 for the booking.", "prompt_for_task_generation": "Choose country code <country_code> for the booking."},
    ],
)

OCCASION_SELECTED_USE_CASE = UseCase(
    name="OCCASION_SELECTED",
    description="Specify an occasion such as birthday or anniversary.",
    event=OccasionSelectedEvent,
    event_source_code=OccasionSelectedEvent.get_source_code_of_class(),
    constraints_generator=generate_occasion_selected_constraints,
    examples=[{"prompt": "Select 'Birthday' as the occasion.", "prompt_for_task_generation": "Select '<occasion>' as the occasion."}],
)

RESERVATION_COMPLETE_USE_CASE = UseCase(
    name="RESERVATION_COMPLETE",
    description="Submit the reservation form.",
    event=ReservationCompleteEvent,
    event_source_code=ReservationCompleteEvent.get_source_code_of_class(),
    constraints_generator=generate_reservation_complete_constraints,
    examples=[{"prompt": "Complete the booking for 2 people at 7 PM.", "prompt_for_task_generation": "Complete the booking for <people_count> people at <reservation_time>."}],
)

SCROLL_VIEW_USE_CASE = UseCase(
    name="SCROLL_VIEW",
    description="Scroll through a featured carousel.",
    event=ScrollViewEvent,
    event_source_code=ScrollViewEvent.get_source_code_of_class(),
    constraints_generator=generate_scroll_view_constraints,
    examples=[{"prompt": "Scroll right through the featured restaurants section.", "prompt_for_task_generation": "Scroll <direction> through the '<section_title>' section."}],
)

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
