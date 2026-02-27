from __future__ import annotations

import asyncio
import inspect
import json
from collections.abc import Awaitable, Callable, Iterable
from pathlib import Path

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from pydantic import AnyHttpUrl, BaseModel, Field
from starlette.datastructures import QueryParams

from modules.dynamic_proxy.core.config import DynamicPhaseConfig
from modules.dynamic_proxy.core.engine import MutationEngine, MutationResult

RUNTIME_DIR = Path(__file__).resolve().parents[1] / "runtime"


class ProxyProjectConfig(BaseModel):
    project_id: str
    origin: AnyHttpUrl
    listen_host: str = "127.0.0.1"
    listen_port: int = Field(..., gt=0)
    palette_dir: str | None = None
    enable_d1: bool = True
    enable_d3: bool = True
    enable_d4: bool = True
    cache_size: int = Field(default=32, gt=0)
    html_similarity_threshold: float = Field(default=0.95, gt=0, le=1)
    request_timeout: float = Field(default=30.0, gt=0)
    audit_root: str | None = Field(default="data/dynamic_proxy_audit")
    inject_client_runtime: bool = False
    seed_modulus: int = 32
    runtime_seed_modulus: int = 10000


class ProxyAuditWriter:
    def __init__(self, root: Path, project_id: str) -> None:
        self.root = root.expanduser().resolve()
        self.project_id = project_id
        self.project_dir = self.root / project_id
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self._counter = 0
        self._lock = asyncio.Lock()

    async def write(self, record) -> None:
        async with self._lock:
            self._counter += 1
            base = self.project_dir / f"{self._counter:06d}_seed_{record.seed}"
            base.parent.mkdir(parents=True, exist_ok=True)

            before_path = base.with_suffix(".before.html")
            after_path = base.with_suffix(".after.html")
            plan_path = base.with_suffix(".plan.json")
            summary_path = self.project_dir / "summary.jsonl"

            before_path.write_text(record.html_before, encoding="utf-8")
            after_path.write_text(record.html_after, encoding="utf-8")
            plan_path.write_text(json.dumps(record.plan, ensure_ascii=False, indent=2), encoding="utf-8")

            summary = {
                "record_id": base.name,
                "project_id": self.project_id,
                "seed": record.seed,
                "url": record.url,
                "plan_source": record.plan_source,
                "plan_duration_ms": record.plan_duration_ms,
                "mutation_duration_ms": record.mutation_duration_ms,
                "cache_key": record.cache_key,
                "delta_bytes": record.delta_bytes,
                "metrics": record.metrics,
                "phases": record.phases,
                "before_path": str(before_path.relative_to(self.root)),
                "after_path": str(after_path.relative_to(self.root)),
                "plan_path": str(plan_path.relative_to(self.root)),
            }
            with summary_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(summary, ensure_ascii=False) + "\n")


HttpClientFactory = Callable[[], Awaitable[httpx.AsyncClient] | httpx.AsyncClient]


def create_project_proxy_app(
    config: ProxyProjectConfig,
    *,
    http_client_factory: HttpClientFactory | None = None,
) -> FastAPI:
    """
    Build a FastAPI application that proxies a single demo web project and applies D1/D3/D4 mutations
    before responses reach the client.
    """

    phase_config = DynamicPhaseConfig(
        enable_d1_structure=config.enable_d1,
        enable_d3_attributes=config.enable_d3,
        enable_d4_overlays=config.enable_d4,
        instruction_cache_size=config.cache_size,
        html_similarity_threshold=config.html_similarity_threshold,
        palette_dir=config.palette_dir,
        seed_modulus=config.seed_modulus,
    )
    runtime_levels = {"D1": bool(config.enable_d1), "D3": bool(config.enable_d3), "D4": bool(config.enable_d4)}
    if config.inject_client_runtime:
        phase_config.enable_d1_structure = False
        phase_config.enable_d3_attributes = False
        phase_config.enable_d4_overlays = False
        phase_config.apply_dom_mutations = False
        phase_config.force_generate_plan = True
    else:
        phase_config.apply_dom_mutations = True
        phase_config.force_generate_plan = False
    engine = MutationEngine(config.project_id, phase_config)

    app = FastAPI(
        title=f"{config.project_id} mutation proxy",
        docs_url=None,
        redoc_url=None,
    )
    if RUNTIME_DIR.exists():
        app.mount("/dynamic", StaticFiles(directory=str(RUNTIME_DIR), html=False), name="dynamic-assets")

    @app.on_event("startup")
    async def _startup() -> None:
        client = None
        if http_client_factory:
            client = http_client_factory()
            if inspect.isawaitable(client):
                client = await client  # type: ignore[assignment]
        if client is None:
            client = httpx.AsyncClient(base_url=str(config.origin), timeout=config.request_timeout, follow_redirects=True)
        app.state.http_client = client
        app.state.audit_writer = ProxyAuditWriter(Path(config.audit_root), config.project_id) if config.audit_root else None

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        client: httpx.AsyncClient | None = getattr(app.state, "http_client", None)
        if client is not None:
            await client.aclose()

    hop_by_hop = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"}

    def _filter_headers(items: Iterable[tuple[str, str]]) -> dict[str, str]:
        return {k: v for k, v in items if k.lower() not in hop_by_hop}

    def _extract_seed(params: QueryParams) -> int:
        seed_value = params.get("seed", "0")
        try:
            return int(seed_value)
        except (TypeError, ValueError):
            return 0

    def _should_skip_mutation(params: QueryParams) -> bool:
        if "seed" not in params:
            return True
        flag = params.get("iwa_dynamic")
        return bool(flag and flag.strip() in {"0", "false", "False"})

    def _normalize_seed_value(seed: int) -> int:
        modulus = config.runtime_seed_modulus or 0
        return seed % modulus if modulus > 0 else seed

    def _inject_universal_runtime(content: bytes, seed: int, site_key: str | None) -> bytes:
        payload = {
            "seed": seed,
            "levels": {
                "D1": bool(runtime_levels.get("D1")),
                "D3": bool(runtime_levels.get("D3")),
                "D4": bool(runtime_levels.get("D4")),
            },
            "siteKey": site_key or config.project_id,
        }
        snippet = f'<script>window.__DYN_CONFIG__ = {json.dumps(payload, ensure_ascii=False)};</script>\n<script src="/dynamic/runtime.js"></script>'
        try:
            html = content.decode("utf-8", errors="ignore")
        except Exception:
            return content
        lower = html.lower()
        head_idx = lower.find("</head>")
        if head_idx != -1:
            return (html[:head_idx] + snippet + html[head_idx:]).encode("utf-8")
        body_idx = lower.find("<body")
        if body_idx != -1:
            return (html[:body_idx] + snippet + html[body_idx:]).encode("utf-8")
        return (snippet + html).encode("utf-8")

    def _mutate_if_needed(content: bytes, full_url: str, charset_hint: str, is_head: bool, seed: int) -> tuple[bytes, MutationResult | None]:
        if is_head:
            return content, None
        try:
            charset = "utf-8"
            if "charset=" in charset_hint:
                charset = charset_hint.split("charset=")[-1].split(";")[0].strip() or "utf-8"
            html = content.decode(charset, errors="ignore")
        except Exception:
            html = content.decode("utf-8", errors="ignore")
        result = engine.mutate_html(html, full_url, seed)
        mutated_html = result.html
        return mutated_html.encode("utf-8"), result

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
    async def proxy(path: str, request: Request) -> Response:
        client: httpx.AsyncClient = app.state.http_client
        upstream_headers = _filter_headers(request.headers.items())
        # Avoid upstream compression so we do not have to re-encode mutated payloads.
        upstream_headers["accept-encoding"] = "identity"
        body = await request.body()
        params = list(request.query_params.multi_items())
        upstream_response = await client.request(
            request.method,
            f"/{path}".replace("//", "/"),
            params=params,
            headers=upstream_headers,
            content=body or None,
        )

        content = upstream_response.content
        result: MutationResult | None = None
        content_type = upstream_response.headers.get("content-type", "")
        runtime_seed: int | None = None
        if config.inject_client_runtime and not _should_skip_mutation(request.query_params):
            runtime_seed = _normalize_seed_value(_extract_seed(request.query_params))
        mutate = not _should_skip_mutation(request.query_params) and "text/html" in content_type and phase_config.any_enabled() and upstream_response.status_code not in (204, 304)
        if mutate:
            seed = _extract_seed(request.query_params)
            full_url = str(upstream_response.request.url)
            content, result = _mutate_if_needed(content, full_url, content_type, request.method.upper() == "HEAD", seed)
            if result and result.audit_record and app.state.audit_writer:
                await app.state.audit_writer.write(result.audit_record)

        response_headers = _filter_headers(upstream_response.headers.items())
        runtime_injected = False
        if runtime_seed is not None and "text/html" in content_type and upstream_response.status_code not in (204, 304):
            site_key = request.url.hostname or config.project_id
            content = _inject_universal_runtime(content, runtime_seed, site_key)
            runtime_injected = True
        if mutate:
            response_headers.pop("content-encoding", None)
            response_headers["x-iwa-mutated"] = "1"
        elif runtime_injected:
            response_headers.pop("content-encoding", None)
        response_headers["content-length"] = str(len(content))
        return Response(content=content, status_code=upstream_response.status_code, headers=response_headers, media_type=content_type or None)

    return app


__all__ = ["ProxyProjectConfig", "create_project_proxy_app"]
