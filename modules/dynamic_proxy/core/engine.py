from __future__ import annotations

import json
import random
import time
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag
from loguru import logger

from autoppia_iwa.src.execution.dynamic.palette import PalettePlanGenerator, load_palette_for_project

from .config import DynamicPhaseConfig
from .palettes import load_palette_from_module


@dataclass
class OverlayInstruction:
    trigger_after: int
    html: str
    overlay_type: str
    blocking: bool
    dismiss_selector: str | None

    def to_payload(self) -> dict[str, Any]:
        return {
            "trigger_after": self.trigger_after,
            "html": self.html,
            "overlay_type": self.overlay_type,
            "blocking": self.blocking,
            "dismiss_selector": self.dismiss_selector,
        }


@dataclass
class MutationAuditRecord:
    project_id: str
    url: str
    seed: int
    html_before: str
    html_after: str
    plan: dict[str, Any]
    plan_source: str
    plan_duration_ms: float
    mutation_duration_ms: float
    cache_key: str | None
    delta_bytes: int
    phases: dict[str, bool]
    metrics: dict[str, int]


@dataclass
class MutationResult:
    html: str
    plan: dict[str, Any] | None
    audit_record: MutationAuditRecord | None


class MutationEngine:
    """
    HTML mutation engine shared by the dynamic proxy and any other service that wants
    to mutate demo-web HTML outside of Playwright.
    """

    def __init__(self, project_id: str, phase_config: DynamicPhaseConfig) -> None:
        self.project_id = project_id
        self.phase_config = phase_config
        self._palette = self._load_palette()
        self._plan_cache: dict[int, OrderedDict[str, dict[str, Any]]] = defaultdict(OrderedDict)

    def _load_palette(self):
        palette_dir = Path(self.phase_config.palette_dir).expanduser() if self.phase_config.palette_dir else None
        palette = load_palette_for_project(self.project_id, palette_dir) if palette_dir else None
        if palette is None and self.phase_config.use_module_palettes:
            palette = load_palette_from_module(self.project_id)
        return palette

    def mutate_html(self, html: str, url: str, seed: int) -> MutationResult:
        plan_seed = self._normalize_seed(seed)
        should_generate_plan = self.phase_config.any_enabled() or getattr(self.phase_config, "force_generate_plan", False)
        if not should_generate_plan:
            return MutationResult(html=html, plan=None, audit_record=None)

        metrics = {"cache_hits": 0, "cache_misses": 0, "overlays_injected": 0}
        plan, metadata = self._get_dom_plan(html, url, seed, plan_seed, metrics)
        mutation_started = time.perf_counter()
        soup = BeautifulSoup(html, "html.parser")

        apply_dom = getattr(self.phase_config, "apply_dom_mutations", True)

        if self.phase_config.enable_d1_structure and apply_dom:
            self._apply_structural_mutations(soup, plan.get("d1", []), seed, url)

        if self.phase_config.enable_d3_attributes and apply_dom:
            self._apply_attribute_mutations(soup, plan.get("d3", []))

        overlays: list[OverlayInstruction] = []
        if self.phase_config.enable_d4_overlays:
            overlays = self._build_overlay_instructions(plan.get("d4", []), seed, url)
            metrics["overlays_injected"] = len(overlays)
            self._ensure_overlay_bootstrap(soup, overlays)

        mutated = str(soup)
        mutation_duration_ms = (time.perf_counter() - mutation_started) * 1000
        delta = len(mutated) - len(html)
        logger.debug(f"[DYNAMIC PROXY] project={self.project_id} seed={seed} delta={delta} bytes source={metadata['plan_source']}")

        audit_record = MutationAuditRecord(
            project_id=self.project_id,
            url=url,
            seed=seed,
            html_before=html,
            html_after=mutated,
            plan=plan,
            plan_source=metadata["plan_source"],
            plan_duration_ms=metadata["plan_duration_ms"],
            mutation_duration_ms=mutation_duration_ms,
            cache_key=metadata.get("cache_key"),
            delta_bytes=delta,
            phases={
                "d1": self.phase_config.enable_d1_structure,
                "d3": self.phase_config.enable_d3_attributes,
                "d4": self.phase_config.enable_d4_overlays,
            },
            metrics=metrics,
        )
        return MutationResult(html=mutated, plan=plan, audit_record=audit_record)

    def _get_dom_plan(self, html: str, url: str, seed: int, plan_seed: int, metrics: dict[str, int]) -> tuple[dict[str, Any], dict[str, Any]]:
        cache_key = f"{self.project_id}:{plan_seed}:{url}"
        normalized_html = self._normalize_html(html)
        start = time.perf_counter()

        cache = self._plan_cache[plan_seed]
        existing = cache.get(cache_key)
        if existing:
            metrics["cache_hits"] += 1
            return existing["plan"], {
                "plan_source": "cache",
                "plan_duration_ms": (time.perf_counter() - start) * 1000,
                "cache_key": cache_key,
            }

        similar = self._find_similar_plan(cache, normalized_html)
        if similar:
            metrics["cache_hits"] += 1
            self._remember_plan(seed, cache_key, normalized_html, similar)
            return similar, {
                "plan_source": "similar",
                "plan_duration_ms": (time.perf_counter() - start) * 1000,
                "cache_key": cache_key,
            }

        if self._palette:
            generator = PalettePlanGenerator(
                self._palette,
                seed=seed,
                random_seed=plan_seed,
                max_per_phase=self.phase_config.palette_max_per_phase,
            )
            plan = generator.build_plan(url)
            plan_source = "palette"
        else:
            plan = self._fallback_plan(plan_seed, url)
            plan_source = "fallback"
            metrics["cache_misses"] += 1

        self._remember_plan(plan_seed, cache_key, normalized_html, plan)
        return plan, {
            "plan_source": plan_source,
            "plan_duration_ms": (time.perf_counter() - start) * 1000,
            "cache_key": cache_key,
        }

    def _remember_plan(self, seed: int, cache_key: str, normalized_html: str, plan: dict[str, Any]) -> None:
        cache = self._plan_cache[seed]
        cache[cache_key] = {"plan": plan, "normalized": normalized_html}
        if len(cache) > self.phase_config.instruction_cache_size:
            cache.popitem(last=False)

    def _find_similar_plan(self, cache: OrderedDict[str, dict[str, Any]], normalized_html: str) -> dict[str, Any] | None:
        threshold = self.phase_config.html_similarity_threshold
        for entry in cache.values():
            ratio = SequenceMatcher(None, normalized_html, entry["normalized"]).ratio()
            if ratio >= threshold:
                return entry["plan"]
        return None

    def _apply_structural_mutations(self, soup: BeautifulSoup, instructions: list[dict[str, Any]], seed: int, url: str) -> None:
        rng = random.Random(f"{self.project_id}:{seed}:{url}:d1")
        for instr in instructions:
            target_selector = instr.get("target")
            html_fragment = instr.get("html", "")
            operation = instr.get("operation", "append_child")
            if not target_selector or not html_fragment:
                continue
            try:
                target = soup.select_one(target_selector)
            except Exception:
                target = None
            if target is None:
                continue
            fragment = BeautifulSoup(html_fragment, "html.parser")
            if operation == "insert_before":
                target.insert_before(fragment)
            elif operation == "insert_after":
                target.insert_after(fragment)
            elif operation == "prepend_child":
                target.insert(0, fragment)
            elif operation == "wrap_with":
                target.wrap(fragment)
            elif operation == "replace_inner_html":
                target.clear()
                target.append(fragment)
            elif operation == "shuffle_children":
                children = [child for child in target.contents if isinstance(child, Tag)]
                rng.shuffle(children)
                target.clear()
                for child in children:
                    target.append(child)
            else:
                target.append(fragment)

    def _apply_attribute_mutations(self, soup: BeautifulSoup, instructions: list[dict[str, Any]]) -> None:
        for instr in instructions:
            target_selector = instr.get("target")
            operation = instr.get("operation")
            if not target_selector or not operation:
                continue
            try:
                target = soup.select_one(target_selector)
            except Exception:
                target = None
            if target is None:
                continue

            if operation == "rename_attribute":
                original = instr.get("attribute")
                new_name = instr.get("new_name")
                if original and new_name and original in target.attrs:
                    target.attrs[new_name] = target.attrs.pop(original)
            elif operation == "set_attribute":
                attribute = instr.get("attribute")
                value = instr.get("value", "")
                if attribute:
                    target.attrs[attribute] = value
            elif operation == "replace_text":
                new_text = instr.get("text", "")
                if hasattr(target, "string") and target.string:
                    target.string.replace_with(new_text)
                else:
                    target.append(new_text)
            elif operation == "append_class":
                cls = instr.get("value")
                if cls:
                    existing = target.get("class", [])
                    if cls not in existing:
                        existing.append(cls)
                        target["class"] = existing
            elif operation == "remove_attribute":
                attribute = instr.get("attribute")
                if attribute and attribute in target.attrs:
                    target.attrs.pop(attribute, None)

    def _build_overlay_instructions(self, overlays: list[dict[str, Any]], seed: int, url: str) -> list[OverlayInstruction]:
        instructions: list[OverlayInstruction] = []
        plan_overlays = overlays or self._fallback_overlay_plan(seed, url)
        rng = random.Random(f"{self.project_id}:{seed}:{url}:d4")

        for item in plan_overlays:
            html = item.get("html", "")
            overlay_type = item.get("overlay_type", "modal")
            blocking = item.get("blocking", overlay_type in {"cookie", "modal"})
            dismiss_selector = item.get("dismiss_selector")
            trigger_after = item.get("trigger_after")
            if trigger_after == "random" or not isinstance(trigger_after, int):
                trigger_after = rng.randint(self.phase_config.d4_min_action, self.phase_config.d4_max_action)
            if not html or not isinstance(trigger_after, int):
                continue
            instructions.append(
                OverlayInstruction(
                    trigger_after=trigger_after,
                    html=html,
                    overlay_type=overlay_type,
                    blocking=bool(blocking),
                    dismiss_selector=dismiss_selector or "[data-iwa-dismiss]",
                )
            )
        return instructions

    def _ensure_overlay_bootstrap(self, soup: BeautifulSoup, overlays: list[OverlayInstruction]) -> None:
        if not overlays:
            return
        payload = [overlay.to_payload() for overlay in overlays]
        script = self._build_overlay_script(payload)
        script_tag = soup.new_tag("script")
        script_tag["data-iwa-overlay-bootstrap"] = "true"
        script_tag.string = script
        target = soup.body or soup
        target.append(script_tag)

    def _build_overlay_script(self, payload: list[dict[str, Any]]) -> str:
        data = json.dumps(payload, ensure_ascii=False)
        return (
            "(function(){"
            "if(window.__iwaOverlayProxy){return;}window.__iwaOverlayProxy=true;"
            f"const configs={data};"
            "if(!configs.length){return;}"
            "const state=configs.map(cfg=>Object.assign({fired:false},cfg));"
            "let actionCount=0;"
            "const inject=(cfg)=>{"
            "const wrapper=document.createElement('div');"
            "wrapper.innerHTML=(cfg.html||'').trim();"
            "const node=wrapper.firstElementChild;"
            "if(!node){return false;}"
            "node.dataset.iwaOverlay=cfg.overlay_type||'banner';"
            "if(!node.hasAttribute('tabindex')){node.tabIndex=0;}"
            "node.style.pointerEvents='auto';"
            "document.body.appendChild(node);"
            "const cleanup=()=>{if(node.parentElement){node.parentElement.removeChild(node);}};"
            "const selector=cfg.dismiss_selector||'[data-iwa-dismiss]';"
            "const button=node.matches(selector)?node:node.querySelector(selector);"
            "if(button){button.addEventListener('click',cleanup,{once:true});}"
            "return true;"
            "};"
            "const maybeTrigger=()=>{"
            "state.forEach(cfg=>{"
            "if(!cfg.fired&&actionCount>=cfg.trigger_after){"
            "if(inject(cfg)){cfg.fired=true;}"
            "}"
            "});"
            "if(state.every(cfg=>cfg.fired)){detach();}"
            "};"
            "const handler=()=>{actionCount+=1;maybeTrigger();};"
            "const detach=()=>{['click','keydown','wheel'].forEach(evt=>document.removeEventListener(evt,handler));};"
            "['click','keydown','wheel'].forEach(evt=>document.addEventListener(evt,handler,{passive:true}));"
            "setTimeout(()=>{actionCount=Math.max(actionCount,Math.min(...state.map(cfg=>cfg.trigger_after||1)));maybeTrigger();},2000);"
            "})();"
        )

    def _fallback_plan(self, seed: int, url: str) -> dict[str, Any]:
        rng = random.Random(f"{self.project_id}:{seed}:{url}:fallback")
        shell_html = (
            "<div class='iwa-structural-wrapper' aria-hidden='true' style='display:block;"
            "pointer-events:none;border:1px dashed rgba(148,163,184,0.25);margin:2px 0;'></div>"
        )
        spacer_html = (
            "<div class='iwa-structural-spacer' aria-hidden='true' style='display:block;height:2px;"
            "margin:6px 0;border-bottom:1px solid rgba(148,163,184,0.2);pointer-events:none;'></div>"
        )
        d1 = [
            {"operation": "wrap_with", "target": "main", "html": shell_html},
            {"operation": "insert_before", "target": "section", "html": spacer_html},
        ]
        d3 = [
            {
                "operation": "set_attribute",
                "target": "button",
                "attribute": "data-layout-slot",
                "value": f"slot-{seed % 7}",
            },
            {
                "operation": "set_attribute",
                "target": "nav",
                "attribute": "data-iwa-variant",
                "value": f"nav-{seed % 5}",
            },
            {"operation": "append_class", "target": "header", "value": f"iwa-variant--{rng.randint(1,4)}"},
        ]
        d4 = self._fallback_overlay_plan(seed, url)
        return {"d1": d1, "d3": d3, "d4": d4}

    def _fallback_overlay_plan(self, seed: int, url: str) -> list[dict[str, Any]]:
        rng = random.Random(f"{self.project_id}:{seed}:{url}:overlay")
        variants = [
            {
                "overlay_type": "cookie",
                "html": (
                    "<div class='iwa-overlay iwa-overlay--cookie' style='position:fixed;bottom:16px;left:16px;right:16px;"
                    "max-width:420px;margin:auto;z-index:2147483647;background:#0f172a;color:#fff;border-radius:14px;"
                    "padding:16px;box-shadow:0 24px 50px rgba(15,23,42,0.3);font-family:sans-serif;'>"
                    "<p style='margin:0 0 6px;font-weight:600;'>Session cookies enabled</p>"
                    "<p style='margin:0;font-size:14px;opacity:0.85;'>We keep a tiny buffer active while you finish this task.</p>"
                    "<button data-iwa-dismiss style='margin-top:12px;padding:9px 14px;border:none;border-radius:10px;"
                    "background:#22c55e;color:#0f172a;font-weight:600;width:100%;'>OK</button>"
                    "</div>"
                ),
            },
            {
                "overlay_type": "banner",
                "html": (
                    "<div class='iwa-overlay iwa-overlay--banner' style='position:fixed;top:0;left:0;right:0;padding:12px 20px;"
                    "background:#f97316;color:#0f172a;font-family:sans-serif;font-size:14px;z-index:2147483647;"
                    "box-shadow:0 10px 25px rgba(15,23,42,0.2);display:flex;justify-content:space-between;gap:16px;align-items:center;'>"
                    "<span style='font-weight:600;'>Dynamic seed active</span>"
                    "<button data-iwa-dismiss style='padding:6px 14px;border:none;border-radius:999px;background:#0f172a;color:#fff;'>Dismiss</button>"
                    "</div>"
                ),
            },
            {
                "overlay_type": "modal",
                "html": (
                    "<div class='iwa-overlay iwa-overlay--pulse' style='position:fixed;right:18px;bottom:18px;width:320px;"
                    "background:#fff;color:#0f172a;border-radius:16px;padding:18px;box-shadow:0 35px 60px rgba(15,23,42,0.35);"
                    "font-family:sans-serif;z-index:2147483647;'>"
                    "<p style='margin:0 0 8px;font-weight:600;'>Heartbeat check</p>"
                    "<p style='margin:0 0 16px;font-size:13px;color:#475569;'>Confirm so we keep the experience fresh for automation.</p>"
                    "<button data-iwa-dismiss style='padding:9px 14px;border:none;border-radius:10px;background:#2563eb;color:#fff;width:100%;'>Continue</button>"
                    "</div>"
                ),
            },
        ]
        variant = rng.choice(variants)
        return [
            {
                "trigger_after": rng.randint(self.phase_config.d4_min_action, self.phase_config.d4_max_action),
                "html": variant["html"],
                "overlay_type": variant["overlay_type"],
                "blocking": False,
                "dismiss_selector": "[data-iwa-dismiss]",
            }
        ]

    @staticmethod
    def _normalize_html(html: str) -> str:
        return " ".join(html.split())

    def _normalize_seed(self, seed: int) -> int:
        modulus = getattr(self.phase_config, "seed_modulus", 0) or 0
        if modulus > 0:
            return seed % modulus
        return seed


__all__ = [
    "MutationEngine",
    "MutationResult",
    "MutationAuditRecord",
    "DynamicPhaseConfig",
]
