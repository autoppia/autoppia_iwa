import json
import os
import sys
from pathlib import Path

from autoppia_iwa.config.config import DEMO_WEB_SERVICE_PORT, DEMO_WEBS_ENDPOINT, DEMO_WEBS_STARTING_PORT

sys.path.append(str(Path(__file__).resolve().parents[3]))


# ============================================================================
# URL GENERATION FUNCTIONS
# ============================================================================


def get_frontend_url(index):
    """Get frontend URL for a web project by its index."""
    return f"{DEMO_WEBS_ENDPOINT}:{str(DEMO_WEBS_STARTING_PORT + index) + '/'}"


def get_backend_service_url():
    """Get the shared backend service URL (webs_server on port 8090).

    All web projects share the same backend service.
    """
    return f"{DEMO_WEBS_ENDPOINT}:{DEMO_WEB_SERVICE_PORT}/"


# ============================================================================
# VERSION RETRIEVAL HELPERS
# ============================================================================


def _get_version_from_http(frontend_url: str) -> str | None:
    """Try to get version from HTTP endpoint."""
    try:
        import urllib.error
        import urllib.request

        base_url = frontend_url.rstrip("/")
        version_url = f"{base_url}/api/version"

        req = urllib.request.Request(version_url)
        req.add_header("User-Agent", "IWA-Version-Checker/1.0")
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                version = data.get("version")
                if version and version != "unknown":
                    return str(version)
    except Exception:
        pass
    return None


def _get_project_to_web_map() -> dict[str, str]:
    """Get mapping from project IDs to web folder names."""
    return {
        "autocinema": "web_1_autocinema",
        "autobooks": "web_2_autobooks",
        "autozone": "web_3_autozone",
        "autodining": "web_4_autodining",
        "autocrm": "web_5_autocrm",
        "automail": "web_6_automail",
        "autodelivery": "web_7_autodelivery",
        "autolodge": "web_8_autolodge",
        "autoconnect": "web_9_autoconnect",
        "autowork": "web_10_autowork",
        "autocalendar": "web_11_autocalendar",
        "autolist": "web_12_autolist",
        "autodrive": "web_13_autodrive",
        "autohealth": "web_14_autohealth",
        "autostats": "web_15_autostats",
    }


def _build_package_json_paths(web_folder: str) -> list[Path]:
    """Build list of possible paths to package.json."""
    possible_paths = []

    webs_demo_path = os.getenv("WEBS_DEMO_PATH")
    if webs_demo_path:
        possible_paths.append(Path(webs_demo_path) / web_folder / "package.json")

    iwa_root = Path(__file__).resolve().parents[4]
    possible_paths.append(iwa_root.parent / "autoppia_webs_demo" / web_folder / "package.json")

    current_file = Path(__file__).resolve()
    possible_paths.append(current_file.parent.parent.parent.parent.parent / "autoppia_webs_demo" / web_folder / "package.json")

    return possible_paths


def _read_version_from_package_json(package_json_path: Path) -> str | None:
    """Read version from package.json file."""
    try:
        with open(package_json_path, encoding="utf-8") as f:
            package_data = json.load(f)
            version = package_data.get("version")
            if version:
                return str(version)
    except (OSError, json.JSONDecodeError, KeyError):
        pass
    return None


def _get_version_from_filesystem(project_id: str) -> str | None:
    """Try to get version from filesystem package.json."""
    project_to_web_map = _get_project_to_web_map()
    web_folder = project_to_web_map.get(project_id)
    if not web_folder:
        return None

    possible_paths = _build_package_json_paths(web_folder)

    for package_json_path in possible_paths:
        if package_json_path.exists():
            version = _read_version_from_package_json(package_json_path)
            if version:
                return version

    return None


# ============================================================================
# VERSION RETRIEVAL FUNCTION
# ============================================================================


def get_web_version(project_id: str, frontend_url: str | None = None) -> str | None:
    """
    Get the version of a web project.

    Strategy:
    1. Try HTTP GET to {frontend_url}/api/version (runtime, deployed version)
    2. Fallback: Read package.json from filesystem (build time, local dev)

    Args:
        project_id: The project ID (e.g., "autobooks", "autodining")
        frontend_url: Optional frontend URL to query the /api/version endpoint

    Returns:
        Version string if found, None otherwise
    """
    if frontend_url:
        version = _get_version_from_http(frontend_url)
        if version:
            return version

    return _get_version_from_filesystem(project_id)


# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================


def log_event(event):
    print("=" * 50)
    print(event)
    print("=" * 50)
