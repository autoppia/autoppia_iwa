from autoppia_iwa.src.demo_webs.classes import WebProject
from .events import EVENTS
from .relevant_data import RELEVANT_DATA
from .models import MODELS
from .use_cases import USE_CASES
from ...utils import get_frontend_url, get_backend_url

FRONTEND_PORT_INDEX = 1
BACKEND_PORT_INDEX = 1
cinema_project = WebProject(
    id="cinema",
    name="Autoppia Cinema",
    frontend_url=get_frontend_url(index=FRONTEND_PORT_INDEX),
    backend_url=get_backend_url(index=BACKEND_PORT_INDEX),
    events=EVENTS,
    relevant_data=RELEVANT_DATA,
    models=MODELS,
    use_cases=USE_CASES
)
