"""
Benchmark orchestrator: generate tasks, run agents, evaluate, persist results.

Parallelization strategy:
- Each (agent, task) pair runs as an independent evaluation job
- Each job gets a unique web_agent_id for DB/event isolation on the shared backend
- A semaphore controls max concurrent browser instances (max_parallel_evaluations)
- Agent endpoints can handle multiple concurrent requests — no bottleneck there

Usage:
    config = BenchmarkConfig(
        projects=[autocinema_project],
        agents=[ApifiedWebAgent(base_url="http://localhost:8000")],
        max_parallel_evaluations=4,  # 4 browsers at once
    )
    results = await Benchmark(config).run()
"""

import asyncio
import contextlib
import time
import uuid
from datetime import datetime
from typing import Any

from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.data_generation.tasks.pipeline import TaskGenerationPipeline
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.benchmark.config import BenchmarkConfig
from autoppia_iwa.src.evaluation.benchmark.reporting import (
    aggregate_project_results,
    build_run_report,
    build_task_result,
    build_terminal_report,
    save_run_report,
)
from autoppia_iwa.src.evaluation.benchmark.trace_writer import TraceWriter
from autoppia_iwa.src.evaluation.benchmark.utils.logging import setup_logging
from autoppia_iwa.src.evaluation.benchmark.utils.metrics import TimingMetrics
from autoppia_iwa.src.evaluation.benchmark.utils.task_generation import load_tasks_from_json, save_tasks_to_json
from autoppia_iwa.src.evaluation.classes import EvaluationResult, EvaluationStats, EvaluatorConfig
from autoppia_iwa.src.evaluation.concurrent_evaluator import ConcurrentEvaluator
from autoppia_iwa.src.evaluation.stateful_evaluator import TaskExecutionSession
from autoppia_iwa.src.web_agents.classes import IWebAgent, TaskSolution, sanitize_html


def _make_eval_id(agent_id: str, task_id: str, run_idx: int) -> str:
    """Generate a unique web_agent_id for isolation. Each parallel eval gets its own."""
    short = uuid.uuid4().hex[:8]
    return f"{agent_id}-{short}-r{run_idx}"


class Benchmark:
    """
    Runs agents against generated tasks and produces evaluation results.

    Parallelizes evaluations across tasks and agents using asyncio.gather
    with a semaphore to limit concurrent browser instances. Each evaluation
    gets a unique web_agent_id so the backend isolates DB state and events.
    """

    def __init__(self, config: BenchmarkConfig) -> None:
        self.config = config
        self._sem = asyncio.Semaphore(config.max_parallel_evaluations)
        self._timing = TimingMetrics()
        self._results: dict[str, Any] = {}
        self._project_reports: dict[str, Any] = {}
        self._trace_writer: TraceWriter | None = None
        self.last_run_report: dict[str, Any] | None = None
        self.last_results_path: str | None = None

        self._validate()
        config.log_file.parent.mkdir(parents=True, exist_ok=True)
        setup_logging(str(config.log_file))

    def _validate(self) -> None:
        if not self.config.projects:
            raise ValueError("No projects configured")
        if not self.config.agents:
            raise ValueError("No agents configured")
        if len({a.id for a in self.config.agents}) != len(self.config.agents):
            raise ValueError("Agent IDs must be unique")
        logger.info(
            f"Benchmark: {len(self.config.projects)} projects, "
            f"{len(self.config.agents)} agents, "
            f"{self.config.runs} runs, "
            f"mode={self.config.evaluator_mode}, "
            f"parallel={self.config.max_parallel_evaluations}"
        )

    # ── Public API ──────────────────────────────────────────────────────

    async def run(self) -> dict:
        """Execute the full benchmark. Returns per-project results dict."""
        logger.info("Starting benchmark")
        self._timing.start()

        try:
            for i, project in enumerate(self.config.projects, 1):
                logger.info(f"Project {i}/{len(self.config.projects)}: {project.name}")
                run_results = []
                for run_idx in range(1, self.config.runs + 1):
                    try:
                        result = await self._run_project(project, run_idx)
                        if result:
                            run_results.append(result)
                    except Exception as e:
                        logger.error(f"Run {run_idx} failed for {project.name}: {e}", exc_info=True)
                if run_results:
                    self._aggregate_project(project, run_results)
        finally:
            self._timing.end()

        self.last_run_report = self._build_run_report()
        if self.config.save_results_json and self._results:
            self._save_results()
        if self.config.print_summary and self._results:
            print(self.build_terminal_report())

        logger.success("Benchmark finished")
        return self._results

    def build_terminal_report(self) -> str:
        """Return a concise terminal-friendly summary of the latest run."""
        return build_terminal_report(
            self.last_run_report or {},
            config=self.config,
            results_path=self.last_results_path,
        )

    # ── Task generation ─────────────────────────────────────────────────

    async def _generate_tasks(self, project: WebProject) -> list[Task]:
        cache_dir = str(self.config.base_dir / "benchmark-output" / "cache" / "tasks")

        if self.config.use_cached_tasks:
            cached = await load_tasks_from_json(project, cache_dir)
            if cached:
                logger.info(f"Using {len(cached)} cached tasks for {project.name}")
                return cached

        config = TaskGenerationConfig(
            prompts_per_use_case=self.config.prompts_per_use_case,
            use_cases=self.config.use_cases,
            dynamic=self.config.dynamic,
        )
        tasks = await TaskGenerationPipeline(web_project=project, config=config).generate()
        if tasks:
            await save_tasks_to_json(tasks, project, cache_dir)
        return tasks

    # ── Per-project: build job matrix and run in parallel ───────────────

    async def _run_project(self, project: WebProject, run_idx: int) -> dict[str, dict[str, dict[str, Any]]]:
        tasks = await self._generate_tasks(project)
        if not tasks:
            logger.warning(f"No tasks for {project.name}, skipping")
            return {}

        for t in tasks:
            t.should_record = self.config.record_gif

        # Create trace writer for this run
        ts = datetime.now().strftime("%Y%m%dT%H%M%S")
        trace_dir = self.config.traces_dir / f"{project.id}_{ts}_r{run_idx}"
        self._trace_writer = TraceWriter(trace_dir, run_metadata={
            "project": project.id,
            "evaluator_mode": self.config.evaluator_mode,
            "max_steps": self.config.max_steps_per_task,
            "agents": [a.name for a in self.config.agents],
        })

        # Build all (agent, task) jobs and run them with concurrency control
        jobs = [
            (agent, task)
            for task in tasks
            for agent in self.config.agents
        ]

        total = len(jobs)
        logger.info(f"Running {total} evaluations ({len(tasks)} tasks x {len(self.config.agents)} agents) with max {self.config.max_parallel_evaluations} parallel")

        eval_results = await asyncio.gather(
            *[self._run_eval_job(project, agent, task, run_idx, idx, total) for idx, (agent, task) in enumerate(jobs, 1)],
            return_exceptions=True,
        )

        # Collect results
        results: dict[str, dict[str, dict[str, Any]]] = {}
        for (agent, task), ev_result in zip(jobs, eval_results):
            if isinstance(ev_result, Exception):
                logger.error(f"{agent.name} x {task.id}: {ev_result}")
                continue
            if ev_result is None:
                continue
            results.setdefault(agent.id, {})[task.id] = build_task_result(
                agent=agent,
                task=task,
                evaluation_result=ev_result,
                eval_id=getattr(ev_result.stats, "web_agent_id", None) or ev_result.web_agent_id,
                run_idx=run_idx,
            )

        # Flush traces for debugger
        if self._trace_writer:
            self._trace_writer.flush()

        return results

    # ── Single evaluation job (semaphore-guarded) ───────────────────────

    async def _run_eval_job(
        self,
        project: WebProject,
        agent: IWebAgent,
        task: Task,
        run_idx: int,
        job_num: int,
        total_jobs: int,
    ) -> EvaluationResult | None:
        """Run a single (agent, task) evaluation. Acquires semaphore for browser resources."""
        async with self._sem:
            eval_id = _make_eval_id(agent.id, task.id, run_idx)
            logger.info(f"[{job_num}/{total_jobs}] {agent.name} x {task.id} (eval_id={eval_id})")

            if self.config.evaluator_mode == "stateful":
                return await self._run_stateful(task, agent, eval_id)
            else:
                return await self._run_concurrent(project, task, agent, eval_id, run_idx)

    # ── Concurrent mode: agent returns all actions, evaluator replays ───

    async def _run_concurrent(
        self, project: WebProject, task: Task, agent: IWebAgent, eval_id: str, run_idx: int
    ) -> EvaluationResult | None:
        backend = BackendDemoWebService(project, web_agent_id=eval_id)
        try:
            await backend.reset_database(web_agent_id=eval_id)
            start = time.time()

            actions = await agent.step(task=task, html="", url=task.url, step_index=0)
            if not actions:
                return None

            solution = TaskSolution(task_id=task.id, actions=actions, web_agent_id=eval_id)
            solution.replace_credentials(eval_id)
            solution.replace_web_agent_id()

            self._timing.record_solution_time(agent.id, task.id, time.time() - start)

            evaluator = ConcurrentEvaluator(
                web_project=project,
                config=EvaluatorConfig(
                    should_record_gif=self.config.record_gif,
                    headless=self.config.headless,
                ),
            )
            results = await evaluator.evaluate_task_solutions(task, [solution])
            if not results:
                return None
            result = results[0]
            result.web_agent_id = agent.id
            if result.stats:
                result.stats.web_agent_id = eval_id
            self._timing.record_evaluation_time(agent.id, task.id, result.evaluation_time)
            return result
        except Exception as e:
            logger.error(f"{agent.name} concurrent eval failed on {task.id}: {e}")
            return None
        finally:
            with contextlib.suppress(Exception):
                await backend.close()

    # ── Stateful mode: step-by-step with live browser ───────────────────

    async def _run_stateful(self, task: Task, agent: IWebAgent, eval_id: str) -> EvaluationResult:
        max_steps = self.config.max_steps_per_task
        evaluator = TaskExecutionSession(
            task=task,
            web_agent_id=eval_id,
            should_record_gif=self.config.record_gif,
            headless=self.config.headless,
        )

        # Start episode trace
        uc_name = getattr(task.use_case, "name", "Unknown") if task.use_case else "Unknown"
        episode_trace = self._trace_writer.start_episode(
            episode_task_id=eval_id,
            task_id=task.id,
            use_case=uc_name,
            task_data=task.serialize() if hasattr(task, "serialize") else {"id": task.id, "prompt": task.prompt, "url": task.url},
        ) if self._trace_writer else None

        start = time.time()
        history: list = []
        step_result = None
        total_actions = 0

        try:
            step_result = await evaluator.reset()
            step_idx = 0

            while total_actions < max_steps and not step_result.score.success:
                before_html = step_result.snapshot.html or ""
                before_url = step_result.snapshot.url or task.url
                before_score = step_result.score.raw_score
                html = sanitize_html(before_html, eval_id)

                try:
                    actions = await agent.step(
                        task=task,
                        html=html,
                        url=before_url,
                        step_index=step_idx,
                        history=self._compact_history(history),
                    )
                except Exception as e:
                    logger.warning(f"{agent.name} step failed: {e}")
                    break

                if not actions:
                    break

                for action in actions[: max_steps - total_actions]:
                    step_result = await evaluator.step(action)
                    total_actions += 1

                    # Record trace step
                    if episode_trace:
                        ar = step_result.action_result
                        episode_trace.record_step(
                            step_index=total_actions - 1,
                            before_url=before_url,
                            before_html=before_html,
                            before_score=before_score,
                            after_url=step_result.snapshot.url or "",
                            after_html=step_result.snapshot.html or "",
                            after_score=step_result.score.raw_score,
                            after_success=step_result.score.success,
                            actions=[{"type": action.type, "raw": action.model_dump()}],
                            exec_ok=bool(getattr(ar, "successfully_executed", True)) if ar else True,
                            error=getattr(ar, "error", None) if ar else None,
                        )
                        # Update before state for next iteration
                        before_html = step_result.snapshot.html or ""
                        before_url = step_result.snapshot.url or task.url
                        before_score = step_result.score.raw_score

                    if step_result.action_result:
                        history.append(step_result.action_result)
                    if step_result.score.success:
                        break

                if step_result.score.success:
                    break
                step_idx += 1

        except Exception as e:
            logger.error(f"{agent.name} stateful eval error: {e}")
        finally:
            with contextlib.suppress(Exception):
                await evaluator.close()

        # Close episode trace
        sr = step_result.score if step_result else None
        if episode_trace:
            episode_trace.close(
                success=sr.success if sr else False,
                score=sr.raw_score if sr else 0.0,
                total_steps=total_actions,
                evaluation_time=time.time() - start,
                agent_name=agent.name,
                web_agent_id=eval_id,
            )

        elapsed = time.time() - start
        sr = step_result.score if step_result else None
        self._timing.record_evaluation_time(agent.id, task.id, elapsed)

        return EvaluationResult(
            final_score=sr.raw_score if sr else 0.0,
            raw_score=sr.raw_score if sr else 0.0,
            web_agent_id=agent.id,
            execution_history=history,
            evaluation_time=elapsed,
            stats=EvaluationStats(
                web_agent_id=agent.id,
                task_id=task.id,
                action_count=total_actions,
                start_time=start,
                total_time=elapsed,
                raw_score=sr.raw_score if sr else 0.0,
                final_score=sr.raw_score if sr else 0.0,
                tests_passed=sr.tests_passed if sr else 0,
                total_tests=sr.total_tests if sr else 0,
            ),
        )

    @staticmethod
    def _compact_history(history: list) -> list[dict[str, Any]]:
        out = []
        for i, event in enumerate(history):
            action_data = None
            with contextlib.suppress(Exception):
                raw = getattr(event, "action", None)
                if raw and hasattr(raw, "model_dump"):
                    action_data = raw.model_dump()
            out.append({
                "index": i,
                "action": action_data,
                "success": bool(getattr(event, "successfully_executed", False)),
                "error": getattr(event, "error", None),
            })
        return out

    # ── Results aggregation ─────────────────────────────────────────────

    def _aggregate_project(self, project: WebProject, run_results: list[dict]) -> None:
        summary, project_report = aggregate_project_results(
            project=project,
            agents=self.config.agents,
            run_results=run_results,
        )
        for agent_name, stats in summary.items():
            logger.info(f"  {agent_name}: {stats['passed']}/{stats['total']} ({stats['success_rate'] * 100:.1f}%)")

        self._results[project.name] = summary
        self._project_reports[project.name] = project_report

    def _save_results(self) -> None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.config.output_dir / f"benchmark_{ts}.json"
        data = self.last_run_report or self._build_run_report()
        save_run_report(data, path)
        self.last_results_path = str(path)
        logger.info(f"Results saved: {path}")

    def _build_run_report(self) -> dict[str, Any]:
        return build_run_report(
            config=self.config,
            timing=self._timing,
            project_reports=self._project_reports,
            summary=self._results,
        )
