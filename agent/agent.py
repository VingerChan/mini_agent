from __future__ import annotations
from llm.client import LLMClient
class Agent:
    def __init__(self, system_prompt: str, llm_client: LLMClient):
        self.system_prompt = system_prompt
        self.llm_client = llm_client
    async def run(self, user_message: str) -> str:
        messages = [
            {'role': 'system','content': self.system_prompt},
            {'role': 'user','content': user_message},
        ]
        return await self.llm_client.chat(messages)
