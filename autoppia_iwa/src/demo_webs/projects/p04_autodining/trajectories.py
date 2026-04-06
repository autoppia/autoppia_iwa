from __future__ import annotations

PROJECT_NUMBER = 4
WEB_PROJECT_ID = "autodining"

from autoppia_iwa.src.data_generation.tests.classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.classes import Trajectory
from autoppia_iwa.src.execution.actions.actions import (
    ClickAction,
    NavigateAction,
    TypeAction,
)
from autoppia_iwa.src.execution.actions.base import BaseAction, Selector, SelectorType

ACTIONS = [
    {
        "url": "http://localhost:8003/?seed=880",
        "prompt": "Show me details for 'Thai Garden'",
        "actions": [
            {
                "url": "http://localhost:8003/?seed=880",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/?seed=880",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "TypeAction",
                "text": "Thai Garden",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Thai Garden",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//input[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view_details_button' or @id='dining-view-details-button' or @id='resto-view-details-button' or @id='view-details-btn' or @id='dining-view-details-btn' or @id='resto-view-details-btn' or @id='view-details-action'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='view_details_button' or @id='dining-view-details-button' or @id='resto-view-details-button' or @id='view-details-btn' or @id='dining-view-details-btn' or @id='resto-view-details-btn' or @id='view-details-action'])[1]",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "VIEW_RESTAURANT",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/restaurant/7?seed=175",
        "prompt": "Show the full menu for 'Thai Garden' for 2 people for dinner on July 18.",
        "actions": [
            {
                "url": "http://localhost:8003/restaurant/7?seed=175",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/restaurant/7?seed=175",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='menu-toggle-button' or @id='dining-menu-toggle' or @id='resto-menu-toggle' or @id='menu-expand-button' or @id='dining-menu-expand' or @id='resto-menu-expand' or @id='menu-collapse-button' or @id='dining-menu-collapse' or @id='resto-menu-collapse' or @id='menu-view-toggle'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='menu-toggle-button' or @id='dining-menu-toggle' or @id='resto-menu-toggle' or @id='menu-expand-button' or @id='dining-menu-expand' or @id='resto-menu-expand' or @id='menu-collapse-button' or @id='dining-menu-collapse' or @id='resto-menu-collapse' or @id='menu-view-toggle'])[1]",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "VIEW_FULL_MENU",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/restaurant/7?seed=621",
        "prompt": "Hide the menu for 'Thai Garden'.",
        "actions": [
            {
                "url": "http://localhost:8003/restaurant/7?seed=621",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/restaurant/7?seed=621",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='menu-toggle-button' or @id='dining-menu-toggle' or @id='resto-menu-toggle' or @id='menu-expand-button' or @id='dining-menu-expand' or @id='resto-menu-expand' or @id='menu-collapse-button' or @id='dining-menu-collapse' or @id='resto-menu-collapse' or @id='menu-view-toggle'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='menu-toggle-button' or @id='dining-menu-toggle' or @id='resto-menu-toggle' or @id='menu-expand-button' or @id='dining-menu-expand' or @id='resto-menu-expand' or @id='menu-collapse-button' or @id='dining-menu-collapse' or @id='resto-menu-collapse' or @id='menu-view-toggle'])[1]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='menu-toggle-button' or @id='dining-menu-toggle' or @id='resto-menu-toggle' or @id='menu-expand-button' or @id='dining-menu-expand' or @id='resto-menu-expand' or @id='menu-collapse-button' or @id='dining-menu-collapse' or @id='resto-menu-collapse' or @id='menu-view-toggle'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='menu-toggle-button' or @id='dining-menu-toggle' or @id='resto-menu-toggle' or @id='menu-expand-button' or @id='dining-menu-expand' or @id='resto-menu-expand' or @id='menu-collapse-button' or @id='dining-menu-collapse' or @id='resto-menu-collapse' or @id='menu-view-toggle'])[1]",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "COLLAPSE_MENU",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/?seed=854",
        "prompt": "Open the date selector and select the date '2026-02-23'.",
        "actions": [
            {
                "url": "http://localhost:8003/?seed=854",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/?seed=854",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='date_picker' or @id='date-picker' or @id='date-selector' or @id='date-input' or @id='booking-date' or @id='reservation-date' or @id='calendar-trigger' or @id='date-trigger' or @id='checkin-date' or @id='date-field']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='date_picker' or @id='date-picker' or @id='date-selector' or @id='date-input' or @id='booking-date' or @id='reservation-date' or @id='calendar-trigger' or @id='date-trigger' or @id='checkin-date' or @id='date-field']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//button[@aria-label='Go to previous month' or @aria-label='Previous month'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//button[@aria-label='Go to previous month' or @aria-label='Previous month'])[1]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//button[@aria-label='Go to previous month' or @aria-label='Previous month'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//button[@aria-label='Go to previous month' or @aria-label='Previous month'])[1]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//button[normalize-space()='23' and not(@disabled)])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//button[normalize-space()='23' and not(@disabled)])[1]",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "DATE_DROPDOWN_OPENED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/?seed=321",
        "prompt": "Open the time dropdown and select the time equals '2:30 PM'.",
        "actions": [
            {
                "url": "http://localhost:8003/?seed=321",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/?seed=321",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='time_picker' or @id='time-picker' or @id='time-selector' or @id='time-input' or @id='booking-time' or @id='reservation-time' or @id='time-trigger' or @id='checkin-time' or @id='time-field']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='time_picker' or @id='time-picker' or @id='time-selector' or @id='time-input' or @id='booking-time' or @id='reservation-time' or @id='time-trigger' or @id='checkin-time' or @id='time-field']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//button[normalize-space()='2:30 PM'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//button[normalize-space()='2:30 PM'])[1]",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "TIME_DROPDOWN_OPENED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/?seed=654",
        "prompt": "Open the guest selector dropdown and select people equals 4.",
        "actions": [
            {
                "url": "http://localhost:8003/?seed=654",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/?seed=654",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='people_picker' or @id='people-picker' or @id='guest-picker' or @id='guests-picker' or @id='people-selector' or @id='guest-selector' or @id='booking-people' or @id='reservation-people' or @id='people-input' or @id='guests-input']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='people_picker' or @id='people-picker' or @id='guest-picker' or @id='guests-picker' or @id='people-selector' or @id='guest-selector' or @id='booking-people' or @id='reservation-people' or @id='people-input' or @id='guests-input']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//button[contains(normalize-space(), '4') and (contains(normalize-space(), 'Guest') or contains(normalize-space(), 'Guests'))])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//button[contains(normalize-space(), '4') and (contains(normalize-space(), 'Guest') or contains(normalize-space(), 'Guests'))])[1]",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "PEOPLE_DROPDOWN_OPENED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/?seed=499",
        "prompt": "Search for 'Thai Garden'",
        "actions": [
            {
                "url": "http://localhost:8003/?seed=499",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/?seed=499",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "TypeAction",
                "text": "Thai Garden",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Thai Garden",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//input[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "SEARCH_RESTAURANT",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/?seed=94",
        "prompt": "Scroll in the direction 'right' where section equals 'Featured Products'.",
        "actions": [
            {
                "url": "http://localhost:8003/?seed=94",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/?seed=94",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@data-testid='scroll-right-1' or @id='scroll-right-button' or @id='scroll-right' or @id='scroll-right-btn' or @id='carousel-right' or @id='carousel-right-button' or @id='carousel-right-btn' or @id='next-button' or @id='next-slide' or @id='right-arrow'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@data-testid='scroll-right-1' or @id='scroll-right-button' or @id='scroll-right' or @id='scroll-right-btn' or @id='carousel-right' or @id='carousel-right-button' or @id='carousel-right-btn' or @id='next-button' or @id='next-slide' or @id='right-arrow'])[1]",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "SCROLL_VIEW",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/?seed=404",
        "prompt": "I'd like to book a table at the restaurant which name 'Thai Garden' for 2 people on 2026-04-03 at 12:00 PM.",
        "actions": [
            {
                "url": "http://localhost:8003/?seed=404",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/?seed=404",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "TypeAction",
                "text": "Thai Garden",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Thai Garden",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//input[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[normalize-space()='Thai Garden'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[normalize-space()='Thai Garden'])[1]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='people_picker' or @id='dining-people-picker' or @id='resto-people-picker' or @id='guests-picker' or @id='dining-guests-picker' or @id='resto-guests-picker' or @id='party-size-picker' or @id='dining-party-size-picker' or @id='resto-party-size-picker' or @id='people-selector']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='people_picker' or @id='dining-people-picker' or @id='resto-people-picker' or @id='guests-picker' or @id='dining-guests-picker' or @id='resto-guests-picker' or @id='party-size-picker' or @id='dining-party-size-picker' or @id='resto-party-size-picker' or @id='people-selector']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//button[contains(normalize-space(), '2') and (contains(normalize-space(), 'Guest') or contains(normalize-space(), 'Guests'))])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//button[contains(normalize-space(), '2') and (contains(normalize-space(), 'Guest') or contains(normalize-space(), 'Guests'))])[1]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='date_picker' or @id='dining-date-picker' or @id='resto-date-picker' or @id='booking-date-picker' or @id='dining-booking-date-picker' or @id='resto-booking-date-picker' or @id='date-selector' or @id='dining-date-selector' or @id='resto-date-selector' or @id='date-field']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='date_picker' or @id='dining-date-picker' or @id='resto-date-picker' or @id='booking-date-picker' or @id='dining-booking-date-picker' or @id='resto-booking-date-picker' or @id='date-selector' or @id='dining-date-selector' or @id='resto-date-selector' or @id='date-field']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//button[normalize-space()='3' and not(@disabled)])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//button[normalize-space()='3' and not(@disabled)])[1]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='time_picker' or @id='dining-time-picker' or @id='resto-time-picker' or @id='booking-time-picker' or @id='dining-booking-time-picker' or @id='resto-booking-time-picker' or @id='time-selector' or @id='dining-time-selector' or @id='resto-time-selector' or @id='time-field']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='time_picker' or @id='dining-time-picker' or @id='resto-time-picker' or @id='booking-time-picker' or @id='dining-booking-time-picker' or @id='resto-booking-time-picker' or @id='time-selector' or @id='dining-time-selector' or @id='resto-time-selector' or @id='time-field']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//button[normalize-space()='12:00 PM'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//button[normalize-space()='12:00 PM'])[1]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='book_button' or @id='dining-book-button' or @id='resto-book-button' or @id='booking-button' or @id='dining-booking-button' or @id='resto-booking-button' or @id='reserve-button' or @id='dining-reserve-button' or @id='resto-reserve-button' or @id='book-action-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='book_button' or @id='dining-book-button' or @id='resto-book-button' or @id='booking-button' or @id='dining-booking-button' or @id='resto-booking-button' or @id='reserve-button' or @id='dining-reserve-button' or @id='resto-reserve-button' or @id='book-action-button']",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "BOOK_RESTAURANT",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/booking/7/12%3A00%20PM?seed=910&people=2&date=2026-04-03",
        "prompt": "Select a country where code equals 'IN'.",
        "actions": [
            {
                "url": "http://localhost:8003/booking/7/12%3A00%20PM?seed=910&people=2&date=2026-04-03",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/booking/7/12%3A00%20PM?seed=910&people=2&date=2026-04-03",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='country-select' or @id='country-dropdown' or @id='country-picker' or @id='country-selector' or @id='country-choice' or @id='country-option' or @id='country-field' or @id='country-input' or @id='country-selection' or @id='country-picker-dropdown']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='country-select' or @id='country-dropdown' or @id='country-picker' or @id='country-selector' or @id='country-choice' or @id='country-option' or @id='country-field' or @id='country-input' or @id='country-selection' or @id='country-picker-dropdown']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='country-select' or @id='country-dropdown' or @id='country-picker' or @id='country-selector' or @id='country-choice' or @id='country-option' or @id='country-field' or @id='country-input' or @id='country-selection' or @id='country-picker-dropdown']/option[@value='IN'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='country-select' or @id='country-dropdown' or @id='country-picker' or @id='country-selector' or @id='country-choice' or @id='country-option' or @id='country-field' or @id='country-input' or @id='country-selection' or @id='country-picker-dropdown']/option[@value='IN'])[1]",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "COUNTRY_SELECTED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/booking/7/12%3A00%20PM?seed=156&people=2&date=2026-04-03",
        "prompt": "This reservation is for a 'birthday'.",
        "actions": [
            {
                "url": "http://localhost:8003/booking/7/12%3A00%20PM?seed=156&people=2&date=2026-04-03",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/booking/7/12%3A00%20PM?seed=156&people=2&date=2026-04-03",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='occasion-select' or @id='occasion-dropdown' or @id='occasion-picker' or @id='occasion-selector' or @id='occasion-choice' or @id='occasion-option' or @id='occasion-field' or @id='occasion-input' or @id='occasion-selection' or @id='occasion-picker-dropdown']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='occasion-select' or @id='occasion-dropdown' or @id='occasion-picker' or @id='occasion-selector' or @id='occasion-choice' or @id='occasion-option' or @id='occasion-field' or @id='occasion-input' or @id='occasion-selection' or @id='occasion-picker-dropdown']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='occasion-select' or @id='occasion-dropdown' or @id='occasion-picker' or @id='occasion-selector' or @id='occasion-choice' or @id='occasion-option' or @id='occasion-field' or @id='occasion-input' or @id='occasion-selection' or @id='occasion-picker-dropdown']/option[@value='birthday'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='occasion-select' or @id='occasion-dropdown' or @id='occasion-picker' or @id='occasion-selector' or @id='occasion-choice' or @id='occasion-option' or @id='occasion-field' or @id='occasion-input' or @id='occasion-selection' or @id='occasion-picker-dropdown']/option[@value='birthday'])[1]",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "OCCASION_SELECTED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/booking/7/12%3A00%20PM?seed=750&people=2&date=2026-04-03",
        "prompt": "Complete my reservation for 'Thai Garden' on 2026-04-03 at 12:00 PM for 2 people. My phone is 666777888, it's for an anniversary, and special request is 'delicious'.",
        "actions": [
            {
                "url": "http://localhost:8003/booking/7/12%3A00%20PM?seed=750&people=2&date=2026-04-03",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/booking/7/12%3A00%20PM?seed=750&people=2&date=2026-04-03",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='full-name-input' or @id='name-input' or @id='full-name' or @id='booking-name' or @id='reservation-name' or @id='customer-name' or @id='fullname-input' or @id='name-field' or @id='guest-name' or @id='full-name-field']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='full-name-input' or @id='name-input' or @id='full-name' or @id='booking-name' or @id='reservation-name' or @id='customer-name' or @id='fullname-input' or @id='name-field' or @id='guest-name' or @id='full-name-field']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "TypeAction",
                "text": "agent1",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='full-name-input' or @id='name-input' or @id='full-name' or @id='booking-name' or @id='reservation-name' or @id='customer-name' or @id='fullname-input' or @id='name-field' or @id='guest-name' or @id='full-name-field']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "agent1",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//input[@id='full-name-input' or @id='name-input' or @id='full-name' or @id='booking-name' or @id='reservation-name' or @id='customer-name' or @id='fullname-input' or @id='name-field' or @id='guest-name' or @id='full-name-field']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='phone-number-input' or @id='phone-input' or @id='booking-phone' or @id='reservation-phone' or @id='customer-phone' or @id='phone-field' or @id='mobile-input' or @id='contact-phone' or @id='phone-number' or @id='phone']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='phone-number-input' or @id='phone-input' or @id='booking-phone' or @id='reservation-phone' or @id='customer-phone' or @id='phone-field' or @id='mobile-input' or @id='contact-phone' or @id='phone-number' or @id='phone']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "TypeAction",
                "text": "666777888",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='phone-number-input' or @id='phone-input' or @id='booking-phone' or @id='reservation-phone' or @id='customer-phone' or @id='phone-field' or @id='mobile-input' or @id='contact-phone' or @id='phone-number' or @id='phone']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "666777888",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//input[@id='phone-number-input' or @id='phone-input' or @id='booking-phone' or @id='reservation-phone' or @id='customer-phone' or @id='phone-field' or @id='mobile-input' or @id='contact-phone' or @id='phone-number' or @id='phone']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='email-input' or @id='booking-email' or @id='reservation-email' or @id='customer-email' or @id='email-field' or @id='contact-email' or @id='email-address-input' or @id='email-address' or @id='email']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='email-input' or @id='booking-email' or @id='reservation-email' or @id='customer-email' or @id='email-field' or @id='contact-email' or @id='email-address-input' or @id='email-address' or @id='email']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "TypeAction",
                "text": "user_name@gmail.com",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='email-input' or @id='booking-email' or @id='reservation-email' or @id='customer-email' or @id='email-field' or @id='contact-email' or @id='email-address-input' or @id='email-address' or @id='email']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "user_name@gmail.com",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//input[@id='email-input' or @id='booking-email' or @id='reservation-email' or @id='customer-email' or @id='email-field' or @id='contact-email' or @id='email-address-input' or @id='email-address' or @id='email']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='occasion-select' or @id='occasion-dropdown' or @id='occasion-picker' or @id='occasion-selector' or @id='occasion-choice' or @id='occasion-option' or @id='occasion-field' or @id='occasion-input' or @id='occasion-selection' or @id='occasion-picker-dropdown']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='occasion-select' or @id='occasion-dropdown' or @id='occasion-picker' or @id='occasion-selector' or @id='occasion-choice' or @id='occasion-option' or @id='occasion-field' or @id='occasion-input' or @id='occasion-selection' or @id='occasion-picker-dropdown']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='occasion-select' or @id='occasion-dropdown' or @id='occasion-picker' or @id='occasion-selector' or @id='occasion-choice' or @id='occasion-option' or @id='occasion-field' or @id='occasion-input' or @id='occasion-selection' or @id='occasion-picker-dropdown']/option[@value='anniversary'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='occasion-select' or @id='occasion-dropdown' or @id='occasion-picker' or @id='occasion-selector' or @id='occasion-choice' or @id='occasion-option' or @id='occasion-field' or @id='occasion-input' or @id='occasion-selection' or @id='occasion-picker-dropdown']/option[@value='anniversary'])[1]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='special-requests-textarea' or @id='special-request-textarea' or @id='special-request' or @id='special-requests' or @id='request-textarea' or @id='booking-request' or @id='reservation-request' or @id='notes-textarea' or @id='comments-textarea' or @id='special-notes']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='special-requests-textarea' or @id='special-request-textarea' or @id='special-request' or @id='special-requests' or @id='request-textarea' or @id='booking-request' or @id='reservation-request' or @id='notes-textarea' or @id='comments-textarea' or @id='special-notes']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "TypeAction",
                "text": "delicious",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//textarea[@id='special-requests-textarea' or @id='special-request-textarea' or @id='special-request' or @id='special-requests' or @id='request-textarea' or @id='booking-request' or @id='reservation-request' or @id='notes-textarea' or @id='comments-textarea' or @id='special-notes']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "delicious",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//textarea[@id='special-requests-textarea' or @id='special-request-textarea' or @id='special-request' or @id='special-requests' or @id='request-textarea' or @id='booking-request' or @id='reservation-request' or @id='notes-textarea' or @id='comments-textarea' or @id='special-notes']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='confirm_button' or @id='confirm-booking-button' or @id='complete-reservation-button' or @id='finalize-reservation-button' or @id='submit-reservation-button' or @id='reservation-confirm-button' or @id='finish-booking-button' or @id='complete-booking-button' or @id='confirm-reservation-button' or @id='reservation-submit-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='confirm_button' or @id='confirm-booking-button' or @id='complete-reservation-button' or @id='finalize-reservation-button' or @id='submit-reservation-button' or @id='reservation-confirm-button' or @id='finish-booking-button' or @id='complete-booking-button' or @id='confirm-reservation-button' or @id='reservation-submit-button']",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "RESERVATION_COMPLETE",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/?seed=376",
        "prompt": "Contact where name equals 'James'.",
        "actions": [
            {
                "url": "http://localhost:8003/?seed=376",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/?seed=376",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='nav-contact' or @id='contact-link' or @id='contact-us-link' or @id='contact-nav' or @id='contact-us-nav' or @id='contact-button' or @id='contact-us-button' or @id='contact-menu-item' or @id='contact-us-menu-item' or @id='contact-navigation']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='nav-contact' or @id='contact-link' or @id='contact-us-link' or @id='contact-nav' or @id='contact-us-nav' or @id='contact-button' or @id='contact-us-button' or @id='contact-menu-item' or @id='contact-us-menu-item' or @id='contact-navigation']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='contact-name-input' or @id='name-input-contact' or @id='contact-name-field' or @id='name-field-contact' or @id='contact-name-text-input' or @id='name-text-input-contact' or @id='contact-name-entry' or @id='name-entry-contact' or @id='contact-name-textbox' or @id='name-textbox-contact']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='contact-name-input' or @id='name-input-contact' or @id='contact-name-field' or @id='name-field-contact' or @id='contact-name-text-input' or @id='name-text-input-contact' or @id='contact-name-entry' or @id='name-entry-contact' or @id='contact-name-textbox' or @id='name-textbox-contact']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "TypeAction",
                "text": "agent1",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='contact-name-input' or @id='name-input-contact' or @id='contact-name-field' or @id='name-field-contact' or @id='contact-name-text-input' or @id='name-text-input-contact' or @id='contact-name-entry' or @id='name-entry-contact' or @id='contact-name-textbox' or @id='name-textbox-contact']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "agent1",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//input[@id='contact-name-input' or @id='name-input-contact' or @id='contact-name-field' or @id='name-field-contact' or @id='contact-name-text-input' or @id='name-text-input-contact' or @id='contact-name-entry' or @id='name-entry-contact' or @id='contact-name-textbox' or @id='name-textbox-contact']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='contact-email-input' or @id='email-input-contact' or @id='contact-email-field' or @id='email-field-contact' or @id='contact-email-text-input' or @id='email-text-input-contact' or @id='contact-email-entry' or @id='email-entry-contact' or @id='contact-email-textbox' or @id='email-textbox-contact']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='contact-email-input' or @id='email-input-contact' or @id='contact-email-field' or @id='email-field-contact' or @id='contact-email-text-input' or @id='email-text-input-contact' or @id='contact-email-entry' or @id='email-entry-contact' or @id='contact-email-textbox' or @id='email-textbox-contact']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "TypeAction",
                "text": "gg@hairmail.com",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='contact-email-input' or @id='email-input-contact' or @id='contact-email-field' or @id='email-field-contact' or @id='contact-email-text-input' or @id='email-text-input-contact' or @id='contact-email-entry' or @id='email-entry-contact' or @id='contact-email-textbox' or @id='email-textbox-contact']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "gg@hairmail.com",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//input[@id='contact-email-input' or @id='email-input-contact' or @id='contact-email-field' or @id='email-field-contact' or @id='contact-email-text-input' or @id='email-text-input-contact' or @id='contact-email-entry' or @id='email-entry-contact' or @id='contact-email-textbox' or @id='email-textbox-contact']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='contact-subject-input' or @id='subject-input-contact' or @id='contact-subject-field' or @id='subject-field-contact' or @id='contact-subject-text-input' or @id='subject-text-input-contact' or @id='contact-subject-entry' or @id='subject-entry-contact' or @id='contact-subject-textbox' or @id='subject-textbox-contact']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='contact-subject-input' or @id='subject-input-contact' or @id='contact-subject-field' or @id='subject-field-contact' or @id='contact-subject-text-input' or @id='subject-text-input-contact' or @id='contact-subject-entry' or @id='subject-entry-contact' or @id='contact-subject-textbox' or @id='subject-textbox-contact']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "TypeAction",
                "text": "hesitations",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='contact-subject-input' or @id='subject-input-contact' or @id='contact-subject-field' or @id='subject-field-contact' or @id='contact-subject-text-input' or @id='subject-text-input-contact' or @id='contact-subject-entry' or @id='subject-entry-contact' or @id='contact-subject-textbox' or @id='subject-textbox-contact']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "hesitations",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//input[@id='contact-subject-input' or @id='subject-input-contact' or @id='contact-subject-field' or @id='subject-field-contact' or @id='contact-subject-text-input' or @id='subject-text-input-contact' or @id='contact-subject-entry' or @id='subject-entry-contact' or @id='contact-subject-textbox' or @id='subject-textbox-contact']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='contact-message-textarea' or @id='message-textarea-contact' or @id='contact-message-field' or @id='message-field-contact' or @id='contact-message-text-area' or @id='message-text-area-contact' or @id='contact-message-entry' or @id='message-entry-contact' or @id='contact-message-textbox' or @id='message-textbox-contact']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='contact-message-textarea' or @id='message-textarea-contact' or @id='contact-message-field' or @id='message-field-contact' or @id='contact-message-text-area' or @id='message-text-area-contact' or @id='contact-message-entry' or @id='message-entry-contact' or @id='contact-message-textbox' or @id='message-textbox-contact']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "TypeAction",
                "text": "idk where is the cheeckout button",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//textarea[@id='contact-message-textarea' or @id='message-textarea-contact' or @id='contact-message-field' or @id='message-field-contact' or @id='contact-message-text-area' or @id='message-text-area-contact' or @id='contact-message-entry' or @id='message-entry-contact' or @id='contact-message-textbox' or @id='message-textbox-contact']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "idk where is the cheeckout button",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//textarea[@id='contact-message-textarea' or @id='message-textarea-contact' or @id='contact-message-field' or @id='message-field-contact' or @id='contact-message-text-area' or @id='message-text-area-contact' or @id='contact-message-entry' or @id='message-entry-contact' or @id='contact-message-textbox' or @id='message-textbox-contact']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='send-message-button' or @id='send-message-btn' or @id='submit-contact-form' or @id='contact-submit-button' or @id='message-submit-button' or @id='send-contact-button' or @id='contact-send-button' or @id='submit-message-button' or @id='contact-form-submit' or @id='send-btn']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='send-message-button' or @id='send-message-btn' or @id='submit-contact-form' or @id='contact-submit-button' or @id='message-submit-button' or @id='send-contact-button' or @id='contact-send-button' or @id='submit-message-button' or @id='contact-form-submit' or @id='send-btn']",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "CONTACT_FORM_SUBMIT",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/?seed=300",
        "prompt": "Navigate to the About page to read about the company's mission and values.",
        "actions": [
            {
                "url": "http://localhost:8003/?seed=300",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/?seed=300",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='nav-about' or @id='about-link' or @id='about-us-link' or @id='about-nav' or @id='about-us-nav' or @id='about-button' or @id='about-us-button' or @id='about-menu-item' or @id='about-us-menu-item' or @id='about-navigation']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='nav-about' or @id='about-link' or @id='about-us-link' or @id='about-nav' or @id='about-us-nav' or @id='about-button' or @id='about-us-button' or @id='about-menu-item' or @id='about-us-menu-item' or @id='about-navigation']",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "ABOUT_PAGE_VIEW",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/?seed=240",
        "prompt": "Navigate to the Help page to view frequently asked questions and support guides.",
        "actions": [
            {
                "url": "http://localhost:8003/?seed=240",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/?seed=240",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='nav-help' or @id='help-link' or @id='support-link' or @id='help-nav' or @id='support-nav' or @id='help-button' or @id='support-button' or @id='help-menu-item' or @id='support-menu-item' or @id='help-navigation']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='nav-help' or @id='help-link' or @id='support-link' or @id='help-nav' or @id='support-nav' or @id='help-button' or @id='support-button' or @id='help-menu-item' or @id='support-menu-item' or @id='help-navigation']",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "HELP_PAGE_VIEW",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/?seed=471",
        "prompt": "Click the Trending Spots feature on the About page.",
        "actions": [
            {
                "url": "http://localhost:8003/?seed=471",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/?seed=471",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='nav-about' or @id='about-link' or @id='about-us-link' or @id='about-nav' or @id='about-us-nav' or @id='about-button' or @id='about-us-button' or @id='about-menu-item' or @id='about-us-menu-item' or @id='about-navigation']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='nav-about' or @id='about-link' or @id='about-us-link' or @id='about-nav' or @id='about-us-nav' or @id='about-button' or @id='about-us-button' or @id='about-menu-item' or @id='about-us-menu-item' or @id='about-navigation']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[normalize-space()='Trending Spots' or normalize-space()='Easy Reservations' or normalize-space()='Curated Restaurants'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[normalize-space()='Trending Spots' or normalize-space()='Easy Reservations' or normalize-space()='Curated Restaurants'])[1]",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "ABOUT_FEATURE_CLICK",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/?seed=384",
        "prompt": "Open the contact page.",
        "actions": [
            {
                "url": "http://localhost:8003/?seed=384",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/?seed=384",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='nav-contact' or @id='contact-link' or @id='contact-us-link' or @id='contact-nav' or @id='contact-us-nav' or @id='contact-button' or @id='contact-us-button' or @id='contact-menu-item' or @id='contact-us-menu-item' or @id='contact-navigation']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='nav-contact' or @id='contact-link' or @id='contact-us-link' or @id='contact-nav' or @id='contact-us-nav' or @id='contact-button' or @id='contact-us-button' or @id='contact-menu-item' or @id='contact-us-menu-item' or @id='contact-navigation']",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "CONTACT_PAGE_VIEW",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/?seed=539",
        "prompt": "Click the phone contact card on the contact page.",
        "actions": [
            {
                "url": "http://localhost:8003/?seed=539",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/?seed=539",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='nav-contact' or @id='contact-link' or @id='contact-us-link' or @id='contact-nav' or @id='contact-us-nav' or @id='contact-button' or @id='contact-us-button' or @id='contact-menu-item' or @id='contact-us-menu-item' or @id='contact-navigation']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='nav-contact' or @id='contact-link' or @id='contact-us-link' or @id='contact-nav' or @id='contact-us-nav' or @id='contact-button' or @id='contact-us-button' or @id='contact-menu-item' or @id='contact-us-menu-item' or @id='contact-navigation']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//a[starts-with(@href,'tel:') or .//*[normalize-space()='Call Us']])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//a[starts-with(@href,'tel:') or .//*[normalize-space()='Call Us']])[1]",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "CONTACT_CARD_CLICK",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/?seed=913",
        "prompt": "Select the Payments category in Help.",
        "actions": [
            {
                "url": "http://localhost:8003/?seed=913",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/?seed=913",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='nav-help' or @id='help-link' or @id='support-link' or @id='help-nav' or @id='support-nav' or @id='help-button' or @id='support-button' or @id='help-menu-item' or @id='support-menu-item' or @id='help-navigation']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='nav-help' or @id='help-link' or @id='support-link' or @id='help-nav' or @id='support-nav' or @id='help-button' or @id='support-button' or @id='help-menu-item' or @id='support-menu-item' or @id='help-navigation']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='help-category-payments' or @id='category-payments' or @id='help-payments-category' or @id='payments-category' or @id='help-category-payments-btn' or @id='category-payments-btn' or @id='help-payments-filter' or @id='payments-filter' or @id='help-payments-category-button' or @id='payments-category-button' or normalize-space()='Payments']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='help-category-payments' or @id='category-payments' or @id='help-payments-category' or @id='payments-category' or @id='help-category-payments-btn' or @id='category-payments-btn' or @id='help-payments-filter' or @id='payments-filter' or @id='help-payments-category-button' or @id='payments-category-button' or normalize-space()='Payments']",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "HELP_CATEGORY_SELECTED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8003/?seed=803",
        "prompt": "Expand the refund FAQ.",
        "actions": [
            {
                "url": "http://localhost:8003/?seed=803",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8003/?seed=803",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='nav-help' or @id='help-link' or @id='support-link' or @id='help-nav' or @id='support-nav' or @id='help-button' or @id='support-button' or @id='help-menu-item' or @id='support-menu-item' or @id='help-navigation']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='nav-help' or @id='help-link' or @id='support-link' or @id='help-nav' or @id='support-nav' or @id='help-button' or @id='support-button' or @id='help-menu-item' or @id='support-menu-item' or @id='help-navigation']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='faq-item-4' or @id='faq-tile-4' or @id='faq-card-4' or @id='faq-item-0' or @id='faq-tile-0' or @id='faq-card-0']//button | //button[.//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'refund')] or .//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cancellation policy')]])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[@id='faq-item-4' or @id='faq-tile-4' or @id='faq-card-4' or @id='faq-item-0' or @id='faq-tile-0' or @id='faq-card-0']//button | //button[.//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'refund')] or .//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cancellation policy')]])[1]",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "HELP_FAQ_TOGGLED",
        "has_success": False,
    },
]


# CheckEventTest payloads aligned with autodining_tasks.json (per use_case.name).
_RAW_TESTS: dict[str, list[dict]] = {
    "VIEW_RESTAURANT": [
        {
            "type": "CheckEventTest",
            "event_name": "VIEW_RESTAURANT",
            "event_criteria": {
                "rating": 4.5,
                "bookings": {"operator": "less_than", "value": 613},
                "name": {"operator": "not_equals", "value": "lvarcw"},
                "reviews": {"operator": "less_equal", "value": 1568},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "VIEW_FULL_MENU": [
        {
            "type": "CheckEventTest",
            "event_name": "VIEW_FULL_MENU",
            "event_criteria": {"reviews": {"operator": "not_equals", "value": 5679}, "cuisine": "Indian"},
            "description": "Check if specific event was triggered",
        }
    ],
    "COLLAPSE_MENU": [
        {"type": "CheckEventTest", "event_name": "COLLAPSE_MENU", "event_criteria": {"cuisine": {"operator": "not_equals", "value": "mhydqx"}}, "description": "Check if specific event was triggered"}
    ],
    "DATE_DROPDOWN_OPENED": [
        {
            "type": "CheckEventTest",
            "event_name": "DATE_DROPDOWN_OPENED",
            "event_criteria": {"date": {"operator": "less_equal", "value": "2026-04-16T19:00:00+00:00"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "TIME_DROPDOWN_OPENED": [{"type": "CheckEventTest", "event_name": "TIME_DROPDOWN_OPENED", "event_criteria": {"time": "12:00 PM"}, "description": "Check if specific event was triggered"}],
    "PEOPLE_DROPDOWN_OPENED": [{"type": "CheckEventTest", "event_name": "PEOPLE_DROPDOWN_OPENED", "event_criteria": {"people": 7}, "description": "Check if specific event was triggered"}],
    "SEARCH_RESTAURANT": [
        {"type": "CheckEventTest", "event_name": "SEARCH_RESTAURANT", "event_criteria": {"query": {"operator": "contains", "value": "Jay Fai"}}, "description": "Check if specific event was triggered"}
    ],
    "SCROLL_VIEW": [
        {
            "type": "CheckEventTest",
            "event_name": "SCROLL_VIEW",
            "event_criteria": {"section": {"operator": "contains", "value": "Introducing OpenDinning Icons"}, "direction": "right"},
            "description": "Check if specific event was triggered",
        }
    ],
    "BOOK_RESTAURANT": [
        {
            "type": "CheckEventTest",
            "event_name": "BOOK_RESTAURANT",
            "event_criteria": {"bookings": {"operator": "less_equal", "value": 893}, "people": 5, "date": {"operator": "less_equal", "value": "2026-04-08T19:00:00+00:00"}, "time": "2:00 PM"},
            "description": "Check if specific event was triggered",
        }
    ],
    "COUNTRY_SELECTED": [
        {
            "type": "CheckEventTest",
            "event_name": "COUNTRY_SELECTED",
            "event_criteria": {
                "cuisine": {"operator": "not_equals", "value": "qddqol"},
                "reviews": {"operator": "greater_equal", "value": 986},
                "name": {"operator": "not_contains", "value": "fjoewn"},
                "country": {"operator": "not_equals", "value": "Japan"},
                "people": {"operator": "greater_equal", "value": 8},
                "date": {"operator": "less_equal", "value": "2026-04-10T19:00:00+00:00"},
                "time": "2:00 PM",
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "OCCASION_SELECTED": [
        {
            "type": "CheckEventTest",
            "event_name": "OCCASION_SELECTED",
            "event_criteria": {
                "name": "Astrid y Gastón",
                "bookings": {"operator": "less_than", "value": 346},
                "people": {"operator": "greater_equal", "value": 5},
                "date": {"operator": "less_equal", "value": "2026-04-07T19:00:00+00:00"},
                "time": "12:30 PM",
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "RESERVATION_COMPLETE": [
        {
            "type": "CheckEventTest",
            "event_name": "RESERVATION_COMPLETE",
            "event_criteria": {
                "rating": {"operator": "greater_than", "value": 3.5},
                "reviews": {"operator": "greater_than", "value": 1122},
                "occasion": "anniversary",
                "code": {"operator": "not_equals", "value": "US"},
                "date": {"operator": "greater_equal", "value": "2026-04-12T19:00:00+00:00"},
                "people": 8,
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "CONTACT_FORM_SUBMIT": [
        {
            "type": "CheckEventTest",
            "event_name": "CONTACT_FORM_SUBMIT",
            "event_criteria": {
                "message": {"operator": "not_contains", "value": "Can you share details about your recent updates or new features?"},
                "email": {"operator": "not_equals", "value": "james.wilson@example.com"},
                "subject": "Website Issue Report",
                "username": {"operator": "contains", "value": "ni"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "ABOUT_PAGE_VIEW": [{"type": "CheckEventTest", "event_name": "ABOUT_PAGE_VIEW", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "HELP_PAGE_VIEW": [{"type": "CheckEventTest", "event_name": "HELP_PAGE_VIEW", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "ABOUT_FEATURE_CLICK": [
        {
            "type": "CheckEventTest",
            "event_name": "ABOUT_FEATURE_CLICK",
            "event_criteria": {"feature": {"operator": "not_contains", "value": "Live availability"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "CONTACT_PAGE_VIEW": [{"type": "CheckEventTest", "event_name": "CONTACT_PAGE_VIEW", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "CONTACT_CARD_CLICK": [
        {
            "type": "CheckEventTest",
            "event_name": "CONTACT_CARD_CLICK",
            "event_criteria": {"card_type": {"operator": "not_contains", "value": "Phone"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "HELP_CATEGORY_SELECTED": [
        {
            "type": "CheckEventTest",
            "event_name": "HELP_CATEGORY_SELECTED",
            "event_criteria": {"category": {"operator": "not_equals", "value": "Account"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "HELP_FAQ_TOGGLED": [{"type": "CheckEventTest", "event_name": "HELP_FAQ_TOGGLED", "event_criteria": {"question": "Can I get a refund?"}, "description": "Check if specific event was triggered"}],
}

_TESTS: dict[str, list[BaseTaskTest]] = {uc: [BaseTaskTest.deserialize(p) for p in pl] for uc, pl in _RAW_TESTS.items()}


def _uc(use_case: str, prompt: str, actions: list[BaseAction]) -> Trajectory:
    return Trajectory(name=use_case, prompt=prompt, actions=actions, tests=_TESTS[use_case])


def _xp(expr: str) -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value=expr)


def _id(element_id: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=element_id)


BASE = "http://localhost:8003"
# From autodining_tasks.json (?seed= in each task URL)
SEED_VIEW_RESTAURANT = 880
SEED_VIEW_FULL_MENU = 175
SEED_COLLAPSE_MENU = 621
SEED_DATE_DROPDOWN_OPENED = 854
SEED_TIME_DROPDOWN_OPENED = 321
SEED_PEOPLE_DROPDOWN_OPENED = 654
SEED_SEARCH_RESTAURANT = 499
SEED_SCROLL_VIEW = 94
SEED_BOOK_RESTAURANT = 404
SEED_COUNTRY_SELECTED = 910
SEED_OCCASION_SELECTED = 156
SEED_RESERVATION_COMPLETE = 750
SEED_CONTACT_FORM_SUBMIT = 376
SEED_ABOUT_PAGE_VIEW = 300
SEED_HELP_PAGE_VIEW = 240
SEED_ABOUT_FEATURE_CLICK = 471
SEED_CONTACT_PAGE_VIEW = 384
SEED_CONTACT_CARD_CLICK = 539
SEED_HELP_CATEGORY_SELECTED = 913
SEED_HELP_FAQ_TOGGLED = 803

VIEW_RESTAURANT = _uc(
    "VIEW_RESTAURANT",
    prompt="Show details for a restaurant where the rating equals '4.5', bookings are less than '613', name is NOT 'lvarcw', and reviews are less than or equal to '1568'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_VIEW_RESTAURANT}"),
        ClickAction(
            selector=_xp(
                "//*[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//input[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']"
            ),
            text="Thai Garden",
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='view_details_button' or @id='dining-view-details-button' or @id='resto-view-details-button' or @id='view-details-btn' or @id='dining-view-details-btn' or @id='resto-view-details-btn' or @id='view-details-action'])[1]"
            )
        ),
    ],
)

VIEW_FULL_MENU = _uc(
    "VIEW_FULL_MENU",
    prompt="Show me the full menu for a restaurant with cuisine equals 'Indian' that does NOT have '5679' reviews.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_VIEW_FULL_MENU}"),
        ClickAction(
            selector=_xp(
                "(//*[@id='menu-toggle-button' or @id='dining-menu-toggle' or @id='resto-menu-toggle' or @id='menu-expand-button' or @id='dining-menu-expand' or @id='resto-menu-expand' or @id='menu-collapse-button' or @id='dining-menu-collapse' or @id='resto-menu-collapse' or @id='menu-view-toggle'])[1]"
            )
        ),
    ],
)

COLLAPSE_MENU = _uc(
    "COLLAPSE_MENU",
    prompt="Please collapse the menu for the restaurant where the cuisine is NOT 'mhydqx'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_COLLAPSE_MENU}"),
        ClickAction(
            selector=_xp(
                "(//*[@id='menu-toggle-button' or @id='dining-menu-toggle' or @id='resto-menu-toggle' or @id='menu-expand-button' or @id='dining-menu-expand' or @id='resto-menu-expand' or @id='menu-collapse-button' or @id='dining-menu-collapse' or @id='resto-menu-collapse' or @id='menu-view-toggle'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='menu-toggle-button' or @id='dining-menu-toggle' or @id='resto-menu-toggle' or @id='menu-expand-button' or @id='dining-menu-expand' or @id='resto-menu-expand' or @id='menu-collapse-button' or @id='dining-menu-collapse' or @id='resto-menu-collapse' or @id='menu-view-toggle'])[1]"
            )
        ),
    ],
)

DATE_DROPDOWN_OPENED = _uc(
    "DATE_DROPDOWN_OPENED",
    prompt="Open the date selector and select the date less equal '2026-04-16T19:00:00+00:00'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DATE_DROPDOWN_OPENED}"),
        ClickAction(
            selector=_xp(
                "//*[@id='date_picker' or @id='date-picker' or @id='date-selector' or @id='date-input' or @id='booking-date' or @id='reservation-date' or @id='calendar-trigger' or @id='date-trigger' or @id='checkin-date' or @id='date-field']"
            )
        ),
        ClickAction(selector=_xp("(//button[@aria-label='Go to previous month' or @aria-label='Previous month'])[1]")),
        ClickAction(selector=_xp("(//button[@aria-label='Go to previous month' or @aria-label='Previous month'])[1]")),
        ClickAction(selector=_xp("(//button[normalize-space()='23' and not(@disabled)])[1]")),
    ],
)

TIME_DROPDOWN_OPENED = _uc(
    "TIME_DROPDOWN_OPENED",
    prompt="Open the time dropdown and select the time equals '12:00 PM'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_TIME_DROPDOWN_OPENED}"),
        ClickAction(
            selector=_xp(
                "//*[@id='time_picker' or @id='time-picker' or @id='time-selector' or @id='time-input' or @id='booking-time' or @id='reservation-time' or @id='time-trigger' or @id='checkin-time' or @id='time-field']"
            )
        ),
        ClickAction(selector=_xp("(//button[normalize-space()='2:30 PM'])[1]")),
    ],
)

PEOPLE_DROPDOWN_OPENED = _uc(
    "PEOPLE_DROPDOWN_OPENED",
    prompt="Open the guest selector dropdown and select people equals '7'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_PEOPLE_DROPDOWN_OPENED}"),
        ClickAction(
            selector=_xp(
                "//*[@id='people_picker' or @id='people-picker' or @id='guest-picker' or @id='guests-picker' or @id='people-selector' or @id='guest-selector' or @id='booking-people' or @id='reservation-people' or @id='people-input' or @id='guests-input']"
            )
        ),
        ClickAction(selector=_xp("(//button[contains(normalize-space(), '4') and (contains(normalize-space(), 'Guest') or contains(normalize-space(), 'Guests'))])[1]")),
    ],
)

SEARCH_RESTAURANT = _uc(
    "SEARCH_RESTAURANT",
    prompt="Search for restaurants where the query contains 'Jay Fai'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_SEARCH_RESTAURANT}"),
        ClickAction(
            selector=_xp(
                "//*[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//input[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']"
            ),
            text="Thai Garden",
        ),
    ],
)

SCROLL_VIEW = _uc(
    "SCROLL_VIEW",
    prompt="Scroll in the direction 'right' where section contains 'Introducing OpenDinning Icons'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_SCROLL_VIEW}"),
        ClickAction(
            selector=_xp(
                "(//*[@data-testid='scroll-right-1' or @id='scroll-right-button' or @id='scroll-right' or @id='scroll-right-btn' or @id='carousel-right' or @id='carousel-right-button' or @id='carousel-right-btn' or @id='next-button' or @id='next-slide' or @id='right-arrow'])[1]"
            )
        ),
    ],
)

BOOK_RESTAURANT = _uc(
    "BOOK_RESTAURANT",
    prompt="Please book a table for 5 people at a restaurant where the bookings are less than or equal to '893' on '2026-04-08T19:00:00+00:00' at '2:00 PM'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_BOOK_RESTAURANT}"),
        ClickAction(
            selector=_xp(
                "//*[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//input[@id='search-input' or @id='search-input-help' or @id='search-box' or @id='search-field' or @id='query-box' or @id='restaurant-search' or @id='search-restaurants' or @id='search-text']"
            ),
            text="Thai Garden",
        ),
        ClickAction(selector=_xp("(//*[normalize-space()='Thai Garden'])[1]")),
        ClickAction(
            selector=_xp(
                "//*[@id='people_picker' or @id='dining-people-picker' or @id='resto-people-picker' or @id='guests-picker' or @id='dining-guests-picker' or @id='resto-guests-picker' or @id='party-size-picker' or @id='dining-party-size-picker' or @id='resto-party-size-picker' or @id='people-selector']"
            )
        ),
        ClickAction(selector=_xp("(//button[contains(normalize-space(), '2') and (contains(normalize-space(), 'Guest') or contains(normalize-space(), 'Guests'))])[1]")),
        ClickAction(
            selector=_xp(
                "//*[@id='date_picker' or @id='dining-date-picker' or @id='resto-date-picker' or @id='booking-date-picker' or @id='dining-booking-date-picker' or @id='resto-booking-date-picker' or @id='date-selector' or @id='dining-date-selector' or @id='resto-date-selector' or @id='date-field']"
            )
        ),
        ClickAction(selector=_xp("(//button[normalize-space()='3' and not(@disabled)])[1]")),
        ClickAction(
            selector=_xp(
                "//*[@id='time_picker' or @id='dining-time-picker' or @id='resto-time-picker' or @id='booking-time-picker' or @id='dining-booking-time-picker' or @id='resto-booking-time-picker' or @id='time-selector' or @id='dining-time-selector' or @id='resto-time-selector' or @id='time-field']"
            )
        ),
        ClickAction(selector=_xp("(//button[normalize-space()='12:00 PM'])[1]")),
        ClickAction(
            selector=_xp(
                "//*[@id='book_button' or @id='dining-book-button' or @id='resto-book-button' or @id='booking-button' or @id='dining-booking-button' or @id='resto-booking-button' or @id='reserve-button' or @id='dining-reserve-button' or @id='resto-reserve-button' or @id='book-action-button']"
            )
        ),
    ],
)

COUNTRY_SELECTED = _uc(
    "COUNTRY_SELECTED",
    prompt="Please select a country from the dropdown that is NOT 'Japan' for your reservation, ensuring the cuisine is NOT 'qddqol', the reviews are GREATER THAN or EQUAL to 986, the name does NOT CONTAIN 'fjoewn', the number of people is GREATER THAN or EQUAL to 8, the date is LESS THAN or EQUAL to '2026-04-10T19:00:00+00:00', and the time is '2:00 PM'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_COUNTRY_SELECTED}"),
        ClickAction(
            selector=_xp(
                "//*[@id='country-select' or @id='country-dropdown' or @id='country-picker' or @id='country-selector' or @id='country-choice' or @id='country-option' or @id='country-field' or @id='country-input' or @id='country-selection' or @id='country-picker-dropdown']"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='country-select' or @id='country-dropdown' or @id='country-picker' or @id='country-selector' or @id='country-choice' or @id='country-option' or @id='country-field' or @id='country-input' or @id='country-selection' or @id='country-picker-dropdown']/option[@value='IN'])[1]"
            )
        ),
    ],
)

OCCASION_SELECTED = _uc(
    "OCCASION_SELECTED",
    prompt="Please select a special occasion for a booking at a restaurant where the name equals 'Astrid y Gast\u00f3n', the bookings are less than 346, the number of people is greater than or equal to 5, the date is less than or equal to '2026-04-07T19:00:00+00:00', and the time equals '12:30 PM'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_OCCASION_SELECTED}"),
        ClickAction(
            selector=_xp(
                "//*[@id='occasion-select' or @id='occasion-dropdown' or @id='occasion-picker' or @id='occasion-selector' or @id='occasion-choice' or @id='occasion-option' or @id='occasion-field' or @id='occasion-input' or @id='occasion-selection' or @id='occasion-picker-dropdown']"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='occasion-select' or @id='occasion-dropdown' or @id='occasion-picker' or @id='occasion-selector' or @id='occasion-choice' or @id='occasion-option' or @id='occasion-field' or @id='occasion-input' or @id='occasion-selection' or @id='occasion-picker-dropdown']/option[@value='birthday'])[1]"
            )
        ),
    ],
)

RESERVATION_COMPLETE = _uc(
    "RESERVATION_COMPLETE",
    prompt="Please finalize and complete the restaurant reservation for 8 people for an occasion that is 'anniversary' at a restaurant with a rating greater than 3.5, with more than 1122 reviews, where the code is NOT 'US', on or after '2026-04-12T19:00:00+00:00'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_RESERVATION_COMPLETE}"),
        ClickAction(
            selector=_xp(
                "//*[@id='full-name-input' or @id='name-input' or @id='full-name' or @id='booking-name' or @id='reservation-name' or @id='customer-name' or @id='fullname-input' or @id='name-field' or @id='guest-name' or @id='full-name-field']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//input[@id='full-name-input' or @id='name-input' or @id='full-name' or @id='booking-name' or @id='reservation-name' or @id='customer-name' or @id='fullname-input' or @id='name-field' or @id='guest-name' or @id='full-name-field']"
            ),
            text="agent1",
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='phone-number-input' or @id='phone-input' or @id='booking-phone' or @id='reservation-phone' or @id='customer-phone' or @id='phone-field' or @id='mobile-input' or @id='contact-phone' or @id='phone-number' or @id='phone']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//input[@id='phone-number-input' or @id='phone-input' or @id='booking-phone' or @id='reservation-phone' or @id='customer-phone' or @id='phone-field' or @id='mobile-input' or @id='contact-phone' or @id='phone-number' or @id='phone']"
            ),
            text="666777888",
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='email-input' or @id='booking-email' or @id='reservation-email' or @id='customer-email' or @id='email-field' or @id='contact-email' or @id='email-address-input' or @id='email-address' or @id='email']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//input[@id='email-input' or @id='booking-email' or @id='reservation-email' or @id='customer-email' or @id='email-field' or @id='contact-email' or @id='email-address-input' or @id='email-address' or @id='email']"
            ),
            text="user_name@gmail.com",
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='occasion-select' or @id='occasion-dropdown' or @id='occasion-picker' or @id='occasion-selector' or @id='occasion-choice' or @id='occasion-option' or @id='occasion-field' or @id='occasion-input' or @id='occasion-selection' or @id='occasion-picker-dropdown']"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='occasion-select' or @id='occasion-dropdown' or @id='occasion-picker' or @id='occasion-selector' or @id='occasion-choice' or @id='occasion-option' or @id='occasion-field' or @id='occasion-input' or @id='occasion-selection' or @id='occasion-picker-dropdown']/option[@value='anniversary'])[1]"
            )
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='special-requests-textarea' or @id='special-request-textarea' or @id='special-request' or @id='special-requests' or @id='request-textarea' or @id='booking-request' or @id='reservation-request' or @id='notes-textarea' or @id='comments-textarea' or @id='special-notes']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//textarea[@id='special-requests-textarea' or @id='special-request-textarea' or @id='special-request' or @id='special-requests' or @id='request-textarea' or @id='booking-request' or @id='reservation-request' or @id='notes-textarea' or @id='comments-textarea' or @id='special-notes']"
            ),
            text="delicious",
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='confirm_button' or @id='confirm-booking-button' or @id='complete-reservation-button' or @id='finalize-reservation-button' or @id='submit-reservation-button' or @id='reservation-confirm-button' or @id='finish-booking-button' or @id='complete-booking-button' or @id='confirm-reservation-button' or @id='reservation-submit-button']"
            )
        ),
    ],
)

CONTACT_FORM_SUBMIT = _uc(
    "CONTACT_FORM_SUBMIT",
    prompt="Contact support where message does NOT contain 'Can you share details about your recent updates or new features?' and email does NOT equal 'james.wilson@example.com' and subject equals 'Website Issue Report' and username contains 'ni'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_CONTACT_FORM_SUBMIT}"),
        ClickAction(
            selector=_xp(
                "//*[@id='nav-contact' or @id='contact-link' or @id='contact-us-link' or @id='contact-nav' or @id='contact-us-nav' or @id='contact-button' or @id='contact-us-button' or @id='contact-menu-item' or @id='contact-us-menu-item' or @id='contact-navigation']"
            )
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='contact-name-input' or @id='name-input-contact' or @id='contact-name-field' or @id='name-field-contact' or @id='contact-name-text-input' or @id='name-text-input-contact' or @id='contact-name-entry' or @id='name-entry-contact' or @id='contact-name-textbox' or @id='name-textbox-contact']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//input[@id='contact-name-input' or @id='name-input-contact' or @id='contact-name-field' or @id='name-field-contact' or @id='contact-name-text-input' or @id='name-text-input-contact' or @id='contact-name-entry' or @id='name-entry-contact' or @id='contact-name-textbox' or @id='name-textbox-contact']"
            ),
            text="agent1",
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='contact-email-input' or @id='email-input-contact' or @id='contact-email-field' or @id='email-field-contact' or @id='contact-email-text-input' or @id='email-text-input-contact' or @id='contact-email-entry' or @id='email-entry-contact' or @id='contact-email-textbox' or @id='email-textbox-contact']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//input[@id='contact-email-input' or @id='email-input-contact' or @id='contact-email-field' or @id='email-field-contact' or @id='contact-email-text-input' or @id='email-text-input-contact' or @id='contact-email-entry' or @id='email-entry-contact' or @id='contact-email-textbox' or @id='email-textbox-contact']"
            ),
            text="gg@hairmail.com",
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='contact-subject-input' or @id='subject-input-contact' or @id='contact-subject-field' or @id='subject-field-contact' or @id='contact-subject-text-input' or @id='subject-text-input-contact' or @id='contact-subject-entry' or @id='subject-entry-contact' or @id='contact-subject-textbox' or @id='subject-textbox-contact']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//input[@id='contact-subject-input' or @id='subject-input-contact' or @id='contact-subject-field' or @id='subject-field-contact' or @id='contact-subject-text-input' or @id='subject-text-input-contact' or @id='contact-subject-entry' or @id='subject-entry-contact' or @id='contact-subject-textbox' or @id='subject-textbox-contact']"
            ),
            text="hesitations",
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='contact-message-textarea' or @id='message-textarea-contact' or @id='contact-message-field' or @id='message-field-contact' or @id='contact-message-text-area' or @id='message-text-area-contact' or @id='contact-message-entry' or @id='message-entry-contact' or @id='contact-message-textbox' or @id='message-textbox-contact']"
            )
        ),
        TypeAction(
            selector=_xp(
                "//textarea[@id='contact-message-textarea' or @id='message-textarea-contact' or @id='contact-message-field' or @id='message-field-contact' or @id='contact-message-text-area' or @id='message-text-area-contact' or @id='contact-message-entry' or @id='message-entry-contact' or @id='contact-message-textbox' or @id='message-textbox-contact']"
            ),
            text="idk where is the cheeckout button",
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='send-message-button' or @id='send-message-btn' or @id='submit-contact-form' or @id='contact-submit-button' or @id='message-submit-button' or @id='send-contact-button' or @id='contact-send-button' or @id='submit-message-button' or @id='contact-form-submit' or @id='send-btn']"
            )
        ),
    ],
)

ABOUT_PAGE_VIEW = _uc(
    "ABOUT_PAGE_VIEW",
    prompt="Navigate to the About page to view company information.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_ABOUT_PAGE_VIEW}"),
        ClickAction(
            selector=_xp(
                "//*[@id='nav-about' or @id='about-link' or @id='about-us-link' or @id='about-nav' or @id='about-us-nav' or @id='about-button' or @id='about-us-button' or @id='about-menu-item' or @id='about-us-menu-item' or @id='about-navigation']"
            )
        ),
    ],
)

HELP_PAGE_VIEW = _uc(
    "HELP_PAGE_VIEW",
    prompt="Navigate to the Help page to find guidance, FAQs, or troubleshooting information.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_HELP_PAGE_VIEW}"),
        ClickAction(
            selector=_xp(
                "//*[@id='nav-help' or @id='help-link' or @id='support-link' or @id='help-nav' or @id='support-nav' or @id='help-button' or @id='support-button' or @id='help-menu-item' or @id='support-menu-item' or @id='help-navigation']"
            )
        ),
    ],
)

ABOUT_FEATURE_CLICK = _uc(
    "ABOUT_FEATURE_CLICK",
    prompt="Click on the highlighted feature on the About page that does NOT contain 'Live availability'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_ABOUT_FEATURE_CLICK}"),
        ClickAction(
            selector=_xp(
                "//*[@id='nav-about' or @id='about-link' or @id='about-us-link' or @id='about-nav' or @id='about-us-nav' or @id='about-button' or @id='about-us-button' or @id='about-menu-item' or @id='about-us-menu-item' or @id='about-navigation']"
            )
        ),
        ClickAction(selector=_xp("(//*[normalize-space()='Trending Spots' or normalize-space()='Easy Reservations' or normalize-space()='Curated Restaurants'])[1]")),
    ],
)

CONTACT_PAGE_VIEW = _uc(
    "CONTACT_PAGE_VIEW",
    prompt="Open the contact page.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_CONTACT_PAGE_VIEW}"),
        ClickAction(
            selector=_xp(
                "//*[@id='nav-contact' or @id='contact-link' or @id='contact-us-link' or @id='contact-nav' or @id='contact-us-nav' or @id='contact-button' or @id='contact-us-button' or @id='contact-menu-item' or @id='contact-us-menu-item' or @id='contact-navigation']"
            )
        ),
    ],
)

CONTACT_CARD_CLICK = _uc(
    "CONTACT_CARD_CLICK",
    prompt="Click the contact card where the card_type does NOT contain 'Phone'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_CONTACT_CARD_CLICK}"),
        ClickAction(
            selector=_xp(
                "//*[@id='nav-contact' or @id='contact-link' or @id='contact-us-link' or @id='contact-nav' or @id='contact-us-nav' or @id='contact-button' or @id='contact-us-button' or @id='contact-menu-item' or @id='contact-us-menu-item' or @id='contact-navigation']"
            )
        ),
        ClickAction(selector=_xp("(//a[starts-with(@href,'tel:') or .//*[normalize-space()='Call Us']])[1]")),
    ],
)

HELP_CATEGORY_SELECTED = _uc(
    "HELP_CATEGORY_SELECTED",
    prompt="Select a help category that is NOT 'Account'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_HELP_CATEGORY_SELECTED}"),
        ClickAction(
            selector=_xp(
                "//*[@id='nav-help' or @id='help-link' or @id='support-link' or @id='help-nav' or @id='support-nav' or @id='help-button' or @id='support-button' or @id='help-menu-item' or @id='support-menu-item' or @id='help-navigation']"
            )
        ),
        ClickAction(
            selector=_xp(
                "//*[@id='help-category-payments' or @id='category-payments' or @id='help-payments-category' or @id='payments-category' or @id='help-category-payments-btn' or @id='category-payments-btn' or @id='help-payments-filter' or @id='payments-filter' or @id='help-payments-category-button' or @id='payments-category-button' or normalize-space()='Payments']"
            )
        ),
    ],
)

HELP_FAQ_TOGGLED = _uc(
    "HELP_FAQ_TOGGLED",
    prompt="Expand the FAQ item where the question equals 'Can I get a refund?'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_HELP_FAQ_TOGGLED}"),
        ClickAction(
            selector=_xp(
                "//*[@id='nav-help' or @id='help-link' or @id='support-link' or @id='help-nav' or @id='support-nav' or @id='help-button' or @id='support-button' or @id='help-menu-item' or @id='support-menu-item' or @id='help-navigation']"
            )
        ),
        ClickAction(
            selector=_xp(
                "(//*[@id='faq-item-4' or @id='faq-tile-4' or @id='faq-card-4' or @id='faq-item-0' or @id='faq-tile-0' or @id='faq-card-0']//button | //button[.//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'refund')] or .//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cancellation policy')]])[1]"
            )
        ),
    ],
)


def load_autodining_use_case_completion_flows() -> dict[str, Trajectory]:
    return {
        "VIEW_RESTAURANT": VIEW_RESTAURANT,
        "VIEW_FULL_MENU": VIEW_FULL_MENU,
        "COLLAPSE_MENU": COLLAPSE_MENU,
        "DATE_DROPDOWN_OPENED": DATE_DROPDOWN_OPENED,
        "TIME_DROPDOWN_OPENED": TIME_DROPDOWN_OPENED,
        "PEOPLE_DROPDOWN_OPENED": PEOPLE_DROPDOWN_OPENED,
        "SEARCH_RESTAURANT": SEARCH_RESTAURANT,
        "SCROLL_VIEW": SCROLL_VIEW,
        "BOOK_RESTAURANT": BOOK_RESTAURANT,
        "COUNTRY_SELECTED": COUNTRY_SELECTED,
        "OCCASION_SELECTED": OCCASION_SELECTED,
        "RESERVATION_COMPLETE": RESERVATION_COMPLETE,
        "CONTACT_FORM_SUBMIT": CONTACT_FORM_SUBMIT,
        "ABOUT_PAGE_VIEW": ABOUT_PAGE_VIEW,
        "HELP_PAGE_VIEW": HELP_PAGE_VIEW,
        "ABOUT_FEATURE_CLICK": ABOUT_FEATURE_CLICK,
        "CONTACT_PAGE_VIEW": CONTACT_PAGE_VIEW,
        "CONTACT_CARD_CLICK": CONTACT_CARD_CLICK,
        "HELP_CATEGORY_SELECTED": HELP_CATEGORY_SELECTED,
        "HELP_FAQ_TOGGLED": HELP_FAQ_TOGGLED,
    }
