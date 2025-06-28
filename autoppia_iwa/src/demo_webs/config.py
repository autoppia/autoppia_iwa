import sys
from pathlib import Path

from .classes import WebProject
from .projects.books_2.main import books_project
from .projects.cinema_1.main import cinema_project
from .projects.dining_4.main import dining_project
from .projects.omnizone_3.main import omnizone_project

sys.path.append(str(Path(__file__).resolve().parents[3]))


demo_web_projects: list[WebProject] = [
    cinema_project,
    books_project,
    omnizone_project,
    dining_project,
]
