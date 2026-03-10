from ...classes import UseCase
from .events import (
    AboutFeatureClickEvent,
    AboutPageViewEvent,
    BookRestaurantEvent,
    CollapseMenuEvent,
    ContactCardClickEvent,
    ContactEvent,
    ContactPageViewEvent,
    CountrySelectedEvent,
    DateDropdownOpenedEvent,
    HelpCategorySelectedEvent,
    HelpFaqToggledEvent,
    HelpPageViewEvent,
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
    generate_about_feature_click_constraints,
    generate_book_restaurant_constraints,
    generate_collapse_menu_constraints,
    generate_contact_card_click_constraints,
    generate_contact_constraints,
    generate_country_selected_constraints,
    generate_date_dropdown_opened_constraints,
    generate_help_category_selected_constraints,
    generate_help_faq_toggled_constraints,
    generate_occasion_selected_constraints,
    generate_people_dropdown_opened_constraints,
    generate_reservation_complete_constraints,
    generate_scroll_view_constraints,
    generate_search_restaurant_constraints,
    generate_time_dropdown_opened_constraints,
    generate_view_full_menu_constraints,
    generate_view_restaurant_constraints,
)

###############################################################################
# DATE_DROPDOWN_OPENED_USE_CASE
###############################################################################

DATE_DROPDOWN_OPENED_INFO = """
CRITICAL REQUIREMENTS: EVERY prompt you generate MUST:
1. Explicitly instruct the user to open or interact with the date selector dropdown (e.g., "Open the date selector", "Click on the date field").
2. Clearly describe an action that triggers the date selection interface.
3. Ensure the action leads directly to the DATE_DROPDOWN_OPENED event.
4. Do not include date comparison conditions or date selection instructions unless explicitly required by constraints.
5. Do not include unrelated actions such as confirming, submitting, or selecting other fields.

Examples:
- CORRECT: "Open the date selector and select the date equals '2026-02-23T19:00:00+00:00'."
- INCORRECT: "Select the date '2026-02-23T19:00:00+00:00'." (does not explicitly open the date selector)
- INCORRECT: "Confirm the booking date." (wrong action)
- INCORRECT: "Open the date selector." (missing required date selection when constraints specify a date)
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
            "prompt": "Open the date selector and select the date '2026-02-23T19:00:00+00:00'.",
            "prompt_for_task_generation": "Open the date selector and select the date '<date>'.",
        },
        {
            "prompt": "Open the date selector and select a date not equal to '2026-02-28T19:00:00+00:00'.",
            "prompt_for_task_generation": "Open the date selector and select a date not equal to '<date>'.",
        },
        {
            "prompt": "Open the date selector and select a date greater than '2026-01-23T12:00:00+00:00'.",
            "prompt_for_task_generation": "Open the date selector and select a date greater than '<date>'.",
        },
        {
            "prompt": "Open the date selector and select a date less than '2026-02-21T18:00:00+00:00'.",
            "prompt_for_task_generation": "Open the date selector and select a date less than '<date>'.",
        },
        {
            "prompt": "Open the date selector and select a date greater equals '2026-02-20T21:00:00+00:00'.",
            "prompt_for_task_generation": "Open the date selector and select a date greater equal '<date>'.",
        },
        {
            "prompt": "Open the date selector and select a date less equals '2026-02-24T13:00:00+00:00'.",
            "prompt_for_task_generation": "Open the date selector and select a date less equal '<date>'.",
        },
    ],
)

###############################################################################
# TIME_DROPDOWN_OPENED_USE_CASE
###############################################################################

TIME_DROPDOWN_OPENED_INFO = """
CRITICAL REQUIREMENTS: EVERY prompt you generate MUST:
1. Explicitly indicate interaction with a time selection UI element (e.g., "Open the time selector", "Click on the time field").
2. The event captures the time displayed or selected at the moment the interaction occurs.
3. The prompt must clearly lead to the TIME_DROPDOWN_OPENED event.
4. Do not include unrelated actions such as confirming, submitting, or interacting with other fields.

Examples:
- CORRECT: "Open the time dropdown and select the time equals '2:30 PM'."
- INCORRECT: "Select the time '2:30 PM'." (does not explicitly open the time dropdown)
- INCORRECT: "Confirm the booking time." (wrong action)
- INCORRECT: "Open the time dropdown." (missing required time selection when constraints specify a time)
"""


TIME_DROPDOWN_OPENED_USE_CASE = UseCase(
    name="TIME_DROPDOWN_OPENED",
    description="User interacts with (opens or focuses on) a time selection dropdown/input.",
    event=TimeDropdownOpenedEvent,
    event_source_code=TimeDropdownOpenedEvent.get_source_code_of_class(),
    additional_prompt_info=TIME_DROPDOWN_OPENED_INFO,
    constraints_generator=generate_time_dropdown_opened_constraints,
    examples=[
        {
            "prompt": "Open the time dropdown and select the time equals '2:30 PM'.",
            "prompt_for_task_generation": "Open the time dropdown and select the time equals '2:30 PM'.",
        },
        {
            "prompt": "Open the time dropdown and select a time not equals '2:30 PM'.",
            "prompt_for_task_generation": "Open the time dropdown and select a time not equals '2:30 PM'.",
        },
        {
            "prompt": "Open the time dropdown and select a time greater than '1:00 PM'.",
            "prompt_for_task_generation": "Open the time dropdown and select a time greater than '1:00 PM'.",
        },
        {
            "prompt": "Open the time dropdown and select a time less than '5:00 PM'.",
            "prompt_for_task_generation": "Open the time dropdown and select a time less than '5:00 PM'.",
        },
        {
            "prompt": "Open the time dropdown and select a time greater equal '3:00 PM'.",
            "prompt_for_task_generation": "Open the time dropdown and select a time greater equal '3:00 PM'.",
        },
        {
            "prompt": "Open the time dropdown and select a time less equals '6:00 PM'.",
            "prompt_for_task_generation": "Open the time dropdown and select a time less equal '6:00 PM'.",
        },
    ],
)

###############################################################################
# PEOPLE_DROPDOWN_OPENED_USE_CASE
###############################################################################

PEOPLE_DROPDOWN_OPENED_INFO = """
CRITICAL REQUIREMENTS: EVERY prompt you generate MUST:
1. Clearly describe interaction with the guest selection UI element (e.g., "Open the guest selector dropdown", "Click on the guest field").
2. Ensure the event captures the number of guests selected at the moment of interaction.
3. The prompt should explicitly trigger the GUEST_SELECTOR_DROPDOWN_OPENED event.
4. Avoid including unrelated actions such as confirming, submitting, or interacting with other fields.

Examples:
- CORRECT: "Open the guest selector dropdown and select people equals 4."
- INCORRECT: "Select 4 guests." (does not explicitly open the guest selector dropdown)
- INCORRECT: "Confirm the number of guests." (wrong action)
- INCORRECT: "Open the guest selector dropdown." (missing required people selection when constraints specify a value)
"""

PEOPLE_DROPDOWN_OPENED_USE_CASE = UseCase(
    name="PEOPLE_DROPDOWN_OPENED",
    description="User interacts with (opens or focuses on) a dropdown to select the number of people/guests.",
    event=PeopleDropdownOpenedEvent,
    event_source_code=PeopleDropdownOpenedEvent.get_source_code_of_class(),
    additional_prompt_info=PEOPLE_DROPDOWN_OPENED_INFO,
    constraints_generator=generate_people_dropdown_opened_constraints,
    examples=[
        {
            "prompt": "Open the guest selector dropdown and select people equals 4.",
            "prompt_for_task_generation": "Open the guest selector dropdown and select people equals <count>.",
        },
        {
            "prompt": "Open the guest selector dropdown and select people not equal to 5.",
            "prompt_for_task_generation": "Open the guest selector dropdown and select people not equal to <count>.",
        },
        {
            "prompt": "Open the guest selector dropdown and select people greater than 6.",
            "prompt_for_task_generation": "Open the guest selector dropdown and select people greater than <count>.",
        },
        {
            "prompt": "Open the guest selector dropdown and select people less than 3.",
            "prompt_for_task_generation": "Open the guest selector dropdown and select people less than <count>.",
        },
        {
            "prompt": "Open the guest selector dropdown and select people greater than or equal to 2.",
            "prompt_for_task_generation": "Open the guest selector dropdown and select people greater than or equal to <count>.",
        },
        {
            "prompt": "Open the guest selector dropdown and select people less than or equal to 8.",
            "prompt_for_task_generation": "Open the guest selector dropdown and select people less than or equal to <count>.",
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
        },
        {
            "prompt": "Find restaurants named 'The Royal Dine'",
            "prompt_for_task_generation": "Find restaurants named '<query>'",
        },
        {
            "prompt": "Look up places to eat that serve vegan food",
            "prompt_for_task_generation": "Look up places to eat that serve <query> food",
        },
        {
            "prompt": "Search for restaurants with outdoor seating in midtown",
            "prompt_for_task_generation": "Search for restaurants with <query> in midtown",
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
    examples=[
        {
            "prompt": "Show me details for 'The Royal Dine'",
            "prompt_for_task_generation": "Show me details for '<name>'",
        },
        {
            "prompt": "View restaurant page for ID 'royal-dine'",
            "prompt_for_task_generation": "View restaurant page for ID '<restaurant_id>'",
        },
        {
            "prompt": "Show me the page for a restaurant with rating above 4.5",
            "prompt_for_task_generation": "Show me the page for a restaurant with rating above <rating>",
        },
        {
            "prompt": "View details for restaurants that serve sushi",
            "prompt_for_task_generation": "View details for restaurants that serve <cuisine>",
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
            "prompt_for_task_generation": "Show the full menu for '<name>' for <people> people for <meal_time> on <date_description>.",
        },
        {
            "prompt": "Display the complete menu for lunch at 'Sushi Palace'",
            "prompt_for_task_generation": "Display the complete menu for <meal_time> at '<name>'",
            "reasoning": "Requests menu for specific meal time.",
        },
        {
            "prompt": "View the full dinner menu for restaurants with vegan options",
            "prompt_for_task_generation": "View the full <meal_time> menu for restaurants with <dietary_requirement> options",
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
            "prompt_for_task_generation": "Hide the menu for '<name>'.",
        }
    ],
)

###############################################################################
# BOOK_RESTAURANT_USE_CASE
###############################################################################

BOOK_RESTAURANT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Clearly state the intention to **book a table** or make a reservation.
2. ONLY INCLUDES RESTAURANT NAMES IN THE LIST IF THE NAME ARE IN THE CONSTRAINTS. YOU CANNOT SAY A NAME IF NOT ARE IN THE CONSTRAINTS
3. Specify the desired date, time, and number of guests for the booking. BE SC
4. DO NOT CONFUSE DESC with NAME. If the constraints mention DESC (description) just include the constriants do not use name if it is not specified in the prompt
5. IF NAME IS IN CONSTRAINTS SPECIFY CLEARLY YOU CANNOT SAY Book a table in a restaurant that does NOT contain 'qpehvk'. ONLY IF NAME IS IN CONSTRAINTS, an dthen you have to specify NAME
"""

BOOK_RESTAURANT_USE_CASE = UseCase(
    name="BOOK_RESTAURANT",
    description="User initiates a restaurant table booking with specified details like restaurant name, number of people, date, and time.",
    event=BookRestaurantEvent,
    event_source_code=BookRestaurantEvent.get_source_code_of_class(),
    constraints_generator=generate_book_restaurant_constraints,
    additional_prompt_info=BOOK_RESTAURANT_INFO,
    examples=[
        {
            "prompt": "I'd like to book a table at the restaurant which name 'The Royal Dine' for 2 people on 2025-05-16 at 1:30 PM.",
            "prompt_for_task_generation": "I'd like to book a table at the restaurant which name'<name>' for <people> people on <date> at <time>.",
        },
        {
            "prompt": "Book a table for 3 people on 2024-07-18 for dinner at the restaurant which name 'Sushi Palace' at time '1:30 PM'.",
            "prompt_for_task_generation": "Book a table for <people> people on <date> for <time> at the restaurant which name '<name>'.",
        },
        {
            "prompt": "Book a table for 7 or more people on '2025-08-06' at a time that is NOT '12:30 PM' with a rating of 5 or less.",
            "prompt_for_task_generation": "Book a table for <people> or more people on <date> at a time that is NOT <time> with a rating of <rating> or less.",
        },
    ],
)

###############################################################################
# COUNTRY_SELECTED_USE_CASE
###############################################################################

COUNTRY_SELECTED_INFO = """
CRITICAL REQUIREMENTS:

1. Every prompt MUST indicate the action of **selecting a country** from a list or dropdown.
2. The prompt MUST clearly mention the **country name or country code** being selected.
3. The prompt MUST be situated in the context of a **larger form-filling** or reservation-related flow (e.g., selecting country for contact or billing details).
4. The corresponding event MUST lead to the `COUNTRY_SELECTED` event.
5. If the prompt mentions a restaurant, it should be included **only in the prompt**, **not in the event criteria**.
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
            "prompt": "Select a country where country equals 'India'.",
            "prompt_for_task_generation": "Select a country where country equals '<country>'.",
        },
        {
            "prompt": "Select a country where country not equals 'United States'.",
            "prompt_for_task_generation": "Select a country where country not equals '<country>'.",
        },
        {
            "prompt": "Select a country where code equals 'IN'.",
            "prompt_for_task_generation": "Select a country where code equals '<code>'.",
        },
        {
            "prompt": "Select a country where code not equals 'US' and name equals 'The Royal Dine'.",
            "prompt_for_task_generation": "Select a country where code not equals '<code>' and name equals '<name>'.",
        },
        {
            "prompt": "Select a country where country equals 'Australia' and people equals 2 and date equals '2025-05-16' and time equals '1:30 PM'.",
            "prompt_for_task_generation": "Select a country where country equals '<country>' and people equals <people> and date equals '<date>' and time equals '<time>'.",
        },
        {
            "prompt": "Select a country where country equals 'Canada' and name contains 'Palace' and rating greater than or equal to 4.",
            "prompt_for_task_generation": "Select a country where country equals '<country>' and name contains '<name>' and rating greater than or equal to <rating>.",
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
            "prompt_for_task_generation": "This reservation is for a '<occasion>'.",
        },
        {
            "prompt": "Mark this booking as a special occasion (not anniversary)",
            "prompt_for_task_generation": "Mark this booking as a special occasion (not <occasion>)",
        },
        {
            "prompt": "Select 'business dinner' as the occasion type",
            "prompt_for_task_generation": "Select '<occasion>' as the occasion type",
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
4. Only provide a restauant name if its mentioned in the constraints
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
            "prompt": "Complete my reservation for 'The Royal Dine' on July 18th at 1:30 PM for 2 people. My phone is 123, it's for a birthday, and special request is 'a quiet table'.",
            "prompt_for_task_generation": "Complete my reservation for '<name>' on <date> at <time> for <people>. My email is <email>, phone is <phone>, it's for a <occasion>, and special request is '<request>'.",
        },
        {
            "prompt": "Please finalize my reservation at 'Ocean Breeze' for July 20th, 8:00 PM, 4 people. You can reach me at my number is 9876543210. It's for an anniversary. We'd like a table with a sea view.",
            "prompt_for_task_generation": "Please finalize my reservation at '<name>' for <date>, <time>, <people>. You can reach me at my number is <phone>. It's for an <occasion>. We'd like a table with a <request>.",
        },
        {
            "prompt": "Finish booking at 'Mountain Top Grill' for 6 people at 6:15 PM on August 5. My email is sam.kim@domain.org and phone is 111-222-3333. Please note it's for a corporate event. Requesting projector setup.",
            "prompt_for_task_generation": "Finish booking at '<name>' for <people> at <time> on <date>. My phone is <phone>. Please note it's for a <occasion>. Requesting <request>.",
        },
        {
            "prompt": "Confirm my dinner booking at 'Bella Roma' for September 9th at 9 PM for 3. Call me at +44-1234-567890. We're celebrating a graduation. Please arrange for a dessert surprise.",
            "prompt_for_task_generation": "Confirm my dinner booking at '<name>' for <date> at <time> for <people>. Call me at <phone>. We're celebrating a <occasion>. Please arrange <request>.",
        },
        {
            "prompt": "Book my table at 'City Lights Bistro' on October 2nd, 5 PM, party of 5. Phone: 555-0099. It's a reunion. No loud music please.",
            "prompt_for_task_generation": "Book my table at '<name>' on <date>, <time>, party of <people>. phone: <phone>. It's a <occasion>. <request>.",
        },
    ],
)

###############################################################################
# SCROLL_VIEW_USE_CASE
###############################################################################

SCROLL_VIEW_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Explicitly describe scrolling or navigating (use phrases like "Scroll", "Browse more", etc.).
2. Include the carousel section title if it is specified in the constraints.
3. Specify the scroll direction (left/right) if it is included in the constraints.
4. Avoid mentioning product selection actions or any interactions other than scrolling.
5. Do not include multiple conditions for the same field (e.g., specifying the direction twice is not allowed).


For example:
- CORRECT: "Scroll in the direction 'right' where section equals 'Featured Products'"
- INCORRECT: "View details for product in section" (wrong action)
- INCORRECT: "Show me section items" (no scroll action)
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
            "prompt": "Scroll in the direction 'right' where section equals 'Featured Products'.",
            "prompt_for_task_generation": "Scroll in the <direction> where section equals <Featured Products>.",
        },
        {
            "prompt": "Scroll in the direction 'left' where section not equal to 'Featured Products'.",
            "prompt_for_task_generation": "Scroll in the <direction> where section not equal to <Featured Products>.",
        },
        {
            "prompt": "Scroll in the direction 'right' where section contains 'Top Sellers'.",
            "prompt_for_task_generation": "Scroll in the <direction> where section contains <Top Sellers>.",
        },
        {
            "prompt": "Scroll in the direction 'left' where section does not contain 'Electronics'.",
            "prompt_for_task_generation": "Scroll in the <direction> where section does not contain <Electronics>.",
        },
    ],
)

CONTACT_INFO_USE_CASE = UseCase(
    name="CONTACT_FORM_SUBMIT",
    description="User contacts to user support.",
    event=ContactEvent,
    event_source_code=ContactEvent.get_source_code_of_class(),
    constraints_generator=generate_contact_constraints,
    examples=[
        {
            "prompt": "Contact where name equals 'James'.",
            "prompt_for_task_generation": "Contact where name equals 'James'.",
        },
        {
            "prompt": "Contact where name not equals 'William' and message equals 'Can you provide more information about your pricing plans?'.",
            "prompt_for_task_generation": "Contact where name not equals 'William' and message equals 'Can you provide more information about your pricing plans?'.",
        },
        {
            "prompt": "Contact where name contains 'liam' and message contains 'report a technical bug' and subject equals 'Inquiry About Your Services' and email equals 'emma.johnson@example.com'",
            "prompt_for_task_generation": "Contact where name contains 'liam' and message contains 'report a technical bug' and subject equals 'Inquiry About Your Services' and email equals 'emma.johnson@example.com'",
        },
    ],
)
ABOUT_PAGE_USE_CASE = UseCase(
    name="ABOUT_PAGE_VIEW",
    description="User navigates to or interacts with the About page to view company or application information.",
    event=AboutPageViewEvent,
    event_source_code=AboutPageViewEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {
            "prompt": "Navigate to the About page to read about the company's mission and values.",
            "prompt_for_task_generation": "Navigate to the About page to read about the company's mission and values.",
        },
        {
            "prompt": "Navigate to the About page to view team member profiles and company history.",
            "prompt_for_task_generation": "Navigate to the About page to view team member profiles and company history.",
        },
        {
            "prompt": "Open the About page and explore the sections detailing company achievements and milestones.",
            "prompt_for_tas_generation": "Open the About page and explore the sections detailing company achievements and milestones.",
        },
        {
            "prompt": "Navigate the About page to find information about the company's vision and services.",
            "prompt_for_task_generation": "Navigate the About page to find information about the company's vision and services.",
        },
    ],
)
HELP_PAGE_USE_CASE = UseCase(
    name="HELP_PAGE_VIEW",
    description="User navigates to or interacts with the Help page to find guidance, FAQs, or troubleshooting information.",
    event=HelpPageViewEvent,
    event_source_code=HelpPageViewEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {
            "prompt": "Navigate to the Help page to view frequently asked questions and support guides.",
            "prompt_for_task_generation": "Navigate to the Help page to view frequently asked questions and support guides.",
        },
        {
            "prompt": "Navigate to the Help page to find tutorials and troubleshooting tips.",
            "prompt_for_task_generation": "Navigate to the Help page to find tutorials and troubleshooting tips.",
        },
        {
            "prompt": "Open the Help page and explore sections for technical support and user guidance.",
            "prompt_for_task_generation": "Open the Help page and explore sections for technical support and user guidance.",
        },
        {
            "prompt": "Navigate the Help page to locate detailed instructions and help resources.",
            "prompt_for_task_generation": "Navigate the Help page to locate detailed instructions and help resources.",
        },
    ],
)

ABOUT_FEATURE_CLICK_USE_CASE = UseCase(
    name="ABOUT_FEATURE_CLICK",
    description="Triggered when a user clicks a highlighted feature on the About page.",
    event=AboutFeatureClickEvent,
    event_source_code=AboutFeatureClickEvent.get_source_code_of_class(),
    constraints_generator=generate_about_feature_click_constraints,
    examples=[
        {"prompt": "Click the live availability feature on the About page.", "prompt_for_task_generation": "Click the live availability feature on the About page."},
    ],
)

CONTACT_PAGE_VIEW_USE_CASE = UseCase(
    name="CONTACT_PAGE_VIEW",
    description="Triggered when the Contact page is viewed.",
    event=ContactPageViewEvent,
    event_source_code=ContactPageViewEvent.get_source_code_of_class(),
    constraints_generator=None,
    examples=[
        {"prompt": "Open the contact page.", "prompt_for_task_generation": "Open the contact page."},
        {"prompt": "Go to the content page.", "prompt_for_task_generation": "Go to the content page."},
    ],
)

CONTACT_CARD_CLICK_USE_CASE = UseCase(
    name="CONTACT_CARD_CLICK",
    description="Triggered when a specific contact card (email/phone/chat) is clicked.",
    event=ContactCardClickEvent,
    event_source_code=ContactCardClickEvent.get_source_code_of_class(),
    constraints_generator=generate_contact_card_click_constraints,
    examples=[{"prompt": "Click the phone contact card on the contact page.", "prompt_for_task_generation": "Click the phone contact card."}],
)

HELP_CATEGORY_SELECTED_USE_CASE = UseCase(
    name="HELP_CATEGORY_SELECTED",
    description="Triggered when a help/support category is selected.",
    event=HelpCategorySelectedEvent,
    event_source_code=HelpCategorySelectedEvent.get_source_code_of_class(),
    constraints_generator=generate_help_category_selected_constraints,
    examples=[{"prompt": "Select the Payments category in Help.", "prompt_for_task_generation": "Select the Payments category in Help."}],
)

HELP_FAQ_TOGGLED_USE_CASE = UseCase(
    name="HELP_FAQ_TOGGLED",
    description="Triggered when a FAQ item is expanded or collapsed.",
    event=HelpFaqToggledEvent,
    event_source_code=HelpFaqToggledEvent.get_source_code_of_class(),
    constraints_generator=generate_help_faq_toggled_constraints,
    examples=[{"prompt": "Expand the refund FAQ.", "prompt_for_task_generation": "Expand the refund FAQ."}],
)

###############################################################################
# UPDATED FINAL LIST: ALL_USE_CASES
###############################################################################

ALL_USE_CASES = [
    VIEW_RESTAURANT_USE_CASE,
    VIEW_FULL_MENU_USE_CASE,
    COLLAPSE_MENU_USE_CASE,
    DATE_DROPDOWN_OPENED_USE_CASE,
    TIME_DROPDOWN_OPENED_USE_CASE,
    PEOPLE_DROPDOWN_OPENED_USE_CASE,
    SEARCH_RESTAURANT_USE_CASE,
    SCROLL_VIEW_USE_CASE,
    BOOK_RESTAURANT_USE_CASE,
    COUNTRY_SELECTED_USE_CASE,
    OCCASION_SELECTED_USE_CASE,
    RESERVATION_COMPLETE_USE_CASE,
    CONTACT_INFO_USE_CASE,
    ABOUT_PAGE_USE_CASE,
    HELP_PAGE_USE_CASE,
    ABOUT_FEATURE_CLICK_USE_CASE,
    CONTACT_PAGE_VIEW_USE_CASE,
    CONTACT_CARD_CLICK_USE_CASE,
    HELP_CATEGORY_SELECTED_USE_CASE,
    HELP_FAQ_TOGGLED_USE_CASE,
]
