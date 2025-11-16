"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


import pytest
import asyncio
from database.db_manager import DatabaseManager
from engines.chat_engine import ChatEngine
from engines.react_engine import ReActEngine

@pytest.fixture
def db_manager():
    """Create test database"""
    mgr = DatabaseManager(":memory:")
    mgr.initialize_schema("database/schema.sql")
    return mgr

@pytest.fixture
def mock_llm_facade():
    """Mock LLM facade for testing"""
    class MockLLM:
        async def chat_completion_async(self, messages, **kwargs):
            return {
                "content": "Test response",
                "finish_reason": "stop",
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
            }
    return MockLLM()

class TestChatEngine:
    """Test chat engine"""
    
    @pytest.mark.asyncio
    async def test_basic_chat(self, db_manager, mock_llm_facade):
        """Test basic chat execution"""
        engine = ChatEngine(
            user_id="test_user",
            llm_facade=mock_llm_facade,
            db_manager=db_manager
        )
        
        result = await engine.execute("Hello, world!")
        
        assert result["success"] == True
        assert "response" in result
        assert result["session_id"] is not None
    
    @pytest.mark.asyncio
    async def test_session_persistence(self, db_manager, mock_llm_facade):
        """Test session is saved to database"""
        engine = ChatEngine(
            user_id="test_user",
            llm_facade=mock_llm_facade,
            db_manager=db_manager
        )
        
        result = await engine.execute("Test message")
        session_id = result["session_id"]
        
        # Verify session in database
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM execution_sessions WHERE session_id = ?
            """, (session_id,))
            session = cursor.fetchone()
        
        assert session is not None
        assert session["user_id"] == "test_user"
        assert session["execution_mode"] == "chat"

class TestReActEngine:
    """Test ReAct engine"""
    
    @pytest.mark.asyncio
    async def test_react_execution(self, db_manager, mock_llm_facade):
        """Test ReAct loop"""
        from abhikarta_components.registry import ToolRegistry
        
        engine = ReActEngine(
            user_id="test_user",
            llm_facade=mock_llm_facade,
            tool_registry=ToolRegistry(),
            db_manager=db_manager
        )
        
        # This would execute with mocked LLM
        # result = await engine.execute(goal="Test goal", max_iterations=2)
        
        # For now, just test initialization
        assert engine.user_id == "test_user"
        assert engine.get_mode_name() == "react"
