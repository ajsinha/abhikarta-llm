"""
Base Engine for all execution modes
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
import uuid
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class BaseExecutionEngine(ABC):
    """Abstract base class for all execution engines"""
    
    def __init__(
        self,
        session_id: Optional[str] = None,
        user_id: str = None,
        llm_facade: Any = None,
        tool_registry: Any = None,
        vector_store: Any = None,
        db_manager: Any = None,
        config: Optional[Dict] = None
    ):
        """
        Initialize base engine
        
        Args:
            session_id: Execution session ID
            user_id: User initiating execution
            llm_facade: LLM facade instance
            tool_registry: Tool registry instance
            vector_store: Vector store instance
            db_manager: Database manager instance
            config: Configuration dictionary
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.user_id = user_id
        self.llm_facade = llm_facade
        self.tool_registry = tool_registry
        self.vector_store = vector_store
        self.db_manager = db_manager
        self.config = config or {}
        
        self.status = "pending"
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.metadata = {}
        
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute the engine
        
        Returns:
            Dictionary with execution results
        """
        pass
    
    @abstractmethod
    def get_mode_name(self) -> str:
        """
        Get the execution mode name
        
        Returns:
            Mode name string
        """
        pass
    
    def create_session_record(self):
        """Create database record for this session"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO execution_sessions (
                    session_id, user_id, execution_mode, status, configuration,
                    llm_provider, llm_model, llm_config, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.session_id,
                self.user_id,
                self.get_mode_name(),
                self.status,
                json.dumps(self.config),
                getattr(self.llm_facade, "provider", None),
                getattr(self.llm_facade, "model_name", None),
                json.dumps(getattr(self.llm_facade, "config", {})),
                self.created_at.isoformat(),
                json.dumps(self.metadata)
            ))
            conn.commit()
    
    def update_session_status(self, status: str, error: Optional[str] = None):
        """Update session status in database"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            if error:
                cursor.execute("""
                    UPDATE execution_sessions 
                    SET status = ?, error_message = ?, updated_at = ?
                    WHERE session_id = ?
                """, (status, error, datetime.now().isoformat(), self.session_id))
            else:
                cursor.execute("""
                    UPDATE execution_sessions 
                    SET status = ?, updated_at = ?
                    WHERE session_id = ?
                """, (status, datetime.now().isoformat(), self.session_id))
            conn.commit()
    
    def save_interaction(
        self,
        role: str,
        content: str,
        interaction_type: str = "message",
        sequence_number: int = None,
        **kwargs
    ) -> str:
        """Save interaction to database"""
        interaction_id = str(uuid.uuid4())
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get next sequence number if not provided
            if sequence_number is None:
                cursor.execute("""
                    SELECT COALESCE(MAX(sequence_number), 0) + 1
                    FROM interactions WHERE session_id = ?
                """, (self.session_id,))
                sequence_number = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO interactions (
                    interaction_id, session_id, user_id, interaction_type,
                    sequence_number, role, content, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                interaction_id,
                self.session_id,
                self.user_id,
                interaction_type,
                sequence_number,
                role,
                content,
                datetime.now().isoformat(),
                json.dumps(kwargs)
            ))
            conn.commit()
        
        return interaction_id
    
    def get_context_window(self, limit: int = None) -> List[Dict]:
        """Get recent interactions for context"""
        if limit is None:
            limit = self.config.get("context_window_size", 10)
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, content, metadata
                FROM interactions
                WHERE session_id = ?
                ORDER BY sequence_number DESC
                LIMIT ?
            """, (self.session_id, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in reversed(rows)]
