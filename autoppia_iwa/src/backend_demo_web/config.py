import sys
from pathlib import Path

from autoppia_iwa.src.backend_demo_web.classes import WebProject

sys.path.append(str(Path(__file__).resolve().parents[3]))

from autoppia_iwa.config.config import DEMO_WEBS_ENDPOINT, DEMO_WEBS_STARTING_PORT
from modules.webs_demo.web_1_demo_django_jobs.events.events import EVENTS_ALLOWED as events_allowed_web_1
from autoppia_iwa.src.web_analysis.application.web_analysis_pipeline import WebAnalysisPipeline
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis
from typing import Optional
from dependency_injector.wiring import Provide
from autoppia_iwa.src.llms.domain.interfaces import ILLMService
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.shared.infrastructure.databases.base_mongo_repository import (
    BaseMongoRepository)


def get_frontend_url(index):
    return f"{DEMO_WEBS_ENDPOINT}:{str(8000 + index)}"


def get_backend_url(index: int, symetric=True):
    if symetric:
        return f"{DEMO_WEBS_ENDPOINT}:{str(DEMO_WEBS_STARTING_PORT + (index))}"
    else:
        return f"{DEMO_WEBS_ENDPOINT}:{str(DEMO_WEBS_STARTING_PORT + (index + 1))}"


demo_web_projects = [
    WebProject(
        name="jobs",
        frontend_url=get_frontend_url(index=0),
        backend_url=get_backend_url(index=0),
        events_to_check=events_allowed_web_1,
    )
    # ),
    # DemoWebProject(
    #     name="angular",
    #     frontend_url=get_frontend_url(index=1),
    #     backend_url=get_backend_url(index=1, symetric=False),
    #     events_to_check=events_allowed_web_2,
    # ),
]


def initialize_demo_webs_projects():
    for demo_web_project in demo_web_projects:
        _load_web_analysis(demo_web_project)
    return demo_web_projects


def initialize_test_demo_web_projects():
    test_demo_web_projects = [
        WebProject(
            name="Autoppia",
            backend_url="",
            frontend_url="https://www.autoppia.com",
            is_real_web=True,
            events=[],
            data_classes={}
        )
    ]
    for test_demo_web_project in test_demo_web_projects:
        _load_web_analysis(test_demo_web_project)
    return test_demo_web_projects


def _run_web_analysis(demo_web_project:WebProject, llm_service: ILLMService = Provide[DIContainer.llm_service],
                      web_analysis_repository: BaseMongoRepository = Provide[DIContainer.analysis_repository]) -> Optional[DomainAnalysis]:
    """
    Executes the web analysis pipeline to gather information from the target page.
    """
    analyzer = WebAnalysisPipeline(
        start_url=demo_web_project.frontend_url, 
        llm_service=llm_service,
        analysis_repository=web_analysis_repository
    )
    return analyzer.analyze(
        save_results_in_db=True,
        enable_crawl=True,
    )


def _load_web_analysis(demo_web_project:WebProject):
    web_analysis:DomainAnalysis = _run_web_analysis(demo_web_project)
    demo_web_project.web_analysis = web_analysis
    demo_web_project.urls = web_analysis.urls
