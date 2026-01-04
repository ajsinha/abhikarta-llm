# Abhikarta SDK API Reference

Complete API reference for both SDK packages.

## SDK Client API

### AbhikartaClient

Main client class for connecting to Abhikarta server.

```python
from abhikarta_client import AbhikartaClient, ClientConfig

# Basic usage
client = AbhikartaClient("http://localhost:5000")

# With configuration
config = ClientConfig(
    base_url="http://localhost:5000",
    api_key="your-api-key",
    timeout=300,
    verify_ssl=True
)
client = AbhikartaClient(config=config)
```

#### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `health_check()` | Check server status | `bool` |
| `get_server_info()` | Get server info | `Dict` |
| `close()` | Close connection | `None` |

#### Sub-clients

| Property | Type | Description |
|----------|------|-------------|
| `agents` | `AgentsClient` | Agent operations |
| `workflows` | `WorkflowsClient` | Workflow operations |
| `swarms` | `SwarmsClient` | Swarm operations |
| `organizations` | `OrganizationsClient` | AI Org operations |
| `scripts` | `ScriptsClient` | Script operations |

### AgentsClient

```python
# List agents
agents = client.agents.list()
agents = client.agents.list(agent_type="react")

# Get agent
agent = client.agents.get("agent-id")

# Create agent
agent = client.agents.create(
    name="My Agent",
    agent_type="react",      # react, goal, reflect, hierarchical
    model="llama3.2:3b",
    provider="ollama",
    system_prompt="You are helpful.",
    tools=["tool1", "tool2"]
)

# Execute agent
result = client.agents.execute("agent-id", prompt="Hello")

# Delete agent
client.agents.delete("agent-id")
```

### WorkflowsClient

```python
# List workflows
workflows = client.workflows.list()

# Create workflow
workflow = client.workflows.create(
    name="My Workflow",
    nodes=[
        {"id": "input", "name": "Input", "node_type": "input"},
        {"id": "llm", "name": "Process", "node_type": "llm"},
        {"id": "output", "name": "Output", "node_type": "output"}
    ],
    edges=[
        {"source": "input", "target": "llm"},
        {"source": "llm", "target": "output"}
    ]
)

# Execute workflow
result = client.workflows.execute("workflow-id", {"input": "data"})
```

### SwarmsClient

```python
# Create swarm
swarm = client.swarms.create(
    name="My Swarm",
    strategy="collaborative",
    agents=[
        {"role": "coordinator", "name": "Lead"},
        {"role": "worker", "name": "Worker"}
    ]
)

# Execute swarm
result = client.swarms.execute("swarm-id", task="Analyze data")
```

### OrganizationsClient

```python
# Create organization
org = client.organizations.create(
    name="My Org",
    nodes=[
        {"node_id": "ceo", "role_name": "CEO", "role_type": "executive"},
        {"node_id": "dev", "role_name": "Dev", "role_type": "specialist",
         "parent_node_id": "ceo"}
    ],
    root_node_id="ceo"
)

# Submit task
result = org.submit_task("Task Title", "Task description")
```

---

## SDK Embedded API

### Abhikarta

Main application class for embedded usage.

```python
from abhikarta_embedded import Abhikarta, AbhikartaConfig

# Basic usage
app = Abhikarta()

# With configuration
config = AbhikartaConfig(
    default_provider="ollama",
    default_model="llama3.2:3b",
    ollama_base_url="http://localhost:11434",
    timeout=300
)
app = Abhikarta(config)
```

#### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `configure_provider(name, ...)` | Configure provider | `Abhikarta` |
| `get_provider(name)` | Get provider instance | `BaseProvider` |
| `agent(name)` | Create agent builder | `AgentBuilder` |
| `workflow(name)` | Create workflow builder | `WorkflowBuilder` |
| `swarm(name)` | Create swarm builder | `SwarmBuilder` |
| `organization(name)` | Create org builder | `OrganizationBuilder` |

### Agent

Factory class for creating agents.

```python
from abhikarta_embedded import Agent

# Create agent
agent = Agent.create(
    agent_type="react",    # react, goal, reflect, hierarchical
    name="My Agent",
    model="llama3.2:3b",
    provider="ollama",
    system_prompt="You are helpful.",
    max_iterations=10,
    temperature=0.7
)

# Configure provider
from abhikarta_embedded.providers import Provider
agent.provider = Provider.create("ollama")

# Run agent
result = agent.run("Hello!")
print(result.response)
```

### AgentResult

```python
@dataclass
class AgentResult:
    success: bool          # Whether execution succeeded
    response: str          # Agent's response
    iterations: int        # Number of iterations used
    tool_calls: List[Dict] # Tools that were called
    execution_time: float  # Execution time in seconds
    metadata: Dict         # Additional metadata
```

### Agent Types

| Type | Class | Description |
|------|-------|-------------|
| `react` | `ReActAgent` | Reasoning + Acting pattern |
| `goal` | `GoalAgent` | Goal-oriented planning |
| `reflect` | `ReflectAgent` | Self-improving quality |
| `hierarchical` | `HierarchicalAgent` | Task decomposition |

### Workflow

```python
from abhikarta_embedded import Workflow

workflow = Workflow.create(
    name="My Workflow",
    nodes=[...],
    edges=[...]
)

result = workflow.execute({"input": "data"})
```

### Node Types

| Type | Description |
|------|-------------|
| `input` | Entry point |
| `output` | Exit point |
| `llm` | LLM processing |
| `code` | Python execution |
| `transform` | Data transformation |

### Swarm

```python
from abhikarta_embedded import Swarm

swarm = Swarm.create(
    name="My Swarm",
    strategy="collaborative",
    agents=[...]
)

result = swarm.execute("Task description")
```

### Organization

```python
from abhikarta_embedded import Organization

org = Organization.create(
    name="My Org",
    nodes=[...],
    root_node_id="ceo"
)

result = org.submit_task("Title", "Description")
```

### Providers

```python
from abhikarta_embedded.providers import (
    Provider,
    OllamaProvider,
    OpenAIProvider,
    AnthropicProvider,
    ProviderConfig
)

# Factory method
provider = Provider.create("ollama", base_url="http://localhost:11434")

# Direct instantiation
config = ProviderConfig(
    name="ollama",
    base_url="http://localhost:11434",
    default_model="llama3.2:3b"
)
provider = OllamaProvider(config)

# Usage
response = provider.chat([
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello!"}
])
```

### Tools

```python
from abhikarta_embedded import Tool, BaseTool, ToolRegistry

# Create from function
def my_func(arg: str) -> dict:
    return {"result": arg}

tool = Tool.from_function(my_func, description="My tool")

# Create with class
class MyTool(BaseTool):
    name = "my_tool"
    description = "My custom tool"
    
    def execute(self, **params):
        return {"result": "success"}

# Registry
registry = ToolRegistry()
registry.register(tool)
registry.get("my_tool")
registry.list()
```

### Decorators

```python
from abhikarta_embedded import agent, tool, workflow, swarm, organization

# @tool
@tool(description="Calculate math")
def calculator(expression: str) -> dict:
    return {"result": eval(expression)}

# @agent
@agent(type="react", model="ollama/llama3.2:3b")
class MyAgent:
    system_prompt = "You are helpful."

# Usage
my_agent = MyAgent()
result = my_agent.run("Hello!")
```

---

## Common Patterns

### Error Handling

```python
# SDK Client
import httpx

try:
    result = client.agents.execute("id", prompt="test")
except httpx.HTTPStatusError as e:
    print(f"HTTP Error: {e.response.status_code}")
except httpx.RequestError as e:
    print(f"Connection Error: {e}")

# SDK Embedded
try:
    result = agent.run("Hello")
except ValueError as e:
    print(f"Config error: {e}")
except TimeoutError as e:
    print(f"Timeout: {e}")
```

### Context Managers

```python
# SDK Client
with AbhikartaClient("http://localhost:5000") as client:
    agents = client.agents.list()
    # Connection closed automatically
```

### Async Usage (Client)

```python
import asyncio
from abhikarta_client import AsyncAbhikartaClient

async def main():
    async with AsyncAbhikartaClient("http://localhost:5000") as client:
        agents = await client.agents.list()

asyncio.run(main())
```
