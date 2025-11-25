from autoppia_iwa.src.demo_webs.classes import WebProject
from ...utils import get_frontend_url
from .events import EVENTS
from .use_cases import ALL_USE_CASES

autodining_project = WebProject(
    id="autodining",
    name="Autoppia Dining",
    frontend_url=get_frontend_url(index=3),
    backend_url="${AUTOPPIA_BACKEND_URL:-http://localhost:8090}/",
    events=EVENTS,
    use_cases=ALL_USE_CASES,
    relevant_data={"summary": "Restaurant reservation marketplace with dynamic menus and booking flow.", "owner": "autoppia-core", "contact": "deck@autoppia.com", "seed_notes": "Use ?seed=<id> to vary restaurant data, menus, and booking availability."},
)
