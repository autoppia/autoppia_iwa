"""
Code-first entrypoint: configure projects, agents, runs, and options here.
Then run with:  python -m entrypoints.benchmark.run
"""

import asyncio

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.config import demo_web_projects

# from autoppia_iwa.src.web_analysis.domain.classes
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.web_voyager_utils import load_real_tasks
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_analysis.application.web_analysis_pipeline import WebAnalysisPipeline

# =========================
# 💡 Code configuration
# =========================

# 1) Agents (ports where your agents are listening)
AGENTS = [
    # ApifiedWebAgent(id="1", name="AutoppiaAgent1", host="127.0.0.1", port=5000, timeout=120),
    # ApifiedWebAgent(id="2", name="AutoppiaAgent2", host="127.0.0.1", port=7000, timeout=120),
    ApifiedWebAgent(id="2", name="BrowserUse-OpenAI", host="127.0.0.1", port=5000, timeout=120),
]

# 2) Projects to evaluate (by id from demo_web_projects)
PROJECT_IDS = [
    # "autocinema",
    # "autobooks",
    # "autozone",
    # "autodining",
    # "autocrm",
    # "automail",
    # "autodelivery",
    # "autolodge",
    "autoconnect",
    # "autowork",
    # "autocalendar",
    # "autolist",
    # "autodrive",
    # add more project ids here
]
PROJECTS = get_projects_by_ids(demo_web_projects, PROJECT_IDS)


async def _run_web_analysis(
    demo_web_project: WebProject,
    llm_service: ILLM,
):
    """
    Executes the web analysis pipeline to gather information from the target page.
    """
    analyzer = WebAnalysisPipeline(start_url=demo_web_project.frontend_url, llm_service=llm_service)
    return await analyzer.analyze(
        save_results_in_db=False,
        enable_crawl=True,
    )


async def _load_web_analysis(demo_web_project: WebProject):
    web_analysis = await _run_web_analysis(demo_web_project)
    demo_web_project.domain_analysis = web_analysis
    demo_web_project.urls = web_analysis.urls


#
num_of_urls = 1  # number of URLs to load and evaluate per project
tasks_data = load_real_tasks(num_of_urls)
REAL_PROJECTS = {t.id: WebProject(id=t.id, name=t.web_name, frontend_url=t.web, backend_url=t.web, is_web_real=True) for t in tasks_data}
#
# for td in tasks_data:
#     project = REAL_PROJECTS.get(td.id)
#     if project:
#         _load_web_analysis(project)
#         tasks = generate_tasks_for_web_project(project, td)
#         if tasks:
#             # run_evaluation(project, tasks, timing_metrics)
#             ...

is_web_real = True

# 3) Benchmark parameters
CFG = BenchmarkConfig(
    projects=REAL_PROJECTS if is_web_real else PROJECTS,
    agents=AGENTS,
    # Tasks
    use_cached_tasks=False,  # load project tasks from JSON cache if available
    prompts_per_use_case=1,
    num_use_cases=0,  # 0 = all use-cases
    # Execution
    runs=1,  # how many runs do you want?
    max_parallel_agent_calls=1,  # limit concurrency to avoid overloading agents
    use_cached_solutions=False,  # if True, skip calling agent when cached solution exists
    record_gif=False,  # if your evaluator returns GIFs
    # Persistence
    save_results_json=True,
    plot_results=False,
    evaluate_real_tasks=True,
    num_of_urls=1,
)


def main():
    """
    Main entrypoint for the benchmark.
    """
    try:
        logger.info("Initializing benchmark...")

        # Validate configuration early
        if not CFG.projects:
            logger.error("No valid projects in PROJECT_IDS.")
            return

        if not CFG.agents:
            logger.error("No agents configured in AGENTS.")
            return

        logger.info(f"Configuration: {len(CFG.projects)} projects, {len(CFG.agents)} agents, {CFG.runs} runs")

        # Create and run benchmark
        benchmark = Benchmark(CFG)
        if CFG.evaluate_real_tasks:
            asyncio.run(benchmark.run_real_tasks())
        else:
            asyncio.run(benchmark.run())

    except KeyboardInterrupt:
        logger.warning("Benchmark interrupted by user")
    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
