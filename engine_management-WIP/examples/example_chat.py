"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


import asyncio
from engine_management.api import AbhikartaExecutionAPI

async def main():
    """Example: Simple chat interaction"""
    
    # Initialize API (assuming you have LLM facade setup)
    api = AbhikartaExecutionAPI(
        db_path="example.db",
        # llm_facade=your_llm_facade,
        # tool_registry=your_tool_registry
    )
    
    # Execute chat
    result = await api.execute_chat(
        user_id="user_123",
        message="What is the capital of France?"
    )
    
    print(f"Response: {result['response']}")
    print(f"Session ID: {result['session_id']}")

if __name__ == "__main__":
    asyncio.run(main())
