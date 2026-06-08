"""
settings.py
===========
One place for all configuration (paths, DB credentials, model names).

WHY:
No secrets or magic strings scattered through the code. Everything that
might change between your laptop and a server lives here, read from
environment variables where possible.

WHAT GOES HERE LATER:
- DATABASE_URL (read from env, never hard-code passwords)
- EMBEDDING_MODEL name
- RATE_LIMIT_SECONDS, USER_AGENT for the scraper
- API keys for LLM providers (read from env)
"""

import os

# --- Database ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/vn_legal")

# --- Embedding model ---
EMBEDDING_MODEL = "vinai/phobert-base"
EMBEDDING_DIM = 768

# --- Scraper politeness ---
RATE_LIMIT_SECONDS = 3.0
USER_AGENT = "VGU-Research-Bot/1.0 (Thesis research; contact: your.email@vgu.edu.vn)"

# --- LLM API keys (set these as environment variables, do NOT commit them) ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
