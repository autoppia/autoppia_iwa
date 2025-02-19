# file: examples/run_task_generation.py

import asyncio
import json
import re
from typing import List, Any

from autoppia_iwa.src.data_generation.domain.classes import (
    TaskGenerationConfig,
    TasksGenerationOutput,
)
from autoppia_iwa.src.backend_demo_web.classes import WebProject
from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.backend_demo_web.config import initialize_test_demo_web_projects


async def main():
    # Bootstrap the application and its DI container.
    app = AppBootstrap()

    # 1) Create a WebProject (we let web analysis fill in domain_analysis & pages).
    my_web_project: List[WebProject] = initialize_test_demo_web_projects()[0]

    # 2) Create a TaskGenerationConfig specifying how many tasks we want.
    my_config = TaskGenerationConfig(
        save_task_in_db=False,
        save_web_analysis_in_db=True,
        enable_crawl=True,
        generate_milestones=False,
        global_tasks_to_generate=3,
        local_tasks_to_generate_per_url=2,
    )

    # 3) Instantiate the pipeline with the project and configuration.
    pipeline = TaskGenerationPipeline(web_project=my_web_project, config=my_config)

    # 4) Run the pipeline to generate tasks.
    output: TasksGenerationOutput = await pipeline.generate()

    # 5) Log and manually inspect the generated tasks and corresponding tests.
    print("----- Generated Tasks and Tests -----")
    all_tasks_data = []
    for idx, task in enumerate(output.tasks, 1):
        tests_list = []
        if task.tests:
            for test in task.tests:
                tests_list.append(test.model_dump())

        task_json = {
            "index": idx,
            "type": task.type,
            "url": task.url,
            "prompt": task.prompt,
            "success_criteria": getattr(task, "success_criteria", None),
            "category": task.category,
            "tests": tests_list
        }
        all_tasks_data.append(task_json)

        print(f"\nTask {idx}:")
        print(f"  Type: {task.type}")
        print(f"  URL: {task.url}")
        print(f"  Prompt: {task.prompt}")
        if tests_list:
            print("  Tests:")
            for t in tests_list:
                print(f"    - {t}")
        else:
            print("  No tests generated.")

    input("\nReview the above tasks and tests. Press Enter to proceed to the final judgment...")

    # 6) Use the OpenAI 03-mini model (o3) to judge the overall output.
    judge_input = "Here is a summary of the generated tasks and tests:\n\n"
    for tdata in all_tasks_data:
        judge_input += f"Task {tdata['index']}:\n"
        judge_input += f"  Type: {tdata['type']}\n"
        judge_input += f"  Prompt: {tdata['prompt']}\n"
        judge_input += f"  URL: {tdata['url']}\n"
        if tdata["tests"]:
            judge_input += "  Tests:\n"
            for test in tdata["tests"]:
                judge_input += f"    - {json.dumps(test)}\n"
        else:
            judge_input += "  No tests generated.\n"
        judge_input += "\n"

    judge_input += (
        "Please evaluate whether these tasks and tests are sensible, actionable, and sufficiently "
        "detailed for further automated evaluation. Provide a brief opinion and any suggestions for improvements."
    )

    llm_service = app.container.llm_service()

    judge_response = await llm_service.async_make_request(
        message_payload=[{"role": "user", "content": judge_input}],
        chat_completion_kwargs={
            "temperature": 0.5,
            "top_k": 40,
            "model": "03-mini",  # Force using the 03-mini model for judgment
        },
    )

    print("\n----- O3 Judge's Opinion -----")
    print(judge_response)
    input("\nReview the judge's opinion. Press Enter to proceed to the final refinement...")

    # 7) Refine tasks/tests using 03-mini:
    refine_prompt = f"""
Below is a JSON array of tasks with their tests. 
Each item has fields: index, type, url, prompt, success_criteria, category, tests.

You are allowed to:
 - Remove tasks entirely if they are not sensible or not actionable,
 - Edit the 'prompt', 'success_criteria', or 'tests' if needed,
 - Remove or edit specific test objects if they do not make sense.

Return ONLY the final JSON array with your modifications (no extra text).
"""
    refine_prompt += "\nTasks:\n"
    refine_prompt += json.dumps(all_tasks_data, indent=2)

    refine_response = await llm_service.make_request(
        message_payload=[{"role": "user", "content": refine_prompt}],
        chat_completion_kwargs={
            "temperature": 0.3,
            "top_k": 40,
            "model": "03-mini",
        },
    )

    def parse_json_response(response: str) -> Any:
        response = response.strip()
        md_pattern = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL)
        match = md_pattern.match(response)
        if match:
            response = match.group(1)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return None

    final_tasks_array = parse_json_response(refine_response)
    if not isinstance(final_tasks_array, list):
        print("\nNo valid refinement was returned. Keeping original tasks.\n")
        final_tasks_array = all_tasks_data

    print("\n----- Final Refined Tasks -----")
    print(json.dumps(final_tasks_array, indent=2))

    input("\nReview the final refined tasks. Press Enter to finish.")


if __name__ == '__main__':
    asyncio.run(main())
