# python
import pytest
from playwright.async_api import async_playwright

from autoppia_iwa.src.execution.actions.actions import (
    ClickAction,
    DoubleClickAction,
    MiddleClickAction,
    MouseDownAction,
    MouseMoveAction,
    MouseUpAction,
    RightClickAction,
    TripleClickAction,
)
from autoppia_iwa.src.execution.actions.base import Selector, SelectorType


@pytest.mark.asyncio
async def test_mouse_actions_end_to_end():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Minimal page with event accounting
        await page.set_content(
            """
            <!doctype html>
            <html>
            <head>
              <meta charset="utf-8"/>
              <style>
                body { margin: 0; padding: 16px; font-family: sans-serif; }
                #area { width: 240px; height: 160px; background: #eef; border: 1px solid #99c; }
                #target { margin-top: 12px; padding: 8px 12px; }
              </style>
            </head>
            <body>
              <div id="area">move area</div>
              <button id="target">target</button>
              <script>
                window.state = {
                  clicks: [],
                  dblclicks: 0,
                  tripleClicks: 0,
                  contextmenu: 0,
                  middle: 0,
                  mousedown: 0,
                  mouseup: 0,
                  mousemoves: 0
                };

                const target = document.getElementById('target');
                const area = document.getElementById('area');

                target.addEventListener('click', (e) => {
                  window.state.clicks.push(e.detail);
                  if (e.detail === 3) { window.state.tripleClicks += 1; }
                });
                target.addEventListener('dblclick', () => { window.state.dblclicks += 1; });
                target.addEventListener('contextmenu', (e) => { e.preventDefault(); window.state.contextmenu += 1; });
                target.addEventListener('auxclick', (e) => { if (e.button === 1) window.state.middle += 1; });
                target.addEventListener('mousedown', () => { window.state.mousedown += 1; });
                target.addEventListener('mouseup', () => { window.state.mouseup += 1; });

                area.addEventListener('mousemove', () => { window.state.mousemoves += 1; });
              </script>
            </body>
            </html>
            """,
        )

        # Build selectors
        sel_target = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="target")
        sel_area = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="area")

        # Execute actions (selector-driven)
        await ClickAction(selector=sel_target).execute(page, backend_service=None, web_agent_id="t")
        await DoubleClickAction(selector=sel_target).execute(page, backend_service=None, web_agent_id="t")
        await TripleClickAction(selector=sel_target).execute(page, backend_service=None, web_agent_id="t")
        await RightClickAction(selector=sel_target).execute(page, backend_service=None, web_agent_id="t")
        await MiddleClickAction(selector=sel_target).execute(page, backend_service=None, web_agent_id="t")
        await MouseDownAction(selector=sel_target).execute(page, backend_service=None, web_agent_id="t")
        await MouseUpAction(selector=sel_target).execute(page, backend_service=None, web_agent_id="t")
        await MouseMoveAction(selector=sel_area, steps=5).execute(page, backend_service=None, web_agent_id="t")

        # Also exercise coordinate paths for coverage (move to area center)
        area_box = await page.locator("#area").bounding_box()
        assert area_box is not None
        cx = int(area_box["x"] + area_box["width"] / 2)
        cy = int(area_box["y"] + area_box["height"] / 2)
        await MouseMoveAction(x=cx, y=cy, steps=3).execute(page, backend_service=None, web_agent_id="t")

        # Validate effects
        state = await page.evaluate("window.state")

        # Clicks detail should contain 1 (single), 2 (double), and 3 (triple)
        assert 1 in state["clicks"]
        assert any(d >= 2 for d in state["clicks"])
        assert 3 in state["clicks"]
        assert state["dblclicks"] >= 1
        assert state["tripleClicks"] >= 1

        # Right and middle clicks observed
        assert state["contextmenu"] >= 1
        assert state["middle"] >= 1

        # Mouse down/up and move observed
        assert state["mousedown"] >= 1
        assert state["mouseup"] >= 1
        assert state["mousemoves"] > 0

        await context.close()
        await browser.close()
