import argparse
import asyncio
import contextlib
import json
from copy import deepcopy

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.entrypoints.benchmark.utils.task_generation import get_projects_by_ids
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator
from autoppia_iwa.src.di_container import DIContainer

from .consistence_reviewer import ConsistenceReviewer
from .llm_reviewer import LLMReviewer

VERIFICATION_DIR = PROJECT_BASE_DIR.parent / "verification_results"


class MockTask:
    def __init__(self, task_id, prompt, use_case):
        self.id = task_id
        self.prompt = prompt
        self.use_case = use_case


async def run_comparison(project_id, llm_service):
    input_file = VERIFICATION_DIR / f"misgenerated_tasks_{project_id}.json"

    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        return

    # Load project metadata
    web_project = None
    projects = get_projects_by_ids(demo_web_projects, [project_id])
    if projects:
        web_project = projects[0]

    with open(input_file) as f:
        data = json.load(f)

    use_cases = data.get("use_cases", {})

    old_reviewer = LLMReviewer(llm_service)
    new_reviewer = ConsistenceReviewer(llm_service)

    results = []

    print(f"\n🚀 Comparing OLv vs NEW Reviewer for project: {project_id}")
    print("=" * 100)
    print(f"{'Use Case':<25} | {'Task ID':<10} | {'OLD Result':<12} | {'NEW Result':<12}")
    print("-" * 100)

    stats = {"old": {"correct": 0, "total": 0}, "new": {"correct": 0, "total": 0}}

    for uc_name, uc_content in use_cases.items():
        tasks = uc_content.get("tasks", [])

        # Find UseCase object
        use_case_obj = None
        if web_project:
            for uc in web_project.use_cases:
                if uc.name == uc_name:
                    use_case_obj = uc
                    break

        for task_data in tasks:
            # Prepare for Old Reviewer (needs Enum operators)
            uc_old = deepcopy(use_case_obj) if use_case_obj else None
            if uc_old:
                enum_constraints = []
                for c in task_data.get("constraints", []):
                    new_c = deepcopy(c)
                    op_str = new_c.get("operator")
                    if isinstance(op_str, str):
                        with contextlib.suppress(ValueError):
                            new_c["operator"] = ComparisonOperator(op_str)
                    enum_constraints.append(new_c)
                uc_old.constraints = enum_constraints

            mock_task_old = MockTask(task_data.get("task_id"), task_data.get("prompt"), uc_old)

            # Prepare for New Reviewer (expects task dict or object)
            # ConsistenceReviewer handles dict tasks

            # Run OLD
            old_res = await old_reviewer.review_task_and_constraints(mock_task_old)
            old_valid = old_res.get("valid", False)

            # Run NEW
            new_res = await new_reviewer.review_task_and_constraints(task_data)
            new_valid = new_res.get("valid", False)

            stats["old"]["total"] += 1
            stats["new"]["total"] += 1
            if old_valid:
                stats["old"]["correct"] += 1
            if new_valid:
                stats["new"]["correct"] += 1

            old_status = "✅ BIEN" if old_valid else "❌ MAL"
            new_status = "✅ BIEN" if new_valid else "❌ MAL"

            print(f"{uc_name[:25]:<25} | {task_data.get('task_id')[:8]:<10} | {old_status:<12} | {new_status:<12}")

            results.append(
                {
                    "task_id": task_data.get("task_id"),
                    "use_case": uc_name,
                    "prompt": task_data.get("prompt"),
                    "constraints_str": task_data.get("constraints_str"),
                    "constraints": task_data.get("constraints"),
                    "old_reviewer": old_res,
                    "new_reviewer": new_res,
                }
            )

    print("-" * 100)
    old_pc = (stats["old"]["correct"] / stats["old"]["total"] * 100) if stats["old"]["total"] > 0 else 0
    new_pc = (stats["new"]["correct"] / stats["new"]["total"] * 100) if stats["new"]["total"] > 0 else 0

    print("RESUMEN FINAL:")
    print(f"OLD Reviewer Success: {stats['old']['correct']}/{stats['old']['total']} ({old_pc:.1f}%)")
    print(f"NEW Reviewer Success: {stats['new']['correct']}/{stats['new']['total']} ({new_pc:.1f}%)")
    print("=" * 100)

    # Save comparison log
    output_file = VERIFICATION_DIR / f"comparison_{project_id}.json"
    with open(output_file, "w") as f:
        json.dump({"summary": stats, "details": results}, f, indent=2)
    print(f"Log detallado en: {output_file}")


async def main():
    parser = argparse.ArgumentParser(description="Compara old vs new reviewer usando tareas fallidas.")
    parser.add_argument("--project-id", type=str, default="autobooks", help="ID del proyecto")
    args = parser.parse_args()

    AppBootstrap()
    llm_service = DIContainer.llm_service()

    await run_comparison(args.project_id, llm_service)


if __name__ == "__main__":
    asyncio.run(main())
