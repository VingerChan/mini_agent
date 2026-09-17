import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agent.agent import Agent, MAX_FAILURES
from tools.registry import registry


def _mock_llm(responses: list[str]) -> MagicMock:
    mock = MagicMock()
    mock.chat = AsyncMock(side_effect=responses)
    return mock


SYSTEM_PROMPT = "你是测试助手"


class TestAgent:
    @pytest.mark.asyncio
    @patch("agent.agent.LLMClient")
    async def test_tool_fallback(self, MockLLMClient):
        mock_llm = _mock_llm([
            '<tool_call>\n{"tool": "nonexistent_tool", "args": {}}\n</tool_call>'
        ] * (MAX_FAILURES + 1))
        MockLLMClient.return_value = mock_llm
        agent = Agent(system_prompt=SYSTEM_PROMPT, llm_client=mock_llm, registry=registry)
        reply, traces, history = await agent.run("测试")
        assert "无法完成任务" in reply

    @pytest.mark.asyncio
    @patch("agent.agent.LLMClient")
    async def test_tool_exec_error(self, MockLLMClient):
        call_count = 0

        def side_effect(messages):
            nonlocal call_count
            call_count += 1
            if call_count <= MAX_FAILURES:
                return '<tool_call>\n{"tool": "broken", "args": {}}\n</tool_call>'
            return "最终答案"

        mock_llm = _mock_llm([])
        mock_llm.chat = AsyncMock(side_effect=side_effect)
        MockLLMClient.return_value = mock_llm

        def broken_func(**kwargs):
            raise RuntimeError("工具故障")

        from tools.registry import Tool
        broken_tool = Tool(
            name="broken",
            description="会报错的工具",
            parameters={"type": "object", "properties": {}, "required": []},
            func=broken_func,
        )
        registry.register(broken_tool)

        agent = Agent(system_prompt=SYSTEM_PROMPT, llm_client=mock_llm, registry=registry)
        reply, traces, history = await agent.run("测试")
        assert "无法完成任务" in reply

    @pytest.mark.asyncio
    @patch("agent.agent.LLMClient")
    async def test_empty_response(self, MockLLMClient):
        mock_llm = _mock_llm([""])
        MockLLMClient.return_value = mock_llm
        agent = Agent(system_prompt=SYSTEM_PROMPT, llm_client=mock_llm, registry=registry)
        reply, traces, history = await agent.run("测试")
        assert "抱歉" in reply

    @pytest.mark.asyncio
    @patch("agent.agent.LLMClient")
    async def test_normal_tool_call(self, MockLLMClient):
        mock_llm = _mock_llm([
            '<tool_call>\n{"tool": "calculator", "args": {"expression": "1+1"}}\n</tool_call>',
            "1+1等于2",
        ])
        MockLLMClient.return_value = mock_llm
        agent = Agent(system_prompt=SYSTEM_PROMPT, llm_client=mock_llm, registry=registry)
        reply, traces, history = await agent.run("1+1等于多少")
        assert reply == "1+1等于2"
        assert len(traces) == 1
        assert traces[0].tool_name == "calculator"
        assert traces[0].success is True
