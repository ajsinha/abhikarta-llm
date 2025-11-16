"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from .base_engine import BaseExecutionEngine
from typing import Dict, Any
import uuid
import asyncio

class HITLEngine(BaseExecutionEngine):
    """Human-in-the-Loop execution"""
    
    def get_mode_name(self) -> str:
        return "hitl"
    
    async def execute(self, task: str, approval_required: bool = True, **kwargs) -> Dict[str, Any]:
        """Execute with human approval gates"""
        self.create_session_record()
        self.update_session_status("running")
        
        try:
            # Generate initial plan
            plan = await self._generate_plan(task)
            
            if approval_required:
                # Request approval
                approved = await self._request_approval(
                    "plan_approval",
                    {"plan": plan, "task": task}
                )
                
                if not approved:
                    self.update_session_status("cancelled")
                    return {"success": False, "reason": "Plan not approved"}
            
            # Execute plan
            result = await self._execute_plan(plan)
            
            self.update_session_status("completed")
            return {
                "success": True,
                "result": result,
                "session_id": self.session_id
            }
        except Exception as e:
            self.update_session_status("failed", str(e))
            return {"success": False, "error": str(e)}
    
    async def _request_approval(self, request_type: str, content: Dict) -> bool:
        """Request human approval"""
        request_id = str(uuid.uuid4())
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO approval_requests (
                    request_id, session_id, request_type,
                    request_content, status
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                request_id, self.session_id, request_type,
                json.dumps(content), "pending"
            ))
            conn.commit()
        
        # Wait for approval (polling)
        timeout = 300  # 5 minutes
        elapsed = 0
        while elapsed < timeout:
            await asyncio.sleep(5)
            elapsed += 5
            
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT status FROM approval_requests
                    WHERE request_id = ?
                """, (request_id,))
                status = cursor.fetchone()[0]
                
                if status == "approved":
                    return True
                elif status == "rejected":
                    return False
        
        return False  # Timeout
    
    async def _generate_plan(self, task: str) -> Dict:
        """Generate plan for task"""
        # Implementation similar to planning engine
        return {"steps": [{"action": "execute_task"}]}
    
    async def _execute_plan(self, plan: Dict) -> Any:
        """Execute approved plan"""
        # Implementation
        return "completed"
