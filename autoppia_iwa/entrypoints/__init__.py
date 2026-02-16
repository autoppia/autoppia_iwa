import os

from autoppia_iwa.config.env import init_env

# Load .env only for standalone entrypoints (safe default).
if os.getenv("AUTOPPIA_IWA_LOAD_DOTENV", "true").lower() not in {"0", "false", "no"}:
    init_env(override=True)

# Allow lightweight consumers (e.g., affine_service) to skip full DI bootstrap
# to avoid pulling optional heavy dependencies.
if os.getenv("SKIP_APP_BOOTSTRAP", "").lower() not in {"1", "true", "yes"}:
    from autoppia_iwa.src.bootstrap import AppBootstrap

    app = AppBootstrap()
else:  # pragma: no cover - simple guard
    app = None
