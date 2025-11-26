from __future__ import annotations

"""
ActionAdapter: traduce acciones discretas del entorno RL a BaseActions reales
del sistema (ClickAction, TypeAction, ScrollAction, NavigateAction, etc.).
"""

from dataclasses import dataclass
from typing import List, Optional

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import (
    ClickAction,
    HoldKeyAction,
    NavigateAction,
    ScrollAction,
    TypeAction,
)
from .browser_manager import Candidate


@dataclass
class ActionLayout:
    topk: int
    # [NOOP] + [CLICK_0..K-1] + macros
    offset_click: int = 1
    macros: tuple[str, ...] = ("type_confirm", "submit", "scroll_down", "scroll_up", "back")

    @property
    def offset_macros(self) -> int:
        return self.offset_click + self.topk

    @property
    def n_actions(self) -> int:
        return 1 + self.topk + len(self.macros)


class ActionAdapter:
    def __init__(self, layout: ActionLayout):
        self.layout = layout

    def adapt(self, action_index: int, candidates: List[Candidate], task: Task):
        # NOOP
        if action_index == 0:
            return None

        # CLICK_i
        if self.layout.offset_click <= action_index < self.layout.offset_macros:
            i = action_index - self.layout.offset_click
            if i < 0 or i >= len(candidates):
                return None
            c = candidates[i]
            cx, cy = c.center()
            if cx is None or cy is None:
                return None
            return ClickAction(x=int(cx), y=int(cy))

        # MACROS
        m_idx = action_index - self.layout.offset_macros
        if m_idx < 0 or m_idx >= len(self.layout.macros):
            return None
        name = self.layout.macros[m_idx]
        if name == "type_confirm":
            text = str((task.relevant_data or {}).get("type_text") or task.prompt or "").strip()
            if not text:
                return None
            return TypeAction(text=text)
        if name == "submit":
            # Usamos Enter por simplicidad/robustez
            return HoldKeyAction(key="Enter")
        if name == "scroll_down":
            return ScrollAction(down=True)
        if name == "scroll_up":
            return ScrollAction(up=True)
        if name == "back":
            return NavigateAction(go_back=True)
        return None

