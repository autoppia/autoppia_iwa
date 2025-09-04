import pytest
from playwright.async_api import async_playwright

from autoppia_iwa.src.execution.actions.actions import ScrollAction


async def get_scroll_metrics(page):
    return await page.evaluate(
        """() => {
          const el = document.scrollingElement || document.documentElement;
          const innerW = window.innerWidth;
          const innerH = window.innerHeight;
          const maxX = Math.max(0, el.scrollWidth - el.clientWidth);
          const maxY = Math.max(0, el.scrollHeight - el.clientHeight);
          return {
            x: Math.round(el.scrollLeft),
            y: Math.round(el.scrollTop),
            innerW, innerH,
            maxX: Math.round(maxX),
            maxY: Math.round(maxY),
          };
        }"""
    )


@pytest.mark.asyncio
async def test_scroll_action_vertical_horizontal_and_text():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Large scrollable page with a text target far bottom-right
        await page.set_content(
            """
            <!doctype html>
            <html>
            <head>
              <meta charset="utf-8"/>
              <style>
                html, body { margin: 0; padding: 0; }
                #canvas {
                  position: relative;
                  width: 5000px;
                  height: 4000px;
                  background: linear-gradient(90deg, #f5f5f5, #eee);
                }
                #target {
                  position: absolute;
                  top: 3500px;
                  left: 4200px;
                  width: 300px;
                  height: 120px;
                  background: #cfe8ff;
                  border: 1px solid #99c;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  font-family: sans-serif;
                }
              </style>
            </head>
            <body>
              <div id="canvas">
                <div id="target">SCROLL_TARGET_12345</div>
              </div>
            </body>
            </html>
            """,
        )

        m0 = await get_scroll_metrics(page)
        assert m0["x"] == 0 and m0["y"] == 0

        # Down by default step (viewport height)
        await ScrollAction(down=True).execute(page, backend_service=None, web_agent_id="t")
        m1 = await get_scroll_metrics(page)
        assert m1["y"] > m0["y"] and m1["y"] >= max(1, int(m1["innerH"] * 0.8))

        # Up by 200px
        await ScrollAction(value=200, up=True).execute(page, backend_service=None, web_agent_id="t")
        m2 = await get_scroll_metrics(page)
        dy = m1["y"] - m2["y"]
        assert 150 <= dy <= 250  # tolerance around 200

        # Right by default step (viewport width)
        await ScrollAction(right=True).execute(page, backend_service=None, web_agent_id="t")
        m3 = await get_scroll_metrics(page)
        assert m3["x"] > m2["x"] and m3["x"] >= max(1, int(m3["innerW"] * 0.8))

        # Left by 150px
        await ScrollAction(value=150, left=True).execute(page, backend_service=None, web_agent_id="t")
        m4 = await get_scroll_metrics(page)
        dx = m3["x"] - m4["x"]
        assert 120 <= dx <= 180  # tolerance around 150

        # Scroll to bottom/right edges
        await ScrollAction(value="bottom").execute(page, backend_service=None, web_agent_id="t")
        mbot = await get_scroll_metrics(page)
        assert abs(mbot["y"] - mbot["maxY"]) <= 5

        await ScrollAction(value="right").execute(page, backend_service=None, web_agent_id="t")
        mright = await get_scroll_metrics(page)
        assert abs(mright["x"] - mright["maxX"]) <= 5

        # Back to top/left edges
        await ScrollAction(value="top").execute(page, backend_service=None, web_agent_id="t")
        mtop = await get_scroll_metrics(page)
        assert mtop["y"] <= 5

        await ScrollAction(value="left").execute(page, backend_service=None, web_agent_id="t")
        mleft = await get_scroll_metrics(page)
        assert mleft["x"] <= 5

        # Scroll to specific text
        await ScrollAction(value="SCROLL_TARGET_12345").execute(page, backend_service=None, web_agent_id="t")
        mtxt = await get_scroll_metrics(page)
        assert mtxt["x"] > 0 or mtxt["y"] > 0

        rect = await page.evaluate(
            """() => {
              const el = document.getElementById('target');
              const r = el.getBoundingClientRect();
              return { top: r.top, left: r.left, bottom: r.bottom, right: r.right, iw: window.innerWidth, ih: window.innerHeight };
            }"""
        )
        # Target is at least partially visible within viewport
        assert rect["top"] < rect["ih"] and rect["left"] < rect["iw"]
        assert rect["bottom"] > 0 and rect["right"] > 0

        await context.close()
        await browser.close()
