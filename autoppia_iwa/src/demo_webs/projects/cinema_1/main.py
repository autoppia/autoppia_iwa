from autoppia_iwa.config.config import DEMO_WEBS_ENDPOINT
from autoppia_iwa.src.demo_webs.classes import WebProject

from .events import EVENTS
from .relevant_data import RELEVANT_DATA
from .use_cases import ALL_USE_CASES

FRONTEND_URL = f"{DEMO_WEBS_ENDPOINT}:8000/"
BACKEND_URL = f"{DEMO_WEBS_ENDPOINT}:8000/"
cinema_project = WebProject(
    id="autocinema",
    name="Autoppia Cinema",
    frontend_url=FRONTEND_URL,
    backend_url=BACKEND_URL,
    events=EVENTS,
    relevant_data=RELEVANT_DATA,
    use_cases=ALL_USE_CASES,
)
