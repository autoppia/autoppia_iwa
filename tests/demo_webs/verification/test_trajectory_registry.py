from autoppia_iwa.src.demo_webs.trajectory_registry import (
    get_trajectory_map,
    remap_url_to_frontend,
    supported_trajectory_project_ids,
)


def test_remap_url_to_frontend_preserves_path_query_and_fragment():
    out = remap_url_to_frontend(
        "http://old-host:9999/ride/trip?seed=317&x=1#frag",
        "https://new.example:443",
    )
    assert out == "https://new.example:443/ride/trip?seed=317&x=1#frag"


def test_remap_url_to_frontend_empty_returns_original():
    assert remap_url_to_frontend("", "http://localhost:8000") == ""
    assert remap_url_to_frontend("http://a/b", "") == "http://a/b"


def test_supported_trajectory_project_ids_contains_known_demo_projects():
    ids = supported_trajectory_project_ids()
    assert "autolodge" in ids
    assert "autoconnect" in ids
    assert "autolist" in ids
    assert "autodrive" in ids
    assert "autohealth" in ids


def test_get_trajectory_map_returns_dict_for_autodrive():
    m = get_trajectory_map("autodrive")
    assert m is not None
    assert "SEARCH" in m or "ENTER_LOCATION" in m


def test_get_trajectory_map_unknown_project_returns_none():
    assert get_trajectory_map("__unknown_demo_web__") is None


def test_get_trajectory_map_autolodge_loads_from_python():
    from autoppia_iwa.src.execution.actions import NavigateAction

    m = get_trajectory_map("autolodge")
    assert m is not None
    assert len(m) == 19
    t = m["SEARCH_HOTEL"]
    assert len(t.actions) >= 2
    assert isinstance(t.actions[0], NavigateAction)
    assert t.tests and t.tests[0].type == "CheckEventTest"


def test_get_trajectory_map_autoconnect_loads_from_python():
    from autoppia_iwa.src.execution.actions import NavigateAction

    m = get_trajectory_map("autoconnect")
    assert m is not None
    assert len(m) == 26
    t = m["VIEW_USER_PROFILE"]
    assert len(t.actions) >= 2
    assert isinstance(t.actions[0], NavigateAction)
    assert t.tests and t.tests[0].type == "CheckEventTest"
