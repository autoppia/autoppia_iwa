from autoppia_iwa.config.config import DEMO_WEBS_ENDPOINT
from autoppia_iwa.src.demo_webs.classes import WebProject

from .events import CALENDAR_EVENTS
from .use_cases import ALL_USE_CASES

FRONTEND_URL = f"{DEMO_WEBS_ENDPOINT}:8009/"
BACKEND_URL = f"{DEMO_WEBS_ENDPOINT}:8009/"

autocalendar_project = WebProject(
    id="autocalendar",
    name="Autoppia Calender",
    frontend_url=FRONTEND_URL,
    backend_url=BACKEND_URL,
    events=CALENDAR_EVENTS,
    use_cases=ALL_USE_CASES,
)
