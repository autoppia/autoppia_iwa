import sys
from datetime import UTC, datetime
from pathlib import Path

from autoppia_iwa.config.config import DEMO_WEBS_ENDPOINT, DEMO_WEBS_STARTING_PORT

sys.path.append(str(Path(__file__).resolve().parents[3]))


def get_frontend_url(index):
    return f"{DEMO_WEBS_ENDPOINT}:{str(DEMO_WEBS_STARTING_PORT + index) + '/'}"


def get_backend_url(index: int, symmetric=True):
    if symmetric:
        return f"{DEMO_WEBS_ENDPOINT}:{str(DEMO_WEBS_STARTING_PORT + index) + '/'}"
    else:
        return f"{DEMO_WEBS_ENDPOINT}:{str(DEMO_WEBS_STARTING_PORT + index + 1) + '/'}"


def datetime_from_utc_to_local(utc_datetime: datetime) -> datetime:
    """Convert a UTC datetime to local time using system timezone."""
    if utc_datetime.tzinfo is None:
        utc_datetime = utc_datetime.replace(tzinfo=UTC)
    return utc_datetime.astimezone()  # converts to local timezone


def log_event(event):
    print("=" * 50)
    print(event)
    print("=" * 50)
