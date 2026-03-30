from autoppia_iwa.src.demo_webs.classes import WebProject

from ...utils import get_backend_service_url, get_frontend_url, get_web_version
from .events import EVENTS
from .use_cases import ALL_USE_CASES

FRONTEND_PORT_INDEX = 7
_frontend_url = get_frontend_url(index=FRONTEND_PORT_INDEX)
lodge_project = WebProject(
    id="autolodge",
    name="Autoppia Lodge",
    frontend_url=_frontend_url,
    backend_url=get_backend_service_url(),
    version=get_web_version("autolodge", frontend_url=_frontend_url),
    events=EVENTS,
    use_cases=ALL_USE_CASES,
)
