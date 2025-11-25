from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents.random.agent import RandomClickerWebAgent

from ..benchmark.instrumented import InstrumentedBenchmark
from ..evaluators.instrumented import InstrumentationConfig
from ..web_agents.faulty_agent import FaultyWebAgent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect JS+DOM traces by running a small benchmark batch.")
    parser.add_argument("--projects", nargs="*", default=["autobooks"], help="Demo web project IDs to sample")
    parser.add_argument("--runs", type=int, default=1, help="Evaluation runs per task")
    parser.add_argument("--prompts-per-use-case", type=int, default=1, dest="prompts_per_use_case")
    parser.add_argument("--num-use-cases", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=Path("data/inputs/reward_model/raw_traces"))
    parser.add_argument("--capture-screenshots", action="store_true", help="Store screenshots inside traces")
    parser.add_argument("--use-cached-tasks", action="store_true", help="Reuse cached tasks if available")
    parser.add_argument("--disable-logging", action="store_true", help="Run without persisting traces (useful for dry-runs)")
    parser.add_argument("--agent-mode", choices=["random", "faulty"], default="random", help="Select which simple agent to use for trace collection.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    projects = get_projects_by_ids(demo_web_projects, args.projects)
    if not projects:
        raise SystemExit("No valid projects supplied.")

    agents = [FaultyWebAgent(id="faulty-tracer", name="faulty-tracer")] if args.agent_mode == "faulty" else [RandomClickerWebAgent(id="js-tracer", name="js-tracer", is_random=True)]

    cfg = BenchmarkConfig(
        projects=projects,
        agents=agents,
        prompts_per_use_case=args.prompts_per_use_case,
        num_use_cases=args.num_use_cases,
        runs=args.runs,
        max_parallel_agent_calls=1,
        use_cached_tasks=args.use_cached_tasks,
        record_gif=False,
        enable_dynamic_html=False,
        save_results_json=False,
        plot_results=False,
    )

    instrumentation = InstrumentationConfig(
        enabled=not args.disable_logging,
        output_dir=args.output_dir,
        capture_screenshots=args.capture_screenshots,
    )

    benchmark = InstrumentedBenchmark(cfg, instrumentation)
    asyncio.run(benchmark.run())


if __name__ == "__main__":
    main()
