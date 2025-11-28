import os

if os.getenv("SKIP_APP_BOOTSTRAP", "").lower() not in {"1", "true", "yes"}:
    from autoppia_iwa.src.bootstrap import AppBootstrap

    app = AppBootstrap()
else:  # pragma: no cover
    app = None
