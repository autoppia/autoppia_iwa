from __future__ import annotations

PROJECT_NUMBER = 3
WEB_PROJECT_ID = "autozone"

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
        "url": "http://localhost:8002/?seed=18",
        "prompt": "Show me details for the Premium Drone",
        "actions": [
            {
                "url": "http://localhost:8002/?seed=18",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8002/?seed=18",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "Premium Drone",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Premium Drone",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "VIEW_DETAIL",
        "has_success": True,
    },
    {
        "url": "http://localhost:8002/?seed=18",
        "prompt": "Expand the Explore further section for the Premium Drone page.",
        "actions": [
            {
                "url": "http://localhost:8002/?seed=18",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8002/?seed=18",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "Premium Drone",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Premium Drone",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='toggle-btn' or @id='toggle-button' or @id='switch-btn' or @id='toggle-control' or @id='toggle-action' or @id='switch-control' or @id='toggle-state' or @id='toggle-option' or @id='toggle-choice' or @id='toggle']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='toggle-btn' or @id='toggle-button' or @id='switch-btn' or @id='toggle-control' or @id='toggle-action' or @id='switch-control' or @id='toggle-state' or @id='toggle-option' or @id='toggle-choice' or @id='toggle']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "DETAILS_TOGGLE",
        "has_success": True,
    },
    {
        "url": "http://localhost:8002/?seed=15",
        "prompt": "Search for products that contain 'Premium Drone'",
        "actions": [
            {
                "url": "http://localhost:8002/?seed=15",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8002/?seed=15",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "Premium Drone",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Premium Drone",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "SEARCH_PRODUCT",
        "has_success": True,
    },
    {
        "url": "http://localhost:8002/?seed=15",
        "prompt": "Filter results to Technology products.",
        "actions": [
            {
                "url": "http://localhost:8002/?seed=15",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8002/?seed=15",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='browse-all-button' or @id='browse-all-btn' or @id='browse-btn' or @id='browse-button' or @id='browse-all-items-btn' or @id='browse-items-btn' or @id='browse-catalog-btn' or @id='browse-list-btn' or @id='open-browse-btn' or @id='browse-more-btn']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='browse-all-button' or @id='browse-all-btn' or @id='browse-btn' or @id='browse-button' or @id='browse-all-items-btn' or @id='browse-items-btn' or @id='browse-catalog-btn' or @id='browse-list-btn' or @id='open-browse-btn' or @id='browse-more-btn']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='category-link' or @id='cat-link' or @id='category-btn' or @id='cat-btn' or @id='category-action' or @id='cat-action' or @id='browse-category' or @id='view-category' or @id='goto-category' or @id='category-nav'][contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'technology')])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='category-link' or @id='cat-link' or @id='category-btn' or @id='cat-btn' or @id='category-action' or @id='cat-action' or @id='browse-category' or @id='view-category' or @id='goto-category' or @id='category-nav'][contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'technology')])[1]",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "CATEGORY_FILTER",
        "has_success": True,
    },
    {
        "url": "http://localhost:8002/?seed=15",
        "prompt": "Add the Premium Drone to my cart.",
        "actions": [
            {
                "url": "http://localhost:8002/?seed=15",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8002/?seed=15",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "Premium Drone",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Premium Drone",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='add-cart-btn' or @id='cart-add' or @id='add-basket' or @id='add-to-basket' or @id='cart-action' or @id='basket-action' or @id='add-item' or @id='cart-item-add' or @id='basket-add-item' or @id='add-product'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='add-cart-btn' or @id='cart-add' or @id='add-basket' or @id='add-to-basket' or @id='cart-action' or @id='basket-action' or @id='add-item' or @id='cart-item-add' or @id='basket-add-item' or @id='add-product'])[1]",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "ADD_TO_CART",
        "has_success": True,
    },
    {
        "url": "http://localhost:8002/?seed=15",
        "prompt": "Add the Premium Drone to my wishlist.",
        "actions": [
            {
                "url": "http://localhost:8002/?seed=15",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8002/?seed=15",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "Premium Drone",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Premium Drone",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "SendKeysAction",
                "keys": [
                    "Enter",
                ],
                "attributes": {
                    "keys": [
                        "Enter",
                    ],
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='wishlist-btn' or @id='add-wishlist' or @id='save-later' or @id='wishlist-add' or @id='favorite-btn' or @id='save-item' or @id='add-favorite' or @id='wishlist-action' or @id='save-product' or @id='favorite-action']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='wishlist-btn' or @id='add-wishlist' or @id='save-later' or @id='wishlist-add' or @id='favorite-btn' or @id='save-item' or @id='add-favorite' or @id='wishlist-action' or @id='save-product' or @id='favorite-action']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "ADD_TO_WISHLIST",
        "has_success": True,
    },
    {
        "url": "http://localhost:8002/?seed=15",
        "prompt": "Open my wishlist page.",
        "actions": [
            {
                "url": "http://localhost:8002/?seed=15",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8002/?seed=15",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='view-wishlist-button' or @id='wishlist-btn' or @id='wishlist-link' or @id='go-wishlist' or @id='view-wishlist-btn' or @id='wishlist-button' or @id='show-wishlist-btn' or @id='open-wishlist-btn' or @id='wishlist-view-btn' or @id='all-wishlist-btn' or @id='save-later']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='view-wishlist-button' or @id='wishlist-btn' or @id='wishlist-link' or @id='go-wishlist' or @id='view-wishlist-btn' or @id='wishlist-button' or @id='show-wishlist-btn' or @id='open-wishlist-btn' or @id='wishlist-view-btn' or @id='all-wishlist-btn' or @id='save-later']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "VIEW_WISHLIST",
        "has_success": True,
    },
    {
        "url": "http://localhost:8002/?seed=15",
        "prompt": "Open my cart page.",
        "actions": [
            {
                "url": "http://localhost:8002/?seed=15",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8002/?seed=15",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='cart-btn' or @id='shopping-cart' or @id='basket-btn' or @id='cart-action' or @id='view-cart' or @id='goto-cart' or @id='cart-link' or @id='basket-link' or @id='cart-icon' or @id='shopping-basket']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='cart-btn' or @id='shopping-cart' or @id='basket-btn' or @id='cart-action' or @id='view-cart' or @id='goto-cart' or @id='cart-link' or @id='basket-link' or @id='cart-icon' or @id='shopping-basket']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "VIEW_CART",
        "has_success": True,
    },
    {
        "url": "http://localhost:8002/?seed=15",
        "prompt": "On Premium Drone details, change quantity from 1 to 2.",
        "actions": [
            {
                "url": "http://localhost:8002/?seed=15",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8002/?seed=15",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "Premium Drone",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Premium Drone",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='qty-input' or @id='quantity-field' or @id='qty-field' or @id='amount-input' or @id='qty-box' or @id='quantity-box' or @id='qty-select' or @id='quantity-select' or @id='item-qty' or @id='product-qty']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='qty-input' or @id='quantity-field' or @id='qty-field' or @id='amount-input' or @id='qty-box' or @id='quantity-box' or @id='qty-select' or @id='quantity-select' or @id='item-qty' or @id='product-qty']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "SendKeysAction",
                "keys": [
                    "ArrowDown",
                ],
                "attributes": {
                    "keys": [
                        "ArrowDown",
                    ],
                },
            },
            {
                "type": "SendKeysAction",
                "keys": [
                    "Enter",
                ],
                "attributes": {
                    "keys": [
                        "Enter",
                    ],
                },
            },
        ],
        "use_case": "QUANTITY_CHANGED",
        "has_success": True,
    },
    {
        "url": "http://localhost:8002/?seed=15",
        "prompt": "From cart, proceed to checkout with the Premium Drone.",
        "actions": [
            {
                "url": "http://localhost:8002/?seed=15",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8002/?seed=15",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "Premium Drone",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Premium Drone",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='add-cart-btn' or @id='cart-add' or @id='add-basket' or @id='add-to-basket' or @id='cart-action' or @id='basket-action' or @id='add-item' or @id='cart-item-add' or @id='basket-add-item' or @id='add-product'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='add-cart-btn' or @id='cart-add' or @id='add-basket' or @id='add-to-basket' or @id='cart-action' or @id='basket-action' or @id='add-item' or @id='cart-item-add' or @id='basket-add-item' or @id='add-product'])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='checkout-btn' or @id='proceed-checkout' or @id='goto-checkout' or @id='checkout-action' or @id='checkout-now' or @id='proceed-btn' or @id='finalize-order' or @id='complete-order' or @id='checkout-link' or @id='order-btn']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='checkout-btn' or @id='proceed-checkout' or @id='goto-checkout' or @id='checkout-action' or @id='checkout-now' or @id='proceed-btn' or @id='finalize-order' or @id='complete-order' or @id='checkout-link' or @id='order-btn']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "PROCEED_TO_CHECKOUT",
        "has_success": True,
    },
    {
        "url": "http://localhost:8002/?seed=15",
        "prompt": "Start checkout from the Premium Drone detail page.",
        "actions": [
            {
                "url": "http://localhost:8002/?seed=15",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8002/?seed=15",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "Premium Drone",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Premium Drone",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='order-now' or @id='checkout-btn' or @id='proceed-checkout' or @id='goto-checkout' or @id='checkout-action' or @id='checkout-now' or @id='proceed-btn' or @id='finalize-order' or @id='complete-order' or @id='checkout-link' or @id='order-btn']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='order-now' or @id='checkout-btn' or @id='proceed-checkout' or @id='goto-checkout' or @id='checkout-action' or @id='checkout-now' or @id='proceed-btn' or @id='finalize-order' or @id='complete-order' or @id='checkout-link' or @id='order-btn']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "CHECKOUT_STARTED",
        "has_success": True,
    },
    {
        "url": "http://localhost:8002/?seed=15",
        "prompt": "Share the Premium Drone product page.",
        "actions": [
            {
                "url": "http://localhost:8002/?seed=15",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8002/?seed=15",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "Premium Drone",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Premium Drone",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='share-btn' or @id='share-button' or @id='share-action' or @id='share-link' or @id='share-control' or @id='share-item' or @id='share-product' or @id='share-page' or @id='share-trigger' or @id='share']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='share-btn' or @id='share-button' or @id='share-action' or @id='share-link' or @id='share-control' or @id='share-item' or @id='share-product' or @id='share-page' or @id='share-trigger' or @id='share']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "SHARE_PRODUCT",
        "has_success": True,
    },
    {
        "url": "http://localhost:8002/?seed=15",
        "prompt": "Scroll right in the Featured Products carousel.",
        "actions": [
            {
                "url": "http://localhost:8002/?seed=15",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8002/?seed=15",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='carousel-right-btn' or @id='carousel-next' or @id='carousel-forward' or @id='carousel-right' or @id='carousel-next-btn' or @id='carousel-arrow-right' or @id='carousel-control-right' or @id='carousel-nav-right' or @id='carousel-right-control' or @id='carousel-right-arrow']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='carousel-right-btn' or @id='carousel-next' or @id='carousel-forward' or @id='carousel-right' or @id='carousel-next-btn' or @id='carousel-arrow-right' or @id='carousel-control-right' or @id='carousel-nav-right' or @id='carousel-right-control' or @id='carousel-right-arrow']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "CAROUSEL_SCROLL",
        "has_success": True,
    },
    {
        "url": "http://localhost:8002/?seed=15",
        "prompt": "Complete an order for the Premium Drone.",
        "actions": [
            {
                "url": "http://localhost:8002/?seed=15",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8002/?seed=15",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "Premium Drone",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Premium Drone",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='add-cart-btn' or @id='cart-add' or @id='add-basket' or @id='add-to-basket' or @id='cart-action' or @id='basket-action' or @id='add-item' or @id='cart-item-add' or @id='basket-add-item' or @id='add-product'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='add-cart-btn' or @id='cart-add' or @id='add-basket' or @id='add-to-basket' or @id='cart-action' or @id='basket-action' or @id='add-item' or @id='cart-item-add' or @id='basket-add-item' or @id='add-product'])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='checkout-btn' or @id='proceed-checkout' or @id='goto-checkout' or @id='checkout-action' or @id='checkout-now' or @id='proceed-btn' or @id='finalize-order' or @id='complete-order' or @id='checkout-link' or @id='order-btn']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='checkout-btn' or @id='proceed-checkout' or @id='goto-checkout' or @id='checkout-action' or @id='checkout-now' or @id='proceed-btn' or @id='finalize-order' or @id='complete-order' or @id='checkout-link' or @id='order-btn']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='finalize-order-button' or @id='place-order-btn' or @id='complete-order-button' or @id='confirm-order-btn' or @id='submit-order-button' or @id='finish-order-btn' or @id='order-now-button' or @id='checkout-button' or @id='place-order-button' or @id='confirm-purchase-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='finalize-order-button' or @id='place-order-btn' or @id='complete-order-button' or @id='confirm-order-btn' or @id='submit-order-button' or @id='finish-order-btn' or @id='order-now-button' or @id='checkout-button' or @id='place-order-button' or @id='confirm-purchase-button']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "ORDER_COMPLETED",
        "has_success": True,
    },
]


# CheckEventTest payloads aligned with autozone_tasks.json (per use_case.name).
_RAW_TESTS: dict[str, list[dict]] = {
    "VIEW_DETAIL": [
        {
            "type": "CheckEventTest",
            "event_name": "VIEW_DETAIL",
            "event_criteria": {"rating": {"operator": "less_equal", "value": 4.3}, "category": {"operator": "contains", "value": "en"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "DETAILS_TOGGLE": [
        {
            "type": "CheckEventTest",
            "event_name": "DETAILS_TOGGLE",
            "event_criteria": {"rating": 4.4, "category": {"operator": "contains", "value": "Home"}, "title": "Drybar Buttercup Hair Dryer"},
            "description": "Check if specific event was triggered",
        }
    ],
    "SHARE_PRODUCT": [
        {"type": "CheckEventTest", "event_name": "SHARE_PRODUCT", "event_criteria": {"category": {"operator": "not_equals", "value": "Home"}}, "description": "Check if specific event was triggered"}
    ],
    "SEARCH_PRODUCT": [{"type": "CheckEventTest", "event_name": "SEARCH_PRODUCT", "event_criteria": {"query": "Ninja Foodi 8-in-1"}, "description": "Check if specific event was triggered"}],
    "CATEGORY_FILTER": [{"type": "CheckEventTest", "event_name": "CATEGORY_FILTER", "event_criteria": {"category": "electronics"}, "description": "Check if specific event was triggered"}],
    "ADD_TO_CART": [
        {
            "type": "CheckEventTest",
            "event_name": "ADD_TO_CART",
            "event_criteria": {"price": {"operator": "greater_equal", "value": 99.99}, "brand": {"operator": "not_equals", "value": "Arlo"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "ADD_TO_WISHLIST": [
        {
            "type": "CheckEventTest",
            "event_name": "ADD_TO_WISHLIST",
            "event_criteria": {"brand": {"operator": "not_contains", "value": "NinjaXYZ184"}, "rating": 4.6, "price": {"operator": "not_equals", "value": 92.0}},
            "description": "Check if specific event was triggered",
        }
    ],
    "VIEW_CART": [{"type": "CheckEventTest", "event_name": "VIEW_CART", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "VIEW_WISHLIST": [{"type": "CheckEventTest", "event_name": "VIEW_WISHLIST", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "CAROUSEL_SCROLL": [
        {
            "type": "CheckEventTest",
            "event_name": "CAROUSEL_SCROLL",
            "event_criteria": {"title": "Top Sellers In Fitness", "direction": {"operator": "not_equals", "value": "RIGHT"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "QUANTITY_CHANGED": [
        {
            "type": "CheckEventTest",
            "event_name": "QUANTITY_CHANGED",
            "event_criteria": {"title": "Instant Pot Duo Plus", "new_quantity": {"operator": "less_equal", "value": 6}},
            "description": "Check if specific event was triggered",
        }
    ],
    "PROCEED_TO_CHECKOUT": [{"type": "CheckEventTest", "event_name": "PROCEED_TO_CHECKOUT", "event_criteria": {"total_amount": 189.99}, "description": "Check if specific event was triggered"}],
    "CHECKOUT_STARTED": [
        {
            "type": "CheckEventTest",
            "event_name": "CHECKOUT_STARTED",
            "event_criteria": {"total_amount": {"operator": "less_equal", "value": 349.0}},
            "description": "Check if specific event was triggered",
        }
    ],
    "ORDER_COMPLETED": [
        {"type": "CheckEventTest", "event_name": "ORDER_COMPLETED", "event_criteria": {"title": {"operator": "contains", "value": "ple"}}, "description": "Check if specific event was triggered"}
    ],
}

_TESTS: dict[str, list[BaseTaskTest]] = {uc: [BaseTaskTest.deserialize(p) for p in pl] for uc, pl in _RAW_TESTS.items()}


def _uc(use_case: str, prompt: str, actions: list[BaseAction]) -> Trajectory:
    return Trajectory(name=use_case, prompt=prompt, actions=actions, tests=_TESTS[use_case])


def _xp(expr: str) -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value=expr)


def _id(element_id: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=element_id)


VIEW_DETAIL = _uc(
    "VIEW_DETAIL",
    prompt="Show details for a product with a rating of 4.3 or less and a category that contains 'en'",
    actions=[
        NavigateAction(url="http://localhost:8002/?seed=18"),
        ClickAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            ),
            text="Premium Drone",
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]"
            )
        ),
    ],
)

DETAILS_TOGGLE = _uc(
    "DETAILS_TOGGLE",
    prompt="Expand the details section for the product with title 'Drybar Buttercup Hair Dryer' that has a rating of 4.4 and belongs to the category that contains 'Home'.",
    actions=[
        NavigateAction(url="http://localhost:8002/?seed=18"),
        ClickAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            ),
            text="Premium Drone",
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='toggle-btn' or @id='toggle-button' or @id='switch-btn' or @id='toggle-control' or @id='toggle-action' or @id='switch-control' or @id='toggle-state' or @id='toggle-option' or @id='toggle-choice' or @id='toggle']"
            )
        ),
    ],
)

SEARCH_PRODUCT = _uc(
    "SEARCH_PRODUCT",
    prompt="Search for products with query equals 'Ninja Foodi 8-in-1'",
    actions=[
        NavigateAction(url="http://localhost:8002/?seed=15"),
        ClickAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            ),
            text="Premium Drone",
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']"
            )
        ),
    ],
)

CATEGORY_FILTER = _uc(
    "CATEGORY_FILTER",
    prompt="Filter to show only products in the category 'electronics'.",
    actions=[
        NavigateAction(url="http://localhost:8002/?seed=15"),
        ClickAction(
            selector=_xp(
                "//*[@id='browse-all-button' or @id='browse-all-btn' or @id='browse-btn' or @id='browse-button' or @id='browse-all-items-btn' or @id='browse-items-btn' or @id='browse-catalog-btn' or @id='browse-list-btn' or @id='open-browse-btn' or @id='browse-more-btn']"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='category-link' or @id='cat-link' or @id='category-btn' or @id='cat-btn' or @id='category-action' or @id='cat-action' or @id='browse-category' or @id='view-category' or @id='goto-category' or @id='category-nav'][contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'technology')])[1]"
            )
        ),
    ],
)

ADD_TO_CART = _uc(
    "ADD_TO_CART",
    prompt="Add 1 item to cart where the price is GREATER THAN or EQUAL to '99.99' and the brand is NOT 'Arlo'",
    actions=[
        NavigateAction(url="http://localhost:8002/?seed=15"),
        ClickAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            ),
            text="Premium Drone",
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='add-cart-btn' or @id='cart-add' or @id='add-basket' or @id='add-to-basket' or @id='cart-action' or @id='basket-action' or @id='add-item' or @id='cart-item-add' or @id='basket-add-item' or @id='add-product'])[1]"
            )
        ),
    ],
)

ADD_TO_WISHLIST = _uc(
    "ADD_TO_WISHLIST",
    prompt="Add to wishlist an item where the brand does NOT CONTAIN 'NinjaXYZ184', the rating equals '4.6', and the price is NOT '92.0'",
    actions=[
        NavigateAction(url="http://localhost:8002/?seed=15"),
        ClickAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            ),
            text="Premium Drone",
        ),
        SendKeysIWAAction(keys="Enter"),
        ClickAction(
            selector=_xp(
                "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='wishlist-btn' or @id='add-wishlist' or @id='save-later' or @id='wishlist-add' or @id='favorite-btn' or @id='save-item' or @id='add-favorite' or @id='wishlist-action' or @id='save-product' or @id='favorite-action']"
            )
        ),
    ],
)

VIEW_WISHLIST = _uc(
    "VIEW_WISHLIST",
    prompt="Open my wishlist from the home wishlist preview.",
    actions=[
        NavigateAction(url="http://localhost:8002/?seed=15"),
        ClickAction(
            selector=_xp(
                "//*[@id='view-wishlist-button' or @id='wishlist-btn' or @id='wishlist-link' or @id='go-wishlist' or @id='view-wishlist-btn' or @id='wishlist-button' or @id='show-wishlist-btn' or @id='open-wishlist-btn' or @id='wishlist-view-btn' or @id='all-wishlist-btn' or @id='save-later']"
            )
        ),
    ],
)

VIEW_CART = _uc(
    "VIEW_CART",
    prompt="Show me the contents of my shopping cart",
    actions=[
        NavigateAction(url="http://localhost:8002/?seed=15"),
        ClickAction(
            selector=_xp(
                "//*[@id='cart-btn' or @id='shopping-cart' or @id='basket-btn' or @id='cart-action' or @id='view-cart' or @id='goto-cart' or @id='cart-link' or @id='basket-link' or @id='cart-icon' or @id='shopping-basket']"
            )
        ),
    ],
)

QUANTITY_CHANGED = _uc(
    "QUANTITY_CHANGED",
    prompt="Update quantity of item with title 'Instant Pot Duo Plus' in my cart to 6",
    actions=[
        NavigateAction(url="http://localhost:8002/?seed=15"),
        ClickAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            ),
            text="Premium Drone",
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='qty-input' or @id='quantity-field' or @id='qty-field' or @id='amount-input' or @id='qty-box' or @id='quantity-box' or @id='qty-select' or @id='quantity-select' or @id='item-qty' or @id='product-qty']"
            )
        ),
        SendKeysIWAAction(keys="ArrowDown"),
        SendKeysIWAAction(keys="Enter"),
    ],
)

PROCEED_TO_CHECKOUT = _uc(
    "PROCEED_TO_CHECKOUT",
    prompt="Proceed to checkout with a total amount of '189.99'",
    actions=[
        NavigateAction(url="http://localhost:8002/?seed=15"),
        ClickAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            ),
            text="Premium Drone",
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='add-cart-btn' or @id='cart-add' or @id='add-basket' or @id='add-to-basket' or @id='cart-action' or @id='basket-action' or @id='add-item' or @id='cart-item-add' or @id='basket-add-item' or @id='add-product'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='checkout-btn' or @id='proceed-checkout' or @id='goto-checkout' or @id='checkout-action' or @id='checkout-now' or @id='proceed-btn' or @id='finalize-order' or @id='complete-order' or @id='checkout-link' or @id='order-btn']"
            )
        ),
    ],
)

CHECKOUT_STARTED = _uc(
    "CHECKOUT_STARTED",
    prompt="Click on Buy now to initiate the checkout process with a total amount less equal to '349.0'.",
    actions=[
        NavigateAction(url="http://localhost:8002/?seed=15"),
        ClickAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            ),
            text="Premium Drone",
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='order-now' or @id='checkout-btn' or @id='proceed-checkout' or @id='goto-checkout' or @id='checkout-action' or @id='checkout-now' or @id='proceed-btn' or @id='finalize-order' or @id='complete-order' or @id='checkout-link' or @id='order-btn']"
            )
        ),
    ],
)

SHARE_PRODUCT = _uc(
    "SHARE_PRODUCT",
    prompt="Share the product link for an item where the category is NOT 'Home'.",
    actions=[
        NavigateAction(url="http://localhost:8002/?seed=15"),
        ClickAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            ),
            text="Premium Drone",
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='share-btn' or @id='share-button' or @id='share-action' or @id='share-link' or @id='share-control' or @id='share-item' or @id='share-product' or @id='share-page' or @id='share-trigger' or @id='share']"
            )
        ),
    ],
)

CAROUSEL_SCROLL = _uc(
    "CAROUSEL_SCROLL",
    prompt="Scroll through the carousel titled 'Top Sellers In Fitness' where the direction is NOT 'RIGHT'",
    actions=[
        NavigateAction(url="http://localhost:8002/?seed=15"),
        ClickAction(
            selector=_xp(
                "//*[@id='carousel-right-btn' or @id='carousel-next' or @id='carousel-forward' or @id='carousel-right' or @id='carousel-next-btn' or @id='carousel-arrow-right' or @id='carousel-control-right' or @id='carousel-nav-right' or @id='carousel-right-control' or @id='carousel-right-arrow']"
            )
        ),
    ],
)

ORDER_COMPLETED = _uc(
    "ORDER_COMPLETED",
    prompt="Complete my order with a title that CONTAINS 'ple'",
    actions=[
        NavigateAction(url="http://localhost:8002/?seed=15"),
        ClickAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//*[@id='type-to-search' or @id='search-input' or @id='query-box' or @id='filter-input' or @id='product-search' or @id='item-search' or @id='search-field' or @id='lookup-input' or @id='find-input' or @id='search-box']"
            ),
            text="Premium Drone",
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='execute-search' or @id='search-btn' or @id='submit-search' or @id='go-search' or @id='search-action' or @id='find-btn' or @id='query-btn' or @id='search-submit' or @id='do-search' or @id='run-search']"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='view-details-btn' or @id='details-btn' or @id='view-btn' or @id='open-details' or @id='view-details' or @id='details-action' or @id='product-details-btn' or @id='item-details-btn' or @id='more-details-btn' or @id='details-link'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='add-cart-btn' or @id='cart-add' or @id='add-basket' or @id='add-to-basket' or @id='cart-action' or @id='basket-action' or @id='add-item' or @id='cart-item-add' or @id='basket-add-item' or @id='add-product'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='checkout-btn' or @id='proceed-checkout' or @id='goto-checkout' or @id='checkout-action' or @id='checkout-now' or @id='proceed-btn' or @id='finalize-order' or @id='complete-order' or @id='checkout-link' or @id='order-btn']"
            )
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='finalize-order-button' or @id='place-order-btn' or @id='complete-order-button' or @id='confirm-order-btn' or @id='submit-order-button' or @id='finish-order-btn' or @id='order-now-button' or @id='checkout-button' or @id='place-order-button' or @id='confirm-purchase-button']"
            )
        ),
    ],
)


def load_autozone_use_case_completion_flows() -> dict[str, Trajectory]:
    return {
        "VIEW_DETAIL": VIEW_DETAIL,
        "DETAILS_TOGGLE": DETAILS_TOGGLE,
        "SEARCH_PRODUCT": SEARCH_PRODUCT,
        "CATEGORY_FILTER": CATEGORY_FILTER,
        "ADD_TO_CART": ADD_TO_CART,
        "ADD_TO_WISHLIST": ADD_TO_WISHLIST,
        "VIEW_WISHLIST": VIEW_WISHLIST,
        "VIEW_CART": VIEW_CART,
        "QUANTITY_CHANGED": QUANTITY_CHANGED,
        "PROCEED_TO_CHECKOUT": PROCEED_TO_CHECKOUT,
        "CHECKOUT_STARTED": CHECKOUT_STARTED,
        "SHARE_PRODUCT": SHARE_PRODUCT,
        "CAROUSEL_SCROLL": CAROUSEL_SCROLL,
        "ORDER_COMPLETED": ORDER_COMPLETED,
    }
