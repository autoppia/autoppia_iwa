from autoppia_iwa.src.demo_webs.classes import WebProject
from modules.webs_demo.web_3_demo_movies.export import USE_CASES, EVENTS , RELEVANT_DATA, MODELS
from ..utils import get_frontend_url, get_backend_url

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
