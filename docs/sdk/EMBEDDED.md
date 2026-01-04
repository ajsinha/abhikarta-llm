# Abhikarta SDK Embedded Guide

## Overview

The SDK Embedded provides a standalone Python library for building AI agents, workflows, swarms, and organizations without requiring a server. Perfect for notebooks, scripts, CLI tools, and embedded applications.

## Installation

```bash
# Base installation
pip install abhikarta-sdk-embedded

# With specific provider support
pip install abhikarta-sdk-embedded[ollama]
pip install abhikarta-sdk-embedded[openai]
pip install abhikarta-sdk-embedded[anthropic]

# All providers
pip install abhikarta-sdk-embedded[all]
```

## Quick Start

### Method 1: Factory Pattern (Simplest)

```python
from abhikarta_embedded import Agent

# Create agent in one line
agent = Agent.create("react", model="ollama/llama3.2:3b")

# Configure provider
from abhikarta_embedded.providers import Provider
agent.provider = Provider.create("ollama")

# Run
result = agent.run("What is the capital of France?")
print(result.response)
```

### Method 2: Fluent API (More Control)

```python
from abhikarta_embedded import Abhikarta

app = Abhikarta()

agent = (app.agent("Research Assistant")
    .type("react")
    .model("llama3.2:3b")
    .system_prompt("You are a helpful research assistant.")
    .temperature(0.3)
    .build())

result = agent.run("Explain quantum computing")
print(result.response)
```

### Method 3: Decorator Pattern (Most Pythonic)

```python
from abhikarta_embedded import agent, tool

@tool(description="Calculate mathematical expressions")
def calculator(expression: str) -> dict:
    return {"result": eval(expression)}

@agent(type="react", model="ollama/llama3.2:3b")
class MathAgent:
    system_prompt = "You are a math assistant."

my_agent = MathAgent()
result = my_agent.run("What is 15 * 23?")
```

## Agent Types

### ReAct Agent (Reasoning + Acting)

The ReAct agent follows the Reasoning + Acting pattern:
1. **Think**: Analyze the situation
2. **Act**: Execute a tool or action
3. **Observe**: Review results
4. **Repeat**: Until task is complete

```python
from abhikarta_embedded import Agent

agent = Agent.create(
    "react",
    model="llama3.2:3b",
    system_prompt="You are a research assistant.",
    max_iterations=10
)

result = agent.run("Research the history of AI")
print(f"Response: {result.response}")
print(f"Iterations: {result.iterations}")
print(f"Time: {result.execution_time:.2f}s")
```

### Goal Agent (Goal-Oriented Planning)

Creates structured plans with milestones and systematically works toward goals.

```python
agent = Agent.create(
    "goal",
    model="llama3.2:3b",
    system_prompt="You are a project planner."
)

result = agent.run("Plan a marketing campaign launch")
```

### Reflect Agent (Self-Improving Quality)

Iteratively improves output through self-evaluation.

```python
agent = Agent.create(
    "reflect",
    model="llama3.2:3b",
    system_prompt="You are a professional writer."
)

result = agent.run("Write a professional email about project delays")
```

### Hierarchical Agent (Task Decomposition)

Breaks complex tasks into subtasks and delegates to specialists.

```python
agent = Agent.create(
    "hierarchical",
    model="llama3.2:3b",
    max_parallel=3
)

result = agent.run("Create a comprehensive market analysis report")
```

## Workflows

```python
from abhikarta_embedded import Workflow

workflow = Workflow.create(
    name="Text Analysis Pipeline",
    nodes=[
        {"id": "input", "name": "Input", "node_type": "input"},
        {"id": "analyze", "name": "Analyze", "node_type": "llm",
         "config": {"prompt": "Analyze sentiment: {input}"}},
        {"id": "output", "name": "Output", "node_type": "output"}
    ],
    edges=[
        {"source": "input", "target": "analyze"},
        {"source": "analyze", "target": "output"}
    ]
)

from abhikarta_embedded.providers import Provider
workflow.provider = Provider.create("ollama")

result = workflow.execute({"input": "Customer feedback text..."})
```

## Swarms

```python
from abhikarta_embedded import Swarm

swarm = Swarm.create(
    name="Research Team",
    strategy="collaborative",
    agents=[
        {"role": "coordinator", "name": "Team Lead"},
        {"role": "researcher", "name": "Data Researcher"},
        {"role": "reviewer", "name": "Quality Reviewer"}
    ]
)

from abhikarta_embedded.providers import Provider
swarm.provider = Provider.create("ollama")

result = swarm.execute("Analyze market trends in renewable energy")
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

from abhikarta_embedded.providers import Provider
org.provider = Provider.create("ollama")

result = org.submit_task("Feature Implementation", "Build user auth")
```

## Provider Configuration

### Ollama (Default)
```python
from abhikarta_embedded import Abhikarta, AbhikartaConfig

config = AbhikartaConfig(
    default_provider="ollama",
    ollama_base_url="http://localhost:11434",
    default_model="llama3.2:3b"
)
app = Abhikarta(config)
```

### OpenAI
```python
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

## Decorators Reference

### @agent
```python
@agent(type="react", model="ollama/llama3.2:3b")
class MyAgent:
    system_prompt = "You are helpful."
```

### @tool
```python
@tool(description="Calculate math")
def calculator(expression: str) -> dict:
    return {"result": eval(expression)}
```

## Best Practices

1. Configure provider once at application startup
2. Use appropriate agent types for different tasks
3. Set reasonable timeouts and max_iterations
4. Handle errors gracefully
5. Use decorators for cleaner code
