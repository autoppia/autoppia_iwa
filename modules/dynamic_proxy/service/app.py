from __future__ import annotations

import asyncio
import base64
import inspect
import json
from pathlib import Path
from typing import Any, Awaitable, Callable, Iterable

import httpx
from fastapi import FastAPI, Request, Response
from pydantic import AnyHttpUrl, BaseModel, Field
from starlette.datastructures import QueryParams

from modules.dynamic_proxy.core.config import DynamicPhaseConfig
from modules.dynamic_proxy.core.engine import MutationEngine, MutationResult


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
    if config.inject_client_runtime:
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

    def _build_client_runtime_script(plan_payload: dict[str, Any], seed: int) -> str:
        payload = {
            "project_id": config.project_id,
            "seed": seed,
            "plan": {
                "d1": plan_payload.get("d1") or [],
                "d3": plan_payload.get("d3") or [],
            },
        }
        if not payload["plan"]["d1"] and not payload["plan"]["d3"]:
            return ""
        encoded = base64.b64encode(json.dumps(payload, ensure_ascii=False).encode("utf-8")).decode("ascii")
        script = (
            "(function(){"
            f"const payload=JSON.parse(atob('{encoded}'));"
            "const store=window.__iwaClientRuntimeStore||(window.__iwaClientRuntimeStore={});"
            "const key=payload.project_id+':'+payload.seed;"
            "if(store[key]){return;}"
            "const plan=payload.plan||{};"
            "const d1=plan.d1||[];"
            "const d3=plan.d3||[];"
            "if(!d1.length&&!d3.length){return;}"
            "const insertedAttr='data-iwa-node-id';"
            "const wrapperAttr='data-iwa-wrapper-id';"
            "const contentAttr='data-iwa-content-id';"
            "const attrAttr='data-iwa-attr-id';"
            "const templateCache={};"
            "const getNodes=(instr)=>{const key=instr.id||instr.target||'node';if(!templateCache[key]){const tpl=document.createElement('template');tpl.innerHTML=instr.html||'';templateCache[key]=Array.from(tpl.content.childNodes);}return templateCache[key];};"
            "const cloneNodes=(nodes,id)=>nodes.map(node=>{const clone=node.cloneNode(true);if(clone.nodeType===1){clone.setAttribute(insertedAttr,id);}return clone;});"
            "const removeInserted=(id)=>{document.querySelectorAll('['+insertedAttr+'=\"'+id+'\"]').forEach(node=>{if(node.parentNode){node.parentNode.removeChild(node);}});};"
            "const insertNodes=(parent,before,nodes)=>{if(!parent){return;}nodes.forEach(node=>parent.insertBefore(node,before));};"
            "const applyStructural=(instr)=>{"
            "if(!instr||!instr.target){return false;}"
            "const target=document.querySelector(instr.target);"
            "if(!target){return false;}"
            "const op=instr.operation||'append_child';"
            "const id=instr.id||instr.target||'d1';"
            "const nodes=getNodes(instr);"
            "const parent=target.parentNode;"
            "if(op==='wrap_with'){const wrappers=nodes.filter(node=>node.nodeType===1);if(!wrappers.length){return false;}const wrapper=wrappers[0].cloneNode(true);wrapper.setAttribute(wrapperAttr,id);if(parent){parent.insertBefore(wrapper,target);}else{(document.body||document.documentElement).appendChild(wrapper);}wrapper.appendChild(target);return true;}"
            "if(op==='replace_inner_html'){target.innerHTML=instr.html||'';target.setAttribute(contentAttr,id);return true;}"
            "if(op==='insert_before'){if(!parent||!nodes.length){return false;}removeInserted(id);insertNodes(parent,target,cloneNodes(nodes,id));return true;}"
            "if(op==='insert_after'){if(!parent||!nodes.length){return false;}removeInserted(id);insertNodes(parent,target.nextSibling,cloneNodes(nodes,id));return true;}"
            "if(op==='prepend_child'){if(!nodes.length){return false;}removeInserted(id);const clones=cloneNodes(nodes,id);const first=target.firstChild;clones.forEach(node=>target.insertBefore(node,first));return true;}"
            "if(op==='append_child'){if(!nodes.length){return false;}removeInserted(id);cloneNodes(nodes,id).forEach(node=>target.appendChild(node));return true;}"
            "if(op==='shuffle_children'){return false;}"
            "return false;"
            "};"
            "const applyAttributes=(instr)=>{"
            "if(!instr||!instr.target){return false;}"
            "const target=document.querySelector(instr.target);"
            "if(!target){return false;}"
            "const op=instr.operation||'set_attribute';"
            "const id=instr.id||instr.target||'d3';"
            "if(op==='set_attribute'&&instr.attribute){if(target.getAttribute(instr.attribute)===instr.value){return false;}target.setAttribute(instr.attribute,instr.value||'');target.setAttribute(attrAttr+'-'+id,'1');return true;}"
            "if(op==='append_class'&&instr.value){if(target.classList.contains(instr.value)){return false;}target.classList.add(instr.value);target.setAttribute(attrAttr+'-'+id,'1');return true;}"
            "if(op==='replace_text'){if(target.textContent===(instr.text||'')){return false;}target.textContent=instr.text||'';target.setAttribute(attrAttr+'-'+id,'1');return true;}"
            "return false;"
            "};"
            "const applyAll=()=>{let changed=false;d1.forEach(instr=>{try{if(applyStructural(instr)){changed=true;}}catch(e){}});d3.forEach(instr=>{try{if(applyAttributes(instr)){changed=true;}}catch(e){}});return changed;};"
            "const start=()=>{const runtime={active:true,pending:false};store[key]=runtime;const run=()=>{applyAll();};const observer=new MutationObserver(()=>{if(!runtime.active){return;}if(runtime.pending){return;}runtime.pending=true;requestAnimationFrame(()=>{runtime.pending=false;applyAll();});});const root=document.body||document.documentElement;run();observer.observe(root,{childList:true,subtree:true});runtime.observer=observer;};"
            "if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',start,{once:true});}else{start();}"
            "})();"
        )
        return f"<script data-iwa-client-runtime=\"true\">{script}</script>"

    def _inject_client_runtime(html: str, plan_payload: dict[str, Any], seed: int) -> str:
        script_tag = _build_client_runtime_script(plan_payload, seed)
        if not script_tag:
            return html
        lower = html.lower()
        marker = lower.rfind("</body>")
        if marker == -1:
            return html + script_tag
        return html[:marker] + script_tag + html[marker:]

    async def _mutate_if_needed(content: bytes, full_url: str, charset_hint: str, is_head: bool, seed: int) -> tuple[bytes, MutationResult | None]:
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
        if config.inject_client_runtime and result.plan:
            mutated_html = _inject_client_runtime(mutated_html, result.plan, seed)
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
        mutate = (
            not _should_skip_mutation(request.query_params)
            and "text/html" in content_type
            and phase_config.any_enabled()
            and upstream_response.status_code not in (204, 304)
        )
        if mutate:
            seed = _extract_seed(request.query_params)
            full_url = str(upstream_response.request.url)
            content, result = await _mutate_if_needed(content, full_url, content_type, request.method.upper() == "HEAD", seed)
            if result and result.audit_record and app.state.audit_writer:
                await app.state.audit_writer.write(result.audit_record)

        response_headers = _filter_headers(upstream_response.headers.items())
        if mutate:
            # Mutated payloads are always returned as plain UTF-8, so remove the upstream encoding marker.
            response_headers.pop("content-encoding", None)
            response_headers["x-iwa-mutated"] = "1"
        response_headers["content-length"] = str(len(content))
        return Response(content=content, status_code=upstream_response.status_code, headers=response_headers, media_type=content_type or None)

    return app


__all__ = ["ProxyProjectConfig", "create_project_proxy_app"]
