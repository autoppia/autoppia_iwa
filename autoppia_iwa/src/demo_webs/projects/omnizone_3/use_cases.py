from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import AddToCartEvent, CarouselScrollEvent, CheckoutStartedEvent, ItemDetailEvent, OrderCompletedEvent, ProceedToCheckoutEvent, QuantityChangedEvent, SearchProductEvent, ViewCartEvent
from .generation_functions import generate_omnizone_products_constraints
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
    name="PRODUCT_DETAIL",
    description="The user explicitly requests to view the details page of a specific product that meets certain criteria.",
    event=ItemDetailEvent,
    event_source_code=ItemDetailEvent.get_source_code_of_class(),
    constraints_generator=generate_omnizone_products_constraints,
    replace_func=replace_products_placeholders,
    additional_prompt_info=PRODUCT_DETAIL_INFO,
    examples=[
        {
            "prompt": "Show me details for the iPhone 15 Pro",
            "prompt_for_task_generation": "Show me details for the <product_name>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_DETAIL",
                "event_criteria": {"item_name": {"value": "iPhone 15 Pro", "operator": "equals"}},
                "reasoning": "Explicitly requests to view details for a specific product.",
            },
        },
        {
            "prompt": "View product page for a 'laptop' with rating above 4.5",
            "prompt_for_task_generation": "View product page for a <product_name> with rating above <rating>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_DETAIL",
                "event_criteria": {"item_category": {"value": "laptop", "operator": "equals"}, "item_rating": {"value": 4.5, "operator": "greater_than"}},
                "reasoning": "Requests to view details for products matching category and rating criteria.",
            },
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
    additional_prompt_info=SEARCH_PRODUCT_INFO,
    replace_func=replace_products_placeholders,
    examples=[
        {
            "prompt": "Search for wireless earbuds",
            "prompt_for_task_generation": "Search for <query>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_PRODUCT",
                "event_criteria": {"query": {"value": "wireless earbuds"}},
                "reasoning": "Explicit search for products matching the query.",
            },
        }
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
- CORRECT: "Add 2 iPhone 15 cases to cart"
- INCORRECT: "Buy iPhone 15 cases" (implies checkout)
"""

ADD_TO_CART_USE_CASE = UseCase(
    name="ADD_TO_CART",
    description="The user adds items to their shopping cart.",
    event=AddToCartEvent,
    event_source_code=AddToCartEvent.get_source_code_of_class(),
    constraints_generator=generate_omnizone_products_constraints,
    replace_func=replace_products_placeholders,
    additional_prompt_info=ADD_TO_CART_INFO,
    examples=[
        {
            "prompt": "Add AirPods Pro to my cart",
            "prompt_for_task_generation": "Add <product_name> to my cart",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_TO_CART",
                "event_criteria": {"item_name": {"value": "AirPods Pro", "operator": "equals"}},
                "reasoning": "Explicit request to add specific product to cart.",
            },
        }
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
- INCORRECT: "Show me iPhone in my cart" (includes product detail)
"""

VIEW_CART_USE_CASE = UseCase(
    name="VIEW_CART",
    description="The user views the contents of their shopping cart.",
    event=ViewCartEvent,
    event_source_code=ViewCartEvent.get_source_code_of_class(),
    additional_prompt_info=VIEW_CART_INFO,
    examples=[
        {
            "prompt": "View my shopping cart",
            "prompt_for_task_generation": "View my shopping cart",
            "test": {"type": "CheckEventTest", "event_name": "VIEW_CART", "event_criteria": {}, "reasoning": "Simple request to view cart contents."},
        }
    ],
)

###############################################################################
# CHECKOUT_USE_CASE
###############################################################################

CHECKOUT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Explicitly mention checkout/proceeding to purchase
2. May include cart contents if specified in constraints
3. DO NOT include payment/shipping details unless specified

For example:
- CORRECT: "Proceed to checkout with my cart items"
- INCORRECT: "Pay for my order" (too late in flow)
"""

CHECKOUT_USE_CASE = UseCase(
    name="CHECKOUT_STARTED",
    description="The user initiates the checkout process.",
    event=CheckoutStartedEvent,
    event_source_code=CheckoutStartedEvent.get_source_code_of_class(),
    additional_prompt_info=CHECKOUT_INFO,
    examples=[
        {
            "prompt": "Proceed to checkout with my current cart",
            "prompt_for_task_generation": "Proceed to checkout with my current cart",
            "test": {"type": "CheckEventTest", "event_name": "CHECKOUT_STARTED", "event_criteria": {}, "reasoning": "Initiates checkout process with current cart contents."},
        }
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
    name="ORDER_COMPLETION",
    description="The user completes an order/purchase.",
    event=OrderCompletedEvent,
    event_source_code=OrderCompletedEvent.get_source_code_of_class(),
    additional_prompt_info=ORDER_COMPLETION_INFO,
    examples=[
        {
            "prompt": "Complete my purchase with PayPal",
            "prompt_for_task_generation": "Complete my purchase with <payment_method>",
            "test": {"type": "CheckEventTest", "event_name": "ORDER_COMPLETED", "event_criteria": {}, "reasoning": "Completes the order with specified payment method."},
        }
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
    additional_prompt_info=PROCEED_TO_CHECKOUT_INFO,
    examples=[
        {
            "prompt": "Proceed to checkout with my current cart items",
            "prompt_for_task_generation": "Proceed to checkout with my current cart items",
            "test": {"type": "CheckEventTest", "event_name": "PROCEED_TO_CHECKOUT", "event_criteria": {}, "reasoning": "Initiates checkout process with current cart contents."},
        },
        {
            "prompt": "Go to checkout with my 2 items worth $99.98",
            "prompt_for_task_generation": "Go to checkout with my <item_count> items worth <total_amount>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "PROCEED_TO_CHECKOUT",
                "event_criteria": {"total_items": {"value": 2, "operator": "equals"}, "total_amount": {"value": 99.98, "operator": "equals"}},
                "reasoning": "Proceeds to checkout with specific item count and total amount.",
            },
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
    additional_prompt_info=QUANTITY_CHANGE_INFO,
    examples=[
        {
            "prompt": "Update quantity of AirPods Pro in my cart from 1 to 2",
            "prompt_for_task_generation": "Update quantity of <product_name> in my cart from <previous_quantity> to <new_quantity>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "QUANTITY_CHANGED",
                "event_criteria": {
                    "item_name": {"value": "AirPods Pro", "operator": "equals"},
                    "previous_quantity": {"value": 1, "operator": "equals"},
                    "new_quantity": {"value": 2, "operator": "equals"},
                },
                "reasoning": "Changes quantity of specific product in cart.",
            },
        },
        {
            "prompt": "Reduce quantity of USB-C cables in my cart to 1",
            "prompt_for_task_generation": "Reduce quantity of <product_name> in my cart to <new_quantity>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "QUANTITY_CHANGED",
                "event_criteria": {"item_name": {"value": "USB-C cables", "operator": "equals"}, "new_quantity": {"value": 1, "operator": "equals"}},
                "reasoning": "Reduces quantity of product without specifying previous quantity.",
            },
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

For example:
- CORRECT: "Scroll right in the 'Featured Products' carousel"
- INCORRECT: "View details for product in carousel" (wrong action)
- INCORRECT: "Show me carousel items" (no scroll action)
"""

CAROUSEL_SCROLL_USE_CASE = UseCase(
    name="CAROUSEL_SCROLL",
    description="The user scrolls through a product carousel.",
    event=CarouselScrollEvent,
    event_source_code=CarouselScrollEvent.get_source_code_of_class(),
    additional_prompt_info=CAROUSEL_SCROLL_INFO,
    examples=[
        {
            "prompt": "Scroll right in the 'Recommended For You' carousel",
            "prompt_for_task_generation": "Scroll <direction> in the '<carousel_title>' carousel",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CAROUSEL_SCROLL",
                "event_criteria": {"direction": {"value": "RIGHT", "operator": "equals"}, "title": {"value": "Recommended For You", "operator": "equals"}},
                "reasoning": "Scrolls right in specified carousel section.",
            },
        },
        {
            "prompt": "Browse more products in the 'Trending Now' section",
            "prompt_for_task_generation": "Browse more products in the '<carousel_title>' section",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CAROUSEL_SCROLL",
                "event_criteria": {"title": {"value": "Trending Now", "operator": "equals"}},
                "reasoning": "Implies scrolling through specified carousel (default direction).",
            },
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
    QUANTITY_CHANGE_USE_CASE,
    PROCEED_TO_CHECKOUT_USE_CASE,
    CHECKOUT_USE_CASE,
    ORDER_COMPLETION_USE_CASE,
    CAROUSEL_SCROLL_USE_CASE,
]
