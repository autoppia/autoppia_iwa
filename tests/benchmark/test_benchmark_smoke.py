import asyncio
import os

os.environ.setdefault("AUTOPPIA_BOOTSTRAP_DISABLE", "1")


from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent


def test_benchmark_runs_with_stub_agent(monkeypatch, stub_agent):
    async def fake_generate_tasks(*args, **kwargs):
        return [
            Task(
                url="https://example.com",
                prompt="Do nothing",
                web_project_id="test-project",
                tests=[],
            )
        ]

    monkeypatch.setattr("autoppia_iwa.entrypoints.benchmark.benchmark.generate_tasks_for_project", fake_generate_tasks)

    project = WebProject(
        id="test-project",
        name="Test Project",
        backend_url="https://example.com/api/",
        frontend_url="https://example.com/",
        use_cases=[],
    )

    agent = ApifiedWebAgent(base_url=stub_agent.base_url, id="stub-agent", name="StubAgent")

    config = BenchmarkConfig(
        projects=[project],
        agents=[agent],
        runs=1,
        max_parallel_agent_calls=1,
        prompts_per_use_case=1,
        num_use_cases=1,
        use_cached_tasks=True,
        save_results_json=False,
        plot_results=False,
        enable_dynamic_html=False,
    )

    async def run():
        benchmark = Benchmark(config)
        results = await benchmark.run()
        assert isinstance(results, dict)

    asyncio.run(run())
