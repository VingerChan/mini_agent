from __future__ import annotations

import logging
from typing import Any

from openai import AsyncOpenAI

from core.config import settings

logger = logging.getLogger(__name__)

MAX_ROUNDS = 5
KEEP_ROUNDS = 2


class ContextManager:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.dashscope_base_url,
        )
        self._model = settings.model_summary

    def _is_summary(self, msg: dict[str, Any]) -> bool:
        return msg.get("role") == "system" and msg.get("content", "").startswith("[摘要]")

    def _is_tool_result(self, msg: dict[str, Any]) -> bool:
        return msg.get("role") == "user" and msg.get("content", "").startswith("工具调用结果：")

    async def process_history(self, history: list[dict[str, Any]]) -> list[dict[str, Any]]:
        clean = [m for m in history if not self._is_summary(m)]

        user_msg_count = sum(1 for m in clean if m.get("role") == "user" and not self._is_tool_result(m))

        if user_msg_count <= MAX_ROUNDS:
            return clean

        split_point = (MAX_ROUNDS - KEEP_ROUNDS) * 2
        to_summarize = clean[:split_point]
        remaining = clean[split_point:]

        summary_text = await self._summarize(to_summarize)

        summary_msg = {"role": "system", "content": f"[摘要] {summary_text}"}
        logger.info(
            "上下文摘要完成: 原始消息数=%d, 摘要消息数=%d, 保留消息数=%d",
            len(clean), len(to_summarize), len(remaining),
        )
        logger.info("摘要内容: %s", summary_text)
        return [summary_msg] + remaining

    async def _summarize(self, messages: list[dict[str, Any]]) -> str:
        prompt = [
            {"role": "system", "content": (
                "请将以下对话内容总结为一段简洁的中文摘要。"
                "要求："
                "1.保留关键信息（用户需求、重要结论）；"
                "2.去掉冗余细节；"
                "3.控制在200字以内。"
                "注意：对话中可能包含工具调用结果和助手思考过程，请一并纳入摘要。"
            )}
        ] + messages

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=prompt,
            temperature=0.3,
            max_tokens=500,
        )
        content = response.choices[0].message.content or ""
        logger.info("摘要生成成功: 长度=%d", len(content))
        return content
