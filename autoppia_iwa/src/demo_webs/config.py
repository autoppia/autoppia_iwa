import sys
from pathlib import Path

from .classes import WebProject
from .projects.autobooks_2.main import autobooks_project
from .projects.autocalendar_11.main import autocalendar_project
from .projects.autocinema_1.main import autocinema_project
from .projects.autoconnect_9.main import connect_project
from .projects.autocrm_5.main import crm_project
from .projects.autodelivery_7.main import autodelivery_project
from .projects.autodining_4.main import autodining_project
from .projects.autodiscord_16.main import discord_project
from .projects.autodrive_13.main import drive_project
from .projects.autohealth_14.main import health_project
from .projects.autolist_12.main import autolist_project
from .projects.autolodge_8.main import lodge_project
from .projects.automail_6.main import automail_project
from .projects.autowork_10.main import work_project
from .projects.autozone_3.main import autozone_project

sys.path.append(str(Path(__file__).resolve().parents[3]))


demo_web_projects: list[WebProject] = [
    autocinema_project,
    autobooks_project,
    autozone_project,
    autodining_project,
    crm_project,
    automail_project,
    lodge_project,
    autodelivery_project,
    work_project,
    connect_project,
    autocalendar_project,
    autolist_project,
    drive_project,
    health_project,
    discord_project,
]
