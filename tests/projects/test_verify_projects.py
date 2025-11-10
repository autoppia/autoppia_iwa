from pathlib import Path

import pytest

from modules.web_verification.verify_project import SECTION_PROCEDURAL, verify_project

PROJECTS_DIR = Path("autoppia_iwa/src/demo_webs/projects")
PROJECT_SLUGS = sorted(
    [
        path.name
        for path in PROJECTS_DIR.iterdir()
        if path.is_dir() and not path.name.startswith("__") and not path.name.startswith(".")
    ]
)


@pytest.mark.parametrize("project_slug", PROJECT_SLUGS)
def test_project_structures_have_valid_webproject(project_slug):
    report, web_project = verify_project(project_slug)
    assert web_project is not None, f"{project_slug} should expose a WebProject instance"
    procedural = report.sections.get(SECTION_PROCEDURAL)
    assert procedural is not None and procedural.ok, f"{project_slug} procedural checks failed"
