from __future__ import annotations

import fastapi
import httpx
from fastapi.responses import HTMLResponse
from fastapi.testclient import TestClient

from modules.dynamic_proxy.service.app import ProxyProjectConfig, create_project_proxy_app


def _build_origin_app():
    app = fastapi.FastAPI()

    @app.get("/")
    async def home():
        return HTMLResponse("<html><body><div id='root'><button>Pay</button></div></body></html>")

    return app


def test_proxy_mutates_html():
    origin_app = _build_origin_app()
    transport = httpx.ASGITransport(app=origin_app)

    async def client_factory():
        return httpx.AsyncClient(transport=transport, base_url="http://origin.local")

    config = ProxyProjectConfig(
        project_id="autotest",
        origin="http://origin.local",
        listen_port=8100,
        enable_d1=True,
        enable_d3=True,
        enable_d4=True,
        palette_dir=None,
        audit_root=None,
    )
    app = create_project_proxy_app(config, http_client_factory=client_factory)
    with TestClient(app) as client:
        response = client.get("/?seed=11")
        assert response.status_code == 200
        assert "iwa-wrapper" in response.text
        assert response.headers.get("x-iwa-mutated") == "1"
