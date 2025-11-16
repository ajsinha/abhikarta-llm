"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


import pytest
from database.db_manager import DatabaseManager
from state_management.state_manager import StateManager
from state_management.checkpoint_manager import CheckpointManager

@pytest.fixture
def db_manager():
    mgr = DatabaseManager(":memory:")
    mgr.initialize_schema("database/schema.sql")
    return mgr

class TestStateManager:
    """Test state management"""
    
    def test_save_and_load_state(self, db_manager):
        """Test state persistence"""
        mgr = StateManager(db_manager)
        
        test_state = {
            "step": 1,
            "data": {"key": "value"},
            "history": [1, 2, 3]
        }
        
        state_id = mgr.save_state("session_123", test_state)
        assert state_id is not None
        
        loaded_state = mgr.load_state("session_123")
        assert loaded_state == test_state

class TestCheckpointManager:
    """Test checkpoint management"""
    
    def test_create_checkpoint(self, db_manager):
        """Test checkpoint creation"""
        mgr = CheckpointManager(db_manager)
        
        checkpoint_data = {"progress": 50, "current_node": "node_5"}
        
        checkpoint_id = mgr.create_checkpoint(
            "session_123",
            checkpoint_data,
            description="Midpoint checkpoint"
        )
        
        assert checkpoint_id is not None
        
        restored = mgr.restore_checkpoint("session_123", checkpoint_id)
        assert restored == checkpoint_data
    
    def test_list_checkpoints(self, db_manager):
        """Test listing checkpoints"""
        mgr = CheckpointManager(db_manager)
        
        # Create multiple checkpoints
        mgr.create_checkpoint("session_123", {"step": 1})
        mgr.create_checkpoint("session_123", {"step": 2})
        mgr.create_checkpoint("session_123", {"step": 3})
        
        checkpoints = mgr.list_checkpoints("session_123")
        assert len(checkpoints) == 3
