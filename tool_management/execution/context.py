"""
Abhikarta LLM - Tool Management Framework
Execution Context

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This module provides execution context management for tool operations.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime
import uuid


@dataclass
class ExecutionContext:
    """
    Execution context for tool operations.
    
    Provides a container for passing state and metadata through
    the execution pipeline and middleware chain.
    """
    
    # Unique execution identifier
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Tool information
    tool_name: str = ""
    tool_version: str = ""
    
    # Parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # User/session context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Execution flags
    skip_execution: bool = False
    dry_run: bool = False
    
    # Custom metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Middleware communication
    middleware_data: Dict[str, Any] = field(default_factory=dict)
    
    def set_metadata(self, key: str, value: Any) -> 'ExecutionContext':
        """Set a metadata value"""
        self.metadata[key] = value
        return self
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get a metadata value"""
        return self.metadata.get(key, default)
    
    def set_middleware_data(self, key: str, value: Any) -> 'ExecutionContext':
        """Set middleware-specific data"""
        self.middleware_data[key] = value
        return self
    
    def get_middleware_data(self, key: str, default: Any = None) -> Any:
        """Get middleware-specific data"""
        return self.middleware_data.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            "execution_id": self.execution_id,
            "tool_name": self.tool_name,
            "tool_version": self.tool_version,
            "parameters": self.parameters,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "metadata": self.metadata,
        }
