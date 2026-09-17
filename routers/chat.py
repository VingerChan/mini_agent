from __future__ import annotations
import logging
from fastapi import APIRouter, HTTPException
from schemas.chat import ChatRequest, ChatResponse
from llm.client import LLMClient
from agent.agent import Agent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")

SYSTEM_PROMPT = """
你是一个智能助手，你叫Kevin。
你需要：
1.根据用户的提问信息简洁回答
2.使用中文回复
"""
llm_client = LLMClient()
agent = Agent(system_prompt=SYSTEM_PROMPT, llm_client=llm_client)

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    logger.info("收到聊天请求: %s", req.message)
    try:
        reply = await agent.run(req.message)
    except Exception as e:
        logger.exception("调用大模型失败")
        raise HTTPException(status_code=500, detail=str(e))
    return ChatResponse(reply=reply)
