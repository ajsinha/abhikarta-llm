"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

class StateManager:
    """Manages execution state and checkpoints"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def save_state(
        self,
        session_id: str,
        state_data: Dict[str, Any],
        state_type: str = "snapshot",
        node_name: str = None
    ) -> str:
        """Save execution state"""
        state_id = str(uuid.uuid4())
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO execution_state (
                    state_id, session_id, state_type, state_data, node_name
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                state_id, session_id, state_type,
                json.dumps(state_data), node_name
            ))
            conn.commit()
        
        return state_id
    
    def load_state(self, session_id: str, state_type: str = None) -> Optional[Dict]:
        """Load latest state for session"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            if state_type:
                cursor.execute("""
                    SELECT state_data FROM execution_state
                    WHERE session_id = ? AND state_type = ?
                    ORDER BY created_at DESC LIMIT 1
                """, (session_id, state_type))
            else:
                cursor.execute("""
                    SELECT state_data FROM execution_state
                    WHERE session_id = ?
                    ORDER BY created_at DESC LIMIT 1
                """, (session_id,))
            
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None
    
    def create_checkpoint(self, session_id: str, state_data: Dict) -> str:
        """Create recoverable checkpoint"""
        return self.save_state(session_id, state_data, state_type="checkpoint")
    
    def restore_from_checkpoint(self, session_id: str) -> Optional[Dict]:
        """Restore from latest checkpoint"""
        return self.load_state(session_id, state_type="checkpoint")
