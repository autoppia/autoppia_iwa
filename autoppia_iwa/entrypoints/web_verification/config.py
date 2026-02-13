"""
Configuration for Web Verification Pipeline
"""

from dataclasses import dataclass


@dataclass
class WebVerificationConfig:
    """Configuration for web verification pipeline"""

    # Task generation
    tasks_per_use_case: int = 2
    dynamic_enabled: bool = True

    # LLM review
    llm_review_enabled: bool = True
    llm_timeout_seconds: float = 30.0
    reviewer_type: str = "old"  # Either 'old' or 'new'

    # IWAP client
    iwap_enabled: bool = True
    iwap_base_url: str | None = None  # Will be set from env or default
    iwap_api_key: str = "AIagent2025"  # API key for IWAP
    iwap_timeout_seconds: float = 10.0
    iwap_use_mock: bool = False  # Use mock response instead of real API (for testing)

    # Dynamic verification
    dynamic_verification_enabled: bool = True
    seed_values: list[int] = None  # Default seeds to test

    # Output
    output_dir: str = "./verification_results"
    verbose: bool = False

    def __post_init__(self):
        """Set default values after initialization"""
        if self.seed_values is None:
            self.seed_values = [1, 50, 100, 200, 300]

        if self.iwap_base_url is None:
            # Try to get from environment variable or use default IWAP API URL
            import os

            self.iwap_base_url = os.getenv("IWAP_BASE_URL", "https://api-leaderboard.autoppia.com")
