import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from .classes import WebProject
from .projects.books_2.main import books_project
from .projects.cinema_1.main import cinema_project

demo_web_projects: list[WebProject] = [cinema_project, books_project]
