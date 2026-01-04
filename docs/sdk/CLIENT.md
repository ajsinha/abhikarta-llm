# Abhikarta SDK Client Guide

## Overview

The SDK Client provides a Python interface to connect to a running Abhikarta-LLM server. It enables programmatic access to all server features including agents, workflows, swarms, and AI organizations.

## Installation

```bash
pip install abhikarta-sdk-client
```

## Quick Start

```python
from abhikarta_client import AbhikartaClient

# Connect to server
client = AbhikartaClient("http://localhost:5000")

# Check connection
if client.health_check():
    print("Connected successfully!")

# List agents
agents = client.agents.list()
for agent in agents:
    print(f"- {agent['name']}")
```

## Authentication

```python
# With API key (if enabled on server)
client = AbhikartaClient(
    "http://localhost:5000",
    api_key="your-api-key"
)

# Full configuration
from abhikarta_client import ClientConfig

config = ClientConfig(
    base_url="http://localhost:5000",
    api_key="your-api-key",
    timeout=300,
    verify_ssl=True
)
client = AbhikartaClient(config=config)
```

## Agents API

### List Agents

```python
# All agents
agents = client.agents.list()

# Filter by type
react_agents = client.agents.list(agent_type="react")
```

### Get Agent

```python
agent = client.agents.get("agent-id")
print(f"Name: {agent.name}")
print(f"Type: {agent.agent_type}")
print(f"Model: {agent.model}")
```

### Create Agent

```python
agent = client.agents.create(
    name="Research Assistant",
    agent_type="react",
    model="llama3.2:3b",
    provider="ollama",
    system_prompt="You are a helpful research assistant.",
    tools=["web_search", "calculator"]
)
```

### Execute Agent

```python
# Using RemoteAgent
result = agent.execute("Research quantum computing trends")
print(result['response'])

# Direct execution by ID
result = client.agents.execute(
    agent_id="agent-id",
    prompt="What is AI?",
    max_iterations=5
)
```

### Update Agent

```python
agent.update(
    name="Updated Name",
    system_prompt="New system prompt"
)
```

### Delete Agent

```python
agent.delete()
# or
client.agents.delete("agent-id")
```

### From Template

```python
# List templates
templates = client.agents.list_templates()

# Create from template
agent = client.agents.create_from_template(
    template_id="react-research-template",
    name="My Research Agent"
)
```

## Workflows API

### Create Workflow

```python
workflow = client.workflows.create(
    name="Data Pipeline",
    nodes=[
        {"id": "input", "name": "Input", "node_type": "input"},
        {"id": "process", "name": "Process", "node_type": "llm",
         "config": {"prompt": "Analyze: {input}"}},
        {"id": "output", "name": "Output", "node_type": "output"}
    ],
    edges=[
        {"source": "input", "target": "process"},
        {"source": "process", "target": "output"}
    ]
)
```

### Execute Workflow

```python
result = workflow.execute({
    "input": "Sample data to analyze"
})
print(result)
```

## Swarms API

### Create Swarm

```python
swarm = client.swarms.create(
    name="Research Team",
    strategy="collaborative",
    agents=[
        {"role": "coordinator", "name": "Team Lead"},
        {"role": "researcher", "name": "Researcher"},
        {"role": "reviewer", "name": "QA Reviewer"}
    ]
)
```

### Execute Swarm

```python
result = swarm.execute("Analyze market trends in AI")
print(result)
```

## Organizations API

### Create Organization

```python
org = client.organizations.create(
    name="Project Team",
    nodes=[
        {"node_id": "ceo", "role_name": "CEO", "role_type": "executive"},
        {"node_id": "manager", "role_name": "Manager", "role_type": "manager",
         "parent_node_id": "ceo"},
        {"node_id": "dev", "role_name": "Developer", "role_type": "specialist",
         "parent_node_id": "manager"}
    ],
    root_node_id="ceo"
)
```

### Submit Task

```python
result = org.submit_task(
    title="Feature Implementation",
    description="Build the user authentication module",
    priority="high"
)
```

## Scripts API (Python Script Mode)

### Create Script

```python
script_content = '''
agent = {
    "name": "Script Agent",
    "agent_type": "react",
    "model": "llama3.2:3b"
}

__export__ = agent

def execute(input_data):
    return {"success": True, "response": "Hello!"}
'''

script = client.scripts.create(
    name="My Script",
    entity_type="agent",
    script_content=script_content
)
```

### Execute Script

```python
result = client.scripts.execute(
    script['id'],
    {"prompt": "Test input"}
)
```

## Async Client

```python
import asyncio
from abhikarta_client import AsyncAbhikartaClient

async def main():
    async with AsyncAbhikartaClient("http://localhost:5000") as client:
        agents = await client.agents.list()
        print(agents)

asyncio.run(main())
```

## Context Manager

```python
with AbhikartaClient("http://localhost:5000") as client:
    agents = client.agents.list()
    # Connection automatically closed on exit
```

## Error Handling

```python
import httpx

try:
    result = client.agents.execute("invalid-id", prompt="test")
except httpx.HTTPStatusError as e:
    print(f"HTTP Error: {e.response.status_code}")
except httpx.RequestError as e:
    print(f"Connection Error: {e}")
```

## Best Practices

1. **Use context managers** for automatic cleanup
2. **Handle errors** appropriately
3. **Set reasonable timeouts** for long-running operations
4. **Use async client** for high-concurrency applications
5. **Cache frequently accessed data** on the client side

## Next Steps

- [SDK Embedded Guide](./EMBEDDED.md) - For standalone usage
- [API Reference](./API_REFERENCE.md) - Complete API docs
