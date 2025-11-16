"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from .base_engine import BaseExecutionEngine
from typing import Dict, Any, List
import json
import asyncio

class MultiAgentEngine(BaseExecutionEngine):
    """Multi-agent swarm execution"""
    
    def get_mode_name(self) -> str:
        return "multi_agent"
    
    async def execute(self, task: str, agent_ids: List[str], **kwargs) -> Dict[str, Any]:
        """Execute multi-agent collaboration"""
        self.create_session_record()
        self.update_session_status("running")
        
        try:
            agents = self._load_agents(agent_ids)
            results = await asyncio.gather(*[
                self._execute_agent(agent, task) for agent in agents
            ])
            
            # Aggregate results
            final_result = self._aggregate_results(results)
            
            self.update_session_status("completed")
            return {
                "success": True,
                "result": final_result,
                "agent_results": results,
                "session_id": self.session_id
            }
        except Exception as e:
            self.update_session_status("failed", str(e))
            return {"success": False, "error": str(e)}
    
    def _load_agents(self, agent_ids: List[str]) -> List[Dict]:
        """Load agent definitions"""
        agents = []
        with self.db_manager.get_connection() as conn:
            for agent_id in agent_ids:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM agent_definitions WHERE agent_id = ?", (agent_id,))
                agent = dict(cursor.fetchone())
                agents.append(agent)
        return agents
    
    async def _execute_agent(self, agent: Dict, task: str) -> Dict:
        """Execute single agent"""
        prompt = f"{agent['system_prompt']}\n\nTask: {task}"
        response = await self.llm_facade.chat_completion_async(
            messages=[{"role": "user", "content": prompt}]
        )
        return {
            "agent_id": agent["agent_id"],
            "agent_name": agent["name"],
            "response": response["content"]
        }
    
    def _aggregate_results(self, results: List[Dict]) -> str:
        """Aggregate multiple agent results"""
        combined = "\n\n".join([
            f"Agent {r['agent_name']}: {r['response']}" for r in results
        ])
        return f"Combined results from {len(results)} agents:\n\n{combined}"
