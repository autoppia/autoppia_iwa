import sys
from pathlib import Path

from .classes import WebProject
from .projects.autocrm_5.main import crm_project
from .projects.autolodge_8.main import lodge_project
from .projects.automail_6.main import automail_project
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
    crm_project,
    automail_project,
    lodge_project,
]
