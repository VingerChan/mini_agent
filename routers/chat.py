from __future__ import annotations
import logging
from fastapi import APIRouter, HTTPException
from schemas.chat import ChatRequest, ChatResponse
from llm.client import LLMClient
from agent.agent import Agent
from tools.registry import registry

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")

SYSTEM_PROMPT = """
## 身份
- 你是一个智能助手，你叫Kevin。
## 严格指令
1.根据用户的提问信息简洁回答
2.使用中文回复
## 工具调用格式
当你需要使用工具时，必须严格按照以下XML格式输出：
<tool_call>
{"tool": "工具名称", "args": {"参数名": "参数值"}}
</tool_call>

## 可用工具：
- calculator(expression)：计算数学表达式，支持加减乘除
- search(query)：根据关键词搜索信息
- weather(location)：查询指定地区的天气详情

## 工具调用示例
user：1+1等于多少
assistant：<tool_call>
{"tool": "calculator", "args": {"expression": "1+1"}}
</tool_call>

user：今天广州天气怎么样
assistant：<tool_call>
{"tool": "weather", "args": {"location": "广州"}}
</tool_call>

user：搜索Python教程
assistant：<tool_call>
{"tool": "search", "args": {"query": "Python教程"}}
</tool_call>

## 直接回复示例
user：你好
assistant：你好！有什么我可以帮助你的吗？

## 重要
- 如果问题需要使用工具，必须使用上述XML格式调用，禁止直接回答
- 如果问题不需要工具，直接回复即可
"""
llm_client = LLMClient()
agent = Agent(system_prompt=SYSTEM_PROMPT, llm_client=llm_client, registry=registry)

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    logger.info("收到聊天请求: %s", req.message)
    try:
        reply, traces = await agent.run(req.message)
    except Exception as e:
        logger.exception("调用大模型失败")
        raise HTTPException(status_code=500, detail=str(e))
    return ChatResponse(reply=reply, tool_trace=[vars(t) for t in traces])
