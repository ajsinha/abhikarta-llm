# Abhikarta SDK Embedded

Standalone Python SDK for building AI agents, workflows, swarms, and organizations without requiring a server. Perfect for notebooks, scripts, and embedded applications.

## Installation

```bash
pip install abhikarta-sdk-embedded

# With provider support
pip install abhikarta-sdk-embedded[ollama]
pip install abhikarta-sdk-embedded[openai]
pip install abhikarta-sdk-embedded[all]
```

Or install from source:
```bash
cd abhikarta-sdk-embedded
pip install -e .
```

## Quick Start

### Create an Agent in 3 Lines

```python
from abhikarta_embedded import Agent

agent = Agent.create("react", model="ollama/llama3.2:3b")
result = agent.run("What is the capital of France?")
print(result.response)
```

### Using the Fluent API

```python
from abhikarta_embedded import Abhikarta

app = Abhikarta()

# Build an agent with fluent API
agent = (app.agent("Research Assistant")
    .type("react")
    .model("llama3.2:3b")
    .system_prompt("You are a helpful research assistant.")
    .temperature(0.3)
    .build())

result = agent.run("Research quantum computing trends")
```

### Using Decorators

```python
from abhikarta_embedded import agent, tool

@tool(description="Search the web for information")
def web_search(query: str) -> dict:
    return {"results": ["Result 1", "Result 2"]}

@agent(type="react", model="ollama/llama3.2:3b", tools=[web_search])
class ResearchAgent:
    system_prompt = "You are a research assistant with web search capability."

# Use the agent
my_agent = ResearchAgent()
result = my_agent.run("Find information about AI trends")
```

## Agent Types

### ReAct Agent (Reasoning + Acting)
```python
agent = Agent.create("react", model="ollama/llama3.2:3b")
```

### Goal Agent (Goal-Oriented Planning)
```python
agent = Agent.create("goal", model="ollama/llama3.2:3b")
```

### Reflect Agent (Self-Improving)
```python
agent = Agent.create("reflect", model="ollama/llama3.2:3b")
```

### Hierarchical Agent (Task Decomposition)
```python
agent = Agent.create("hierarchical", model="ollama/llama3.2:3b")
```

## Workflows

```python
from abhikarta_embedded import Workflow

workflow = Workflow.create(
    name="Data Pipeline",
    nodes=[
        {"id": "input", "name": "Input", "node_type": "input"},
        {"id": "process", "name": "Process", "node_type": "llm", 
         "config": {"prompt": "Summarize: {input}"}},
        {"id": "output", "name": "Output", "node_type": "output"}
    ],
    edges=[
        {"source": "input", "target": "process"},
        {"source": "process", "target": "output"}
    ]
)

result = workflow.execute({"input": "Long text to summarize..."})
```

## Swarms

```python
from abhikarta_embedded import Swarm

swarm = Swarm.create(
    name="Research Team",
    strategy="collaborative",
    agents=[
        {"role": "coordinator", "name": "Team Lead"},
        {"role": "researcher", "name": "Researcher"},
        {"role": "reviewer", "name": "QA Reviewer"}
    ]
)

result = swarm.execute("Analyze market trends")
```

## AI Organizations

```python
from abhikarta_embedded import Organization

org = Organization.create(
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

result = org.submit_task("Feature Implementation", "Build user auth module")
```

## Provider Configuration

### Ollama (Default)
```python
app = Abhikarta()
app.configure_provider("ollama", base_url="http://localhost:11434")
```

### OpenAI
```python
from abhikarta_embedded import Abhikarta, AbhikartaConfig

config = AbhikartaConfig(
    default_provider="openai",
    openai_api_key="sk-..."
)
app = Abhikarta(config)
```

### Anthropic
```python
config = AbhikartaConfig(
    default_provider="anthropic",
    anthropic_api_key="sk-ant-..."
)
app = Abhikarta(config)
```

## For Server-Based Usage

If you need persistence, web UI, or multi-user support, use `abhikarta-sdk-client`:

```bash
pip install abhikarta-sdk-client
```

```python
from abhikarta_client import AbhikartaClient

client = AbhikartaClient("http://localhost:5000")
agents = client.agents.list()
```

## License

MIT License - Copyright © 2025-2030 Ashutosh Sinha
