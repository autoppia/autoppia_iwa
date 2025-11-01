from autoppia_iwa.config.config import DEMO_WEBS_ENDPOINT
from autoppia_iwa.src.demo_webs.classes import WebProject

from .events import EVENTS
from .use_cases import ALL_USE_CASES

FRONTEND_URL = f"{DEMO_WEBS_ENDPOINT}:8002/"
BACKEND_URL = f"{DEMO_WEBS_ENDPOINT}:8090/"
omnizone_project = WebProject(
    id="autozone",
    name="Autoppia AutoZone",
    frontend_url=FRONTEND_URL,
    backend_url=BACKEND_URL,
    events=EVENTS,
    use_cases=ALL_USE_CASES,
)
