import asyncio
import logging
from datetime import datetime, timezone

from agent_sdk.database.memory import get_memories
from database.mongo import MongoDB

from .prompts import SYSTEM_PROMPT, RESPONSE_FORMAT_INSTRUCTIONS

logger = logging.getLogger("agent_news.context_builder")

# Inlined from agent_common.utils.text — update to agent_common import once submodule is added
_TRIVIAL_FOLLOWUPS: frozenset[str] = frozenset({
    "yes", "no", "sure", "ok", "okay", "please", "yes please",
    "no thanks", "proceed", "go ahead", "continue", "yeah", "yep",
})


def _build_system_prompt(response_format: str | None = None) -> str:
    fmt = RESPONSE_FORMAT_INSTRUCTIONS.get(response_format or "detailed", "")
    if fmt:
        return SYSTEM_PROMPT + "\n" + fmt
    return SYSTEM_PROMPT


async def _build_dynamic_context(session_id: str, query: str, response_format: str | None = None,
                                  user_id: str | None = None) -> str:
    """Build dynamic context block (date, memories, preferences) to prepend to the user query."""
    mem_key = user_id or session_id
    mem_err: str | None = None

    async def _get_mem():
        if query.strip().lower() not in _TRIVIAL_FOLLOWUPS and len(query.strip()) > 10:
            return await asyncio.to_thread(get_memories, user_id=mem_key, query=query)
        return [], None

    async def _get_prefs():
        if user_id:
            return await MongoDB.get_preferences(user_id)
        return None

    (memories, mem_err), preferences = await asyncio.gather(_get_mem(), _get_prefs())

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    year = today[:4]

    parts = []
    parts.append(
        f"Today's date: {today}. Always include the current year ({year}) and today's date "
        f"in search queries to get the most recent news (e.g. 'AI regulation news {today}')."
    )

    if preferences:
        pref_parts = []
        if preferences.get("topics"):
            pref_parts.append(f"Topics of interest: {', '.join(preferences['topics'])}")
        if preferences.get("regions"):
            pref_parts.append(f"Regions of focus: {', '.join(preferences['regions'])}")
        if preferences.get("excluded_topics"):
            pref_parts.append(f"Topics to exclude: {', '.join(preferences['excluded_topics'])}")
        if preferences.get("market_tickers"):
            pref_parts.append(f"Tracked tickers/assets: {', '.join(preferences['market_tickers'])}")
        if pref_parts:
            parts.append(
                "User's news preferences (stored settings — always honor these):\n"
                + "\n".join(f"- {p}" for p in pref_parts)
            )

    if memories:
        memory_lines = "\n".join(f"- {m}" for m in memories)
        parts.append(
            f"User's interests (from past conversations):\n{memory_lines}\n"
            "Use these to personalize coverage when relevant."
        )
        logger.info("Injected %d memories into context for session='%s'", len(memories), session_id)

    if mem_err:
        parts.append(f"Note: {mem_err}")
        logger.warning("Mem0 degradation for session='%s': %s", session_id, mem_err)

    context_block = "\n\n".join(parts)
    return f"[CONTEXT]\n{context_block}\n[/CONTEXT]\n\n"
