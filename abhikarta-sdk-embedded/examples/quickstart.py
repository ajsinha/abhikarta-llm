"""
Abhikarta SDK Embedded Examples
===============================

Demonstrates standalone usage without a server.

Prerequisites:
    - Ollama running at http://localhost:11434
    - pip install abhikarta-sdk-embedded

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

from abhikarta_embedded import (
    Agent, Abhikarta, AbhikartaConfig,
    Workflow, Swarm, Organization,
    agent, tool
)


def example_simple_agent():
    """Create and run a simple agent."""
    print("=" * 60)
    print("Example 1: Simple Agent")
    print("=" * 60)
    
    # Create agent in one line
    my_agent = Agent.create(
        "react",
        model="llama3.2:3b",
        system_prompt="You are a helpful assistant. Be concise."
    )
    
    # Configure provider
    from abhikarta_embedded.providers import Provider
    my_agent.provider = Provider.create("ollama")
    
    # Run agent
    result = my_agent.run("What is 2 + 2? Answer in one word.")
    print(f"Response: {result.response}")
    print(f"Iterations: {result.iterations}")
    print(f"Time: {result.execution_time:.2f}s")


def example_fluent_api():
    """Use fluent API to build an agent."""
    print("\n" + "=" * 60)
    print("Example 2: Fluent API")
    print("=" * 60)
    
    app = Abhikarta()
    
    # Build agent with fluent API
    agent = (app.agent("Research Bot")
        .type("react")
        .model("llama3.2:3b")
        .system_prompt("You are a research assistant.")
        .temperature(0.3)
        .build())
    
    result = agent.run("What are the main applications of AI?")
    print(f"Response: {result.response[:200]}...")


def example_decorator_api():
    """Use decorators to define agents."""
    print("\n" + "=" * 60)
    print("Example 3: Decorator API")
    print("=" * 60)
    
    @tool(description="Get the current weather")
    def get_weather(location: str) -> dict:
        return {"location": location, "temp": "72°F", "condition": "Sunny"}
    
    @agent(type="react", model="ollama/llama3.2:3b")
    class WeatherAgent:
        system_prompt = "You are a weather assistant."
    
    my_agent = WeatherAgent()
    print(f"Created agent: {my_agent._agent.name}")


def example_different_agent_types():
    """Demonstrate different agent types."""
    print("\n" + "=" * 60)
    print("Example 4: Different Agent Types")
    print("=" * 60)
    
    from abhikarta_embedded.providers import Provider
    provider = Provider.create("ollama")
    
    agent_types = ["react", "goal", "reflect", "hierarchical"]
    
    for agent_type in agent_types:
        agent = Agent.create(agent_type, model="llama3.2:3b")
        agent.provider = provider
        print(f"  - {agent_type.title()}: {agent.name}")


def example_workflow():
    """Create and run a workflow."""
    print("\n" + "=" * 60)
    print("Example 5: Workflow")
    print("=" * 60)
    
    workflow = Workflow.create(
        name="Text Summarizer",
        nodes=[
            {"id": "input", "name": "Input", "node_type": "input"},
            {"id": "summarize", "name": "Summarize", "node_type": "llm",
             "config": {"prompt": "Summarize in one sentence: {input}"}},
            {"id": "output", "name": "Output", "node_type": "output"}
        ],
        edges=[
            {"source": "input", "target": "summarize"},
            {"source": "summarize", "target": "output"}
        ]
    )
    
    # Set provider
    from abhikarta_embedded.providers import Provider
    workflow.provider = Provider.create("ollama")
    
    result = workflow.execute({
        "input": "AI is transforming many industries including healthcare, finance, and transportation."
    })
    print(f"Workflow result: {result.output}")


def example_swarm():
    """Create and run a swarm."""
    print("\n" + "=" * 60)
    print("Example 6: Swarm")
    print("=" * 60)
    
    swarm = Swarm.create(
        name="Analysis Team",
        strategy="collaborative",
        agents=[
            {"role": "researcher", "name": "Data Researcher"},
            {"role": "analyst", "name": "Data Analyst"},
            {"role": "reviewer", "name": "Quality Reviewer"}
        ]
    )
    
    from abhikarta_embedded.providers import Provider
    swarm.provider = Provider.create("ollama")
    
    result = swarm.execute("Analyze the benefits of remote work")
    print(f"Swarm result (truncated): {result.response[:300]}...")


def example_organization():
    """Create and use an AI organization."""
    print("\n" + "=" * 60)
    print("Example 7: AI Organization")
    print("=" * 60)
    
    org = Organization.create(
        name="Project Team",
        nodes=[
            {"node_id": "lead", "role_name": "Team Lead", "role_type": "executive",
             "description": "Strategic oversight"},
            {"node_id": "dev", "role_name": "Developer", "role_type": "specialist",
             "parent_node_id": "lead", "description": "Implementation"}
        ],
        root_node_id="lead"
    )
    
    from abhikarta_embedded.providers import Provider
    org.provider = Provider.create("ollama")
    
    result = org.submit_task(
        title="Code Review",
        description="Review the authentication module"
    )
    print(f"Org result: {result.response[:200]}...")


def example_provider_configuration():
    """Configure different providers."""
    print("\n" + "=" * 60)
    print("Example 8: Provider Configuration")
    print("=" * 60)
    
    # Ollama (local)
    from abhikarta_embedded.providers import OllamaProvider, ProviderConfig
    
    ollama = OllamaProvider(ProviderConfig(
        name="ollama",
        base_url="http://localhost:11434",
        default_model="llama3.2:3b"
    ))
    
    print("Configured Ollama provider")
    
    # Check available models
    try:
        models = ollama.list_models()
        print(f"Available models: {models[:3]}...")
    except Exception as e:
        print(f"Could not list models: {e}")


def main():
    """Run all examples."""
    print("\n" + "#" * 60)
    print("# Abhikarta SDK Embedded Examples")
    print("#" * 60)
    
    try:
        example_simple_agent()
        example_fluent_api()
        example_decorator_api()
        example_different_agent_types()
        example_workflow()
        example_swarm()
        example_organization()
        example_provider_configuration()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("Make sure Ollama is running at http://localhost:11434")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
