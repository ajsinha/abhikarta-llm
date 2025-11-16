"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from .base_engine import BaseExecutionEngine
from typing import Dict, Any
import json

class HybridEngine(BaseExecutionEngine):
    """Hybrid execution combining multiple modes"""
    
    def get_mode_name(self) -> str:
        return "hybrid"
    
    async def execute(self, workflow: Dict, **kwargs) -> Dict[str, Any]:
        """Execute hybrid workflow"""
        self.create_session_record()
        self.update_session_status("running")
        
        try:
            results = {}
            
            for step in workflow["steps"]:
                mode = step["mode"]
                config = step.get("config", {})
                
                # Execute based on mode
                if mode == "rag":
                    from .rag_engine import RAGEngine
                    engine = RAGEngine(
                        self.session_id, self.user_id,
                        self.llm_facade, self.tool_registry,
                        self.vector_store, self.db_manager, config
                    )
                    result = await engine.execute(**step["params"])
                
                elif mode == "react":
                    from .react_engine import ReActEngine
                    engine = ReActEngine(
                        self.session_id, self.user_id,
                        self.llm_facade, self.tool_registry,
                        self.vector_store, self.db_manager, config
                    )
                    result = await engine.execute(**step["params"])
                
                elif mode == "tool":
                    from .tool_engine import ToolCallingEngine
                    engine = ToolCallingEngine(
                        self.session_id, self.user_id,
                        self.llm_facade, self.tool_registry,
                        self.vector_store, self.db_manager, config
                    )
                    result = await engine.execute(**step["params"])
                
                results[step["name"]] = result
            
            self.update_session_status("completed")
            return {
                "success": True,
                "results": results,
                "session_id": self.session_id
            }
        except Exception as e:
            self.update_session_status("failed", str(e))
            return {"success": False, "error": str(e)}
