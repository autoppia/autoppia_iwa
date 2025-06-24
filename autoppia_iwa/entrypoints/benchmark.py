from __future__ import annotations

import asyncio
import base64
import json
import time
from collections import defaultdict

from loguru import logger

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.application.tasks.local.tests.test_generation_pipeline import (
    LocalTestGenerationPipeline,
)
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.demo_webs.utils import initialize_demo_webs_projects
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.shared.utils_entrypoints.benchmark_utils import (
    BenchmarConfig,
    setup_logging,
)
from autoppia_iwa.src.shared.utils_entrypoints.metrics import TimingMetrics
from autoppia_iwa.src.shared.utils_entrypoints.results import (
    plot_results,
    plot_task_comparison,
    print_performance_statistics,
    save_results_to_json,
)
from autoppia_iwa.src.shared.utils_entrypoints.solutions import ConsolidatedSolutionCache
from autoppia_iwa.src.shared.utils_entrypoints.tasks import generate_tasks_for_web_project
from autoppia_iwa.src.shared.visualizator import (
    SubnetVisualizer,
    visualize_list_of_evaluations,
    visualize_task,
)
from autoppia_iwa.src.shared.web_voyager_utils import TaskData
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.base import IWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution

# ---------------------------------------------------------------------------
# Configuration & globals
# ---------------------------------------------------------------------------

PROJECTS_TO_RUN: list[WebProject] = [demo_web_projects[0]]
AGENTS: list[IWebAgent] = [ApifiedWebAgent(id="3", name="AutoppiaAgent", host="127.0.0.1", port=5000, timeout=120)]

config = BenchmarConfig(projects_to_run=PROJECTS_TO_RUN, agents=AGENTS)

setup_logging("benchmark.log")
solution_cache = ConsolidatedSolutionCache(str(config.solutions_cache_dir))
visualizer = SubnetVisualizer()
SEM = asyncio.Semaphore(config.max_parallel_agent_calls)

# ---------------------------------------------------------------------------
# Task generation
# ---------------------------------------------------------------------------


@visualize_task(visualizer)
async def generate_tasks(project: WebProject, tasks_data: TaskData | None = None) -> list[Task]:
    """Generate (or load cached) tasks for a given project."""

    if config.evaluate_real_tasks and tasks_data:
        single = Task(url=tasks_data.web, prompt=tasks_data.ques, is_web_real=True)
        return await LocalTestGenerationPipeline(project).add_tests_to_tasks([single])

    if not project.use_cases:
        logger.warning(f"Project '{project.name}' has no use cases, skipping.")
        return []

    return await generate_tasks_for_web_project(
        project,
        config.use_cached_tasks,
        str(config.tasks_cache_dir),
        prompts_per_use_case=config.prompt_per_use_case,
        num_of_use_cases=getattr(config, "num_of_use_cases", 1),
    )


# ---------------------------------------------------------------------------
# Solution & evaluation helpers
# ---------------------------------------------------------------------------


aSYNC_GIF_RUN = "benchmark_run"


def _gif_path(agent_name: str, task_id: str, run_no: int) -> str:
    return str(config.recordings_dir / agent_name / f"{task_id}_run_{run_no}.gif")


async def _save_gif(b64: str, task_id: str, agent_name: str, run_no: int) -> None:
    path = config.recordings_dir / agent_name
    path.mkdir(exist_ok=True)
    with open(_gif_path(agent_name, task_id, run_no), "wb") as fh:
        fh.write(base64.b64decode(b64))
    logger.info(f"GIF saved for {agent_name} → {task_id}")


@visualize_list_of_evaluations(visualizer)
async def evaluate_multiple_solutions(
    project: WebProject,
    task: Task,
    sols: list[TaskSolution],
    validator_id: str | None = None,
):
    evaluator = ConcurrentEvaluator(project, EvaluatorConfig(enable_grouping_tasks=False, chunk_size=20))
    results = await evaluator.evaluate_task_solutions(task, sols)

    if config.return_evaluation_gif:
        for res in results:
            if res.gif_recording:
                agent = next((a.name for a in config.agents if a.id == res.web_agent_id), "unknown")
                await _save_gif(res.gif_recording, task.id, agent, 0)
    return results


async def generate_solution(project: WebProject, agent: IWebAgent, task: Task, timing: TimingMetrics):
    async with SEM:
        backend = BackendDemoWebService(project)
        await backend.reset_database()
        try:
            if config.use_cached_solutions:
                cached = await solution_cache.load_solution(task.id, agent.id)
                if cached and cached.actions:
                    return cached

            start = time.time()
            prepared = task.prepare_for_agent(agent.id)
            sol = await agent.solve_task(prepared)
            task_sol = TaskSolution(task_id=task.id, actions=sol.actions or [], web_agent_id=agent.id)
            task_sol.actions = task_sol.replace_web_agent_id()
            timing.record_solution_time(agent.id, task.id, time.time() - start)
            solution_cache.save_solution(task_sol, agent.id, agent.name)
            return task_sol
        except Exception as exc:
            logger.error(f"{agent.name} failed on {task.id}: {exc!r}")
            return None
        finally:
            await backend.close()


async def run_evaluation(project: WebProject, tasks: list[Task], timing: TimingMetrics, run_no: int):
    aggregated: dict[str, dict[str, dict]] = {}
    for task in tasks:
        sols = await asyncio.gather(*[generate_solution(project, ag, task, timing) for ag in config.agents])
        eval_res = await evaluate_multiple_solutions(project, task, sols, aSYNC_GIF_RUN)
        for ev in eval_res:
            uc = getattr(task.use_case, "name", "Unknown")
            aggregated.setdefault(ev.web_agent_id, {})[task.id] = {"score": ev.final_score, "task_use_case": uc}

    print_performance_statistics(aggregated, config.agents, timing)
    if config.plot_benchmark_results:
        plot_results(aggregated, config.agents, timing, str(config.output_dir))
        plot_task_comparison(aggregated, config.agents, tasks, str(config.output_dir))
    if config.save_evaluation_results:
        save_results_to_json(aggregated, config.agents, timing, str(config.output_dir))
    return aggregated


# ---------------------------------------------------------------------------
# Stats helper
# ---------------------------------------------------------------------------


def show_stats(all_runs: list[dict], project: WebProject) -> None:
    """Aggregate success rates (per agent & overall) and write JSON."""

    per_agent: defaultdict[str, defaultdict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for run in all_runs:
        for aid, td in run.items():
            agent_name = next((a.name for a in config.agents if a.id == aid), aid)
            for res in td.values():
                per_agent[agent_name][res["task_use_case"].upper()].append(res["score"])

    logger.info(f"\n=== SUMMARY for {project.name} ===")
    overall_success = overall_total = 0
    for agent in config.agents:
        scores = [s for lst in per_agent[agent.name].values() for s in lst]
        success = sum(1 for s in scores if s == 1.0)
        total = len(scores)
        rate = success / total * 100 if total else 0.0
        overall_success += success
        overall_total += total
        logger.info(f"{agent.name:<20} | {rate:6.2f}% ({success}/{total})")

    overall_rate = overall_success / overall_total * 100 if overall_total else 0.0
    logger.info(f"{'OVERALL':<20} | {overall_rate:6.2f}% ({overall_success}/{overall_total})")

    json_ready = {
        "agents": {
            ag: {
                uc: {
                    "success_count": sum(1 for s in scores if s == 1.0),
                    "total": len(scores),
                    "success_rate": round(sum(1 for s in scores if s == 1.0) / len(scores), 3) if scores else 0,
                }
                for uc, scores in uc_dict.items()
            }
            for ag, uc_dict in per_agent.items()
        },
        "overall": {
            "success_count": overall_success,
            "total": overall_total,
            "success_rate": round(overall_success / overall_total, 3) if overall_total else 0,
        },
    }

    file_stub = project.name.lower().replace(" ", "_")
    if file_stub == "autoppia_cinema":
        file_stub = "autoppia_cinama"  # user-requested spelling
    out_path = PROJECT_BASE_DIR / f"{file_stub}_stats.json"
    out_path.write_text(json.dumps(json_ready, indent=2))
    logger.info(f"Stats written to {out_path}")


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------


async def main() -> None:
    logger.info("Starting benchmark …")
    AppBootstrap()
    timing = TimingMetrics()

    await initialize_demo_webs_projects(demo_web_projects)

    for proj in config.projects_to_run:
        all_runs: list[dict] = []
        for run_idx in range(1, config.num_runs + 1):
            timing.start()
            tasks = await generate_tasks(proj)
            for t in tasks:
                t.should_record = config.return_evaluation_gif
            if tasks:
                all_runs.append(await run_evaluation(proj, tasks, timing, run_idx))
            else:
                logger.warning(f"No tasks for {proj.name}  skipping run")
        show_stats(all_runs, proj)

    logger.success("Benchmark finished ✔")


if __name__ == "__main__":
    asyncio.run(main())
