import sys
from pathlib import Path

from autoppia_iwa.config.config import DEMO_WEBS_ENDPOINT, DEMO_WEBS_STARTING_PORT
from autoppia_iwa.src.demo_webs.classes import WebProject

sys.path.append(str(Path(__file__).resolve().parents[3]))


def get_frontend_url(index):
    return f"{DEMO_WEBS_ENDPOINT}:{str(8000 + index) + '/'}"


def get_backend_url(index: int, symmetric=True):
    if symmetric:
        return f"{DEMO_WEBS_ENDPOINT}:{str(DEMO_WEBS_STARTING_PORT + index) + '/'}"
    else:
        return f"{DEMO_WEBS_ENDPOINT}:{str(DEMO_WEBS_STARTING_PORT + index + 1) + '/'}"


async def initialize_demo_webs_projects(demo_web_projects: list[WebProject]):
    # Uncomment when need the web analysis
    # for demo_web_project in demo_web_projects:
    #     await _load_web_analysis(demo_web_project)
    return demo_web_projects
