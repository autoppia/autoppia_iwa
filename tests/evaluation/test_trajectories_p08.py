import pytest

from .trajectories_project_helper import assert_project_fixture, load_project_fixture, project_ids, project_params, replay_project_trajectory

PROJECT_ID = "p08_autolodge"
PROJECT_NAME_LEGACY = "autolodge"
FIXTURE = load_project_fixture(PROJECT_ID)


def test_trajectories_p08_fixture_contains_only_autolodge():
    assert_project_fixture(FIXTURE, PROJECT_ID, PROJECT_NAME_LEGACY)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize(("index", "trajectory"), project_params(FIXTURE), ids=project_ids(FIXTURE))
async def test_trajectories_p08(index: int, trajectory: dict):
    await replay_project_trajectory(FIXTURE, index, trajectory)
