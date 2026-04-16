import sys
from pathlib import Path

from .classes import WebProject
from .projects.p01_autocinema.main import autocinema_project
from .projects.p02_autobooks.main import autobooks_project
from .projects.p03_autozone.main import autozone_project
from .projects.p04_autodining.main import autodining_project
from .projects.p05_autocrm.main import crm_project
from .projects.p06_automail.main import automail_project
from .projects.p07_autodelivery.main import autodelivery_project
from .projects.p08_autolodge.main import lodge_project
from .projects.p09_autoconnect.main import connect_project
from .projects.p10_autowork.main import work_project
from .projects.p11_autocalendar.main import autocalendar_project
from .projects.p12_autolist.main import autolist_project
from .projects.p13_autodrive.main import drive_project
from .projects.p14_autohealth.main import health_project
from .projects.p15_autostats.main import autostats_project
from .projects.p16_autodiscord.main import discord_project

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
    autostats_project,
    discord_project,
]
