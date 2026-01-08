import os
from pathlib import Path

from distutils.util import strtobool
from dotenv import load_dotenv

# Load environment variables from the autoppia_iwa project .env, not the caller CWD.
# This ensures DEMO_WEB_SERVICE_PORT and related settings come from this repo.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env", override=True)

# ============================
# LLM CONFIGURATION
# ============================
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local")  # Can be "local", "openai", or "chutes"
LLM_THRESHOLD = 100
LLM_CONTEXT_WINDOW = int(os.getenv("LLM_CONTEXT_WINDOW", 10000))

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_MAX_TOKENS = int(os.getenv("LLM_CONTEXT_WINDOW", 2000))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0.8))

# Chutes Configuration
CHUTES_BASE_URL = os.getenv("CHUTES_BASE_URL", "https://your-username-your-chute.chutes.ai/v1")
CHUTES_API_KEY = os.getenv("CHUTES_API_KEY")
CHUTES_MODEL = os.getenv("CHUTES_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
CHUTES_MAX_TOKENS = int(os.getenv("CHUTES_MAX_TOKENS", 2048))
CHUTES_TEMPERATURE = float(os.getenv("CHUTES_TEMPERATURE", 0.7))
CHUTES_USE_BEARER = bool(strtobool(os.getenv("CHUTES_USE_BEARER", "False")))

# Validate critical environment variables
if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER is set to 'openai'.")
if LLM_PROVIDER == "chutes" and not CHUTES_API_KEY:
    raise ValueError("CHUTES_API_KEY is required when LLM_PROVIDER is set to 'chutes'.")

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
