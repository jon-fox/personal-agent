from pydantic_ai import Agent
from pydantic_ai.capabilities import WebSearch
from pydantic_ai_harness import Advisor, Coder
from constants.agent_constants import OPENAI_SOL

agent = Agent(
    OPENAI_SOL,
    capabilities=[
        Coder(),  # files, shell, repo context, planning, sub-agents, context management
        WebSearch(),  # look up docs and error messages on the web
        Advisor('openai:gpt-5.6-sol'),  # a second opinion from another model when stuck
    ],
)
agent.to_cli_sync()