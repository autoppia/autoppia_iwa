from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat


@dataclass
class ScreenshotMetrics:
    path: Path
    width: int
    height: int
    size_kb: float
    brightness: float
    contrast: float
    coverage: float

    @property
    def resolution_str(self) -> str:
        return f"{self.width}x{self.height}"


def _compute_metrics(path: Path) -> ScreenshotMetrics:
    with Image.open(path) as img:
        width, height = img.size
        gray = img.convert("L")
        stat = ImageStat.Stat(gray)
        brightness = stat.mean[0]
        contrast = stat.stddev[0]
        non_white = sum(1 for pixel in gray.getdata() if pixel < 250)
        coverage = non_white / (width * height)
    size_kb = path.stat().st_size / 1024
    return ScreenshotMetrics(path=path, width=width, height=height, size_kb=size_kb, brightness=brightness, contrast=contrast, coverage=coverage)


async def _llm_summary_async(llm_service, metadata: dict[str, Any]) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You review screenshot metadata (resolution, brightness, coverage) to rate whether the UI likely looks "
                "rich enough for browser-agent benchmarks. Respond with one short sentence, prefixed by ✅ if quality looks"
                " acceptable or ⚠️ otherwise. Mention the route hint if provided."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Filename: {metadata['filename']}\n"
                f"Route hint: {metadata['route_hint']}\n"
                f"Resolution: {metadata['resolution']}\n"
                f"File size (KB): {metadata['size_kb']:.1f}\n"
                f"Average brightness (0-255): {metadata['brightness']:.1f}\n"
                f"Contrast (std dev): {metadata['contrast']:.1f}\n"
                f"Coverage (non-white %): {metadata['coverage']*100:.1f}%\n"
                "Summarize quality."
            ),
        },
    ]
    raw = await llm_service.async_predict(messages=messages, json_format=False, return_raw=False)
    if isinstance(raw, str):
        return raw.strip().split("\n")[0][:200]
    if isinstance(raw, dict):
        content = raw.get("content") or raw.get("text") or ""
        if isinstance(content, list):
            content = " ".join(str(part) for part in content)
        if isinstance(content, str):
            return content.strip().split("\n")[0][:200]
    return str(raw).split("\n")[0][:200]


def summarize_screenshots(
    screenshot_dir: Path,
    project_id: str,
    llm_service: Any | None,
) -> list[dict[str, str | float]]:
    if not screenshot_dir.exists():
        return []
    reviews: list[dict[str, str | float]] = []
    files = sorted(p for p in screenshot_dir.glob("*.png"))
    for path in files:
        metrics = _compute_metrics(path)
        route_hint = path.stem.split("_", 1)[1] if "_" in path.stem else path.stem
        summary = ""
        if llm_service:
            metadata = {
                "filename": path.name,
                "route_hint": route_hint,
                "resolution": metrics.resolution_str,
                "size_kb": metrics.size_kb,
                "brightness": metrics.brightness,
                "contrast": metrics.contrast,
                "coverage": metrics.coverage,
            }
            try:
                summary = asyncio.run(_llm_summary_async(llm_service, metadata))
            except Exception as exc:
                summary = f"⚠️ LLM summary unavailable ({exc})"
        if not summary:
            verdict = "✅" if metrics.width >= 1280 and metrics.height >= 720 and metrics.coverage > 0.15 else "⚠️"
            summary = (
                f"{verdict} {metrics.resolution_str} screenshot (~{metrics.size_kb:.0f}KB) with coverage "
                f"{metrics.coverage*100:.0f}%; heuristic quality assessment."
            )
        reviews.append(
            {
                "filename": path.name,
                "resolution": metrics.resolution_str,
                "size_kb": round(metrics.size_kb, 1),
                "summary": summary,
            }
        )
    return reviews
