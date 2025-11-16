"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from typing import Any, Dict, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.callbacks.base import BaseCallbackHandler

class LangChainAdapter:
    """Adapter for LangChain integration"""
    
    def __init__(self, llm_facade, db_manager):
        self.llm_facade = llm_facade
        self.db_manager = db_manager
    
    def to_langchain_messages(self, messages: List[Dict]) -> List[BaseMessage]:
        """Convert messages to LangChain format"""
        lc_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            elif role == "system":
                lc_messages.append(SystemMessage(content=content))
        
        return lc_messages
    
    def from_langchain_messages(self, messages: List[BaseMessage]) -> List[Dict]:
        """Convert from LangChain format"""
        converted = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            elif isinstance(msg, SystemMessage):
                role = "system"
            else:
                continue
            
            converted.append({
                "role": role,
                "content": msg.content
            })
        
        return converted

class ExecutionCallback(BaseCallbackHandler):
    """Callback handler for tracking executions"""
    
    def __init__(self, session_id: str, db_manager):
        self.session_id = session_id
        self.db_manager = db_manager
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        """Track LLM start"""
        pass
    
    def on_llm_end(self, response, **kwargs):
        """Track LLM completion"""
        pass
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs):
        """Track tool execution start"""
        pass
    
    def on_tool_end(self, output: str, **kwargs):
        """Track tool completion"""
        pass
