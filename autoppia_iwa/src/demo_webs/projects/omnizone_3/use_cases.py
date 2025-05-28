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
    # generate_order_completion_constraints,
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
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_DETAIL",
                "event_criteria": {"item_name": {"value": "Espresso Machine", "operator": "equals"}},
                "reasoning": "Explicitly requests to view details for a specific product.",
            },
        },
        {
            "prompt": "View product page for a 'Kitchen' item with rating above 4.6",
            "prompt_for_task_generation": "View product page for a <product_category> item with rating above <rating>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_DETAIL",
                "event_criteria": {
                    "item_category": {"value": "Kitchen", "operator": "equals"},
                    "item_rating": {"value": 4.6, "operator": "greater_than"},
                },
                "reasoning": "Requests to view details for products matching category and rating criteria.",
            },
        },
        {
            "prompt": "Show me the details for the cheapest Electric Kettle",
            "prompt_for_task_generation": "Show me the details for the <price_sort> <product_category>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_DETAIL",
                "event_criteria": {
                    "item_category": {"value": "Electric Kettle", "operator": "equals"},
                    "sort_by": {"value": "price", "operator": "equals"},
                    "sort_order": {"value": "asc", "operator": "equals"},
                },
                "reasoning": "Requests to view details for products matching category with specific sorting.",
            },
        },
        {
            "prompt": "Display product details for a KitchenAid Stand Mixer between $200 and $300",
            "prompt_for_task_generation": "Display product details for a <brand> <product_name> between <min_price> and <max_price>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "VIEW_DETAIL",
                "event_criteria": {
                    "item_brand": {"value": "KitchenAid", "operator": "equals"},
                    "item_name": {"value": "Stand Mixer", "operator": "equals"},
                    "item_price": {"value": 200.00, "operator": "greater_than_or_equal"},
                    # "item_price": {"value": 300.00, "operator": "less_than_or_equal"},
                },
                "reasoning": "Requests to view details for products matching multiple criteria.",
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
    constraints_generator=generate_search_query_constraints,
    replace_func=replace_products_placeholders,
    additional_prompt_info=SEARCH_PRODUCT_INFO,
    examples=[
        {
            "prompt": "Search for kitchen appliances",
            "prompt_for_task_generation": "Search for <query>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_PRODUCT",
                "event_criteria": {"query": {"value": "kitchen appliances"}},
                "reasoning": "Explicit search for products matching the query.",
            },
        },
        {
            "prompt": "Find products matching 'Espresso Machine'",
            "prompt_for_task_generation": "Find products matching '<query>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_PRODUCT",
                "event_criteria": {"query": {"value": "Espresso Machine"}},
                "reasoning": "Search with exact phrase match.",
            },
        },
        {
            "prompt": "Look up Wireless Earbuds",
            "prompt_for_task_generation": "Look up <query>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_PRODUCT",
                "event_criteria": {"query": {"value": "Wireless Earbuds"}},
                "reasoning": "Search with specific product specifications.",
            },
        },
        {
            "prompt": "Search for products by KitchenAid",
            "prompt_for_task_generation": "Search for <query>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_PRODUCT",
                "event_criteria": {"query": {"value": "products by KitchenAid"}},
                "reasoning": "Search with brand name included.",
            },
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
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_TO_CART",
                "event_criteria": {"item_name": {"value": "Air Fryer", "operator": "equals"}},
                "reasoning": "Explicit request to add specific product to cart.",
            },
        },
        {
            "prompt": "Put 2 units of the Stainless Steel Cookware Set in my shopping cart",
            "prompt_for_task_generation": "Put <quantity> units of the <product_name> in my shopping cart",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_TO_CART",
                "event_criteria": {
                    "item_name": {"value": "Stainless Steel Cookware Set", "operator": "equals"},
                    "quantity": {"value": 2, "operator": "equals"},
                },
                "reasoning": "Adds specific product with quantity.",
            },
        },
        {
            "prompt": "Add the Smart Watch to my cart",
            "prompt_for_task_generation": "Add the <product_name> to my cart",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_TO_CART",
                "event_criteria": {"item_name": {"value": "Smart Watch", "operator": "equals"}},
                "reasoning": "Adds product by name.",
            },
        },
        {
            "prompt": "Add three of item kitchen-4 to my cart",
            "prompt_for_task_generation": "Add <quantity> of item <product_reference> to my cart",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_TO_CART",
                "event_criteria": {
                    "item_id": {"value": "kitchen-4", "operator": "equals"},
                    "quantity": {"value": 3, "operator": "equals"},
                },
                "reasoning": "Adds product by ID with quantity.",
            },
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
    examples=[
        {
            "prompt": "View my shopping cart",
            "prompt_for_task_generation": "View my shopping cart",
            "test": {"type": "CheckEventTest", "event_name": "VIEW_CART", "event_criteria": {}, "reasoning": "Simple request to view cart contents."},
        },
        {
            "prompt": "Show me what's in my cart right now",
            "prompt_for_task_generation": "Show me what's in my cart right now",
            "test": {"type": "CheckEventTest", "event_name": "VIEW_CART", "event_criteria": {}, "reasoning": "Alternative phrasing to view cart."},
        },
        {
            "prompt": "Display my current shopping basket contents",
            "prompt_for_task_generation": "Display my current shopping basket contents",
            "test": {"type": "CheckEventTest", "event_name": "VIEW_CART", "event_criteria": {}, "reasoning": "British English variant for viewing cart."},
        },
        {
            "prompt": "What items do I have in my cart?",
            "prompt_for_task_generation": "What items do I have in my cart?",
            "test": {"type": "CheckEventTest", "event_name": "VIEW_CART", "event_criteria": {}, "reasoning": "Question format to view cart."},
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
            "test": {"type": "CheckEventTest", "event_name": "CHECKOUT_STARTED", "event_criteria": {}, "reasoning": "Initiates checkout process with current cart contents by clicking Buy now."},
        },
        {
            "prompt": "Click Buy now to start the checkout process for these items",
            "prompt_for_task_generation": "Click Buy now to start the checkout process for these items",
            "test": {"type": "CheckEventTest", "event_name": "CHECKOUT_STARTED", "event_criteria": {}, "reasoning": "Initiates checkout with implied cart contents by clicking Buy now."},
        },
        {
            "prompt": "I want to begin checkout for my selected products, click the Buy now button.",
            "prompt_for_task_generation": "I want to begin checkout for my selected products, click the Buy now button.",
            "test": {"type": "CheckEventTest", "event_name": "CHECKOUT_STARTED", "event_criteria": {}, "reasoning": "Alternative phrasing to start checkout via Buy now."},
        },
        {
            "prompt": "I'm ready to checkout now, click Buy now.",
            "prompt_for_task_generation": "I'm ready to checkout now, click Buy now.",
            "test": {"type": "CheckEventTest", "event_name": "CHECKOUT_STARTED", "event_criteria": {}, "reasoning": "Simple declaration to start checkout by clicking Buy now."},
        },
        {
            "prompt": "Buy now and take me to the checkout page.",
            "prompt_for_task_generation": "Buy now and take me to the checkout page.",
            "test": {"type": "CheckEventTest", "event_name": "CHECKOUT_STARTED", "event_criteria": {}, "reasoning": "Direct request to proceed to checkout via Buy now."},
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
    # constraints_generator=generate_order_completion_constraints,
    additional_prompt_info=ORDER_COMPLETION_INFO,
    examples=[
        {
            "prompt": "Complete my purchase with Credit Card",
            "prompt_for_task_generation": "Complete my purchase with Credit Card",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ORDER_COMPLETED",
                # "event_criteria": {"payment_method": {"value": "Credit Card", "operator": "equals"}},
                "reasoning": "Completes the order with specified payment method.",
            },
        },
        {
            "prompt": "Place my order using my saved payment info",
            "prompt_for_task_generation": "Place my order using my saved payment info",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ORDER_COMPLETED",
                # "event_criteria": {"payment_method": {"value": "saved payment info", "operator": "equals"}},
                "reasoning": "Completes order with saved payment method.",
            },
        },
        {
            "prompt": "Finalize my purchase with standard shipping",
            "prompt_for_task_generation": "Finalize my purchase with standard shipping",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ORDER_COMPLETED",
                # "event_criteria": {"shipping_method": {"value": "standard", "operator": "equals"}},
                "reasoning": "Completes order with shipping preference.",
            },
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
            "test": {"type": "CheckEventTest", "event_name": "PROCEED_TO_CHECKOUT", "event_criteria": {}, "reasoning": "Initiates checkout process with current cart contents."},
        },
        {
            "prompt": "Go to checkout with my 3 items worth $379.97",
            "prompt_for_task_generation": "Go to checkout with my <item_count> items worth <total_amount>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "PROCEED_TO_CHECKOUT",
                "event_criteria": {"total_amount": {"value": 379.97, "operator": "equals"}},
                "reasoning": "Proceeds to checkout with specific item count and total amount.",
            },
        },
        {
            "prompt": "Take me to checkout with these selected products",
            "prompt_for_task_generation": "Take me to checkout with <cart_reference>",
            "test": {"type": "CheckEventTest", "event_name": "PROCEED_TO_CHECKOUT", "event_criteria": {}, "reasoning": "Alternative phrasing to proceed to checkout."},
        },
        {
            "prompt": "Continue to checkout with the items in my cart",
            "prompt_for_task_generation": "Continue to checkout with the items in my cart",
            "test": {"type": "CheckEventTest", "event_name": "PROCEED_TO_CHECKOUT", "event_criteria": {}, "reasoning": "Explicit reference to cart items for checkout."},
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
            "test": {
                "type": "CheckEventTest",
                "event_name": "QUANTITY_CHANGED",
                "event_criteria": {
                    "item_name": {"value": "Espresso Machine", "operator": "equals"},
                    "new_quantity": {"value": 2, "operator": "equals"},
                },
                "reasoning": "Changes quantity of specific product in cart.",
            },
        },
        {
            "prompt": "Reduce quantity of Wireless Earbuds in my cart to 1",
            "prompt_for_task_generation": "Reduce quantity of <product_name> in my cart to <new_quantity>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "QUANTITY_CHANGED",
                "event_criteria": {"item_name": {"value": "Wireless Earbuds", "operator": "equals"}, "new_quantity": {"value": 1, "operator": "equals"}},
                "reasoning": "Reduces quantity of product without specifying previous quantity.",
            },
        },
        {
            "prompt": "Change the quantity of item kitchen-6 to 3",
            "prompt_for_task_generation": "Change the quantity of <product_id> from <previous_quantity> to <new_quantity>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "QUANTITY_CHANGED",
                "event_criteria": {
                    "item_id": {"value": "kitchen-6", "operator": "equals"},
                    "new_quantity": {"value": 3, "operator": "equals"},
                },
                "reasoning": "Changes quantity using product ID reference.",
            },
        },
        {
            "prompt": "Increase quantity of the Electric Kettle by 5",
            "prompt_for_task_generation": "Increase quantity of <product_name> by <new_quantity>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "QUANTITY_CHANGED",
                "event_criteria": {
                    "item_name": {"value": "Electric Kettle", "operator": "equals"},
                    "new_quantity": {"value": 1, "operator": "equals"},
                },
                "reasoning": "Changes quantity by delta using product name.",
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
    constraints_generator=generate_carousel_scroll_constraints,
    additional_prompt_info=CAROUSEL_SCROLL_INFO,
    examples=[
        {
            "prompt": "Scroll right in the 'Kitchen Appliances' carousel",
            "prompt_for_task_generation": "Scroll <direction> in the '<carousel_title>' carousel",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CAROUSEL_SCROLL",
                "event_criteria": {"direction": {"value": "RIGHT", "operator": "equals"}, "title": {"value": "Kitchen Appliances", "operator": "equals"}},
                "reasoning": "Scrolls right in specified carousel section.",
            },
        },
        {
            "prompt": "Browse more products in the 'Electronics' section",
            "prompt_for_task_generation": "Browse more products in the '<carousel_title>' section",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CAROUSEL_SCROLL",
                "event_criteria": {"title": {"value": "Electronics", "operator": "equals"}},
                "reasoning": "Implies scrolling through specified carousel (default direction).",
            },
        },
        {
            "prompt": "Navigate left in the 'Best Sellers' carousel",
            "prompt_for_task_generation": "Navigate <direction> in the '<carousel_title>' carousel",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CAROUSEL_SCROLL",
                "event_criteria": {"direction": {"value": "LEFT", "operator": "equals"}, "title": {"value": "Best Sellers", "operator": "equals"}},
                "reasoning": "Navigates left in specified carousel section.",
            },
        },
        {
            "prompt": "Show me more items from the 'Featured Products' slider",
            "prompt_for_task_generation": "Show me more items from the '<carousel_title>' slider",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CAROUSEL_SCROLL",
                "event_criteria": {"title": {"value": "Featured Products", "operator": "equals"}},
                "reasoning": "Alternative terminology for scrolling through carousel.",
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
    CAROUSEL_SCROLL_USE_CASE,
    QUANTITY_CHANGE_USE_CASE,
    PROCEED_TO_CHECKOUT_USE_CASE,
    CHECKOUT_STARTED_USE_CASE,
    ORDER_COMPLETION_USE_CASE,
]
