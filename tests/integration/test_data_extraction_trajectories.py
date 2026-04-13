from autoppia_iwa.src.demo_webs.data_extraction_trajectory_registry import (
    get_data_extraction_trajectories,
    supported_data_extraction_trajectory_project_ids,
)


def test_data_extraction_registry_supports_expected_projects() -> None:
    assert supported_data_extraction_trajectory_project_ids() == {
        "autocinema",
        "autobooks",
        "autozone",
        "autodining",
        "autocrm",
        "automail",
        "autodelivery",
        "autolodge",
        "autoconnect",
        "autowork",
        "autocalendar",
        "autolist",
        "autodrive",
        "autohealth",
        "autostats",
        "autodiscord",
    }


def test_data_extraction_registry_counts_match_supported_use_cases() -> None:
    expected_counts = {
        "autobooks": 8,
        "autocalendar": 11,
        "autocinema": 7,
        "autoconnect": 16,
        "autocrm": 15,
        "autodelivery": 7,
        "autodining": 8,
        "autodrive": 6,
        "autodiscord": 5,
        "autohealth": 14,
        "autolist": 6,
        "autolodge": 9,
        "automail": 17,
        "autostats": 5,
        "autowork": 12,
        "autozone": 7,
    }

    for project_id, expected_count in expected_counts.items():
        trajectories = get_data_extraction_trajectories(project_id)
        assert trajectories is not None
        assert len(trajectories) == expected_count
        assert len({trajectory.use_case for trajectory in trajectories}) == expected_count


def test_data_extraction_registry_payload_shape_all_projects() -> None:
    for project_id in supported_data_extraction_trajectory_project_ids():
        trajectories = get_data_extraction_trajectories(project_id)
        assert trajectories is not None
        assert trajectories

        for trajectory in trajectories:
            dumped = trajectory.to_step_tool_calls_trajectory()
            assert dumped["trajectory_type"] == "data_extraction"
            assert dumped["web_project_id"] == project_id
            assert dumped["seed"] == 1
            assert dumped["use_case"]
            assert dumped["question"]
            assert dumped["expected_answer"]
            assert dumped["id"]
            if trajectory.actions:
                assert isinstance(dumped["url"], str)
                assert dumped["url"].startswith("http://localhost:")
                assert len(dumped["actions"]) >= 1
            else:
                assert dumped["url"] is None
                assert dumped["actions"] == []


def test_data_extraction_trajectory_autocinema_seed1_payload_is_valid() -> None:
    trajectories = get_data_extraction_trajectories("autocinema")
    assert trajectories is not None
    assert len(trajectories) == 7

    expected_use_cases = {
        "FILM_DETAIL",
        "SEARCH_FILM",
        "FILTER_FILM",
        "ADD_TO_WATCHLIST",
        "SHARE_MOVIE",
        "WATCH_TRAILER",
        "DELETE_FILM",
    }
    assert {trajectory.use_case for trajectory in trajectories} == expected_use_cases

    for trajectory in trajectories:
        dumped = trajectory.to_step_tool_calls_trajectory()
        assert dumped["trajectory_type"] == "data_extraction"
        assert dumped["web_project_id"] == "autocinema"
        assert dumped["seed"] == 1
        assert dumped["use_case"] in expected_use_cases
        assert dumped["id"].startswith("autocinema.de.seed1.")
        assert dumped["url"] is None
        assert dumped["question"]
        assert dumped["expected_answer"]
        assert dumped["actions"] == []


def test_data_extraction_trajectory_autocinema_seed1_is_dataset_only() -> None:
    trajectories = get_data_extraction_trajectories("autocinema")
    assert trajectories is not None

    for trajectory in trajectories:
        payload = trajectory.to_step_tool_calls_trajectory()
        assert payload["url"] is None
        assert payload["actions"] == []
