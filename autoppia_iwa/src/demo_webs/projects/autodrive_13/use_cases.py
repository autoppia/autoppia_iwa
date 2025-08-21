from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    EnterDestinationEvent,
    EnterLocationEvent,
    NextPickupEvent,
    SeePricesEvent,
    SelectDateEvent,
    SelectTimeEvent,
)
from .generation_functions import (
    generate_enter_destination_constraint,
    generate_enter_location_constraint,
    generate_next_pickup_constraint,
    generate_see_prices_constraint,
    generate_select_date_constraint,
    generate_select_time_constraint,
)

ENTER_LOCATION_USE_CASE = UseCase(
    name="ENTER_LOCATION",
    description="The user enters a location value (e.g., city, country, or region)",
    event=EnterLocationEvent,
    event_source_code=EnterLocationEvent.get_source_code_of_class(),
    constraints_generator=generate_enter_location_constraint,
    examples=[
        {
            "prompt": "Enter location equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'",
            "prompt_for_task_generation": "Enter location equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'",
        },
        {
            "prompt": "Enter location not equals '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA'",
            "prompt_for_task_generation": "Enter location not equals '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA'",
        },
        {
            "prompt": "Enter location contains '1000 Chestnut Street Apartments'",
            "prompt_for_task_generation": "Enter location contains '1000 Chestnut Street Apartments'",
        },
        {
            "prompt": "Enter location not contains '1001 Castro Street'",
            "prompt_for_task_generation": "Enter location not contains '1001 Castro Street'",
        },
    ],
)
ENTER_DESTINATION_USE_CASE = UseCase(
    name="ENTER_DESTINATION",
    description="The user enters a destination value (e.g., city, country, or region)",
    event=EnterDestinationEvent,
    event_source_code=EnterDestinationEvent.get_source_code_of_class(),
    constraints_generator=generate_enter_destination_constraint,
    examples=[
        {
            "prompt": "Enter destination equals '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA'",
            "prompt_for_task_generation": "Enter destination equals '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA'",
        },
        {
            "prompt": "Enter destination not equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'",
            "prompt_for_task_generation": "Enter destination not equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'",
        },
        {
            "prompt": "Enter destination contains '1001 Castro Street'",
            "prompt_for_task_generation": "Enter destination contains '1001 Castro Street'",
        },
        {
            "prompt": "Enter destination not contains '1000 Chestnut Street Apartments'",
            "prompt_for_task_generation": "Enter destination not contains '1000 Chestnut Street Apartments'",
        },
    ],
)
SEE_PRICES_USE_CASE = UseCase(
    name="SEE_PRICES",
    description="The user sees prices for a trip between a location and a destination",
    event=SeePricesEvent,
    event_source_code=SeePricesEvent.get_source_code_of_class(),
    constraints_generator=generate_see_prices_constraint,
    examples=[
        {
            "prompt": "See prices where location equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA' and destination equals '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA'",
            "prompt_for_task_generation": "See prices where location equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA' and destination equals '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA'",
        },
        {
            "prompt": "See prices where location not equals '1000 Chestnut Street Apartments - 1000 Chestnut St, San Francisco, CA 94109, USA' and destination equals '1001 Castro Street - 1001 Castro St, San Francisco, CA 94114, USA'",
            "prompt_for_task_generation": "See prices where location not equals '1000 Chestnut Street Apartments - 1000 Chestnut St, San Francisco, CA 94109, USA' and destination equals '1001 Castro Street - 1001 Castro St, San Francisco, CA 94114, USA'",
        },
        {
            "prompt": "See prices where destination contains 'Van Ness' and destination contains 'Castro'",
            "prompt_for_task_generation": "See prices where location contains 'Van Ness' and destination contains 'Castro'",
        },
        {
            "prompt": "See prices where destination not contains 'Chestnut' and destination not contains 'Hotel'",
            "prompt_for_task_generation": "See prices where location not contains 'Chestnut' and destination not contains 'Hotel'",
        },
    ],
)
SELECT_DATE_USE_CASE = UseCase(
    name="SELECT_DATE",
    description="The user selects a specific date for their trip or booking",
    event=SelectDateEvent,
    event_source_code=SelectDateEvent.get_source_code_of_class(),
    constraints_generator=generate_select_date_constraint,
    examples=[
        {
            "prompt": "Select date equals '2025-08-20'",
            "prompt_for_task_generation": "Select date equals '2025-08-20'",
        },
        {
            "prompt": "Select date not equals '2025-08-21'",
            "prompt_for_task_generation": "Select date not equals '2025-08-21'",
        },
        {
            "prompt": "Select date greater than '2025-08-15'",
            "prompt_for_task_generation": "Select date greater than '2025-08-15'",
        },
        {
            "prompt": "Select date less than '2025-09-01'",
            "prompt_for_task_generation": "Select date less than '2025-09-01'",
        },
        {
            "prompt": "Select date greater equal '2025-08-20'",
            "prompt_for_task_generation": "Select date greater equal '2025-08-20'",
        },
        {
            "prompt": "Select date less equal '2025-08-31'",
            "prompt_for_task_generation": "Select date less equal '2025-08-31'",
        },
    ],
)

SELECT_TIME_USE_CASE = UseCase(
    name="SELECT_TIME",
    description="The user selects a specific time for their trip or booking",
    event=SelectTimeEvent,
    event_source_code=SelectTimeEvent.get_source_code_of_class(),
    constraints_generator=generate_select_time_constraint,
    examples=[
        {
            "prompt": "Select time equals '10:00:00'",
            "prompt_for_task_generation": "Select time equals '10:00:00'",
        },
        {
            "prompt": "Select time not equals '15:30:00'",
            "prompt_for_task_generation": "Select time not equals '15:30:00'",
        },
        {
            "prompt": "Select time greater than '08:00:00'",
            "prompt_for_task_generation": "Select time greater than '08:00:00'",
        },
        {
            "prompt": "Select time less than '20:00:00'",
            "prompt_for_task_generation": "Select time less than '20:00:00'",
        },
        {
            "prompt": "Select time greater equal '12:00:00'",
            "prompt_for_task_generation": "Select time greater equal '12:00:00'",
        },
        {
            "prompt": "Select time less equal '18:00:00'",
            "prompt_for_task_generation": "Select time less equal '18:00:00'",
        },
    ],
)
NEXT_PICKUP_USE_CASE = UseCase(
    name="NEXT_PICKUP",
    description="The user clicks the 'Next' button after successfully selecting a pickup date and time.",
    event=NextPickupEvent,
    event_source_code=NextPickupEvent.get_source_code_of_class(),
    constraints_generator=generate_next_pickup_constraint,
    examples=[
        {
            "prompt": "Next pickup date equals '2025-08-20' and time equals '10:00:00'",
            "prompt_for_task_generation": "Next pickup date equals '2025-08-20' and time equals '10:00:00'",
        },
        {
            "prompt": "Next pickup date not equals '2025-08-25'",
            "prompt_for_task_generation": "Next pickup date not equals '2025-08-25'",
        },
        {
            "prompt": "Next pickup date greater than '2025-08-15'",
            "prompt_for_task_generation": "Next pickup date greater than '2025-08-15'",
        },
        {
            "prompt": "Next pickup time less than '18:00:00'",
            "prompt_for_task_generation": "Next pickup time less than '18:00:00'",
        },
        {
            "prompt": "Next pickup time greater equal '09:00:00'",
            "prompt_for_task_generation": "Next pickup time greater equal '09:00:00'",
        },
        {
            "prompt": "Next pickup date less equal '2025-08-30'",
            "prompt_for_task_generation": "Next pickup date less equal '2025-08-30'",
        },
    ],
)


ALL_USE_CASES = [
    # ENTER_LOCATION_USE_CASE,
    # ENTER_DESTINATION_USE_CASE,
    # SEE_PRICES_USE_CASE,
    # SELECT_DATE_USE_CASE,
    # SELECT_TIME_USE_CASE,
    NEXT_PICKUP_USE_CASE,
]
