"""
Example Tools for Workflow System

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | Email: ajsinha@gmail.com

This module provides example tools that extend BaseTool for use in workflows.
"""

import time
import random
from typing import Any, Dict
from tool_management.base import BaseTool
from tool_management.types import ToolType, ExecutionMode
from tool_management.parameters import ToolParameter, ParameterType
from tool_management.results import ToolResult


class TextAnalysisTool(BaseTool):
    """Analyzes text and returns statistics"""
    
    def __init__(self):
        super().__init__(
            name="text_analysis",
            description="Analyzes text and provides word count, character count, and sentiment",
            tool_type=ToolType.DATA_PROCESSING,
            execution_mode=ExecutionMode.SYNC,
            version="1.0.0"
        )
        
        # Add parameters
        self.add_parameter(ToolParameter(
            name="text",
            param_type=ParameterType.STRING,
            description="Text to analyze",
            required=True,
            min_length=1,
            max_length=10000
        ))
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute text analysis"""
        text = kwargs.get('text', '')
        
        # Perform analysis
        word_count = len(text.split())
        char_count = len(text)
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        
        # Simple sentiment (mock)
        positive_words = ['good', 'great', 'excellent', 'happy', 'love']
        negative_words = ['bad', 'terrible', 'awful', 'sad', 'hate']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        result_data = {
            "word_count": word_count,
            "character_count": char_count,
            "sentence_count": sentence_count,
            "sentiment": sentiment,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count
        }
        
        return ToolResult.success_result(
            data=result_data,
            tool_name=self.name
        )


class DataTransformTool(BaseTool):
    """Transforms data from one format to another"""
    
    def __init__(self):
        super().__init__(
            name="data_transform",
            description="Transforms data by applying operations like uppercase, lowercase, or reverse",
            tool_type=ToolType.DATA_PROCESSING,
            execution_mode=ExecutionMode.SYNC,
            version="1.0.0"
        )
        
        self.add_parameter(ToolParameter(
            name="input_data",
            param_type=ParameterType.STRING,
            description="Input data to transform",
            required=True
        ))
        
        self.add_parameter(ToolParameter(
            name="operation",
            param_type=ParameterType.STRING,
            description="Operation to perform",
            required=True,
            enum=["uppercase", "lowercase", "reverse", "title"]
        ))
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute data transformation"""
        input_data = kwargs.get('input_data', '')
        operation = kwargs.get('operation', 'uppercase')
        
        if operation == "uppercase":
            output = input_data.upper()
        elif operation == "lowercase":
            output = input_data.lower()
        elif operation == "reverse":
            output = input_data[::-1]
        elif operation == "title":
            output = input_data.title()
        else:
            return ToolResult.failure_result(
                error=f"Unknown operation: {operation}",
                tool_name=self.name
            )
        
        return ToolResult.success_result(
            data={"input": input_data, "output": output, "operation": operation},
            tool_name=self.name
        )


class MathCalculatorTool(BaseTool):
    """Performs mathematical calculations"""
    
    def __init__(self):
        super().__init__(
            name="math_calculator",
            description="Performs basic mathematical operations",
            tool_type=ToolType.COMPUTATION,
            execution_mode=ExecutionMode.SYNC,
            version="1.0.0"
        )
        
        self.add_parameter(ToolParameter(
            name="operation",
            param_type=ParameterType.STRING,
            description="Mathematical operation to perform",
            required=True,
            enum=["add", "subtract", "multiply", "divide", "power", "sqrt"]
        ))
        
        self.add_parameter(ToolParameter(
            name="operand1",
            param_type=ParameterType.NUMBER,
            description="First operand",
            required=True
        ))
        
        self.add_parameter(ToolParameter(
            name="operand2",
            param_type=ParameterType.NUMBER,
            description="Second operand (not required for sqrt)",
            required=False,
            default=0
        ))
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute calculation"""
        operation = kwargs.get('operation')
        operand1 = kwargs.get('operand1')
        operand2 = kwargs.get('operand2', 0)
        
        try:
            if operation == "add":
                result = operand1 + operand2
            elif operation == "subtract":
                result = operand1 - operand2
            elif operation == "multiply":
                result = operand1 * operand2
            elif operation == "divide":
                if operand2 == 0:
                    return ToolResult.failure_result(
                        error="Division by zero",
                        tool_name=self.name
                    )
                result = operand1 / operand2
            elif operation == "power":
                result = operand1 ** operand2
            elif operation == "sqrt":
                if operand1 < 0:
                    return ToolResult.failure_result(
                        error="Cannot calculate square root of negative number",
                        tool_name=self.name
                    )
                result = operand1 ** 0.5
            else:
                return ToolResult.failure_result(
                    error=f"Unknown operation: {operation}",
                    tool_name=self.name
                )
            
            return ToolResult.success_result(
                data={
                    "operation": operation,
                    "operand1": operand1,
                    "operand2": operand2,
                    "result": result
                },
                tool_name=self.name
            )
        except Exception as e:
            return ToolResult.failure_result(
                error=str(e),
                error_type=type(e).__name__,
                tool_name=self.name
            )


class DelaySimulatorTool(BaseTool):
    """Simulates delay for testing parallel execution"""
    
    def __init__(self):
        super().__init__(
            name="delay_simulator",
            description="Simulates a delay for testing purposes",
            tool_type=ToolType.CUSTOM,
            execution_mode=ExecutionMode.SYNC,
            version="1.0.0"
        )
        
        self.add_parameter(ToolParameter(
            name="delay_seconds",
            param_type=ParameterType.NUMBER,
            description="Number of seconds to delay",
            required=True,
            minimum=0,
            maximum=30
        ))
        
        self.add_parameter(ToolParameter(
            name="message",
            param_type=ParameterType.STRING,
            description="Message to return after delay",
            required=False,
            default="Delay completed"
        ))
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute delay"""
        delay = kwargs.get('delay_seconds', 1)
        message = kwargs.get('message', 'Delay completed')
        
        time.sleep(delay)
        
        return ToolResult.success_result(
            data={
                "delayed_seconds": delay,
                "message": message,
                "timestamp": time.time()
            },
            tool_name=self.name
        )


class RandomNumberTool(BaseTool):
    """Generates random numbers"""
    
    def __init__(self):
        super().__init__(
            name="random_number",
            description="Generates random numbers within a specified range",
            tool_type=ToolType.COMPUTATION,
            execution_mode=ExecutionMode.SYNC,
            version="1.0.0"
        )
        
        self.add_parameter(ToolParameter(
            name="min_value",
            param_type=ParameterType.INTEGER,
            description="Minimum value (inclusive)",
            required=False,
            default=1
        ))
        
        self.add_parameter(ToolParameter(
            name="max_value",
            param_type=ParameterType.INTEGER,
            description="Maximum value (inclusive)",
            required=False,
            default=100
        ))
        
        self.add_parameter(ToolParameter(
            name="count",
            param_type=ParameterType.INTEGER,
            description="Number of random numbers to generate",
            required=False,
            default=1,
            minimum=1,
            maximum=100
        ))
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute random number generation"""
        min_value = kwargs.get('min_value', 1)
        max_value = kwargs.get('max_value', 100)
        count = kwargs.get('count', 1)
        
        if min_value > max_value:
            return ToolResult.failure_result(
                error="min_value must be less than or equal to max_value",
                tool_name=self.name
            )
        
        numbers = [random.randint(min_value, max_value) for _ in range(count)]
        
        return ToolResult.success_result(
            data={
                "numbers": numbers,
                "count": count,
                "min": min_value,
                "max": max_value,
                "sum": sum(numbers),
                "average": sum(numbers) / len(numbers)
            },
            tool_name=self.name
        )


class DataValidatorTool(BaseTool):
    """Validates data against rules"""
    
    def __init__(self):
        super().__init__(
            name="data_validator",
            description="Validates data against specified rules",
            tool_type=ToolType.DATA_PROCESSING,
            execution_mode=ExecutionMode.SYNC,
            version="1.0.0"
        )
        
        self.add_parameter(ToolParameter(
            name="value",
            param_type=ParameterType.NUMBER,
            description="Value to validate",
            required=True
        ))
        
        self.add_parameter(ToolParameter(
            name="min_threshold",
            param_type=ParameterType.NUMBER,
            description="Minimum acceptable value",
            required=True
        ))
        
        self.add_parameter(ToolParameter(
            name="max_threshold",
            param_type=ParameterType.NUMBER,
            description="Maximum acceptable value",
            required=True
        ))
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute validation"""
        value = kwargs.get('value')
        min_threshold = kwargs.get('min_threshold')
        max_threshold = kwargs.get('max_threshold')
        
        is_valid = min_threshold <= value <= max_threshold
        
        result_data = {
            "value": value,
            "is_valid": is_valid,
            "min_threshold": min_threshold,
            "max_threshold": max_threshold,
            "validation_result": "PASS" if is_valid else "FAIL"
        }
        
        if not is_valid:
            if value < min_threshold:
                result_data["reason"] = f"Value {value} is below minimum {min_threshold}"
            else:
                result_data["reason"] = f"Value {value} exceeds maximum {max_threshold}"
        
        return ToolResult.success_result(
            data=result_data,
            tool_name=self.name
        )


# Registry of all example tools
EXAMPLE_TOOLS = {
    "text_analysis": TextAnalysisTool,
    "data_transform": DataTransformTool,
    "math_calculator": MathCalculatorTool,
    "delay_simulator": DelaySimulatorTool,
    "random_number": RandomNumberTool,
    "data_validator": DataValidatorTool
}


def get_tool(tool_name: str) -> BaseTool:
    """Get an instance of a tool by name"""
    tool_class = EXAMPLE_TOOLS.get(tool_name)
    if not tool_class:
        raise ValueError(f"Unknown tool: {tool_name}")
    return tool_class()


def list_available_tools() -> Dict[str, str]:
    """List all available example tools"""
    return {
        name: tool_class().description
        for name, tool_class in EXAMPLE_TOOLS.items()
    }
