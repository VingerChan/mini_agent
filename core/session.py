from __future__ import annotations

import json
import logging
from typing import Any

import redis.asyncio as redis

logger = logging.getLogger(__name__)

DEFAULT_TTL = 86400  # 24 hours


class SessionManager:
    def __init__(self, redis_url: str, ttl: int = DEFAULT_TTL) -> None:
        self._redis = redis.from_url(redis_url, decode_responses=True)
        self._ttl = ttl

    async def get_history(self, session_id: str) -> list[dict[str, Any]]:
        data = await self._redis.get(f"session:{session_id}")
        if data:
            logger.info("加载会话历史: session=%s, 消息数=%d", session_id, len(json.loads(data)))
            return json.loads(data)
        logger.info("新会话: session=%s", session_id)
        return []

    async def save_history(self, session_id: str, messages: list[dict[str, Any]]) -> None:
        await self._redis.setex(f"session:{session_id}", self._ttl, json.dumps(messages))
        logger.info("保存会话历史: session=%s, 消息数=%d", session_id, len(messages))

    async def delete_session(self, session_id: str) -> None:
        await self._redis.delete(f"session:{session_id}")
        logger.info("删除会话: session=%s", session_id)
