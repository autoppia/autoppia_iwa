from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    CancelReservationEvent,
    EnterDestinationEvent,
    EnterLocationEvent,
    NextPickupEvent,
    ReserveRideEvent,
    SearchRideEvent,
    SeePricesEvent,
    SelectCarEvent,
    SelectDateEvent,
    SelectTimeEvent,
    TripDetailsEvent,
)
from .generation_functions import (
    generate_cancel_reservation_constraints,
    generate_enter_destination_constraints,
    generate_enter_location_constraints,
    generate_next_pickup_constraints,
    generate_reserve_ride_constraints,
    generate_search_ride_constraints,
    generate_see_prices_constraints,
    generate_select_car_constraints,
    generate_select_date_constraints,
    generate_select_time_constraints,
    generate_trip_details_constraints,
)

ENTER_LOCATION_USE_CASE = UseCase(
    name="ENTER_LOCATION",
    description="The user enters a location value (e.g., city, country, or region)",
    event=EnterLocationEvent,
    event_source_code=EnterLocationEvent.get_source_code_of_class(),
    constraints_generator=generate_enter_location_constraints,
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
    constraints_generator=generate_enter_destination_constraints,
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
    constraints_generator=generate_see_prices_constraints,
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
    constraints_generator=generate_select_date_constraints,
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
    constraints_generator=generate_select_time_constraints,
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
    constraints_generator=generate_next_pickup_constraints,
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
SEARCH_RIDE_USE_CASE = UseCase(
    name="SEARCH",
    description="The user clicks on the 'Search' button after selecting pickup, dropoff, and optionally scheduling a ride.",
    event=SearchRideEvent,
    event_source_code=SearchRideEvent.get_source_code_of_class(),
    constraints_generator=generate_search_ride_constraints,
    examples=[
        {
            "prompt": "Search ride with pickup '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA' and dropoff '1030 Post Street Apartments - 1030 Post St #112, San Francisco, CA 94109, USA'",
            "prompt_for_task_generation": "Search ride with pickup '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA' and dropoff '1030 Post Street Apartments - 1030 Post St #112, San Francisco, CA 94109, USA'",
        },
        {
            "prompt": "Search ride with pickup '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA' and dropoff '1000 Chestnut Street Apartments - 1000 Chestnut St, San Francisco, CA 94109, USA'",
            "prompt_for_task_generation": "Search ride with pickup '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA' and dropoff '1000 Chestnut Street Apartments - 1000 Chestnut St, San Francisco, CA 94109, USA'",
        },
        {
            "prompt": "Search ride where scheduled equals '2025-07-18 13:00:00'",
            "prompt_for_task_generation": "Search ride where scheduled equals '2025-07-18 13:00:00'",
        },
        {
            "prompt": "Search ride where scheduled greater than '2025-07-15 09:00:00'",
            "prompt_for_task_generation": "Search ride where scheduled greater than '2025-07-15 09:00:00'",
        },
    ],
)
SELECT_CAR_USE_CASE = UseCase(
    name="SELECT_CAR",
    description="The user selects an available car option for their ride, including details such as price, discount, seats, and pickup/dropoff information.",
    event=SelectCarEvent,
    event_source_code=SelectCarEvent.get_source_code_of_class(),
    constraints_generator=generate_select_car_constraints,
    examples=[
        {
            "prompt": "Select car with ride name 'AutoDriverX' and eta equals '1 min away · 1:39 PM'",
            "prompt_for_task_generation": "Select car with ride name 'AutoDriverX' and eta equals '1 min away · 1:39 PM'",
        },
        {
            "prompt": "Select car with ride name 'Comfort' where price equals 31.5 and old price equals 35.0",
            "prompt_for_task_generation": "Select car with ride name 'Comfort' where price equals 31.5 and old price equals 35.0",
        },
        {
            "prompt": "Select car with ride name 'AutoDriverXL' where seats equals 6 and eta equals '3 min away · 1:41 PM'",
            "prompt_for_task_generation": "Select car with ride name 'AutoDriverXL' where seats equals 6 and eta equals '3 min away · 1:41 PM'",
        },
        {
            "prompt": "Select car with pickup '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA' and dropoff '1030 Post Street Apartments - 1030 Post St #112, San Francisco, CA 94109, USA'",
            "prompt_for_task_generation": "Select car with pickup '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA' and dropoff '1030 Post Street Apartments - 1030 Post St #112, San Francisco, CA 94109, USA'",
        },
        {
            "prompt": "Select car where discount percentage equals '10%' and price difference less equal 5.0",
            "prompt_for_task_generation": "Select car where discount percentage equals '10%' and price difference less equal 5.0",
        },
        {
            "prompt": "Select car where scheduled equals '2025-07-18 13:00:00'",
            "prompt_for_task_generation": "Select car where scheduled equals '2025-07-18 13:00:00'",
        },
    ],
)
RESERVE_RIDE_USE_CASE = UseCase(
    name="RESERVE_RIDE",
    description="The user reserves an available car for their ride, including details such as price, discount, seats, and pickup/dropoff information.",
    event=ReserveRideEvent,
    event_source_code=ReserveRideEvent.get_source_code_of_class(),
    constraints_generator=generate_reserve_ride_constraints,
    examples=[
        {
            "prompt": "Reserve ride where ride name is not equals 'AutoDriverX' and pickup equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'",
            "prompt_for_task_generation": "Reserve ride where ride name is not equals 'AutoDriverX' and pickup equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'",
        },
        {
            "prompt": "Reserve ride where ride name contains 'Comfort' and where total price is 31.5 and scheduled time equals '2025-07-18 13:00:00'",
            "prompt_for_task_generation": "Reserve ride where ride name contains 'Comfort' and where total price is 31.5 and scheduled time equals '2025-07-18 13:00:00'",
        },
        {
            "prompt": "Reserve ride where ride name is 'AutoDriverXL' and seats greater than '4' and dropoff '1000 Chestnut Street Apartments - 1000 Chestnut St, San Francisco, CA 94109, USA'",
            "prompt_for_task_generation": "Reserve ride where ride name is 'AutoDriverXL' and seats greater than '4' and dropoff '1000 Chestnut Street Apartments - 1000 Chestnut St, San Francisco, CA 94109, USA'",
        },
        {
            "prompt": "Reserve ride where discount percentage equals '12%' and old price equals 35.0",
            "prompt_for_task_generation": "Reserve ride where discount percentage equals '12%' and old price equals 35.0",
        },
        {
            "prompt": "Reserve ride with pickup '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA' and scheduled at '2025-07-18 13:00:00'",
            "prompt_for_task_generation": "Reserve ride with pickup '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA' and scheduled at '2025-07-18 13:00:00'",
        },
        {
            "prompt": "Reserve ride where ride name is equals 'AutoDriverX' where eta equals '1 min away · 1:39 PM'",
            "prompt_for_task_generation": "Reserve ride where ride name is equals 'AutoDriverX' where eta equals '1 min away · 1:39 PM'",
        },
    ],
)
TRIP_DETAILS_USE_CASE = UseCase(
    name="TRIP_DETAILS",
    description="The user checks details of a specific trip, including pickup, dropoff, date, time and price.",
    event=TripDetailsEvent,
    event_source_code=TripDetailsEvent.get_source_code_of_class(),
    constraints_generator=generate_trip_details_constraints,
    examples=[
        {
            "prompt": "Show trip details where ride name equals 'AutoDriverX' and price equals 26.6",
            "prompt_for_task_generation": "Show trip details where ride name equals 'AutoDriverX' and price equals 26.6",
        },
        {
            "prompt": "Get trip details for pickup '100 Van Ness Ave, San Francisco, CA 94102' and dropoff '1030 Post St, San Francisco, CA 94109'",
            "prompt_for_task_generation": "Get trip details for pickup '100 Van Ness Ave, San Francisco, CA 94102' and dropoff '1030 Post St, San Francisco, CA 94109'",
        },
        {
            "prompt": "Retrieve trip details where price less than 30.0",
            "prompt_for_task_generation": "Retrieve trip details where price less than 30.0",
        },
        {
            "prompt": "Check trip details where scheduled date equals '2025-08-20' and time equals '14:30:00'",
            "prompt_for_task_generation": "Check trip details where scheduled date equals '2025-08-20' and time equals '14:30:00'",
        },
        {
            "prompt": "Find trip details where ride index equals 2 and ride name equals 'Comfort'",
            "prompt_for_task_generation": "Find trip details where ride index equals 2 and ride name equals 'Comfort'",
        },
        {
            "prompt": "Show trip details where pickup label equals '1 Hotel San Francisco' and dropoff label equals 'Ferry Building Marketplace'",
            "prompt_for_task_generation": "Show trip details where pickup label equals '1 Hotel San Francisco' and dropoff label equals 'Ferry Building Marketplace'",
        },
    ],
)
CANCEL_RESERVATION_USE_CASE = UseCase(
    name="CANCEL_RESERVATION",
    description="The user cancels a previously reserved ride, providing details such as ride name, pickup, dropoff, price, and scheduled date/time.",
    event=CancelReservationEvent,
    event_source_code=CancelReservationEvent.get_source_code_of_class(),
    constraints_generator=generate_cancel_reservation_constraints,
    examples=[
        {
            "prompt": "Cancel reservation with ride name 'AutoDriverX'",
            "prompt_for_task_generation": "Cancel reservation with ride name 'AutoDriverX'",
        },
        {
            "prompt": "Cancel reservation for pickup '500 Howard St, San Francisco, CA 94105' and dropoff 'Golden Gate Park, San Francisco, CA'",
            "prompt_for_task_generation": "Cancel reservation for pickup '500 Howard St, San Francisco, CA 94105' and dropoff 'Golden Gate Park, San Francisco, CA'",
        },
        {
            "prompt": "Cancel reservation where scheduled date equals '2025-09-12' and time equals '18:45:00'",
            "prompt_for_task_generation": "Cancel reservation where scheduled date equals '2025-09-12' and time equals '18:45:00'",
        },
        {
            "prompt": "Cancel reservation where price equals 22.5",
            "prompt_for_task_generation": "Cancel reservation where price equals 22.5",
        },
        {
            "prompt": "Cancel reservation with ride index equals 3 and ride name equals 'Comfort'",
            "prompt_for_task_generation": "Cancel reservation with ride index equals 3 and ride name equals 'Comfort'",
        },
        {
            "prompt": "Cancel reservation where pickup label equals 'Moscone Center' and dropoff label equals 'Pier 39'",
            "prompt_for_task_generation": "Cancel reservation where pickup label equals 'Moscone Center' and dropoff label equals 'Pier 39'",
        },
    ],
)


ALL_USE_CASES = [
    # ENTER_LOCATION_USE_CASE,
    # ENTER_DESTINATION_USE_CASE,
    # SEE_PRICES_USE_CASE,
    # SELECT_DATE_USE_CASE,
    # SELECT_TIME_USE_CASE,
    # NEXT_PICKUP_USE_CASE,
    # SEARCH_RIDE_USE_CASE,
    # SELECT_CAR_USE_CASE,
    # RESERVE_RIDE_USE_CASE,
    # TRIP_DETAILS_USE_CASE,
    CANCEL_RESERVATION_USE_CASE,
]
