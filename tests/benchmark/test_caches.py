from __future__ import annotations

import asyncio

from autoppia_iwa.entrypoints.benchmark.utils.solutions import ConsolidatedSolutionCache
from autoppia_iwa.entrypoints.benchmark.utils.tasks import load_tasks_from_json, save_tasks_to_json
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.web_agents.classes import TaskSolution


def _make_project(project_id: str = "proj-1") -> WebProject:
    return WebProject(id=project_id, name=f"Project {project_id}", backend_url="https://api.example/", frontend_url="https://example.com/", use_cases=[])


def test_task_cache_merges_and_deduplicates(tmp_path):
    project = _make_project()
    cache_dir = tmp_path.as_posix()

    task_a = Task(id="task-a", url="https://example.com/a", prompt="A")
    task_b = Task(id="task-b", url="https://example.com/b", prompt="B")

    async def run():
        await save_tasks_to_json([task_a], project, cache_dir)
        await save_tasks_to_json([task_b, Task(id="task-a", url="https://example.com/a?updated", prompt="A updated")], project, cache_dir)
        return await load_tasks_from_json(project, cache_dir)

    tasks = asyncio.run(run())
    assert tasks is not None
    assert {t.id for t in tasks} == {"task-a", "task-b"}


def test_task_cache_rejects_mismatched_project(tmp_path):
    project = _make_project("proj-main")
    other = _make_project("proj-other")
    cache_dir = tmp_path.as_posix()

    async def run():
        await save_tasks_to_json([Task(id="task-a", url="https://example.com/a", prompt="A")], project, cache_dir)
        return await load_tasks_from_json(other, cache_dir)

    loaded = asyncio.run(run())
    assert loaded is None


def test_solutions_cache_persists_across_instances(tmp_path):
    cache = ConsolidatedSolutionCache(tmp_path.as_posix())
    solution = TaskSolution(task_id="task-1", actions=[], web_agent_id="agent-1")
    assert cache.save_solution(solution, agent_id="agent-1", agent_name="Agent One")
    assert cache.solution_exists("task-1", "agent-1")

    cache_reopened = ConsolidatedSolutionCache(tmp_path.as_posix())
    assert cache_reopened.solution_exists("task-1", "agent-1")
