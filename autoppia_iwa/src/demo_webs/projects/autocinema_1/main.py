from autoppia_iwa.src.demo_webs.classes import WebProject

from ...utils import get_backend_service_url, get_frontend_url, get_web_version
from .events import EVENTS
from .relevant_data import RELEVANT_DATA
from .use_cases import ALL_USE_CASES

FRONTEND_PORT_INDEX = 0
_frontend_url = get_frontend_url(index=FRONTEND_PORT_INDEX)
cinema_project = WebProject(
    id="autocinema",
    name="Autoppia Cinema",
    frontend_url=_frontend_url,
    backend_url=get_backend_service_url(),
    version=get_web_version("autocinema", frontend_url=_frontend_url),
    events=EVENTS,
    relevant_data=RELEVANT_DATA,
    use_cases=ALL_USE_CASES,
)
