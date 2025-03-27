from autoppia_iwa.src.demo_webs.classes import WebProject

from ...utils import get_backend_url, get_frontend_url
from .events import EVENTS
from .relevant_data import RELEVANT_DATA
from .use_cases import ALL_USE_CASES

# from .models import MODELS
# from .urls import URLS

FRONTEND_PORT_INDEX = 2
BACKEND_PORT_INDEX = 2
cinema_project = WebProject(
    id="personal_management",
    name="Autoppia Personal Management",
    frontend_url=get_frontend_url(index=FRONTEND_PORT_INDEX),
    backend_url=get_backend_url(index=BACKEND_PORT_INDEX, symmetric=True),
    events=EVENTS,
    relevant_data=RELEVANT_DATA,
    # models=MODELS,
    use_cases=ALL_USE_CASES,
    # urls=URLS,
)
