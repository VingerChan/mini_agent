from __future__ import annotations
import logging
from llm.client import LLMClient
from tools.registry import ToolRegistry, ToolCall, parse_llm_output

logger = logging.getLogger(__name__)
MAX_FAILURES = 3

class Agent:
    def __init__(self, system_prompt: str, llm_client: LLMClient, registry: ToolRegistry):
        self.system_prompt = system_prompt
        self.llm_client = llm_client
        self.registry = registry

    async def run(self, user_message: str) -> tuple[str, list[ToolCall]]:
        self.registry.clear_traces()
        messages = [
            {'role': 'system','content': self.system_prompt},
            {'role': 'user','content': user_message},
        ]
        failures = 0
        while True:
            response_text = await self.llm_client.chat(messages)
            logger.info("大模型原始回复: %s", response_text)
            if not response_text.strip():
                logger.warning("大模型返回空回复")
                return "抱歉，我暂时无法回答这个问题，请换个问法试试。", self.registry.get_traces()
            parsed = parse_llm_output(response_text)
            if parsed['type'] == 'answer':
                return parsed['content'], self.registry.get_traces()
            tool_name = parsed['tool']
            tool_args = parsed['args']
            tool_obj = self.registry.get(tool_name)
            if tool_obj is None:
                result = f"工具 {tool_name} 不存在"
                failures += 1
            else:
                try:
                    result = tool_obj.func(**tool_args)
                    failures = 0
                except Exception as e:
                    result = f"工具 {tool_name} 执行出错: {e}"
                    failures += 1
            if failures >= MAX_FAILURES:
                return f"工具连续调用失败 {failures} 次，无法完成任务，请简化问题后重试。", self.registry.get_traces()
            messages.append({"role": "assistant", "content": response_text})
            messages.append({"role": "user", "content": f"工具调用结果：\n{result}"})
