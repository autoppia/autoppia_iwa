"""Helpers to convert evaluation snapshots into policy-aligned observations."""

from __future__ import annotations

import html
import re

from ..models.schemas import BrowserSnapshot, ObsPublic

URL_SPLIT = re.compile(r"[/:?&#=._-]+")
SCRIPT_BLOCK = re.compile(r"<script[\s\S]*?</script>", flags=re.IGNORECASE)
STYLE_BLOCK = re.compile(r"<style[\s\S]*?</style>", flags=re.IGNORECASE)
TAG_BLOCK = re.compile(r"<[^>]+>")
WHITESPACE = re.compile(r"\s+")


def clean_dom(html_text: str, max_chars: int = 3_000) -> str:
    """Return a lightweight text version of the DOM suitable for LLM/encoders."""

    text = SCRIPT_BLOCK.sub(" ", html_text)
    text = STYLE_BLOCK.sub(" ", text)
    text = TAG_BLOCK.sub(" ", text)
    text = html.unescape(text)
    text = WHITESPACE.sub(" ", text).strip()
    return text[:max_chars]


def tokenize_url(url: str, limit: int = 50) -> list[str]:
    tokens = [tok for tok in URL_SPLIT.split(url) if tok]
    return tokens[:limit]


def snap_to_obs_public(snap: BrowserSnapshot, prev_url: str | None, stagnation_steps: int) -> ObsPublic:
    """Convert a snapshot into the observation visible to the policy."""

    url_changed = 0.0 if prev_url == snap.current_url else 1.0
    dom_excerpt = clean_dom(snap.current_html)
    dyn = {
        "url_changed": url_changed,
        "stagnation": float(stagnation_steps),
        "iteration_norm": float(snap.iteration),
    }
    return ObsPublic(
        url_tokens=tokenize_url(snap.current_url),
        dom_excerpt=dom_excerpt,
        dyn=dyn,
        action_prev=snap.action.kind if snap.action else None,
    )
