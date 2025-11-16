"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from typing import Dict, Any
from .mode_registry import ModeRegistry
from ..engines.base_engine import BaseExecutionEngine

class ModeFactory:
    """Factory for creating execution engines"""
    
    @staticmethod
    def create_engine(
        mode: str,
        user_id: str,
        llm_facade: Any,
        tool_registry: Any,
        vector_store: Any,
        db_manager: Any,
        config: Dict[str, Any] = None,
        session_id: str = None
    ) -> BaseExecutionEngine:
        """
        Create an execution engine for the specified mode
        
        Args:
            mode: Execution mode name
            user_id: User ID
            llm_facade: LLM facade instance
            tool_registry: Tool registry instance
            vector_store: Vector store instance
            db_manager: Database manager
            config: Configuration dict
            session_id: Optional session ID
        
        Returns:
            Initialized execution engine
        
        Raises:
            ValueError: If mode is not registered
        """
        engine_class = ModeRegistry.get(mode)
        
        if engine_class is None:
            available = ModeRegistry.list_modes()
            raise ValueError(
                f"Unknown execution mode: {mode}. "
                f"Available modes: {', '.join(available)}"
            )
        
        return engine_class(
            session_id=session_id,
            user_id=user_id,
            llm_facade=llm_facade,
            tool_registry=tool_registry,
            vector_store=vector_store,
            db_manager=db_manager,
            config=config or {}
        )
