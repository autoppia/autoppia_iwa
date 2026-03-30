import os
from pathlib import Path

try:
    from distutils.util import strtobool
except ImportError:
    # Python 3.12+ removed distutils, use alternative
    def strtobool(val: str) -> int:
        """Convert a string representation of truth to 1 or 0."""
        val = val.lower()
        if val in ("y", "yes", "t", "true", "on", "1"):
            return 1
        elif val in ("n", "no", "f", "false", "off", "0"):
            return 0
        else:
            raise ValueError(f"invalid truth value {val!r}")


# ============================
# LLM CONFIGURATION
# ============================
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # Can be "openai" or "chutes"
LLM_THRESHOLD = int(os.getenv("LLM_THRESHOLD", 100))
LLM_CONTEXT_WINDOW = int(os.getenv("LLM_CONTEXT_WINDOW", 10000))

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", 2000))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0.8))

# Chutes Configuration
CHUTES_BASE_URL = os.getenv("CHUTES_BASE_URL", "https://your-username-your-chute.chutes.ai/v1")
CHUTES_API_KEY = os.getenv("CHUTES_API_KEY")
CHUTES_MODEL = os.getenv("CHUTES_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
CHUTES_MAX_TOKENS = int(os.getenv("CHUTES_MAX_TOKENS", 2048))
CHUTES_TEMPERATURE = float(os.getenv("CHUTES_TEMPERATURE", 0.7))
CHUTES_USE_BEARER = bool(strtobool(os.getenv("CHUTES_USE_BEARER", "False")))

# Validate critical environment variables
has_openai_credentials = bool(OPENAI_API_KEY)
has_chutes_credentials = bool(CHUTES_API_KEY)

if not has_openai_credentials and not has_chutes_credentials:
    raise ValueError("No LLM credentials configured. Set OPENAI_API_KEY or CHUTES_API_KEY (and LLM_PROVIDER=chutes if you want to use Chutes for generation).")

if LLM_PROVIDER == "openai" and not has_openai_credentials:
    raise ValueError("LLM_PROVIDER is set to 'openai' but OPENAI_API_KEY is missing. Set OPENAI_API_KEY or switch to LLM_PROVIDER='chutes' with CHUTES_API_KEY.")
if LLM_PROVIDER == "chutes" and not has_chutes_credentials:
    raise ValueError("LLM_PROVIDER is set to 'chutes' but CHUTES_API_KEY is missing. Set CHUTES_API_KEY or switch to LLM_PROVIDER='openai' with OPENAI_API_KEY.")

# ============================
# Application Configuration
# ============================
EVALUATOR_HEADLESS = bool(strtobool(os.getenv("EVALUATOR_HEADLESS", "True")))

# ============================
# Project Base Directory Path
# ============================
PROJECT_BASE_DIR = Path(__file__).resolve().parents[1]

# ============================
# DEMO WEBS
# ============================
DEMO_WEBS_ENDPOINT = os.getenv("DEMO_WEBS_ENDPOINT", "http://localhost").strip("/")
DEMO_WEBS_STARTING_PORT = int(os.getenv("DEMO_WEBS_STARTING_PORT", "8000"))
DEMO_WEB_SERVICE_PORT = int(os.getenv("DEMO_WEB_SERVICE_PORT", "8090"))

# ============================
# Agent Configurations
# ============================
AGENT_NAME = os.getenv("AGENT_NAME", "Newbie Agent")
USE_APIFIED_AGENT = bool(strtobool(os.getenv("USE_APIFIED_AGENT", "true")))
AGENT_HOST = os.getenv("AGENT_HOST", "localhost")
AGENT_PORT = int(os.getenv("AGENT_PORT", "5000"))

# ============================
# Validator Configuration
# ============================
VALIDATOR_ID = os.getenv("VALIDATOR_ID", "custom_validator")
