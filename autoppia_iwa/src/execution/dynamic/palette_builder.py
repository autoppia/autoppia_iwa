from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import html
import json
from typing import Iterable
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from autoppia_iwa.src.execution.dynamic.palette import MutationPalette, MutationTemplate


@dataclass
class PageSnapshot:
    url: str
    html: str


COMMON_TAG_SELECTORS = [
    "header",
    "nav",
    "main",
    "section",
    "article",
    "aside",
    "footer",
    "form",
    "table",
    "ul",
    "ol",
]


def _collect_class_selectors(soup: BeautifulSoup, limit: int = 8) -> list[str]:
    counter: Counter[str] = Counter()
    for element in soup.find_all(class_=True):
        for cls in element.get("class", []):
            if 2 < len(cls) <= 40 and cls.isascii():
                counter[cls] += 1
    return [f".{cls}" for cls, _ in counter.most_common(limit)]


def _collect_data_selectors(soup: BeautifulSoup, limit: int = 6) -> list[str]:
    selectors: list[str] = []
    for attr in ["data-testid", "data-test", "aria-label", "role"]:
        for element in soup.select(f"[{attr}]"):
            value = element.get(attr)
            if value and len(value) <= 32:
                selectors.append(f"[{attr}='{value}']")
                if len(selectors) >= limit:
                    return selectors
    return selectors


def _deduplicate(seq: Iterable[str]) -> list[str]:
    seen: dict[str, None] = {}
    for item in seq:
        if item not in seen:
            seen[item] = None
    return list(seen.keys())


def _candidate_selectors(soup: BeautifulSoup) -> list[str]:
    selectors: list[str] = []
    for selector in COMMON_TAG_SELECTORS:
        if soup.select_one(selector):
            selectors.append(selector)
    selectors.extend(_collect_class_selectors(soup))
    selectors.extend(_collect_data_selectors(soup))
    buttons = soup.select("button, a[class], input[type='submit']")
    if buttons:
        selectors.append("button")
    # cap the selector list so palettes stay focused on impactful nodes
    return _deduplicate(selectors)[:18]


def _slugify_path(path: str) -> str:
    slug = path.strip("/") or "home"
    slug = slug.replace("/", "_").replace("-", "_")
    return slug[:40]


def _structural_wrapper_html(idx: int) -> str:
    palette = [
        "border-radius:10px;border:1px dashed rgba(148,163,184,0.25);padding:2px;margin:2px 0;",
        "border-radius:6px;border:1px solid rgba(148,163,184,0.15);padding:1px;margin:1px 0;",
        "border-left:2px solid rgba(148,163,184,0.35);padding-left:4px;",
    ]
    style = palette[idx % len(palette)]
    return (
        "<div class='iwa-structural-wrapper' aria-hidden='true' data-iwa-structural='{{seed}}' "
        f"style='display:block;pointer-events:none;{style}'>"
        "<div style='height:0;overflow:hidden;'></div></div>"
    )


def _structural_spacer_html(idx: int) -> str:
    palette = [
        "height:1px;background:rgba(148,163,184,0.25);margin:6px 0;",
        "height:4px;background:transparent;margin:4px 0;border-top:1px solid rgba(148,163,184,0.12);",
        "height:0;margin:0;border-bottom:1px solid rgba(148,163,184,0.18);",
    ]
    style = palette[idx % len(palette)]
    return (
        "<div class='iwa-structural-spacer' aria-hidden='true' data-iwa-structural='{{seed}}' "
        f"style='display:block;pointer-events:none;{style}'></div>"
    )


def _structural_anchor_html(idx: int) -> str:
    palette = [
        "min-height:6px;display:block;",
        "min-height:4px;display:block;",
        "min-height:2px;display:block;",
    ]
    style = palette[idx % len(palette)]
    return (
        "<div class='iwa-structural-anchor' aria-hidden='true' data-iwa-structural='{{seed}}' "
        f"style='pointer-events:none;{style}'></div>"
    )


def _make_d1_templates(selector: str, path: str, idx: int) -> list[MutationTemplate]:
    base_id = f"{_slugify_path(path)}-d1-{idx}"
    wrapper_html = _structural_wrapper_html(idx)
    spacer_html = _structural_spacer_html(idx)
    anchor_html = _structural_anchor_html(idx)
    return [
        MutationTemplate(
            id=f"{base_id}-wrap",
            phase="d1",
            selector=selector,
            operation="wrap_with",
            html=wrapper_html,
            url_pattern=path,
        ),
        MutationTemplate(
            id=f"{base_id}-insert-before",
            phase="d1",
            selector=selector,
            operation="insert_before",
            html=spacer_html,
            url_pattern=path,
        ),
        MutationTemplate(
            id=f"{base_id}-insert-after",
            phase="d1",
            selector=selector,
            operation="insert_after",
            html=spacer_html,
            url_pattern=path,
        ),
        MutationTemplate(
            id=f"{base_id}-prepend",
            phase="d1",
            selector=selector,
            operation="prepend_child",
            html=anchor_html,
            url_pattern=path,
        ),
    ]


def _make_d3_templates(selector: str, path: str, idx: int) -> list[MutationTemplate]:
    base_id = f"{_slugify_path(path)}-d3-{idx}"
    safe_path = html.escape(path or "/").replace(" ", "")
    return [
        MutationTemplate(
            id=f"{base_id}-data-variant",
            phase="d3",
            selector=selector,
            operation="set_attribute",
            attribute="data-iwa-variant",
            value=f"{safe_path}-s{{{{seed}}}}",
            url_pattern=path,
        ),
        MutationTemplate(
            id=f"{base_id}-data-slot",
            phase="d3",
            selector=selector,
            operation="set_attribute",
            attribute="data-layout-slot",
            value=f"slot-{{{{seed}}}}-{idx}",
            url_pattern=path,
        ),
        MutationTemplate(
            id=f"{base_id}-class",
            phase="d3",
            selector=selector,
            operation="append_class",
            value=f"iwa-variant--{idx % 5}-{{{{seed}}}}",
            url_pattern=path,
        ),
    ]


def _overlay_variants() -> list[dict[str, str | bool]]:
    return [
        {
            "name": "cookie",
            "overlay_type": "cookie",
            "html": (
                "<div class='iwa-overlay iwa-overlay--cookie' style='position:fixed;bottom:16px;left:16px;right:16px;"
                "max-width:420px;margin:auto;z-index:2147483647;background:#0f172a;color:#fff;"
                "border-radius:14px;padding:16px;box-shadow:0 24px 50px rgba(15,23,42,0.3);font-family:sans-serif;'>"
                "<p style='margin:0 0 6px;font-weight:600;'>Heads up</p>"
                "<p style='margin:0;font-size:14px;opacity:0.85;'>We keep a short session buffer active while you complete this flow.</p>"
                "<div style='display:flex;gap:8px;margin-top:12px;flex-wrap:wrap;'>"
                "<button data-iwa-dismiss style='flex:1;min-width:140px;padding:10px 14px;border:none;border-radius:10px;"
                "background:#22c55e;color:#0f172a;font-weight:600;'>Sounds good</button>"
                "<button style='flex:1;min-width:120px;padding:10px 14px;border-radius:10px;border:1px solid rgba(148,163,184,0.45);"
                "background:transparent;color:#e2e8f0;'>Details</button>"
                "</div></div>"
            ),
        },
        {
            "name": "announcement",
            "overlay_type": "banner",
            "html": (
                "<div class='iwa-overlay iwa-overlay--banner' style='position:fixed;top:0;left:0;right:0;padding:12px 20px;"
                "background:#f97316;color:#0f172a;font-family:sans-serif;font-size:14px;z-index:2147483647;"
                "box-shadow:0 10px 25px rgba(15,23,42,0.2);display:flex;justify-content:space-between;gap:16px;align-items:center;'>"
                "<span style='font-weight:600;'>Dynamic review in progress</span>"
                "<button data-iwa-dismiss style='padding:6px 14px;border:none;border-radius:999px;background:#0f172a;color:#fff;'>Dismiss</button>"
                "</div>"
            ),
        },
        {
            "name": "pulse",
            "overlay_type": "modal",
            "html": (
                "<div class='iwa-overlay iwa-overlay--pulse' style='position:fixed;right:18px;bottom:18px;width:320px;"
                "background:#fff;color:#0f172a;border-radius:16px;padding:18px;box-shadow:0 35px 60px rgba(15,23,42,0.35);"
                "font-family:sans-serif;z-index:2147483647;'>"
                "<p style='margin:0 0 8px;font-weight:600;'>Session heartbeat</p>"
                "<p style='margin:0 0 16px;font-size:13px;color:#475569;'>Confirm activity so automated flows keep running.</p>"
                "<button data-iwa-dismiss style='padding:9px 14px;border:none;border-radius:10px;background:#2563eb;color:#fff;width:100%;'>Continue</button>"
                "</div>"
            ),
        },
    ]


def _make_d4_templates(path: str, idx: int) -> list[MutationTemplate]:
    variants = _overlay_variants()
    variant = variants[idx % len(variants)]
    base_id = f"{_slugify_path(path)}-d4-{idx}"
    return [
        MutationTemplate(
            id=base_id,
            phase="d4",
            selector="body",
            operation="overlay",
            html=variant["html"],  # type: ignore[arg-type]
            overlay_type=variant["overlay_type"],  # type: ignore[arg-type]
            blocking=False,
            dismiss_selector="[data-iwa-dismiss]",
            trigger_after=2 + (idx % 3),
            url_pattern=path,
        )
    ]


def build_palette(project_id: str, snapshots: list[PageSnapshot], *, generated_by: str = "palette-builder", max_templates_per_phase: int = 60) -> MutationPalette:
    templates: list[MutationTemplate] = []
    seen_keys: set[tuple[str, str, str]] = set()
    per_phase_counts = {"d1": 0, "d3": 0, "d4": 0}

    for snapshot in snapshots:
        soup = BeautifulSoup(snapshot.html, "html.parser")
        selectors = _candidate_selectors(soup)
        if not selectors:
            continue
        path = urlsplit(snapshot.url).path or "/"
        for idx, selector in enumerate(selectors):
            for template in _make_d1_templates(selector, path, idx):
                if per_phase_counts["d1"] >= max_templates_per_phase:
                    break
                key = (template.phase, template.selector, template.operation, template.url_pattern)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                templates.append(template)
                per_phase_counts["d1"] += 1
            if per_phase_counts["d1"] >= max_templates_per_phase:
                break
        for idx, selector in enumerate(selectors):
            for template in _make_d3_templates(selector, path, idx):
                if per_phase_counts["d3"] >= max_templates_per_phase:
                    break
                key = (template.phase, template.selector, template.operation, template.url_pattern)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                templates.append(template)
                per_phase_counts["d3"] += 1
            if per_phase_counts["d3"] >= max_templates_per_phase:
                break

        if per_phase_counts["d4"] < max_templates_per_phase:
            for idx in range(min(3, max_templates_per_phase - per_phase_counts["d4"])):
                for template in _make_d4_templates(path, idx + per_phase_counts["d4"]):
                    key = (template.phase, template.selector, template.overlay_type, template.url_pattern)
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)
                    templates.append(template)
                    per_phase_counts["d4"] += 1
                    if per_phase_counts["d4"] >= max_templates_per_phase:
                        break
                if per_phase_counts["d4"] >= max_templates_per_phase:
                    break

    return MutationPalette(project_id=project_id, generated_by=generated_by, templates=templates)


__all__ = ["PageSnapshot", "build_palette"]
