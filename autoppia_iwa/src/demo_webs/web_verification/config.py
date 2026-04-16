"""
Configuration for Web Verification Pipeline
"""

from dataclasses import dataclass


@dataclass
class WebVerificationConfig:
    """Configuration for web verification pipeline"""

    # Scope: if non-empty, only these use case names (exact match) are verified; None = all
    use_case_filter: list[str] | None = None

    # Task generation
    tasks_per_use_case: int = 2
    dynamic_enabled: bool = True

    # LLM review
    llm_review_enabled: bool = True
    llm_timeout_seconds: float = 30.0

    # Step 3 reference solution: registered trajectories preferred over IWAP when enabled
    trajectory_doability_enabled: bool = True

    # IWAP client (fallback when no trajectory is registered for the use case)
    iwap_enabled: bool = True
    iwap_base_url: str | None = None  # Will be set from env or default
    iwap_api_key: str = "AIagent2025"  # API key for IWAP
    iwap_timeout_seconds: float = 10.0
    iwap_use_mock: bool = False  # Use mock response instead of real API (for testing)

    # Dynamic verification
    dynamic_verification_enabled: bool = True
    seed_values: list[int] | None = None  # Default seeds to test

    # Trajectory evaluation (repo-local golden flows from trajectories.py)
    evaluate_trajectories: bool = False
    # Skip task generation, LLM review, and IWAP; only V2 + trajectory replay (no OpenAI init).
    evaluate_trajectories_only: bool = False

    # Event trajectories verification (project-level)
    event_trajectory_verification_enabled: bool = True

    # Data extraction (steps 2.5 + 2.6): trajectories + DE task generation verification
    data_extraction_verification_enabled: bool = True
    data_extraction_seed: int = 1

    # Output
    output_dir: str = "./verification_results"
    verbose: bool = False

    def __post_init__(self):
        """Set default values after initialization"""
        if self.evaluate_trajectories_only:
            self.evaluate_trajectories = True
        if self.seed_values is None:
            self.seed_values = [1, 50, 100, 200, 300]

        if self.iwap_base_url is None:
            # Try to get from environment variable or use default local IWAP API URL
            import os

            self.iwap_base_url = os.getenv("IWAP_BASE_URL", "https://api-leaderboard.autoppia.com")
