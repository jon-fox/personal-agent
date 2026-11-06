import os

# Set before agent.agent is imported: Agent() refuses to construct without a key.
os.environ.setdefault("OPENAI_API_KEY", "test-key")
