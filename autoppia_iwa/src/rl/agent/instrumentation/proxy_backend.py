from __future__ import annotations

from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService


class ProxyBackendDemoWebService(BackendDemoWebService):
    """Force usage of the webs_server proxy API regardless of the configured backend port."""

    def _should_use_proxy_api(self) -> bool:  # type: ignore[override]
        return True
