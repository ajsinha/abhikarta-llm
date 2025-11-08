"""
Abhikarta LLM - Tool Management Framework
Built-in Computational Tools

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This module provides built-in computational tools.
"""

import json
import math
from typing import Any, List
from ..core import (
    BaseTool,
    ToolType,
    ExecutionMode,
    ToolResult,
    ToolParameter,
    ParameterType
)


class CalculatorTool(BaseTool):
    """
    Safe mathematical expression evaluator.
    
    Supports basic arithmetic, functions, and constants.
    """
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Evaluate mathematical expressions safely",
            tool_type=ToolType.COMPUTATION,
            execution_mode=ExecutionMode.SYNC
        )
        
        self.add_parameter(ToolParameter(
            name="expression",
            param_type=ParameterType.STRING,
            description="Mathematical expression to evaluate (e.g., '2 + 2', 'sqrt(16)', 'sin(pi/2)')",
            required=True,
            examples=["2 + 2", "sqrt(16)", "10 ** 2"]
        ))
    
    def execute(self, expression: str) -> ToolResult:
        """
        Execute mathematical expression.
        
        Args:
            expression: Math expression string
            
        Returns:
            ToolResult with calculated value
        """
        try:
            # Safe math environment
            safe_dict = {
                "__builtins__": {},
                # Math functions
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "sum": sum,
                "pow": pow,
                # Math module functions
                "sqrt": math.sqrt,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "log": math.log,
                "log10": math.log10,
                "exp": math.exp,
                "floor": math.floor,
                "ceil": math.ceil,
                # Constants
                "pi": math.pi,
                "e": math.e,
            }
            
            result = eval(expression, safe_dict, {})
            
            return ToolResult.success_result(
                data={
                    "expression": expression,
                    "result": result
                },
                tool_name=self.name
            )
            
        except Exception as e:
            return ToolResult.failure_result(
                error=f"Failed to evaluate expression: {str(e)}",
                error_type=type(e).__name__,
                tool_name=self.name
            )


class JSONValidatorTool(BaseTool):
    """Validates and formats JSON data"""
    
    def __init__(self):
        super().__init__(
            name="json_validator",
            description="Validate and format JSON data",
            tool_type=ToolType.DATA_PROCESSING,
            execution_mode=ExecutionMode.SYNC
        )
        
        self.add_parameter(ToolParameter(
            name="json_string",
            param_type=ParameterType.STRING,
            description="JSON string to validate",
            required=True
        ))
        
        self.add_parameter(ToolParameter(
            name="format",
            param_type=ParameterType.BOOLEAN,
            description="Whether to format the JSON",
            default=True
        ))
    
    def execute(self, json_string: str, format: bool = True) -> ToolResult:
        """
        Validate and optionally format JSON.
        
        Args:
            json_string: JSON string to validate
            format: Whether to format the JSON
            
        Returns:
            ToolResult with validation results
        """
        try:
            # Parse JSON
            data = json.loads(json_string)
            
            # Format if requested
            formatted = json.dumps(data, indent=2) if format else json_string
            
            return ToolResult.success_result(
                data={
                    "valid": True,
                    "formatted": formatted,
                    "type": type(data).__name__
                },
                tool_name=self.name
            )
            
        except json.JSONDecodeError as e:
            return ToolResult.failure_result(
                error=f"Invalid JSON: {str(e)}",
                error_type="JSONDecodeError",
                tool_name=self.name
            )


class TextAnalyzerTool(BaseTool):
    """Analyzes text and provides statistics"""
    
    def __init__(self):
        super().__init__(
            name="text_analyzer",
            description="Analyze text and provide statistics",
            tool_type=ToolType.DATA_PROCESSING,
            execution_mode=ExecutionMode.SYNC
        )
        
        self.add_parameter(ToolParameter(
            name="text",
            param_type=ParameterType.STRING,
            description="Text to analyze",
            required=True
        ))
    
    def execute(self, text: str) -> ToolResult:
        """
        Analyze text and return statistics.
        
        Args:
            text: Text to analyze
            
        Returns:
            ToolResult with text statistics
        """
        words = text.split()
        sentences = text.split('.')
        
        stats = {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "average_word_length": sum(len(w) for w in words) / len(words) if words else 0,
            "unique_words": len(set(words))
        }
        
        return ToolResult.success_result(
            data=stats,
            tool_name=self.name
        )
