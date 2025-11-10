# python
import asyncio
from playwright.async_api import async_playwright

from autoppia_iwa.src.execution.actions.actions import HoldKeyAction, LeftClickDragAction
from autoppia_iwa.src.execution.actions.base import Selector, SelectorType


def test_hold_key_action_end_to_end():
    async def run():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.set_content(
                """
                <!doctype html>
                <html>
                <body>
                  <input id="field" />
                  <script>
                    window.state = { keydowns: 0, keyups: 0, lastKeyDown: "", lastKeyUp: "" };
                    document.addEventListener('keydown', (e) => { window.state.keydowns += 1; window.state.lastKeyDown = e.key; });
                    document.addEventListener('keyup', (e) => { window.state.keyups += 1; window.state.lastKeyUp = e.key; });
                  </script>
                </body>
                </html>
                """
            )

            await page.focus("#field")

            await HoldKeyAction(key="Shift", duration_ms=50).execute(page, backend_service=None, web_agent_id="t")
            await page.wait_for_timeout(20)
            state = await page.evaluate("window.state")
            assert state["keydowns"] >= 1
            assert state["keyups"] >= 1
            assert state["lastKeyDown"] in ("Shift", "ShiftLeft", "ShiftRight")

            await HoldKeyAction(key="Alt").execute(page, backend_service=None, web_agent_id="t")
            await page.wait_for_timeout(20)
            mid_state = await page.evaluate("window.state")
            assert mid_state["keydowns"] >= state["keydowns"] + 1
            assert mid_state["keyups"] == state["keyups"]

            await HoldKeyAction(key="Alt", release=True).execute(page, backend_service=None, web_agent_id="t")
            await page.wait_for_timeout(20)
            end_state = await page.evaluate("window.state")
            assert end_state["keyups"] >= mid_state["keyups"] + 1
            assert end_state["lastKeyUp"] in ("Alt", "AltLeft", "AltRight")

            await context.close()
            await browser.close()

    asyncio.run(run())


def test_left_click_drag_action_end_to_end():
    async def run():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.set_content(
                """
                <!doctype html>
                <html>
                <head>
                  <style>
                    #source { width: 100px; height: 100px; background: #cfc; display:inline-block; }
                    #spacer { display:inline-block; width: 220px; height: 1px; }
                    #target { width: 120px; height: 120px; background: #ccf; display:inline-block; }
                  </style>
                </head>
                <body>
                  <div id="source">source</div>
                  <div id="spacer"></div>
                  <div id="target">target</div>
                  <script>
                    window.state = { downOnSource: 0, upOnTarget: 0, moves: 0 };
                    let dragging = false;
                    const src = document.getElementById('source');
                    const tgt = document.getElementById('target');
                    src.addEventListener('mousedown', () => { dragging = true; window.state.downOnSource += 1; });
                    document.addEventListener('mousemove', () => { if (dragging) window.state.moves += 1; });
                    tgt.addEventListener('mouseup', () => { if (dragging) { window.state.upOnTarget += 1; dragging = false; }});
                  </script>
                </body>
                </html>
                """
            )

            sel_source = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="source")
            sel_target = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="target")

            await LeftClickDragAction(selector=sel_source, targetSelector=sel_target, steps=10).execute(page, backend_service=None, web_agent_id="t")
            await page.wait_for_timeout(50)
            state = await page.evaluate("window.state")
            assert state["downOnSource"] >= 1
            assert state["upOnTarget"] >= 1
            assert state["moves"] > 0

            src_box = await page.locator("#source").bounding_box()
            tgt_box = await page.locator("#target").bounding_box()
            assert src_box and tgt_box
            sx, sy = int(src_box["x"] + src_box["width"] / 2), int(src_box["y"] + src_box["height"] / 2)
            tx, ty = int(tgt_box["x"] + tgt_box["width"] / 2), int(tgt_box["y"] + tgt_box["height"] / 2)

            await LeftClickDragAction(x=sx, y=sy, targetX=tx, targetY=ty, steps=4).execute(page, backend_service=None, web_agent_id="t")
            await page.wait_for_timeout(50)
            state2 = await page.evaluate("window.state")
            assert state2["moves"] >= state["moves"] + 1

            await context.close()
            await browser.close()

    asyncio.run(run())
