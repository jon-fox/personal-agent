import logging

from hy_memory import HyMemoryClient
from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import WebSearch
from pydantic_ai_harness import Advisor, Coder

from agent.security_review import format_report, run_review
from constants.agent_constants import ADVISOR_MODEL, AGENT_MODEL, MEMORY_MODE, MEMORY_USER_ID

MAX_LIST_LIMIT = 200

logging.getLogger("hy_memory").setLevel(logging.WARNING)

# stores under ~/.hy_memory; uses OPENAI_API_KEY unless MEMORY_LLM_*/MEMORY_EMBEDDER_* are set
memory = HyMemoryClient(mode=MEMORY_MODE)

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
    recalled = list(dict.fromkeys(item.strip() for item in recalled if str(item).strip()))
    if not recalled:
        return ""
    lines = "\n".join(f"- {item}" for item in recalled)
    return f"Memories about the user recalled from previous sessions:\n{lines}"


@agent.tool_plain
def save_memory(content: str) -> str:
    """Save a fact worth remembering across sessions: user preferences, project context,
    decisions, or corrections. Phrase it as a standalone sentence."""
    content = content.strip()
    if not content:
        return "Nothing to save: content is empty."
    try:
        memory.add(content, user_id=MEMORY_USER_ID)
    except Exception:
        logging.getLogger(__name__).exception("memory add failed")
        return "Failed to save memory; the memory backend returned an error."
    return "Saved to long-term memory."


@agent.tool_plain
def list_memories(limit: int = 50) -> str:
    """List stored long-term memories with their IDs, newest first. Use this to review
    what is remembered before correcting or deleting a memory. Limit is clamped to 1-200."""
    limit = max(1, min(limit, MAX_LIST_LIMIT))
    try:
        result = memory.list_memories(user_id=MEMORY_USER_ID, limit=limit)
    except Exception:
        logging.getLogger(__name__).exception("memory list failed")
        return "Failed to list memories; the memory backend returned an error."
    items = (result.get("vdb") or {}).get("memories") or []
    lines = [
        f"{m['memory_id']}: {m['content']}"
        for m in items
        if isinstance(m, dict) and m.get("memory_id") and m.get("content")
    ]
    return "\n".join(lines) if lines else "No memories stored."


@agent.tool_plain
def forget_memory(memory_id: str) -> str:
    """Delete a stored memory that is wrong or outdated, by the ID shown in list_memories.
    When the user corrects a remembered fact, delete the stale memory and save the new one."""
    memory_id = memory_id.strip()
    if not memory_id:
        return "Nothing to delete: memory_id is empty. Use list_memories to find the ID."
    try:
        memory.delete(memory_id)
    except Exception:
        logging.getLogger(__name__).exception("memory delete failed")
        return "Failed to delete memory; the memory backend returned an error."
    return f"Deleted memory {memory_id}."


@agent.tool_plain
def review_repo_security(path: str = ".") -> str:
    """Run a read-only security review of a repository: tracked sensitive files, possible committed
    secrets, .gitignore gaps, CI workflow hardening, and Dependabot presence. Returns findings with
    severity and location; makes no changes."""
    try:
        return format_report(run_review(path))
    except Exception:
        logging.getLogger(__name__).exception("security review failed")
        return "Security review failed; see logs for the error."


def main() -> None:
    agent.to_cli_sync()


if __name__ == "__main__":
    main()
