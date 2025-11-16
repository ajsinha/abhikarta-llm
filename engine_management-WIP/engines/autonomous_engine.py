"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from .base_engine import BaseExecutionEngine
from typing import Dict, Any
import json

class AutonomousEngine(BaseExecutionEngine):
    """Self-directed autonomous execution"""
    
    def get_mode_name(self) -> str:
        return "autonomous"
    
    async def execute(
        self,
        objective: str,
        max_iterations: int = 20,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute autonomous loop"""
        self.create_session_record()
        self.update_session_status("running")
        
        try:
            iteration = 0
            completed = False
            history = []
            
            while iteration < max_iterations and not completed:
                iteration += 1
                
                # Decide next action
                action = await self._decide_action(objective, history)
                
                # Execute action
                result = await self._execute_action(action)
                history.append({"action": action, "result": result})
                
                # Check completion
                completed = await self._check_completion(objective, history)
            
            self.update_session_status("completed")
            return {
                "success": True,
                "iterations": iteration,
                "history": history,
                "session_id": self.session_id
            }
        except Exception as e:
            self.update_session_status("failed", str(e))
            return {"success": False, "error": str(e)}
    
    async def _decide_action(self, objective: str, history: list) -> Dict:
        """Decide next action using LLM"""
        prompt = f"""
Objective: {objective}

History: {json.dumps(history[-5:], indent=2)}

Decide the next action. Return JSON:
{{"action_type": "tool" or "analyze", "tool_name": "...", "inputs": {{}}}}
"""
        response = await self.llm_facade.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response["content"])
    
    async def _execute_action(self, action: Dict) -> Any:
        """Execute the decided action"""
        if action["action_type"] == "tool":
            result = await self.tool_registry.execute(
                action["tool_name"], **action.get("inputs", {})
            )
            return result.data
        return "analyzed"
    
    async def _check_completion(self, objective: str, history: list) -> bool:
        """Check if objective is completed"""
        prompt = f"""
Objective: {objective}
History: {json.dumps(history, indent=2)}

Has the objective been completed? Return JSON:
{{"completed": true/false, "reason": "..."}}
"""
        response = await self.llm_facade.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        result = json.loads(response["content"])
        return result.get("completed", False)
