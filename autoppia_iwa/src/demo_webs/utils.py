import sys
from pathlib import Path

from autoppia_iwa.config.config import DEMO_WEB_SERVICE_PORT, DEMO_WEBS_ENDPOINT, DEMO_WEBS_STARTING_PORT

sys.path.append(str(Path(__file__).resolve().parents[3]))


def get_frontend_url(index):
    """Get frontend URL for a web project by its index."""
    return f"{DEMO_WEBS_ENDPOINT}:{str(DEMO_WEBS_STARTING_PORT + index) + '/'}"


def get_backend_service_url():
    """Get the shared backend service URL (webs_server on port 8090).

    All web projects share the same backend service.
    """
    return f"{DEMO_WEBS_ENDPOINT}:{DEMO_WEB_SERVICE_PORT}/"


def log_event(event):
    print("=" * 50)
    print(event)
    print("=" * 50)
