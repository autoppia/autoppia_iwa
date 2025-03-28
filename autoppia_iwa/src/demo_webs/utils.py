import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from dependency_injector.wiring import Provide

from autoppia_iwa.config.config import DEMO_WEBS_ENDPOINT, DEMO_WEBS_STARTING_PORT
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.infrastructure.databases.base_mongo_repository import BaseMongoRepository
from autoppia_iwa.src.web_analysis.application.web_analysis_pipeline import WebAnalysisPipeline
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis


def get_frontend_url(index):
    return f"{DEMO_WEBS_ENDPOINT}:{str(8000 + index) + '/'}"


def get_backend_url(index: int, symmetric=True):
    if symmetric:
        return f"{DEMO_WEBS_ENDPOINT}:{str(DEMO_WEBS_STARTING_PORT + index) + '/'}"
    else:
        return f"{DEMO_WEBS_ENDPOINT}:{str(DEMO_WEBS_STARTING_PORT + index + 1) + '/'}"


async def initialize_demo_webs_projects(demo_web_projects: list[WebProject]):
    for demo_web_project in demo_web_projects:
        await _load_web_analysis(demo_web_project)
    return demo_web_projects


async def _run_web_analysis(
    demo_web_project: WebProject, llm_service: ILLM = Provide[DIContainer.llm_service], web_analysis_repository: BaseMongoRepository = Provide[DIContainer.analysis_repository]
) -> DomainAnalysis | None:
    """
    Executes the web analysis pipeline to gather information from the target page.
    """
    analyzer = WebAnalysisPipeline(start_url=demo_web_project.frontend_url, llm_service=llm_service, analysis_repository=web_analysis_repository)
    return await analyzer.analyze(
        save_results_in_db=True,
        enable_crawl=True,
    )


async def _load_web_analysis(demo_web_project: WebProject):
    web_analysis: DomainAnalysis = await _run_web_analysis(demo_web_project)
    demo_web_project.domain_analysis = web_analysis
    demo_web_project.urls = web_analysis.urls
