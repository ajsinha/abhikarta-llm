"""
Abhikarta LLM - Tool Management Framework
Custom Exceptions

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This module defines custom exceptions for the tool management framework.
"""


class ToolManagementError(Exception):
    """Base exception for all tool management errors"""
    pass


class ToolNotFoundError(ToolManagementError):
    """Raised when a requested tool is not found in the registry"""
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        super().__init__(f"Tool '{tool_name}' not found in registry")


class ToolDisabledError(ToolManagementError):
    """Raised when attempting to execute a disabled tool"""
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        super().__init__(f"Tool '{tool_name}' is currently disabled")


class ToolRegistrationError(ToolManagementError):
    """Raised when tool registration fails"""
    pass


class ParameterValidationError(ToolManagementError):
    """Raised when parameter validation fails"""
    def __init__(self, message: str, parameter_name: str = None):
        self.parameter_name = parameter_name
        super().__init__(message)


class ToolExecutionError(ToolManagementError):
    """Raised when tool execution fails"""
    def __init__(self, tool_name: str, original_error: Exception = None):
        self.tool_name = tool_name
        self.original_error = original_error
        message = f"Execution failed for tool '{tool_name}'"
        if original_error:
            message += f": {str(original_error)}"
        super().__init__(message)


class ToolTimeoutError(ToolManagementError):
    """Raised when tool execution times out"""
    def __init__(self, tool_name: str, timeout_seconds: float):
        self.tool_name = tool_name
        self.timeout_seconds = timeout_seconds
        super().__init__(
            f"Tool '{tool_name}' execution timeout after {timeout_seconds}s"
        )


class MCPError(ToolManagementError):
    """Base exception for MCP-related errors"""
    pass


class MCPConnectionError(MCPError):
    """Raised when MCP server connection fails"""
    pass


class MCPProtocolError(MCPError):
    """Raised when MCP protocol communication fails"""
    pass


class SchemaValidationError(ToolManagementError):
    """Raised when schema validation fails"""
    pass


class MiddlewareError(ToolManagementError):
    """Raised when middleware execution fails"""
    pass
