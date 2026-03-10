"""
Web Verification Pipeline

This module provides a comprehensive verification pipeline for web projects that:
1. Generates 2 tasks per use case and tests them
2. Reviews tasks with GPT to verify tests make sense with prompts
3. Queries iwap to check how many people successfully solved tasks
4. Verifies dynamic functionality by testing with different seed values
"""

from .config import WebVerificationConfig
from .web_verification_pipeline import WebVerificationPipeline

__all__ = ["WebVerificationConfig", "WebVerificationPipeline"]
