from autoppia_iwa.src.demo_webs.web_verification.config import WebVerificationConfig

__all__ = ["WebVerificationConfig", "WebVerificationPipeline"]


def __getattr__(name: str):
    if name == "WebVerificationPipeline":
        from autoppia_iwa.src.demo_webs.web_verification.pipeline import WebVerificationPipeline

        return WebVerificationPipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
