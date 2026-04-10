from __future__ import annotations

PROJECT_NUMBER = 7
WEB_PROJECT_ID = "autodelivery"

from autoppia_iwa.src.data_generation.tests.classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.classes import Trajectory
from autoppia_iwa.src.execution.actions.actions import (
    ClickAction,
    NavigateAction,
    SendKeysIWAAction,
    TypeAction,
)
from autoppia_iwa.src.execution.actions.base import BaseAction, Selector, SelectorType

ACTIONS = [
    {
        "url": "http://localhost:8006/?seed=223",
        "prompt": "Search for restaurants named 'Bella Vista'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=223",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__DELIVERY_SEARCH_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "SendKeysAction",
                "keys": ["Enter"],
                "attributes": {"keys": ["Enter"]},
            },
        ],
        "use_case": "SEARCH_DELIVERY_RESTAURANT",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=201",
        "prompt": "View details for the restaurant named 'Bella Vista'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=201",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__DELIVERY_SEARCH_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'] | //*[@id='restaurant-image'] | //*[@id='restaurant-name'])[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "VIEW_DELIVERY_RESTAURANT",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=648",
        "prompt": "Filter restaurants to show only Italian cuisine.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=648",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='search-filters']/div[3]/button[2]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__DELIVERY_SEARCH_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "SendKeysAction",
                "keys": ["Enter"],
                "attributes": {"keys": ["Enter"]},
            },
        ],
        "use_case": "RESTAURANT_FILTER",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=283",
        "prompt": "Return to the full restaurant list.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=283",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='quick-order-header' or contains(@id,'quick-order')] | //button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'quick order')] | //button[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'quick order')] | //nav//button[contains(@class,'bg-green-600')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//button[normalize-space()='View All Restaurants' or contains(normalize-space(),'View All') or contains(normalize-space(),'Restaurants')] | //div[contains(@class,'mt-6') and contains(@class,'pt-6') and contains(@class,'border-t')]//button[1])[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "VIEW_ALL_RESTAURANTS",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=12",
        "prompt": "Return to all restaurants after viewing 'Bella Vista'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=12",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__DELIVERY_SEARCH_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='restaurant-grid-item-0']//*[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'] | //*[@id='restaurant-image'] | //*[@id='restaurant-name'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='back-to-list' or @id='back-button' or contains(@id,'back-button')] | //button[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'back to all restaurants')] | //button[contains(normalize-space(),'Back to all')])[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "BACK_TO_ALL_RESTAURANTS",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/restaurants?seed=670",
        "prompt": "Open the add-to-cart modal for 'Pepperoni Classic' at 'Pizza Paradise'.",
        "actions": [
            {
                "url": "http://localhost:8006/restaurants?seed=670",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__DELIVERY_RESTAURANT_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='restaurant-grid-item-0']//*[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'] | //*[@id='restaurant-image'] | //*[@id='restaurant-name'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '__DELIVERY_MENU_ITEM__')]/ancestor::*[self::div or self::article][1]//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')][1] | //*[@id='add-to-cart' or contains(@id,'add-to-cart') or contains(@id,'add-cart')][1])",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "ADD_TO_CART_MODAL_OPEN",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=811",
        "prompt": "Add 'Pepperoni Classic' to cart from 'Pizza Paradise'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=811",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__DELIVERY_RESTAURANT_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='restaurant-grid-item-1']//*[contains(@class,'absolute')] | //*[@id='restaurant-grid-item-0']//*[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'] | //*[@id='restaurant-image'] | //*[@id='restaurant-name'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '__DELIVERY_MENU_ITEM__')]/ancestor::*[self::div or self::article][1]//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')][1] | //*[@id='add-to-cart' or contains(@id,'add-to-cart') or contains(@id,'add-cart')][1])",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@role='dialog']//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')] | //*[@id='add-to-cart' and ancestor::*[@role='dialog']] | //div[contains(@class,'sm:flex-row')]//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')])[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "ADD_TO_CART_MENU_ITEM",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=899",
        "prompt": "Start a quick order from any restaurant.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=899",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='quick-order' or @id='quick-order-header' or contains(@id,'quick-order')] | //button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'quick order')] | //button[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'quick order')])[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "QUICK_ORDER_STARTED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=345",
        "prompt": "Go to the checkout page.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=345",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='menu-item-1-1']//button | //*[@id='menu-item-1-0']//button | //*[@id='add-to-cart'][1])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@role='dialog']//*[@id='add-to-cart'] | //*[@role='dialog']//button[contains(normalize-space(), 'Add to Cart')] | //div[contains(@class,'sm:flex-row')]//button[contains(normalize-space(), 'Add to Cart')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "cart-total-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "OPEN_CHECKOUT_PAGE",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=822",
        "prompt": "Show me the next page of restaurants.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=822",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='pagination-next'] | //button[@id='pagination-next'] | //button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')])[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "RESTAURANT_NEXT_PAGE",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=24",
        "prompt": "Show me the previous page of restaurants.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=24",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='pagination-next'] | //button[@id='pagination-next'] | //button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='pagination-prev'] | //button[@id='pagination-prev'] | //button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'prev')] | //button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'previous')])[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "RESTAURANT_PREV_PAGE",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=745",
        "prompt": "Submit a review with name 'Agente' and comment 'good'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=745",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "review-name",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "Agente",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "review-name",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "review-comment",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "good",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "review-comment",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//button[contains(normalize-space(), 'Submit review')] | //*[@id='review-submit'] | //form//button[@type='submit'])[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "REVIEW_SUBMITTED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=893",
        "prompt": "Delete the review for the restaurant with name 'Bella Vista' where the author contains 'ria', the comment contains 'ood!', the rating is NOT '4.5', the cuisine does NOT contain 'Japanese', and the review_rating is NOT '4.5'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=893",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='review-item-0']//button | //*[@id='delete-review-btn'] | //button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'delete')])[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "DELETE_REVIEW",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=242",
        "prompt": "Empty my cart where the quantity is less than or equal to 8 and the price equals '14.99'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=242",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='menu-item-1-1']//button | //*[@id='menu-item-1-0']//button | //*[@id='add-to-cart'][1])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@role='dialog']//*[@id='add-to-cart'] | //*[@role='dialog']//button[contains(normalize-space(), 'Add to Cart')] | //div[contains(@class,'sm:flex-row')]//button[contains(normalize-space(), 'Add to Cart')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "cart-total-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='empty-cart-button-1-0'] | //*[@id='empty-cart-button'] | //button[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'remove item from cart')] | //button[contains(@title,'Remove item from cart')])[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "EMPTY_CART",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=371",
        "prompt": "Set dropoff preference where quantity greater equal 2 and item equals 'Picanha' and price less equal 26.99 and restaurant equals 'Carnaval Grill' and delivery_preference equals 'Hand it to me'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=371",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__DELIVERY_RESTAURANT_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@id='restaurant-grid-item-1']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '__DELIVERY_MENU_ITEM__')]/ancestor::*[self::div or self::article][1]//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')][1] | //*[@id='menu-item-1-0']//button | //*[@id='add-to-cart'][1])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='quantity-increase-1' or starts-with(@id,'quantity-increase') or contains(@id,'quantity-increase') or @aria-label='Increase quantity' or contains(@aria-label,'Increase quantity')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@role='dialog']//*[@id='add-to-cart'] | //*[@role='dialog']//button[contains(normalize-space(), 'Add to Cart')] | //div[contains(@class,'sm:flex-row')]//button[contains(normalize-space(), 'Add to Cart')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "cart-total-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='dropoff-preferences-selector'] | //*[@id='dropoff-section'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='dropoff-option-hand-it-to-me'] | //button[contains(normalize-space(), 'Hand it to me')])[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "DROPOFF_PREFERENCE",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=434",
        "prompt": "Add an address where quantity greater equal 2 and item equals 'Picanha' and price less equal 26.99 and restaurant equals 'Carnaval Grill' and address equals '505 Cherry Circle, Fairview'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=434",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__DELIVERY_RESTAURANT_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@id='restaurant-grid-item-1']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '__DELIVERY_MENU_ITEM__')]/ancestor::*[self::div or self::article][1]//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')][1] | //*[@id='menu-item-1-0']//button | //*[@id='add-to-cart'][1])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='quantity-increase-1' or starts-with(@id,'quantity-increase') or contains(@id,'quantity-increase') or @aria-label='Increase quantity' or contains(@aria-label,'Increase quantity')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@role='dialog']//*[@id='add-to-cart'] | //*[@role='dialog']//button[contains(normalize-space(), 'Add to Cart')] | //div[contains(@class,'sm:flex-row')]//button[contains(normalize-space(), 'Add to Cart')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "cart-total-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "address-selector",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "custom-address-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "505 Cherry Circle, Fairview",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "custom-address-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "save-address-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "ADDRESS_ADDED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=383",
        "prompt": "Place an order where address not contains '101 Elm Drive, Centerville' and phone not equals '+1-555-901-2345' and mode not contains 'delivery' and preferences not contains 'soy-free' and size not contains 'medium' and quantity less than '2' and price equals '14.3' and restaurant equals 'Tokyo Sushi House'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=383",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__DELIVERY_RESTAURANT_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@id='restaurant-grid-item-1']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'chicken teriyaki')]/ancestor::*[self::div or self::article][1]//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')][1] | //*[@id='menu-item-25-3']//button | //*[@id='menu-item-1-0']//button | //*[@id='add-to-cart'][1])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@role='dialog']//*[@id='add-to-cart'] | //*[@role='dialog']//button[contains(normalize-space(), 'Add to Cart')] | //div[contains(@class,'sm:flex-row')]//button[contains(normalize-space(), 'Add to Cart')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "cart-total-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='pickup-mode-button' or contains(@id,'pickup-mode-button')] | //button[contains(normalize-space(), 'Pickup')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='customer-name' or contains(@id,'customer-name')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "user",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='customer-name' or contains(@id,'customer-name')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='contact-phone' or contains(@id,'contact-phone')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "123456432",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='contact-phone' or contains(@id,'contact-phone')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='place-order' or contains(@id,'place-order')] | //button[contains(normalize-space(),'Place Order')])[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "PLACE_ORDER",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=239",
        "prompt": "Edit the cart item 'Margherita Pizza' from Sushi Zen where the item does NOT contain 'Egg & Cheese Sandwich' and the restaurant is NOT 'Waffle Works'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=239",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='menu-item-1-0']//button | //*[@id='add-to-cart'][1])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@role='dialog']//*[@id='add-to-cart'] | //*[@role='dialog']//button[contains(normalize-space(), 'Add to Cart')] | //div[contains(@class,'sm:flex-row')]//button[contains(normalize-space(), 'Add to Cart')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "cart-total-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='edit-cart'] | //*[@id='edit-cart-button-1-0'] | //*[@id='edit-cart-button'] | //button[contains(normalize-space(), 'Edit')])[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "EDIT_CART_ITEM",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=483",
        "prompt": "Select a delivery priority that is 'normal' for an item with size that CONTAINS 'll', a quantity of at least 2, an item that CONTAINS 'eek', a price greater than 9.17, and a restaurant that CONTAINS 'Table'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=483",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__DELIVERY_RESTAURANT_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@id='restaurant-grid-item-1']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '__DELIVERY_MENU_ITEM__')]/ancestor::*[self::div or self::article][1]//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')][1] | //*[@id='menu-item-1-0']//button | //*[@id='add-to-cart'][1])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@role='dialog']//*[@id='add-to-cart'] | //*[@role='dialog']//button[contains(normalize-space(), 'Add to Cart')] | //div[contains(@class,'sm:flex-row')]//button[contains(normalize-space(), 'Add to Cart')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "cart-total-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='quantity-increase-1-0' or starts-with(@id,'quantity-increase') or contains(@id,'quantity-increase') or @aria-label='Increase quantity' or contains(@aria-label,'Increase quantity')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//label[contains(normalize-space(), 'Priority: ready')])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//label[contains(normalize-space(), 'Normal: standard prep')] | //input[@name='delivery-priority' and @value='normal']/ancestor::label[1])[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "DELIVERY_PRIORITY_SELECTED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8006/?seed=693",
        "prompt": "Increase the quantity of 'Pepperoni Classic' to 2 at 'Pizza Paradise'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=693",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__DELIVERY_RESTAURANT_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='restaurant-grid-item-0']//*[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'] | //*[@id='restaurant-image'] | //*[@id='restaurant-name'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '__DELIVERY_MENU_ITEM__')]/ancestor::*[self::div or self::article][1]//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')][1] | //*[@id='add-to-cart' or contains(@id,'add-to-cart') or contains(@id,'add-cart')][1])",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='quantity-increase-1' or starts-with(@id,'quantity-increase') or contains(@id,'quantity-increase') or @aria-label='Increase quantity' or contains(@aria-label,'Increase quantity')])[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "ITEM_INCREMENTED",
        "has_success": False,
    },
]


# CheckEventTest payloads aligned with autodelivery_tasks.json (per use_case.name).
_RAW_TESTS: dict[str, list[dict]] = {
    "SEARCH_DELIVERY_RESTAURANT": [
        {
            "type": "CheckEventTest",
            "event_name": "SEARCH_DELIVERY_RESTAURANT",
            "event_criteria": {"query": {"operator": "not_equals", "value": "Casa Saltshaker"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "VIEW_DELIVERY_RESTAURANT": [
        {
            "type": "CheckEventTest",
            "event_name": "VIEW_DELIVERY_RESTAURANT",
            "event_criteria": {"rating": {"operator": "less_equal", "value": 4.7}, "cuisine": {"operator": "not_contains", "value": "Asian"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "RESTAURANT_FILTER": [
        {
            "type": "CheckEventTest",
            "event_name": "RESTAURANT_FILTER",
            "event_criteria": {"rating": {"operator": "less_than", "value": 4.7}, "cuisine": {"operator": "not_contains", "value": "Austrian"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "VIEW_ALL_RESTAURANTS": [{"type": "CheckEventTest", "event_name": "VIEW_ALL_RESTAURANTS", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "DELETE_REVIEW": [
        {
            "type": "CheckEventTest",
            "event_name": "DELETE_REVIEW",
            "event_criteria": {"cuisine": "Healthy", "rating": {"operator": "not_equals", "value": 4.8}, "author": {"operator": "not_equals", "value": "Olivia M."}},
            "description": "Check if specific event was triggered",
        }
    ],
    "BACK_TO_ALL_RESTAURANTS": [
        {
            "type": "CheckEventTest",
            "event_name": "BACK_TO_ALL_RESTAURANTS",
            "event_criteria": {"name": {"operator": "not_contains", "value": "Nobu"}, "cuisine": {"operator": "not_equals", "value": "Desserts"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "ADD_TO_CART_MODAL_OPEN": [
        {
            "type": "CheckEventTest",
            "event_name": "ADD_TO_CART_MODAL_OPEN",
            "event_criteria": {"price": 33.98, "restaurant": {"operator": "contains", "value": "ggan"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "ITEM_INCREMENTED": [
        {
            "type": "CheckEventTest",
            "event_name": "ITEM_INCREMENTED",
            "event_criteria": {
                "quantity": {"operator": "less_equal", "value": 7},
                "item": {"operator": "contains", "value": "hef's Special"},
                "restaurant": {"operator": "not_equals", "value": "Cedar Middle Eastern Cafe"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "ADD_TO_CART_MENU_ITEM": [
        {
            "type": "CheckEventTest",
            "event_name": "ADD_TO_CART_MENU_ITEM",
            "event_criteria": {
                "preferences": {"operator": "not_in_list", "value": ["vegetarian", "mild"]},
                "quantity": {"operator": "less_equal", "value": 8},
                "price": {"operator": "not_equals", "value": 25.98},
                "restaurant": "Waffle Works",
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "EDIT_CART_ITEM": [
        {
            "type": "CheckEventTest",
            "event_name": "EDIT_CART_ITEM",
            "event_criteria": {"item": "Hummus", "restaurant": {"operator": "not_contains", "value": "Beirut Express"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "QUICK_ORDER_STARTED": [{"type": "CheckEventTest", "event_name": "QUICK_ORDER_STARTED", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "QUICK_REORDER": [
        {
            "type": "CheckEventTest",
            "event_name": "QUICK_REORDER",
            "event_criteria": {"item": {"operator": "not_contains", "value": "Wagyu Beef"}, "restaurant": {"operator": "not_contains", "value": "Horváth"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "OPEN_CHECKOUT_PAGE": [
        {
            "type": "CheckEventTest",
            "event_name": "OPEN_CHECKOUT_PAGE",
            "event_criteria": {
                "preferences": {"operator": "contains", "value": "peanut-fre"},
                "size": {"operator": "not_contains", "value": "small"},
                "quantity": {"operator": "less_equal", "value": 3},
                "item": "Chef's Special",
                "restaurant": {"operator": "contains", "value": "ik"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "DROPOFF_PREFERENCE": [
        {
            "type": "CheckEventTest",
            "event_name": "DROPOFF_PREFERENCE",
            "event_criteria": {
                "quantity": {"operator": "greater_than", "value": 3},
                "price": {"operator": "less_equal", "value": 65.98},
                "item": {"operator": "contains", "value": "aisse"},
                "restaurant": "Gordon Ramsay",
                "delivery_preference": "Meet in the lobby",
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "ADDRESS_ADDED": [
        {
            "type": "CheckEventTest",
            "event_name": "ADDRESS_ADDED",
            "event_criteria": {
                "address": "404 Walnut Blvd, Brookside",
                "size": {"operator": "contains", "value": "al"},
                "preferences": {"operator": "contains", "value": "o-oni"},
                "quantity": 3,
                "price": {"operator": "not_equals", "value": 13.48},
                "restaurant": {"operator": "contains", "value": "Ba"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "EMPTY_CART": [
        {
            "type": "CheckEventTest",
            "event_name": "EMPTY_CART",
            "event_criteria": {"quantity": {"operator": "greater_than", "value": 9}, "item": "Wagyu Beef", "price": 91.98, "restaurant": {"operator": "contains", "value": "suya's"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "PLACE_ORDER": [
        {
            "type": "CheckEventTest",
            "event_name": "PLACE_ORDER",
            "event_criteria": {
                "address": "202 Birch Lane, Lakeview",
                "username": "George Kim",
                "mode": {"operator": "not_equals", "value": "delivery"},
                "phone": "+1-555-456-7890",
                "size": {"operator": "not_contains", "value": "large"},
                "preferences": {"operator": "not_in_list", "value": ["peanut-free", "organic"]},
                "quantity": {"operator": "not_equals", "value": 9},
                "item": "German Fried Potatoes",
                "restaurant": "Peter Luger Steak House",
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "RESTAURANT_NEXT_PAGE": [{"type": "CheckEventTest", "event_name": "RESTAURANT_NEXT_PAGE", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "RESTAURANT_PREV_PAGE": [{"type": "CheckEventTest", "event_name": "RESTAURANT_PREV_PAGE", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "REVIEW_SUBMITTED": [
        {
            "type": "CheckEventTest",
            "event_name": "REVIEW_SUBMITTED",
            "event_criteria": {"comment": {"operator": "not_contains", "value": "Super friendly staff and delicious food at the hotel restaurant."}},
            "description": "Check if specific event was triggered",
        }
    ],
    "DELIVERY_PRIORITY_SELECTED": [
        {
            "type": "CheckEventTest",
            "event_name": "DELIVERY_PRIORITY_SELECTED",
            "event_criteria": {
                "preferences": {"operator": "not_contains", "value": "paleo"},
                "quantity": {"operator": "less_equal", "value": 7},
                "price": {"operator": "greater_than", "value": 15.45},
                "restaurant": {"operator": "contains", "value": "Taco Fiesta"},
                "priority": {"operator": "not_equals", "value": "normal"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
}

_TESTS: dict[str, list[BaseTaskTest]] = {uc: [BaseTaskTest.deserialize(p) for p in pl] for uc, pl in _RAW_TESTS.items()}


def _uc(use_case: str, prompt: str, actions: list[BaseAction]) -> Trajectory:
    return Trajectory(name=use_case, prompt=prompt, actions=actions, tests=_TESTS[use_case])


def _xp(expr: str) -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value=expr)


def _id(element_id: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=element_id)


BASE = "http://localhost:8006"
# From autodelivery_tasks.json (?seed= in each task URL)
SEED_SEARCH_DELIVERY_RESTAURANT = 223
SEED_VIEW_DELIVERY_RESTAURANT = 201
SEED_RESTAURANT_FILTER = 648
SEED_VIEW_ALL_RESTAURANTS = 283
SEED_DELETE_REVIEW = 893
SEED_BACK_TO_ALL_RESTAURANTS = 12
SEED_ADD_TO_CART_MODAL_OPEN = 670
SEED_ITEM_INCREMENTED = 693
SEED_ADD_TO_CART_MENU_ITEM = 811
SEED_EDIT_CART_ITEM = 239
SEED_QUICK_ORDER_STARTED = 899
SEED_QUICK_REORDER = 956
SEED_OPEN_CHECKOUT_PAGE = 345
SEED_DROPOFF_PREFERENCE = 371
SEED_ADDRESS_ADDED = 434
SEED_EMPTY_CART = 242
SEED_PLACE_ORDER = 383
SEED_RESTAURANT_NEXT_PAGE = 822
SEED_RESTAURANT_PREV_PAGE = 24
SEED_REVIEW_SUBMITTED = 745
SEED_DELIVERY_PRIORITY_SELECTED = 483

SEARCH_DELIVERY_RESTAURANT = _uc(
    "SEARCH_DELIVERY_RESTAURANT",
    prompt="Search for restaurants where the query is NOT 'Casa Saltshaker'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_SEARCH_DELIVERY_RESTAURANT}"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__DELIVERY_SEARCH_QUERY__"),
        SendKeysIWAAction(keys="Enter"),
    ],
)

VIEW_DELIVERY_RESTAURANT = _uc(
    "VIEW_DELIVERY_RESTAURANT",
    prompt="Show me the details of a restaurant where the rating is less equal to '4.7' and the cuisine does not contain 'Asian'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_VIEW_DELIVERY_RESTAURANT}"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__DELIVERY_SEARCH_QUERY__"),
        ClickAction(selector=_xp("(//*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'] | //*[@id='restaurant-image'] | //*[@id='restaurant-name'])[1]")),
    ],
)

RESTAURANT_FILTER = _uc(
    "RESTAURANT_FILTER",
    prompt="Show me restaurants with a rating LESS THAN 4.7 that do NOT have a cuisine that CONTAINS 'Austrian'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_RESTAURANT_FILTER}"),
        ClickAction(selector=_xp("//*[@id='search-filters']/div[3]/button[2]")),
        TypeAction(selector=_id("search-input"), text="__DELIVERY_SEARCH_QUERY__"),
        SendKeysIWAAction(keys="Enter"),
    ],
)

VIEW_ALL_RESTAURANTS = _uc(
    "VIEW_ALL_RESTAURANTS",
    prompt="Show me all restaurants.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_VIEW_ALL_RESTAURANTS}"),
        ClickAction(
            selector=_xp(
                "(//*[@id='quick-order-header' or contains(@id,'quick-order')] | //button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'quick order')] | //button[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'quick order')] | //nav//button[contains(@class,'bg-green-600')])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//button[normalize-space()='View All Restaurants' or contains(normalize-space(),'View All') or contains(normalize-space(),'Restaurants')] | //div[contains(@class,'mt-6') and contains(@class,'pt-6') and contains(@class,'border-t')]//button[1])[1]"
            )
        ),
    ],
)

BACK_TO_ALL_RESTAURANTS = _uc(
    "BACK_TO_ALL_RESTAURANTS",
    prompt="Return to all restaurants where the name does NOT contain 'Nobu' and the cuisine does NOT equal 'Desserts'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_BACK_TO_ALL_RESTAURANTS}"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__DELIVERY_SEARCH_QUERY__"),
        ClickAction(
            selector=_xp(
                "(//*[@id='restaurant-grid-item-0']//*[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'] | //*[@id='restaurant-image'] | //*[@id='restaurant-name'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='back-to-list' or @id='back-button' or contains(@id,'back-button')] | //button[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'back to all restaurants')] | //button[contains(normalize-space(),'Back to all')])[1]"
            )
        ),
    ],
)

ADD_TO_CART_MODAL_OPEN = _uc(
    "ADD_TO_CART_MODAL_OPEN",
    prompt="Open the add-to-cart modal where price equals '33.98' and restaurant contains 'ggan'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_ADD_TO_CART_MODAL_OPEN}"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__DELIVERY_RESTAURANT_QUERY__"),
        ClickAction(
            selector=_xp(
                "(//*[@id='restaurant-grid-item-0']//*[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'] | //*[@id='restaurant-image'] | //*[@id='restaurant-name'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '__DELIVERY_MENU_ITEM__')]/ancestor::*[self::div or self::article][1]//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')][1] | //*[@id='add-to-cart' or contains(@id,'add-to-cart') or contains(@id,'add-cart')][1])"
            )
        ),
    ],
)

ADD_TO_CART_MENU_ITEM = _uc(
    "ADD_TO_CART_MENU_ITEM",
    prompt="Add a menu item to my cart where preferences is NOT one of ['vegetarian', 'mild'] and quantity is less equal '8' and price is NOT '25.98' and restaurant equals 'Waffle Works'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_ADD_TO_CART_MENU_ITEM}"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__DELIVERY_RESTAURANT_QUERY__"),
        ClickAction(
            selector=_xp(
                "(//*[@id='restaurant-grid-item-1']//*[contains(@class,'absolute')] | //*[@id='restaurant-grid-item-0']//*[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'] | //*[@id='restaurant-image'] | //*[@id='restaurant-name'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '__DELIVERY_MENU_ITEM__')]/ancestor::*[self::div or self::article][1]//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')][1] | //*[@id='add-to-cart' or contains(@id,'add-to-cart') or contains(@id,'add-cart')][1])"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@role='dialog']//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')] | //*[@id='add-to-cart' and ancestor::*[@role='dialog']] | //div[contains(@class,'sm:flex-row')]//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')])[1]"
            )
        ),
    ],
)

QUICK_ORDER_STARTED = _uc(
    "QUICK_ORDER_STARTED",
    prompt="Start a quick order from any restaurant.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_QUICK_ORDER_STARTED}"),
        ClickAction(
            selector=_xp(
                "(//*[@id='quick-order' or @id='quick-order-header' or contains(@id,'quick-order')] | //button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'quick order')] | //button[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'quick order')])[1]"
            )
        ),
    ],
)

OPEN_CHECKOUT_PAGE = _uc(
    "OPEN_CHECKOUT_PAGE",
    prompt="Go to the checkout page where preferences contains 'peanut-fre' and size not contains 'small' and quantity less equal '3' and item equals 'Chef's Special' and restaurant contains 'ik'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_OPEN_CHECKOUT_PAGE}"),
        ClickAction(selector=_xp("(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]")),
        ClickAction(selector=_xp("(//*[@id='menu-item-1-1']//button | //*[@id='menu-item-1-0']//button | //*[@id='add-to-cart'][1])[1]")),
        ClickAction(
            selector=_xp(
                "(//*[@role='dialog']//*[@id='add-to-cart'] | //*[@role='dialog']//button[contains(normalize-space(), 'Add to Cart')] | //div[contains(@class,'sm:flex-row')]//button[contains(normalize-space(), 'Add to Cart')])[1]"
            )
        ),
        ClickAction(selector=_id("cart-total-button")),
    ],
)

RESTAURANT_NEXT_PAGE = _uc(
    "RESTAURANT_NEXT_PAGE",
    prompt="Show me the next set of restaurants.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_RESTAURANT_NEXT_PAGE}"),
        ClickAction(
            selector=_xp(
                "(//*[@id='pagination-next'] | //button[@id='pagination-next'] | //button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')])[1]"
            )
        ),
    ],
)

RESTAURANT_PREV_PAGE = _uc(
    "RESTAURANT_PREV_PAGE",
    prompt="Go back to the previous page of restaurants.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_RESTAURANT_PREV_PAGE}"),
        ClickAction(
            selector=_xp(
                "(//*[@id='pagination-next'] | //button[@id='pagination-next'] | //button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='pagination-prev'] | //button[@id='pagination-prev'] | //button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'prev')] | //button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'previous')])[1]"
            )
        ),
    ],
)

REVIEW_SUBMITTED = _uc(
    "REVIEW_SUBMITTED",
    prompt="Submit a review for a restaurant where the comment does NOT contain 'Super friendly staff and delicious food at the hotel restaurant.'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_REVIEW_SUBMITTED}"),
        ClickAction(selector=_xp("(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]")),
        ClickAction(selector=_id("review-name")),
        TypeAction(selector=_id("review-name"), text="Agente"),
        ClickAction(selector=_id("review-comment")),
        TypeAction(selector=_id("review-comment"), text="good"),
        ClickAction(selector=_xp("(//button[contains(normalize-space(), 'Submit review')] | //*[@id='review-submit'] | //form//button[@type='submit'])[1]")),
    ],
)

DELETE_REVIEW = _uc(
    "DELETE_REVIEW",
    prompt="Delete the review for the restaurant with cuisine equals 'Healthy' where the rating is NOT '4.8' and the author is NOT 'Olivia M.'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DELETE_REVIEW}"),
        ClickAction(selector=_xp("(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]")),
        ClickAction(
            selector=_xp(
                "(//*[@id='review-item-0']//button | //*[@id='delete-review-btn'] | //button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'delete')])[1]"
            )
        ),
    ],
)

EMPTY_CART = _uc(
    "EMPTY_CART",
    prompt="Clear my shopping cart of items where the quantity is greater than 9, the item equals 'Wagyu Beef', the price equals '91.98', and the restaurant contains 'suya's'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_EMPTY_CART}"),
        ClickAction(selector=_xp("(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]")),
        ClickAction(selector=_xp("(//*[@id='menu-item-1-1']//button | //*[@id='menu-item-1-0']//button | //*[@id='add-to-cart'][1])[1]")),
        ClickAction(
            selector=_xp(
                "(//*[@role='dialog']//*[@id='add-to-cart'] | //*[@role='dialog']//button[contains(normalize-space(), 'Add to Cart')] | //div[contains(@class,'sm:flex-row')]//button[contains(normalize-space(), 'Add to Cart')])[1]"
            )
        ),
        ClickAction(selector=_id("cart-total-button")),
        ClickAction(
            selector=_xp(
                "(//*[@id='empty-cart-button-1-0'] | //*[@id='empty-cart-button'] | //button[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'remove item from cart')] | //button[contains(@title,'Remove item from cart')])[1]"
            )
        ),
    ],
)

DROPOFF_PREFERENCE = _uc(
    "DROPOFF_PREFERENCE",
    prompt="Set dropoff preference where quantity greater than 3 and price less equal 65.98 and item contains 'aisse' and restaurant equals 'Gordon Ramsay' and delivery_preference equals 'Meet in the lobby'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DROPOFF_PREFERENCE}"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__DELIVERY_RESTAURANT_QUERY__"),
        ClickAction(
            selector=_xp(
                "(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@id='restaurant-grid-item-1']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '__DELIVERY_MENU_ITEM__')]/ancestor::*[self::div or self::article][1]//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')][1] | //*[@id='menu-item-1-0']//button | //*[@id='add-to-cart'][1])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='quantity-increase-1' or starts-with(@id,'quantity-increase') or contains(@id,'quantity-increase') or @aria-label='Increase quantity' or contains(@aria-label,'Increase quantity')])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@role='dialog']//*[@id='add-to-cart'] | //*[@role='dialog']//button[contains(normalize-space(), 'Add to Cart')] | //div[contains(@class,'sm:flex-row')]//button[contains(normalize-space(), 'Add to Cart')])[1]"
            )
        ),
        ClickAction(selector=_id("cart-total-button")),
        ClickAction(selector=_xp("(//*[@id='dropoff-preferences-selector'] | //*[@id='dropoff-section'])[1]")),
        ClickAction(selector=_xp("(//*[@id='dropoff-option-hand-it-to-me'] | //button[contains(normalize-space(), 'Hand it to me')])[1]")),
    ],
)

ADDRESS_ADDED = _uc(
    "ADDRESS_ADDED",
    prompt="Add an address that equals '404 Walnut Blvd, Brookside' with a size that contains 'al', preferences that contains 'o-oni', quantity equals '3', and price not equals '13.48' at a restaurant that contains 'Ba'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_ADDRESS_ADDED}"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__DELIVERY_RESTAURANT_QUERY__"),
        ClickAction(
            selector=_xp(
                "(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@id='restaurant-grid-item-1']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '__DELIVERY_MENU_ITEM__')]/ancestor::*[self::div or self::article][1]//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')][1] | //*[@id='menu-item-1-0']//button | //*[@id='add-to-cart'][1])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='quantity-increase-1' or starts-with(@id,'quantity-increase') or contains(@id,'quantity-increase') or @aria-label='Increase quantity' or contains(@aria-label,'Increase quantity')])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@role='dialog']//*[@id='add-to-cart'] | //*[@role='dialog']//button[contains(normalize-space(), 'Add to Cart')] | //div[contains(@class,'sm:flex-row')]//button[contains(normalize-space(), 'Add to Cart')])[1]"
            )
        ),
        ClickAction(selector=_id("cart-total-button")),
        ClickAction(selector=_id("address-selector")),
        ClickAction(selector=_id("custom-address-input")),
        TypeAction(selector=_id("custom-address-input"), text="505 Cherry Circle, Fairview"),
        ClickAction(selector=_id("save-address-button")),
    ],
)

PLACE_ORDER = _uc(
    "PLACE_ORDER",
    prompt="Place an order where address equals '202 Birch Lane, Lakeview' and username equals 'George Kim' and mode not equals 'delivery' and phone equals '+1-555-456-7890' and size not contains 'large' and preferences is not one of ['peanut-free', 'organic'] and quantity not equals '9' and item equals 'German Fried Potatoes' and restaurant equals 'Peter Luger Steak House'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_PLACE_ORDER}"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__DELIVERY_RESTAURANT_QUERY__"),
        ClickAction(
            selector=_xp(
                "(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@id='restaurant-grid-item-1']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'chicken teriyaki')]/ancestor::*[self::div or self::article][1]//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')][1] | //*[@id='menu-item-25-3']//button | //*[@id='menu-item-1-0']//button | //*[@id='add-to-cart'][1])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@role='dialog']//*[@id='add-to-cart'] | //*[@role='dialog']//button[contains(normalize-space(), 'Add to Cart')] | //div[contains(@class,'sm:flex-row')]//button[contains(normalize-space(), 'Add to Cart')])[1]"
            )
        ),
        ClickAction(selector=_id("cart-total-button")),
        ClickAction(selector=_xp("(//*[@id='pickup-mode-button' or contains(@id,'pickup-mode-button')] | //button[contains(normalize-space(), 'Pickup')])[1]")),
        ClickAction(selector=_xp("(//*[@id='customer-name' or contains(@id,'customer-name')])[1]")),
        TypeAction(selector=_xp("(//*[@id='customer-name' or contains(@id,'customer-name')])[1]"), text="user"),
        ClickAction(selector=_xp("(//*[@id='contact-phone' or contains(@id,'contact-phone')])[1]")),
        TypeAction(selector=_xp("(//*[@id='contact-phone' or contains(@id,'contact-phone')])[1]"), text="123456432"),
        ClickAction(selector=_xp("(//*[@id='place-order' or contains(@id,'place-order')] | //button[contains(normalize-space(),'Place Order')])[1]")),
    ],
)

EDIT_CART_ITEM = _uc(
    "EDIT_CART_ITEM",
    prompt="Edit the cart item 'Hummus' from a restaurant that does NOT contain 'Beirut Express'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_EDIT_CART_ITEM}"),
        ClickAction(selector=_xp("(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]")),
        ClickAction(selector=_xp("(//*[@id='menu-item-1-0']//button | //*[@id='add-to-cart'][1])[1]")),
        ClickAction(
            selector=_xp(
                "(//*[@role='dialog']//*[@id='add-to-cart'] | //*[@role='dialog']//button[contains(normalize-space(), 'Add to Cart')] | //div[contains(@class,'sm:flex-row')]//button[contains(normalize-space(), 'Add to Cart')])[1]"
            )
        ),
        ClickAction(selector=_id("cart-total-button")),
        ClickAction(selector=_xp("(//*[@id='edit-cart'] | //*[@id='edit-cart-button-1-0'] | //*[@id='edit-cart-button'] | //button[contains(normalize-space(), 'Edit')])[1]")),
    ],
)

DELIVERY_PRIORITY_SELECTED = _uc(
    "DELIVERY_PRIORITY_SELECTED",
    prompt="Select a delivery priority for my order that is NOT 'normal', with a quantity of items that is less than or equal to 7, a price that is greater than 15.45, and from a restaurant that contains 'Taco Fiesta', ensuring that my preferences do NOT contain 'paleo'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DELIVERY_PRIORITY_SELECTED}"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__DELIVERY_RESTAURANT_QUERY__"),
        ClickAction(
            selector=_xp(
                "(//*[@id='restaurant-grid-item-0']//div[contains(@class,'absolute')] | //*[@id='restaurant-grid-item-1']//div[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '__DELIVERY_MENU_ITEM__')]/ancestor::*[self::div or self::article][1]//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')][1] | //*[@id='menu-item-1-0']//button | //*[@id='add-to-cart'][1])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@role='dialog']//*[@id='add-to-cart'] | //*[@role='dialog']//button[contains(normalize-space(), 'Add to Cart')] | //div[contains(@class,'sm:flex-row')]//button[contains(normalize-space(), 'Add to Cart')])[1]"
            )
        ),
        ClickAction(selector=_id("cart-total-button")),
        ClickAction(
            selector=_xp(
                "(//*[@id='quantity-increase-1-0' or starts-with(@id,'quantity-increase') or contains(@id,'quantity-increase') or @aria-label='Increase quantity' or contains(@aria-label,'Increase quantity')])[1]"
            )
        ),
        ClickAction(selector=_xp("(//label[contains(normalize-space(), 'Priority: ready')])[1]")),
        ClickAction(selector=_xp("(//label[contains(normalize-space(), 'Normal: standard prep')] | //input[@name='delivery-priority' and @value='normal']/ancestor::label[1])[1]")),
    ],
)

ITEM_INCREMENTED = _uc(
    "ITEM_INCREMENTED",
    prompt="Increase the quantity of 'hef's Special' to 7 where the restaurant is NOT 'Cedar Middle Eastern Cafe'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_ITEM_INCREMENTED}"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__DELIVERY_RESTAURANT_QUERY__"),
        ClickAction(
            selector=_xp(
                "(//*[@id='restaurant-grid-item-0']//*[contains(@class,'absolute')] | //*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'] | //*[@id='restaurant-image'] | //*[@id='restaurant-name'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '__DELIVERY_MENU_ITEM__')]/ancestor::*[self::div or self::article][1]//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')][1] | //*[@id='add-to-cart' or contains(@id,'add-to-cart') or contains(@id,'add-cart')][1])"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='quantity-increase-1' or starts-with(@id,'quantity-increase') or contains(@id,'quantity-increase') or @aria-label='Increase quantity' or contains(@aria-label,'Increase quantity')])[1]"
            )
        ),
    ],
)


def load_autodelivery_use_case_completion_flows() -> dict[str, Trajectory]:
    return {
        "SEARCH_DELIVERY_RESTAURANT": SEARCH_DELIVERY_RESTAURANT,
        "VIEW_DELIVERY_RESTAURANT": VIEW_DELIVERY_RESTAURANT,
        "RESTAURANT_FILTER": RESTAURANT_FILTER,
        "VIEW_ALL_RESTAURANTS": VIEW_ALL_RESTAURANTS,
        "BACK_TO_ALL_RESTAURANTS": BACK_TO_ALL_RESTAURANTS,
        "ADD_TO_CART_MODAL_OPEN": ADD_TO_CART_MODAL_OPEN,
        "ADD_TO_CART_MENU_ITEM": ADD_TO_CART_MENU_ITEM,
        "QUICK_ORDER_STARTED": QUICK_ORDER_STARTED,
        "OPEN_CHECKOUT_PAGE": OPEN_CHECKOUT_PAGE,
        "RESTAURANT_NEXT_PAGE": RESTAURANT_NEXT_PAGE,
        "RESTAURANT_PREV_PAGE": RESTAURANT_PREV_PAGE,
        "REVIEW_SUBMITTED": REVIEW_SUBMITTED,
        "DELETE_REVIEW": DELETE_REVIEW,
        "EMPTY_CART": EMPTY_CART,
        "DROPOFF_PREFERENCE": DROPOFF_PREFERENCE,
        "ADDRESS_ADDED": ADDRESS_ADDED,
        "PLACE_ORDER": PLACE_ORDER,
        "EDIT_CART_ITEM": EDIT_CART_ITEM,
        "DELIVERY_PRIORITY_SELECTED": DELIVERY_PRIORITY_SELECTED,
        "ITEM_INCREMENTED": ITEM_INCREMENTED,
    }
