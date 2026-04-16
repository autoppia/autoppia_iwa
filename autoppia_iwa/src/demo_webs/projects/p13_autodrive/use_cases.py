from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    CancelReservationEvent,
    EnterDestinationEvent,
    EnterLocationEvent,
    NextPickupEvent,
    ReserveRideEvent,
    SearchDestinationEvent,
    SearchLocationEvent,
    SearchRideEvent,
    SelectCarEvent,
    SelectDateEvent,
    SelectTimeEvent,
    TripDetailsEvent,
)
from .generation_functions import (
    generate_enter_destination_constraints,
    generate_enter_location_constraints,
    generate_next_pickup_constraints,
    generate_reserve_ride_constraints,
    generate_search_ride_constraints,
    generate_select_car_constraints,
    generate_select_date_constraints,
    generate_select_time_constraints,
    generate_trip_details_constraints,
)

ENTER_LOCATION_ADDITIONAL_INFO = """
Critical requirements:
1. The request must start with "Enter and select a location...".
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()
ENTER_LOCATION_USE_CASE = UseCase(
    name="ENTER_LOCATION",
    description="The user enters a location value (e.g., city, country, or region)",
    event=EnterLocationEvent,
    event_source_code=EnterLocationEvent.get_source_code_of_class(),
    constraints_generator=generate_enter_location_constraints,
    additional_prompt_info=ENTER_LOCATION_ADDITIONAL_INFO,
    examples=[
        {
            "prompt": "Enter and select a location from dropdown where location equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'",
            "prompt_for_task_generation": "Enter and select a location from dropdown where location equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'",
        },
        {
            "prompt": "Enter and select a location from dropdown where location not equals '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA'",
            "prompt_for_task_generation": "Enter and select a location from dropdown where location not equals '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA'",
        },
        {
            "prompt": "Enter and select a location from dropdown where location contains '1000 Chestnut Street Apartments'",
            "prompt_for_task_generation": "Enter and select a location from dropdown where location contains '1000 Chestnut Street Apartments'",
        },
        {
            "prompt": "Enter and select a location from dropdown where location not contains '1001 Castro Street'",
            "prompt_for_task_generation": "Enter and select a location from dropdown where location not contains '1001 Castro Street'",
        },
    ],
)

ENTER_DESTINATION_ADDITIONAL_INFO = """
Critical requirements:
1. The request must start with "Enter destination...".
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()
ENTER_DESTINATION_USE_CASE = UseCase(
    name="ENTER_DESTINATION",
    description="The user enters a destination value (e.g., city, country, or region)",
    event=EnterDestinationEvent,
    event_source_code=EnterDestinationEvent.get_source_code_of_class(),
    constraints_generator=generate_enter_destination_constraints,
    additional_prompt_info=ENTER_DESTINATION_ADDITIONAL_INFO,
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

SEARCH_DESTINATION_ADDITIONAL_INFO = """
Critical requirements:
1. The request must start with "Search destination...".
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()
SEARCH_DESTINATION_USE_CASE = UseCase(
    name="SEARCH_DESTINATION",
    description="The user search a destination value (e.g., city, country, or region)",
    event=SearchDestinationEvent,
    event_source_code=SearchDestinationEvent.get_source_code_of_class(),
    constraints_generator=generate_enter_destination_constraints,
    additional_prompt_info=SEARCH_DESTINATION_ADDITIONAL_INFO,
    examples=[
        {
            "prompt": "Search destination equals '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA'",
            "prompt_for_task_generation": "Search destination equals '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA'",
        },
        {
            "prompt": "Search destination not equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'",
            "prompt_for_task_generation": "Search destination not equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'",
        },
        {
            "prompt": "Search destination contains '1001 Castro Street'",
            "prompt_for_task_generation": "Search destination contains '1001 Castro Street'",
        },
        {
            "prompt": "Search destination not contains '1000 Chestnut Street Apartments'",
            "prompt_for_task_generation": "Search destination not contains '1000 Chestnut Street Apartments'",
        },
    ],
)

SEARCH_LOCATION_ADDITIONAL_INFO = """
Critical requirements:
1. The request must start with "Search location...".
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()
SEARCH_LOCATION_USE_CASE = UseCase(
    name="SEARCH_LOCATION",
    description="The user searches a location value (e.g., city, country, or region)",
    event=SearchLocationEvent,
    event_source_code=SearchDestinationEvent.get_source_code_of_class(),
    constraints_generator=generate_enter_destination_constraints,
    additional_prompt_info=SEARCH_LOCATION_ADDITIONAL_INFO,
    examples=[
        {
            "prompt": "Search location equals '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA'",
            "prompt_for_task_generation": "Search location equals '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA'",
        },
        {
            "prompt": "Search location not equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'",
            "prompt_for_task_generation": "Search location not equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'",
        },
        {
            "prompt": "Search location contains '1001 Castro Street'",
            "prompt_for_task_generation": "Search location contains '1001 Castro Street'",
        },
        {
            "prompt": "Search location not contains '1000 Chestnut Street Apartments'",
            "prompt_for_task_generation": "Search location not contains '1000 Chestnut Street Apartments'",
        },
    ],
)

SELECT_DATE_ADDITIONAL_INFO = """
Critical requirements:
1. The request must start with "Select date...".
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()

SELECT_DATE_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field in the select date context.

Use natural language only. Do NOT use schema-style field names such as "date" or names with underscores (_).

Do NOT start questions with imperative phrasing like "Select...", "Pick...", or "Choose...".

Always follow this strict question structure:
"Can you please tell me the default pickup <verify field>, so I can continue setting the pickup schedule?"

For example:
- "Can you please tell me the default pickup date, so I can continue setting the pickup schedule?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Ask only for the verify field value.

The output must be a single question asking only for the verify field value.
""".strip()

SELECT_DATE_USE_CASE = UseCase(
    name="SELECT_DATE",
    description="The user selects a specific date for their trip or booking",
    event=SelectDateEvent,
    event_source_code=SelectDateEvent.get_source_code_of_class(),
    constraints_generator=generate_select_date_constraints,
    additional_prompt_info=SELECT_DATE_ADDITIONAL_INFO,
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

SELECT_TIME_ADDITIONAL_INFO = """
Critical requirements:
1. The request must start with "Select time...".
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()

SELECT_TIME_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field in the select time context.

Use natural language only. Do NOT use schema-style field names such as "time" or names with underscores (_).

Refer to the field naturally (for example: selected time, pickup time, trip time).

Do NOT start questions with imperative phrasing like "Select...", "Pick...", or "Choose...".

Always follow this strict question structure:
"Can you please tell me the default pickup <verify field>, so I can continue setting the pickup schedule?"

For example:
- "Can you please tell me the default pickup time, so I can continue setting the pickup schedule?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Ask only for the verify field value.

The output must be a single question asking only for the verify field value.
""".strip()
SELECT_TIME_USE_CASE = UseCase(
    name="SELECT_TIME",
    description="The user selects a specific time for their trip or booking",
    event=SelectTimeEvent,
    event_source_code=SelectTimeEvent.get_source_code_of_class(),
    constraints_generator=generate_select_time_constraints,
    additional_prompt_info=SELECT_TIME_ADDITIONAL_INFO,
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

NEXT_PICKUP_ADDITIONAL_INFO = """
Critical requirements:
1. The request must start with "Next pickup...".
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()
NEXT_PICKUP_USE_CASE = UseCase(
    name="NEXT_PICKUP",
    description="The user clicks the 'Next' button after successfully selecting a pickup date and time.",
    event=NextPickupEvent,
    event_source_code=NextPickupEvent.get_source_code_of_class(),
    constraints_generator=generate_next_pickup_constraints,
    additional_prompt_info=NEXT_PICKUP_ADDITIONAL_INFO,
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

SEARCH_RIDE_ADDITIONAL_INFO = """
Critical requirements:
1. The request must start with "Search ride...".
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()

CAR_SEARCH_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a car in the trip selection context (e.g., ride name, eta, price, old price, description).

Use natural language only. Do NOT use schema-style field names such as "ride_name", "eta", "price", "old_price", "description" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., car name, estimated time, current price, previous price, description).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Select...", "Choose...", or "Book...".

Always follow this strict question structure:
"Can you please tell me the <verify field> of the car whose <question fields with their values> after entering the trip route that is <from> to <to>?"


For example, if the verify field is 'ride_name', format the question exactly like:
- "Can you please tell me the name of the car whose eta is '30 mins', current price is '$20', old price is '$18' and description is 'Affordable everyday rides' after entering the trip route that is from 'Central Park' to 'Airport'?"

Examples:
- "Can you please tell me the current price of the car whose eta is '25 mins' and ride name is 'City Express' and old price is '$18' after entering the trip route that is from 'Station' to 'Museum'?"
- "Can you please tell me the eta of the car whose current price is '$20' and ride name is 'City Cab' after entering the trip route that is from 'Hotel Plaza' to 'Station'?"
- "Can you please tell me the description of the car whose eta is '15 mins' current price is '$30' and old price is '$18' after entering the trip route that is from 'Airport' to 'Central Park'?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
""".strip()

SEARCH_RIDE_USE_CASE = UseCase(
    name="SEARCH",
    description="The user clicks on the 'Search' button after selecting pickup, dropoff, and optionally scheduling a ride.",
    event=SearchRideEvent,
    event_source_code=SearchRideEvent.get_source_code_of_class(),
    constraints_generator=generate_search_ride_constraints,
    additional_prompt_info=SEARCH_RIDE_ADDITIONAL_INFO,
    examples=[
        {
            "prompt": "Search ride after successfully selects pickup location from dropdown that is not equals '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA'",
            "prompt_for_task_generation": "Search ride after successfully selects pickup location from dropdown that is not equals '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA'",
        },
        {
            "prompt": "Search ride after successfully selects dropoff location from dropdown that is not contains '100 Van Ness'",
            "prompt_for_task_generation": "Search ride after successfully selects dropoff location from dropdown that is not contains '100 Van Ness'",
        },
        {
            "prompt": "Search ride after successfully selects pickup scheduled date and time equals to '2025-08-31 13:00:00'",
            "prompt_for_task_generation": "Search ride after successfully selects pickup scheduled date and time equals to '2025-08-31 13:00:00'",
        },
        {
            "prompt": "Search ride after successfully selects pickup scheduled date and time greater than '2025-08-31 13:00:00'",
            "prompt_for_task_generation": "Search ride after successfully selects pickup scheduled date and time greater than to '2025-08-31 13:00:00'",
        },
    ],
)

SELECT_CAR_ADDITIONAL_INFO = """
Critical requirements:
1. The request must start with "Select car...".
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()

SELECT_CAR_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a car in the trip selection context (e.g., ride name, eta, current price, old price, description).

Use natural language only. Do NOT use schema-style field names such as "ride_name", "eta", "price", "old_price", "description" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., car name, estimated time, current price, old price, description).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Select...", "Choose...", or "Book...".

Always follow this strict question structure:
"Can you please tell me the <verify field> of the car whose <question fields with their values> after entering the trip route that is <from> to <to>, so I can select it?"


For example, if the verify field is 'ride_name', format the question exactly like:
- "Can you please tell me the name of the car whose eta is '30 mins', current price is '$20', old price is '$18' and description is 'Affordable everyday rides' after entering the trip route that is from 'Central Park' to 'Airport', so I can select it?"

Examples:
- "Can you please tell me the current price of the car whose eta is '25 mins' and ride name is 'City Express' and old price is '$18' after entering the trip route that is from 'Station' to 'Museum', so I can select it?"
- "Can you please tell me the eta of the car whose current price is '$20' and ride name is 'City Cab' after entering the trip route that is from 'Hotel Plaza' to 'Station', so I can select it?"
- "Can you please tell me the description of the car whose eta is '15 mins', current price is '$30' and old price is '$18' after entering the trip route that is from 'Airport' to 'Central Park', so I can select it?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
""".strip()

SELECT_CAR_USE_CASE = UseCase(
    name="SELECT_CAR",
    description="The user selects an available car option for their ride, including details such as price, discount, seats, and pickup/dropoff information.",
    event=SelectCarEvent,
    event_source_code=SelectCarEvent.get_source_code_of_class(),
    constraints_generator=generate_select_car_constraints,
    additional_prompt_info=SELECT_CAR_ADDITIONAL_INFO,
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

RESERVE_RIDE_ADDITIONAL_INFO = """
Critical requirements:
1. The request must start with "Reserve ride...".
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()

RESERVE_RIDE_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a car in the trip selection context (e.g., ride name, eta, current price, old price, description).

Use natural language only. Do NOT use schema-style field names such as "ride_name", "eta", "price", "old_price", "description" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., car name, estimated time, current price, old price, description).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Select...", "Choose...", or "Reserve...".

Always follow this strict question structure:
"Can you please tell me the <verify field> of the car whose <question fields with their values> after entering the trip route that is <from> to <to>, so I can reserve it?"


For example, if the verify field is 'ride_name', format the question exactly like:
- "Can you please tell me the name of the car whose eta is '30 mins', current price is '$20', old price is '$18' and description is 'Affordable everyday rides' after entering the trip route that is from 'Central Park' to 'Airport', so I can reserve it?"

Examples:
- "Can you please tell me the current price of the car whose eta is '25 mins' and ride name is 'City Express' and old price is '$18' after entering the trip route that is from 'Station' to 'Museum', so I can reserve it?"
- "Can you please tell me the eta of the car whose current price is '$20' and ride name is 'City Cab' after entering the trip route that is from 'Hotel Plaza' to 'Station', so I can reserve it?"
- "Can you please tell me the description of the car whose eta is '15 mins', current price is '$30' and old price is '$18' after entering the trip route that is from 'Airport' to 'Central Park', so I can reserve it?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
""".strip()

RESERVE_RIDE_USE_CASE = UseCase(
    name="RESERVE_RIDE",
    description="The user reserves an available car for their ride, including details such as price, discount, seats, and pickup/dropoff information.",
    event=ReserveRideEvent,
    event_source_code=ReserveRideEvent.get_source_code_of_class(),
    constraints_generator=generate_reserve_ride_constraints,
    additional_prompt_info=RESERVE_RIDE_ADDITIONAL_INFO,
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

TRIP_DETAILS_ADDITIONAL_INFO = """
Critical requirements:
1. The request must start with "View trip details...".
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()

TRIP_DETAILS_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a trip in the trip details context (e.g., title, date, price, time).

Use natural language only. Do NOT use schema-style field names such as "title", "date", "price", "time" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., trip title, date, price, time).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "View...", "Check...", or "See...".

For example, if the verify field is 'price', format the question naturally:
- "What is the price of the trip whose title 'Beach Vacation', date is '6/13/2024' and time is '6:17:48 PM'?"

Examples:
- "What is the trip title whose date is '6/12/2024', price is '$50', and time is '9:04:31 PM'?"
- "What is the date of the trip whose title 'Mountain Adventure', price is '$20.3' and time is '1:04:31 PM'?"
- "What is the time of the trip whose title 'City Tour', date is '10/21/2025' and price is '$31.4'?"
- "What is the price of the trip whose title 'Desert Safari', date is '2/27/2025' and time is '8:38:14 AM'?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only non-verify fields for identification.
- Always include all question fields with values in the question for precise identification.

The output must be a single question asking only for the verify field value.
""".strip()

TRIP_DETAILS_USE_CASE = UseCase(
    name="TRIP_DETAILS",
    description="The user views details of a trip, including trip information, ride details, driver information, and location details.",
    event=TripDetailsEvent,
    event_source_code=TripDetailsEvent.get_source_code_of_class(),
    constraints_generator=generate_trip_details_constraints,
    additional_prompt_info=TRIP_DETAILS_ADDITIONAL_INFO,
    examples=[
        {
            "prompt": "View trip details where ride name is not equals 'AutoDriverX' and pickup equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'",
            "prompt_for_task_generation": "View trip details where ride name is not equals 'AutoDriverX' and pickup equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'",
        },
        {
            "prompt": "View trip details where ride name contains 'Comfort' and where total price is 31.5 and scheduled time equals '2025-07-18 13:00:00'",
            "prompt_for_task_generation": "View trip details where ride name contains 'Comfort' and where total price is 31.5 and scheduled time equals '2025-07-18 13:00:00'",
        },
        {
            "prompt": "View trip details where ride name is 'AutoDriverXL' and seats greater than '4' and dropoff '1000 Chestnut Street Apartments - 1000 Chestnut St, San Francisco, CA 94109, USA'",
            "prompt_for_task_generation": "View trip details where ride name is 'AutoDriverXL' and seats greater than '4' and dropoff '1000 Chestnut Street Apartments - 1000 Chestnut St, San Francisco, CA 94109, USA'",
        },
        {
            "prompt": "View trip details where discount percentage equals '12%' and old price equals 35.0",
            "prompt_for_task_generation": "View trip details where discount percentage equals '12%' and old price equals 35.0",
        },
        {
            "prompt": "View trip details with pickup '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA' and scheduled at '2025-07-18 13:00:00'",
            "prompt_for_task_generation": "View trip details with pickup '100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA' and scheduled at '2025-07-18 13:00:00'",
        },
        {
            "prompt": "View trip details where ride name is equals 'AutoDriverX' where eta equals '1 min away · 1:39 PM'",
            "prompt_for_task_generation": "View trip details where ride name is equals 'AutoDriverX' where eta equals '1 min away · 1:39 PM'",
        },
    ],
)

CANCEL_RESERVATION_ADDITIONAL_INFO = """
Critical requirements:
1. The request must start with "Cancel reservation...".
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()
CANCEL_RESERVATION_USE_CASE = UseCase(
    name="CANCEL_RESERVATION",
    description="The user cancels a trip reservation, including the trip ID and cancellation reason.",
    event=CancelReservationEvent,
    event_source_code=CancelReservationEvent.get_source_code_of_class(),
    constraints_generator=generate_reserve_ride_constraints,
    additional_prompt_info=CANCEL_RESERVATION_ADDITIONAL_INFO,
    examples=[
        {
            "prompt": "Cancel ride reservation where ride name is not equals 'AutoDriverX' and pickup equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'",
            "prompt_for_task_generation": "Cancel ride reservation where ride name is not equals 'AutoDriverX' and pickup equals '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'",
        },
        {
            "prompt": "Cancel ride reservation where ride name contains 'Comfort' and where total price is 31.5 and scheduled time equals '2025-07-18 13:00:00'",
            "prompt_for_task_generation": "Cancel ride reservation where ride name contains 'Comfort' and where total price is 31.5 and scheduled time equals '2025-07-18 13:00:00'",
        },
        {
            "prompt": "Cancel ride reservation where ride name is 'AutoDriverXL' and seats greater than '4' and dropoff '1000 Chestnut Street Apartments - 1000 Chestnut St, San Francisco, CA 94109, USA'",
            "prompt_for_task_generation": "Cancel ride reservation where ride name is 'AutoDriverXL' and seats greater than '4' and dropoff '1000 Chestnut Street Apartments - 1000 Chestnut St, San Francisco, CA 94109, USA'",
        },
        {
            "prompt": "Cancel ride reservation where discount percentage equals '12%' and old price equals 35.0",
            "prompt_for_task_generation": "Cancel ride reservation where discount percentage equals '12%' and old price equals 35.0",
        },
    ],
)


ALL_USE_CASES = [
    ENTER_LOCATION_USE_CASE,
    ENTER_DESTINATION_USE_CASE,
    SEARCH_LOCATION_USE_CASE,
    SEARCH_DESTINATION_USE_CASE,
    SELECT_DATE_USE_CASE,
    SELECT_TIME_USE_CASE,
    NEXT_PICKUP_USE_CASE,
    SEARCH_RIDE_USE_CASE,
    SELECT_CAR_USE_CASE,
    RESERVE_RIDE_USE_CASE,
    TRIP_DETAILS_USE_CASE,
    CANCEL_RESERVATION_USE_CASE,
]
