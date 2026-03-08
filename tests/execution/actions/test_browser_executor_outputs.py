import asyncio
import base64
import textwrap

from playwright.async_api import async_playwright

from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification
from autoppia_iwa.src.execution.actions.actions import EvaluateAction, ExtractAction, NavigateAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor


def _data_url(html: str) -> str:
    encoded = base64.b64encode(html.encode("utf-8")).decode("ascii")
    return f"data:text/html;base64,{encoded}"


def test_executor_persists_action_outputs() -> None:
    html = textwrap.dedent(
        """
        <!doctype html>
        <html>
        <body>
          <h1>Pricing</h1>
          <div id="summary">Total Treasury: 2.8K</div>
          <script>
            window.exampleValue = 42;
          </script>
        </body>
        </html>
        """
    )

    async def run() -> None:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            specs = BrowserSpecification()
            executor = PlaywrightBrowserExecutor(specs, page, backend_demo_webs_service=None)

            nav = NavigateAction(url=_data_url(html))
            nav_res = await executor.execute_single_action(nav, web_agent_id="t", iteration=0, is_web_real=True)
            assert nav_res.successfully_executed is True
            assert nav_res.action_output is None

            eval_res = await executor.execute_single_action(
                EvaluateAction(script="() => window.exampleValue"),
                web_agent_id="t",
                iteration=1,
                is_web_real=True,
            )
            assert eval_res.successfully_executed is True
            assert eval_res.action_output == 42

            extract_res = await executor.execute_single_action(
                ExtractAction(query="Treasury", max_chars=200),
                web_agent_id="t",
                iteration=2,
                is_web_real=True,
            )
            assert extract_res.successfully_executed is True
            assert "Total Treasury: 2.8K" in str(extract_res.action_output or "")

            await context.close()
            await browser.close()

    asyncio.run(run())
