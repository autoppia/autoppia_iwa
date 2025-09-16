from ...classes import UseCase
from .events import (
    AddToWishlistEvent,
    BackToAllHotelsEvent,
    ConfirmAndPayEvent,
    EditCheckInOutDatesEvent,
    IncreaseNumberOfGuestsEvent,
    MessageHostEvent,
    ReserveHotelEvent,
    SearchHotelEvent,
    ShareHotelEvent,
    ViewHotelEvent,
)
from .generation_functions import (
    generate_confirm_and_pay_constraints,
    generate_edit_checkin_checkout_constraints,
    generate_increase_guests_constraints,
    generate_message_host_constraints,
    generate_reserve_hotel_constraints,
    generate_search_hotel_constraints,
    generate_share_hotel_constraints,
    generate_view_hotel_constraints,
)

###############################################################################
# SEARCH_HOTEL_USE_CASE
###############################################################################

SEARCH_HOTEL_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Be an EXPLICIT search for hotels using terms like:
   - "Search for hotels..."
   - "Find hotels in..."
   - "Look up hotels near..."
2. May optionally include details such as:
   - Destination or area (e.g., 'Murree', 'beachside', 'city center')
   - Travel dates (check-in and check-out)
   - Guest details: number of adults, children, infants, or pets
3. DO NOT include any other interactions like hotel selection, booking, or viewing details - just the search intent.
4. For constraint of search term, if the operator is 'contains', mention that substring exactly:
    Example:
    constraint:{'search_term': {'operator': 'contains', 'value': 'k, Ic'}}},
    prompt:
    CORRECT: Search for hotels where the search term CONTAINS 'k, Ic'
    INCORRECT: Search for hotels where the search term CONTAINS 'k' and 'Ic'
"""

SEARCH_HOTEL_USE_CASE = UseCase(
    name="SEARCH_HOTEL",
    description="The user searches for hotels with optional filters like location, dates, and guest composition.",
    event=SearchHotelEvent,
    event_source_code=SearchHotelEvent.get_source_code_of_class(),
    constraints_generator=generate_search_hotel_constraints,
    additional_prompt_info=SEARCH_HOTEL_INFO,
    examples=[
        {
            "prompt": "Search for hotels where search term is Murree from July 25 to July 28 for 2 adults and 1 child",
            "prompt_for_task_generation": "Search for hotels where search term is Murree from July 25 to July 28 for 2 adults and 1 child",
        },
        {
            "prompt": "Search for hotel where search term is Lake View, for 2 adults and no kids",
            "prompt_for_task_generation": "Search for hotel where search term is Lake View, for 2 adults and no kids",
        },
        {
            "prompt": "Search for hotels from August 10 to August 12 for a family of 4 with a pet",
            "prompt_for_task_generation": "Search for hotels from August 10 to August 12 for a family of 4 with a pet",
        },
        {
            "prompt": "Search for hotels where search term is Skardu",
            "prompt_for_task_generation": "Search for hotels where search term in Skardu",
        },
        {
            "prompt": "Find a hotel where search term is Mall Road for 3 adults and 1 infant",
            "prompt_for_task_generation": "Find a hotel where search term is Mall Road for 3 adults and 1 infant",
        },
    ],
)

###############################################################################
# VIEW_HOTEL_USE_CASE
###############################################################################


VIEW_HOTEL_INFO = """
Make sure to mention all constraints in the prompt.
CRITICAL REQUIREMENT:
1. If the constraints contain amenities, be sure to include them, especially for `in_list` and `not_in_list` operators, and mention them like:
   Examples:
   Constraint: {'amenities': {'operator': 'in_list', 'value': ['Memory foam mattress', 'Historic charm']}}
   Prompt: "Retrieve details of a hotel that has amenities in the list ['Memory foam mattress', 'Historic charm']."
"""

VIEW_HOTEL_USE_CASE = UseCase(
    name="VIEW_HOTEL",
    description="Triggered when the user views a specific hotel listing with detailed information.",
    event=ViewHotelEvent,
    event_source_code=ViewHotelEvent.get_source_code_of_class(),
    constraints_generator=generate_view_hotel_constraints,
    additional_prompt_info=VIEW_HOTEL_INFO,
    examples=[
        {
            "prompt": "I like the one in Murree with 5-star rating and free breakfast. Can you show me more about it?",
            "prompt_for_task_generation": "View hotel in Murree with 5-star rating and free breakfast.",
        },
        {
            "prompt": "Open the second hotel from the list - the one hosted by Fatima since 2018, I think.",
            "prompt_for_task_generation": "View hotel hosted by Fatima since 2018.",
        },
        {
            "prompt": "The luxury suite with mountain views and a private pool looks good. Let me check it out.",
            "prompt_for_task_generation": "View hotel with mountain views and private pool.",
        },
        {
            "prompt": "What's the deal with that hotel in Lahore under 12k per night, rated above 4.5?",
            "prompt_for_task_generation": "View hotel in Lahore with price under 12000 and rating above 4.5.",
        },
        {
            "prompt": "Show me the villa hosted by someone with great reviews - the one that says 'hosted since 2016'.",
            "prompt_for_task_generation": "View hotel hosted since 2016 with high host rating.",
        },
        {
            "prompt": "Let me see the hotel with the heated indoor pool and close to downtown Karachi.",
            "prompt_for_task_generation": "View hotel in downtown Karachi with heated indoor pool.",
        },
        {
            "prompt": "Open the listing that includes free parking, pet-friendly options, and balcony views.",
            "prompt_for_task_generation": "View hotel with free parking, pet-friendly, and balcony view amenities.",
        },
    ],
)

ADD_TO_WISHLIST_INFO = """
CRITICAL REQUIREMENT:
1. If constraints include amenities, price, rating, or location, they must be mentioned in the prompt clearly.
2. Emphasize intent to 'save', 'wishlist', 'mark as favorite', or similar phrasing that implies adding a hotel to the user's wishlist.

Examples:
Constraint: {'amenities': {'operator': 'in_list', 'value': ['Pool', 'City view']}}
Prompt: "Add to wishlist a hotel that has a pool and city view."
"""

ADD_TO_WISHLIST_USE_CASE = UseCase(
    name="ADD_TO_WISHLIST",
    description="Triggered when the user adds a hotel listing to their wishlist.",
    event=AddToWishlistEvent,
    event_source_code=AddToWishlistEvent.get_source_code_of_class(),
    constraints_generator=generate_view_hotel_constraints,
    additional_prompt_info=ADD_TO_WISHLIST_INFO,
    examples=[
        {
            "prompt": "Add that beautiful hotel in Skardu with the river view to my wishlist.",
            "prompt_for_task_generation": "Add to wishlist hotel in Skardu with river view.",
        },
        {
            "prompt": "I want to save the one in Islamabad with the rooftop pool and gym.",
            "prompt_for_task_generation": "Add to wishlist hotel in Islamabad with rooftop pool and gym.",
        },
        {
            "prompt": "Mark the luxury villa in Murree with the hot tub as a favorite.",
            "prompt_for_task_generation": "Add to wishlist luxury villa in Murree with hot tub.",
        },
        {
            "prompt": "Save the hotel near downtown Karachi under 10k per night with great reviews.",
            "prompt_for_task_generation": "Add to wishlist hotel near downtown Karachi with price under 10000 and high rating.",
        },
        {
            "prompt": "I loved the place with the mountain view and free breakfast - please add it to my list.",
            "prompt_for_task_generation": "Add to wishlist hotel with mountain view and free breakfast.",
        },
        {
            "prompt": "Bookmark the listing hosted by Ayesha that has 5 stars and private parking.",
            "prompt_for_task_generation": "Add to wishlist hotel hosted by Ayesha with 5-star rating and private parking.",
        },
    ],
)

SHARE_HOTEL_INFO = """
CRITICAL REQUIREMENTS:
1. The prompt should clearly indicate the intent to share a hotel with someone via email or other means.
2. If the constraints include amenities, price, rating, or location, mention them clearly in the prompt.
3. If an email is part of the constraint, it should be reflected explicitly (e.g., "share with my friend at abc@example.com").
4. Explicitly mention the email constraint operator in the prompt and all the constraint operators explicitly.

Examples:
Constraint: {'email': {'operator': 'equals', 'value': 'friend@example.com'}}
Prompt: "Share the hotel with friend@example.com."

Constraint: {'email': {'operator': 'contains', 'value': '.scott@design}}
Prompt: "Share the hotel with email that contains '.scott@design'."
MENTION the constraint operator defined in the prompt.
"""

SHARE_HOTEL_USE_CASE = UseCase(
    name="SHARE_HOTEL",
    description="Triggered when the user shares a hotel listing with someone, typically via email.",
    event=ShareHotelEvent,
    event_source_code=ShareHotelEvent.get_source_code_of_class(),
    constraints_generator=generate_share_hotel_constraints,
    additional_prompt_info=SHARE_HOTEL_INFO,
    examples=[
        {
            "prompt": "Share the hotel listing with zoe.baker@civicgroup.org where the title does NOT contain lcu, location does NOT contain pep, rating equals 4.5, price is less than or equal to 198, reviews are less than or equal to 44, available from a date before 2025-07-16 00:00:00 to a date on or after 2025-07-16 00:00:00, for 5 guests, hosted by Brian, and amenities do NOT contain Art-inspired decor.",
            "prompt_for_task_generation": "Share the hotel listing with zoe.baker@civicgroup.org where the title does NOT contain lcu, location does NOT contain pep, rating equals 4.5, price is less than or equal to 198, reviews are less than or equal to 44, available from a date before 2025-07-16 00:00:00 to a date on or after 2025-07-16 00:00:00, for 5 guests, hosted by Brian, and amenities do NOT contain Art-inspired decor.",
        },
        {
            "prompt": "Please email zoe.baker@civicgroup.org any hotel hosted by Brian that sleeps 5, costs at most $198, has a 4.5 rating, reviews ≤ 44, excludes 'Art-inspired decor', and is available around 2025-07-16.",
            "prompt_for_task_generation": "Please email zoe.baker@civicgroup.org any hotel hosted by Brian that sleeps 5, costs at most $198, has a 4.5 rating, reviews ≤ 44, excludes 'Art-inspired decor', and is available around 2025-07-16.",
        },
        {
            "prompt": "Share with zoe.baker@civicgroup.org: Brian's 5-guest listing ≤198 USD, rating 4.5, reviews ≤44, exclude titles with 'lcu' and locations with 'pep', and no 'Art-inspired decor' in amenities. Availability must include 2025-07-16.",
            "prompt_for_task_generation": "Share with zoe.baker@civicgroup.org: Brian's 5-guest listing ≤198 USD, rating 4.5, reviews ≤44, exclude titles with 'lcu' and locations with 'pep', and no 'Art-inspired decor' in amenities. Availability must include 2025-07-16.",
        },
        {
            "prompt": "Send to zoe.baker@civicgroup.org any hotel (host: Brian) for five guests, price up to $198, rating exactly 4.5, reviews up to 44, and do not include properties with 'Art-inspired decor'. Make sure availability covers the date 2025-07-16.",
            "prompt_for_task_generation": "Send to zoe.baker@civicgroup.org any hotel (host: Brian) for five guests, price up to $198, rating exactly 4.5, reviews up to 44, and do not include properties with 'Art-inspired decor'. Make sure availability covers the date 2025-07-16.",
        },
        {
            "prompt": "Share Brian's 5-person, ≤$198 hotel (rating 4.5, reviews ≤44) with zoe.baker@civicgroup.org; exclude 'lcu' in title, 'pep' in location, and any listing with 'Art-inspired decor'.",
            "prompt_for_task_generation": "Share Brian's 5-person, ≤$198 hotel (rating 4.5, reviews ≤44) with zoe.baker@civicgroup.org; exclude 'lcu' in title, 'pep' in location, and any listing with 'Art-inspired decor'.",
        },
    ],
)

###############################################################################
# INCREASE_NUMBER_OF_GUESTS_USE_CASE
###############################################################################

INCREASE_NUMBER_OF_GUESTS_INFO = """
CRITICAL REQUIREMENT:
1. Mention increment of guests only in prompt.
2. Do NOT add any details other than number of guests.
3. Start prompt with "Increase number of guests where" or similar phrases.
4. Keep the constraints values as it is in the prompt, and do not complete or correct them.

✅ CORRECT EXAMPLE:
Increase number of guests where guests_to is less than or equal to '2' and rating is greater than '4.1' and amenities contains 'owntown core' and location equals 'Toronto, Canada'

❌ INCORRECT EXAMPLES:

# ❌ Fixing or completing constraint values:
Increase number of guests where guests_to is less than or equal to '2' and rating is greater than '4.1' and amenities contains 'downtown core' and location equals 'Toronto, Canada'
# (The test data says 'owntown core' — do not correct it to 'downtown core')

# ❌ Adding extra context/details:
Increase number of guests where guests_to is less than or equal to '2' and rating is greater than '4.1' and amenities contains 'owntown core' and location equals 'Toronto, Canada' because we need to accommodate more people

# ❌ Prompt doesn't start correctly:
We need to increase the number of guests where guests_to is less than or equal to '2'...

# ❌ Talks about other fields like price or availability:
Increase number of guests and update availability where guests_to is less than or equal to '2'...
"""

INCREASE_NUMBER_OF_GUESTS_USE_CASE = UseCase(
    name="INCREASE_NUMBER_OF_GUESTS",
    description="Triggered when the user increases the number of guests for a booking or search.",
    event=IncreaseNumberOfGuestsEvent,
    event_source_code=IncreaseNumberOfGuestsEvent.get_source_code_of_class(),
    constraints_generator=generate_increase_guests_constraints,
    additional_prompt_info=INCREASE_NUMBER_OF_GUESTS_INFO,
    examples=[
        {
            "prompt": "Increase number of guests where guests_to is 3.",
            "prompt_for_task_generation": "Increase number of guests where guests_to is 3.",
        },
        {
            "prompt": "Increase guests count to 4.",
            "prompt_for_task_generation": "Increase guests count to 4.",
        },
        {
            "prompt": "Increase number of guests where guests are greater than 4.",
            "prompt_for_task_generation": "Increase number of guests where guests are greater than 4.",
        },
    ],
)
###############################################################################
# RESERVE_HOTEL_USE_CASE
###############################################################################
RESERVE_HOTEL_INFO = """
Important:
1. Begin your request by phrases like: 'Reserve the hotel...', 'Book the hotel for...', or similar.
2. Keep the constraints values as it is in the prompt, and do not complete or correct them.
    ⚠️ Do not add values not present in event_criteria (e.g., if guests = 1, do NOT write '1 and 2')
3. Do NOT split, rephrase, or interpret list values. Use them exactly as shown in event_criteria.
    Example:
        'amenities': {'operator': 'in_list', 'value': ['Ski-in, Ski-out']}

    ✅ Correct: amenities in list ['Ski-in, Ski-out']
    ❌ Incorrect: amenities include 'Ski-in' or 'Ski-out'

EXAMPLES:

✅ CORRECT:
Reserve the hotel for a stay with guests NOT equal to '1' at a location that does NOT contain 'kjo' AND amenities NOT in list ['Self check-in', 'Fast WiFi'] AND title contains 'owe' AND rating less than '6.714277681586925' AND reviews greater equal '212'

❌ INCORRECT:
Reserve the hotel for a stay with guests NOT equal to '1' AND '2'...  # (Added extra guest value not in criteria)
"""

RESERVE_HOTEL_USE_CASE = UseCase(
    name="RESERVE_HOTEL",
    description="Triggered when the user confirms a reservation or booking for a hotel.",
    event=ReserveHotelEvent,
    event_source_code=ReserveHotelEvent.get_source_code_of_class(),
    constraints_generator=generate_reserve_hotel_constraints,
    additional_prompt_info=RESERVE_HOTEL_INFO,
    examples=[
        {
            "prompt": "Reserve hotel from 5th to 9th August for 2 guests.",
            "prompt_for_task_generation": "Reserve hotel from 5th to 9th August for 2 guests.",
        },
        {
            "prompt": "Reserve the mountain view cottage we just looked at for 3 guests, next weekend.",
            "prompt_for_task_generation": "Reserve hotel for 3 guests for the upcoming weekend.",
        },
        {
            "prompt": "I want to confirm my stay from Sept 1st to Sept 4th, just me.",
            "prompt_for_task_generation": "Reserve hotel for 1 guest from September 1st to 4th.",
        },
        {
            "prompt": "Reserve hotel for 3 guests from Friday to Sunday.",
            "prompt_for_task_generation": "Reserve hotel for 3 guests from Friday to Sunday.",
        },
        {
            "prompt": "Reserve hotel from May 10th to 14th for 4 guests.",
            "prompt_for_task_generation": "Reserve hotel from May 10th to 14th for 4 guests.",
        },
        {
            "prompt": "Reserve hotel for 2 guests starting next Thursday for 3 nights.",
            "prompt_for_task_generation": "Reserve hotel for 2 guests starting next Thursday for 3 nights.",
        },
    ],
)

###############################################################################
# EDIT_CHECK_IN_OUT_DATES_USE_CASE
###############################################################################


EDIT_CHECK_IN_OUT_DATES_INFO = """
CRITICAL REQUIREMENTS:
1. Start the prompt like:
    Example: Edit checkin checkout dates where checkin date <operator> <checkin-date> and checkout date <operator> <checkout-date> ...
2. Keep the constraints values as it is in the prompt, and do not complete or correct them.
    Do not add values not present in event_criteria (e.g., if guests = 1, do NOT write '1 and 2')
3. Do NOT split, rephrase, or interpret list values. Use them exactly as shown in event_criteria.
    Example:
        'amenities': {'operator': 'in_list', 'value': ['Ski-in, Ski-out']}

    Correct: amenities in list ['Ski-in, Ski-out']
    Incorrect: amenities include 'Ski-in' or 'Ski-out'

"""

EDIT_CHECK_IN_OUT_DATES_USE_CASE = UseCase(
    name="EDIT_CHECK_IN_OUT_DATES",
    description="Triggered when a user edits the check-in or check-out dates of a reservation or search.",
    event=EditCheckInOutDatesEvent,
    event_source_code=EditCheckInOutDatesEvent.get_source_code_of_class(),
    constraints_generator=generate_edit_checkin_checkout_constraints,
    additional_prompt_info=EDIT_CHECK_IN_OUT_DATES_INFO,
    examples=[
        {
            "prompt": "Edit checkin checkout dates where check-in date greater than August 12, 2025 and check-out date less than or equal September 1, 2025.",
            "prompt_for_task_generation": "Edit checkin checkout dates where check-in date greater than August 12, 2025 and check-out date less than or equal September 1, 2025.",
        },
        {
            "prompt": "Edit checkin checkout dates where check-in date not equal to September 5, 2025 and check-out date equal to September 9, 2025.",
            "prompt_for_task_generation": "Edit checkin checkout dates where check-in date not equal to September 5, 2025 and check-out date equal to September 9, 2025.",
        },
        {
            "prompt": "Edit checkin checkout dates where check-in date less than September 18, 2025 and check-out date greater than or equal September 22, 2025.",
            "prompt_for_task_generation": "Edit checkin checkout dates where check-in date less than September 18, 2025 and check-out date greater than or equal September 22, 2025.",
        },
        {
            "prompt": "Edit checkin checkout dates where check-in date equal to October 2, 2025 and check-out date greater than October 5, 2025.",
            "prompt_for_task_generation": "Edit checkin checkout dates where check-in date equal to October 2, 2025 and check-out date greater than October 5, 2025.",
        },
        {
            "prompt": "Edit checkin checkout dates where check-in date not equal to October 11, 2025 and check-out date less than October 15, 2025.",
            "prompt_for_task_generation": "Edit checkin checkout dates where check-in date not equal to October 11, 2025 and check-out date less than October 15, 2025.",
        },
    ],
)

###############################################################################
# CONFIRM_AND_PAY_USE_CASE
###############################################################################

CONFIRM_AND_PAY_INFO = """
CRITICAL REQUIREMENT:
1. Start the prompt with details confirmation like:
    Please confirm the booking details for a stay where ...
2. Keep the constraints values as it is in the prompt, and do not complete or correct them.
    Do not add values not present in event_criteria (e.g., if guests = 1, do NOT write '1 and 2')
3. Do NOT split, rephrase, or interpret list values. Use them exactly as shown in event_criteria.
    Example:
        'amenities': {'operator': 'in_list', 'value': ['Ski-in, Ski-out']}

    Correct: amenities in list ['Ski-in, Ski-out']
    Incorrect: amenities include 'Ski-in' or 'Ski-out'

EXAMPLES:

CORRECT:
Please confirm the booking details for a stay where guests NOT equal to '1' at a location that does NOT contain 'kjo' AND amenities NOT in list ['Self check-in', 'Fast WiFi'] AND title contains 'owe' AND rating less than '6.714277681586925' AND reviews greater equal '212'

INCORRECT:
Please confirm the booking details for a stay where guests NOT equal to '1' AND '2'...  # (Added extra guest value not in criteria)
"""

CONFIRM_AND_PAY_USE_CASE = UseCase(
    name="CONFIRM_AND_PAY",
    description="Triggered when the user confirms booking details and initiates payment.",
    event=ConfirmAndPayEvent,
    event_source_code=ConfirmAndPayEvent.get_source_code_of_class(),
    constraints_generator=generate_confirm_and_pay_constraints,
    additional_prompt_info=CONFIRM_AND_PAY_INFO,
    examples=[
        {
            "prompt": "Everything looks great - the beach house in Malibu from Aug 15-19 for 2 guests. Use my Visa ending in 4242 to confirm and pay.",
            "prompt_for_task_generation": "Everything looks great - the beach house in Malibu from Aug 15-19 for 2 guests. Use my Visa ending in 4242 to confirm and pay.",
        },
        {
            "prompt": "Confirm the apartment in NYC, Aug 10 to 13, 3 guests. Pay with my Mastercard ending in 1234.",
            "prompt_for_task_generation": "Confirm the apartment in NYC, Aug 10 to 13, 3 guests. Pay with my Mastercard ending in 1234.",
        },
        {
            "prompt": "The mountain cabin from Sept 2 to 5 for 4 guests looks perfect. Go ahead and charge my PayPal.",
            "prompt_for_task_generation": "The mountain cabin from Sept 2 to 5 for 4 guests looks perfect. Go ahead and charge my PayPal.",
        },
        {
            "prompt": "Book the downtown loft for 2 guests from July 25-28. Pay in PKR using my saved card.",
            "prompt_for_task_generation": "Book the downtown loft for 2 guests from July 25-28. Pay in PKR using my saved card.",
        },
        {
            "prompt": "Confirm the booking - Lakeview Villa, August 12-15, 5 guests. Complete the payment now.",
            "prompt_for_task_generation": "Confirm the booking - Lakeview Villa, August 12-15, 5 guests. Complete the payment now.",
        },
        {
            "prompt": "Looks good: Santorini Suite, Sept 10-14, 2 guests. Finalize and charge my card.",
            "prompt_for_task_generation": "Looks good: Santorini Suite, Sept 10-14, 2 guests. Finalize and charge my card.",
        },
        {
            "prompt": "Confirm all details - 3 nights in Dubai, 2 guests, Sept 20-23. Proceed to payment with saved Visa.",
            "prompt_for_task_generation": "Confirm all details - 3 nights in Dubai, 2 guests, Sept 20-23. Proceed to payment with saved Visa.",
        },
        {
            "prompt": "Confirm the treehouse stay from Aug 30 to Sept 2 for 2. Pay with Apple Pay.",
            "prompt_for_task_generation": "Confirm the treehouse stay from Aug 30 to Sept 2 for 2. Pay with Apple Pay.",
        },
        {
            "prompt": "Yes, confirm this listing for 1 guest, July 29-Aug 1. Go ahead and apply my saved card.",
            "prompt_for_task_generation": "Yes, confirm this listing for 1 guest, July 29-Aug 1. Go ahead and apply my saved card.",
        },
    ],
)

###############################################################################
# MESSAGE_HOST_USE_CASE
###############################################################################


MESSAGE_HOST_INFO = """
CRITICAL REQUIREMENTS:
1. Use explicit phrases such as 'Message the host where message ...',or similar.
2. Keep the constraints values as it is in the prompt, and do not complete or correct them.
    ⚠️ Do not add values not present in event_criteria (e.g., if guests = 1, do NOT write '1 and 2')
3. Do NOT split, rephrase, or interpret list values. Use them exactly as shown in event_criteria.
    Example:
        'amenities': {'operator': 'in_list', 'value': ['Ski-in, Ski-out']}

    ✅ Correct: amenities in list ['Ski-in, Ski-out']
    ❌ Incorrect: amenities include 'Ski-in' or 'Ski-out'

EXAMPLES:

✅ CORRECT:
Message the host with message equals 'Is early check-in possible?', guests NOT equal to '1' at a location that does NOT contain 'kjo' AND amenities NOT in list ['Self check-in', 'Fast WiFi'] AND title contains 'owe' AND rating less than '6.714277681586925' AND reviews greater equal '212'

❌ INCORRECT:
Message the host with message equals 'Is early check-in possible?', guests NOT equal to '1' AND '2'...  # (Added extra guest value not in criteria)
"""

MESSAGE_HOST_USE_CASE = UseCase(
    name="MESSAGE_HOST",
    description="Triggered when the user sends a message to the host.",
    event=MessageHostEvent,
    event_source_code=MessageHostEvent.get_source_code_of_class(),
    constraints_generator=generate_message_host_constraints,
    additional_prompt_info=MESSAGE_HOST_INFO,
    examples=[
        {
            "prompt": "Message host Natalie where message contains 'ly check-in possible?', title contains 'cozy' and location equals 'New York'",
            "prompt_for_task_generation": "Message host Natalie where message contains 'ly check-in possible?', title contains 'cozy' and location equals 'New York'",
        },
        {"prompt": "Message host where message equals 'I will be arriving around 10pm.'", "prompt_for_task_generation": "Message host where message equals 'I will be arriving around 10pm.'"},
        {"prompt": "Message host John where message not contains 'no pets'", "prompt_for_task_generation": "Message host John where message not contains 'no pets'"},
        {"prompt": "Message host where message not equals 'No amenities needed.'", "prompt_for_task_generation": "Message host where message not equals 'No amenities needed.'"},
        {"prompt": "Message host where message equals 'Does the kitchen have a microwave?'", "prompt_for_task_generation": "Message host where message equals 'Does the kitchen have a microwave?'"},
        {"prompt": "Message host Alex where message not contains 'no blanket'", "prompt_for_task_generation": "Message host Alex where message not contains 'no blanket'"},
        {
            "prompt": "Message host Sarah where message equals 'We loved the place. Thank you!'",
            "prompt_for_task_generation": "Message host Sarah where message equals 'We loved the place. Thank you!'",
        },
    ],
)

###############################################################################
# BACK_TO_ALL_HOTELS_USE_CASE
###############################################################################


BACK_TO_ALL_HOTELS_INFO = """
CRITICAL REQUIREMENTS:
1. Start with explicit navigation phrases like:
   - "Go back to all hotels..."
   - "Return to the hotel dashboard..."
2. Clearly express intent to leave current view and return to main listing
"""

BACK_TO_ALL_HOTELS_USE_CASE = UseCase(
    name="BACK_TO_ALL_HOTELS",
    description="Triggered when the user goes back to the main hotels dashboard.",
    event=BackToAllHotelsEvent,
    event_source_code=BackToAllHotelsEvent.get_source_code_of_class(),
    constraints_generator=generate_reserve_hotel_constraints,
    additional_prompt_info=BACK_TO_ALL_HOTELS_INFO,
    examples=[
        {
            "prompt": "Take me back to the hotel dashboard.",
            "prompt_for_task_generation": "Return to the main hotels dashboard.",
        },
        {
            "prompt": "Go back to all hotels.",
            "prompt_for_task_generation": "Navigate to the dashboard showing all hotels.",
        },
        {
            "prompt": "I want to see the full hotel list again.",
            "prompt_for_task_generation": "Return to the hotels dashboard.",
        },
        {
            "prompt": "Back to the main hotel screen.",
            "prompt_for_task_generation": "Go back to the hotel dashboard page.",
        },
        {
            "prompt": "Exit this and show me the dashboard.",
            "prompt_for_task_generation": "Leave this view and go to the main hotels dashboard.",
        },
        {
            "prompt": "Reset and show all hotel options.",
            "prompt_for_task_generation": "Return to full dashboard with all hotels visible.",
        },
        {
            "prompt": "Go to the homepage for hotels.",
            "prompt_for_task_generation": "Return to hotels dashboard.",
        },
        {
            "prompt": "Show me the dashboard with all listings.",
            "prompt_for_task_generation": "Display the main hotels dashboard.",
        },
    ],
)

ALL_USE_CASES = [
    # SEARCH_HOTEL_USE_CASE,
    # VIEW_HOTEL_USE_CASE,
    # INCREASE_NUMBER_OF_GUESTS_USE_CASE,
    # RESERVE_HOTEL_USE_CASE,
    # EDIT_CHECK_IN_OUT_DATES_USE_CASE,
    CONFIRM_AND_PAY_USE_CASE,
    # MESSAGE_HOST_USE_CASE,
    # SHARE_HOTEL_USE_CASE,
    # ADD_TO_WISHLIST_USE_CASE,
    # BACK_TO_ALL_HOTELS_USE_CASE,
]
