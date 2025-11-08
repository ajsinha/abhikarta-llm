"""
Abhikarta LLM - Tool Management Framework
Basic Usage Example

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This example demonstrates basic usage of the tool management framework.
"""

import asyncio
from tool_management import (
    ToolRegistry,
    BaseTool,
    ToolParameter,
    ToolResult,
    ToolType,
    ParameterType,
    ExecutionMode
)
from tool_management.builtin import CalculatorTool, TextAnalyzerTool
from tool_management.execution import logging_middleware, CachingMiddleware


# Example 1: Create a simple custom tool
class GreetingTool(BaseTool):
    """Simple greeting tool"""
    
    def __init__(self):
        super().__init__(
            name="greeting",
            description="Generate personalized greeting messages",
            tool_type=ToolType.CUSTOM,
            execution_mode=ExecutionMode.SYNC
        )
        
        self.add_parameter(ToolParameter(
            name="name",
            param_type=ParameterType.STRING,
            description="Name of the person to greet",
            required=True,
            min_length=1,
            max_length=100
        ))
        
        self.add_parameter(ToolParameter(
            name="greeting_type",
            param_type=ParameterType.STRING,
            description="Type of greeting",
            required=False,
            default="hello",
            enum=["hello", "hi", "greetings", "welcome"]
        ))
    
    def execute(self, name: str, greeting_type: str = "hello") -> ToolResult:
        """Execute greeting generation"""
        
        greetings = {
            "hello": f"Hello, {name}!",
            "hi": f"Hi there, {name}!",
            "greetings": f"Greetings, {name}!",
            "welcome": f"Welcome, {name}!"
        }
        
        message = greetings.get(greeting_type, f"Hello, {name}!")
        
        return ToolResult.success_result(
            data={"message": message, "name": name},
            tool_name=self.name
        )


async def main():
    """Main example function"""
    
    print("=" * 60)
    print("Abhikarta Tool Management Framework - Basic Usage")
    print("=" * 60)
    print()
    
    # Create registry
    print("1. Creating tool registry...")
    registry = ToolRegistry()
    print("   ✓ Registry created\n")
    
    # Register built-in tools
    print("2. Registering built-in tools...")
    calculator = CalculatorTool()
    analyzer = TextAnalyzerTool()
    
    registry.register(calculator, group="computation", tags=["math"])
    registry.register(analyzer, group="text", tags=["nlp", "analysis"])
    print("   ✓ Registered calculator tool")
    print("   ✓ Registered text analyzer tool\n")
    
    # Register custom tool
    print("3. Registering custom tool...")
    greeting = GreetingTool()
    registry.register(greeting, group="utilities", tags=["greeting"])
    print("   ✓ Registered greeting tool\n")
    
    # Add middleware
    print("4. Adding middleware...")
    registry.add_middleware(logging_middleware)
    cache = CachingMiddleware(ttl=60)
    registry.add_middleware(cache)
    print("   ✓ Added logging middleware")
    print("   ✓ Added caching middleware\n")
    
    # Example 1: Use calculator
    print("5. Example: Using calculator tool")
    result = await registry.execute("calculator", expression="sqrt(16) + 10")
    if result.success:
        print(f"   Expression: {result.data['expression']}")
        print(f"   Result: {result.data['result']}")
        print(f"   Execution time: {result.execution_time:.4f}s\n")
    
    # Example 2: Use text analyzer
    print("6. Example: Using text analyzer tool")
    text = "The quick brown fox jumps over the lazy dog"
    result = await registry.execute("text_analyzer", text=text)
    if result.success:
        print(f"   Text: {text}")
        print(f"   Word count: {result.data['word_count']}")
        print(f"   Character count: {result.data['character_count']}")
        print(f"   Unique words: {result.data['unique_words']}\n")
    
    # Example 3: Use greeting tool
    print("7. Example: Using custom greeting tool")
    result = await registry.execute(
        "greeting",
        name="Alice",
        greeting_type="welcome"
    )
    if result.success:
        print(f"   Message: {result.data['message']}\n")
    
    # Example 4: Error handling
    print("8. Example: Error handling")
    result = await registry.execute("calculator", expression="invalid expression")
    if not result.success:
        print(f"   Error detected: {result.error}")
        print(f"   Error type: {result.error_type}\n")
    
    # Example 5: List tools
    print("9. Listing all registered tools:")
    for tool in registry.list_all():
        print(f"   - {tool.name}: {tool.description}")
    print()
    
    # Example 6: Get tool statistics
    print("10. Tool statistics:")
    stats = calculator.get_stats()
    print(f"   Calculator executions: {stats['execution_count']}")
    print(f"   Average execution time: {stats['average_execution_time']:.4f}s\n")
    
    # Example 7: Registry statistics
    print("11. Registry statistics:")
    reg_stats = registry.get_statistics()
    print(f"   Total tools: {reg_stats['total_tools']}")
    print(f"   Total groups: {reg_stats['total_groups']}")
    print(f"   Total executions: {reg_stats['total_executions']}\n")
    
    # Example 8: Get schemas for LLM
    print("12. Getting tool schemas (Anthropic format):")
    schemas = registry.get_all_schemas(format="anthropic")
    print(f"   Generated {len(schemas)} tool schemas")
    print(f"   Example schema for '{schemas[0]['name']}':")
    print(f"   Description: {schemas[0]['description']}\n")
    
    print("=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
