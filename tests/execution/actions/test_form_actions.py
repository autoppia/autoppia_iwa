import asyncio
import base64
import textwrap

import pytest
from playwright.async_api import async_playwright

from autoppia_iwa.src.execution.actions.actions import (
    AssertAction,
    DragAndDropAction,
    GetDropDownOptionsAction,
    HoverAction,
    NavigateAction,
    ScreenshotAction,
    SelectAction,
    SelectDropDownOptionAction,
    SendKeysIWAAction,
    SubmitAction,
    TypeAction,
    WaitAction,
)
from autoppia_iwa.src.execution.actions.base import Selector, SelectorType


def _data_url(html: str) -> str:
    encoded = base64.b64encode(html.encode("utf-8")).decode("ascii")
    return f"data:text/html;base64,{encoded}"


def test_form_and_misc_actions(tmp_path):
    html = textwrap.dedent(
        """
        <!doctype html>
        <html>
        <body style="height:2400px;">
          <div id="status"></div>
          <form id="test-form">
            <input id="text-input" name="text" />
            <button id="submit-btn">Submit</button>
          </form>
          <select id="pet-select">
            <option value="">Choose</option>
            <option value="dog">Dog</option>
            <option value="cat">Cat</option>
          </select>
          <div id="hover-me">hover me</div>
          <div id="drag-source" draggable="true">Drag</div>
          <div id="drag-target" style="width:120px;height:120px;border:1px solid #333;">Drop</div>
          <div id="delayed-root"></div>
          <div id="assert-area">Hello Assert Action</div>
          <script>
            window.state = {
              text: "",
              select: "",
              hovered: 0,
              submitted: 0,
              dropped: 0,
              keyPresses: []
            };
            document.getElementById('text-input').addEventListener('input', (e) => window.state.text = e.target.value);
            document.getElementById('test-form').addEventListener('submit', (e) => {
              e.preventDefault();
              window.state.submitted += 1;
              document.getElementById('status').textContent = 'Submitted!';
            });
            document.getElementById('pet-select').addEventListener('change', (e) => window.state.select = e.target.value);
            document.getElementById('hover-me').addEventListener('mouseenter', () => window.state.hovered += 1);
            const target = document.getElementById('drag-target');
            target.addEventListener('dragover', (e) => e.preventDefault());
            target.addEventListener('drop', (e) => { e.preventDefault(); window.state.dropped += 1; target.textContent = 'Dropped!'; });
            document.addEventListener('keydown', (e) => window.state.keyPresses.push(e.key));
            document.addEventListener('keyup', (e) => window.state.keyPresses.push('up:' + e.key));
            setTimeout(() => {
              const el = document.createElement('div');
              el.id = 'ready';
              el.textContent = 'ready';
              document.getElementById('delayed-root').appendChild(el);
            }, 100);
          </script>
        </body>
        </html>
        """
    )

    data_url = _data_url(html)

    async def run():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await NavigateAction(url=data_url).execute(page, backend_service=None, web_agent_id="t")
            assert page.url.startswith("data:text/html")

            input_selector = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="text-input")
            await TypeAction(selector=input_selector, text="dynamic text").execute(page, backend_service=None, web_agent_id="t")

            select_selector = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="pet-select")
            await SelectAction(selector=select_selector, value="dog").execute(page, backend_service=None, web_agent_id="t")

            await HoverAction(selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="hover-me")).execute(page, backend_service=None, web_agent_id="t")

            await WaitAction(selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="ready")).execute(page, backend_service=None, web_agent_id="t")
            await WaitAction(time_seconds=0.05).execute(page, backend_service=None, web_agent_id="t")

            await page.focus("#text-input")
            await SendKeysIWAAction(keys="ArrowRight").execute(page, backend_service=None, web_agent_id="t")

            await SubmitAction(selector=input_selector).execute(page, backend_service=None, web_agent_id="t")

            await AssertAction(text_to_assert="Hello Assert Action").execute(page, backend_service=None, web_agent_id="t")
            with pytest.raises(AssertionError):
                await AssertAction(text_to_assert="does-not-exist").execute(page, backend_service=None, web_agent_id="t")

            await DragAndDropAction(sourceSelector="#drag-source", targetSelector="#drag-target").execute(page, backend_service=None, web_agent_id="t")

            await GetDropDownOptionsAction(selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//select[@id='pet-select']")).execute(page, backend_service=None, web_agent_id="t")

            selected = await SelectDropDownOptionAction(
                selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//select[@id='pet-select']"),
                text="Cat",
            ).execute(page, backend_service=None, web_agent_id="t")
            assert selected is True

            screenshot_path = tmp_path / "snap.png"
            await ScreenshotAction(file_path=str(screenshot_path), full_page=False).execute(page, backend_service=None, web_agent_id="t")
            assert screenshot_path.exists()

            state = await page.evaluate("window.state")
            assert state["text"] == "dynamic text"
            assert state["select"] == "cat"
            assert state["hovered"] >= 1
            assert state["submitted"] >= 1
            assert state["dropped"] >= 1
            assert any(key.startswith("up:") for key in state["keyPresses"])

            await context.close()
            await browser.close()

    asyncio.run(run())
