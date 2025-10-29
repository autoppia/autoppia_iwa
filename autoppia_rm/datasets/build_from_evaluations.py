"""Build cached features, LLM labels, and preference pairs from evaluation logs."""

from __future__ import annotations

import glob
import json
import random
from pathlib import Path
from typing import Iterable, Iterator

from loguru import logger

from autoppia_rm.features.snapshot_encoder import clean_dom, snap_to_obs_public
from autoppia_rm.llm.labeler import label_snapshot
from autoppia_rm.models.schemas import BrowserSnapshot, EvaluationEpisode, EvaluationStep, ObsPublic
from autoppia_rm.utils import config_path as get_config_path

try:
    import yaml
except Exception:  # pragma: no cover - optional dependency
    yaml = None


RAW_DIR = Path("data/rm/raw_evaluations")
FEATURE_DIR = Path("data/rm/features")
PAIRS_DIR = Path("data/rm/pairs")

FEATURE_DIR.mkdir(parents=True, exist_ok=True)
PAIRS_DIR.mkdir(parents=True, exist_ok=True)


def _iter_episode_files(include_patterns: Iterable[str] | None = None) -> Iterable[Path]:
    """Yield evaluation files matching the provided patterns.

    Patterns are resolved against the raw evaluations directory unless they
    already point to concrete files. Legacy dumps that end with `_old.jsonl`
    are skipped by default.
    """

    paths: set[Path] = set()

    def _add_path(path_str: str) -> None:
        matches = glob.glob(path_str)
        if not matches:
            matches = glob.glob(str(RAW_DIR / path_str))

        if not matches:
            candidate = Path(path_str)
            if candidate.exists():
                matches = [str(candidate)]
            else:
                raw_candidate = RAW_DIR / path_str
                if raw_candidate.exists():
                    matches = [str(raw_candidate)]

        for match in matches:
            match_path = Path(match)
            if match_path.is_dir():
                paths.update(match_path.glob("*.jsonl"))
            elif match_path.suffix == ".jsonl" and match_path.is_file():
                paths.add(match_path)

    if include_patterns:
        for pattern in include_patterns:
            _add_path(pattern)
    else:
        paths.update(RAW_DIR.glob("*.jsonl"))

    for path in sorted(paths):
        if not path.is_file():
            continue
        if not include_patterns and path.name.endswith("_old.jsonl"):
            logger.debug(f"Skipping legacy evaluation dump {path}")
            continue
        yield path


def iter_episodes(include_patterns: Iterable[str] | None = None) -> Iterator[EvaluationEpisode]:
    for path in _iter_episode_files(include_patterns):
        with path.open() as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield EvaluationEpisode.model_validate_json(line)
                except Exception as exc:
                    logger.warning(f"Failed to parse evaluation line in {path}: {exc}")


def _make_row_id(episode: EvaluationEpisode, step: EvaluationStep) -> str:
    return f"{episode.episode_id}_{step.index}"


def _load_llm_config(config_path: str | Path) -> dict:
    cfg_path = Path(config_path)
    if cfg_path.exists() and yaml is not None:
        try:
            return yaml.safe_load(cfg_path.read_text()) or {}
        except Exception as exc:  # pragma: no cover
            logger.warning(f"Failed to parse {config_path}: {exc}")
    return {}


def build_obs_and_labels(
    config_path: str | Path | None = None,
    include_patterns: Iterable[str] | None = None,
) -> None:
    """Generate ObsPublic and semantic label JSON files for each evaluation step."""

    cfg_path = config_path or get_config_path("llm_labeler.yaml")
    cfg = _load_llm_config(cfg_path)
    llm_model = cfg.get("model", "unused")
    llm_provider = cfg.get("provider")
    sleep_ms = int(cfg.get("sleep_ms", 100))
    max_dom_chars = int(cfg.get("max_dom_chars", 3000))

    FEATURE_DIR.mkdir(parents=True, exist_ok=True)
    for episode in iter_episodes(include_patterns):
        prev_url = None
        stagnation = 0
        for step in episode.steps:
            snap = step.action_result.browser_snapshot
            if prev_url == snap.current_url:
                stagnation += 1
            else:
                stagnation = 0
            obs_pub: ObsPublic = snap_to_obs_public(snap, prev_url, stagnation)
            dom_clean = clean_dom(snap.current_html, max_chars=max_dom_chars)
            label = label_snapshot(
                snap.current_url,
                dom_clean,
                model=llm_model,
                sleep_ms=sleep_ms,
                provider=llm_provider,
            )

            row_id = _make_row_id(episode, step)
            (FEATURE_DIR / f"{row_id}.obs.json").write_text(obs_pub.model_dump_json())
            (FEATURE_DIR / f"{row_id}.sem.json").write_text(json.dumps(label, ensure_ascii=False))

            prev_url = snap.current_url


def build_preference_pairs(
    num_recent_steps: int = 3,
    max_pairs: int = 50_000,
    include_patterns: Iterable[str] | None = None,
) -> None:
    """Create preference pairs from successful vs. unsuccessful episode steps."""

    positives: list[str] = []
    negatives: list[str] = []

    for episode in iter_episodes(include_patterns):
        steps = episode.steps
        if not steps:
            continue
        slice_steps = steps[-num_recent_steps:]
        ids = [_make_row_id(episode, step) for step in slice_steps]
        if episode.final_score > 0.5:
            positives.extend(ids)
        else:
            negatives.extend(ids)

    if not positives or not negatives:
        logger.warning("Not enough positives/negatives to form preference pairs")
        return

    random.shuffle(positives)
    pairs_path = PAIRS_DIR / "pairs.jsonl"
    with pairs_path.open("w") as handle:
        count = 0
        while positives and negatives and count < max_pairs:
            pos_id = positives[count % len(positives)]
            neg_id = random.choice(negatives)
            handle.write(json.dumps({"pos_id": pos_id, "neg_id": neg_id}) + "\n")
            count += 1
    logger.info(f"Wrote preference pairs to {pairs_path}")
