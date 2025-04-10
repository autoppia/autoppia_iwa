from autoppia_iwa.src.demo_webs.classes import WebProject

from ...utils import get_backend_url, get_frontend_url
from .events import EVENTS
from .relevant_data import RELEVANT_DATA

FRONTEND_PORT_INDEX = 1
BACKEND_PORT_INDEX = 1
books_project = WebProject(
    id="books",
    name="Autoppia Books",
    frontend_url=get_frontend_url(index=FRONTEND_PORT_INDEX),
    backend_url=get_backend_url(index=BACKEND_PORT_INDEX, symmetric=True),
    events=EVENTS,
    relevant_data=RELEVANT_DATA,
    # models=MODELS,
    # use_cases=ALL_USE_CASES,
    # urls=URLS,
)
