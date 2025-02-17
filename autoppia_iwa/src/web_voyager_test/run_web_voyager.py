import asyncio
import json
import logging
import random
import shutil
from pathlib import Path
from typing import List, Tuple

from pydantic import BaseModel

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.application.task_tests_generator import TaskTestGenerator
from autoppia_iwa.src.data_generation.domain.classes import Task, WebProject
from autoppia_iwa.src.web_analysis.application.web_analysis_pipeline import WebAnalysisPipeline
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis
from modules.webs_demo.web_1_demo_django_jobs.events.events import EVENTS_ALLOWED

logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO, handlers=[logging.StreamHandler()])


class TaskData(BaseModel):
    """Data model for tasks."""

    id: str
    web: str
    ques: str
    web_name: str


def cleanup_webdriver_cache() -> None:
    """Clean up webdriver cache directories."""
    cache_paths = [Path.home() / '.wdm', Path.home() / '.cache' / 'selenium', Path.home() / 'Library' / 'Caches' / 'selenium']
    for path in cache_paths:
        if path.exists():
            logging.info(f'Removing cache directory: {path}')
            shutil.rmtree(path, ignore_errors=True)


def _generate_tests_for_web_project(url: str, task_description: str, enable_crawl: bool, is_real_web: bool = False) -> Tuple[List, DomainAnalysis]:
    """Generate task-based tests for a web project."""
    try:
        web_analysis_pipeline = WebAnalysisPipeline(start_url=url)
        web_analysis = web_analysis_pipeline.analyze(enable_crawl=enable_crawl, save_results_in_db=True)
        web_project = WebProject(backend_url=url, frontend_url=url, name='example' if is_real_web else 'Local Web App', events_to_check=EVENTS_ALLOWED, is_real_web=is_real_web)
        task_test_generator = TaskTestGenerator(web_project=web_project, web_analysis=web_analysis)
        tests = task_test_generator.generate_task_tests(task_description, url)
        return tests, web_analysis
    except Exception as e:
        logging.error(f"Failed to generate tests for URL '{url}': {e}")
        raise


async def main() -> None:
    """Main function to load tasks, generate tests, and save results."""
    ENABLE_CRAWL = False
    IS_WEB_REAL = True
    try:
        from autoppia_iwa.config.config import PROJECT_BASE_DIR

        data_dir = Path(PROJECT_BASE_DIR.parent / 'data')
        cleanup_webdriver_cache()
        tasks = []
        with open(data_dir / 'WebVoyager_data.jsonl', 'r') as f:
            for line in f:
                tasks.append(json.loads(line))
        with open(data_dir / 'WebVoyagerImpossibleTasks.json', 'r') as f:
            impossible_tasks = set(json.load(f))
        tasks = [TaskData(**task) for task in tasks if task['id'] not in impossible_tasks]
        random.seed(42)
        random.shuffle(tasks)
        tests_generated_tasks: List[Task] = []
        for task in tasks[:2]:
            logging.info(f'Generating tests for task ID: {task.id}, URL: {task.web}')
            task_tests, task_web_analysis = _generate_tests_for_web_project(task.web, task.ques, ENABLE_CRAWL, IS_WEB_REAL)
            tests_generated_tasks.append(Task(url=task.web, prompt=task.ques, tests=task_tests, web_analysis=task_web_analysis, milestones=[]))
        output_file = data_dir / 'GeneratedTests.json'
        with open(output_file, 'w') as f:
            json.dump([task.nested_model_dump() for task in tests_generated_tasks], f, indent=4)
        logging.info(f'Generated tests saved to: {output_file}')
    except Exception as e:
        logging.error(f'Main loop error: {e}', exc_info=True)
    finally:
        logging.info('Shutting down...')


if __name__ == '__main__':
    app_bootstrap = AppBootstrap()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\nReceived keyboard interrupt, shutting down...')
    except Exception as e:
        logging.error(f'Fatal error: {e}', exc_info=True)
