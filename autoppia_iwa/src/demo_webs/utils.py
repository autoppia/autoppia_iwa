import sys
from pathlib import Path

from autoppia_iwa.config.config import DEMO_WEBS_ENDPOINT, DEMO_WEBS_STARTING_PORT
from autoppia_iwa.src.demo_webs.classes import WebProject

sys.path.append(str(Path(__file__).resolve().parents[3]))


def get_frontend_url(index):
    return f"{DEMO_WEBS_ENDPOINT}:{str(DEMO_WEBS_STARTING_PORT + index) + '/'}"


def get_backend_url(index: int, symmetric=True):
    if symmetric:
        return f"{DEMO_WEBS_ENDPOINT}:{str(DEMO_WEBS_STARTING_PORT + index) + '/'}"
    else:
        return f"{DEMO_WEBS_ENDPOINT}:{str(DEMO_WEBS_STARTING_PORT + index + 1) + '/'}"

