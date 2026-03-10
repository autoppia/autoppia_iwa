from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    # dotenv is optional - environment variables can be set directly
    def load_dotenv(*_args, **_kwargs):
        return None


_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def init_env(override: bool = False) -> None:
    """
    Load environment variables from the autoppia_iwa project .env.

    - override=False: respect any variables already set by the caller (e.g., subnet validator).
    - override=True: force .env values (standalone entrypoints).
    """
    load_dotenv(_PROJECT_ROOT / ".env", override=override)
