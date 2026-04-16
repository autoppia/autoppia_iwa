from __future__ import annotations

from unittest.mock import Mock

from autoppia_iwa.src.bootstrap import AppBootstrap


def test_app_bootstrap_initializes_and_wires_container(monkeypatch):
    fake_container = Mock()
    fake_container.wire = Mock()
    monkeypatch.setattr("autoppia_iwa.src.bootstrap.DIContainer", Mock(return_value=fake_container))

    bootstrap = AppBootstrap()

    assert bootstrap.container is fake_container
    fake_container.wire.assert_called_once_with(packages=["autoppia_iwa.src"])
