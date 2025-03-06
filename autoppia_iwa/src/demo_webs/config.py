import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))
from autoppia_iwa.src.demo_webs.classes import WebProject
from .projects.cinema_1.main import cinema_project

demo_web_projects = [
    cinema_project
]

test_demo_web_projects = [
    WebProject(
        id="autoppia",
        name="Autoppia", 
        backend_url="", 
        frontend_url="https://www.autoppia.com", 
        is_web_real=True, 
        events=[], 
        relevant_data={}
    )
]
