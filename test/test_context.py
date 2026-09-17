import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from core.context import ContextManager, MAX_ROUNDS, KEEP_ROUNDS


def _make_mock_response(content: str) -> MagicMock:
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content=content))]
    return response


def _build_history(rounds: int, with_tool_result: bool = False) -> list[dict]:
    history = []
    for i in range(rounds):
        history.append({"role": "user", "content": f"问题{i+1}"})
        if with_tool_result:
            history.append({"role": "assistant", "content": "<tool_call></tool_call>"})
            history.append({"role": "user", "content": f"工具调用结果：\n结果{i+1}"})
        history.append({"role": "assistant", "content": f"回答{i+1}"})
    return history


class TestContextManager:
    @pytest.mark.asyncio
    @patch("core.context.AsyncOpenAI")
    async def test_short_no_summary(self, mock_openai_cls):
        cm = ContextManager()
        history = _build_history(3)
        result = await cm.process_history(history)
        assert result == history
        mock_openai_cls.return_value.chat.completions.create.assert_not_called()

    @pytest.mark.asyncio
    @patch("core.context.AsyncOpenAI")
    async def test_long_triggers_summary(self, mock_openai_cls):
        mock_openai_cls.return_value.chat.completions.create = AsyncMock(
            return_value=_make_mock_response("这是一段测试摘要")
        )
        cm = ContextManager()
        history = _build_history(6)
        result = await cm.process_history(history)
        assert len(result) > 0
        assert result[0]["role"] == "system"
        assert result[0]["content"].startswith("[摘要]")
        assert "测试摘要" in result[0]["content"]
        split_point = (MAX_ROUNDS - KEEP_ROUNDS) * 2
        expected_len = len(history) - split_point + 1
        assert len(result) == expected_len

    @pytest.mark.asyncio
    @patch("core.context.AsyncOpenAI")
    async def test_tool_result_excluded(self, mock_openai_cls):
        cm = ContextManager()
        history = _build_history(3, with_tool_result=True)
        result = await cm.process_history(history)
        assert result == history
        mock_openai_cls.return_value.chat.completions.create.assert_not_called()

    @pytest.mark.asyncio
    @patch("core.context.AsyncOpenAI")
    async def test_existing_summary_replaced(self, mock_openai_cls):
        mock_openai_cls.return_value.chat.completions.create = AsyncMock(
            return_value=_make_mock_response("新摘要内容")
        )
        cm = ContextManager()
        history = [
            {"role": "system", "content": "[摘要] 旧摘要"},
            {"role": "user", "content": "问题1"},
            {"role": "assistant", "content": "回答1"},
            {"role": "user", "content": "问题2"},
            {"role": "assistant", "content": "回答2"},
            {"role": "user", "content": "问题3"},
            {"role": "assistant", "content": "回答3"},
            {"role": "user", "content": "问题4"},
            {"role": "assistant", "content": "回答4"},
            {"role": "user", "content": "问题5"},
            {"role": "assistant", "content": "回答5"},
            {"role": "user", "content": "问题6"},
            {"role": "assistant", "content": "回答6"},
        ]
        result = await cm.process_history(history)
        assert result[0]["content"].startswith("[摘要]")
        assert "新摘要内容" in result[0]["content"]
        assert "旧摘要" not in result[0]["content"]
