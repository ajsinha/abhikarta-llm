"""
Abhikarta SDK Client Examples
=============================

This file demonstrates how to use the Abhikarta SDK Client
to interact with an Abhikarta-LLM server.

Prerequisites:
    - Abhikarta-LLM server running at http://localhost:5000
    - pip install abhikarta-sdk-client

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

from abhikarta_client import AbhikartaClient


def example_basic_usage():
    """Basic usage example - connecting and listing agents."""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)
    
    # Connect to server
    client = AbhikartaClient("http://localhost:5000")
    
    # Check server health
    if client.health_check():
        print("✓ Server is running!")
    else:
        print("✗ Server is not available")
        return
    
    # List all agents
    agents = client.agents.list()
    print(f"\nFound {len(agents)} agents:")
    for agent in agents[:5]:  # Show first 5
        print(f"  - {agent.get('name', 'Unknown')} ({agent.get('agent_type', 'N/A')})")
    
    client.close()


def example_create_and_execute_agent():
    """Create a new agent and execute it."""
    print("\n" + "=" * 60)
    print("Example 2: Create and Execute Agent")
    print("=" * 60)
    
    with AbhikartaClient("http://localhost:5000") as client:
        # Create a ReAct agent
        agent = client.agents.create(
            name="SDK Demo Agent",
            agent_type="react",
            model="llama3.2:3b",
            provider="ollama",
            system_prompt="You are a helpful assistant. Be concise."
        )
        print(f"✓ Created agent: {agent.name} (ID: {agent.id})")
        
        # Execute the agent
        print("\nExecuting agent with prompt: 'What is Python?'")
        result = agent.execute("What is Python? Answer in one sentence.")
        print(f"Response: {result.get('response', 'No response')[:200]}...")
        
        # Clean up
        agent.delete()
        print("✓ Agent deleted")


def example_workflow_execution():
    """Create and execute a workflow."""
    print("\n" + "=" * 60)
    print("Example 3: Workflow Execution")
    print("=" * 60)
    
    with AbhikartaClient("http://localhost:5000") as client:
        # Define a simple workflow
        workflow = client.workflows.create(
            name="SDK Demo Workflow",
            description="A simple data processing workflow",
            nodes=[
                {
                    "id": "input_node",
                    "name": "Input",
                    "node_type": "input"
                },
                {
                    "id": "llm_node",
                    "name": "Process with LLM",
                    "node_type": "llm",
                    "config": {
                        "prompt": "Summarize this text: {input}",
                        "model": "llama3.2:3b"
                    }
                },
                {
                    "id": "output_node",
                    "name": "Output",
                    "node_type": "output"
                }
            ],
            edges=[
                {"source": "input_node", "target": "llm_node"},
                {"source": "llm_node", "target": "output_node"}
            ]
        )
        print(f"✓ Created workflow: {workflow.name} (ID: {workflow.id})")
        
        # Execute the workflow
        print("\nExecuting workflow...")
        result = workflow.execute({
            "input": "Artificial intelligence is transforming industries worldwide."
        })
        print(f"Workflow result: {result}")
        
        # Clean up
        workflow.delete()
        print("✓ Workflow deleted")


def example_list_templates():
    """List available templates."""
    print("\n" + "=" * 60)
    print("Example 4: List Templates")
    print("=" * 60)
    
    with AbhikartaClient("http://localhost:5000") as client:
        # List agent templates
        agent_templates = client.agents.list_templates()
        print(f"\nAgent Templates ({len(agent_templates)}):")
        for tmpl in agent_templates[:5]:
            print(f"  - {tmpl.get('name', 'Unknown')}: {tmpl.get('description', '')[:50]}...")
        
        # List workflow templates
        workflow_templates = client.workflows.list_templates()
        print(f"\nWorkflow Templates ({len(workflow_templates)}):")
        for tmpl in workflow_templates[:5]:
            print(f"  - {tmpl.get('name', 'Unknown')}: {tmpl.get('description', '')[:50]}...")
        
        # List script templates
        script_templates = client.scripts.list_templates()
        print(f"\nScript Templates ({len(script_templates)}):")
        for tmpl in script_templates[:5]:
            print(f"  - {tmpl.get('name', 'Unknown')}: {tmpl.get('description', '')[:50]}...")


def example_swarm_execution():
    """Create and execute a swarm."""
    print("\n" + "=" * 60)
    print("Example 5: Swarm Execution")
    print("=" * 60)
    
    with AbhikartaClient("http://localhost:5000") as client:
        # Create a swarm
        swarm = client.swarms.create(
            name="SDK Demo Swarm",
            strategy="collaborative",
            agents=[
                {"role": "coordinator", "name": "Team Lead"},
                {"role": "researcher", "name": "Researcher"},
                {"role": "reviewer", "name": "QA Reviewer"}
            ]
        )
        print(f"✓ Created swarm: {swarm.name} (ID: {swarm.id})")
        
        # Execute swarm
        print("\nExecuting swarm with task...")
        result = swarm.execute("Analyze the benefits of remote work")
        print(f"Swarm result: {result}")
        
        # Clean up
        swarm.delete()
        print("✓ Swarm deleted")


def example_ai_organization():
    """Create and use an AI organization."""
    print("\n" + "=" * 60)
    print("Example 6: AI Organization")
    print("=" * 60)
    
    with AbhikartaClient("http://localhost:5000") as client:
        # Create organization
        org = client.organizations.create(
            name="SDK Demo Organization",
            nodes=[
                {
                    "node_id": "ceo",
                    "role_name": "CEO",
                    "role_type": "executive",
                    "description": "Strategic decision maker"
                },
                {
                    "node_id": "tech_lead",
                    "role_name": "Tech Lead",
                    "role_type": "manager",
                    "parent_node_id": "ceo",
                    "description": "Technical oversight"
                },
                {
                    "node_id": "developer",
                    "role_name": "Developer",
                    "role_type": "specialist",
                    "parent_node_id": "tech_lead",
                    "description": "Implementation specialist"
                }
            ],
            root_node_id="ceo"
        )
        print(f"✓ Created organization: {org.name} (ID: {org.id})")
        
        # Submit a task
        print("\nSubmitting task to organization...")
        task_result = org.submit_task(
            title="Feature Implementation",
            description="Implement user authentication module"
        )
        print(f"Task result: {task_result}")
        
        # Clean up
        org.delete()
        print("✓ Organization deleted")


def example_python_scripts():
    """Create and execute Python scripts."""
    print("\n" + "=" * 60)
    print("Example 7: Python Script Mode")
    print("=" * 60)
    
    with AbhikartaClient("http://localhost:5000") as client:
        # Create a simple agent script
        script_content = '''
"""
Simple Agent Script
"""

agent = {
    "name": "SDK Script Agent",
    "agent_type": "react",
    "model": "llama3.2:3b",
    "system_prompt": "You are helpful."
}

__export__ = agent

def execute(input_data):
    prompt = input_data.get("prompt", "Hello")
    return {"success": True, "response": f"Processed: {prompt}"}

def validate():
    return True, "Valid configuration"
'''
        
        script = client.scripts.create(
            name="SDK Demo Script",
            entity_type="agent",
            script_content=script_content,
            description="A demo script created via SDK"
        )
        print(f"✓ Created script: {script.get('name')} (ID: {script.get('id')})")
        
        # Execute the script
        print("\nExecuting script...")
        result = client.scripts.execute(
            script['id'],
            {"prompt": "Test from SDK"}
        )
        print(f"Script result: {result}")
        
        # Clean up
        client.scripts.delete(script['id'])
        print("✓ Script deleted")


def main():
    """Run all examples."""
    print("\n" + "#" * 60)
    print("# Abhikarta SDK Client Examples")
    print("#" * 60)
    
    try:
        example_basic_usage()
        example_create_and_execute_agent()
        example_workflow_execution()
        example_list_templates()
        example_swarm_execution()
        example_ai_organization()
        example_python_scripts()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("Make sure the Abhikarta-LLM server is running at http://localhost:5000")


if __name__ == "__main__":
    main()
