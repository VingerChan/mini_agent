from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from llm.client import LLMClient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")
llm_client = LLMClient()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    logger.info("收到聊天请求: %s", req.message)
    try:
        messages = [{"role": "user", "content": req.message}]
        reply = await llm_client.chat(messages)
    except Exception as e:
        logger.exception("调用大模型失败")
        raise HTTPException(status_code=500, detail=str(e))
    return ChatResponse(reply=reply)
