import logging
import os

from agent_sdk.agents import BaseAgent
from agent_sdk.checkpoint import get_default_checkpointer

from .config import MCP_SERVERS
from .prompts import SYSTEM_PROMPT

logger = logging.getLogger("agent_news.agent")

_agent_instance: BaseAgent | None = None


def create_agent() -> BaseAgent:
    global _agent_instance
    if _agent_instance is None:
        logger.info("Creating news agent (singleton) with MCP servers")
        _agent_instance = BaseAgent(
            tools=[],
            mcp_servers=MCP_SERVERS,
            system_prompt=SYSTEM_PROMPT,
            checkpointer=get_default_checkpointer(os.getenv("MONGO_DB_NAME", "agent_news")),
        )
    return _agent_instance
