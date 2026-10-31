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
    try:
        memory.add(content, user_id=MEMORY_USER_ID)
    except Exception:
        logging.getLogger(__name__).exception("memory add failed")
        return "Failed to save memory; the memory backend returned an error."
    return "Saved to long-term memory."


@agent.tool_plain
def list_memories(limit: int = 50) -> str:
    """List stored long-term memories with their IDs, newest first. Use this to review
    what is remembered before correcting or deleting a memory."""
    try:
        result = memory.list_memories(user_id=MEMORY_USER_ID, limit=limit)
    except Exception:
        logging.getLogger(__name__).exception("memory list failed")
        return "Failed to list memories; the memory backend returned an error."
    items = (result.get("vdb") or {}).get("memories") or []
    if not items:
        return "No memories stored."
    return "\n".join(f"{m['memory_id']}: {m['content']}" for m in items if m.get("content"))


@agent.tool_plain
def forget_memory(memory_id: str) -> str:
    """Delete a stored memory that is wrong or outdated, by the ID shown in list_memories.
    When the user corrects a remembered fact, delete the stale memory and save the new one."""
    try:
        memory.delete(memory_id)
    except Exception:
        logging.getLogger(__name__).exception("memory delete failed")
        return "Failed to delete memory; the memory backend returned an error."
    return f"Deleted memory {memory_id}."


def main() -> None:
    agent.to_cli_sync()


if __name__ == "__main__":
    main()
