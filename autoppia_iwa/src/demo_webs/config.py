import sys
from pathlib import Path

from .projects.cinema_1.main import cinema_project

sys.path.append(str(Path(__file__).resolve().parents[3]))


# from modules.webs_demo.web_1_demo_django_jobs.events.events import RELEVANT_DATA as relevant_data_web_1


# from .utils import get_backend_url, get_frontend_url

demo_web_projects = [cinema_project]
