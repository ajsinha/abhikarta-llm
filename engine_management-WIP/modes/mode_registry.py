"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from typing import Dict, Type, Optional
from ..engines.base_engine import BaseExecutionEngine

class ModeRegistry:
    """Registry for execution modes"""
    
    _modes: Dict[str, Type[BaseExecutionEngine]] = {}
    
    @classmethod
    def register(cls, mode_name: str, engine_class: Type[BaseExecutionEngine]):
        """Register an execution mode"""
        cls._modes[mode_name] = engine_class
    
    @classmethod
    def get(cls, mode_name: str) -> Optional[Type[BaseExecutionEngine]]:
        """Get engine class for mode"""
        return cls._modes.get(mode_name)
    
    @classmethod
    def list_modes(cls) -> list:
        """List all registered modes"""
        return list(cls._modes.keys())
    
    @classmethod
    def is_registered(cls, mode_name: str) -> bool:
        """Check if mode is registered"""
        return mode_name in cls._modes

# Register default modes
from ..engines.chat_engine import ChatEngine
from ..engines.dag_engine import DAGEngine
from ..engines.react_engine import ReActEngine
from ..engines.rag_engine import RAGEngine

ModeRegistry.register("chat", ChatEngine)
ModeRegistry.register("dag", DAGEngine)
ModeRegistry.register("react", ReActEngine)
ModeRegistry.register("rag", RAGEngine)
