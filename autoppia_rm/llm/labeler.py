"""Utilities to bootstrap semantic labels using the configured LLM provider."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Dict, Iterable

from loguru import logger

from autoppia_iwa.config.config import (
    CHUTES_API_KEY,
    CHUTES_BASE_URL,
    CHUTES_MODEL,
    CHUTES_MAX_TOKENS,
    CHUTES_TEMPERATURE,
    CHUTES_USE_BEARER,
    LLM_PROVIDER,
    LOCAL_MODEL_ENDPOINT,
    OPENAI_API_KEY,
    OPENAI_MAX_TOKENS,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
)
from autoppia_iwa.src.llms.domain.interfaces import LLMConfig
from autoppia_iwa.src.llms.infrastructure.llm_service import LLMFactory

from .label_schema import SCHEMA_JSON, SYSTEM_PROMPT, USER_TEMPLATE

CACHE_DIR = Path("data/rm/llm_labels")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

_LLM_CLIENT = None


def _hash_payload(url: str, dom: str) -> str:
    h = hashlib.sha256()
    h.update(url.encode("utf-8"))
    h.update(dom.encode("utf-8"))
    return h.hexdigest()


def _build_llm_client(provider_override: str | None = None):
    global _LLM_CLIENT
    if _LLM_CLIENT is not None:
        return _LLM_CLIENT

    provider = provider_override or LLM_PROVIDER

    if provider == "openai":
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY not configured")
        cfg = LLMConfig(model=OPENAI_MODEL, max_tokens=OPENAI_MAX_TOKENS, temperature=OPENAI_TEMPERATURE)
        _LLM_CLIENT = LLMFactory.create_llm("openai", cfg, api_key=OPENAI_API_KEY)
    elif provider == "local":
        endpoint = LOCAL_MODEL_ENDPOINT or "http://127.0.0.1:6000/generate"
        cfg = LLMConfig(model="local", max_tokens=OPENAI_MAX_TOKENS, temperature=OPENAI_TEMPERATURE)
        _LLM_CLIENT = LLMFactory.create_llm("local", cfg, endpoint_url=endpoint)
    elif provider == "chutes":
        if not CHUTES_API_KEY or not CHUTES_BASE_URL:
            raise RuntimeError("Chutes configuration missing; set CHUTES_API_KEY and CHUTES_BASE_URL")
        cfg = LLMConfig(model=CHUTES_MODEL, max_tokens=CHUTES_MAX_TOKENS, temperature=CHUTES_TEMPERATURE)
        _LLM_CLIENT = LLMFactory.create_llm(
            "chutes",
            cfg,
            base_url=CHUTES_BASE_URL,
            api_key=CHUTES_API_KEY,
            use_bearer=CHUTES_USE_BEARER,
        )
    else:
        raise RuntimeError(f"Unsupported LLM provider '{provider}' for semantic labeling")

    return _LLM_CLIENT


def _ensure_defaults(payload: Dict[str, object]) -> Dict[str, object]:
    affordances = payload.setdefault("affordances", {})
    for key in ("can_go_back", "can_search", "can_filter", "can_add_to_cart", "can_submit_form"):
        affordances.setdefault(key, False)

    payload.setdefault("nav_depth", 0)
    payload.setdefault("item_count", 0)
    payload.setdefault("price_present", False)
    payload.setdefault("pagination_state", "none")
    payload.setdefault("salient_entities", [])
    payload.setdefault("is_on_wrong_product", False)
    payload.setdefault("confidence", 0.5)

    goal_progress = float(payload.get("goal_progress", 0.0))
    payload["goal_progress"] = max(0.0, min(1.0, goal_progress))

    if payload.get("pagination_state") not in {"none", "has_next", "has_prev", "both"}:
        payload["pagination_state"] = "none"

    return payload


def _call_llm(url: str, dom_clean: str, provider_override: str | None = None) -> Dict[str, object]:
    client = _build_llm_client(provider_override)
    schema_text = json.dumps(SCHEMA_JSON, ensure_ascii=False)
    system_prompt = (
        f"{SYSTEM_PROMPT}\nRespond with JSON that exactly matches this schema: {schema_text}. "
        "Return only the JSON string."
    )
    user_prompt = USER_TEMPLATE.format(url=url, dom=dom_clean)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = client.predict(messages, json_format=False)
    if not response:
        raise RuntimeError("LLM returned empty response")

    trimmed = response.strip()
    if trimmed.startswith("```"):
        trimmed = trimmed.split("\n", 1)[-1]
    if trimmed.endswith("```"):
        trimmed = trimmed.rsplit("\n", 1)[0]

    try:
        data = json.loads(trimmed)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"LLM response is not valid JSON: {trimmed}") from exc

    return _ensure_defaults(data)


def label_snapshot(url: str, dom_clean: str, *, model: str = "unused", sleep_ms: int = 100, provider: str | None = None) -> Dict[str, object]:
    """Request structured semantic labels for a snapshot, using cache when available."""

    cache_key = _hash_payload(url, dom_clean)
    cache_path = CACHE_DIR / f"{cache_key}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text())

    logger.debug(
        "Requesting semantic label from provider=%s cache_key=%s",
        provider or LLM_PROVIDER,
        cache_key[:8],
    )
    data = _call_llm(url, dom_clean, provider_override=provider)
    cache_path.write_text(json.dumps(data, ensure_ascii=False))
    time.sleep(max(sleep_ms, 0) / 1000.0)
    return data


def batch_label(samples: Iterable[dict], *, model: str = "unused", sleep_ms: int = 100, provider: str | None = None) -> None:
    """Iterate through samples dicts (with url/dom keys) and ensure cached labels exist."""

    for sample in samples:
        url = sample.get("url", "")
        dom = sample.get("dom", "")
        if not url or not dom:
            logger.warning("Skipping sample with missing url/dom")
            continue
        try:
            label_snapshot(url, dom, sleep_ms=sleep_ms, provider=provider)
        except Exception as exc:
            logger.error(f"Failed to label snapshot ({url}): {exc}")
