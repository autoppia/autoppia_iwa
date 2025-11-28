from __future__ import annotations

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator


def generate_date_dropdown_opened_constraints():
    return [
        {"field": "selected_date", "operator": ComparisonOperator.EQUALS, "value": "2024-06-20"},
    ]


def generate_time_dropdown_opened_constraints():
    return [
        {"field": "selected_time", "operator": ComparisonOperator.EQUALS, "value": "7:30 PM"},
    ]


def generate_people_dropdown_opened_constraints():
    return [
        {"field": "people_count", "operator": ComparisonOperator.EQUALS, "value": 6},
    ]


def generate_search_restaurant_constraints():
    return [
        {"field": "query", "operator": ComparisonOperator.EQUALS, "value": "vegan"},
    ]


def generate_view_restaurant_constraints():
    return [
        {"field": "rating", "operator": ComparisonOperator.EQUALS, "value": 45},
    ]


def generate_view_full_menu_constraints():
    return [
        {"field": "people", "operator": ComparisonOperator.EQUALS, "value": 4},
        {"field": "action", "operator": ComparisonOperator.EQUALS, "value": "expand"},
    ]


def generate_collapse_menu_constraints():
    return [
        {"field": "action", "operator": ComparisonOperator.EQUALS, "value": "collapse"},
    ]


def generate_book_restaurant_constraints():
    return [
        {"field": "people", "operator": ComparisonOperator.EQUALS, "value": 4},
        {"field": "time", "operator": ComparisonOperator.EQUALS, "value": "8:30 PM"},
    ]


def generate_country_selected_constraints():
    return [
        {"field": "country_code", "operator": ComparisonOperator.EQUALS, "value": "+34"},
    ]


def generate_occasion_selected_constraints():
    return [
        {"field": "occasion", "operator": ComparisonOperator.EQUALS, "value": "Birthday"},
    ]


def generate_reservation_complete_constraints():
    return [
        {"field": "people_count", "operator": ComparisonOperator.EQUALS, "value": 2},
    ]


def generate_scroll_view_constraints():
    return [
        {"field": "direction", "operator": ComparisonOperator.EQUALS, "value": "right"},
    ]
