import getpass
import os

OPENAI_PREFIX = "openai:"
ANTHROPIC_PREFIX = "anthropic:"

OPENAI_SOL = OPENAI_PREFIX + "gpt-5.6-sol"


def _default_user_id() -> str:
    try:
        return getpass.getuser()
    except Exception:
        return "default"


AGENT_MODEL = os.getenv("AGENT_MODEL", OPENAI_SOL)
ADVISOR_MODEL = os.getenv("ADVISOR_MODEL", OPENAI_SOL)
MEMORY_MODE = os.getenv("MEMORY_MODE", "pro")  # lite = embeddings only, no LLM extraction
MEMORY_USER_ID = os.getenv("MEMORY_USER_ID") or _default_user_id()
