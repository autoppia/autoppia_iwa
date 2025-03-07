import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))
from autoppia_iwa.src.demo_webs.classes import WebProject
from modules.webs_demo.web_1_demo_django_jobs.events.events import EVENTS_ALLOWED as events_allowed_web_1
from modules.webs_demo.web_1_demo_django_jobs.events.events import RELEVANT_DATA as relevant_data_web_1

from .utils import get_backend_url, get_frontend_url

# from .projects.cinema_1.main import cinema_project

# demo_web_projects = [cinema_project]

# test_demo_web_projects = [WebProject(id="autoppia", name="Autoppia", backend_url="", frontend_url="https://www.autoppia.com", is_web_real=True, events=[], relevant_data={})]
web_1_demo_projects = WebProject(
    id="jobs",
    name="Jobs Demo Website",
    frontend_url=get_frontend_url(index=0),
    backend_url=get_backend_url(index=0),
    events=events_allowed_web_1,
    relevant_data=relevant_data_web_1,
)
