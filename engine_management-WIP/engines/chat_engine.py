"""
Abhikarta LLM Platform - chat_engine.py
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

Legal Notice:
This module and the associated software architecture are proprietary and confidential.
"""

from .base_engine import BaseExecutionEngine
from typing import Dict, Any, List
import json

class ChatEngine(BaseExecutionEngine):
    """Simple conversational chat execution"""
    
    def get_mode_name(self) -> str:
        return "chat"
    
    async def execute(self, user_message: str, **kwargs) -> Dict[str, Any]:
        """Execute chat interaction"""
        self.create_session_record()
        self.update_session_status("running")
        
        try:
            # Save user message
            self.save_interaction("user", user_message)
            
            # Get context
            context = self.get_context_window()
            
            # Build messages for LLM
            messages = []
            for item in context:
                messages.append({
                    "role": item["role"],
                    "content": item["content"]
                })
            
            # Call LLM
            response = await self.llm_facade.chat_completion_async(
                messages=messages,
                **self.config.get("llm_params", {})
            )
            
            # Save assistant response
            self.save_interaction("assistant", response["content"])
            
            self.update_session_status("completed")
            
            return {
                "success": True,
                "response": response["content"],
                "session_id": self.session_id
            }
            
        except Exception as e:
            self.update_session_status("failed", str(e))
            return {
                "success": False,
                "error": str(e),
                "session_id": self.session_id
            }
