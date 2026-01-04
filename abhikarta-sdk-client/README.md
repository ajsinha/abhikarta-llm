# Abhikarta SDK Client

Python SDK for connecting to an Abhikarta-LLM server. Use this when you have Abhikarta-LLM deployed and want to interact with it programmatically.

## Installation

```bash
pip install abhikarta-sdk-client
```

Or install from source:
```bash
cd abhikarta-sdk-client
pip install -e .
```

## Quick Start

```python
from abhikarta_client import AbhikartaClient

# Connect to server
client = AbhikartaClient("http://localhost:5000")

# Check server health
if client.health_check():
    print("Server is running!")

# List all agents
agents = client.agents.list()
for agent in agents:
    print(f"- {agent['name']} ({agent['agent_type']})")

# Execute an agent
result = client.agents.execute(
    agent_id="your-agent-id",
    prompt="What are the latest AI trends?"
)
print(result['response'])
```

## Creating Entities

### Create an Agent

```python
agent = client.agents.create(
    name="Research Assistant",
    agent_type="react",
    model="llama3.2:3b",
    provider="ollama",
    system_prompt="You are a helpful research assistant."
)

# Execute the new agent
result = agent.execute("Research quantum computing")
print(result['response'])
```

### Create a Workflow

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

# Execute workflow
result = workflow.execute({"data": "Sample input data"})
```

### Create a Swarm

```python
swarm = client.swarms.create(
    name="Research Team",
    strategy="collaborative",
    agents=[
        {"role": "coordinator", "name": "Coordinator"},
        {"role": "researcher", "name": "Researcher"},
        {"role": "reviewer", "name": "Reviewer"}
    ]
)

result = swarm.execute("Analyze market trends in AI")
```

### Create an AI Organization

```python
org = client.organizations.create(
    name="Project Team",
    nodes=[
        {"node_id": "director", "role": "executive", "name": "Director"},
        {"node_id": "manager", "role": "manager", "name": "Manager", 
         "parent_id": "director"},
        {"node_id": "analyst", "role": "specialist", "name": "Analyst",
         "parent_id": "manager"}
    ],
    root_node_id="director"
)

result = org.submit_task(
    title="Quarterly Report",
    description="Prepare Q4 financial analysis"
)
```

## Async Support

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

## API Reference

### AbhikartaClient

| Method | Description |
|--------|-------------|
| `health_check()` | Check server status |
| `get_server_info()` | Get server version and info |

### AgentsClient (client.agents)

| Method | Description |
|--------|-------------|
| `list()` | List all agents |
| `get(id)` | Get agent by ID |
| `create(...)` | Create new agent |
| `execute(id, prompt)` | Execute agent |
| `delete(id)` | Delete agent |

### WorkflowsClient (client.workflows)

| Method | Description |
|--------|-------------|
| `list()` | List all workflows |
| `get(id)` | Get workflow by ID |
| `create(...)` | Create new workflow |
| `execute(id, data)` | Execute workflow |
| `delete(id)` | Delete workflow |

### SwarmsClient (client.swarms)

| Method | Description |
|--------|-------------|
| `list()` | List all swarms |
| `get(id)` | Get swarm by ID |
| `create(...)` | Create new swarm |
| `execute(id, task)` | Execute swarm |
| `delete(id)` | Delete swarm |

### OrganizationsClient (client.organizations)

| Method | Description |
|--------|-------------|
| `list()` | List all organizations |
| `get(id)` | Get organization by ID |
| `create(...)` | Create new organization |
| `delete(id)` | Delete organization |

### ScriptsClient (client.scripts)

| Method | Description |
|--------|-------------|
| `list()` | List all scripts |
| `get(id)` | Get script by ID |
| `create(...)` | Create new script |
| `execute(id, data)` | Execute script |
| `delete(id)` | Delete script |

## For Embedded Use

If you want to use Abhikarta without a server (standalone mode), use `abhikarta-sdk-embedded` instead:

```bash
pip install abhikarta-sdk-embedded
```

## License

MIT License - Copyright © 2025-2030 Ashutosh Sinha
