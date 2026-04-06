from __future__ import annotations

import re
from typing import Any

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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Search for restaurants named 'Bella Vista'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "View details for the restaurant named 'Bella Vista'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Filter restaurants to show only Italian cuisine.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Return to the full restaurant list.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Return to all restaurants after viewing 'Bella Vista'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/restaurants?seed=1",
        "prompt": "Open the add-to-cart modal for 'Pepperoni Classic' at 'Pizza Paradise'.",
        "actions": [
            {
                "url": "http://localhost:8006/restaurants?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Add 'Pepperoni Classic' to cart from 'Pizza Paradise'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Start a quick order from any restaurant.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Go to the checkout page.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Show me the next page of restaurants.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Show me the previous page of restaurants.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Submit a review with name 'Agente' and comment 'good'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Delete the review for the restaurant with name 'Bella Vista' where the author contains 'ria', the comment contains 'ood!', the rating is NOT '4.5', the cuisine does NOT contain 'Japanese', and the review_rating is NOT '4.5'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Empty my cart where the quantity is less than or equal to 8 and the price equals '14.99'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Set dropoff preference where quantity greater equal 2 and item equals 'Picanha' and price less equal 26.99 and restaurant equals 'Carnaval Grill' and delivery_preference equals 'Hand it to me'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Add an address where quantity greater equal 2 and item equals 'Picanha' and price less equal 26.99 and restaurant equals 'Carnaval Grill' and address equals '505 Cherry Circle, Fairview'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Place an order where address not contains '101 Elm Drive, Centerville' and phone not equals '+1-555-901-2345' and mode not contains 'delivery' and preferences not contains 'soy-free' and size not contains 'medium' and quantity less than '2' and price equals '14.3' and restaurant equals 'Tokyo Sushi House'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Edit the cart item 'Margherita Pizza' from Sushi Zen where the item does NOT contain 'Egg & Cheese Sandwich' and the restaurant is NOT 'Waffle Works'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Select a delivery priority that is 'normal' for an item with size that CONTAINS 'll', a quantity of at least 2, an item that CONTAINS 'eek', a price greater than 9.17, and a restaurant that CONTAINS 'Table'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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
        "url": "http://localhost:8006/?seed=1",
        "prompt": "Increase the quantity of 'Pepperoni Classic' to 2 at 'Pizza Paradise'.",
        "actions": [
            {
                "url": "http://localhost:8006/?seed=1",
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


def _normalize_field_name(raw_field: str) -> str:
    field = raw_field.strip().lower().replace(" ", "_")
    aliases = {
        "movie_name": "name",
        "film_name": "name",
    }
    return aliases.get(field, field)


def _parse_value_token(raw_value: str) -> Any:
    value = raw_value.strip().strip(".")
    if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _maybe_add_operator_criterion(criteria: dict[str, Any], field: str, operator: str, raw_value: str) -> None:
    criteria[_normalize_field_name(field)] = {
        "operator": operator,
        "value": _parse_value_token(raw_value),
    }


def _extract_event_criteria_from_prompt(prompt: str) -> dict[str, Any]:
    # Conservative parser: if prompt looks complex/ambiguous, return empty criteria.
    lowered = prompt.lower()
    tricky_markers = (" one of ", " or ", " either ", " directly ", " then ")
    if any(marker in lowered for marker in tricky_markers):
        return {}

    criteria: dict[str, Any] = {}

    not_equals_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+is\s+not\s+'([^']+)'",
        r"\b([a-zA-Z_ ]+?)\s+not\s+'([^']+)'",
    ]
    contains_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+contains\s+'([^']+)'",
    ]
    not_contains_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+does\s+not\s+contain\s+'([^']+)'",
        r"\b([a-zA-Z_ ]+?)\s+not\s+contain\s+'([^']+)'",
    ]
    equals_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+equals\s+'([^']+)'",
    ]
    less_equal_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+less\s+equal\s+'?([0-9]+(?:\.[0-9]+)?)'?",
        r"\b([a-zA-Z_ ]+?)\s+less\s+than\s+or\s+equal\s+to\s+'?([0-9]+(?:\.[0-9]+)?)'?",
    ]
    greater_equal_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+greater\s+equal\s+'?([0-9]+(?:\.[0-9]+)?)'?",
        r"\b([a-zA-Z_ ]+?)\s+greater\s+than\s+or\s+equal\s+to\s+'?([0-9]+(?:\.[0-9]+)?)'?",
    ]
    less_than_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+less\s+than\s+'?([0-9]+(?:\.[0-9]+)?)'?",
    ]
    greater_than_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+greater\s+than\s+'?([0-9]+(?:\.[0-9]+)?)'?",
    ]

    for pattern in not_contains_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "not_contains", value)

    for pattern in contains_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "contains", value)

    for pattern in not_equals_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "not_equals", value)

    for pattern in equals_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            criteria[_normalize_field_name(field)] = _parse_value_token(value)

    for pattern in less_equal_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "less_equal", value)

    for pattern in greater_equal_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "greater_equal", value)

    for pattern in less_than_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "less_than", value)

    for pattern in greater_than_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "greater_than", value)

    return criteria


def _build_raw_tests_from_actions(actions_data: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    raw_tests: dict[str, list[dict[str, Any]]] = {}
    for item in actions_data:
        use_case = str(item.get("use_case", "")).strip()
        if not use_case:
            continue
        prompt = str(item.get("prompt", ""))
        criteria = _extract_event_criteria_from_prompt(prompt)
        raw_tests[use_case] = [
            {
                "type": "CheckEventTest",
                "event_name": use_case,
                "event_criteria": criteria,
                "description": "Check if specific event was triggered",
            }
        ]
    return raw_tests


_RAW_TESTS: dict[str, list[dict[str, Any]]] = _build_raw_tests_from_actions(ACTIONS)
_TESTS: dict[str, list[BaseTaskTest]] = {uc: [BaseTaskTest.deserialize(p) for p in pl] for uc, pl in _RAW_TESTS.items()}


def _uc(use_case: str, prompt: str, actions: list[BaseAction]) -> Trajectory:
    return Trajectory(name=use_case, prompt=prompt, actions=actions, tests=_TESTS.get(use_case, []))


def _xp(expr: str) -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value=expr)


def _id(element_id: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=element_id)


SEARCH_DELIVERY_RESTAURANT = _uc(
    "SEARCH_DELIVERY_RESTAURANT",
    prompt="Search for restaurants named 'Bella Vista'.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__DELIVERY_SEARCH_QUERY__"),
        SendKeysIWAAction(keys="Enter"),
    ],
)

VIEW_DELIVERY_RESTAURANT = _uc(
    "VIEW_DELIVERY_RESTAURANT",
    prompt="View details for the restaurant named 'Bella Vista'.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__DELIVERY_SEARCH_QUERY__"),
        ClickAction(selector=_xp("(//*[@data-element-type='VIEW_DELIVERY_RESTAURANT'] | //*[@id='restaurant-card'] | //*[@id='restaurant-image'] | //*[@id='restaurant-name'])[1]")),
    ],
)

RESTAURANT_FILTER = _uc(
    "RESTAURANT_FILTER",
    prompt="Filter restaurants to show only Italian cuisine.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
        ClickAction(selector=_xp("//*[@id='search-filters']/div[3]/button[2]")),
        TypeAction(selector=_id("search-input"), text="__DELIVERY_SEARCH_QUERY__"),
        SendKeysIWAAction(keys="Enter"),
    ],
)

VIEW_ALL_RESTAURANTS = _uc(
    "VIEW_ALL_RESTAURANTS",
    prompt="Return to the full restaurant list.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
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
    prompt="Return to all restaurants after viewing 'Bella Vista'.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
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
    prompt="Open the add-to-cart modal for 'Pepperoni Classic' at 'Pizza Paradise'.",
    actions=[
        NavigateAction(url="http://localhost:8006/restaurants?seed=1"),
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
    prompt="Add 'Pepperoni Classic' to cart from 'Pizza Paradise'.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
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
        NavigateAction(url="http://localhost:8006/?seed=1"),
        ClickAction(
            selector=_xp(
                "(//*[@id='quick-order' or @id='quick-order-header' or contains(@id,'quick-order')] | //button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'quick order')] | //button[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'quick order')])[1]"
            )
        ),
    ],
)

OPEN_CHECKOUT_PAGE = _uc(
    "OPEN_CHECKOUT_PAGE",
    prompt="Go to the checkout page.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
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
    prompt="Show me the next page of restaurants.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
        ClickAction(
            selector=_xp(
                "(//*[@id='pagination-next'] | //button[@id='pagination-next'] | //button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')])[1]"
            )
        ),
    ],
)

RESTAURANT_PREV_PAGE = _uc(
    "RESTAURANT_PREV_PAGE",
    prompt="Show me the previous page of restaurants.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
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
    prompt="Submit a review with name 'Agente' and comment 'good'.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
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
    prompt="Delete the review for the restaurant with name 'Bella Vista' where the author contains 'ria', the comment contains 'ood!', the rating is NOT '4.5', the cuisine does NOT contain 'Japanese', and the review_rating is NOT '4.5'.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
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
    prompt="Empty my cart where the quantity is less than or equal to 8 and the price equals '14.99'.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
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
    prompt="Set dropoff preference where quantity greater equal 2 and item equals 'Picanha' and price less equal 26.99 and restaurant equals 'Carnaval Grill' and delivery_preference equals 'Hand it to me'.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
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
    prompt="Add an address where quantity greater equal 2 and item equals 'Picanha' and price less equal 26.99 and restaurant equals 'Carnaval Grill' and address equals '505 Cherry Circle, Fairview'.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
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
    prompt="Place an order where address not contains '101 Elm Drive, Centerville' and phone not equals '+1-555-901-2345' and mode not contains 'delivery' and preferences not contains 'soy-free' and size not contains 'medium' and quantity less than '2' and price equals '14.3' and restaurant equals 'Tokyo Sushi House'.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
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
    prompt="Edit the cart item 'Margherita Pizza' from Sushi Zen where the item does NOT contain 'Egg & Cheese Sandwich' and the restaurant is NOT 'Waffle Works'.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
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
    prompt="Select a delivery priority that is 'normal' for an item with size that CONTAINS 'll', a quantity of at least 2, an item that CONTAINS 'eek', a price greater than 9.17, and a restaurant that CONTAINS 'Table'.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
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
    prompt="Increase the quantity of 'Pepperoni Classic' to 2 at 'Pizza Paradise'.",
    actions=[
        NavigateAction(url="http://localhost:8006/?seed=1"),
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
