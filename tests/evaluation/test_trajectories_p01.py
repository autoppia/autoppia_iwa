import pytest

from .trajectories_project_helper import (
    assert_project_fixture,
    load_project_fixture,
    project_ids,
    project_params,
    replay_project_trajectory,
)

PROJECT_ID = "p01_autocinema"
PROJECT_NAME_LEGACY = "autocinema"
FIXTURE = load_project_fixture(PROJECT_ID)


def test_trajectories_p01_fixture_contains_only_autocinema():
    assert_project_fixture(FIXTURE, PROJECT_ID, PROJECT_NAME_LEGACY)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("index", "trajectory"),
    project_params(FIXTURE),
    ids=project_ids(FIXTURE),
)
async def test_trajectories_p01(index: int, trajectory: dict):
    await replay_project_trajectory(FIXTURE, index, trajectory)
