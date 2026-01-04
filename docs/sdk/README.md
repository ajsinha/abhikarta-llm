# Abhikarta SDK Documentation

## Overview

Abhikarta provides two SDK packages for different use cases:

| Package | Use Case | Server Required |
|---------|----------|-----------------|
| `abhikarta-sdk-client` | Connect to deployed Abhikarta server | Yes |
| `abhikarta-sdk-embedded` | Standalone usage without server | No |

## Installation

### SDK Client (Requires Server)

```bash
pip install abhikarta-sdk-client
```

Use this when you have Abhikarta-LLM deployed and want to:
- Access existing agents, workflows, swarms, and organizations
- Share entities across multiple applications
- Use the web UI for management
- Persist configurations in a database

### SDK Embedded (Standalone)

```bash
pip install abhikarta-sdk-embedded

# With provider support
pip install abhikarta-sdk-embedded[ollama]
pip install abhikarta-sdk-embedded[openai]
pip install abhikarta-sdk-embedded[all]
```

Use this when you want to:
- Build AI agents in notebooks or scripts
- Embed AI capabilities in applications
- Run without infrastructure dependencies
- Create quick prototypes

## Quick Comparison

### SDK Client Usage

```python
from abhikarta_client import AbhikartaClient

# Connect to server
client = AbhikartaClient("http://localhost:5000")

# Use existing agent
agent = client.agents.get("research-agent-id")
result = agent.execute("Research AI trends")

# Create new agent (persisted on server)
new_agent = client.agents.create(
    name="My Agent",
    agent_type="react",
    model="llama3.2:3b"
)
```

### SDK Embedded Usage

```python
from abhikarta_embedded import Agent

# Create agent locally
agent = Agent.create("react", model="ollama/llama3.2:3b")
result = agent.run("Research AI trends")

# Or use decorators
from abhikarta_embedded import agent

@agent(type="react", model="ollama/llama3.2:3b")
class MyAgent:
    system_prompt = "You are helpful."

my_agent = MyAgent()
result = my_agent.run("Hello!")
```

## Project Structure

```
abhikarta-llm/
├── abhikarta/                    # Core library
│   ├── agent/                    # Agent management
│   ├── workflow/                 # Workflow engine
│   ├── swarm/                    # Swarm orchestration
│   ├── aiorg/                    # AI Organizations
│   ├── langchain/                # LangChain integration
│   ├── database/                 # Persistence layer
│   └── ...
│
├── abhikarta-web/                # Web UI module
│   └── src/abhikarta_web/
│       ├── routes/               # Flask routes
│       ├── templates/            # Jinja2 templates
│       └── static/               # CSS, JS, images
│
├── abhikarta-sdk-client/         # API Client SDK
│   └── src/abhikarta_client/
│       ├── client.py             # Main client
│       ├── agents.py             # Agents API
│       ├── workflows.py          # Workflows API
│       ├── swarms.py             # Swarms API
│       └── organizations.py      # Organizations API
│
├── abhikarta-sdk-embedded/       # Embedded SDK
│   └── src/abhikarta_embedded/
│       ├── core.py               # Main Abhikarta class
│       ├── agents/               # Agent implementations
│       ├── workflows/            # Workflow engine
│       ├── swarms/               # Swarm engine
│       ├── orgs/                 # Organization engine
│       ├── providers/            # LLM providers
│       ├── tools/                # Tool framework
│       └── decorators.py         # @agent, @tool, etc.
│
├── entity_definitions/           # Entity JSON templates
│   ├── agents/
│   ├── workflows/
│   ├── swarms/
│   ├── aiorg/
│   └── scripts/
│
└── run_server.py                 # Application entry point
```

## Feature Matrix

| Feature | SDK Client | SDK Embedded |
|---------|------------|--------------|
| Agent Types | ✅ All | ✅ All |
| Workflows | ✅ Full DAG | ✅ Basic DAG |
| Swarms | ✅ Full | ✅ Basic |
| AI Organizations | ✅ Full | ✅ Basic |
| Python Script Mode | ✅ | ❌ |
| Template Library | ✅ | ❌ |
| Web UI | ✅ | ❌ |
| Persistence | ✅ Database | ❌ In-memory |
| Multi-user | ✅ | ❌ |
| HITL Integration | ✅ | ❌ |
| Notifications | ✅ Slack/Teams | ❌ |
| MCP Integration | ✅ | ❌ |
| Ollama Provider | ✅ | ✅ |
| OpenAI Provider | ✅ | ✅ |
| Anthropic Provider | ✅ | ✅ |

## Next Steps

- [SDK Client Guide](./CLIENT.md) - Detailed client SDK documentation
- [SDK Embedded Guide](./EMBEDDED.md) - Detailed embedded SDK documentation
- [Provider Configuration](./PROVIDERS.md) - Setting up LLM providers
- [API Reference](./API_REFERENCE.md) - Complete API documentation

## License

MIT License - Copyright © 2025-2030 Ashutosh Sinha
