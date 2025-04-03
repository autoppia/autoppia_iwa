import asyncio
import time
import traceback

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
    NavigateAction(url="http://localhost:8001/", go_back=False, go_forward=False),
    ClickAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/a"}),
    TypeAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div/input"}, text="Inception 4"),
    TypeAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div[3]/div/div/input"}, text="Christopher Nolan"),
    TypeAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div[2]/div/div/input"}, text="2010"),
    TypeAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div[2]/div[2]/div/input"}, text="148"),
    SelectDropDownOptionAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div[4]/select"}, text="Science Fiction"),
    SelectDropDownOptionAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div[4]/select"}, text="Action"),
    TypeAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div[5]/input"}, text="Leonardo DiCaprio, Joseph Gordon-Levitt"),
    TypeAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div[6]/textarea"}, text="An Amazing Sci-Fi Movie"),
    ClickAction(selector={"type": "xpathSelector", "value": "html/body/main/div/div/div/div/div[2]/form/div[10]/button"}),
]


async def evaluate_in_browser(web_agent_id: str, actions: list[BaseAction], is_web_real: bool, backend_demo_webs_service) -> tuple[list[ActionExecutionResult], list[float]]:
    """
    Executes all actions in a Playwright browser context and returns the results + times.
    """
    action_execution_times: list[float] = []
    action_results: list[ActionExecutionResult] = []

    async with async_playwright() as playwright:
        browser, context = None, None
        try:
            browser = await playwright.chromium.launch(headless=False)
            context = await browser.new_context(extra_http_headers={"X-WebAgent-Id": web_agent_id})
            context.set_default_timeout(30000)
            page = await context.new_page()

            browser_executor = PlaywrightBrowserExecutor(BrowserSpecification(), page, backend_demo_webs_service)
            for i, action in enumerate(actions):
                start_time_action = time.time()
                try:
                    result = await browser_executor.execute_single_action(action, web_agent_id, iteration=i, is_web_real=is_web_real)
                    action_results.append(result)
                    elapsed = time.time() - start_time_action
                    action_execution_times.append(elapsed)

                except Exception as e:
                    logger.error(f"Action {i + 1}/{len(actions)} failed: {e}")
                    logger.info(traceback.format_exc())
                    elapsed = time.time() - start_time_action
                    action_execution_times.append(elapsed)

                    break

            return action_results, action_execution_times

        except Exception as e:
            logger.error(f"Browser evaluation error: {e}")
            return [], []
        finally:
            if context:
                await context.close()
            if browser:
                await browser.close()


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
