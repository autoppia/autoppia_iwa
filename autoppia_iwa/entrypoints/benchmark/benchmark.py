from __future__ import annotations

import asyncio
import base64
import time
from collections import defaultdict

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.utils.logging import setup_logging
from autoppia_iwa.entrypoints.benchmark.utils.metrics import TimingMetrics
from autoppia_iwa.entrypoints.benchmark.utils.results import (
    plot_results,
    save_results_to_json,
)
from autoppia_iwa.entrypoints.benchmark.utils.solutions import ConsolidatedSolutionCache
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.web_agents.base import IWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution

from .config import BenchmarkConfig
from .task_generation import generate_tasks_for_project


class Benchmark:
    """
    High-level orchestrator: generate tasks (cache-aware), solve with agents,
    evaluate results, and persist metrics/artifacts.
    """

    def __init__(self, cfg: BenchmarkConfig, log_file: str = "benchmark.log"):
        self.cfg = cfg
        self._sem = asyncio.Semaphore(cfg.max_parallel_agent_calls)
        self.solution_cache = ConsolidatedSolutionCache(str(cfg.solutions_cache_dir))
        self.timings = TimingMetrics()
        self._global_agent_stats: dict[str, dict[str, float | int]] = defaultdict(lambda: {"success": 0, "total": 0, "time_sum": 0.0, "time_cnt": 0})
        setup_logging(log_file)

    async def _save_gif(self, b64: str, agent_name: str, task_id: str, run_no: int) -> None:
        """
        Decode and save a base64 GIF recording for a task and agent.
        """
        p = self.cfg.recordings_dir / agent_name
        p.mkdir(exist_ok=True)
        (p / f"{task_id}_run_{run_no}.gif").write_bytes(base64.b64decode(b64))
        logger.info(f"GIF saved: {agent_name} -> {task_id}")

    async def _solve_one(self, project: WebProject, agent: IWebAgent, task, run_no: int):
        """
        Ask a single agent to solve a single task.
        Optionally use cached solution when configured.
        """
        async with self._sem:
            backend = BackendDemoWebService(project)
            await backend.reset_database()
            try:
                if self.cfg.use_cached_solutions:
                    cached = await self.solution_cache.load_solution(task.id, agent.id)
                    if cached and cached.actions:
                        return cached

                t0 = time.time()
                prepared = task.prepare_for_agent(agent.id)
                solution = await agent.solve_task(prepared)
                task_solution = TaskSolution(
                    task_id=task.id,
                    actions=solution.actions or [],
                    web_agent_id=agent.id,
                )
                # Normalize agent ids inside actions, if needed
                task_solution.actions = task_solution.replace_web_agent_id()

                self.timings.record_solution_time(agent.id, task.id, time.time() - t0)
                self.solution_cache.save_solution(task_solution, agent.id, agent.name)
                return task_solution
            except Exception as e:
                logger.error(f"{agent.name} failed on {task.id}: {e!r}")
                return None
            finally:
                await backend.close()

    async def _evaluate(self, project: WebProject, task, solutions: list[TaskSolution], run_no: int):
        """
        Evaluate all agent solutions for a single task and optionally store GIFs.
        """
        evaluator = ConcurrentEvaluator(project, EvaluatorConfig(enable_grouping_tasks=False, chunk_size=20))
        results = await evaluator.evaluate_task_solutions(task, solutions)
        if self.cfg.record_gif:
            for res in results:
                if getattr(res, "gif_recording", None):
                    agent_name = next((a.name for a in self.cfg.agents if a.id == res.web_agent_id), "unknown")
                    await self._save_gif(res.gif_recording, agent_name, task.id, run_no)
        return results

    async def _run_once(self, project: WebProject, run_no: int) -> dict:
        """
        Run a single iteration (run) for a given project:
        - Generate/load tasks
        - Solve with all agents
        - Evaluate solutions
        - Return per-agent results for this run
        """
        tasks = await generate_tasks_for_project(
            project=project,
            use_cached=self.cfg.use_cached_tasks,
            cache_dir=str(self.cfg.tasks_cache_dir),
            prompts_per_use_case=self.cfg.prompts_per_use_case,
            num_use_cases=self.cfg.num_use_cases,
        )
        if not tasks:
            logger.warning(f"No tasks for {project.name} — skipping run {run_no}")
            return {}

        # Tell the evaluator whether to record GIFs per task
        for t in tasks:
            t.should_record = self.cfg.record_gif

        per_task_results: dict = {}
        for task in tasks:
            sols = await asyncio.gather(*[self._solve_one(project, ag, task, run_no) for ag in self.cfg.agents])
            evals = await self._evaluate(project, task, sols, run_no)
            for ev in evals:
                uc = getattr(task.use_case, "name", "Unknown")
                per_task_results.setdefault(ev.web_agent_id, {})[task.id] = {
                    "prompt": task.prompt,
                    "score": ev.final_score,
                    "task_use_case": uc,
                }
        return per_task_results

    def _update_global_stats(self, evaluation_runs: list[dict]):
        """
        Aggregate per-agent stats across runs for a human-friendly log summary
        and an optional overall JSON later if you want to persist it.
        """
        per_agent_scores: dict[str, list[float]] = defaultdict(list)
        per_agent_times: dict[str, list[float]] = defaultdict(list)

        for run in evaluation_runs:
            for agent in self.cfg.agents:
                if agent.id not in run:
                    continue
                for task_id, res in run[agent.id].items():
                    per_agent_scores[agent.name].append(res["score"])
                    t = self.timings.solution_times.get(agent.id, {}).get(task_id, 0)
                    per_agent_times[agent.name].append(t)

        for a in self.cfg.agents:
            scores = per_agent_scores[a.name]
            times = per_agent_times[a.name]
            succ = sum(1 for s in scores if s == 1.0)
            tot = len(scores)
            g = self._global_agent_stats[a.name]
            g["success"] += succ
            g["total"] += tot
            g["time_sum"] += sum(times)
            g["time_cnt"] += len(times)
            rate = (succ / tot) if tot else 0.0
            avg_t = (sum(times) / len(times)) if times else 0.0
            logger.info(f"{a.name:<20} | {rate * 100:6.2f}% ({succ}/{tot}) | avg {avg_t:.2f}s")

    async def run(self):
        """
        Execute the whole benchmark across all configured projects and runs.
        """
        logger.info("Starting benchmark…")
        self.timings.start()

        for project in self.cfg.projects:
            logger.info(f"\n=== Project: {project.name} ===")
            per_project_runs: list[dict] = []

            for run_no in range(1, self.cfg.runs + 1):
                logger.info(f"Run {run_no}/{self.cfg.runs}")
                run_result = await self._run_once(project, run_no)
                if run_result:
                    per_project_runs.append(run_result)

            # Update global rollups and persist last runs results/plots if configured
            self._update_global_stats(per_project_runs)
            last = per_project_runs[-1] if per_project_runs else {}
            if last and self.cfg.save_results_json:
                save_results_to_json(last, self.cfg.agents, self.timings, str(self.cfg.output_dir))
            if last and self.cfg.plot_results:
                plot_results(last, self.cfg.agents, self.timings, str(self.cfg.output_dir))

        self.timings.end()
        logger.success("Benchmark finished ✔")
