import pytest
from core.session import SessionManager


@pytest.fixture
def session_manager():
    return SessionManager(redis_url="redis://localhost:6379")


class TestSession:
    @pytest.mark.asyncio
    async def test_save_and_load(self, session_manager):
        session_id = "test_session_save_load"
        messages = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！"},
        ]
        await session_manager.save_history(session_id, messages)
        loaded = await session_manager.get_history(session_id)
        assert loaded == messages
        await session_manager.delete_session(session_id)

    @pytest.mark.asyncio
    async def test_empty_session(self, session_manager):
        session_id = "test_session_nonexistent"
        await session_manager.delete_session(session_id)
        loaded = await session_manager.get_history(session_id)
        assert loaded == []

    @pytest.mark.asyncio
    async def test_session_persistence(self, session_manager):
        session_id = "test_session_persist"
        await session_manager.delete_session(session_id)
        messages1 = [{"role": "user", "content": "第一轮"}, {"role": "assistant", "content": "回复1"}]
        await session_manager.save_history(session_id, messages1)
        messages2 = messages1 + [{"role": "user", "content": "第二轮"}, {"role": "assistant", "content": "回复2"}]
        await session_manager.save_history(session_id, messages2)
        loaded = await session_manager.get_history(session_id)
        assert loaded == messages2
        await session_manager.delete_session(session_id)

    @pytest.mark.asyncio
    async def test_delete_session(self, session_manager):
        session_id = "test_session_delete"
        messages = [{"role": "user", "content": "test"}]
        await session_manager.save_history(session_id, messages)
        await session_manager.delete_session(session_id)
        loaded = await session_manager.get_history(session_id)
        assert loaded == []
