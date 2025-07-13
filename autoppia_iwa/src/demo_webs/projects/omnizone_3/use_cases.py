from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    AddToCartEvent,
    CarouselScrollEvent,
    CheckoutStartedEvent,
    ItemDetailEvent,
    OrderCompletedEvent,
    ProceedToCheckoutEvent,
    QuantityChangedEvent,
    SearchProductEvent,
    ViewCartEvent,
)
from .generation_functions import (
    generate_autozone_products_constraints,
    generate_carousel_scroll_constraints,
    generate_cart_operation_constraints,
    generate_checkout_constraints,
    generate_order_completed_constraints,
    generate_quantity_change_constraints,
    generate_search_query_constraints,
)
from .replace_functions import replace_products_placeholders

###############################################################################
# PRODUCT_DETAIL_USE_CASE
###############################################################################

PRODUCT_DETAIL_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above - not just some of them
2. Include ONLY the constraints mentioned above - do not add any other criteria
3. Be phrased as a request to **view details** of a product (use phrases like "Show details for...", "View product page for...", etc.)
4. Only use the product attributes defined in the constraints

For example, if the constraints are "brand equals Apple AND price less_than 1000":
- CORRECT: "Show me details for an Apple product under $1000"
- INCORRECT: "Show me details for a Samsung product" (wrong brand)
- INCORRECT: "Show me details for an Apple laptop" (adding extra condition)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL containing EXACTLY the same constraint criteria.
"""

PRODUCT_DETAIL_USE_CASE = UseCase(
    name="VIEW_DETAIL",
    description="The user explicitly requests to view the details page of a specific product that meets certain criteria.",
    event=ItemDetailEvent,
    event_source_code=ItemDetailEvent.get_source_code_of_class(),
    constraints_generator=generate_autozone_products_constraints,
    replace_func=replace_products_placeholders,
    additional_prompt_info=PRODUCT_DETAIL_INFO,
    examples=[
        {
            "prompt": "Show me details for the Espresso Machine",
            "prompt_for_task_generation": "Show me details for the <product_name>",
        },
        {
            "prompt": "View product page for a 'Kitchen' item with rating above 4.6",
            "prompt_for_task_generation": "View product page for a <product_category> item with rating above <rating>",
        },
        {
            "prompt": "Show me the details for the cheapest Electric Kettle",
            "prompt_for_task_generation": "Show me the details for the <price_sort> <product_category>",
        },
        {
            "prompt": "Display product details for a KitchenAid Stand Mixer between $200 and $300",
            "prompt_for_task_generation": "Display product details for a <brand> <product_name> between <min_price> and <max_price>",
        },
    ],
)

###############################################################################
# SEARCH_PRODUCT_USE_CASE
###############################################################################

SEARCH_PRODUCT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Make it EXPLICIT that this is a SEARCH using clear terms like:
    - "Search for..."
    - "Find products..."
    - "Look up..."
2. Include ONLY the search query
3. DO NOT include any filters or conditions in the search

For example:
- CORRECT: "Search for wireless headphones"
- INCORRECT: "Find wireless headphones under $100" (includes price filter)
- INCORRECT: "Show me wireless headphones" (not explicit search)
"""

SEARCH_PRODUCT_USE_CASE = UseCase(
    name="SEARCH_PRODUCT",
    description="The user searches for products using a search query.",
    event=SearchProductEvent,
    event_source_code=SearchProductEvent.get_source_code_of_class(),
    constraints_generator=generate_search_query_constraints,
    replace_func=replace_products_placeholders,
    additional_prompt_info=SEARCH_PRODUCT_INFO,
    examples=[
        {
            "prompt": "Search for kitchen appliances",
            "prompt_for_task_generation": "Search for <query>",
        },
        {
            "prompt": "Find products matching 'Espresso Machine'",
            "prompt_for_task_generation": "Find products matching '<query>'",
        },
        {
            "prompt": "Search for products that contain 'fPlu'",
            "prompt_for_task_generation": "Look up <query>",
        },
        {
            "prompt": "Look up products which contain 'example'",
            "prompt_for_task_generation": "Look up products which contain <query>",
        },
    ],
)

###############################################################################
# ADD_TO_CART_USE_CASE
###############################################################################

ADD_TO_CART_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Explicitly mention adding to cart
2. Include product details (name/ID at minimum)
3. May include quantity if specified in constraints
4. DO NOT include checkout/purchase actions

For example:
- CORRECT: "Add 2 Air Fryers to cart"
- INCORRECT: "Buy Air Fryers" (implies checkout)
"""

ADD_TO_CART_USE_CASE = UseCase(
    name="ADD_TO_CART",
    description="The user adds items to their shopping cart.",
    event=AddToCartEvent,
    event_source_code=AddToCartEvent.get_source_code_of_class(),
    constraints_generator=generate_cart_operation_constraints,
    replace_func=replace_products_placeholders,
    additional_prompt_info=ADD_TO_CART_INFO,
    examples=[
        {
            "prompt": "Add Air Fryer to my cart",
            "prompt_for_task_generation": "Add <product_name> to my cart",
        },
        {
            "prompt": "Put 2 units of the Stainless Steel Cookware Set in my shopping cart",
            "prompt_for_task_generation": "Put <quantity> units of the <product_name> in my shopping cart",
        },
        {
            "prompt": "Add the Smart Watch to my cart",
            "prompt_for_task_generation": "Add the <product_name> to my cart",
        },
        {
            "prompt": "Add three of item kitchen-4 to my cart",
            "prompt_for_task_generation": "Add <quantity> of item <product_reference> to my cart",
        },
    ],
)

###############################################################################
# VIEW_CART_USE_CASE
###############################################################################

VIEW_CART_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Explicitly mention viewing the cart
2. NOT include any product details
3. NOT include checkout/purchase actions

For example:
- CORRECT: "Show me my shopping cart"
- INCORRECT: "Show me Espresso Machine in my cart" (includes product detail)
"""

VIEW_CART_USE_CASE = UseCase(
    name="VIEW_CART",
    description="The user views the contents of their shopping cart.",
    event=ViewCartEvent,
    event_source_code=ViewCartEvent.get_source_code_of_class(),
    additional_prompt_info=VIEW_CART_INFO,
    constraints_generator=False,
    examples=[
        {
            "prompt": "View my shopping cart",
            "prompt_for_task_generation": "View my shopping cart",
        },
        {
            "prompt": "Show me what's in my cart right now",
            "prompt_for_task_generation": "Show me what's in my cart right now",
        },
        {
            "prompt": "Display my current shopping basket contents",
            "prompt_for_task_generation": "Display my current shopping basket contents",
        },
        {
            "prompt": "What items do I have in my cart?",
            "prompt_for_task_generation": "What items do I have in my cart?",
        },
    ],
)

###############################################################################
# CHECKOUT_USE_CASE
###############################################################################

CHECKOUT_STARTED_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Explicitly mention 'Click on Buy now' to purchase
2. May include cart contents if specified in constraints

For example:
- CORRECT: "Click on Buy now to process checkout with my cart items"
- INCORRECT: "Pay for my order" (too late in flow)
"""
CHECKOUT_STARTED_USE_CASE = UseCase(
    name="CHECKOUT_STARTED",
    description="The user initiates the checkout process by clicking on Buy now.",
    event=CheckoutStartedEvent,
    event_source_code=CheckoutStartedEvent.get_source_code_of_class(),
    constraints_generator=generate_checkout_constraints,
    additional_prompt_info=CHECKOUT_STARTED_INFO,
    examples=[
        {
            "prompt": "Click on Buy now to procees checkout with my cart items",
            "prompt_for_task_generation": "Click on Buy now to procees checkout with my cart items",
        },
        {
            "prompt": "Click Buy now to start the checkout process for these items",
            "prompt_for_task_generation": "Click Buy now to start the checkout process for these items",
        },
        {
            "prompt": "I want to begin checkout for my selected products, click the Buy now button.",
            "prompt_for_task_generation": "I want to begin checkout for my selected products, click the Buy now button.",
        },
        {
            "prompt": "I'm ready to checkout now, click Buy now.",
            "prompt_for_task_generation": "I'm ready to checkout now, click Buy now.",
        },
        {
            "prompt": "Buy now and take me to the checkout page.",
            "prompt_for_task_generation": "Buy now and take me to the checkout page.",
        },
    ],
)
###############################################################################
# ORDER_COMPLETION_USE_CASE
###############################################################################

ORDER_COMPLETION_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Explicitly mention order completion/purchase
2. Include order summary details if specified
3. May include payment/shipping confirmation

For example:
- CORRECT: "Complete my order with credit card payment"
- INCORRECT: "Add to cart" (wrong action)
"""

ORDER_COMPLETION_USE_CASE = UseCase(
    name="ORDER_COMPLETED",
    description="The user completes an order/purchase.",
    event=OrderCompletedEvent,
    event_source_code=OrderCompletedEvent.get_source_code_of_class(),
    constraints_generator=generate_order_completed_constraints,
    additional_prompt_info=ORDER_COMPLETION_INFO,
    examples=[
        {
            "prompt": "Complete Buying 2 units of the Apple Watch",
            "prompt_for_task_generation": "Complete Buying <quantity> units of the <product_name>",
        },
        {
            "prompt": "Complete the purchase with a product called 'Stainless Steel Cookware Set'",
            "prompt_for_task_generation": "Complete the purchase with a product called <product_name>",
        },
        {
            "prompt": "Finalize the order with 3 units of 'Smart Watch'",
            "prompt_for_task_generation": "Finalize the order with <quantity> units of '<product_name>'",
        },
        {
            "prompt": "Order a Fitness Tracker and complete the order.",
            "prompt_for_task_generation": "Order a <product_name> and complete the order.",
        },
    ],
)

###############################################################################
# PROCEED_TO_CHECKOUT_USE_CASE
###############################################################################

PROCEED_TO_CHECKOUT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Explicitly mention proceeding to checkout (use phrases like "Proceed to checkout", "Go to checkout", etc.)
2. Include cart contents if specified in constraints
3. May include total amount or item count if specified
4. DO NOT include payment/shipping details unless explicitly required

For example:
- CORRECT: "Proceed to checkout with my 3 items totaling $150"
- INCORRECT: "Pay for my order" (too late in flow)
- INCORRECT: "Add to cart" (wrong action)
"""

PROCEED_TO_CHECKOUT_USE_CASE = UseCase(
    name="PROCEED_TO_CHECKOUT",
    description="The user proceeds from cart to checkout with selected items.",
    event=ProceedToCheckoutEvent,
    event_source_code=ProceedToCheckoutEvent.get_source_code_of_class(),
    constraints_generator=generate_checkout_constraints,
    additional_prompt_info=PROCEED_TO_CHECKOUT_INFO,
    examples=[
        {
            "prompt": "Proceed to checkout with my current cart items",
            "prompt_for_task_generation": "Proceed to checkout with my current cart items",
        },
        {
            "prompt": "Go to checkout with my 3 items worth $379.97",
            "prompt_for_task_generation": "Go to checkout with my <item_count> items worth <total_amount>",
        },
        {
            "prompt": "Take me to checkout with these selected products",
            "prompt_for_task_generation": "Take me to checkout with <cart_reference>",
        },
        {
            "prompt": "Continue to checkout with the items in my cart",
            "prompt_for_task_generation": "Continue to checkout with the items in my cart",
        },
    ],
)

###############################################################################
# QUANTITY_CHANGE_USE_CASE
###############################################################################

QUANTITY_CHANGE_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Explicitly mention changing quantity (use phrases like "Update quantity", "Change to X", etc.)
2. Include both product identifier and new quantity
3. May include previous quantity if specified in constraints
4. Must be for items already in cart

For example:
- CORRECT: "Change quantity of iPhone case in my cart from 1 to 3"
- INCORRECT: "Add 3 iPhone cases" (new addition, not quantity change)
- INCORRECT: "Remove iPhone case" (removal, not quantity change)
"""

QUANTITY_CHANGE_USE_CASE = UseCase(
    name="QUANTITY_CHANGED",
    description="The user changes the quantity of an item in their shopping cart.",
    event=QuantityChangedEvent,
    event_source_code=QuantityChangedEvent.get_source_code_of_class(),
    constraints_generator=generate_quantity_change_constraints,
    replace_func=replace_products_placeholders,
    additional_prompt_info=QUANTITY_CHANGE_INFO,
    examples=[
        {
            "prompt": "Update quantity of Espresso Machine in my cart from 1 to 2",
            "prompt_for_task_generation": "Update quantity of <product_name> in my cart from <previous_quantity> to <new_quantity>",
        },
        {
            "prompt": "Reduce quantity of Wireless Earbuds in my cart to 1",
            "prompt_for_task_generation": "Reduce quantity of <product_name> in my cart to <new_quantity>",
        },
        {
            "prompt": "Change the quantity of item kitchen-6 to 3",
            "prompt_for_task_generation": "Change the quantity of <product_id> from <previous_quantity> to <new_quantity>",
        },
        {
            "prompt": "Increase quantity of the Electric Kettle by 5",
            "prompt_for_task_generation": "Increase quantity of <product_name> by <new_quantity>",
        },
    ],
)

###############################################################################
# CAROUSEL_SCROLL_USE_CASE
###############################################################################

CAROUSEL_SCROLL_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Explicitly mention scrolling/navigating a carousel (use phrases like "Scroll left", "Browse more", etc.)
2. Include carousel section title if specified in constraints
3. Must specify direction (left/right) if required
4. Should not include product selection actions
5. Dont mention two conditions about same field, like direction ( example "Scroll left in the carousel where the direction is 'RIGHT'") - this is not allowed.


For example:
- CORRECT: "Scroll right in the 'Featured Products' carousel"
- INCORRECT: "View details for product in carousel" (wrong action)
- INCORRECT: "Show me carousel items" (no scroll action)
- INCORRECT: Scroll left in the carousel where the direction is NOT 'LEFT'    (you cannot specify twice same direction)
"""

CAROUSEL_SCROLL_USE_CASE = UseCase(
    name="CAROUSEL_SCROLL",
    description="The user scrolls through a product carousel.",
    event=CarouselScrollEvent,
    event_source_code=CarouselScrollEvent.get_source_code_of_class(),
    constraints_generator=generate_carousel_scroll_constraints,
    additional_prompt_info=CAROUSEL_SCROLL_INFO,
    examples=[
        {
            "prompt": "Scroll right in the 'Kitchen Appliances' carousel",
            "prompt_for_task_generation": "Scroll <direction> in the '<carousel_title>' carousel",
        },
        {
            "prompt": "Browse more products in the 'Electronics' section",
            "prompt_for_task_generation": "Browse more products in the '<carousel_title>' section",
        },
        {
            "prompt": "Navigate left in the 'Best Sellers' carousel",
            "prompt_for_task_generation": "Navigate <direction> in the '<carousel_title>' carousel",
        },
        {
            "prompt": "Show me more items from the 'Featured Products' slider",
            "prompt_for_task_generation": "Show me more items from the '<carousel_title>' slider",
        },
    ],
)

###############################################################################
# UPDATED FINAL LIST: ALL_USE_CASES
###############################################################################

ALL_USE_CASES = [
    PRODUCT_DETAIL_USE_CASE,
    SEARCH_PRODUCT_USE_CASE,
    ADD_TO_CART_USE_CASE,
    VIEW_CART_USE_CASE,
    CAROUSEL_SCROLL_USE_CASE,
    QUANTITY_CHANGE_USE_CASE,
    PROCEED_TO_CHECKOUT_USE_CASE,
    CHECKOUT_STARTED_USE_CASE,
    ORDER_COMPLETION_USE_CASE,
]
