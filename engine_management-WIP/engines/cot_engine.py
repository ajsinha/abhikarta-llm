"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from .base_engine import BaseExecutionEngine
from typing import Dict, Any
import json
import uuid

class ChainOfThoughtEngine(BaseExecutionEngine):
    """Chain of Thought reasoning execution"""
    
    def get_mode_name(self) -> str:
        return "cot"
    
    async def execute(self, problem: str, **kwargs) -> Dict[str, Any]:
        """Execute with chain of thought reasoning"""
        self.create_session_record()
        self.update_session_status("running")
        
        try:
            # Generate chain of thought
            cot_prompt = f"""
Think step by step to solve this problem: {problem}

Show your reasoning chain explicitly:
1. First, ...
2. Then, ...
3. Finally, ...

Answer: ...
"""
            response = await self.llm_facade.chat_completion_async(
                messages=[{"role": "user", "content": cot_prompt}]
            )
            
            # Parse thought chain
            thoughts = self._parse_thoughts(response["content"])
            
            # Save thought chain
            chain_id = str(uuid.uuid4())
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO thought_chains (
                        chain_id, session_id, chain_type,
                        thoughts, reasoning_depth
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    chain_id, self.session_id, "sequential",
                    json.dumps(thoughts), len(thoughts)
                ))
                conn.commit()
            
            self.update_session_status("completed")
            return {
                "success": True,
                "thoughts": thoughts,
                "final_answer": response["content"].split("Answer:")[-1].strip(),
                "session_id": self.session_id
            }
        except Exception as e:
            self.update_session_status("failed", str(e))
            return {"success": False, "error": str(e)}
    
    def _parse_thoughts(self, content: str) -> list:
        """Parse thought steps from response"""
        thoughts = []
        lines = content.split("\n")
        for line in lines:
            if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith("-")):
                thoughts.append(line.strip())
        return thoughts
