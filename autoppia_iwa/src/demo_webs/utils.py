import sys
from pathlib import Path

from autoppia_iwa.config.config import (
    DEMO_WEB_SERVICE_PORT,
    DEMO_WEBS_DEPLOYMENT,
    DEMO_WEBS_ENDPOINT,
    DEMO_WEBS_STARTING_PORT,
)

sys.path.append(str(Path(__file__).resolve().parents[3]))


# Known remote endpoints for each demo project when running in REMOTE mode.
# These map the project id (see each project's main.py) to its deployed URL.
REMOTE_FRONTEND_ENDPOINTS = {
    "autocinema": "https://autocinema.autoppia.com",
    "autobooks": "https://autobooks.autoppia.com",
    "autozone": "https://autozone.autoppia.com",
    "autodining": "https://autodining.autoppia.com",
    "autocrm": "https://autocrm.autoppia.com",
    "automail": "https://automail.autoppia.com",
    "autolodge": "https://autolodge.autoppia.com",
    "autodelivery": "https://autodelivery.autoppia.com",
    "autowork": "https://autowork.autoppia.com",
    "autoconnect": "https://autoconnect.autoppia.com",
    "autocalendar": "https://autocalendar.autoppia.com",
    "autolist": "https://autolist.autoppia.com",
    "autodrive": "https://autodrive.autoppia.com",
}


def _base_endpoint() -> str:
    return DEMO_WEBS_ENDPOINT.rstrip("/")


def get_frontend_url(index: int, project_id: str | None = None):
    """Get frontend URL for a web project by its index or project id.

    In remote mode, prefer the project-specific endpoint if it is known. Otherwise,
    fall back to the base DEMO_WEBS_ENDPOINT. In local mode, derive the port from
    DEMO_WEBS_STARTING_PORT.
    """

    if DEMO_WEBS_DEPLOYMENT == "remote":
        if project_id and project_id in REMOTE_FRONTEND_ENDPOINTS:
            return f"{REMOTE_FRONTEND_ENDPOINTS[project_id].rstrip('/')}/"
        return f"{_base_endpoint()}/"

    return f"{_base_endpoint()}:{str(DEMO_WEBS_STARTING_PORT + index) + '/'}"


def get_backend_service_url():
    """Get the shared backend service URL (webs_server on port 8090).

    All web projects share the same backend service.
    """
    if DEMO_WEBS_DEPLOYMENT == "remote":
        return f"{_base_endpoint()}/"
    return f"{_base_endpoint()}:{DEMO_WEB_SERVICE_PORT}/"


def log_event(event):
    print("=" * 50)
    print(event)
    print("=" * 50)
