import os

# Allow lightweight consumers (e.g., affine_service) to skip full DI bootstrap
# to avoid pulling optional heavy dependencies.
if os.getenv("SKIP_APP_BOOTSTRAP", "").lower() not in {"1", "true", "yes"}:
    from autoppia_iwa.src.bootstrap import AppBootstrap

    app = AppBootstrap()
else:  # pragma: no cover - simple guard
    app = None
