import os
from pathlib import Path


def _env_bool(key: str, default: str = "false") -> bool:
    return os.getenv(key, default).lower() in ("1", "true", "yes", "on")


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
CHUTES_USE_BEARER = _env_bool("CHUTES_USE_BEARER")

# LLM credentials (validated lazily when actually used, not at import time)
HAS_OPENAI_CREDENTIALS = bool(OPENAI_API_KEY)
HAS_CHUTES_CREDENTIALS = bool(CHUTES_API_KEY)

# ============================
# Application Configuration
# ============================
EVALUATOR_HEADLESS = _env_bool("EVALUATOR_HEADLESS", "true")

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
USE_APIFIED_AGENT = _env_bool("USE_APIFIED_AGENT", "true")
AGENT_HOST = os.getenv("AGENT_HOST", "localhost")
AGENT_PORT = int(os.getenv("AGENT_PORT", "5000"))

# ============================
# Validator Configuration
# ============================
VALIDATOR_ID = os.getenv("VALIDATOR_ID", "custom_validator")
