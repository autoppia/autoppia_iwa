## Dynamic Proxy Module

This module packages the FastAPI reverse proxy that mutates demo web HTML before it reaches clients.

### Build & Run (Docker)

```bash
docker build -f modules/dynamic_proxy/Dockerfile -t autoppia-dynamic-proxy .
docker run --network=host \
  -e DYNAMIC_PROXY_CONFIG=/config/proxy_config.json \
  -v $(pwd)/modules/dynamic_proxy/config.example.json:/config/proxy_config.json \
  autoppia-dynamic-proxy
```

Mount your own config file with all demo web mappings; the service reads `DYNAMIC_PROXY_CONFIG` to locate it.

### Config format

Each entry in the JSON describes a project:

```json
{
  "project_id": "autocinema",
  "origin": "http://127.0.0.1:8100",
  "listen_host": "0.0.0.0",
  "listen_port": 8200,
  "palette_dir": null,
  "enable_d1": true,
  "enable_d3": true,
"enable_d4": true,
"inject_client_runtime": true
}
```

The proxy listens on `listen_host:listen_port`, forwards to `origin`, and injects the universal runtime (`/dynamic/runtime.js`) so every page obeys deterministic D1/D3/D4 behavior keyed by `?seed=…`. When `inject_client_runtime` is `true`, server-side DOM mutations are disabled and only the client runtime makes changes.
