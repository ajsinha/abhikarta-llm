"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import uuid

class CheckpointManager:
    """Manages execution checkpoints for recovery"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def create_checkpoint(
        self,
        session_id: str,
        state_data: Dict[str, Any],
        description: str = None
    ) -> str:
        """Create a recovery checkpoint"""
        state_id = str(uuid.uuid4())
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO execution_state (
                    state_id, session_id, state_type,
                    state_data, description
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                state_id,
                session_id,
                "checkpoint",
                json.dumps(state_data),
                description
            ))
            conn.commit()
        
        return state_id
    
    def restore_checkpoint(
        self,
        session_id: str,
        checkpoint_id: str = None
    ) -> Optional[Dict]:
        """Restore from specific or latest checkpoint"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            if checkpoint_id:
                cursor.execute("""
                    SELECT state_data FROM execution_state
                    WHERE state_id = ? AND state_type = 'checkpoint'
                """, (checkpoint_id,))
            else:
                cursor.execute("""
                    SELECT state_data FROM execution_state
                    WHERE session_id = ? AND state_type = 'checkpoint'
                    ORDER BY created_at DESC LIMIT 1
                """, (session_id,))
            
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None
    
    def list_checkpoints(self, session_id: str) -> List[Dict]:
        """List all checkpoints for session"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT state_id, created_at, description
                FROM execution_state
                WHERE session_id = ? AND state_type = 'checkpoint'
                ORDER BY created_at DESC
            """, (session_id,))
            
            return [
                {
                    "checkpoint_id": row[0],
                    "created_at": row[1],
                    "description": row[2]
                }
                for row in cursor.fetchall()
            ]
    
    def delete_checkpoint(self, checkpoint_id: str):
        """Delete a specific checkpoint"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM execution_state WHERE state_id = ?
            """, (checkpoint_id,))
            conn.commit()
    
    def cleanup_old_checkpoints(
        self,
        session_id: str,
        keep_latest: int = 5
    ):
        """Keep only the latest N checkpoints"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM execution_state
                WHERE session_id = ? AND state_type = 'checkpoint'
                AND state_id NOT IN (
                    SELECT state_id FROM execution_state
                    WHERE session_id = ? AND state_type = 'checkpoint'
                    ORDER BY created_at DESC
                    LIMIT ?
                )
            """, (session_id, session_id, keep_latest))
            conn.commit()
