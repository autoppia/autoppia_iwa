from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import Trajectory
from autoppia_iwa.src.execution.actions.actions import ClickAction, NavigateAction, TypeAction
from autoppia_iwa.src.execution.actions.base import Selector, SelectorType

BASE = "http://localhost:8000"
SEED = 1

_SEARCH_INPUT_SELECTOR = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="input")
_SEARCH_SUBMIT_SELECTOR = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="search-submit-button")


def _movie_link_selector(movie_id: str, movie_title: str) -> Selector:
    return Selector(
        type=SelectorType.XPATH_SELECTOR,
        value=f"//a[normalize-space()='{movie_title}' and contains(@href, '/movies/{movie_id}')][1]",
    )


FILM_DETAIL = Trajectory(
    name="FILM_DETAIL",
    prompt="Use search to open Inception details in seed 1.",
    actions=[
        NavigateAction(url=f"{BASE}/search?seed={SEED}"),
        ClickAction(selector=_SEARCH_INPUT_SELECTOR),
        TypeAction(selector=_SEARCH_INPUT_SELECTOR, text="Inception"),
        ClickAction(selector=_SEARCH_SUBMIT_SELECTOR),
        ClickAction(selector=_movie_link_selector("real-movie-007", "Inception")),
    ],
    tests=None,
)


SEARCH_FILM = Trajectory(
    name="SEARCH_FILM",
    prompt="Search for Schindler's List in seed 1.",
    actions=[
        NavigateAction(url=f"{BASE}/search?seed={SEED}"),
        ClickAction(selector=_SEARCH_INPUT_SELECTOR),
        TypeAction(selector=_SEARCH_INPUT_SELECTOR, text="Schindler's List"),
        ClickAction(selector=_SEARCH_SUBMIT_SELECTOR),
    ],
    tests=None,
)


def load_autocinema_use_case_completion_flows() -> dict[str, Trajectory]:
    return {
        "FILM_DETAIL": FILM_DETAIL,
        "SEARCH_FILM": SEARCH_FILM,
    }
