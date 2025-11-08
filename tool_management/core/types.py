"""
Abhikarta LLM - Tool Management Framework
Type Definitions

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This module defines core types and enumerations used throughout the tool framework.
"""

from enum import Enum
from typing import Literal


class ToolType(Enum):
    """
    Categories of tools available in the system.
    
    This enumeration provides a standardized taxonomy for organizing
    and classifying tools based on their primary function.
    """
    API = "api"                              # External API integrations
    COMPUTATION = "computation"              # Computational and mathematical operations
    DATA_PROCESSING = "data_processing"      # Data manipulation and transformation
    COMMUNICATION = "communication"          # Communication services (email, messaging)
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"  # Information retrieval and search
    MCP = "mcp"                             # Model Context Protocol tools
    WORKFLOW = "workflow"                    # Multi-step workflow orchestration
    FILE_SYSTEM = "file_system"             # File operations
    DATABASE = "database"                    # Database operations
    WEB_SCRAPING = "web_scraping"           # Web content extraction
    CUSTOM = "custom"                        # User-defined custom tools


class ExecutionMode(Enum):
    """
    Execution modes for tool operations.
    
    Defines how a tool executes its operations, allowing the framework
    to optimize execution strategies.
    """
    SYNC = "sync"              # Synchronous blocking execution
    ASYNC = "async"            # Asynchronous non-blocking execution
    STREAMING = "streaming"    # Streaming/progressive results
    BATCH = "batch"           # Batch processing mode


class ToolStatus(Enum):
    """Tool availability status"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"
    MAINTENANCE = "maintenance"


class ParameterType(Enum):
    """JSON Schema data types for parameters"""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    NULL = "null"


class ResultStatus(Enum):
    """Result status codes"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"


# Type aliases for clarity
ToolName = str
GroupName = str
ParameterValue = str | int | float | bool | dict | list | None
