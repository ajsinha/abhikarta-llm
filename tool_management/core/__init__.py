"""
Abhikarta LLM - Tool Management Framework
Core Module

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This module provides the core abstractions and types for the tool management framework.
"""

from .types import (
    ToolType,
    ExecutionMode,
    ToolStatus,
    ParameterType,
    ResultStatus,
    ToolName,
    GroupName,
    ParameterValue
)

from .exceptions import (
    ToolManagementError,
    ToolNotFoundError,
    ToolDisabledError,
    ToolRegistrationError,
    ParameterValidationError,
    ToolExecutionError,
    ToolTimeoutError,
    MCPError,
    MCPConnectionError,
    MCPProtocolError,
    SchemaValidationError,
    MiddlewareError
)

from .parameters import (
    ToolParameter,
    ParameterSet
)

from .results import (
    ToolResult,
    ResultAggregator
)

from .base import BaseTool

__all__ = [
    # Types
    'ToolType',
    'ExecutionMode',
    'ToolStatus',
    'ParameterType',
    'ResultStatus',
    'ToolName',
    'GroupName',
    'ParameterValue',
    
    # Exceptions
    'ToolManagementError',
    'ToolNotFoundError',
    'ToolDisabledError',
    'ToolRegistrationError',
    'ParameterValidationError',
    'ToolExecutionError',
    'ToolTimeoutError',
    'MCPError',
    'MCPConnectionError',
    'MCPProtocolError',
    'SchemaValidationError',
    'MiddlewareError',
    
    # Parameters
    'ToolParameter',
    'ParameterSet',
    
    # Results
    'ToolResult',
    'ResultAggregator',
    
    # Base
    'BaseTool',
]
