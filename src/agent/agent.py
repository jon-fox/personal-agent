import logging

from hy_memory import HyMemoryClient
from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import WebSearch
from pydantic_ai_harness import Advisor, Coder

from constants.agent_constants import ADVISOR_MODEL, AGENT_MODEL, MEMORY_MODE, MEMORY_USER_ID

logging.getLogger("hy_memory").setLevel(logging.WARNING)

memory = HyMemoryClient(mode=MEMORY_MODE)  # stores under ~/.hy_memory; uses OPENAI_API_KEY unless MEMORY_LLM_*/MEMORY_EMBEDDER_* are set

agent = Agent(
    AGENT_MODEL,
    capabilities=[
        Coder(),  # files, shell, repo context, planning, sub-agents, context management
        WebSearch(),  # look up docs and error messages on the web
        Advisor(ADVISOR_MODEL),  # a second opinion from another model when stuck
    ],
)


@agent.instructions
def recall_memories(ctx: RunContext) -> str:
    if not isinstance(ctx.prompt, str) or not ctx.prompt.strip():
        return ""
    try:
        results = memory.search(ctx.prompt, user_ids=[MEMORY_USER_ID], limit=5)
    except Exception:
        logging.getLogger(__name__).exception("memory search failed")
        return ""
    recalled = []
    for channel in (results.get("memories") or {}).values():
        if isinstance(channel, list):
            recalled += [m["content"] for m in channel if isinstance(m, dict) and m.get("content")]
    if not recalled:
        return ""
    lines = "\n".join(f"- {item}" for item in recalled)
    return f"Memories about the user recalled from previous sessions:\n{lines}"


@agent.tool_plain
def save_memory(content: str) -> str:
    """Save a fact worth remembering across sessions: user preferences, project context,
    decisions, or corrections. Phrase it as a standalone sentence."""
    memory.add(content, user_id=MEMORY_USER_ID)
    return "Saved to long-term memory."


def main() -> None:
    agent.to_cli_sync()


if __name__ == "__main__":
    main()
