from __future__ import annotations

import json
from pathlib import Path

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.evaluation.benchmark.config import BenchmarkConfig
from autoppia_iwa.src.evaluation.benchmark.reporting import (
    aggregate_project_results,
    build_legacy_performance_report,
    build_legacy_results_payload,
    build_run_report,
    build_task_result,
    build_terminal_report,
    has_zero_score,
    save_run_report,
)
from autoppia_iwa.src.evaluation.benchmark.utils.metrics import TimingMetrics
from autoppia_iwa.src.evaluation.classes import EvaluationResult, EvaluationStats
from autoppia_iwa.src.web_agents.classes import IWebAgent


class _FakeAgent(IWebAgent):
    def __init__(self, agent_id: str, name: str):
        self.id = agent_id
        self.name = name

    async def step(self, *, task, html, screenshot=None, url, step_index, history=None):
        return []


def _project() -> WebProject:
    return WebProject(
        id="autocinema",
        name="Autocinema",
        backend_url="http://localhost:8090",
        frontend_url="http://localhost:8000",
    )


def _config(tmp_path: Path) -> BenchmarkConfig:
    return BenchmarkConfig(
        projects=[_project()],
        agents=[_FakeAgent("a1", "Agent One")],
        base_dir=tmp_path,
        save_results_json=False,
        print_summary=False,
    )


def test_build_task_result_uses_stats_and_defaults(tmp_path):
    agent = _FakeAgent("a1", "Agent One")
    task = Task(id="task-1", prompt="Do it", url="http://localhost", web_project_id="autocinema")
    result = EvaluationResult(
        final_score=1.0,
        evaluation_time=2.5,
        stats=EvaluationStats(
            web_agent_id="eval-1",
            task_id="task-1",
            action_count=3,
            tests_passed=1,
            total_tests=1,
            error_message="",
            start_time=0.0,
        ),
    )

    payload = build_task_result(agent=agent, task=task, evaluation_result=result, eval_id="eval-1", run_idx=2)

    assert payload["run"] == 2
    assert payload["agent_name"] == "Agent One"
    assert payload["success"] is True
    assert payload["tests_passed"] == 1
    assert payload["total_tests"] == 1


def test_aggregate_project_results_and_zero_score_detection():
    agent_one = _FakeAgent("a1", "Agent One")
    agent_two = _FakeAgent("a2", "Agent Two")
    summary, report = aggregate_project_results(
        project=_project(),
        agents=[agent_one, agent_two],
        run_results=[
            {
                "a1": {"task-1": {"score": 1.0, "prompt": "x"}},
                "a2": {"task-1": {"score": 0.0, "prompt": "x"}},
            }
        ],
    )

    assert summary["Agent One"]["passed"] == 1
    assert summary["Agent Two"]["passed"] == 0
    assert report["tasks_by_agent"]["Agent One"][0]["score"] == 1.0
    assert has_zero_score({"a2": {"task-1": {"score": 0.0}}}) is True
    assert has_zero_score({"a1": {"task-1": {"score": 1.0}}}) is False


def test_build_run_report_terminal_report_and_save(tmp_path):
    config = _config(tmp_path)
    timing = TimingMetrics()
    timing.start()
    timing.end()
    run_report = build_run_report(
        config=config,
        timing=timing,
        project_reports={"Autocinema": {"summary": {"Agent One": {"passed": 1, "total": 1, "success_rate": 1.0, "avg_score": 1.0}}}},
        summary={"Autocinema": {"Agent One": {"passed": 1, "total": 1, "success_rate": 1.0, "avg_score": 1.0}}},
    )

    terminal = build_terminal_report(run_report, config=config, results_path="/tmp/results.json")
    assert "BENCHMARK SUMMARY" in terminal
    assert "JSON: /tmp/results.json" in terminal
    assert "Log:" in terminal

    output = tmp_path / "report.json"
    saved = save_run_report(run_report, output)
    assert saved == output
    assert json.loads(output.read_text())["summary"]["Autocinema"]["Agent One"]["passed"] == 1


def test_build_legacy_results_payload_and_report(tmp_path):
    agent = _FakeAgent("a1", "Agent One")
    timing = TimingMetrics()
    timing.record_solution_time("a1", "task-1", 1.25)
    timing.record_evaluation_time("a1", "task-1", 0.75)
    timing.start()
    timing.end()

    results = {"a1": {"task-1": {"score": 1.0, "use_case": "LOGIN", "prompt": "Login"}}}
    payload = build_legacy_results_payload(results, [agent], timing)
    report = build_legacy_performance_report(results, [agent], timing)

    assert payload["agents"]["Agent One"]["tasks"]["task-1"]["solution_time"] == 1.25
    assert payload["agents"]["Agent One"]["tasks"]["task-1"]["evaluation_time"] == 0.75
    assert "PERFORMANCE REPORT" in report
    assert "Agent One" in report
