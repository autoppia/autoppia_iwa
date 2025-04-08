import asyncio
import time

from loguru import logger
from playwright.async_api import async_playwright

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.demo_webs.utils import initialize_demo_webs_projects
from autoppia_iwa.src.execution.actions.actions import ClickAction, NavigateAction, SelectDropDownOptionAction, TypeAction
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.classes import ActionExecutionResult

actions = [
    NavigateAction(url="http://localhost:8000/", go_back=False, go_forward=False),
    ClickAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/a"}),
    TypeAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div/input"}, text="Inception 4"),
    TypeAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div[3]/div/div/input"}, text="Christopher Nolan"),
    TypeAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div[2]/div/div/input"}, text="2010"),
    TypeAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div[2]/div[2]/div/input"}, text="148"),
    SelectDropDownOptionAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div[4]/select"}, text="Comedy"),
    SelectDropDownOptionAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div[4]/select"}, text="Action"),
    TypeAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div[5]/input"}, text="Leonardo DiCaprio, Joseph Gordon-Levitt"),
    TypeAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div[6]/textarea"}, text="An Amazing Sci-Fi Movie"),
    ClickAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div[10]/button"}),
]


async def evaluate_in_browser(web_agent_id: str, actions: list[BaseAction], is_web_real: bool, backend_demo_webs_service: BackendDemoWebService) -> tuple[list[ActionExecutionResult], list[float]]:
    action_results = []
    action_execution_times = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context(extra_http_headers={"X-WebAgent-Id": web_agent_id})
        page = await context.new_page()

        browser_executor = PlaywrightBrowserExecutor(BrowserSpecification(), page, backend_demo_webs_service)

        try:
            for i, action in enumerate(actions):
                await asyncio.sleep(1.0)
                start_time = time.time()
                try:
                    result = await browser_executor.execute_single_action(action, web_agent_id, iteration=i, is_web_real=is_web_real)
                    action_results.append(result)
                    logger.info(f"✅ Action {i + 1}/{len(actions)} executed successfully.")
                except Exception as e:
                    logger.error(f"❌ Action {i + 1}/{len(actions)} failed: {e}")
                finally:
                    elapsed_time = time.time() - start_time
                    action_execution_times.append(elapsed_time)

        except Exception as e:
            logger.error(f"🚨 Browser evaluation error: {e}")

        finally:
            if context:
                await context.close()
            if browser:
                await browser.close()

        return action_results, action_execution_times


async def init_backend() -> BackendDemoWebService:
    """
    Initializes the backend service for demo web projects.
    """
    web_projects = await initialize_demo_webs_projects(demo_web_projects)
    return BackendDemoWebService(web_projects[0])


async def execute_complete() -> tuple[list[ActionExecutionResult], list[float]]:
    """
    Initializes the backend and executes the complete evaluation in the browser.
    """
    backend_service = await init_backend()
    return await evaluate_in_browser("123", actions, False, backend_service)


if __name__ == "__main__":
    app = AppBootstrap()
    actions_result, execution_time = asyncio.run(execute_complete())
