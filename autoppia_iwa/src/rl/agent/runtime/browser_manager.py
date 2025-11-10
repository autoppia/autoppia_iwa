from __future__ import annotations

"""
BrowserManager: obtiene estado del DOM desde Playwright Page y construye
Top‑K de candidatos + máscaras y features para la observación.

Para simplicidad y velocidad inicial:
- Candidatos = elementos con tag/button/a/input/textarea o role relevante o editable.
- Heurística de ranking: clicabilidad + role bonus + similitud con prompt + centro en viewport.
"""

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass
class Candidate:
    idx: int
    tag: str
    role: str | None
    text: str
    clickable: bool
    focusable: bool
    editable: bool
    visible: bool
    enabled: bool
    bbox: Tuple[float, float, float, float] | None

    def center(self) -> Tuple[float | None, float | None]:
        if not self.bbox:
            return None, None
        x, y, w, h = self.bbox
        try:
            return float(x + w / 2.0), float(y + h / 2.0)
        except Exception:
            return None, None


def _tokenize(s: str) -> list[str]:
    import re

    s = (s or "").lower().strip()
    return [t for t in re.split(r"[^\w]+", s) if t]


class BrowserManager:
    def __init__(self, page):
        self.page = page

    async def snapshot_text(self) -> Tuple[str, str]:
        html = await self.page.content()
        url = self.page.url
        return html, url

    async def candidates(self) -> List[Candidate]:
        js = """
        () => {
          const nodes = [];
          const q = document.querySelectorAll('button, a, input, textarea, [role]');
          let i = 0;
          for (const el of q) {
            const style = window.getComputedStyle(el);
            const rect = el.getBoundingClientRect();
            const visible = !!(rect && rect.width > 1 && rect.height > 1) && style.visibility !== 'hidden' && style.display !== 'none';
            const enabled = !el.disabled;
            const tag = (el.tagName || '').toLowerCase();
            const role = (el.getAttribute('role') || '').toLowerCase();
            const type = (el.getAttribute('type') || '').toLowerCase();
            const text = (el.innerText || el.value || '').trim();
            const clickable = ['button','a'].includes(tag) || role === 'button' || type === 'submit' || type === 'search';
            const focusable = (el.tabIndex >= 0) || ['input','textarea','select'].includes(tag) || el.isContentEditable === true;
            const editable = ['input','textarea'].includes(tag) || el.isContentEditable === true;
            nodes.push({
              idx: i++, tag, role, text, clickable, focusable, editable,
              visible, enabled,
              bbox: rect ? [rect.x, rect.y, rect.width, rect.height] : null,
            });
          }
          return nodes;
        }
        """
        raw = await self.page.evaluate(js)
        out: List[Candidate] = []
        for d in raw or []:
            out.append(
                Candidate(
                    idx=int(d.get("idx", 0)),
                    tag=str(d.get("tag", "")),
                    role=str(d.get("role")) if d.get("role") else None,
                    text=str(d.get("text", "")),
                    clickable=bool(d.get("clickable", False)),
                    focusable=bool(d.get("focusable", False)),
                    editable=bool(d.get("editable", False)),
                    visible=bool(d.get("visible", True)),
                    enabled=bool(d.get("enabled", True)),
                    bbox=tuple(d.get("bbox")) if d.get("bbox") else None,
                )
            )
        return out

    async def topk(self, task_prompt: str, K: int) -> Tuple[List[Candidate], np.ndarray, dict]:
        cands = await self.candidates()
        toks_goal = set(_tokenize(task_prompt))

        def score(c: Candidate) -> float:
            if not (c.visible and c.enabled):
                return 0.0
            s = 0.0
            if c.clickable:
                s += 1.0
            if c.focusable:
                s += 0.3
            if c.editable:
                s += 0.2
            role_bonus = {"button": 1.0, "link": 0.9, "submit": 0.95, "textbox": 0.8}.get((c.role or "").lower())
            if role_bonus:
                s += role_bonus
            # similitud simple por solapamiento
            toks = _tokenize(c.text)
            if toks and toks_goal:
                ov = sum(1 for t in toks if t in toks_goal)
                s += ov / max(1.0, np.sqrt(len(toks_goal) * len(toks)))
            # ligera preferencia por centro
            cx, cy = c.center()
            if cx is not None and cy is not None:
                # normalizamos suponiendo 1920x1080
                cxn, cyn = min(1.0, max(0.0, cx / 1920.0)), min(1.0, max(0.0, cy / 1080.0))
                s += 0.05 * (1.0 - abs(0.5 - cxn)) + 0.05 * (1.0 - abs(0.5 - cyn))
            return float(s)

        scored = [(c, score(c)) for c in cands]
        scored.sort(key=lambda x: x[1], reverse=True)
        top = [c for c, s in scored[:K] if s > 0.0]

        # máscara CLICK_K
        click_mask = np.zeros((K,), dtype=np.bool_)
        for i, c in enumerate(top):
            click_mask[i] = bool(c.clickable and c.visible and c.enabled)

        # macros
        macros = {
            "type_confirm": any(c.focusable and c.visible and c.enabled for c in cands),
            "submit": any(
                (c.clickable and c.visible and c.enabled and ((c.role or "").lower() in {"button", "submit"} or any(k in (c.text or "").lower() for k in ("submit", "search", "go"))))
                for c in cands
            ),
            "scroll_down": True,
            "scroll_up": True,
            "back": True,
        }

        return top, click_mask, macros

