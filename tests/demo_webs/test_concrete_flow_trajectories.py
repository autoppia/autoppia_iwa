"""Concrete-flow trajectories bundle actions with in-module `CheckEventTest` payloads (import-time init)."""

from __future__ import annotations

from autoppia_iwa.src.demo_webs.projects.p12_autolist.trajectories import load_autolist_use_case_completion_flows
from autoppia_iwa.src.demo_webs.projects.p13_autodrive.trajectories import load_autodrive_use_case_completion_flows
from autoppia_iwa.src.demo_webs.projects.p14_autohealth.trajectories import load_autohealth_use_case_completion_flows


def test_autodrive_trajectories_include_tests_from_task_cache() -> None:
    flows = load_autodrive_use_case_completion_flows()
    assert len(flows) == 12
    for name, tr in flows.items():
        assert tr.name == name
        assert tr.tests, name
        assert all(getattr(t, "type", None) == "CheckEventTest" for t in tr.tests)


def test_autohealth_trajectories_include_tests_from_task_cache() -> None:
    flows = load_autohealth_use_case_completion_flows()
    assert len(flows) == 16
    for name, tr in flows.items():
        assert tr.name == name
        assert tr.tests, name


def test_autolist_trajectories_include_tests_from_task_cache() -> None:
    flows = load_autolist_use_case_completion_flows()
    assert len(flows) == 12
    for name, tr in flows.items():
        assert tr.name == name
        assert tr.tests, name
