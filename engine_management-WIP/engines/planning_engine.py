"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from .base_engine import BaseExecutionEngine
from typing import Dict, Any
import json
import uuid

class PlanningEngine(BaseExecutionEngine):
    """LLM-generated execution planning"""
    
    def get_mode_name(self) -> str:
        return "planning"
    
    async def execute(self, goal: str, **kwargs) -> Dict[str, Any]:
        """Generate and execute a plan"""
        self.create_session_record()
        self.update_session_status("running")
        
        try:
            # Generate plan
            plan = await self._generate_plan(goal)
            
            # Save plan
            plan_id = str(uuid.uuid4())
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO execution_plans (
                        plan_id, session_id, goal, plan_type,
                        plan_structure, total_steps, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    plan_id, self.session_id, goal, plan["type"],
                    json.dumps(plan["steps"]), len(plan["steps"]), "running"
                ))
                conn.commit()
            
            # Execute plan
            results = await self._execute_plan(plan_id, plan)
            
            self.update_session_status("completed")
            return {
                "success": True,
                "plan": plan,
                "results": results,
                "session_id": self.session_id
            }
        except Exception as e:
            self.update_session_status("failed", str(e))
            return {"success": False, "error": str(e)}
    
    async def _generate_plan(self, goal: str) -> Dict:
        """Generate execution plan using LLM"""
        prompt = f"""
Generate a detailed step-by-step plan for: {goal}

Return JSON with:
{{
    "type": "sequential" or "parallel",
    "steps": [
        {{"step": 1, "action": "...", "tool": "...", "inputs": {{}}}}
    ]
}}
"""
        response = await self.llm_facade.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response["content"])
    
    async def _execute_plan(self, plan_id: str, plan: Dict) -> List[Dict]:
        """Execute the generated plan"""
        results = []
        for i, step in enumerate(plan["steps"]):
            result = await self._execute_step(step)
            results.append(result)
            
            # Update progress
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE execution_plans
                    SET current_step = ?, step_results = ?
                    WHERE plan_id = ?
                """, (i + 1, json.dumps(results), plan_id))
                conn.commit()
        
        return results
    
    async def _execute_step(self, step: Dict) -> Dict:
        """Execute a single plan step"""
        if "tool" in step:
            result = await self.tool_registry.execute(
                step["tool"], **step.get("inputs", {})
            )
            return {"step": step["step"], "result": result.data}
        else:
            return {"step": step["step"], "result": "completed"}
