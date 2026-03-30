import pytest

from autoppia_iwa.src.demo_webs.web_verification.iwap_client import IWAPClient


@pytest.mark.asyncio
async def test_get_tasks_with_solutions_returns_mock_response():
    client = IWAPClient(base_url="https://iwap.example.test", use_mock=True)

    response = await client.get_tasks_with_solutions("autolodge_8", "VIEW_HOTEL")

    assert response["success"] is True
    assert response["website"] == "autolodge"
    assert response["use_case"] == "VIEW_HOTEL"
    assert response["data"]["tasks"]


def test_process_api_response_for_tasks_returns_first_successful_solution():
    client = IWAPClient()
    api_response = {
        "success": True,
        "data": {
            "tasks": [
                {
                    "task": {
                        "taskId": "task-1",
                        "prompt": "Open the hotel details",
                        "tests": [{"type": "CheckEventTest"}],
                        "startUrl": "http://localhost:8004/hotels?seed=1",
                        "webVersion": "1.0",
                    },
                    "solution": {"actions": [{"type": "click"}]},
                    "evaluation": {"score": 1, "passed": True},
                },
                {
                    "task": {"taskId": "task-2"},
                    "solution": {"actions": [{"type": "click"}]},
                    "evaluation": {"score": 0, "passed": False},
                },
            ]
        },
    }

    result = client.process_api_response_for_tasks(api_response)

    assert result["matched"] is True
    assert result["api_task_id"] == "task-1"
    assert result["api_prompt"] == "Open the hotel details"
    assert result["actions"] == [{"type": "click"}]
    assert result["total_solutions_found"] == 1


def test_process_api_response_for_tasks_rejects_missing_actions():
    client = IWAPClient()
    api_response = {
        "success": True,
        "data": {
            "tasks": [
                {
                    "task": {"taskId": "task-1"},
                    "solution": {"actions": []},
                    "evaluation": {"score": 1, "passed": True},
                }
            ]
        },
    }

    result = client.process_api_response_for_tasks(api_response)

    assert result == {
        "matched": False,
        "reason": "No actions found in solution",
        "actions": None,
    }
