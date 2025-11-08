"""
Abhikarta LLM - Tool Management Framework
Custom Tools Example

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This example demonstrates creating advanced custom tools.
"""

import asyncio
import httpx
from typing import List, Dict, Any
from tool_management import (
    ToolRegistry,
    BaseTool,
    ToolParameter,
    ToolResult,
    ToolType,
    ParameterType,
    ExecutionMode
)


class HTTPClientTool(BaseTool):
    """
    HTTP client tool for making API requests.
    
    Demonstrates async execution mode and error handling.
    """
    
    def __init__(self):
        super().__init__(
            name="http_client",
            description="Make HTTP GET requests to external APIs",
            tool_type=ToolType.API,
            execution_mode=ExecutionMode.ASYNC
        )
        
        self.add_parameter(ToolParameter(
            name="url",
            param_type=ParameterType.STRING,
            description="URL to fetch",
            required=True,
            pattern=r"^https?://.*"
        ))
        
        self.add_parameter(ToolParameter(
            name="timeout",
            param_type=ParameterType.NUMBER,
            description="Request timeout in seconds",
            required=False,
            default=30,
            minimum=1,
            maximum=300
        ))
    
    async def execute_async(self, url: str, timeout: float = 30) -> ToolResult:
        """Execute HTTP request"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=timeout)
                response.raise_for_status()
                
                return ToolResult.success_result(
                    data={
                        "status_code": response.status_code,
                        "content": response.text[:1000],  # Truncate
                        "headers": dict(response.headers)
                    },
                    tool_name=self.name
                )
                
        except httpx.TimeoutException:
            return ToolResult.timeout_result(
                timeout_seconds=timeout,
                tool_name=self.name
            )
        except httpx.HTTPError as e:
            return ToolResult.failure_result(
                error=f"HTTP error: {str(e)}",
                error_type="HTTPError",
                tool_name=self.name
            )
        except Exception as e:
            return ToolResult.failure_result(
                error=str(e),
                error_type=type(e).__name__,
                tool_name=self.name
            )


class DataAggregatorTool(BaseTool):
    """
    Tool that aggregates data from multiple sources.
    
    Demonstrates complex parameter structures and nested objects.
    """
    
    def __init__(self):
        super().__init__(
            name="data_aggregator",
            description="Aggregate and combine data from multiple sources",
            tool_type=ToolType.DATA_PROCESSING,
            execution_mode=ExecutionMode.SYNC
        )
        
        self.add_parameter(ToolParameter(
            name="datasets",
            param_type=ParameterType.ARRAY,
            description="List of datasets to aggregate",
            required=True,
            items=ToolParameter(
                name="dataset",
                param_type=ParameterType.OBJECT,
                description="Dataset object",
                properties={
                    "name": ToolParameter(
                        name="name",
                        param_type=ParameterType.STRING,
                        description="Dataset name",
                        required=True
                    ),
                    "values": ToolParameter(
                        name="values",
                        param_type=ParameterType.ARRAY,
                        description="Data values",
                        required=True
                    )
                }
            )
        ))
        
        self.add_parameter(ToolParameter(
            name="operation",
            param_type=ParameterType.STRING,
            description="Aggregation operation",
            required=True,
            enum=["sum", "average", "merge", "count"]
        ))
    
    def execute(
        self,
        datasets: List[Dict[str, Any]],
        operation: str
    ) -> ToolResult:
        """Execute data aggregation"""
        
        try:
            if operation == "sum":
                total = sum(
                    sum(ds["values"]) for ds in datasets
                    if isinstance(ds.get("values"), list)
                )
                result = {"operation": "sum", "result": total}
                
            elif operation == "average":
                all_values = []
                for ds in datasets:
                    if isinstance(ds.get("values"), list):
                        all_values.extend(ds["values"])
                avg = sum(all_values) / len(all_values) if all_values else 0
                result = {"operation": "average", "result": avg}
                
            elif operation == "merge":
                merged = {}
                for ds in datasets:
                    merged[ds["name"]] = ds["values"]
                result = {"operation": "merge", "result": merged}
                
            elif operation == "count":
                total_count = sum(
                    len(ds["values"]) for ds in datasets
                    if isinstance(ds.get("values"), list)
                )
                result = {"operation": "count", "result": total_count}
            
            else:
                return ToolResult.failure_result(
                    error=f"Unknown operation: {operation}",
                    tool_name=self.name
                )
            
            return ToolResult.success_result(data=result, tool_name=self.name)
            
        except Exception as e:
            return ToolResult.failure_result(
                error=str(e),
                error_type=type(e).__name__,
                tool_name=self.name
            )


class ConditionalTool(BaseTool):
    """
    Tool that executes different logic based on conditions.
    
    Demonstrates metadata usage and conditional execution.
    """
    
    def __init__(self):
        super().__init__(
            name="conditional_processor",
            description="Process data conditionally based on rules",
            tool_type=ToolType.DATA_PROCESSING
        )
        
        self.add_parameter(ToolParameter(
            name="value",
            param_type=ParameterType.NUMBER,
            description="Value to process",
            required=True
        ))
        
        self.add_parameter(ToolParameter(
            name="rule",
            param_type=ParameterType.STRING,
            description="Rule to apply",
            required=True,
            enum=["double", "square", "negate", "abs"]
        ))
        
        # Add metadata
        self.set_metadata("version", "2.0")
        self.set_metadata("author", "Tool Team")
        self.add_tag("math")
        self.add_tag("conditional")
    
    def execute(self, value: float, rule: str) -> ToolResult:
        """Execute conditional processing"""
        
        operations = {
            "double": lambda x: x * 2,
            "square": lambda x: x ** 2,
            "negate": lambda x: -x,
            "abs": lambda x: abs(x)
        }
        
        result = operations[rule](value)
        
        return ToolResult.success_result(
            data={
                "original": value,
                "rule": rule,
                "result": result
            },
            tool_name=self.name
        )


async def main():
    """Demonstrate custom tools"""
    
    print("=" * 60)
    print("Custom Tools Example")
    print("=" * 60)
    print()
    
    # Create registry
    registry = ToolRegistry()
    
    # Register custom tools
    print("Registering custom tools...")
    registry.register(HTTPClientTool(), group="networking", tags=["http", "api"])
    registry.register(DataAggregatorTool(), group="data", tags=["aggregation"])
    registry.register(ConditionalTool(), group="processing", tags=["math"])
    print("✓ All tools registered\n")
    
    # Example 1: HTTP Client (commented out as it requires network)
    print("Example 1: HTTP Client Tool")
    print("(Skipped - requires network access)\n")
    
    # Example 2: Data Aggregator
    print("Example 2: Data Aggregator Tool")
    datasets = [
        {"name": "sales_q1", "values": [100, 200, 150]},
        {"name": "sales_q2", "values": [180, 220, 190]}
    ]
    
    result = await registry.execute(
        "data_aggregator",
        datasets=datasets,
        operation="sum"
    )
    
    if result.success:
        print(f"   Operation: {result.data['operation']}")
        print(f"   Result: {result.data['result']}\n")
    
    # Example 3: Conditional Tool
    print("Example 3: Conditional Processor Tool")
    result = await registry.execute(
        "conditional_processor",
        value=5,
        rule="square"
    )
    
    if result.success:
        print(f"   Original: {result.data['original']}")
        print(f"   Rule: {result.data['rule']}")
        print(f"   Result: {result.data['result']}\n")
    
    # Show tool metadata
    print("Example 4: Tool Metadata")
    tool = registry.get("conditional_processor")
    print(f"   Version: {tool.get_metadata('version')}")
    print(f"   Author: {tool.get_metadata('author')}")
    print(f"   Tags: {', '.join(tool._tags)}\n")
    
    # Get schema for LLM
    print("Example 5: Tool Schema Generation")
    schema = tool.get_anthropic_schema()
    print(f"   Name: {schema['name']}")
    print(f"   Description: {schema['description']}")
    print(f"   Parameters: {list(schema['input_schema']['properties'].keys())}\n")
    
    print("=" * 60)
    print("Custom tools examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
