from autoppia_iwa.src.demo_webs.classes import UseCase
from autoppia_iwa.src.demo_webs.projects.autodelivery_7.events import (
    AddressAddedEvent,
    AddToCartEvent,
    AddToCartModalOpenEvent,
    BackToAllRestaurantsEvent,
    DeleteReviewEvent,
    DeliveryPrioritySelectedEvent,
    DropoffPreferenceEvent,
    EditCartItemEvent,
    EmptyCartEvent,
    ItemIncrementedEvent,
    OpenCheckoutPageEvent,
    PlaceOrderEvent,
    QuickOrderStartedEvent,
    QuickReorderEvent,
    RestaurantFilterEvent,
    RestaurantNextPageEvent,
    RestaurantPrevPageEvent,
    ReviewSubmittedEvent,
    SearchRestaurantEvent,
    ViewAllRestaurantsEvent,
    ViewRestaurantEvent,
)

from .generation_functions import (
    generate_add_to_cart_constraints,
    generate_add_to_cart_modal_open_constraints,
    generate_address_added_constraints,
    generate_delete_review_constraints,
    generate_delivery_priority_constraints,
    generate_dropoff_option_constraints,
    generate_edit_cart_item_constraints,
    generate_increment_item_restaurant_constraints,
    generate_place_order_constraints,
    generate_quick_reorder_constraints,
    generate_restaurant_filter_constraints,
    generate_review_submitted_constraints,
    generate_search_restaurant_constraints,
    generate_view_restaurant_constraints,
)

SEARCH_RESTAURANT_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with one of the following: "Search for restaurants...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()
SEARCH_RESTAURANT_USE_CASE = UseCase(
    name="SEARCH_DELIVERY_RESTAURANT",
    description="The user searches for restaurants using a query string.",
    event=SearchRestaurantEvent,
    event_source_code=SearchRestaurantEvent.get_source_code_of_class(),
    constraints_generator=generate_search_restaurant_constraints,
    additional_prompt_info=SEARCH_RESTAURANT_ADDITIONAL_PROMPT_INFO,
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
    name="VIEW_DELIVERY_RESTAURANT",
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

RESTAURANT_FILTER_USE_CASE = UseCase(
    name="RESTAURANT_FILTER",
    description="The user filters restaurants by search, cuisine, or rating.",
    event=RestaurantFilterEvent,
    event_source_code=RestaurantFilterEvent.get_source_code_of_class(),
    constraints_generator=generate_restaurant_filter_constraints,
    examples=[
        {"prompt": "Filter restaurants to show only Italian cuisine with rating above 4.", "prompt_for_task_generation": "Filter restaurants to show only Italian cuisine with rating above 4."},
        {"prompt": "Show restaurants matching search 'pizza' and rating at least 4.5.", "prompt_for_task_generation": "Show restaurants matching search 'pizza' and rating at least 4.5."},
    ],
)

VIEW_ALL_RESTAURANTS_USE_CASE = UseCase(
    name="VIEW_ALL_RESTAURANTS",
    description="The user opens the full list of restaurants from any detail view.",
    event=ViewAllRestaurantsEvent,
    event_source_code=ViewAllRestaurantsEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {"prompt": "Show all restaurants.", "prompt_for_task_generation": "Show all restaurants."},
        {"prompt": "Return to the full restaurant list.", "prompt_for_task_generation": "Return to the full restaurant list."},
        {"prompt": "Open the main restaurants page.", "prompt_for_task_generation": "Open the main restaurants page."},
    ],
)
ADD_TO_CART_MODAL_OPEN_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with one of the following: "Open the add-to-cart modal ..."
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
4. Pay attention to the constraints:
Example:
constraints: {'item': {'operator': 'equals', 'value': 'Margherita Pizza'}, 'restaurant': {'operator': 'equals', 'value': 'Pizza Palace'}, 'price': {'operator': 'equals', 'value': '10.99'}}'}}
Correct:
"Open the add-to-cart modal where item equals 'Margherita Pizza' and restaurant equals 'Pizza Palace' and price equals '10.99'."
Incorrect:
"Open the add-to-cart modal for 'Margherita Pizza' at 'Pizza Palace' with extra cheese."
""".strip()


ADD_TO_CART_MODAL_OPEN_USE_CASE = UseCase(
    name="ADD_TO_CART_MODAL_OPEN",
    description="The user opens the add-to-cart modal for a menu item.",
    event=AddToCartModalOpenEvent,
    event_source_code=AddToCartModalOpenEvent.get_source_code_of_class(),
    constraints_generator=generate_add_to_cart_modal_open_constraints,
    additional_prompt_info=ADD_TO_CART_MODAL_OPEN_ADDITIONAL_PROMPT_INFO,
    examples=[
        {"prompt": "Open the add-to-cart modal for 'Margherita Pizza' at 'Pizza Palace'.", "prompt_for_task_generation": "Open the add-to-cart modal for 'Margherita Pizza' at 'Pizza Palace'."},
        {"prompt": "Show the add-to-cart modal for 'Salmon Nigiri'.", "prompt_for_task_generation": "Show the add-to-cart modal for 'Salmon Nigiri'."},
        {"prompt": "Open the modal to add 'Pepperoni Pizza' (Medium) to cart.", "prompt_for_task_generation": "Open the modal to add 'Pepperoni Pizza' (Medium) to cart."},
        {"prompt": "Open the add-to-cart modal for an item priced at $12.99.", "prompt_for_task_generation": "Open the add-to-cart modal for an item priced at $12.99."},
        {"prompt": "Show the add-to-cart modal for 'California Roll' at any restaurant.", "prompt_for_task_generation": "Show the add-to-cart modal for 'California Roll' at any restaurant."},
    ],
)

ITEM_INCREMENTED_EVENT_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with one of the following: "Increase the quantity of...", "Add one more...", "Increment...", "Set the quantity of...", or "Increase the number of...".
2. Do not mention a single constraint more than once in the request.

Correct examples:
- Increase the quantity of 'Margherita Pizza' to 2 at a restaurant that equals 'Waffle Works'.
- Add one more 'Salmon Nigiri' to my cart if the price is less than 8.53.
- Set the quantity of 'California Roll' to 3 where the item is not equal to 'Classic Cheeseburger'.

Incorrect examples:
- Increase the quantity of 'Margherita Pizza' to 2 at a restaurant that equals 'Waffle Works' where the quantity is less than 8, the item is not equal to 'Classic Cheeseburger', and the price is less than 8.53. (Multiple constraints mentioned more than once)
- Increase the quantity of 'Margherita Pizza' to 2. Add one more 'Margherita Pizza' to my cart. (Repeated intent)

3. Pay attention to the constraints:
example:
constraints: {'quantity': {'operator': 'less_than', 'value': 8}, 'item': {'operator': 'not_equals', 'value': 'Beef Pho'}, 'restaurant': {'operator': 'contains', 'value': ' P'}}
correct:
"Increase the quantity to less than 2 at a restaurant that contains 'P' where the item is not 'Beef Pho'."
incorrect:
"Increase the quantity of 'Beef Pho' to 2 at a restaurant that contains 'P' where the quantity is less than 8."
"""
ITEM_INCREMENTED_USE_CASE = UseCase(
    name="ITEM_INCREMENTED",
    description="The user increases the quantity of a menu item in the cart.",
    event=ItemIncrementedEvent,
    event_source_code=ItemIncrementedEvent.get_source_code_of_class(),
    constraints_generator=generate_increment_item_restaurant_constraints,
    additional_prompt_info=ITEM_INCREMENTED_EVENT_ADDITIONAL_PROMPT_INFO,
    examples=[
        {"prompt": "Increase the quantity of 'Margherita Pizza' to 2.", "prompt_for_task_generation": "Increase the quantity of 'Margherita Pizza' to 2."},
        {"prompt": "Add one more 'Salmon Nigiri' to my cart.", "prompt_for_task_generation": "Add one more 'Salmon Nigiri' to my cart."},
        {"prompt": "Increment 'Pepperoni Pizza' count in the cart.", "prompt_for_task_generation": "Increment 'Pepperoni Pizza' count in the cart."},
        {"prompt": "Set the quantity of 'California Roll' to 3.", "prompt_for_task_generation": "Set the quantity of 'California Roll' to 3."},
        {"prompt": "Increase the number of 'Margherita Pizza' in my order.", "prompt_for_task_generation": "Increase the number of 'Margherita Pizza' in my order."},
    ],
)

ADD_TO_CART_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with one of the following: "Add ..."
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
4. Pay attention to the constraints:
Example:
constraints: {
'item': {'operator': 'equals', 'value': 'Margherita Pizza'},
'size': {'operator': 'equals', 'value': 'Large'},
'quantity': {'operator': 'equals', 'value': '1'},
'price': {'operator': 'equals', 'value': '10.99'},
'restaurant': {'operator': 'equals', 'value': 'Pizza Palace'},
'preferences': {'operator': 'equals', 'value': 'spicy'},
'total_price': {'operator': 'equals', 'value': '10.99'}
}
Correct:
"Add when item equals 'Margherita Pizza' and size equals 'Large' and quantity equals '1' and price equals '10.99' and restaurant equals 'Pizza Palace' and preferences equals 'spicy' and total_price equals '10.99' to my cart."
Incorrect:
"Add 'Margherita Pizza' (Large) to my cart with extra olives."
""".strip()

ADD_TO_CART_USE_CASE = UseCase(
    name="ADD_TO_CART_MENU_ITEM",
    description="The user adds a menu item to the cart.",
    event=AddToCartEvent,
    event_source_code=AddToCartEvent.get_source_code_of_class(),
    constraints_generator=generate_add_to_cart_constraints,
    additional_prompt_info=ADD_TO_CART_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Add when item equals 'Margherita Pizza' and size equals 'Large' to my cart.",
            "prompt_for_task_generation": "Add when item equals 'Margherita Pizza' and size equals 'Large' to my cart.",
        },
        {"prompt": "Add when item equals 'Salmon Nigiri'.", "prompt_for_task_generation": "Add when item equals 'Salmon Nigiri'."},
        {
            "prompt": "Add when item equals 'Pepperoni Pizza' and size equals 'medium' and preferences equals 'No Sauce' and quantity equals '2'.",
            "prompt_for_task_generation": "Add when item equals 'Pepperoni Pizza' and size equals 'medium' and preferences equals 'No Sauce' and quantity equals '2'.",
        },
        {"prompt": "Add when item equals 'California Roll' and quantity equals '3'.", "prompt_for_task_generation": "Add when item equals 'California Roll' and quantity equals '3'."},
        {
            "prompt": "Add when item equals 'Margherita Pizza' and size equals 'small' and preferences in-list ['No Cheese','No Basil'].",
            "prompt_for_task_generation": "Add when item equals 'Margherita Pizza' and size equals 'small' and preferences in-list ['No Cheese','No Basil'].",
        },
    ],
)

EDIT_CART_ITEM_USE_CASE = UseCase(
    name="EDIT_CART_ITEM",
    description="The user edits an existing cart item (size, preferences, or quantity).",
    event=EditCartItemEvent,
    event_source_code=EditCartItemEvent.get_source_code_of_class(),
    constraints_generator=generate_edit_cart_item_constraints,
    examples=[
        {"prompt": "Edit the cart item 'Margherita Pizza' from Sushi Zen.", "prompt_for_task_generation": "Edit the cart item 'Margherita Pizza' from Sushi Zen."},
        {"prompt": "Open edit for the burger I added from Burger Barn.", "prompt_for_task_generation": "Open edit for the burger I added from Burger Barn."},
        {"prompt": "Modify the cart entry for California Roll.", "prompt_for_task_generation": "Modify the cart entry for California Roll."},
    ],
)

QUICK_ORDER_USE_CASE = UseCase(
    name="QUICK_ORDER_STARTED",
    description="The user starts a quick order from the quick order modal.",
    event=QuickOrderStartedEvent,
    event_source_code=QuickOrderStartedEvent.get_source_code_of_class(),
    constraints_generator=None,
    examples=[
        {"prompt": "Start a quick order for pizza.", "prompt_for_task_generation": "Start a quick order for pizza."},
        {"prompt": "Quick order any Japanese restaurant.", "prompt_for_task_generation": "Quick order any Japanese restaurant."},
        {"prompt": "Start a quick order for burgers.", "prompt_for_task_generation": "Start a quick order for burgers."},
        {"prompt": "Quick order from any Chinese restaurant.", "prompt_for_task_generation": "Quick order from any Chinese restaurant."},
        {"prompt": "Start a quick order for desserts.", "prompt_for_task_generation": "Start a quick order for desserts."},
    ],
)

QUICK_REORDER_USE_CASE = UseCase(
    name="QUICK_REORDER",
    description="The user reorders a recently ordered item.",
    event=QuickReorderEvent,
    event_source_code=QuickReorderEvent.get_source_code_of_class(),
    constraints_generator=generate_quick_reorder_constraints,
    examples=[
        {"prompt": "Reorder the recent item 'California Roll' from Sushi Zen.", "prompt_for_task_generation": "Reorder the recent item 'California Roll' from Sushi Zen."},
        {"prompt": "Quick reorder my last pizza order.", "prompt_for_task_generation": "Quick reorder my last pizza order."},
    ],
)

OPEN_CHECKOUT_PAGE_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with one of the following:"Go to checkout ..."
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
4. Pay attention to the constraints:
Example:
constraints: {
'item': {'operator': 'equals', 'value': 'Margherita Pizza'},
'price': {'operator': 'equals', 'value': '10.99'},
'quantity': {'operator': 'equals', 'value': '3'}
}
Correct:
"Go to the checkout page where item equals 'Margherita Pizza' and price equals '10.99' and quantity equals '3' in the cart."
Incorrect:
"Go to the checkout page with 3 items in the cart and apply discount code."
"""

OPEN_CHECKOUT_PAGE_USE_CASE = UseCase(
    name="OPEN_CHECKOUT_PAGE",
    description="The user opens the checkout page to review their order.",
    event=OpenCheckoutPageEvent,
    event_source_code=OpenCheckoutPageEvent.get_source_code_of_class(),
    constraints_generator=generate_add_to_cart_constraints,
    additional_prompt_info=OPEN_CHECKOUT_PAGE_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Go to the checkout page when item equals 'Margherita Pizza' in the cart.",
            "prompt_for_task_generation": "Go to the checkout page when item equals 'Margherita Pizza' in the cart.",
        },
        {"prompt": "Go to the checkout page when item equals 'California Roll'.", "prompt_for_task_generation": "Go to checkout page when item equals 'California Roll'."},
        {
            "prompt": "Go to the checkout page when item equals 'Chicken Tikka Masala' and price equals '13.99' and quantity equals '3'.",
            "prompt_for_task_generation": "Go to the checkout page when item equals 'Chicken Tikka Masala' and price equals '13.99' and quantity equals '3'.",
        },
        {
            "prompt": "Go to the checkout page when item equals 'Classic Cheeseburger' and price equals '8.99' and quantity equals '2'.",
            "prompt_for_task_generation": "Go to the checkout page when item equals 'Classic Cheeseburger' and price equals '8.99' and quantity equals '2'.",
        },
    ],
)
DROPOFF_PREFERENCE_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with one of the following: "Set dropoff preference ..."
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
4. Pay attention to the constraints:
Example:
constraints: {'delivery_preference': {'operator': 'equals', 'value': 'Leave at door'}, 'restaurant': {'operator': 'equals', 'value': 'Pho 88'}}
Correct:'}}
Correct:
"Set dropoff preference where delivery_preference equals 'Leave at door' and restaurant equals 'Pho 88'."
Incorrect:
"Set dropoff preference to 'Leave at door' and also send a text when arriving."
""".strip()


DROPOFF_PREFERENCE_USE_CASE = UseCase(
    name="DROPOFF_PREFERENCE",
    description="The user sets a dropoff preference for delivery.",
    event=DropoffPreferenceEvent,
    event_source_code=DropoffPreferenceEvent.get_source_code_of_class(),
    constraints_generator=generate_dropoff_option_constraints,
    additional_prompt_info=DROPOFF_PREFERENCE_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Set dropoff preference where delivery_preference equals 'Leave at door'.",
            "prompt_for_task_generation": "Set dropoff preference where delivery_preference equals 'Leave at door'.",
        },
        {"prompt": "Set dropoff preference where delivery_preference contains 'door'.", "prompt_for_task_generation": "Set dropoff preference where delivery_preference contains 'door'."},
        {
            "prompt": "Set dropoff preference where delivery_preference not equals 'Call on arrival'.",
            "prompt_for_task_generation": "Set dropoff preference where delivery_preference not equals 'Call on arrival'.",
        },
        {"prompt": "Set dropoff preference where restaurant equals 'Pho 88'"},
        {"prompt_for_task_generation": "Set dropoff preference where restaurant equals 'Pho 88'"},
        {"prompt": "Set dropoff preference where restaurant equals 'Pho 88' and delivery_preference not equals 'Call on arrival'."},
        {"prompt_for_task_generation": "Set dropoff preference where restaurant equals 'Pho 88' and delivery_preference not equals 'Call on arrival'."},
    ],
)
PLACE_ORDER_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with one of the following: "Place an order ...".
2. Do not repeat any constraint more than once in the request.
3. Do not include any information in the request that is not explicitly listed in the constraints.
4. It is MANDATORY to include every provided constraint in the request. Missing even a single constraint is strictly prohibited.
5. Pay attention to the constraints:
Example:
{
 'restaurant': {'operator': 'equals', 'value': 'Pizza Palace'},
 'mode': {'operator': 'equals', 'value': 'delivery'},
 'item': {'operator': 'equals', 'value': 'Chocolate Lava Cake'},
 'address': {'operator': 'equals', 'value': '505 Cherry Circle, Fairview'},
 'preferences': {'operator': 'not in', 'value': ['high-protein', 'egg-free']},
 'username': {'operator': 'equals', 'value': 'Diana Patel'},
 'phone': {'operator': 'not equal', 'value': '+1-555-456-7890'},
 'quantity': {'operator': 'equals', 'value': '8'},
 'size': {'operator': 'equals', 'value': 'small'},
 'price': {"operator": "greater_than", "value": 3.943880555470603},
}
correct:
"Place an order where restaurant equals 'Pizza Palace' and mode equals 'delivery' and item equals 'Chocolate Lava Cake' and address equals '505 Cherry Circle, Fairview' and preferences not in list '['high-protein', 'egg-free']' and username equals 'Diana Patel' and phone not equal '+1-555-456-7890' and quantity equals '8' and size equals 'small' and price greater_than '3.943880555470603'."
""".strip()

PLACE_ORDER_USE_CASE = UseCase(
    name="PLACE_ORDER",
    description="The user places an order with delivery or pickup details.",
    event=PlaceOrderEvent,
    event_source_code=PlaceOrderEvent.get_source_code_of_class(),
    constraints_generator=generate_place_order_constraints,
    additional_prompt_info=PLACE_ORDER_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Place an order where restaurant equals 'Pizza Palace' and mode equals 'delivery' and item equals 'Chocolate Lava Cake'.",
            "prompt_for_task_generation": "Place an order where restaurant equals 'Pizza Palace' and mode equals 'delivery' and item equals 'Chocolate Lava Cake'.",
        },
        {
            "prompt": "Place an order where restaurant contains 'World' and mode contains 'very' and quantity equals '8'.",
            "prompt_for_task_generation": "Place an order where restaurant contains 'World' and mode contains 'very' and quantity equals '8'.",
        },
        {
            "prompt": "Place an order where item equals 'Chocolate Lava Cake' and mode equals 'pickup' and quantity equals '8'.",
            "prompt_for_task_generation": "Place an order where item equals 'Chocolate Lava Cake' and mode equals 'pickup' and quantity equals '8'.",
        },
        {
            "prompt": "Place an order where address equals '505 Cherry Circle, Fairview' and mode equals 'delivery' and preferences not in list '['high-protein', 'egg-free']'.",
            "prompt_for_task_generation": "Place an order where address equals '505 Cherry Circle, Fairview' and mode equals 'delivery' and preferences not in list '['high-protein', 'egg-free']'.",
        },
        {
            "prompt": "Place an order where username equals 'Diana Patel' and phone not equal '+1-555-456-7890'.",
            "prompt_for_task_generation": "Place an order where username equals 'Diana Patel' and phone not equal '+1-555-456-7890'.",
        },
        {
            "prompt": "Place an order where item equals 'Chocolate Lava Cake' and size equals 'small'.",
            "prompt_for_task_generation": "Place an order where item equals 'Chocolate Lava Cake' and size equals 'small'.",
        },
        {
            "prompt": "Place an order where restaurant equals 'Pizza Palace' and preferences not in list '['high-protein', 'egg-free']'.",
            "prompt_for_task_generation": "Place an order where restaurant equals 'Pizza Palace' and preferences not in list '['high-protein', 'egg-free']'.",
        },
        {
            "prompt": "Place an order where phone not equal '+1-555-456-7890' and mode equals 'delivery'.",
            "prompt_for_task_generation": "Place an order where phone not equal '+1-555-456-7890' and mode equals 'delivery'.",
        },
        {
            "prompt": "Place an order where username equals 'Diana Patel' and size equals 'small'.",
            "prompt_for_task_generation": "Place an order where username equals 'Diana Patel' and size equals 'small'.",
        },
        {
            "prompt": "Place an order where item equals 'Chocolate Lava Cake' and price greater_than '3.943880555470603'.",
            "prompt_for_task_generation": "Place an order where item equals 'Chocolate Lava Cake' and price greater_than '3.943880555470603'.",
        },
    ],
)

EMPTY_CART_EVENT_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with one of the following: "Empty my cart...", "Remove all items from the cart...", "Clear my shopping cart...", "Delete everything in my cart...", or "Start a new order by emptying the cart...".
2. Do not mention a single constraint more than once in the request.
"""
EMPTY_CART_USE_CASE = UseCase(
    name="EMPTY_CART",
    description="The user empties their cart after adding an item in cart.",
    event=EmptyCartEvent,
    event_source_code=EmptyCartEvent.get_source_code_of_class(),
    constraints_generator=generate_increment_item_restaurant_constraints,
    additional_prompt_info=EMPTY_CART_EVENT_ADDITIONAL_PROMPT_INFO,
    examples=[
        {"prompt": "Empty my cart.", "prompt_for_task_generation": "Empty my cart."},
        {"prompt": "Remove all items from the cart.", "prompt_for_task_generation": "Remove all items from the cart."},
        {"prompt": "Clear my shopping cart.", "prompt_for_task_generation": "Clear my shopping cart."},
        {"prompt": "Delete everything in my cart.", "prompt_for_task_generation": "Delete everything in my cart."},
        {"prompt": "Start a new order by emptying the cart.", "prompt_for_task_generation": "Start a new order by emptying the cart."},
    ],
)

DELETE_REVIEW_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with one of the following: 'Delete the review ...'.
2. Do not mention a single constraint more than once in the request.
3. Make sure to mention the constraint name as specified in the constraints.
Example:
constraint: {'cuisine': 'Steakhouse'}
request: "Delete the review for the restaurant with cuisine 'Steakhouse'."
""".strip()

DELETE_REVIEW_USE_CASE = UseCase(
    name="DELETE_REVIEW",
    description="The user deletes a review they wrote for a restaurant.",
    event=DeleteReviewEvent,
    event_source_code=DeleteReviewEvent.get_source_code_of_class(),
    constraints_generator=generate_delete_review_constraints,
    additional_prompt_info=DELETE_REVIEW_ADDITIONAL_PROMPT_INFO,
    examples=[
        {"prompt": "Delete my review for 'Pizza Palace' written on 2025-06-02.", "prompt_for_task_generation": "Delete my review for 'Pizza Palace' written on 2025-06-02."},
        {"prompt": "Remove the review I wrote with a rating of 4.", "prompt_for_task_generation": "Remove the review I wrote with a rating of 4."},
        {"prompt": "Delete my comment on 'Sushi World'.", "prompt_for_task_generation": "Delete my comment on 'Sushi World'."},
        {"prompt": "Remove my review from 2025-05-30.", "prompt_for_task_generation": "Remove my review from 2025-05-30."},
        {"prompt": "Delete the review I wrote as 'Marco R.'.", "prompt_for_task_generation": "Delete the review I wrote as 'Marco R.'."},
    ],
)
BACK_TO_ALL_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with one of the following: "Return to all ..."
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()


BACK_TO_ALL_RESTAURANTS_USE_CASE = UseCase(
    name="BACK_TO_ALL_RESTAURANTS",
    description="The user navigates back to the list of all restaurants.",
    event=BackToAllRestaurantsEvent,
    event_source_code=BackToAllRestaurantsEvent.get_source_code_of_class(),
    constraints_generator=generate_view_restaurant_constraints,
    additional_prompt_info=BACK_TO_ALL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {"prompt": "Go back to the list of all restaurants from 'Pizza Palace'.", "prompt_for_task_generation": "Go back to the list of all restaurants from 'Pizza Palace'."},
        {"prompt": "Return to all restaurants after viewing 'Sushi World'.", "prompt_for_task_generation": "Return to all restaurants after viewing 'Sushi World'."},
        {"prompt": "Navigate back to all restaurants.", "prompt_for_task_generation": "Navigate back to all restaurants."},
        {"prompt": "Back to the main restaurant list.", "prompt_for_task_generation": "Back to the main restaurant list."},
        {"prompt": "Go to all restaurants from any restaurant page.", "prompt_for_task_generation": "Go to all restaurants from any restaurant page."},
    ],
)

ADDRESS_ADDED_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with one of the following: "Add an address ..."
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

ADDRESS_ADDED_USE_CASE = UseCase(
    name="ADDRESS_ADDED",
    description="The user adds a new delivery or pickup address.",
    event=AddressAddedEvent,
    event_source_code=AddressAddedEvent.get_source_code_of_class(),
    constraints_generator=generate_address_added_constraints,
    additional_prompt_info=ADDRESS_ADDED_ADDITIONAL_PROMPT_INFO,
    examples=[
        {"prompt": "Add a new delivery address: 456 Oak St.", "prompt_for_task_generation": "Add a new delivery address: 456 Oak St."},
        {"prompt": "Set my pickup address to 789 Pine Ave.", "prompt_for_task_generation": "Set my pickup address to 789 Pine Ave."},
        {"prompt": "Add an address for delivery mode.", "prompt_for_task_generation": "Add an address for delivery mode."},
        {"prompt": "Add a new address for pickup.", "prompt_for_task_generation": "Add a new address for pickup."},
        {"prompt": "Save 321 Maple Rd as my delivery address.", "prompt_for_task_generation": "Save 321 Maple Rd as my delivery address."},
    ],
)

RESTAURANT_NEXT_PAGE_USE_CASE = UseCase(
    name="RESTAURANT_NEXT_PAGE",
    description="The user paginates to the next set of restaurants.",
    event=RestaurantNextPageEvent,
    event_source_code=RestaurantNextPageEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {"prompt": "Go to the next page of restaurants.", "prompt_for_task_generation": "Go to the next page of restaurants."},
        {"prompt": "View restaurants that are on next page.", "prompt_for_task_generation": "View restaurants that are on next page."},
        {"prompt": "Move forward to view upcoming restaurants.", "prompt_for_task_generation": "Move forward to view upcoming restaurants."},
    ],
)

RESTAURANT_PREV_PAGE_USE_CASE = UseCase(
    name="RESTAURANT_PREV_PAGE",
    description="The user navigates back to the previous set of restaurants.",
    event=RestaurantPrevPageEvent,
    event_source_code=RestaurantPrevPageEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {"prompt": "Go back to the previous page of restaurants.", "prompt_for_task_generation": "Go back to the previous page of restaurants."},
        {"prompt": "View restaurants that are on previous page.", "prompt_for_task_generation": "View restaurants that are on previous page."},
        {"prompt": "Move backward to view earlier restaurants.", "prompt_for_task_generation": "Move backward to view earlier restaurants."},
    ],
)

REVIEW_SUBMITTED_USE_CASE = UseCase(
    name="REVIEW_SUBMITTED",
    description="The user submits a new review for a restaurant.",
    event=ReviewSubmittedEvent,
    event_source_code=ReviewSubmittedEvent.get_source_code_of_class(),
    constraints_generator=generate_review_submitted_constraints,
    examples=[
        {"prompt": "Submit a review where rating equals '5' for 'Sushi World'.", "prompt_for_task_generation": "Submit a review where rating equals '5' for Sushi World."},
        {"prompt": "Leave a review saying the food was amazing.", "prompt_for_task_generation": "Leave a review saying the food was amazing."},
        {"prompt": "Leave a review saying the food was amazing and giving rating '4'.", "prompt_for_task_generation": "Leave a review saying the food was amazing and giving rating '4'."},
    ],
)

DELIVERY_PRIORITY_SELECTED_USE_CASE = UseCase(
    name="DELIVERY_PRIORITY_SELECTED",
    description="The user chooses a delivery priority option.",
    event=DeliveryPrioritySelectedEvent,
    event_source_code=DeliveryPrioritySelectedEvent.get_source_code_of_class(),
    constraints_generator=generate_delivery_priority_constraints,
    examples=[
        {"prompt": "Select priority delivery for my order.", "prompt_for_task_generation": "Select priority delivery for my order."},
        {"prompt": "Choose normal delivery speed.", "prompt_for_task_generation": "Choose normal delivery speed."},
    ],
)


ALL_USE_CASES = [
    SEARCH_RESTAURANT_USE_CASE,
    VIEW_RESTAURANT_USE_CASE,
    RESTAURANT_FILTER_USE_CASE,
    VIEW_ALL_RESTAURANTS_USE_CASE,
    DELETE_REVIEW_USE_CASE,
    BACK_TO_ALL_RESTAURANTS_USE_CASE,
    ADD_TO_CART_MODAL_OPEN_USE_CASE,
    ITEM_INCREMENTED_USE_CASE,
    ADD_TO_CART_USE_CASE,
    EDIT_CART_ITEM_USE_CASE,
    QUICK_ORDER_USE_CASE,
    QUICK_REORDER_USE_CASE,
    OPEN_CHECKOUT_PAGE_USE_CASE,
    DROPOFF_PREFERENCE_USE_CASE,
    ADDRESS_ADDED_USE_CASE,
    EMPTY_CART_USE_CASE,
    PLACE_ORDER_USE_CASE,
    RESTAURANT_NEXT_PAGE_USE_CASE,
    RESTAURANT_PREV_PAGE_USE_CASE,
    REVIEW_SUBMITTED_USE_CASE,
    DELIVERY_PRIORITY_SELECTED_USE_CASE,
]
