import logging
import os

from agent_sdk.database.mongo import BaseMongoDatabase

logger = logging.getLogger("agent_news.mongo")

_DB_NAME = os.getenv("MONGO_DB_NAME", "agent_news")

class MongoDB(BaseMongoDatabase):
    @classmethod
    def db_name(cls) -> str:
        return _DB_NAME
