import pytest

from .trajectories_project_helper import assert_project_fixture, load_project_fixture, project_ids, project_params, replay_project_trajectory

PROJECT_ID = "p16_autodiscord"
PROJECT_NAME_LEGACY = "autodiscord"
FIXTURE = load_project_fixture(PROJECT_ID)


def test_trajectories_p16_fixture_contains_only_autodiscord():
    assert_project_fixture(FIXTURE, PROJECT_ID, PROJECT_NAME_LEGACY)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize(("index", "trajectory"), project_params(FIXTURE), ids=project_ids(FIXTURE))
async def test_trajectories_p16(index: int, trajectory: dict):
    await replay_project_trajectory(FIXTURE, index, trajectory)
