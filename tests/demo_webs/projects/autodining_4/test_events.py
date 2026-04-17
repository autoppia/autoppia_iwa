"""Unit tests for autodining_4 events (parse + validate_criteria) to improve coverage."""

from datetime import date

import pytest
from pydantic import ValidationError

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator, CriterionValue
from autoppia_iwa.src.demo_webs.projects.p04_autodining.events import (
    BACKEND_EVENT_TYPES,
    AboutFeatureClickEvent,
    BookRestaurantEvent,
    CollapseMenuEvent,
    ContactCardClickEvent,
    ContactEvent,
    ContactPageViewEvent,
    CountrySelectedEvent,
    DateDropdownOpenedEvent,
    DiningReviewCreatedEvent,
    DiningReviewDeletedEvent,
    HelpCategorySelectedEvent,
    HelpFaqToggledEvent,
    MenuCategory,
    MenuItem,
    OccasionSelectedEvent,
    PeopleDropdownOpenedEvent,
    ReservationCompleteEvent,
    ScrollViewEvent,
    SearchRestaurantEvent,
    TimeDropdownOpenedEvent,
    ViewFullMenuEvent,
    ViewRestaurantEvent,
)

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
    ("TIME_SELECTED", {"time": "19:00"}),
    ("DATE_SELECTED", {"date": "2025-06-01T12:00:00.000Z"}),
    ("PEOPLE_SELECTED", {"people": 4}),
    ("TAG_FILTER_SELECTED", {"tag": "Japanese"}),
    ("LOGIN", {"username": "alex", "source": "login"}),
    ("REGISTER", {"username": "newbie", "source": "register"}),
    ("LOGOUT", {"username": "alex"}),
    (
        "REVIEW_CREATED",
        {"review_id": "r1", "restaurant_id": "rest-1", "username": "alex", "rating": 5, "comment_length": 12},
    ),
    ("REVIEW_EDITED", {"review_id": "r1", "restaurant_id": "rest-1", "username": "alex", "rating": 4, "comment_length": 8}),
    ("REVIEW_DELETED", {"review_id": "r1", "restaurant_id": "rest-1", "username": "alex"}),
]


class TestParseAutodiningEvents:
    def test_search_restaurant_parse(self):
        e = SearchRestaurantEvent.parse(_be("SEARCH_RESTAURANT", {"query": "italian"}))
        assert e.query == "italian"

    def test_menu_item_and_category_parse(self):
        item = MenuItem.parse_from_data({"name": "Pizza", "price": "$12.50"})
        category = MenuCategory.parse_from_data({"category": "Main", "items": [{"name": "Pizza", "price": "$12.50"}]})
        assert item.price == 12.5
        assert category.category == "Main"
        assert category.items[0].name == "Pizza"

    def test_parse_invalid_dates_and_padding_paths(self):
        with pytest.raises(ValidationError):
            ViewFullMenuEvent.parse(_be("VIEW_FULL_MENU", {"menu": [], "date": "bad-date"}))
        with pytest.raises(ValidationError):
            CollapseMenuEvent.parse(_be("COLLAPSE_MENU", {"menu": [], "date": "bad-date"}))
        with pytest.raises(ValidationError):
            BookRestaurantEvent.parse(_be("BOOK_RESTAURANT", {"date": "bad-date"}))
        reservation = ReservationCompleteEvent.parse(
            _be(
                "RESERVATION_COMPLETE",
                {
                    "date": "May 1",
                    "time": "19:00",
                    "people": 2,
                    "countryCode": "US",
                    "countryName": "USA",
                    "phoneNumber": "123",
                    "occasion": "Dinner",
                },
            )
        )
        assert reservation.reservation == "May 01"


class TestValidateAutodiningEventsCriteria:
    """Validate_criteria tests for autodining_4 events that have ValidationCriteria."""

    def test_date_dropdown_opened_validate_none(self):
        e = DateDropdownOpenedEvent.parse(_be("DATE_DROPDOWN_OPENED", {}))
        assert e.validate_criteria(None) is True

    def test_date_dropdown_opened_validate_comparison_operators(self):
        e = DateDropdownOpenedEvent.parse(_be("DATE_DROPDOWN_OPENED", {"date": "2025-03-15"}))
        assert e.validate_criteria(DateDropdownOpenedEvent.ValidationCriteria(date=CriterionValue(value="2025-03-14", operator=ComparisonOperator.GREATER_THAN)))
        assert e.validate_criteria(DateDropdownOpenedEvent.ValidationCriteria(date=CriterionValue(value="2025-03-16", operator=ComparisonOperator.LESS_THAN)))
        assert e.validate_criteria(DateDropdownOpenedEvent.ValidationCriteria(date=CriterionValue(value="2025-03-15", operator=ComparisonOperator.GREATER_EQUAL)))
        assert e.validate_criteria(DateDropdownOpenedEvent.ValidationCriteria(date=CriterionValue(value="2025-03-15", operator=ComparisonOperator.LESS_EQUAL)))

    def test_date_dropdown_opened_validate_invalid_criterion(self):
        e = DateDropdownOpenedEvent.parse(_be("DATE_DROPDOWN_OPENED", {"date": "2025-03-15"}))
        assert e.validate_criteria(DateDropdownOpenedEvent.ValidationCriteria(date=CriterionValue(value=123, operator=ComparisonOperator.EQUALS))) is False

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
        e = ViewFullMenuEvent.parse(_be("VIEW_FULL_MENU", {"menu": [{"category": "Main", "items": [{"name": "Pizza", "price": "$12.50"}]}], "date": "2025-03-15"}))
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

    def test_negative_validation_paths_cover_remaining_event_branches(self):
        assert TimeDropdownOpenedEvent.parse(_be("TIME_DROPDOWN_OPENED", {"time": "19:00"})).validate_criteria(TimeDropdownOpenedEvent.ValidationCriteria(time="20:00")) is False
        assert PeopleDropdownOpenedEvent.parse(_be("PEOPLE_DROPDOWN_OPENED", {"people": 2})).validate_criteria(PeopleDropdownOpenedEvent.ValidationCriteria(people=3)) is False
        assert SearchRestaurantEvent.parse(_be("SEARCH_RESTAURANT", {"query": "italian"})).validate_criteria(SearchRestaurantEvent.ValidationCriteria(query="thai")) is False

        view_restaurant = ViewRestaurantEvent.parse(_be("VIEW_RESTAURANT", {"restaurantId": "1", "restaurantName": "R", "desc": "Nice", "cuisine": "Italian", "rating": 4, "bookings": 9}))
        assert view_restaurant.validate_criteria(ViewRestaurantEvent.ValidationCriteria(name="Other")) is False
        assert view_restaurant.validate_criteria(ViewRestaurantEvent.ValidationCriteria(desc="Other")) is False

        menu = ViewFullMenuEvent.parse(
            _be(
                "VIEW_FULL_MENU",
                {"restaurantId": "1", "restaurantName": "R", "action": "view", "time": "19:00", "date": "2025-03-15", "people": 2, "desc": "Nice", "rating": 4},
            )
        )
        assert menu.validate_criteria(ViewFullMenuEvent.ValidationCriteria(action="collapse")) is False

        collapsed = CollapseMenuEvent.parse(
            _be(
                "COLLAPSE_MENU",
                {"restaurantId": "1", "restaurantName": "R", "action": "collapse", "date": "2025-03-15", "desc": "Nice", "rating": 4, "reviews": 8, "bookings": 2, "cuisine": "Italian"},
            )
        )
        assert collapsed.validate_criteria(CollapseMenuEvent.ValidationCriteria(action="open")) is False

        booked = BookRestaurantEvent.parse(_be("BOOK_RESTAURANT", {"date": "2025-03-15", "restaurantName": "R", "desc": "d", "people": 2, "time": "19:00"}))
        bad_date = BookRestaurantEvent.ValidationCriteria(date=CriterionValue(value="2025-03-14", operator=ComparisonOperator.EQUALS))
        bad_date.date.operator = "unknown"
        assert booked.validate_criteria(bad_date) is False
        assert booked.validate_criteria(BookRestaurantEvent.ValidationCriteria(name="Other")) is False

        country = CountrySelectedEvent.parse(_be("COUNTRY_SELECTED", {"countryCode": "US", "countryName": "USA", "restaurantName": "R"}))
        assert country.validate_criteria(CountrySelectedEvent.ValidationCriteria(code="ES")) is False

        occasion = OccasionSelectedEvent.parse(_be("OCCASION_SELECTED", {"occasion": "dinner", "restaurantName": "R"}))
        assert occasion.validate_criteria(OccasionSelectedEvent.ValidationCriteria(occasion="lunch")) is False

        reservation = ReservationCompleteEvent.parse(
            _be(
                "RESERVATION_COMPLETE",
                {
                    "date": "May 10",
                    "time": "19:00",
                    "people": 2,
                    "countryCode": "US",
                    "countryName": "USA",
                    "phoneNumber": "123",
                    "occasion": "Dinner",
                    "specialRequest": "Window",
                },
            )
        )
        assert reservation.validate_criteria(ReservationCompleteEvent.ValidationCriteria(code="ES")) is False
        assert reservation.validate_criteria(ReservationCompleteEvent.ValidationCriteria(request="Other")) is False

        scroll = ScrollViewEvent.parse(_be("SCROLL_VIEW", {"direction": "down", "sectionTitle": "Menu"}))
        assert scroll.validate_criteria(ScrollViewEvent.ValidationCriteria(direction="up")) is False

        about = AboutFeatureClickEvent.parse(_be("ABOUT_FEATURE_CLICK", {"feature": "hours"}))
        assert about.validate_criteria(AboutFeatureClickEvent.ValidationCriteria(feature="pricing")) is False

        help_category = HelpCategorySelectedEvent.parse(_be("HELP_CATEGORY_SELECTED", {"category": "reservations"}))
        assert help_category.validate_criteria(HelpCategorySelectedEvent.ValidationCriteria(category="billing")) is False

        faq = HelpFaqToggledEvent.parse(_be("HELP_FAQ_TOGGLED", {"question": "Q"}))
        assert faq.validate_criteria(HelpFaqToggledEvent.ValidationCriteria(question="Other")) is False

        contact = ContactEvent.parse(_be("CONTACT_FORM_SUBMIT", {"data": {"message": "m", "name": "N", "email": "e@e.com", "subject": "s"}}))
        assert contact.validate_criteria(ContactEvent.ValidationCriteria(email="other@e.com")) is False

        card = ContactCardClickEvent.parse(_be("CONTACT_CARD_CLICK", {"card_type": "email"}))
        assert card.validate_criteria(ContactCardClickEvent.ValidationCriteria(card_type="phone")) is False

    def test_contact_page_view_event_is_always_true(self):
        event = ContactPageViewEvent.parse(_be("CONTACT_PAGE_VIEW", {}))
        assert event.validate_criteria(None) is True
        assert event.validate_criteria(ContactPageViewEvent.ValidationCriteria()) is True


@pytest.mark.parametrize("event_name,data", AUTODINING_PAYLOADS)
def test_backend_event_types_parse(event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    if event_name == "REVIEW_CREATED":
        assert isinstance(e, DiningReviewCreatedEvent)
    elif event_name == "REVIEW_DELETED":
        assert isinstance(e, DiningReviewDeletedEvent)
    else:
        assert_parse_cls_kwargs_match_model(event_class)
