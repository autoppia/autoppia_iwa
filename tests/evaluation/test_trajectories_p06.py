import pytest

from .trajectories_project_helper import assert_project_fixture, load_project_fixture, project_ids, project_params, replay_project_trajectory

PROJECT_ID = "p06_automail"
PROJECT_NAME_LEGACY = "automail"
FIXTURE = load_project_fixture(PROJECT_ID)


def test_trajectories_p06_fixture_contains_only_automail():
    assert_project_fixture(FIXTURE, PROJECT_ID, PROJECT_NAME_LEGACY)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize(("index", "trajectory"), project_params(FIXTURE), ids=project_ids(FIXTURE))
async def test_trajectories_p06(index: int, trajectory: dict):
    await replay_project_trajectory(FIXTURE, index, trajectory)
