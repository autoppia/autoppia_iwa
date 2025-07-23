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
    BenchmarkConfig,
    setup_logging,
)
from autoppia_iwa.src.shared.utils_entrypoints.metrics import TimingMetrics
from autoppia_iwa.src.shared.utils_entrypoints.results import (
    plot_results,
    plot_task_comparison,
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

PROJECTS_TO_RUN: list[WebProject] = [
    # demo_web_projects[0],
    # demo_web_projects[1],
    # demo_web_projects[2],
    # demo_web_projects[3],
    # demo_web_projects[4],
    demo_web_projects[5],
    demo_web_projects[7],
]
AGENTS: list[IWebAgent] = [
    ApifiedWebAgent(id="2", name="AutoppiaAgent1", host="127.0.0.1", port=5000, timeout=120),
    # ApifiedWebAgent(id="3", name="AutoppiaAgent2", host="127.0.0.1", port=7000, timeout=120),
]

config = BenchmarkConfig(projects_to_run=PROJECTS_TO_RUN, agents=AGENTS)

setup_logging("benchmark.log")
solution_cache = ConsolidatedSolutionCache(str(config.solutions_cache_dir))
visualizer = SubnetVisualizer()
SEM = asyncio.Semaphore(config.max_parallel_agent_calls)

# Global accumulator for per-agent overall (all projects)
AGENT_GLOBALS: dict[str, dict[str, float | int]] = defaultdict(lambda: {"success": 0, "total": 0, "time_sum": 0.0, "time_cnt": 0})

# ---------------------------------------------------------------------------
# Task generation
# ---------------------------------------------------------------------------


@visualize_task(visualizer)
async def generate_tasks(project: WebProject, tasks_data: TaskData | None = None) -> list[Task]:
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
        num_of_use_cases=config.num_of_use_cases,
    )


# ---------------------------------------------------------------------------
# Solution & evaluation helpers
# ---------------------------------------------------------------------------

ASYNC_GIF_RUN = "benchmark_run"


def _gif_path(agent_name: str, task_id: str, run_no: int) -> str:
    return str(config.recordings_dir / agent_name / f"{task_id}_run_{run_no}.gif")


async def _save_gif(b64: str, task_id: str, agent_name: str, run_no: int) -> None:
    path = config.recordings_dir / agent_name
    path.mkdir(exist_ok=True)
    with open(_gif_path(agent_name, task_id, run_no), "wb") as fh:
        fh.write(base64.b64decode(b64))
    logger.info(f"GIF saved for {agent_name} -> {task_id}")


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
                agent_name = next((a.name for a in config.agents if a.id == res.web_agent_id), "unknown")
                await _save_gif(res.gif_recording, task.id, agent_name, 0)
    return results


async def generate_solution(
    project: WebProject,
    agent: IWebAgent,
    task: Task,
    timing: TimingMetrics,
):
    async with SEM:
        backend = BackendDemoWebService(project)
        await backend.reset_database()
        try:
            if config.use_cached_solutions:
                cached = await solution_cache.load_solution(task.id, agent.id)
                if cached and cached.actions:
                    return cached

            start = time.time()
            prepared_task = task.prepare_for_agent(agent.id)
            solution = await agent.solve_task(prepared_task)
            task_solution = TaskSolution(task_id=task.id, actions=solution.actions or [], web_agent_id=agent.id)
            task_solution.actions = task_solution.replace_web_agent_id()
            timing.record_solution_time(agent.id, task.id, time.time() - start)
            solution_cache.save_solution(task_solution, agent.id, agent.name)
            return task_solution
        except Exception as exc:
            logger.error(f"{agent.name} failed on {task.id}: {exc!r}")
            return None
        finally:
            await backend.close()


async def run_evaluation(project: WebProject, tasks: list[Task], timing: TimingMetrics, run_no: int):
    aggregated: dict[str, dict[str, dict]] = {}
    for task in tasks:
        sols = await asyncio.gather(*[generate_solution(project, ag, task, timing) for ag in config.agents])
        eval_res = await evaluate_multiple_solutions(project, task, sols, ASYNC_GIF_RUN)
        for ev in eval_res:
            uc = getattr(task.use_case, "name", "Unknown")
            aggregated.setdefault(ev.web_agent_id, {})[task.id] = {"prompt": task.prompt, "score": ev.final_score, "task_use_case": uc}

    # print_performance_statistics(aggregated, config.agents, timing)
    if config.plot_benchmark_results:
        plot_results(aggregated, config.agents, timing, str(config.output_dir))
        plot_task_comparison(aggregated, config.agents, tasks, str(config.output_dir))
    if config.save_evaluation_results:
        save_results_to_json(aggregated, config.agents, timing, str(config.output_dir))
    return aggregated


# ---------------------------------------------------------------------------
# Stats helper
# ---------------------------------------------------------------------------


def show_stats(all_runs: list[dict], project: WebProject, timing: TimingMetrics) -> None:
    """Generate per-agent → per-project stats plus per-agent overall."""
    per_agent_scores: defaultdict[str, defaultdict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    per_agent_times: defaultdict[str, defaultdict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    for run in all_runs:
        for agent_id, task_dict in run.items():
            agent_name = next((a.name for a in config.agents if a.id == agent_id), agent_id)
            for task_id, res in task_dict.items():
                uc = res["task_use_case"].upper()
                per_agent_scores[agent_name][uc].append(res["score"])
                sol_time = timing.solution_times.get(agent_id, {}).get(task_id, 0)
                per_agent_times[agent_name][uc].append(sol_time)

    json_root: dict = {"agents": {}}

    logger.info(f"\n=== SUMMARY for project {project.name} ===")
    for agent in config.agents:
        a_name = agent.name
        uc_block = {}
        scores_flat: list[float] = []
        time_flat: list[float] = []

        for uc, scores in per_agent_scores[a_name].items():
            times = per_agent_times[a_name][uc]
            succ = sum(1 for s in scores if s == 1.0)
            tot = len(scores)
            avg_time = sum(times) / len(times) if times else 0.0
            uc_block[uc] = {
                "success_count": succ,
                "total": tot,
                "success_rate": round(succ / tot, 3) if tot else 0,
                "avg_solution_time": round(avg_time, 3),
            }
            scores_flat.extend(scores)
            time_flat.extend(times)

        succ_all = sum(1 for s in scores_flat if s == 1.0)
        tot_all = len(scores_flat)
        avg_all_time = sum(time_flat) / len(time_flat) if time_flat else 0.0
        rate_all = succ_all / tot_all if tot_all else 0.0

        logger.info(f"{a_name:<20} | {rate_all * 100:6.2f}% ({succ_all}/{tot_all}) | avg {avg_all_time:.2f}s")

        json_root.setdefault("agents", {}).setdefault(a_name, {})[project.name] = {
            "use_cases": uc_block,
            "overall": {
                "success_count": succ_all,
                "total": tot_all,
                "success_rate": round(rate_all, 3),
                "avg_solution_time": round(avg_all_time, 3),
            },
        }

        # update agent-level global totals
        g = AGENT_GLOBALS[a_name]
        g["success"] += succ_all
        g["total"] += tot_all
        g["time_sum"] += sum(time_flat)
        g["time_cnt"] += len(time_flat)

    # write per-project file
    stub = project.name.lower().replace(" ", "_")
    if stub == "autoppia_cinema":
        stub = "autoppia_cinema"
    (PROJECT_BASE_DIR / f"{stub}_stats.json").write_text(json.dumps(json_root, indent=2))
    logger.info(f"Stats written to {stub}_stats.json")


def write_agent_overalls() -> None:
    """Write one file with overall metrics per agent (across all projects)."""
    root: dict = {"agents": {}}
    for agent in AGENT_GLOBALS:
        g = AGENT_GLOBALS[agent]
        if g["total"]:
            rate = g["success"] / g["total"]
            avg_t = g["time_sum"] / g["time_cnt"] if g["time_cnt"] else 0.0
            root["agents"][agent] = {
                "overall": {
                    "success_count": g["success"],
                    "total": g["total"],
                    "success_rate": round(rate, 3),
                    "avg_solution_time": round(avg_t, 3),
                }
            }
    overall_path = PROJECT_BASE_DIR / "agents_overall_stats.json"
    overall_path.write_text(json.dumps(root, indent=2))
    logger.info(f"Per-agent overall stats written to {overall_path}")


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------


async def main() -> None:
    logger.info("Starting benchmark ...")
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
                logger.warning(f"No tasks for {proj.name} - skipping run")
        show_stats(all_runs, proj, timing)

    logger.success("Benchmark finished ✔")


if __name__ == "__main__":
    asyncio.run(main())
