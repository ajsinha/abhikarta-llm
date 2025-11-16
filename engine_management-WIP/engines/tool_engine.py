"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from .base_engine import BaseExecutionEngine
from typing import Dict, Any
import json
import uuid

class ToolCallingEngine(BaseExecutionEngine):
    """Function/Tool calling execution"""
    
    def get_mode_name(self) -> str:
        return "tool"
    
    async def execute(self, user_message: str, available_tools: list = None, **kwargs) -> Dict[str, Any]:
        """Execute with tool calling"""
        self.create_session_record()
        self.update_session_status("running")
        
        try:
            # Get tool schemas
            if available_tools:
                tools = [
                    self.tool_registry.get(tool_name).get_anthropic_schema()
                    for tool_name in available_tools
                ]
            else:
                tools = self.tool_registry.get_all_schemas(format="anthropic")
            
            # Call LLM with tools
            response = await self.llm_facade.chat_completion_with_tools_async(
                messages=[{"role": "user", "content": user_message}],
                tools=tools
            )
            
            # Handle tool calls
            if response.get("tool_calls"):
                tool_results = []
                for tool_call in response["tool_calls"]:
                    result = await self._execute_tool_call(tool_call)
                    tool_results.append(result)
                
                # Continue with tool results
                final_response = await self.llm_facade.chat_completion_async(
                    messages=[
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "tool_calls": response["tool_calls"]},
                        {"role": "tool", "tool_results": tool_results}
                    ]
                )
                
                result = final_response["content"]
            else:
                result = response["content"]
            
            self.save_interaction("user", user_message)
            self.save_interaction("assistant", result)
            
            self.update_session_status("completed")
            return {
                "success": True,
                "response": result,
                "tool_calls": len(response.get("tool_calls", [])),
                "session_id": self.session_id
            }
        except Exception as e:
            self.update_session_status("failed", str(e))
            return {"success": False, "error": str(e)}
    
    async def _execute_tool_call(self, tool_call: Dict) -> Dict:
        """Execute a single tool call"""
        tool_name = tool_call["name"]
        tool_input = json.loads(tool_call["arguments"])
        
        result = await self.tool_registry.execute(tool_name, **tool_input)
        
        return {
            "tool_call_id": tool_call.get("id"),
            "output": result.data
        }
