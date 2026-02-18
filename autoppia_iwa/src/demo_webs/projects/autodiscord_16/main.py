"""Web_16_autodiscord (AutoDiscord) project for IWA task and test generation.

Exposes autodiscord_project (WebProject) for the web verification pipeline and
benchmark. Frontend port index 15 maps to DEMO_WEBS_STARTING_PORT + 15 (e.g. 8015).
"""

from autoppia_iwa.src.demo_webs.classes import WebProject

from ...utils import get_backend_service_url, get_frontend_url, get_web_version
from .events import EVENTS
from .use_cases import ALL_USE_CASES

FRONTEND_PORT_INDEX = 15
_frontend_url = get_frontend_url(index=FRONTEND_PORT_INDEX)

autodiscord_project = WebProject(
    id="autodiscord",
    name="AutoDiscord",
    frontend_url=_frontend_url,
    backend_url=get_backend_service_url(),
    version=get_web_version("autodiscord", frontend_url=_frontend_url),
    events=EVENTS,
    use_cases=ALL_USE_CASES,
)
