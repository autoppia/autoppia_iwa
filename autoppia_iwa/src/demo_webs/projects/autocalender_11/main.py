from autoppia_iwa.src.demo_webs.classes import WebProject

from ...utils import get_backend_service_url, get_frontend_url
from .events import EVENTS
from .use_cases import ALL_USE_CASES

FRONTEND_PORT_INDEX = 10
autocalendar_project = WebProject(
    id="autocalendar",
    name="Autoppia Calender",
    frontend_url=get_frontend_url(index=FRONTEND_PORT_INDEX),
    backend_url=get_backend_service_url(),
    events=EVENTS,
    use_cases=ALL_USE_CASES,
)
