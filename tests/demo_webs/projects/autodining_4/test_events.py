"""Unit tests for autodining_4 events (parse + validate_criteria) to improve coverage."""

from datetime import date

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.autodining_4.events import (
    BACKEND_EVENT_TYPES,
    AboutFeatureClickEvent,
    BookRestaurantEvent,
    CollapseMenuEvent,
    ContactCardClickEvent,
    ContactEvent,
    CountrySelectedEvent,
    DateDropdownOpenedEvent,
    HelpCategorySelectedEvent,
    HelpFaqToggledEvent,
    OccasionSelectedEvent,
    PeopleDropdownOpenedEvent,
    ScrollViewEvent,
    SearchRestaurantEvent,
    TimeDropdownOpenedEvent,
    ViewFullMenuEvent,
    ViewRestaurantEvent,
)
from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator, CriterionValue

from ..event_parse_helpers import assert_parse_cls_kwargs_match_model


def _be(event_name: str, data: dict | None = None, web_agent_id: str = "test-agent", **kwargs) -> BackendEvent:
    return BackendEvent(event_name=event_name, data=data or {}, web_agent_id=web_agent_id, **kwargs)


AUTODINING_PAYLOADS = [
    ("DATE_DROPDOWN_OPENED", {}),
    ("TIME_DROPDOWN_OPENED", {"time": "19:00"}),
    ("PEOPLE_DROPDOWN_OPENED", {"people": 2}),
    ("SEARCH_RESTAURANT", {"query": "italian"}),
    ("VIEW_RESTAURANT", {"restaurantId": "1", "restaurantName": "R", "cuisine": "Italian", "rating": 4}),
    ("VIEW_FULL_MENU", {"menu": [], "date": "2025-03-15"}),
    ("COLLAPSE_MENU", {"menu": [], "date": "2025-03-15"}),
    ("BOOK_RESTAURANT", {"date": "2025-03-15", "name": "R", "desc": "d"}),
    ("COUNTRY_SELECTED", {"countryCode": "US", "countryName": "USA", "restaurantName": "R"}),
    ("OCCASION_SELECTED", {"occasion": "dinner", "restaurantName": "R"}),
    ("SCROLL_VIEW", {"direction": "down", "sectionTitle": "Menu"}),
    ("ABOUT_PAGE_VIEW", {}),
    ("ABOUT_FEATURE_CLICK", {"feature": "hours"}),
    ("CONTACT_PAGE_VIEW", {}),
    ("CONTACT_CARD_CLICK", {"card_type": "email"}),
    ("HELP_PAGE_VIEW", {}),
    ("HELP_CATEGORY_SELECTED", {"category": "reservations"}),
    ("HELP_FAQ_TOGGLED", {"question": "Q"}),
    ("CONTACT_FORM_SUBMIT", {"data": {"message": "m", "name": "N", "email": "e@e.com", "subject": "s"}}),
]


class TestParseAutodiningEvents:
    def test_search_restaurant_parse(self):
        e = SearchRestaurantEvent.parse(_be("SEARCH_RESTAURANT", {"query": "italian"}))
        assert e.query == "italian"


class TestValidateAutodiningEventsCriteria:
    """Validate_criteria tests for autodining_4 events that have ValidationCriteria."""

    def test_date_dropdown_opened_validate_none(self):
        e = DateDropdownOpenedEvent.parse(_be("DATE_DROPDOWN_OPENED", {}))
        assert e.validate_criteria(None) is True

    def test_time_dropdown_opened_validate_criteria(self):
        e = TimeDropdownOpenedEvent.parse(_be("TIME_DROPDOWN_OPENED", {"time": "19:00"}))
        criteria = TimeDropdownOpenedEvent.ValidationCriteria(time="19:00")
        assert e.validate_criteria(criteria) is True

    def test_people_dropdown_opened_validate_criteria(self):
        e = PeopleDropdownOpenedEvent.parse(_be("PEOPLE_DROPDOWN_OPENED", {"people": 2}))
        criteria = PeopleDropdownOpenedEvent.ValidationCriteria(people=2)
        assert e.validate_criteria(criteria) is True

    def test_search_restaurant_event_validate_criteria(self):
        e = SearchRestaurantEvent.parse(_be("SEARCH_RESTAURANT", {"query": "italian"}))
        criteria = SearchRestaurantEvent.ValidationCriteria(query="italian")
        assert e.validate_criteria(criteria) is True

    def test_view_restaurant_event_validate_criteria(self):
        e = ViewRestaurantEvent.parse(_be("VIEW_RESTAURANT", {"restaurantId": "1", "restaurantName": "R", "cuisine": "Italian", "rating": 4}))
        criteria = ViewRestaurantEvent.ValidationCriteria(name="R", cuisine="Italian", rating=4)
        assert e.validate_criteria(criteria) is True

    def test_view_full_menu_event_validate_criteria(self):
        e = ViewFullMenuEvent.parse(_be("VIEW_FULL_MENU", {"menu": [], "date": "2025-03-15"}))
        criteria = ViewFullMenuEvent.ValidationCriteria(date=CriterionValue(value=date(2025, 3, 15), operator=ComparisonOperator.EQUALS))
        assert e.validate_criteria(criteria) is True

    def test_collapse_menu_event_validate_criteria(self):
        e = CollapseMenuEvent.parse(_be("COLLAPSE_MENU", {"menu": [], "date": "2025-03-15", "action": "collapse"}))
        criteria = CollapseMenuEvent.ValidationCriteria(action="collapse")
        assert e.validate_criteria(criteria) is True

    def test_book_restaurant_event_validate_criteria(self):
        e = BookRestaurantEvent.parse(_be("BOOK_RESTAURANT", {"date": "2025-03-15", "restaurantName": "R", "desc": "d", "people": 2}))
        criteria = BookRestaurantEvent.ValidationCriteria(name="R", desc="d", people=2)
        assert e.validate_criteria(criteria) is True

    def test_country_selected_event_validate_criteria(self):
        e = CountrySelectedEvent.parse(_be("COUNTRY_SELECTED", {"countryCode": "US", "countryName": "USA", "restaurantName": "R"}))
        criteria = CountrySelectedEvent.ValidationCriteria(code="US", country="USA", name="R")
        assert e.validate_criteria(criteria) is True

    def test_occasion_selected_event_validate_criteria(self):
        e = OccasionSelectedEvent.parse(_be("OCCASION_SELECTED", {"occasion": "dinner", "restaurantName": "R"}))
        criteria = OccasionSelectedEvent.ValidationCriteria(occasion="dinner")
        assert e.validate_criteria(criteria) is True

    def test_scroll_view_event_validate_criteria(self):
        e = ScrollViewEvent.parse(_be("SCROLL_VIEW", {"direction": "down", "sectionTitle": "Menu"}))
        criteria = ScrollViewEvent.ValidationCriteria(direction="down", section="Menu")
        assert e.validate_criteria(criteria) is True

    def test_about_feature_click_event_validate_criteria(self):
        e = AboutFeatureClickEvent.parse(_be("ABOUT_FEATURE_CLICK", {"feature": "hours"}))
        criteria = AboutFeatureClickEvent.ValidationCriteria(feature="hours")
        assert e.validate_criteria(criteria) is True

    def test_help_category_selected_event_validate_criteria(self):
        e = HelpCategorySelectedEvent.parse(_be("HELP_CATEGORY_SELECTED", {"category": "reservations"}))
        criteria = HelpCategorySelectedEvent.ValidationCriteria(category="reservations")
        assert e.validate_criteria(criteria) is True

    def test_help_faq_toggled_event_validate_criteria(self):
        e = HelpFaqToggledEvent.parse(_be("HELP_FAQ_TOGGLED", {"question": "Q"}))
        criteria = HelpFaqToggledEvent.ValidationCriteria(question="Q")
        assert e.validate_criteria(criteria) is True

    def test_contact_event_validate_criteria(self):
        e = ContactEvent.parse(_be("CONTACT_FORM_SUBMIT", {"data": {"message": "m", "name": "N", "email": "e@e.com", "subject": "s"}}))
        criteria = ContactEvent.ValidationCriteria(email="e@e.com", message="m", subject="s")
        assert e.validate_criteria(criteria) is True

    def test_contact_card_click_event_validate_criteria(self):
        e = ContactCardClickEvent.parse(_be("CONTACT_CARD_CLICK", {"card_type": "email"}))
        criteria = ContactCardClickEvent.ValidationCriteria(card_type="email")
        assert e.validate_criteria(criteria) is True


@pytest.mark.parametrize("event_name,data", AUTODINING_PAYLOADS)
def test_backend_event_types_parse(event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    assert_parse_cls_kwargs_match_model(event_class)
