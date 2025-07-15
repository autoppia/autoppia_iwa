from autoppia_iwa.src.demo_webs.classes import WebProject

from ...utils import get_backend_url, get_frontend_url
from .events import EVENTS
from .use_cases import ALL_USE_CASES

FRONTEND_PORT_INDEX = 4
BACKEND_PORT_INDEX = 4
crm_project = WebProject(
    id="crm",
    name="Autoppia CRM",
    frontend_url=get_frontend_url(index=FRONTEND_PORT_INDEX),
    backend_url=get_backend_url(index=BACKEND_PORT_INDEX, symmetric=True),
    events=EVENTS,
    use_cases=ALL_USE_CASES,
)
