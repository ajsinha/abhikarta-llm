"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


import asyncio
from engine_management.api import AbhikartaExecutionAPI

async def main():
    """Example: ReAct execution"""
    
    api = AbhikartaExecutionAPI(db_path="example.db")
    
    result = await api.execute_react(
        user_id="user_123",
        goal="Find the current weather in Paris and suggest activities",
        max_iterations=5
    )
    
    print(f"Final Answer: {result['final_answer']}")
    print(f"Iterations: {result['iterations']}")

if __name__ == "__main__":
    asyncio.run(main())
