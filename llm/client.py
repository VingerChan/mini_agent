from __future__ import annotations

import logging
from typing import Any

from openai import (
    APIConnectionError,
    APIError,
    APIStatusError,
    AsyncOpenAI,
    RateLimitError,
)

from core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.dashscope_base_url,
        )
        self._model = settings.model

    async def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        logger.info("正在调用大模型: model=%s, 消息数=%d", self._model, len(messages))
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content or ""
            logger.info("大模型回复成功: 长度=%d", len(content))
            return content
        except RateLimitError:
            logger.error("请求频率超限")
            raise
        except APIConnectionError:
            logger.error("无法连接到大模型API")
            raise
        except APIStatusError as e:
            logger.error("大模型API状态错误: %s", e)
            raise
        except APIError as e:
            logger.error("大模型API错误: %s", e)
            raise
