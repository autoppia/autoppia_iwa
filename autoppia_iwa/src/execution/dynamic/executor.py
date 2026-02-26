from __future__ import annotations

import contextlib
import random
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Literal

from bs4 import BeautifulSoup, Tag
from loguru import logger
from playwright.async_api import Page, Route
from pydantic import BaseModel

from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.dynamic.palette import PalettePlanGenerator, load_palette_for_project
from modules.dynamic_proxy.core.palettes import load_palette_from_module


class DynamicPhaseConfig(BaseModel):
    """
    Controls which dynamic phases (D1/D3/D4) are enabled during browser execution.
    """

    enable_d1_structure: bool = False
    enable_d3_attributes: bool = False
    enable_d4_overlays: bool = False

    d4_min_action: int = 2
    d4_max_action: int = 5

    instruction_cache_size: int = 24
    html_similarity_threshold: float = 0.95

    palette_dir: str | None = None
    palette_max_per_phase: int = 3
    use_module_palettes: bool = True
    apply_dom_mutations: bool = True
    force_generate_plan: bool = False
    seed_modulus: int = 32

    def any_enabled(self) -> bool:
        return self.enable_d1_structure or self.enable_d3_attributes or self.enable_d4_overlays


@dataclass
class OverlayInstruction:
    trigger_after: int
    html: str
    overlay_type: Literal["modal", "banner", "cookie"]
    has_fired: bool = False
    blocking: bool = False
    dismiss_selector: str | None = None


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


class DynamicPlaywrightExecutor(PlaywrightBrowserExecutor):
    """
    Extends the Playwright executor adding three dynamic phases:

    - D1: structural DOM mutations (wrapper divs, re-ordering, inserts).
        - D3: attribute/text rewrites to invalidate brittle selectors.
    - D4: runtime overlays (modals/banners) injected after specific actions.

    Plans come from deterministic palettes (if configured) or built-in seed-driven fallbacks.
    """

    # ============================================================================
    # INITIALIZATION
    # ============================================================================

    def __init__(
        self,
        browser_config,
        page: Page,
        backend_demo_webs_service,
        *,
        dynamic_config: DynamicPhaseConfig | None,
        project_id: str,
        seed: int | None,
        audit_callback: Callable[[MutationAuditRecord], None] | None = None,
    ):
        super().__init__(browser_config, page, backend_demo_webs_service)
        self.dynamic_config = dynamic_config or DynamicPhaseConfig()
        self.project_id = project_id
        self.seed = seed or 0
        self._plan_seed = self.seed % self.dynamic_config.seed_modulus
        self._audit_callback = audit_callback

        self._route_installed = False
        self._dom_plan_cache: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._overlay_instructions: list[OverlayInstruction] = []
        self._rng = random.Random(self._plan_seed)
        self._metrics = {"cache_hits": 0, "cache_misses": 0, "overlays_injected": 0}
        self._last_plan_metadata: dict[str, Any] | None = None
        palette_dir = Path(self.dynamic_config.palette_dir).expanduser() if self.dynamic_config.palette_dir else None
        self._palette = None
        if palette_dir:
            self._palette = load_palette_for_project(self.project_id, palette_dir)
        if self._palette is None and self.dynamic_config.use_module_palettes:
            self._palette = load_palette_from_module(self.project_id)
        self._palette_generator = None
        if self._palette:
            self._palette_generator = PalettePlanGenerator(
                palette=self._palette,
                seed=self.seed,
                random_seed=self._plan_seed,
                max_per_phase=self.dynamic_config.palette_max_per_phase,
            )

    # ============================================================================
    # HOOK METHODS
    # ============================================================================

    async def _before_action(self, action: BaseAction, iteration: int) -> None:
        if not self.dynamic_config.any_enabled():
            return
        await self._ensure_route()

    async def _after_action(self, action: BaseAction, iteration: int) -> None:
        if not (self.dynamic_config.enable_d4_overlays and self._overlay_instructions):
            return
        await self._maybe_trigger_overlays(iteration + 1)

    # ============================================================================
    # ROUTE HANDLING
    # ============================================================================

    async def _ensure_route(self) -> None:
        if self._route_installed or not self.page:
            return
        await self.page.route("**/*", self._handle_route)
        self._route_installed = True

    async def _handle_route(self, route: Route) -> None:
        if not self.dynamic_config.any_enabled():
            await route.continue_()
            return

        try:
            response = await route.fetch()
        except Exception as exc:
            logger.debug(f"Route fetch failed ({route.request.url}): {exc}")
            with contextlib.suppress(Exception):
                await route.continue_()
            return
        try:
            content_type = response.headers.get("content-type", "")
        except AttributeError:
            content_type = ""

        body = await response.body()
        is_html = "text/html" in content_type or route.request.resource_type == "document"
        if not is_html:
            await route.fulfill(status=response.status, headers=response.headers, body=body)
            return

        html = body.decode("utf-8", errors="ignore")
        mutated_html = self._mutate_html(html, route.request.url)

        new_body = mutated_html.encode("utf-8")
        headers = dict(response.headers)
        headers["content-length"] = str(len(new_body))
        await route.fulfill(status=response.status, headers=headers, body=new_body)

    # ============================================================================
    # HTML MUTATION
    # ============================================================================

    def _mutate_html(self, html: str, url: str) -> str:
        plan = self._get_dom_plan(html, url)
        mutation_started = time.perf_counter()
        soup = BeautifulSoup(html, "html.parser")

        if self.dynamic_config.enable_d1_structure:
            self._apply_structural_mutations(soup, plan.get("d1", []))

        if self.dynamic_config.enable_d3_attributes:
            self._apply_attribute_mutations(soup, plan.get("d3", []))

        if self.dynamic_config.enable_d4_overlays and not self._overlay_instructions:
            overlays = plan.get("d4", [])
            self._overlay_instructions = self._build_overlay_instructions(overlays)

        mutated = str(soup)
        mutation_duration_ms = (time.perf_counter() - mutation_started) * 1000
        if self.dynamic_config.any_enabled():
            delta = len(mutated) - len(html)
            logger.debug(f"[DYNAMIC] Applied plan seed={self.seed} delta={delta} bytes")
        self._maybe_emit_audit_record(url, html, mutated, plan, mutation_duration_ms)
        return mutated

    # ============================================================================
    # STRUCTURAL MUTATION HELPERS
    # ============================================================================

    def _get_target_element(self, soup: BeautifulSoup, selector: str) -> Tag | None:
        """Get target element from soup by selector."""
        try:
            return soup.select_one(selector)
        except Exception:
            return None

    def _apply_insert_before(self, target: Tag, fragment: BeautifulSoup) -> None:
        """Apply insert_before operation."""
        target.insert_before(fragment)

    def _apply_insert_after(self, target: Tag, fragment: BeautifulSoup) -> None:
        """Apply insert_after operation."""
        target.insert_after(fragment)

    def _apply_prepend_child(self, target: Tag, fragment: BeautifulSoup) -> None:
        """Apply prepend_child operation."""
        target.insert(0, fragment)

    def _apply_wrap_with(self, target: Tag, fragment: BeautifulSoup) -> None:
        """Apply wrap_with operation."""
        target.wrap(fragment)

    def _apply_replace_inner_html(self, target: Tag, fragment: BeautifulSoup) -> None:
        """Apply replace_inner_html operation."""
        target.clear()
        target.append(fragment)

    def _apply_shuffle_children(self, target: Tag) -> None:
        """Apply shuffle_children operation."""
        children = [child for child in target.contents if isinstance(child, Tag)]
        self._rng.shuffle(children)
        target.clear()
        for child in children:
            target.append(child)

    def _apply_append_child(self, target: Tag, fragment: BeautifulSoup) -> None:
        """Apply append_child operation (default)."""
        target.append(fragment)

    def _apply_structural_operation(self, target: Tag, fragment: BeautifulSoup, operation: str) -> None:
        """Apply a specific structural operation."""
        operation_map = {
            "insert_before": self._apply_insert_before,
            "insert_after": self._apply_insert_after,
            "prepend_child": self._apply_prepend_child,
            "wrap_with": self._apply_wrap_with,
            "replace_inner_html": self._apply_replace_inner_html,
            "shuffle_children": self._apply_shuffle_children,
        }
        operation_func = operation_map.get(operation, self._apply_append_child)
        if operation == "shuffle_children":
            operation_func(target)
        else:
            operation_func(target, fragment)

    def _apply_structural_mutations(self, soup: BeautifulSoup, instructions: list[dict[str, Any]]) -> None:
        for instr in instructions:
            target_selector = instr.get("target")
            html_fragment = instr.get("html", "")
            operation = instr.get("operation", "append_child")
            if not target_selector or not html_fragment:
                continue

            target = self._get_target_element(soup, target_selector)
            if target is None:
                continue

            fragment = BeautifulSoup(html_fragment, "html.parser")
            self._apply_structural_operation(target, fragment, operation)

    # ============================================================================
    # ATTRIBUTE MUTATION HELPERS
    # ============================================================================

    def _apply_rename_attribute(self, target: Tag, original: str, new_name: str) -> None:
        """Apply rename_attribute operation."""
        if original and new_name and original in target.attrs:
            target.attrs[new_name] = target.attrs.pop(original)

    def _apply_set_attribute(self, target: Tag, attribute: str, value: str) -> None:
        """Apply set_attribute operation."""
        if attribute:
            target.attrs[attribute] = value

    def _apply_replace_text(self, target: Tag, new_text: str) -> None:
        """Apply replace_text operation."""
        if hasattr(target, "string") and target.string:
            target.string.replace_with(new_text)
        else:
            target.append(new_text)

    def _apply_append_class(self, target: Tag, cls: str) -> None:
        """Apply append_class operation."""
        if cls:
            existing = target.get("class", [])
            if cls not in existing:
                existing.append(cls)
                target["class"] = existing

    def _apply_remove_attribute(self, target: Tag, attribute: str) -> None:
        """Apply remove_attribute operation."""
        if attribute and attribute in target.attrs:
            target.attrs.pop(attribute, None)

    def _apply_attribute_operation(self, target: Tag, operation: str, instr: dict[str, Any]) -> None:
        """Apply a specific attribute operation."""
        if operation == "rename_attribute":
            self._apply_rename_attribute(target, instr.get("attribute", ""), instr.get("new_name", ""))
        elif operation == "set_attribute":
            self._apply_set_attribute(target, instr.get("attribute", ""), instr.get("value", ""))
        elif operation == "replace_text":
            self._apply_replace_text(target, instr.get("text", ""))
        elif operation == "append_class":
            self._apply_append_class(target, instr.get("value", ""))
        elif operation == "remove_attribute":
            self._apply_remove_attribute(target, instr.get("attribute", ""))

    def _apply_attribute_mutations(self, soup: BeautifulSoup, instructions: list[dict[str, Any]]) -> None:
        for instr in instructions:
            target_selector = instr.get("target")
            operation = instr.get("operation")
            if not target_selector or not operation:
                continue

            target = self._get_target_element(soup, target_selector)
            if target is None:
                continue

            self._apply_attribute_operation(target, operation, instr)

    # ============================================================================
    # OVERLAY HELPERS
    # ============================================================================

    def _build_overlay_instructions(self, overlays: list[dict[str, Any]]) -> list[OverlayInstruction]:
        instructions: list[OverlayInstruction] = []
        if not overlays:
            overlays = self._fallback_overlay_plan()

        for item in overlays:
            trigger_after = item.get("trigger_after")
            html = item.get("html", "")
            overlay_type = item.get("overlay_type", "modal")
            blocking = item.get("blocking", False)
            dismiss_selector = item.get("dismiss_selector")
            if trigger_after == "random":
                trigger_after = self._rng.randint(self.dynamic_config.d4_min_action, self.dynamic_config.d4_max_action)
            if not isinstance(trigger_after, int) or not html:
                continue
            instructions.append(OverlayInstruction(trigger_after=trigger_after, html=html, overlay_type=overlay_type, blocking=blocking, dismiss_selector=dismiss_selector))
        return instructions

    async def _maybe_trigger_overlays(self, completed_actions: int) -> None:
        if not self.page:
            return
        for overlay in self._overlay_instructions:
            if overlay.has_fired:
                continue
            if completed_actions >= overlay.trigger_after:
                await self._inject_overlay(overlay)
                overlay.has_fired = True

    async def _inject_overlay(self, overlay: OverlayInstruction) -> None:
        if not overlay.html:
            return
        script = """
            ({ html, overlayType, blocking }) => {
                const wrapper = document.createElement('div');
                wrapper.innerHTML = html.trim();
                const element = wrapper.firstElementChild;
                if (!element) { return false; }
                element.dataset.iwaOverlay = overlayType;
                if (blocking) {
                    element.dataset.blocking = 'true';
                    document.body.style.pointerEvents = 'none';
                    element.style.pointerEvents = 'auto';
                }
                document.body.appendChild(element);
                return true;
            }
        """
        try:
            await self.page.evaluate(script, {"html": overlay.html, "overlayType": overlay.overlay_type, "blocking": overlay.blocking})
            if overlay.blocking:
                await self._attach_overlay_dismiss_handler(overlay.dismiss_selector)
            self._metrics["overlays_injected"] += 1
        except Exception as exc:
            logger.debug(f"Overlay injection failed: {exc}")

    async def _attach_overlay_dismiss_handler(self, dismiss_selector: str | None) -> None:
        selector = dismiss_selector or "[data-iwa-dismiss]"
        script = """
            (selector) => {
                const overlay = document.querySelector('[data-iwa-overlay][data-blocking=\"true\"]');
                const button = document.querySelector(selector);
                if (!overlay || !button) { return false; }
                const release = () => {
                    document.body.style.pointerEvents = '';
                    overlay.remove();
                };
                button.addEventListener('click', release, { once: true });
                return true;
            }
        """
        try:
            await self.page.evaluate(script, selector)
        except Exception as exc:
            logger.debug(f"Overlay dismiss hook failed: {exc}")

    # ============================================================================
    # DOM PLAN GENERATION AND CACHING
    # ============================================================================

    def _create_plan_metadata(self, source: str, start: float, cache_key: str) -> dict[str, Any]:
        """Create plan metadata dictionary."""
        return {
            "source": source,
            "duration_ms": (time.perf_counter() - start) * 1000,
            "cache_key": cache_key,
        }

    def _get_cached_plan(self, cache_key: str, start: float) -> dict[str, Any] | None:
        """Get plan from cache if available."""
        plan_entry = self._dom_plan_cache.get(cache_key)
        if plan_entry:
            self._metrics["cache_hits"] += 1
            logger.debug(f"[DYNAMIC] Cache hit for {cache_key}")
            self._last_plan_metadata = self._create_plan_metadata("cache", start, cache_key)
            return plan_entry["plan"]
        return None

    def _get_similar_plan(self, normalized: str, cache_key: str, start: float) -> dict[str, Any] | None:
        """Get similar plan if available."""
        similar_plan = self._find_similar_plan(normalized)
        if similar_plan:
            self._metrics["cache_hits"] += 1
            logger.debug(f"[DYNAMIC] Reused similar plan for {cache_key}")
            self._remember_plan(cache_key, normalized, similar_plan)
            self._last_plan_metadata = self._create_plan_metadata("similar", start, cache_key)
            return similar_plan
        return None

    def _get_palette_plan(self, url: str, cache_key: str, normalized: str, start: float) -> dict[str, Any] | None:
        """Get plan from palette generator if available."""
        if not self._palette_generator:
            return None
        plan = self._palette_generator.build_plan(url)
        self._remember_plan(cache_key, normalized, plan)
        self._last_plan_metadata = self._create_plan_metadata("palette", start, cache_key)
        return plan

    def _get_fallback_plan(self, cache_key: str, normalized: str, start: float) -> dict[str, Any]:
        """Get fallback plan."""
        self._metrics["cache_misses"] += 1
        plan = self._fallback_plan()
        self._remember_plan(cache_key, normalized, plan)
        self._last_plan_metadata = self._create_plan_metadata("fallback", start, cache_key)
        return plan

    def _get_dom_plan(self, html: str, url: str) -> dict[str, Any]:
        start = time.perf_counter()
        normalized = self._normalize_html(html)
        cache_key = f"{self.project_id}:{self.seed}:{url}"

        cached_plan = self._get_cached_plan(cache_key, start)
        if cached_plan:
            return cached_plan

        similar_plan = self._get_similar_plan(normalized, cache_key, start)
        if similar_plan:
            return similar_plan

        palette_plan = self._get_palette_plan(url, cache_key, normalized, start)
        if palette_plan:
            return palette_plan

        return self._get_fallback_plan(cache_key, normalized, start)

    def _remember_plan(self, key: str, normalized_html: str, plan: dict[str, Any]) -> None:
        self._dom_plan_cache[key] = {"plan": plan, "normalized": normalized_html}
        if len(self._dom_plan_cache) > self.dynamic_config.instruction_cache_size:
            self._dom_plan_cache.popitem(last=False)

    def _find_similar_plan(self, normalized_html: str) -> dict[str, Any] | None:
        threshold = self.dynamic_config.html_similarity_threshold
        for entry in self._dom_plan_cache.values():
            ratio = SequenceMatcher(None, normalized_html, entry["normalized"]).ratio()
            if ratio >= threshold:
                return entry["plan"]
        return None

    # ============================================================================
    # FALLBACK PLAN GENERATION
    # ============================================================================

    def _fallback_plan(self) -> dict[str, Any]:
        """
        Deterministic fallback instructions derived from the seed to keep evaluations reproducible.
        """
        rng = self._rng
        d1 = [
            {
                "operation": "wrap_with",
                "target": "body > div:first-of-type",
                "html": f"<section class='iwa-wrapper w-{rng.randint(1, 100)}' data-seed='{self.seed}'></section>",
            },
            {
                "operation": "insert_after",
                "target": "header",
                "html": "<div class='iwa-banner'>Limited-time discount</div>",
            },
        ]
        d3 = [
            {
                "operation": "set_attribute",
                "target": "button",
                "attribute": f"data-iwa-{rng.randint(1, 5)}",
                "value": f"mut-{self.seed}",
            },
            {"operation": "append_class", "target": "nav a", "value": f"iwa-link-{rng.randint(1, 50)}"},
            {"operation": "replace_text", "target": "button", "text": "Process request"},
        ]
        d4 = self._fallback_overlay_plan()
        return {"d1": d1, "d3": d3, "d4": d4}

    def _generate_modal_html(self) -> str:
        """Generate HTML for modal overlay."""
        return (
            "<div class='iwa-overlay iwa-modal' style='position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(15,23,42,0.78);"
            "display:flex;align-items:center;justify-content:center;z-index:2147483647;font-family:sans-serif;'>"
            "<div style='background:#fff;padding:24px;border-radius:12px;max-width:420px;text-align:center;'>"
            "<h3 style='margin-bottom:12px;'>Session expired</h3>"
            "<p style='margin-bottom:18px;'>Reconfirm your identity to continue browsing.</p>"
            "<button data-iwa-dismiss style='padding:10px 18px;border:none;border-radius:8px;background:#2563eb;color:#fff;'>Continue</button>"
            "</div></div>"
        )

    def _generate_cookie_html(self, position: str) -> str:
        """Generate HTML for cookie overlay."""
        return (
            f"<div class='iwa-overlay iwa-overlay--{position}' style='position:fixed;{position}:0;left:0;right:0;background:#101828;color:#fff;"
            "padding:18px;z-index:2147483647;font-family:sans-serif;'>"
            "<strong>Cookie preferences</strong> - You must accept tracking to view inventory."
            "<div style='margin-top:10px;display:flex;gap:12px;flex-wrap:wrap;'>"
            "<button data-iwa-dismiss style='padding:6px 14px;border-radius:6px;border:none;background:#10b981;color:#fff;'>Accept all</button>"
            "<button style='padding:6px 14px;border-radius:6px;border:1px solid rgba(255,255,255,0.6);background:transparent;color:#fff;'>View options</button>"
            "</div></div>"
        )

    def _generate_banner_html(self, position: str) -> str:
        """Generate HTML for banner overlay."""
        return (
            f"<div class='iwa-overlay iwa-overlay--{position}' style='position:fixed;{position}:0;left:0;right:0;background:#101828;color:#fff;"
            "padding:18px;z-index:2147483647;font-family:sans-serif;'>"
            "<strong>Autoppia Dynamic Challenge</strong> - Accept cookies to continue."
            "<button data-iwa-dismiss style='margin-left:12px;padding:6px 14px;border-radius:6px;border:none;background:#6941C6;color:#fff;'>Accept</button>"
            "</div>"
        )

    def _generate_overlay_html(self, overlay_type: str, position: str) -> str:
        """Generate HTML for overlay based on type."""
        if overlay_type == "modal":
            return self._generate_modal_html()
        if overlay_type == "cookie":
            return self._generate_cookie_html(position)
        return self._generate_banner_html(position)

    def _fallback_overlay_plan(self) -> list[dict[str, Any]]:
        position = self._rng.choice(["top", "bottom", "center"])
        overlay_type = self._rng.choice(["banner", "modal", "cookie"])
        blocking = overlay_type in {"cookie", "modal"}
        html = self._generate_overlay_html(overlay_type, position)
        return [
            {
                "trigger_after": self._rng.randint(self.dynamic_config.d4_min_action, self.dynamic_config.d4_max_action),
                "html": html,
                "overlay_type": overlay_type,
                "blocking": blocking,
                "dismiss_selector": "[data-iwa-dismiss]",
            }
        ]

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    @staticmethod
    def _normalize_html(html: str) -> str:
        return " ".join(html.split())

    def get_metrics(self) -> dict[str, int]:
        return dict(self._metrics)

    def _maybe_emit_audit_record(self, url: str, html_before: str, html_after: str, plan: dict[str, Any], mutation_duration_ms: float) -> None:
        if not self._audit_callback:
            return
        metadata = self._last_plan_metadata or {}
        record = MutationAuditRecord(
            project_id=self.project_id,
            url=url,
            seed=self.seed,
            html_before=html_before,
            html_after=html_after,
            plan=plan,
            plan_source=metadata.get("source", "unknown"),
            plan_duration_ms=metadata.get("duration_ms", 0.0),
            mutation_duration_ms=mutation_duration_ms,
            cache_key=metadata.get("cache_key"),
            delta_bytes=len(html_after) - len(html_before),
            phases={
                "d1": self.dynamic_config.enable_d1_structure,
                "d3": self.dynamic_config.enable_d3_attributes,
                "d4": self.dynamic_config.enable_d4_overlays,
            },
            metrics=self.get_metrics(),
        )
        try:
            self._audit_callback(record)
        except Exception as exc:  # pragma: no cover - diagnostics only
            logger.debug(f"Audit callback failed: {exc}")
