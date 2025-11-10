from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlsplit, urlunsplit

import aiohttp
from loguru import logger
from playwright.async_api import Browser, Page, async_playwright
from tqdm import tqdm

# Ensure repository root on sys.path for direct script execution
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from modules.dynamic_proxy.core.palettes import project_slug_map
from autoppia_iwa.src.execution.dynamic.audit_runner import build_llm_from_args
from autoppia_iwa.src.execution.dynamic.executor import DynamicPhaseConfig, DynamicPlaywrightExecutor
from autoppia_iwa.src.execution.dynamic.palette import MutationPalette, MutationTemplate
from autoppia_iwa.src.execution.dynamic.palette_builder import PageSnapshot, build_palette


def _select_projects(ids: Iterable[str] | None):
    if not ids:
        return list(demo_web_projects)
    wanted = {pid.lower() for pid in ids}
    return [project for project in demo_web_projects if project.id.lower() in wanted]


def _normalize_url(base_url: str, href: str) -> str:
    if href.startswith(("http://", "https://")):
        return href
    return urljoin(base_url, href)


def _with_seed_param(url: str, seed: int) -> str:
    if "seed=" in url:
        return url
    delimiter = "&" if "?" in url else "?"
    return f"{url}{delimiter}seed={seed}"


async def _discover_routes(page: Page, start_url: str, max_pages: int, seed: int) -> list[str]:
    origin = urlsplit(start_url)
    origin_netloc = origin.netloc
    queue = [_with_seed_param(start_url, seed)]
    seen: set[str] = set()
    discovered: list[str] = []

    while queue and len(discovered) < max_pages:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
        except Exception:
            continue
        discovered.append(url)
        anchors = await page.eval_on_selector_all("a[href]", "els => els.map(a => a.href)")
        for href in anchors:
            normalized = _with_seed_param(_normalize_url(start_url, href), seed)
            parsed = urlsplit(normalized)
            if parsed.netloc and parsed.netloc != origin_netloc:
                continue
            normalized = urlunsplit((origin.scheme, origin.netloc, parsed.path, parsed.query, parsed.fragment))
            if normalized in seen or normalized in queue:
                continue
            if len(discovered) + len(queue) >= max_pages:
                continue
            queue.append(normalized)
    return discovered


async def _collect_snapshots(playwright, browser_name: str, headless: bool, urls: list[str]) -> list[PageSnapshot]:
    snapshots: list[PageSnapshot] = []
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for url in urls:
            try:
                async with session.get(url) as resp:
                    resp.raise_for_status()
                    html = await resp.text()
                    snapshots.append(PageSnapshot(url=url, html=html))
            except Exception as exc:
                logger.warning(f"Failed to capture {url}: {exc}")
    return snapshots


async def _verify_palette(project_id: str, palette_dir: Path, snapshots: list[PageSnapshot], seeds: list[int], sample_pages: int, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    config = DynamicPhaseConfig(
        enable_d1_structure=True,
        enable_d3_attributes=True,
        palette_dir=str(palette_dir),
        palette_max_per_phase=3,
    )
    sample_snapshots = snapshots[:sample_pages]
    for seed in seeds:
        executor = DynamicPlaywrightExecutor(
            browser_config=BrowserSpecification(),
            page=None,
            backend_demo_webs_service=None,
            dynamic_config=config,
            project_id=project_id,
            seed=seed,
        )
        for idx, snapshot in enumerate(sample_snapshots):
            mutated = await executor._mutate_html(snapshot.html, snapshot.url)
            before_path = output_dir / f"seed_{seed}_sample_{idx}_before.html"
            after_path = output_dir / f"seed_{seed}_sample_{idx}_after.html"
            before_path.write_text(snapshot.html, encoding="utf-8")
            after_path.write_text(mutated, encoding="utf-8")


async def _augment_palette_with_llm(llm_service, project_id: str, snapshots: list[PageSnapshot], palette: MutationPalette, max_new: int = 15) -> MutationPalette:
    if not llm_service or not snapshots:
        return palette
    snippet = snapshots[0].html[: 4000]
    messages = [
        {
            "role": "system",
            "content": (
                "You are improving DOM mutation templates for stress-testing web automation agents. "
                "Return STRICT JSON with arrays d1, d3, d4 containing objects that describe selectors, operations, attributes, and HTML fragments."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "project_id": project_id,
                    "html": snippet,
                },
                ensure_ascii=False,
            ),
        },
    ]
    schema = {
        "type": "object",
        "properties": {
            "d1": {"type": "array", "items": {"type": "object"}},
            "d3": {"type": "array", "items": {"type": "object"}},
            "d4": {"type": "array", "items": {"type": "object"}},
        },
        "required": ["d1", "d3", "d4"],
    }
    try:
        response = await llm_service.async_predict(messages, json_format=True, schema=schema)
    except Exception as exc:  # pragma: no cover - best effort augmentation
        logger.warning(f"LLM augmentation failed for {project_id}: {exc}")
        return palette
    try:
        plan = json.loads(response)
    except json.JSONDecodeError:
        logger.warning("LLM augmentation returned invalid JSON")
        return palette

    new_templates: list[MutationTemplate] = []
    counter = 0
    for phase in ("d1", "d3", "d4"):
        for instruction in plan.get(phase, []):
            if counter >= max_new:
                break
            template = MutationTemplate(
                id=f"llm-{phase}-{counter}",
                phase=phase,
                selector=instruction.get("target", "body"),
                operation=instruction.get("operation", "append_child"),
                html=instruction.get("html"),
                attribute=instruction.get("attribute"),
                value=instruction.get("value"),
                text=instruction.get("text"),
                new_name=instruction.get("new_name"),
                overlay_type=instruction.get("overlay_type"),
                blocking=instruction.get("blocking", False),
                dismiss_selector=instruction.get("dismiss_selector"),
                trigger_after=instruction.get("trigger_after"),
            )
            new_templates.append(template)
            counter += 1
        if counter >= max_new:
            break

    if not new_templates:
        return palette

    return MutationPalette(
        project_id=palette.project_id,
        generated_by=palette.generated_by,
        templates=palette.templates + new_templates,
    )


def _write_python_module(palette: MutationPalette, slug: str, module_root: Path) -> Path:
    module_root = module_root.expanduser().resolve()
    target_dir = module_root / slug
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / "mutations.py"
    payload = palette.model_dump(mode="json")
    serialized = json.dumps(payload, indent=2, ensure_ascii=False)
    module_body = (
        "from autoppia_iwa.src.execution.dynamic.palette import MutationPalette\n"
        "import json\n\n"
        "PALETTE_DATA = json.loads(r\"\"\"\n"
        + serialized
        + "\n\"\"\")\n\n"
        "palette = MutationPalette.model_validate(PALETTE_DATA)\n"
    )
    target_path.write_text(module_body, encoding="utf-8")
    return target_path


async def run(args: argparse.Namespace, llm_service) -> None:
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    projects = _select_projects(args.project)
    slug_lookup = project_slug_map()
    async with async_playwright() as playwright:
        for project in tqdm(projects, desc="Building palettes", unit="project"):
            base_url = project.frontend_url
            if not base_url:
                logger.warning(f"Skipping {project.id}: missing frontend URL")
                continue
            start_url = base_url.rstrip("/")
            browser_launcher = getattr(playwright, args.browser)
            discovery_browser: Browser = await browser_launcher.launch(headless=args.headless)
            discovery_page: Page = await discovery_browser.new_page(viewport={"width": 1280, "height": 900})
            urls = await _discover_routes(discovery_page, start_url, args.max_pages, args.discovery_seed)
            await discovery_browser.close()
            if not urls:
                logger.warning(f"No URLs discovered for {project.id}")
                continue
            snapshots = await _collect_snapshots(playwright, args.browser, args.headless, urls)
            palette = build_palette(project.id, snapshots, generated_by="generate_mutations", max_templates_per_phase=args.max_templates_per_phase)
            palette = await _augment_palette_with_llm(llm_service, project.id, snapshots, palette, max_new=args.llm_max_new)
            palette_path = output_dir / f"{project.id}.json"
            palette.save(palette_path)
            logger.info(f"Saved palette for {project.id} with {len(palette.templates)} templates -> {palette_path}")
            if args.emit_python:
                slug = slug_lookup.get(project.id)
                if not slug:
                    logger.warning(f"Unable to determine module directory for {project.id}")
                else:
                    module_path = _write_python_module(palette, slug, args.module_root)
                    logger.info(f"Wrote mutations module -> {module_path}")
            verify_dir = output_dir / project.id / "verification"
            await _verify_palette(project.id, output_dir, snapshots, args.verify_seeds, args.verify_pages, verify_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build deterministic dynamic mutation palettes per project.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/dynamic_palettes"), help="Directory to store palette JSON files.")
    parser.add_argument("--project", action="append", help="Project id to process. Repeat for multiple projects.")
    parser.add_argument("--browser", default="chromium", choices=["chromium", "firefox", "webkit"], help="Playwright browser name.")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode.")
    parser.add_argument("--max-pages", type=int, default=5, help="Pages to crawl per project.")
    parser.add_argument("--discovery-seed", type=int, default=13, help="Seed parameter to append while crawling URLs.")
    parser.add_argument("--max-templates-per-phase", type=int, default=60, help="Upper bound of templates per phase in palette.")
    parser.add_argument("--verify-seeds", type=int, nargs="*", default=[0, 1], help="Seeds to use when verifying palettes.")
    parser.add_argument("--verify-pages", type=int, default=2, help="Number of captured pages to save before/after HTML for.")
    parser.add_argument("--emit-python", action="store_true", help="Emit mutations.py modules alongside JSON palettes.")
    parser.add_argument("--module-root", type=Path, default=Path("autoppia_iwa/src/demo_webs/projects"), help="Root directory for project modules.")
    parser.add_argument("--llm-type", choices=["openai", "local", "chutes"], help="Optional LLM provider to augment templates.")
    parser.add_argument("--llm-api-key", help="API key for OpenAI/Chutes providers.")
    parser.add_argument("--llm-endpoint", help="Endpoint URL for local provider.")
    parser.add_argument("--llm-base-url", help="Base URL for Chutes provider.")
    parser.add_argument("--llm-use-bearer", action="store_true", help="Use Authorization: Bearer header for Chutes.")
    parser.add_argument("--llm-model", default="gpt-3.5-turbo", help="LLM model identifier.")
    parser.add_argument("--llm-temperature", type=float, default=0.2, help="LLM sampling temperature.")
    parser.add_argument("--llm-max-tokens", type=int, default=1024, help="LLM max tokens.")
    parser.add_argument("--llm-max-new", type=int, default=15, help="Maximum number of LLM-derived templates to add per project.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    llm_service = build_llm_from_args(
        args.llm_type,
        api_key=args.llm_api_key,
        endpoint=args.llm_endpoint,
        base_url=args.llm_base_url,
        use_bearer=args.llm_use_bearer,
        model=args.llm_model,
        temperature=args.llm_temperature,
        max_tokens=args.llm_max_tokens,
    )
    asyncio.run(run(args, llm_service))


if __name__ == "__main__":
    main()
