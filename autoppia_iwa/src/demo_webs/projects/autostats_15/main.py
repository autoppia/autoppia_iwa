"""Autostats web_15 project registration."""

from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.utils import get_backend_service_url, get_frontend_url, get_web_version

from .events import EVENTS
from .use_cases import ALL_USE_CASES

FRONTEND_PORT_INDEX = 14  # web_15_autostats
_frontend_url = get_frontend_url(index=FRONTEND_PORT_INDEX)
autostats_project = WebProject(
    id="autostats",
    name="Autoppia AutoStats",
    frontend_url=_frontend_url,
    backend_url=get_backend_service_url(),
    version=get_web_version("autostats", frontend_url=_frontend_url),
    events=EVENTS,
    use_cases=ALL_USE_CASES,
)
