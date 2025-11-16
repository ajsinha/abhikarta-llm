"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from typing import List, Dict, Any

class ContextManager:
    """Manages conversation context and windows"""
    
    def __init__(self, db_manager, window_size: int = 10):
        self.db_manager = db_manager
        self.window_size = window_size
    
    def get_context(
        self,
        session_id: str,
        limit: int = None,
        include_system: bool = False
    ) -> List[Dict]:
        """Get recent context for session"""
        if limit is None:
            limit = self.window_size
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT role, content, metadata
                FROM interactions
                WHERE session_id = ?
            """
            
            if not include_system:
                query += " AND role != 'system'"
            
            query += " ORDER BY sequence_number DESC LIMIT ?"
            
            cursor.execute(query, (session_id, limit))
            rows = cursor.fetchall()
            
            return [
                {
                    "role": row[0],
                    "content": row[1],
                    "metadata": json.loads(row[2]) if row[2] else {}
                }
                for row in reversed(rows)
            ]
    
    def build_messages(
        self,
        session_id: str,
        system_prompt: str = None,
        limit: int = None
    ) -> List[Dict]:
        """Build message list for LLM"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        context = self.get_context(session_id, limit)
        messages.extend(context)
        
        return messages
