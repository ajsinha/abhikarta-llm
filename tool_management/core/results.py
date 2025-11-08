"""
Abhikarta LLM - Tool Management Framework
Result Handling System

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This module provides comprehensive result handling for tool executions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from .types import ResultStatus


@dataclass
class ToolResult:
    """
    Represents the result of a tool execution.
    
    Provides a standardized structure for returning results from tools,
    including success/failure status, data, error information, and metadata.
    """
    success: bool
    data: Any
    error: Optional[str] = None
    error_type: Optional[str] = None
    status: ResultStatus = ResultStatus.SUCCESS
    
    # Metadata
    execution_time: Optional[float] = None  # seconds
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tool_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Pagination support
    has_more: bool = False
    cursor: Optional[str] = None
    
    def __post_init__(self):
        """Ensure status matches success flag"""
        if not self.success and self.status == ResultStatus.SUCCESS:
            self.status = ResultStatus.FAILURE
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary format.
        
        Returns:
            Dictionary representation of the result
        """
        result = {
            "success": self.success,
            "data": self.data,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat()
        }
        
        if self.error is not None:
            result["error"] = self.error
        if self.error_type is not None:
            result["error_type"] = self.error_type
        if self.execution_time is not None:
            result["execution_time"] = self.execution_time
        if self.tool_name is not None:
            result["tool_name"] = self.tool_name
        if self.metadata:
            result["metadata"] = self.metadata
        if self.has_more:
            result["has_more"] = self.has_more
        if self.cursor is not None:
            result["cursor"] = self.cursor
        
        return result
    
    def to_json(self) -> str:
        """Convert result to JSON string"""
        import json
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def success_result(
        cls,
        data: Any,
        tool_name: Optional[str] = None,
        **kwargs
    ) -> 'ToolResult':
        """
        Create a successful result.
        
        Args:
            data: Result data
            tool_name: Name of the tool that produced this result
            **kwargs: Additional metadata
            
        Returns:
            ToolResult instance indicating success
        """
        return cls(
            success=True,
            data=data,
            status=ResultStatus.SUCCESS,
            tool_name=tool_name,
            metadata=kwargs
        )
    
    @classmethod
    def failure_result(
        cls,
        error: str,
        error_type: Optional[str] = None,
        tool_name: Optional[str] = None,
        **kwargs
    ) -> 'ToolResult':
        """
        Create a failure result.
        
        Args:
            error: Error message
            error_type: Type of error (e.g., 'ValidationError')
            tool_name: Name of the tool that produced this result
            **kwargs: Additional metadata
            
        Returns:
            ToolResult instance indicating failure
        """
        return cls(
            success=False,
            data=None,
            error=error,
            error_type=error_type,
            status=ResultStatus.FAILURE,
            tool_name=tool_name,
            metadata=kwargs
        )
    
    @classmethod
    def timeout_result(
        cls,
        timeout_seconds: float,
        tool_name: Optional[str] = None
    ) -> 'ToolResult':
        """Create a timeout result"""
        return cls(
            success=False,
            data=None,
            error=f"Execution timed out after {timeout_seconds} seconds",
            error_type="TimeoutError",
            status=ResultStatus.TIMEOUT,
            tool_name=tool_name,
            execution_time=timeout_seconds
        )
    
    @classmethod
    def rate_limited_result(
        cls,
        retry_after: Optional[int] = None,
        tool_name: Optional[str] = None
    ) -> 'ToolResult':
        """Create a rate-limited result"""
        error_msg = "Rate limit exceeded"
        if retry_after:
            error_msg += f". Retry after {retry_after} seconds"
        
        metadata = {}
        if retry_after:
            metadata["retry_after"] = retry_after
        
        return cls(
            success=False,
            data=None,
            error=error_msg,
            error_type="RateLimitError",
            status=ResultStatus.RATE_LIMITED,
            tool_name=tool_name,
            metadata=metadata
        )


class ResultAggregator:
    """
    Aggregates results from multiple tool executions.
    
    Useful for batch operations or multi-tool workflows.
    """
    
    def __init__(self):
        self.results: list[ToolResult] = []
    
    def add(self, result: ToolResult) -> 'ResultAggregator':
        """Add a result to the aggregator"""
        self.results.append(result)
        return self
    
    def add_all(self, results: list[ToolResult]) -> 'ResultAggregator':
        """Add multiple results"""
        self.results.extend(results)
        return self
    
    def get_successful(self) -> list[ToolResult]:
        """Get all successful results"""
        return [r for r in self.results if r.success]
    
    def get_failed(self) -> list[ToolResult]:
        """Get all failed results"""
        return [r for r in self.results if not r.success]
    
    def success_rate(self) -> float:
        """Calculate success rate (0.0 to 1.0)"""
        if not self.results:
            return 0.0
        return len(self.get_successful()) / len(self.results)
    
    def total_execution_time(self) -> float:
        """Calculate total execution time across all results"""
        return sum(
            r.execution_time for r in self.results
            if r.execution_time is not None
        )
    
    def to_summary(self) -> Dict[str, Any]:
        """Generate a summary of aggregated results"""
        return {
            "total": len(self.results),
            "successful": len(self.get_successful()),
            "failed": len(self.get_failed()),
            "success_rate": self.success_rate(),
            "total_execution_time": self.total_execution_time(),
            "results": [r.to_dict() for r in self.results]
        }
