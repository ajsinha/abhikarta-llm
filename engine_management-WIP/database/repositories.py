"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import uuid

class SessionRepository:
    """Repository for execution sessions"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def create_session(
        self,
        user_id: str,
        execution_mode: str,
        configuration: Dict = None,
        **kwargs
    ) -> str:
        """Create new execution session"""
        session_id = str(uuid.uuid4())
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO execution_sessions (
                    session_id, user_id, execution_mode, status,
                    configuration, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                user_id,
                execution_mode,
                'pending',
                json.dumps(configuration or {}),
                datetime.now().isoformat(),
                json.dumps(kwargs)
            ))
            conn.commit()
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM execution_sessions WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_session(self, session_id: str, **updates):
        """Update session fields"""
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [session_id]
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE execution_sessions
                SET {set_clause}, updated_at = ?
                WHERE session_id = ?
            """, values + [datetime.now().isoformat()])
            conn.commit()
    
    def list_sessions(
        self,
        user_id: str = None,
        status: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """List sessions with filters"""
        query = "SELECT * FROM execution_sessions WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

class InteractionRepository:
    """Repository for interactions"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def create_interaction(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        **kwargs
    ) -> str:
        """Create new interaction"""
        interaction_id = str(uuid.uuid4())
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get next sequence number
            cursor.execute("""
                SELECT COALESCE(MAX(sequence_number), 0) + 1
                FROM interactions WHERE session_id = ?
            """, (session_id,))
            sequence_number = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO interactions (
                    interaction_id, session_id, user_id, role,
                    content, sequence_number, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                interaction_id,
                session_id,
                user_id,
                role,
                content,
                sequence_number,
                datetime.now().isoformat(),
                json.dumps(kwargs)
            ))
            conn.commit()
        
        return interaction_id
    
    def get_interactions(
        self,
        session_id: str,
        limit: int = None
    ) -> List[Dict]:
        """Get interactions for session"""
        query = """
            SELECT * FROM interactions
            WHERE session_id = ?
            ORDER BY sequence_number
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (session_id,))
            return [dict(row) for row in cursor.fetchall()]

class ToolExecutionRepository:
    """Repository for tool executions"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def create_execution(
        self,
        session_id: str,
        tool_name: str,
        input_parameters: Dict,
        **kwargs
    ) -> str:
        """Create tool execution record"""
        execution_id = str(uuid.uuid4())
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tool_executions (
                    execution_id, session_id, tool_name,
                    input_parameters, status, started_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                execution_id,
                session_id,
                tool_name,
                json.dumps(input_parameters),
                'running',
                datetime.now().isoformat()
            ))
            conn.commit()
        
        return execution_id
    
    def complete_execution(
        self,
        execution_id: str,
        output_result: Any,
        status: str = 'success',
        error: str = None
    ):
        """Mark execution as complete"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tool_executions
                SET status = ?, output_result = ?, error_message = ?,
                    completed_at = ?
                WHERE execution_id = ?
            """, (
                status,
                json.dumps(output_result),
                error,
                datetime.now().isoformat(),
                execution_id
            ))
            conn.commit()
    
    def get_tool_stats(self, tool_name: str = None) -> Dict:
        """Get tool usage statistics"""
        query = """
            SELECT 
                tool_name,
                COUNT(*) as total_executions,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                AVG(execution_time_ms) as avg_time_ms
            FROM tool_executions
        """
        
        params = []
        if tool_name:
            query += " WHERE tool_name = ?"
            params.append(tool_name)
        
        query += " GROUP BY tool_name"
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
