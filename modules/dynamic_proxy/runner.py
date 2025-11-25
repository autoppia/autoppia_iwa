from __future__ import annotations

import json
import multiprocessing
import os
import signal
import sys
from pathlib import Path
from typing import Iterable

import uvicorn

from modules.dynamic_proxy.service.app import ProxyProjectConfig, create_project_proxy_app


def _load_configs(path: Path) -> list[ProxyProjectConfig]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload if isinstance(payload, list) else payload.get("projects", [])
    return [ProxyProjectConfig(**entry) for entry in entries]


def _run_uvicorn(config_dict: dict) -> None:
    cfg = ProxyProjectConfig(**config_dict)
    app = create_project_proxy_app(cfg)
    uvicorn.run(app, host=cfg.listen_host, port=cfg.listen_port, log_level="info")


def _spawn_processes(configs: Iterable[ProxyProjectConfig]) -> list[multiprocessing.Process]:
    processes: list[multiprocessing.Process] = []
    for cfg in configs:
        proc = multiprocessing.Process(target=_run_uvicorn, args=(cfg.model_dump(),), name=f"{cfg.project_id}-proxy", daemon=False)
        proc.start()
        processes.append(proc)
        print(f"[dynamic-proxy] {cfg.project_id} -> {cfg.origin} on {cfg.listen_host}:{cfg.listen_port}", flush=True)
    return processes


def run_from_config(config_path: Path, *, projects: list[str] | None = None, list_only: bool = False) -> int:
    configs = _load_configs(config_path)
    if projects:
        wanted = {pid.lower() for pid in projects}
        configs = [cfg for cfg in configs if cfg.project_id.lower() in wanted]

    if not configs:
        print("No proxy configurations found.", file=sys.stderr)
        return 1

    if list_only:
        for cfg in configs:
            print(f"{cfg.project_id}\t{cfg.listen_host}:{cfg.listen_port} -> {cfg.origin}")
        return 0

    processes = _spawn_processes(configs)

    def _shutdown(signum, _frame) -> None:
        for proc in processes:
            if proc.is_alive():
                proc.terminate()

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    for proc in processes:
        proc.join()
    return 0


def resolve_config_path(arg_path: Path | None) -> Path:
    env_value = os.getenv("DYNAMIC_PROXY_CONFIG")
    if arg_path:
        return arg_path.expanduser().resolve()
    if env_value:
        return Path(env_value).expanduser().resolve()
    default = Path("modules/dynamic_proxy/config.example.json")
    return default.expanduser().resolve()


__all__ = ["run_from_config", "resolve_config_path"]
