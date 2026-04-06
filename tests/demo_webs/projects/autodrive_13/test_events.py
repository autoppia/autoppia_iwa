"""Unit tests for autodrive_13 events (parse + validate_criteria) to improve coverage."""

from unittest.mock import patch

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.p13_autodrive.events import (
    BACKEND_EVENT_TYPES,
    CancelReservationEvent,
    EnterDestinationEvent,
    EnterLocationEvent,
    NextPickupEvent,
    ReserveRideEvent,
    SearchDestinationEvent,
    SearchLocationEvent,
    SearchRideEvent,
    SeePricesEvent,
    SelectCarEvent,
    SelectDateEvent,
    SelectTimeEvent,
    TripDetailsEvent,
    parse_datetime,
    parse_time,
)

from ..event_parse_helpers import assert_parse_cls_kwargs_match_model


def _be(event_name: str, data: dict | None = None, web_agent_id: str = "test-agent", **kwargs) -> BackendEvent:
    return BackendEvent(event_name=event_name, data=data or {}, web_agent_id=web_agent_id, **kwargs)


# Valid ISO date/time strings for parse_datetime coverage
ISO_DATE = "2025-03-15"
ISO_DATETIME = "2025-03-15T14:30:00"
TIME_ONLY = "14:30"


@patch("autoppia_iwa.src.demo_webs.projects.p13_autodrive.events.log_event")
class TestParseLocationAndDestination:
    def test_search_location_parse(self, mock_log):
        e = SearchLocationEvent.parse(_be("SEARCH_LOCATION", {"value": "Paris"}))
        assert e.event_name == "SEARCH_LOCATION"
        assert e.location == "Paris"

    def test_enter_location_parse(self, mock_log):
        e = EnterLocationEvent.parse(_be("ENTER_LOCATION", {"value": "Lyon"}))
        assert e.event_name == "ENTER_LOCATION"
        assert e.location == "Lyon"

    def test_enter_location_focus_without_value(self, mock_log):
        """Trip form logs ENTER_LOCATION on focus before any text (no `value` in payload)."""
        e = EnterLocationEvent.parse(
            _be(
                "ENTER_LOCATION",
                {
                    "page": "trip_form",
                    "action": "focus",
                    "inputType": "location",
                    "timestamp": "2026-04-02T10:03:34.741Z",
                },
            )
        )
        assert isinstance(e, EnterLocationEvent)
        assert e.location == ""

    def test_search_location_accepts_location_key(self, mock_log):
        e = SearchLocationEvent.parse(_be("SEARCH_LOCATION", {"location": "Berlin"}))
        assert e.location == "Berlin"

    def test_search_destination_parse(self, mock_log):
        e = SearchDestinationEvent.parse(_be("SEARCH_DESTINATION", {"value": "Marseille"}))
        assert e.destination == "Marseille"

    def test_enter_destination_parse(self, mock_log):
        e = EnterDestinationEvent.parse(_be("ENTER_DESTINATION", {"value": "Nice"}))
        assert e.event_name == "ENTER_DESTINATION"
        assert e.destination == "Nice"

    def test_enter_destination_focus_without_value(self, mock_log):
        e = EnterDestinationEvent.parse(
            _be(
                "ENTER_DESTINATION",
                {"page": "trip_form", "action": "focus", "inputType": "destination"},
            )
        )
        assert isinstance(e, EnterDestinationEvent)
        assert e.destination == ""

    def test_search_destination_accepts_destination_key(self, mock_log):
        e = SearchDestinationEvent.parse(_be("SEARCH_DESTINATION", {"destination": "Toulouse"}))
        assert e.destination == "Toulouse"


@patch("autoppia_iwa.src.demo_webs.projects.p13_autodrive.events.log_event")
class TestParseSeePrices:
    def test_see_prices_parse(self, mock_log):
        e = SeePricesEvent.parse(_be("SEE_PRICES", {"location": "Paris", "destination": "Lyon"}))
        assert e.location == "Paris"
        assert e.destination == "Lyon"


@patch("autoppia_iwa.src.demo_webs.projects.p13_autodrive.events.log_event")
class TestParseDateAndTime:
    def test_select_date_parse_valid_iso(self, mock_log):
        e = SelectDateEvent.parse(_be("SELECT_DATE", {"date": ISO_DATE}))
        assert e.date is not None
        assert e.date.year == 2025 and e.date.month == 3 and e.date.day == 15

    def test_select_date_parse_none(self, mock_log):
        e = SelectDateEvent.parse(_be("SELECT_DATE", {}))
        assert e.date is None

    def test_select_time_parse(self, mock_log):
        e = SelectTimeEvent.parse(_be("SELECT_TIME", {"time": TIME_ONLY}))
        assert e.time is not None

    def test_select_time_parse_none(self, mock_log):
        e = SelectTimeEvent.parse(_be("SELECT_TIME", {}))
        assert e.time is None

    def test_parse_time_helper_variants(self, mock_log):
        assert parse_time(TIME_ONLY) is not None
        assert parse_time(None) is None
        assert parse_time("not-a-time") is None
        from datetime import time as dt_time

        t = dt_time(14, 30)
        assert parse_time(t) == t

    def test_next_pickup_parse(self, mock_log):
        e = NextPickupEvent.parse(_be("NEXT_PICKUP", {"date": ISO_DATE, "time": TIME_ONLY}))
        assert e.date is not None
        assert e.time is not None


@patch("autoppia_iwa.src.demo_webs.projects.p13_autodrive.events.log_event")
class TestParseSearchRide:
    def test_search_ride_parse(self, mock_log):
        e = SearchRideEvent.parse(
            _be(
                "SEARCH",
                {"pickup": "Paris", "dropoff": "Lyon", "scheduled": ISO_DATETIME},
            )
        )
        assert e.location == "Paris"
        assert e.destination == "Lyon"
        assert e.scheduled is not None

    def test_search_ride_scheduled_now_uses_event_timestamp(self, mock_log):
        e = SearchRideEvent.parse(
            _be(
                "SEARCH",
                {
                    "pickup": "Cafe Restaurant - 4629 Maple Dr, Chicago, IL 60608, USA",
                    "dropoff": "Cafe Restaurant - 4629 Maple Dr, Chicago, IL 60608, USA",
                    "scheduled": "now",
                },
                timestamp="2026-04-02T10:39:48.610Z",
            )
        )
        assert e.scheduled.year == 2026
        assert e.scheduled.month == 4
        assert e.scheduled.day == 2


@patch("autoppia_iwa.src.demo_webs.projects.p13_autodrive.events.log_event")
class TestParseSelectCarAndReserve:
    def test_select_car_parse(self, mock_log):
        e = SelectCarEvent.parse(
            _be(
                "SELECT_CAR",
                {
                    "pickup": "A",
                    "dropoff": "B",
                    "rideName": "Economy",
                    "scheduled": ISO_DATETIME,
                    "price": 25.5,
                    "seats": 4,
                },
            )
        )
        assert e.location == "A"
        assert e.destination == "B"
        assert e.ride_name == "Economy"
        assert e.price == 25.5
        assert e.seats == 4

    def test_reserve_ride_parse(self, mock_log):
        e = ReserveRideEvent.parse(
            _be(
                "RESERVE_RIDE",
                {
                    "pickup": "X",
                    "dropoff": "Y",
                    "rideName": "Comfort",
                    "scheduled": ISO_DATETIME,
                    "price": 30.0,
                    "seats": 2,
                },
            )
        )
        assert e.destination == "Y"
        assert e.ride_name == "Comfort"

    def test_trip_details_parse(self, mock_log):
        e = TripDetailsEvent.parse(
            _be(
                "TRIP_DETAILS",
                {
                    "pickup": "P",
                    "dropoff": "D",
                    "rideName": "R",
                    "scheduled": ISO_DATETIME,
                    "price": 10.0,
                    "seats": 1,
                },
            )
        )
        assert e.event_name == "TRIP_DETAILS"

    def test_cancel_reservation_parse(self, mock_log):
        e = CancelReservationEvent.parse(
            _be(
                "CANCEL_RESERVATION",
                {
                    "pickup": "P",
                    "dropoff": "D",
                    "rideName": "R",
                    "scheduled": ISO_DATETIME,
                    "price": 10.0,
                    "seats": 1,
                },
            )
        )
        assert e.event_name == "CANCEL_RESERVATION"

    def test_cancel_reservation_parse_trip_data_shape(self, mock_log):
        payload = {
            "tripId": "1",
            "tripData": {
                "id": "1",
                "date": "2025-07-18",
                "time": "13:00",
                "price": 31.5,
                "pickup": "100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA",
                "dropoff": "1030 Post Street Apartments - 1030 Post St #112, San Francisco, CA 94109, USA",
                "ride": {"name": "Comfort"},
            },
            "timestamp": "2026-04-02T10:40:14.136Z",
        }
        e = CancelReservationEvent.parse(_be("CANCEL_RESERVATION", payload))
        assert e.location.startswith("100 Van Ness")
        assert e.destination.startswith("1030 Post")
        assert e.ride_name == "Comfort"
        assert e.price == 31.5
        assert e.scheduled.year == 2025
        assert e.scheduled.month == 7
        assert e.scheduled.day == 18


# Validation tests
@patch("autoppia_iwa.src.demo_webs.projects.p13_autodrive.events.log_event")
class TestValidateEvents:
    def test_search_location_validate_none(self, mock_log):
        e = SearchLocationEvent.parse(_be("SEARCH_LOCATION", {"value": "Paris"}))
        assert e.validate_criteria(None) is True

    def test_search_location_validate_location(self, mock_log):
        e = SearchLocationEvent.parse(_be("SEARCH_LOCATION", {"value": "Paris"}))
        criteria = SearchLocationEvent.ValidationCriteria(location="Paris")
        assert e.validate_criteria(criteria) is True

    def test_see_prices_validate(self, mock_log):
        e = SeePricesEvent.parse(_be("SEE_PRICES", {"location": "Paris", "destination": "Lyon"}))
        criteria = SeePricesEvent.ValidationCriteria(location="Paris", destination="Lyon")
        assert e.validate_criteria(criteria) is True

    def test_select_date_validate_none(self, mock_log):
        e = SelectDateEvent.parse(_be("SELECT_DATE", {"date": ISO_DATE}))
        assert e.validate_criteria(None) is True

    def test_select_date_and_time_validate_specific_values(self, mock_log):
        d = SelectDateEvent.parse(_be("SELECT_DATE", {"date": ISO_DATE}))
        t = SelectTimeEvent.parse(_be("SELECT_TIME", {"time": TIME_ONLY}))
        assert d.validate_criteria(SelectDateEvent.ValidationCriteria(date=d.date)) is True
        assert t.validate_criteria(SelectTimeEvent.ValidationCriteria(time=t.time)) is True

    def test_search_ride_validate(self, mock_log):
        e = SearchRideEvent.parse(_be("SEARCH", {"pickup": "A", "dropoff": "B", "scheduled": ISO_DATETIME}))
        criteria = SearchRideEvent.ValidationCriteria(destination="B", location="A")
        assert e.validate_criteria(criteria) is True

    def test_select_car_validate(self, mock_log):
        e = SelectCarEvent.parse(
            _be(
                "SELECT_CAR",
                {
                    "pickup": "A",
                    "dropoff": "B",
                    "rideName": "Eco",
                    "scheduled": ISO_DATETIME,
                    "price": 20.0,
                    "seats": 3,
                },
            )
        )
        criteria = SelectCarEvent.ValidationCriteria(destination="B", location="A", ride_name="Eco", price=20.0, seats=3)
        assert e.validate_criteria(criteria) is True

    def test_reserve_ride_validate(self, mock_log):
        e = ReserveRideEvent.parse(
            _be(
                "RESERVE_RIDE",
                {
                    "pickup": "P",
                    "dropoff": "D",
                    "rideName": "R",
                    "scheduled": ISO_DATETIME,
                    "price": 15.0,
                    "seats": 2,
                },
            )
        )
        criteria = ReserveRideEvent.ValidationCriteria(destination="D", location="P", ride_name="R", price=15.0, seats=2)
        assert e.validate_criteria(criteria) is True

    def test_trip_details_and_cancel_reservation_validate(self, mock_log):
        payload = {
            "pickup": "P",
            "dropoff": "D",
            "rideName": "R",
            "scheduled": ISO_DATETIME,
            "price": 10.0,
            "seats": 1,
        }
        trip = TripDetailsEvent.parse(_be("TRIP_DETAILS", payload))
        cancel = CancelReservationEvent.parse(_be("CANCEL_RESERVATION", payload))
        criteria = TripDetailsEvent.ValidationCriteria(destination="D", location="P", ride_name="R", price=10.0, seats=1)
        assert trip.validate_criteria(criteria) is True
        assert cancel.validate_criteria(criteria) is True

    def test_negative_validation_paths(self, mock_log):
        search_location = SearchLocationEvent.parse(_be("SEARCH_LOCATION", {"value": "Paris"}))
        assert search_location.validate_criteria(SearchLocationEvent.ValidationCriteria(location="Lyon")) is False

        see_prices = SeePricesEvent.parse(_be("SEE_PRICES", {"location": "Paris", "destination": "Lyon"}))
        assert see_prices.validate_criteria(SeePricesEvent.ValidationCriteria(destination="Marseille")) is False

        select_date = SelectDateEvent.parse(_be("SELECT_DATE", {"date": ISO_DATE}))
        assert select_date.validate_criteria(SelectDateEvent.ValidationCriteria(date="2026-01-01")) is False

        select_time = SelectTimeEvent.parse(_be("SELECT_TIME", {"time": TIME_ONLY}))
        assert select_time.validate_criteria(SelectTimeEvent.ValidationCriteria(time="15:30")) is False

        next_pickup = NextPickupEvent.parse(_be("NEXT_PICKUP", {"date": ISO_DATE, "time": TIME_ONLY}))
        assert next_pickup.validate_criteria(NextPickupEvent.ValidationCriteria(time="15:30")) is False

        search_ride = SearchRideEvent.parse(_be("SEARCH", {"pickup": "A", "dropoff": "B", "scheduled": ISO_DATETIME}))
        assert search_ride.validate_criteria(SearchRideEvent.ValidationCriteria(location="X")) is False

        select_car = SelectCarEvent.parse(
            _be(
                "SELECT_CAR",
                {
                    "pickup": "A",
                    "dropoff": "B",
                    "rideName": "Eco",
                    "scheduled": ISO_DATETIME,
                    "price": 20.0,
                    "seats": 3,
                },
            )
        )
        assert select_car.validate_criteria(SelectCarEvent.ValidationCriteria(ride_name="Other")) is False

        reserve = ReserveRideEvent.parse(
            _be(
                "RESERVE_RIDE",
                {
                    "pickup": "P",
                    "dropoff": "D",
                    "rideName": "R",
                    "scheduled": ISO_DATETIME,
                    "price": 15.0,
                    "seats": 2,
                },
            )
        )
        assert reserve.validate_criteria(ReserveRideEvent.ValidationCriteria(price=99.0)) is False

    def test_parse_datetime_additional_paths(self, mock_log):
        from datetime import datetime

        assert parse_datetime(datetime(2025, 3, 15, 14, 30)) == datetime(2025, 3, 15, 14, 30)
        assert parse_datetime("2025-03-15 14:30:00") is not None
        assert parse_datetime("2025-03-15") is not None
        assert parse_datetime("bad") is None


@pytest.mark.parametrize(
    "event_name,data",
    [
        ("SEARCH_LOCATION", {"value": "Paris"}),
        ("SEARCH_DESTINATION", {"value": "Lyon"}),
        ("ENTER_LOCATION", {"value": "X"}),
        ("ENTER_DESTINATION", {"value": "Y"}),
        ("NEXT_PICKUP", {"date": ISO_DATE, "time": TIME_ONLY}),
        ("SELECT_DATE", {"date": ISO_DATE}),
        ("SELECT_TIME", {"time": TIME_ONLY}),
        ("SEARCH", {"pickup": "A", "dropoff": "B", "scheduled": ISO_DATETIME}),
        (
            "SELECT_CAR",
            {
                "pickup": "A",
                "dropoff": "B",
                "rideName": "Eco",
                "scheduled": ISO_DATETIME,
                "price": 10.0,
                "seats": 2,
            },
        ),
        (
            "RESERVE_RIDE",
            {
                "pickup": "A",
                "dropoff": "B",
                "rideName": "Eco",
                "scheduled": ISO_DATETIME,
                "price": 10.0,
                "seats": 2,
            },
        ),
        (
            "TRIP_DETAILS",
            {
                "pickup": "A",
                "dropoff": "B",
                "rideName": "Eco",
                "scheduled": ISO_DATETIME,
                "price": 10.0,
                "seats": 2,
            },
        ),
        (
            "CANCEL_RESERVATION",
            {
                "pickup": "A",
                "dropoff": "B",
                "rideName": "Eco",
                "scheduled": ISO_DATETIME,
                "price": 10.0,
                "seats": 2,
            },
        ),
    ],
)
@patch("autoppia_iwa.src.demo_webs.projects.p13_autodrive.events.log_event")
def test_backend_event_types_parse(mock_log, event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    assert_parse_cls_kwargs_match_model(event_class)
