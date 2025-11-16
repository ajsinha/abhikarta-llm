"""
Abhikarta LLM Platform - react_engine.py
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

Legal Notice:
This module and the associated software architecture are proprietary and confidential.
"""

from .base_engine import BaseExecutionEngine
from typing import Dict, Any
import json
import uuid
import re

class ReActEngine(BaseExecutionEngine):
    """Reasoning and Acting iterative execution"""
    
    def get_mode_name(self) -> str:
        return "react"
    
    async def execute(self, goal: str, max_iterations: int = 10, **kwargs) -> Dict[str, Any]:
        """Execute ReAct loop"""
        self.create_session_record()
        self.update_session_status("running")
        
        try:
            iteration = 0
            final_answer = None
            
            while iteration < max_iterations and not final_answer:
                iteration += 1
                
                # Thought phase
                thought_prompt = self._build_thought_prompt(goal, iteration)
                thought_response = await self.llm_facade.chat_completion_async(
                    messages=[{"role": "user", "content": thought_prompt}],
                    **self.config.get("llm_params", {})
                )
                
                thought = thought_response["content"]
                
                # Parse action
                action, action_input, is_final, answer = self._parse_thought(thought)
                
                # Save cycle
                cycle_id = str(uuid.uuid4())
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO react_cycles (
                            cycle_id, session_id, cycle_number, thought,
                            action, action_input, is_final, final_answer
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        cycle_id, self.session_id, iteration, thought,
                        action, action_input, is_final, answer
                    ))
                    conn.commit()
                
                if is_final:
                    final_answer = answer
                    break
                
                # Execute action (tool call)
                if action and self.tool_registry:
                    observation = await self._execute_tool(action, action_input)
                    
                    # Update cycle with observation
                    with self.db_manager.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE react_cycles SET observation = ?
                            WHERE cycle_id = ?
                        """, (observation, cycle_id))
                        conn.commit()
            
            self.update_session_status("completed")
            
            return {
                "success": True,
                "final_answer": final_answer,
                "iterations": iteration,
                "session_id": self.session_id
            }
            
        except Exception as e:
            self.update_session_status("failed", str(e))
            return {
                "success": False,
                "error": str(e),
                "session_id": self.session_id
            }
    
    def _build_thought_prompt(self, goal: str, iteration: int) -> str:
        """Build prompt for thought phase"""
        return f"""
Goal: {goal}

Iteration: {iteration}

You are a reasoning agent. Think step by step about what to do next.

Format your response as:
Thought: [your reasoning]
Action: [tool name or "Answer"]
Action Input: [tool input or final answer]

If you have enough information to answer, use:
Action: Answer
Action Input: [final answer]
"""
    
    def _parse_thought(self, thought: str):
        """Parse thought into components"""
        action_match = re.search(r"Action:\s*(.+?)\n", thought)
        input_match = re.search(r"Action Input:\s*(.+)", thought, re.DOTALL)
        
        action = action_match.group(1).strip() if action_match else None
        action_input = input_match.group(1).strip() if input_match else None
        
        is_final = action == "Answer" if action else False
        answer = action_input if is_final else None
        
        return action, action_input, is_final, answer
    
    async def _execute_tool(self, tool_name: str, tool_input: str) -> str:
        """Execute a tool and return observation"""
        try:
            result = await self.tool_registry.execute(tool_name, input=tool_input)
            return str(result.data)
        except Exception as e:
            return f"Error executing tool: {str(e)}"
