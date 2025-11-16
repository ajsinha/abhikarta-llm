"""
Abhikarta LLM Platform
Multi-Agent Collaboration Example
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""

import asyncio
import sys
sys.path.insert(0, '..')

from engine_management.api import AbhikartaExecutionAPI
from engine_management.database.db_manager import DatabaseManager
import json

async def setup_agents(api):
    """Setup agent definitions in database"""
    
    agents = [
        {
            "agent_id": "researcher_001",
            "name": "Research Agent",
            "description": "Conducts thorough research on topics",
            "agent_type": "researcher",
            "system_prompt": """You are a research specialist. Your job is to:
- Gather comprehensive information on topics
- Verify facts from multiple sources
- Provide detailed, well-sourced insights
Be thorough and cite your sources.""",
            "llm_provider": "anthropic",
            "llm_model": "claude-sonnet-4-20250514"
        },
        {
            "agent_id": "analyst_001",
            "name": "Analysis Agent",
            "description": "Analyzes data and provides insights",
            "agent_type": "analyst",
            "system_prompt": """You are a data analyst. Your job is to:
- Analyze information critically
- Identify patterns and trends
- Provide actionable insights
Be analytical and data-driven.""",
            "llm_provider": "anthropic",
            "llm_model": "claude-sonnet-4-20250514"
        },
        {
            "agent_id": "writer_001",
            "name": "Writing Agent",
            "description": "Creates clear, compelling content",
            "agent_type": "writer",
            "system_prompt": """You are a content writer. Your job is to:
- Transform complex information into clear prose
- Write engaging, accessible content
- Maintain consistent tone and style
Be clear, concise, and engaging.""",
            "llm_provider": "anthropic",
            "llm_model": "claude-sonnet-4-20250514"
        }
    ]
    
    with api.db_manager.get_connection() as conn:
        cursor = conn.cursor()
        for agent in agents:
            cursor.execute("""
                INSERT OR REPLACE INTO agent_definitions (
                    agent_id, name, description, agent_type,
                    system_prompt, llm_provider, llm_model, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent["agent_id"],
                agent["name"],
                agent["description"],
                agent["agent_type"],
                agent["system_prompt"],
                agent["llm_provider"],
                agent["llm_model"],
                1
            ))
        conn.commit()
    
    print("✓ Agents configured")
    return [a["agent_id"] for a in agents]

async def example_collaborative_research():
    """Example: Multiple agents collaborating on research"""
    
    print("="*60)
    print("MULTI-AGENT COLLABORATIVE RESEARCH")
    print("="*60)
    
    # Initialize system
    db_manager = DatabaseManager("examples.db")
    db_manager.initialize_schema("../database/schema.sql")
    
    api = AbhikartaExecutionAPI(db_path="examples.db")
    
    # Setup agents
    agent_ids = await setup_agents(api)
    
    # Task for agents
    task = """
    Research the topic of 'Quantum Computing Applications in Finance'.
    
    Researcher: Find key applications and recent developments
    Analyst: Analyze the market potential and challenges
    Writer: Create a comprehensive summary report
    """
    
    print(f"\n📋 Task: {task}\n")
    
    # Execute multi-agent workflow
    from engine_management.engines.multi_agent_engine import MultiAgentEngine
    
    engine = MultiAgentEngine(
        user_id="demo_user",
        llm_facade=api.llm_facade,
        tool_registry=api.tool_registry,
        db_manager=api.db_manager,
        config={
            "coordination_strategy": "sequential"  # Each agent builds on previous
        }
    )
    
    print("🤖 Executing multi-agent workflow...")
    
    # Note: This would require actual LLM facade implementation
    # result = await engine.execute(
    #     task=task,
    #     agent_ids=agent_ids
    # )
    
    # For demonstration, show the structure
    print("\n📊 Expected Result Structure:")
    demo_result = {
        "success": True,
        "agent_results": [
            {
                "agent_id": "researcher_001",
                "agent_name": "Research Agent",
                "response": "Research findings on quantum computing in finance..."
            },
            {
                "agent_id": "analyst_001",
                "agent_name": "Analysis Agent",
                "response": "Analysis of market potential and challenges..."
            },
            {
                "agent_id": "writer_001",
                "agent_name": "Writing Agent",
                "response": "Final comprehensive report synthesizing all findings..."
            }
        ],
        "final_result": "Synthesized output from all agents"
    }
    
    print(json.dumps(demo_result, indent=2))
    
    # View agent interactions in database
    with api.db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM agent_interactions
        """)
        interaction_count = cursor.fetchone()[0]
    
    print(f"\n✓ Agent interactions logged: {interaction_count}")

async def example_agent_debate():
    """Example: Agents debating different perspectives"""
    
    print("\n" + "="*60)
    print("MULTI-AGENT DEBATE SIMULATION")
    print("="*60)
    
    # Setup debate agents with different perspectives
    debate_agents = [
        {
            "agent_id": "optimist_agent",
            "name": "Optimist Agent",
            "system_prompt": "You are an optimist. Always focus on benefits and opportunities.",
            "agent_type": "debater"
        },
        {
            "agent_id": "skeptic_agent",
            "name": "Skeptic Agent",
            "system_prompt": "You are a skeptic. Always question assumptions and identify risks.",
            "agent_type": "debater"
        },
        {
            "agent_id": "moderator_agent",
            "name": "Moderator Agent",
            "system_prompt": "You are a moderator. Synthesize different viewpoints objectively.",
            "agent_type": "coordinator"
        }
    ]
    
    topic = "Impact of AI on employment in the next decade"
    
    print(f"\n🎯 Debate Topic: {topic}")
    print("\n💭 Agents will present different perspectives...")
    
    # This demonstrates the architecture - actual execution requires LLM facade
    print("\nDemonstration of debate structure:")
    print("1. Optimist presents positive outlook")
    print("2. Skeptic presents concerns")
    print("3. Moderator synthesizes balanced view")

if __name__ == "__main__":
    print("ABHIKARTA MULTI-AGENT EXAMPLES\n")
    
    asyncio.run(example_collaborative_research())
    asyncio.run(example_agent_debate())
    
    print("\n" + "="*60)
    print("✅ Examples completed!")
    print("="*60)
