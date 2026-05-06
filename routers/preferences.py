import logging

from fastapi import APIRouter, HTTPException, Request

from database.mongo import MongoDB
from models.requests import NewsPreferencesRequest

from app import limiter

router = APIRouter(tags=["preferences"])
logger = logging.getLogger("agent_news.api")


@router.post("/preferences")
@limiter.limit("20/minute")
async def save_preferences(body: NewsPreferencesRequest, request: Request):
    """Save or update user news preferences."""
    user_id = request.headers.get("X-User-Id") or None
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    await MongoDB.save_preferences(user_id=user_id, preferences=body.model_dump())
    logger.info("Saved news preferences for user='%s'", user_id)
    return {"success": True}


@router.get("/preferences")
@limiter.limit("60/minute")
async def get_preferences(request: Request):
    """Retrieve user news preferences."""
    user_id = request.headers.get("X-User-Id") or None
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    prefs = await MongoDB.get_preferences(user_id)
    return {"preferences": prefs or {}}
