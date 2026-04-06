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
    DateSelectedEvent,
    HelpCategorySelectedEvent,
    HelpFaqToggledEvent,
    LoginEvent,
    LogoutEvent,
    OccasionSelectedEvent,
    PeopleSelectedEvent,
    RegisterEvent,
    ReviewCreatedEvent,
    ReviewDeletedEvent,
    ReviewEditedEvent,
    ScrollViewEvent,
    SearchRestaurantEvent,
    TagFilterSelectedEvent,
    TimeSelectedEvent,
    ViewFullMenuEvent,
    ViewRestaurantEvent,
)
from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator, CriterionValue

from ..event_parse_helpers import assert_parse_cls_kwargs_match_model


def _be(event_name: str, data: dict | None = None, web_agent_id: str = "test-agent", **kwargs) -> BackendEvent:
    return BackendEvent(event_name=event_name, data=data or {}, web_agent_id=web_agent_id, **kwargs)


AUTODINING_PAYLOADS = [
    ("DATE_SELECTED", {"date": "2026-02-23T19:00:00+00:00"}),
    ("TIME_SELECTED", {"time": "19:00"}),
    ("PEOPLE_SELECTED", {"people": 2}),
    ("TAG_FILTER_SELECTED", {"tag": "sushi", "action": "add", "search": "sushi"}),
    ("LOGIN", {"username": "james", "source": "modal"}),
    ("REGISTER", {"username": "emma", "email": "emma@example.com", "source": "modal"}),
    ("LOGOUT", {"username": "james"}),
    ("REVIEW_CREATED", {"review_id": "review-1", "restaurant_id": "rest-1", "username": "james", "rating": 5, "comment_length": 120}),
    ("REVIEW_EDITED", {"review_id": "review-1", "restaurant_id": "rest-1", "username": "james", "rating": 4, "comment_length": 80}),
    ("REVIEW_DELETED", {"review_id": "review-1", "restaurant_id": "rest-1", "username": "james"}),
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

    def test_date_selected_validate_none(self):
        e = DateSelectedEvent.parse(_be("DATE_SELECTED", {"date": "2026-02-23T19:00:00+00:00"}))
        assert e.validate_criteria(None) is True

    def test_time_selected_validate_criteria(self):
        e = TimeSelectedEvent.parse(_be("TIME_SELECTED", {"time": "19:00"}))
        criteria = TimeSelectedEvent.ValidationCriteria(time="19:00")
        assert e.validate_criteria(criteria) is True

    def test_people_selected_validate_criteria(self):
        e = PeopleSelectedEvent.parse(_be("PEOPLE_SELECTED", {"people": 2}))
        criteria = PeopleSelectedEvent.ValidationCriteria(people=2)
        assert e.validate_criteria(criteria) is True

    def test_tag_filter_selected_validate_criteria(self):
        e = TagFilterSelectedEvent.parse(_be("TAG_FILTER_SELECTED", {"tag": "sushi", "action": "add", "search": "sushi"}))
        criteria = TagFilterSelectedEvent.ValidationCriteria(tag="sushi", action="add")
        assert e.validate_criteria(criteria) is True

    def test_login_validate_criteria(self):
        e = LoginEvent.parse(_be("LOGIN", {"username": "james", "source": "modal"}))
        criteria = LoginEvent.ValidationCriteria(username="james")
        assert e.validate_criteria(criteria) is True

    def test_register_validate_criteria(self):
        e = RegisterEvent.parse(_be("REGISTER", {"username": "emma", "email": "emma@example.com", "source": "modal"}))
        criteria = RegisterEvent.ValidationCriteria(username="emma", email="emma@example.com")
        assert e.validate_criteria(criteria) is True

    def test_logout_validate_criteria(self):
        e = LogoutEvent.parse(_be("LOGOUT", {"username": "james"}))
        criteria = LogoutEvent.ValidationCriteria(username="james")
        assert e.validate_criteria(criteria) is True

    def test_review_created_validate_criteria(self):
        e = ReviewCreatedEvent.parse(_be("REVIEW_CREATED", {"review_id": "review-1", "restaurant_id": "rest-1", "username": "james", "rating": 5, "comment_length": 120}))
        criteria = ReviewCreatedEvent.ValidationCriteria(review_id="review-1", restaurant_id="rest-1", rating=5)
        assert e.validate_criteria(criteria) is True

    def test_review_edited_validate_criteria(self):
        e = ReviewEditedEvent.parse(_be("REVIEW_EDITED", {"review_id": "review-1", "restaurant_id": "rest-1", "username": "james", "rating": 4, "comment_length": 80}))
        criteria = ReviewEditedEvent.ValidationCriteria(review_id="review-1", restaurant_id="rest-1", rating=4)
        assert e.validate_criteria(criteria) is True

    def test_review_deleted_validate_criteria(self):
        e = ReviewDeletedEvent.parse(_be("REVIEW_DELETED", {"review_id": "review-1", "restaurant_id": "rest-1", "username": "james"}))
        criteria = ReviewDeletedEvent.ValidationCriteria(review_id="review-1", restaurant_id="rest-1")
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
