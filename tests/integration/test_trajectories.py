from unittest.mock import patch

from autoppia_iwa.src.execution.actions.actions import ClickAction, NavigateAction, SelectDropDownOptionAction
from autoppia_iwa.src.web_agents.apified_iterative_agent import ApifiedWebAgent

_TRAJECTORIES = [
    {
        "id": "autocinema.film_detail.filters_year_genre_then_director",
        "web_project_id": "autocinema",
        "use_case": {
            "name": "FILM_DETAIL",
            "description": "Open the requested movie and extract a concrete detail from its detail page.",
        },
        "prompt": "Navigate to a movie details page that matches requested year/genre constraints using the Search page filters.",
        "actions": [
            {"name": "browser.navigate", "arguments": {"url": "http://localhost:8000/search"}},
            {
                "name": "browser.select_dropdown",
                "arguments": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//select[.//option[contains(normalize-space(.), 'All genres')]]",
                    },
                    "text": "Sci-Fi",
                },
            },
            {
                "name": "browser.select_dropdown",
                "arguments": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//select[.//option[contains(normalize-space(.), 'All years')]]",
                    },
                    "text": "2010",
                },
            },
            {
                "name": "browser.click",
                "arguments": {
                    "selector": {
                        "type": "tagContainsSelector",
                        "value": "View Details",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "notes": "Use /search filters (genre + year) and open a movie detail page via a 'View Details' card action.",
    },
]


def test_trajectories_test_autocinema_payload_is_valid() -> None:
    trajectory = _TRAJECTORIES[0]

    assert trajectory["id"] == "autocinema.film_detail.filters_year_genre_then_director"
    assert trajectory["web_project_id"] == "autocinema"
    assert trajectory["use_case"]["name"] == "FILM_DETAIL"
    assert trajectory["prompt"]
    assert len(trajectory["actions"]) == 4


def test_trajectories_test_autocinema_actions_parse_with_step_protocol() -> None:
    trajectory = _TRAJECTORIES[0]
    agent = ApifiedWebAgent(base_url="http://127.0.0.1:9999")

    with patch.object(agent, "_rewrite_to_remote", side_effect=lambda value: value):
        actions = agent._parse_actions_response(
            {
                "actions": trajectory["actions"],
                "done": False,
            }
        )

    assert len(actions) == 4
    assert isinstance(actions[0], NavigateAction)
    assert actions[0].url == "http://localhost:8000/search"

    assert isinstance(actions[1], SelectDropDownOptionAction)
    assert actions[1].text == "Sci-Fi"
    assert actions[1].selector is not None
    assert actions[1].selector.value == "//select[.//option[contains(normalize-space(.), 'All genres')]]"

    assert isinstance(actions[2], SelectDropDownOptionAction)
    assert actions[2].text == "2010"
    assert actions[2].selector is not None
    assert actions[2].selector.value == "//select[.//option[contains(normalize-space(.), 'All years')]]"

    assert isinstance(actions[3], ClickAction)
    assert actions[3].selector is not None
    assert actions[3].selector.value == "View Details"
