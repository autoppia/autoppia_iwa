from ...classes import UseCase
from .events import (
    AddToWishlistEvent,
    BackToAllHotelsEvent,
    ConfirmAndPayEvent,
    # DecreaseNumberOfGuestsEvent,
    EditCheckInOutDatesEvent,
    IncreaseNumberOfGuestsEvent,
    MessageHostEvent,
    ReserveHotelEvent,
    # SearchClearedEvent,
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
    # generate_search_cleared_constraints,
    generate_search_hotel_constraints,
    generate_share_hotel_constraints,
    generate_view_hotel_constraints,
)

# from .replace_functions import replace_hotel_placeholders


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
            "prompt": "Search for hotels in Murree from July 25 to July 28 for 2 adults and 1 child",
            "prompt_for_task_generation": "Search for hotels in <location> from <date_from> to <date_to> for <adults> adults and <children> children",
        },
        {
            "prompt": "Find hotels near Lake View for this weekend, 2 adults, no kids",
            "prompt_for_task_generation": "Find hotels near <search_term> for <date_range>, <adults> adults",
        },
        {
            "prompt": "Look up beachside hotels from August 10 to August 12 for a family of 4 with a pet",
            "prompt_for_task_generation": "Look up <search_term> hotels from <date_from> to <date_to> for <adults> adults, <children> children, and <pets> pets",
        },
        {
            "prompt": "Search for hotels in Skardu for next week",
            "prompt_for_task_generation": "Search for hotels in <search_term> for <date_range>",
        },
        {
            "prompt": "Find a hotel near Mall Road for 3 adults and 1 infant",
            "prompt_for_task_generation": "Find a hotel near <search_term> for <adults> adults and <infants> infants",
        },
    ],
)

###############################################################################
# SEARCH_CLEARED_USE_CASE
###############################################################################

# SEARCH_CLEARED_INFO = """
# Trigger this event when the user explicitly clears the search input box or resets a previously entered query.
# This may indicate that they want to restart their search journey or correct a mistake.
# """
#
# SEARCH_CLEARED_USE_CASE = UseCase(
#     name="SEARCH_CLEARED",
#     description="Triggered when the user clears the hotel search input.",
#     event=SearchClearedEvent,
#     event_source_code=SearchClearedEvent.get_source_code_of_class(),
#     constraints_generator=generate_search_cleared_constraints,
#     additional_prompt_info=SEARCH_CLEARED_INFO,
#     examples=[
#         {
#             "prompt": "Clear the search box.",
#             "prompt_for_task_generation": "Clear the search input box.",
#         },
#         {
#             "prompt": "Forget what I just searched for.",
#             "prompt_for_task_generation": "Forget the last search input.",
#         },
#         {
#             "prompt": "Start over. Clear the current hotel search.",
#             "prompt_for_task_generation": "Clear the current hotel search input.",
#         },
#         {
#             "prompt": "Remove all search filters and queries.",
#             "prompt_for_task_generation": "Clear all filters and queries from the hotel search input.",
#         },
#     ],
# )

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
    constraints_generator=generate_view_hotel_constraints,  # reuse existing hotel constraint generator
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

Examples:
Constraint: {'email': {'operator': 'equals', 'value': 'friend@example.com'}}
Prompt: "Share the hotel with friend@example.com."
"""

SHARE_HOTEL_USE_CASE = UseCase(
    name="SHARE_HOTEL",
    description="Triggered when the user shares a hotel listing with someone, typically via email.",
    event=ShareHotelEvent,
    event_source_code=ShareHotelEvent.get_source_code_of_class(),
    constraints_generator=generate_share_hotel_constraints,  # Reuse hotel-based constraints
    additional_prompt_info=SHARE_HOTEL_INFO,
    examples=[
        {
            "prompt": "Share the Murree hotel with a mountain view and hot tub with sara@example.com.",
            "prompt_for_task_generation": "Share hotel in Murree with mountain view and hot tub with sara@example.com.",
        },
        {
            "prompt": "Can you send the Skardu riverside hotel listing to my brother at ali123@gmail.com?",
            "prompt_for_task_generation": "Share hotel in Skardu with river view to ali123@gmail.com.",
        },
        {
            "prompt": "I want to share that 5-star hotel with free breakfast with my travel buddy.",
            "prompt_for_task_generation": "Share 5-star hotel with free breakfast.",
        },
        {
            "prompt": "Send the listing hosted by Ayesha in Islamabad with a rooftop pool to my email.",
            "prompt_for_task_generation": "Share hotel in Islamabad hosted by Ayesha with rooftop pool.",
        },
        {
            "prompt": "Forward the Karachi hotel with private parking and gym to omar@gmail.com.",
            "prompt_for_task_generation": "Share hotel in Karachi with private parking and gym to omar@gmail.com.",
        },
        {
            "prompt": "Let's share that villa in Nathia Gali with jacuzzi and fireplace with my friends.",
            "prompt_for_task_generation": "Share villa in Nathia Gali with jacuzzi and fireplace.",
        },
    ],
)

###############################################################################
# INCREASE_NUMBER_OF_GUESTS_USE_CASE
###############################################################################

INCREASE_NUMBER_OF_GUESTS_INFO = """
CRITICAL REQUIREMENT:
1. Mention increment of guests only in prompt.
2. Do NOT any details other than number of guests.
3. Start prompt with "Increase number of guests to X" or similar phrases.
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
            "prompt": "Increase number of guests to 3.",
            "prompt_for_task_generation": "Increase number of guests to 3.",
        },
        {
            "prompt": "Increase guest count to 4.",
            "prompt_for_task_generation": "Increase guest count to 4.",
        },
        {
            "prompt": "Make that 5 guests total.",
            "prompt_for_task_generation": "Increase number of guests to 5.",
        },
        {
            "prompt": "Need to include my cousin too, so now it's 6 people.",
            "prompt_for_task_generation": "Need to include my cousin too, so now it's 6 people.",
        },
        {
            "prompt": "Btw, we're adding 2 more friends. Increase guests by 2. ",
            "prompt_for_task_generation": "Btw, we're adding 2 more friends. Increase guests by 2. ",
        },
        {
            "prompt": "Oh I forgot about the kids - we're 2 adults and 2 children.",
            "prompt_for_task_generation": "Increase number of guests to 4.",
        },
    ],
)

###############################################################################
# DECREASE_NUMBER_OF_GUESTS_USE_CASE
###############################################################################

# DECREASE_NUMBER_OF_GUESTS_INFO = """
# Trigger this event when a user decreases the number of guests for a hotel booking or search.
# This can be directly stated (e.g., 'make it 2 guests instead of 3') or implied (e.g., 'just me now').
# """
#
# DECREASE_NUMBER_OF_GUESTS_USE_CASE = UseCase(
#     name="DECREASE_NUMBER_OF_GUESTS",
#     description="Triggered when the user reduces the number of guests for a reservation or search.",
#     event=DecreaseNumberOfGuestsEvent,
#     event_source_code=DecreaseNumberOfGuestsEvent.get_source_code_of_class(),
#     additional_prompt_info=DECREASE_NUMBER_OF_GUESTS_INFO,
#     examples=[
#         {
#             "prompt": "Actually, it's just me now.",
#             "prompt_for_task_generation": "Decrease guests to 1.",
#         },
#         {
#             "prompt": "Make that 2 guests instead of 4.",
#             "prompt_for_task_generation": "Decrease guests from 4 to 2.",
#         },
#         {
#             "prompt": "Cancel the extra guest, only 3 of us are coming.",
#             "prompt_for_task_generation": "Decrease guest count to 3.",
#         },
#         {
#             "prompt": "My brother isn't coming anymore - we're now 2.",
#             "prompt_for_task_generation": "Decrease guests from 3 to 2.",
#         },
#         {
#             "prompt": "No kids this time, just the two of us.",
#             "prompt_for_task_generation": "Decrease guests to 2.",
#         },
#         {
#             "prompt": "Let's book it for 1 person only now.",
#             "prompt_for_task_generation": "Decrease guests to 1.",
#         },
#         {
#             "prompt": "Change it from 5 guests to 3.",
#             "prompt_for_task_generation": "Decrease guests from 5 to 3.",
#         },
#     ],
# )

###############################################################################
# RESERVE_HOTEL_USE_CASE
###############################################################################

RESERVE_HOTEL_INFO = """
Important:
1. Begin your request by phrases like: 'Reserve the hotel...', 'Book the hotel for...', or similar.
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
1. The prompt should clearly confirm the updated check-in and/or check-out dates.
2. Use explicit phrases such as 'Change check-in to...', 'Update check-out date...', or similar.
3. Do not include unrelated booking or payment actions in this prompt.
4. 'checkin' and 'checkout' dates are actual values that needs to be updated, 'datesFrom' and 'datesTo' are actual available dates to find the hotel.
Please mention the 'checkin' and 'checkout' dates in the prompt for update only.

{}

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
            "prompt": "Change our check-in to August 10 and check-out to August 14.",
            "prompt_for_task_generation": "Update check-in and check-out dates.",
        },
        {
            "prompt": "Actually, we'll arrive a day earlier.",
            "prompt_for_task_generation": "Change check-in date to a day earlier.",
        },
        {
            "prompt": "Move our departure to Sunday.",
            "prompt_for_task_generation": "Change check-out date to Sunday.",
        },
        {
            "prompt": "Shift the whole trip to next weekend.",
            "prompt_for_task_generation": "Edit both check-in and check-out dates to next weekend.",
        },
        {
            "prompt": "Make it a two-day trip starting on the 5th.",
            "prompt_for_task_generation": "Set check-in to the 5th and check-out two days later.",
        },
        {
            "prompt": "Change only the check-out - we'll stay one extra night.",
            "prompt_for_task_generation": "Extend check-out by one day.",
        },
        {
            "prompt": "Push the trip forward by a week.",
            "prompt_for_task_generation": "Move check-in and check-out one week later.",
        },
    ],
)

###############################################################################
# CONFIRM_AND_PAY_USE_CASE
###############################################################################

CONFIRM_AND_PAY_INFO = """
CRITICAL REQUIREMENT:
1. Start the prompt with details confirmation
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
1. Use explicit phrases such as 'Message the host ...', 'Send the query to host ...', or similar.
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
            "prompt": "Can you ask Natalie if early check-in is possible?",
            "prompt_for_task_generation": "Send message to host Natalie asking about early check-in.",
        },
        {
            "prompt": "Tell the host I'll be arriving around 10pm.",
            "prompt_for_task_generation": "Send message to the host informing them of a 10pm arrival.",
        },
        {
            "prompt": "Let John know we might bring a pet.",
            "prompt_for_task_generation": "Send message to host John asking if pets are allowed.",
        },
        {
            "prompt": "Message the host: do they provide towels and soap?",
            "prompt_for_task_generation": "Send question to the host about amenities like towels and soap.",
        },
        {
            "prompt": "Write to the host and ask if the kitchen has a microwave.",
            "prompt_for_task_generation": "Ask host via message whether kitchen includes a microwave.",
        },
        {
            "prompt": "Please tell Alex we'll need an extra blanket.",
            "prompt_for_task_generation": "Send message to host Alex requesting an extra blanket.",
        },
        {
            "prompt": "Send this to Sarah: 'We loved the place. Thank you!'",
            "prompt_for_task_generation": "Send thank you message to host Sarah.",
        },
        {
            "prompt": "Ask the host if the pool is heated in winter.",
            "prompt_for_task_generation": "Send question to host about winter pool heating.",
        },
        {
            "prompt": "Message host: Is parking included or extra?",
            "prompt_for_task_generation": "Send message to the host asking about parking costs.",
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
    RESERVE_HOTEL_USE_CASE,
    # EDIT_CHECK_IN_OUT_DATES_USE_CASE,
    # CONFIRM_AND_PAY_USE_CASE,
    # MESSAGE_HOST_USE_CASE,
    # SHARE_HOTEL_USE_CASE,
    # ADD_TO_WISHLIST_USE_CASE,
    # BACK_TO_ALL_HOTELS_USE_CASE,
]
