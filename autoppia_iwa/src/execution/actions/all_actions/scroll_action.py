import json
from typing import Any, ClassVar, Literal

from playwright.async_api import Error as PlaywrightError, TimeoutError as PWTimeout
from pydantic import Field, model_validator

from ..base import BaseAction
from .helpers import _ensure_page, action_logger, log_action


class ScrollAction(BaseAction):
    """Scrolls the page up, down, left, right, to a text, or by a specific amount."""

    type: Literal["ScrollAction"] = "ScrollAction"
    browser_use_tool_name: ClassVar[str] = "scroll"
    value: str | int | None = Field(
        None,
        description=(
            "Scroll amount or target. "
            "If int: scroll by that many px in the chosen direction. "
            "If None: scroll by viewport size in the chosen direction. "
            "If str: one of {'top','bottom','left','right','max','start','end'} or text to scroll into view."
        ),
    )
    up: bool = Field(False, description="Scroll vertically up.")
    down: bool = Field(False, description="Scroll vertically down.")
    left: bool = Field(False, description="Scroll horizontally left.")
    right: bool = Field(False, description="Scroll horizontally right.")

    @model_validator(mode="before")
    @classmethod
    def _validate_directions(cls, values):
        up = bool(values.get("up", False))
        down = bool(values.get("down", False))
        left = bool(values.get("left", False))
        right = bool(values.get("right", False))
        value = values.get("value", None)
        dir_count = sum([up, down, left, right])
        if isinstance(value, int | type(None)) and dir_count != 1:
            raise ValueError("ScrollAction requires exactly one of up/down/left/right when 'value' is int or None.")
        return values

    async def _scroll_by_value(self, page, dx: int, dy: int) -> None:
        await page.evaluate(
            """({dx, dy}) => { window.scrollBy(dx, dy); }""",
            {"dx": dx, "dy": dy},
        )

    @staticmethod
    async def _scroll_to_text(page, text: str) -> None:
        locator = page.get_by_text(text, exact=False).first
        count = await locator.count()
        if count == 0:
            locator = page.locator(f"xpath=//*[contains(normalize-space(string(.)), {json.dumps(text)})]").first
            count = await locator.count()
            if count == 0:
                raise ValueError(f"Could not find text on page: {text}")
        await locator.scroll_into_view_if_needed()

    async def _scroll_to_edge(self, page, axis: str, end: str) -> None:
        script = """
            ({axis, end}) => {
              const el = document.scrollingElement || document.documentElement;
              if (axis === 'y') {
                if (end === 'start') {
                  el.scrollTop = 0;
                } else {
                  el.scrollTop = Math.max(0, el.scrollHeight - el.clientHeight);
                }
              } else {
                if (end === 'start') {
                  el.scrollLeft = 0;
                } else {
                  el.scrollLeft = Math.max(0, el.scrollWidth - el.clientWidth);
                }
              }
            }
        """
        await page.evaluate(script, {"axis": axis, "end": end})

    @log_action("ScrollAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "ScrollAction")

        if isinstance(self.value, str):
            v = self.value.strip().lower()
            if v in {"top", "start"}:
                await self._scroll_to_edge(page, axis="y", end="start")
                return
            if v in {"bottom", "max", "end"}:
                await self._scroll_to_edge(page, axis="y", end="end")
                return
            if v in {"left"}:
                await self._scroll_to_edge(page, axis="x", end="start")
                return
            if v in {"right"}:
                await self._scroll_to_edge(page, axis="x", end="end")
                return
            await self._scroll_to_text(page, self.value)
            return

        try:
            axis = "y" if (self.up or self.down) else "x"
            positive = self.down or self.right
            sign = 1 if positive else -1

            if isinstance(self.value, int):
                amount = abs(self.value)
            else:
                inner = await page.evaluate("() => window.innerHeight" if axis == "y" else "() => window.innerWidth")
                amount = int(inner) if inner else 600

            dx, dy = (sign * amount, 0) if axis == "x" else (0, sign * amount)
            await self._scroll_by_value(page, dx=dx, dy=dy)
        except (PlaywrightError, PWTimeout, ValueError, TypeError) as e:
            action_logger.warning(f"ScrollAction failed with JS scrolling: {e}. Using keyboard fallback.")
            try:
                if self.left or (isinstance(self.value, str) and self.value.strip().lower() == "left"):
                    await page.keyboard.press("ArrowLeft")
                elif self.right or (isinstance(self.value, str) and self.value.strip().lower() == "right"):
                    await page.keyboard.press("ArrowRight")
                elif self.up or (isinstance(self.value, str) and self.value.strip().lower() in {"top", "start"}):
                    await page.keyboard.press("PageUp")
                else:
                    await page.keyboard.press("PageDown")
            except (PlaywrightError, PWTimeout) as kb_error:
                raise ValueError(f"ScrollAction completely failed: {e}") from kb_error
