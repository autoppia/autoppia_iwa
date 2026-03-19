"""Unit tests for autostats_15 events (parse + validate_criteria) to improve coverage.

Autostats_15 events expect payload under data.data (inner payload from frontend).
"""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.p15_autostats.events import (
    BACKEND_EVENT_TYPES,
    ConnectWalletEvent,
    ViewSubnetEvent,
)

from ..event_parse_helpers import assert_parse_cls_kwargs_match_model


def _be(event_name: str, data: dict | None = None, web_agent_id: str = "test-agent", **kwargs) -> BackendEvent:
    return BackendEvent(event_name=event_name, data=data or {}, web_agent_id=web_agent_id, **kwargs)


def _wrap_data(inner: dict) -> dict:
    """Wrap inner payload as data.data for autostats_15."""
    return {"data": inner}


AUTOSTATS_PAYLOADS = [
    ("VIEW_SUBNET", _wrap_data({})),
    ("VIEW_VALIDATOR", _wrap_data({})),
    ("VIEW_BLOCK", _wrap_data({})),
    ("VIEW_ACCOUNT", _wrap_data({})),
    ("EXECUTE_BUY", _wrap_data({})),
    ("EXECUTE_SELL", _wrap_data({})),
    ("CONNECT_WALLET", _wrap_data({})),
    ("DISCONNECT_WALLET", _wrap_data({})),
    ("TRANSFER_COMPLETE", _wrap_data({})),
    ("FAVORITE_SUBNET", _wrap_data({})),
]


class TestParseAutostatsEvents:
    def test_view_subnet_parse(self):
        payload = _wrap_data({"subnet_name": "Subnet 1", "price": 1.5})
        e = ViewSubnetEvent.parse(_be("VIEW_SUBNET", payload))
        assert e.event_name == "VIEW_SUBNET"
        assert e.subnet_name == "Subnet 1"
        assert e.price == 1.5

    def test_connect_wallet_parse(self):
        payload = _wrap_data({"wallet_name": "Polkadot.js", "address": "0x123"})
        e = ConnectWalletEvent.parse(_be("CONNECT_WALLET", payload))
        assert e.event_name == "CONNECT_WALLET"
        assert e.wallet_name == "Polkadot.js"
        assert e.address == "0x123"


class TestValidateAutostatsEvents:
    def test_view_subnet_validate_none(self):
        e = ViewSubnetEvent.parse(_be("VIEW_SUBNET", _wrap_data({"subnet_name": "X"})))
        assert e.validate_criteria(None) is True

    def test_view_subnet_validate_criteria(self):
        e = ViewSubnetEvent.parse(_be("VIEW_SUBNET", _wrap_data({"subnet_name": "Subnet A", "price": 2.0})))
        criteria = ViewSubnetEvent.ValidationCriteria(subnet_name="Subnet A", price=2.0)
        assert e.validate_criteria(criteria) is True

    def test_connect_wallet_validate_none(self):
        e = ConnectWalletEvent.parse(_be("CONNECT_WALLET", _wrap_data({})))
        assert e.validate_criteria(None) is True


@pytest.mark.parametrize("event_name,data", AUTOSTATS_PAYLOADS)
def test_backend_event_types_parse(event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    assert_parse_cls_kwargs_match_model(event_class)
