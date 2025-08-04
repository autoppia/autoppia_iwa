from autoppia_iwa.src.demo_webs.classes import UseCase
from autoppia_iwa.src.demo_webs.projects.autodelivery_7.events import (
    AddressAddedEvent,
    AddToCartEvent,
    AddToCartModalOpenEvent,
    BackToAllRestaurantsEvent,
    DeleteReviewEvent,
    # DeliveryModeEvent,
    DropoffPreferenceEvent,
    EmptyCartEvent,
    ItemIncrementedEvent,
    OpenCheckoutPageEvent,
    # PickupModeEvent,
    PlaceOrderEvent,
    SearchRestaurantEvent,
    ViewRestaurantEvent,
)

from .generation_functions import (
    generate_add_to_cart_constraints,
    generate_add_to_cart_modal_open_constraints,
    generate_address_added_constraints,
    generate_dropoff_option_constraints,
    generate_increment_item_restaurant_constraints,
    generate_place_order_constraints,
    generate_search_restaurant_constraints,
    generate_view_restaurant_constraints,
)

SEARCH_RESTAURANT_USE_CASE = UseCase(
    name="SEARCH_RESTAURANT",
    description="The user searches for restaurants using a query string.",
    event=SearchRestaurantEvent,
    event_source_code=SearchRestaurantEvent.get_source_code_of_class(),
    constraints_generator=generate_search_restaurant_constraints,
    examples=[
        {"prompt": "Search for restaurants serving Italian cuisine.", "prompt_for_task_generation": "Search for restaurants serving Italian cuisine."},
        {"prompt": "Find restaurants with 'Sushi' in their name.", "prompt_for_task_generation": "Find restaurants with 'Sushi' in their name."},
        {"prompt": "Look for pizza places nearby.", "prompt_for_task_generation": "Look for pizza places nearby."},
        {"prompt": "Show me restaurants rated above 4.5.", "prompt_for_task_generation": "Show me restaurants rated above 4.5."},
        {"prompt": "Find any restaurant that offers delivery in under 45 minutes.", "prompt_for_task_generation": "Find any restaurant that offers delivery in under 45 minutes."},
    ],
)

VIEW_RESTAURANT_ADDITIONAL_PROMPT_INFO = """
"Critical requirement:
1. The request must start with one of the following: "
    "View the details...", "Show me the details...", "Open the restaurant page for...",
    "View the restaurant that has...", or "Show details for the featured restaurant.""".strip()

VIEW_RESTAURANT_USE_CASE = UseCase(
    name="VIEW_RESTAURANT",
    description="The user views the details of a restaurant.",
    event=ViewRestaurantEvent,
    event_source_code=ViewRestaurantEvent.get_source_code_of_class(),
    constraints_generator=generate_view_restaurant_constraints,
    additional_prompt_info=VIEW_RESTAURANT_ADDITIONAL_PROMPT_INFO,
    examples=[
        {"prompt": "View details for 'Pizza Palace'.", "prompt_for_task_generation": "View details for 'Pizza Palace'."},
        {"prompt": "Show me the menu of the restaurant with cuisine 'Japanese'.", "prompt_for_task_generation": "Show me the menu of the restaurant with cuisine 'Japanese'."},
        {"prompt": "Open the restaurant page for the one rated 4.7.", "prompt_for_task_generation": "Open the restaurant page for the one rated 4.7."},
        {
            "prompt": "View the restaurant that has 'Best wood-fired pizzas' in its description.",
            "prompt_for_task_generation": "View the restaurant that has 'Best wood-fired pizzas' in its description.",
        },
        {"prompt": "Show details for the featured restaurant.", "prompt_for_task_generation": "Show details for the featured restaurant."},
    ],
)

ADD_TO_CART_MODAL_OPEN_USE_CASE = UseCase(
    name="ADD_TO_CART_MODAL_OPEN",
    description="The user opens the add-to-cart modal for a menu item.",
    event=AddToCartModalOpenEvent,
    event_source_code=AddToCartModalOpenEvent.get_source_code_of_class(),
    constraints_generator=generate_add_to_cart_modal_open_constraints,
    examples=[
        {"prompt": "Open the add-to-cart modal for 'Margherita Pizza' at 'Pizza Palace'.", "prompt_for_task_generation": "Open the add-to-cart modal for 'Margherita Pizza' at 'Pizza Palace'."},
        {"prompt": "Show the add-to-cart modal for 'Salmon Nigiri'.", "prompt_for_task_generation": "Show the add-to-cart modal for 'Salmon Nigiri'."},
        {"prompt": "Open the modal to add 'Pepperoni Pizza' (Medium) to cart.", "prompt_for_task_generation": "Open the modal to add 'Pepperoni Pizza' (Medium) to cart."},
        {"prompt": "Open the add-to-cart modal for an item priced at $12.99.", "prompt_for_task_generation": "Open the add-to-cart modal for an item priced at $12.99."},
        {"prompt": "Show the add-to-cart modal for 'California Roll' at any restaurant.", "prompt_for_task_generation": "Show the add-to-cart modal for 'California Roll' at any restaurant."},
    ],
)

ITEM_INCREMENTED_USE_CASE = UseCase(
    name="ITEM_INCREMENTED",
    description="The user increases the quantity of a menu item in the cart.",
    event=ItemIncrementedEvent,
    event_source_code=ItemIncrementedEvent.get_source_code_of_class(),
    constraints_generator=generate_increment_item_restaurant_constraints,
    examples=[
        {"prompt": "Increase the quantity of 'Margherita Pizza' to 2.", "prompt_for_task_generation": "Increase the quantity of 'Margherita Pizza' to 2."},
        {"prompt": "Add one more 'Salmon Nigiri' to my cart.", "prompt_for_task_generation": "Add one more 'Salmon Nigiri' to my cart."},
        {"prompt": "Increment 'Pepperoni Pizza' count in the cart.", "prompt_for_task_generation": "Increment 'Pepperoni Pizza' count in the cart."},
        {"prompt": "Set the quantity of 'California Roll' to 3.", "prompt_for_task_generation": "Set the quantity of 'California Roll' to 3."},
        {"prompt": "Increase the number of 'Margherita Pizza' in my order.", "prompt_for_task_generation": "Increase the number of 'Margherita Pizza' in my order."},
    ],
)

# ITEM_DECREMENTED_USE_CASE = UseCase(
#     name="ITEM_DECREMENTED",
#     description="The user decreases the quantity of a menu item in the cart.",
#     event=ItemDecrementedEvent,
#     event_source_code=ItemDecrementedEvent.get_source_code_of_class(),
#     constraints_generator=None,
#     examples=[
#         {"prompt": "Decrease the quantity of 'Pepperoni Pizza' to 1.", "prompt_for_task_generation": "Decrease the quantity of 'Pepperoni Pizza' to 1."},
#         {"prompt": "Remove one 'Salmon Nigiri' from my cart.", "prompt_for_task_generation": "Remove one 'Salmon Nigiri' from my cart."},
#         {"prompt": "Decrement 'California Roll' count in the cart.", "prompt_for_task_generation": "Decrement 'California Roll' count in the cart."},
#         {"prompt": "Set the quantity of 'Margherita Pizza' to 0.", "prompt_for_task_generation": "Set the quantity of 'Margherita Pizza' to 0."},
#         {"prompt": "Reduce the number of 'Pepperoni Pizza' in my order.", "prompt_for_task_generation": "Reduce the number of 'Pepperoni Pizza' in my order."},
#     ],
# )

ADD_TO_CART_USE_CASE = UseCase(
    name="ADD_TO_CART",
    description="The user adds a menu item to the cart.",
    event=AddToCartEvent,
    event_source_code=AddToCartEvent.get_source_code_of_class(),
    constraints_generator=generate_add_to_cart_constraints,
    examples=[
        {"prompt": "Add 'Margherita Pizza' (Large) to my cart.", "prompt_for_task_generation": "Add 'Margherita Pizza' (Large) to my cart."},
        {"prompt": "Add 'Salmon Nigiri' with no modifications.", "prompt_for_task_generation": "Add 'Salmon Nigiri' with no modifications."},
        {"prompt": "Add two 'Pepperoni Pizza' (Medium) with 'No Sauce' option.", "prompt_for_task_generation": "Add two 'Pepperoni Pizza' (Medium) with 'No Sauce' option."},
        {"prompt": "Add 'California Roll' and set quantity to 3.", "prompt_for_task_generation": "Add 'California Roll' and set quantity to 3."},
        {"prompt": "Add 'Margherita Pizza' (Small) with 'No Cheese' and 'No Basil'.", "prompt_for_task_generation": "Add 'Margherita Pizza' (Small) with 'No Cheese' and 'No Basil'."},
    ],
)

OPEN_CHECKOUT_PAGE_USE_CASE = UseCase(
    name="OPEN_CHECKOUT_PAGE",
    description="The user opens the checkout page to review their order.",
    event=OpenCheckoutPageEvent,
    event_source_code=OpenCheckoutPageEvent.get_source_code_of_class(),
    constraints_generator=generate_add_to_cart_constraints,
    examples=[
        {"prompt": "Go to the checkout page with 3 items in the cart.", "prompt_for_task_generation": "Go to the checkout page with 3 items in the cart."},
        {"prompt": "Open checkout to review 'Margherita Pizza' and 'California Roll'.", "prompt_for_task_generation": "Open checkout to review 'Margherita Pizza' and 'California Roll'."},
        {"prompt": "Proceed to checkout with all current items.", "prompt_for_task_generation": "Proceed to checkout with all current items."},
        {"prompt": "Open the checkout page after adding 'Pepperoni Pizza'.", "prompt_for_task_generation": "Open the checkout page after adding 'Pepperoni Pizza'."},
        {"prompt": "Go to checkout with a total of 2 items.", "prompt_for_task_generation": "Go to checkout with a total of 2 items."},
    ],
)

DROPOFF_PREFERENCE_USE_CASE = UseCase(
    name="DROPOFF_PREFERENCE",
    description="The user sets a dropoff preference for delivery.",
    event=DropoffPreferenceEvent,
    event_source_code=DropoffPreferenceEvent.get_source_code_of_class(),
    constraints_generator=generate_dropoff_option_constraints,
    examples=[
        {"prompt": "Set dropoff preference to 'Leave at door'.", "prompt_for_task_generation": "Set dropoff preference to 'Leave at door'."},
        {"prompt": "Choose 'Hand to me' as the dropoff option.", "prompt_for_task_generation": "Choose 'Hand to me' as the dropoff option."},
        {"prompt": "Select 'Ring bell' for delivery dropoff.", "prompt_for_task_generation": "Select 'Ring bell' for delivery dropoff."},
        {"prompt": "Set my delivery dropoff to 'Call on arrival'.", "prompt_for_task_generation": "Set my delivery dropoff to 'Call on arrival'."},
        {"prompt": "Change dropoff preference to 'Front desk'.", "prompt_for_task_generation": "Change dropoff preference to 'Front desk'."},
    ],
)

PLACE_ORDER_USE_CASE = UseCase(
    name="PLACE_ORDER",
    description="The user places an order with delivery or pickup details.",
    event=PlaceOrderEvent,
    event_source_code=PlaceOrderEvent.get_source_code_of_class(),
    constraints_generator=generate_place_order_constraints,
    examples=[
        {"prompt": "Place an order for 'Pizza Palace' to be delivered to 123 Main St.", "prompt_for_task_generation": "Place an order for 'Pizza Palace' to be delivered to 123 Main St."},
        {"prompt": "Order 'Sushi World' for pickup at 5pm.", "prompt_for_task_generation": "Order 'Sushi World' for pickup at 5pm."},
        {"prompt": "Order 'Pepperoni Pizza' and 'California Roll' for delivery.", "prompt_for_task_generation": "Order 'Pepperoni Pizza' and 'California Roll' for delivery."},
        {"prompt": "Place an order with the dropoff preference 'Leave at door'.", "prompt_for_task_generation": "Place an order with the dropoff preference 'Leave at door'."},
        {"prompt": "Order all items in my cart and pay by card.", "prompt_for_task_generation": "Order all items in my cart and pay by card."},
    ],
)

# PICKUP_MODE_USE_CASE = UseCase(
#     name="PICKUP_MODE",
#     description="The user selects pickup as the order mode.",
#     event=PickupModeEvent,
#     event_source_code=PickupModeEvent.get_source_code_of_class(),
#     constraints_generator=generate_pickup_mode_constraints,
#     examples=[
#         {"prompt": "Switch to pickup mode for my order.", "prompt_for_task_generation": "Switch to pickup mode for my order."},
#         {"prompt": "Select pickup instead of delivery.", "prompt_for_task_generation": "Select pickup instead of delivery."},
#         {"prompt": "Change order mode to pickup.", "prompt_for_task_generation": "Change order mode to pickup."},
#         {"prompt": "Choose pickup for 'Pizza Palace'.", "prompt_for_task_generation": "Choose pickup for 'Pizza Palace'."},
#         {"prompt": "Set my order to be picked up at the restaurant.", "prompt_for_task_generation": "Set my order to be picked up at the restaurant."},
#     ],
# )

EMPTY_CART_USE_CASE = UseCase(
    name="EMPTY_CART",
    description="The user empties their cart.",
    event=EmptyCartEvent,
    event_source_code=EmptyCartEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {"prompt": "Empty my cart.", "prompt_for_task_generation": "Empty my cart."},
        {"prompt": "Remove all items from the cart.", "prompt_for_task_generation": "Remove all items from the cart."},
        {"prompt": "Clear my shopping cart.", "prompt_for_task_generation": "Clear my shopping cart."},
        {"prompt": "Delete everything in my cart.", "prompt_for_task_generation": "Delete everything in my cart."},
        {"prompt": "Start a new order by emptying the cart.", "prompt_for_task_generation": "Start a new order by emptying the cart."},
    ],
)

DELETE_REVIEW_USE_CASE = UseCase(
    name="DELETE_REVIEW",
    description="The user deletes a review they wrote for a restaurant.",
    event=DeleteReviewEvent,
    event_source_code=DeleteReviewEvent.get_source_code_of_class(),
    constraints_generator=generate_view_restaurant_constraints,
    examples=[
        {"prompt": "Delete my review for 'Pizza Palace' written on 2025-06-02.", "prompt_for_task_generation": "Delete my review for 'Pizza Palace' written on 2025-06-02."},
        {"prompt": "Remove the review I wrote with a rating of 4.", "prompt_for_task_generation": "Remove the review I wrote with a rating of 4."},
        {"prompt": "Delete my comment on 'Sushi World'.", "prompt_for_task_generation": "Delete my comment on 'Sushi World'."},
        {"prompt": "Remove my review from 2025-05-30.", "prompt_for_task_generation": "Remove my review from 2025-05-30."},
        {"prompt": "Delete the review I wrote as 'Marco R.'.", "prompt_for_task_generation": "Delete the review I wrote as 'Marco R.'."},
    ],
)

BACK_TO_ALL_RESTAURANTS_USE_CASE = UseCase(
    name="BACK_TO_ALL_RESTAURANTS",
    description="The user navigates back to the list of all restaurants.",
    event=BackToAllRestaurantsEvent,
    event_source_code=BackToAllRestaurantsEvent.get_source_code_of_class(),
    constraints_generator=generate_view_restaurant_constraints,
    examples=[
        {"prompt": "Go back to the list of all restaurants from 'Pizza Palace'.", "prompt_for_task_generation": "Go back to the list of all restaurants from 'Pizza Palace'."},
        {"prompt": "Return to all restaurants after viewing 'Sushi World'.", "prompt_for_task_generation": "Return to all restaurants after viewing 'Sushi World'."},
        {"prompt": "Navigate back to all restaurants.", "prompt_for_task_generation": "Navigate back to all restaurants."},
        {"prompt": "Back to the main restaurant list.", "prompt_for_task_generation": "Back to the main restaurant list."},
        {"prompt": "Go to all restaurants from any restaurant page.", "prompt_for_task_generation": "Go to all restaurants from any restaurant page."},
    ],
)

ADDRESS_ADDED_USE_CASE = UseCase(
    name="ADDRESS_ADDED",
    description="The user adds a new delivery or pickup address.",
    event=AddressAddedEvent,
    event_source_code=AddressAddedEvent.get_source_code_of_class(),
    constraints_generator=generate_address_added_constraints,
    examples=[
        {"prompt": "Add a new delivery address: 456 Oak St.", "prompt_for_task_generation": "Add a new delivery address: 456 Oak St."},
        {"prompt": "Set my pickup address to 789 Pine Ave.", "prompt_for_task_generation": "Set my pickup address to 789 Pine Ave."},
        {"prompt": "Add an address for delivery mode.", "prompt_for_task_generation": "Add an address for delivery mode."},
        {"prompt": "Add a new address for pickup.", "prompt_for_task_generation": "Add a new address for pickup."},
        {"prompt": "Save 321 Maple Rd as my delivery address.", "prompt_for_task_generation": "Save 321 Maple Rd as my delivery address."},
    ],
)

# DELIVERY_MODE_USE_CASE = UseCase(
#     name="DELIVERY_MODE",
#     description="The user selects delivery as the order mode.",
#     event=DeliveryModeEvent,
#     event_source_code=DeliveryModeEvent.get_source_code_of_class(),
#     constraints_generator=None,
#     examples=[
#         {"prompt": "Switch to delivery mode for my order.", "prompt_for_task_generation": "Switch to delivery mode for my order."},
#         {"prompt": "Select delivery instead of pickup.", "prompt_for_task_generation": "Select delivery instead of pickup."},
#         {"prompt": "Change order mode to delivery.", "prompt_for_task_generation": "Change order mode to delivery."},
#         {"prompt": "Choose delivery for 'Sushi World'.", "prompt_for_task_generation": "Choose delivery for 'Sushi World'."},
#         {"prompt": "Set my order to be delivered to my address.", "prompt_for_task_generation": "Set my order to be delivered to my address."},
#     ],
# )

ALL_USE_CASES = [
    SEARCH_RESTAURANT_USE_CASE,
    VIEW_RESTAURANT_USE_CASE,
    ADD_TO_CART_MODAL_OPEN_USE_CASE,
    ITEM_INCREMENTED_USE_CASE,
    # ITEM_DECREMENTED_USE_CASE,
    ADD_TO_CART_USE_CASE,
    OPEN_CHECKOUT_PAGE_USE_CASE,
    DROPOFF_PREFERENCE_USE_CASE,
    ADDRESS_ADDED_USE_CASE,
    # DELIVERY_MODE_USE_CASE,
    # PICKUP_MODE_USE_CASE,
    EMPTY_CART_USE_CASE,
    DELETE_REVIEW_USE_CASE,
    BACK_TO_ALL_RESTAURANTS_USE_CASE,
    PLACE_ORDER_USE_CASE,
]
