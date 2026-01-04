# Abhikarta-LLM Core Library

**Enterprise AI Agent Orchestration Framework**

The `abhikarta` package is the core library of the Abhikarta-LLM platform, providing the foundational components for building, managing, and orchestrating AI agents, workflows, swarms, and AI organizations.

## Overview

Abhikarta-LLM Core provides:

- **Agent System** - ReAct, Goal-based, Reflect, and Hierarchical agent architectures
- **Workflow Engine** - DAG-based workflow execution with parallel/sequential patterns
- **Swarm Intelligence** - Multi-agent coordination and collaboration
- **AI Organizations** - Hierarchical team structures with delegation
- **Actor System** - Pekko-inspired concurrent processing
- **Tool Framework** - Extensible tool system with 10 base classes
- **LLM Provider Integration** - Ollama, OpenAI, Anthropic, Google, and more
- **Database Layer** - SQLite and PostgreSQL support
- **Notification System** - Slack, Teams, and webhook integrations
- **MCP Support** - Model Context Protocol integration

## Installation

```bash
# Basic installation
pip install abhikarta

# With specific features
pip install abhikarta[postgres]     # PostgreSQL support
pip install abhikarta[openai]       # OpenAI provider
pip install abhikarta[anthropic]    # Anthropic provider
pip install abhikarta[messaging]    # RabbitMQ, Kafka, ActiveMQ
pip install abhikarta[notifications] # Slack, Teams

# All features
pip install abhikarta[all]
```

## Architecture

```
abhikarta-main/
├── src/abhikarta/          # Core Python module
│   ├── actor/              # Pekko-inspired actor system
│   ├── agent/              # Agent management and templates
│   ├── aiorg/              # AI Organization framework
│   ├── config/             # Configuration management
│   ├── core/               # Core utilities and config
│   ├── database/           # Database abstraction layer
│   │   ├── delegates/      # Specialized database delegates
│   │   └── schema/         # SQLite and PostgreSQL schemas
│   ├── hitl/               # Human-in-the-loop management
│   ├── langchain/          # LangChain integration
│   ├── llm/                # LLM adapter layer
│   ├── llm_provider/       # Provider facade
│   ├── mcp/                # Model Context Protocol
│   ├── messaging/          # Message broker integrations
│   ├── notification/       # Notification adapters
│   ├── rbac/               # Role-based access control
│   ├── scripts/            # Python script mode
│   ├── swarm/              # Swarm orchestration
│   ├── tools/              # Tool framework
│   │   └── prebuilt/       # Pre-built tool classes
│   ├── user_management/    # User facade
│   ├── utils/              # Utility functions
│   └── workflow/           # Workflow engine
│
├── entity_definitions/     # JSON entity templates
│   ├── agents/             # Agent templates (12)
│   ├── workflows/          # Workflow templates (22)
│   ├── swarms/             # Swarm templates (5)
│   ├── aiorg/              # AI Org templates (5)
│   └── scripts/            # Script templates (7)
│
├── examples/               # Example code and usage patterns
├── tests/                  # Unit tests
├── pyproject.toml          # Package configuration
└── README.md               # This file
```

## Key Components

### Agent System

```python
from abhikarta.agent import AgentManager, AgentTemplateManager

# Create agent manager
agent_manager = AgentManager(db_facade, llm_facade)

# Load templates
template_manager = AgentTemplateManager()
templates = template_manager.list_templates()
```

### Workflow Engine

```python
from abhikarta.workflow import WorkflowTemplateManager
from abhikarta.workflow.executor import WorkflowExecutor

# Load workflow templates
workflow_manager = WorkflowTemplateManager()

# Execute workflow
executor = WorkflowExecutor(db_facade, llm_facade)
result = await executor.execute(workflow_id, inputs)
```

### Swarm Orchestration

```python
from abhikarta.swarm import SwarmOrchestrator, SwarmTemplateManager

# Load swarm templates
swarm_manager = SwarmTemplateManager()

# Create orchestrator
orchestrator = SwarmOrchestrator(db_facade, llm_facade)
```

### AI Organizations

```python
from abhikarta.aiorg import OrgManager, AIorgTemplateManager

# Load organization templates
aiorg_manager = AIorgTemplateManager()

# Create organization manager
org_manager = OrgManager(db_facade, llm_facade)
```

### Actor System

```python
from abhikarta.actor import ActorSystem, Actor, Props

# Create actor system
system = ActorSystem("my-system")

# Define actor
class MyActor(Actor):
    async def receive(self, message):
        print(f"Received: {message}")

# Create actor
actor_ref = system.actor_of(Props(MyActor), "my-actor")
```

### Tool Framework

```python
from abhikarta.tools import BaseTool, FunctionTool, HTTPTool

# Create custom tool
class MyTool(BaseTool):
    name = "my_tool"
    description = "Does something useful"
    
    def run(self, **kwargs):
        return {"result": "success"}
```

## Database Support

### SQLite (Default)

```python
from abhikarta.database import DatabaseFacade
from abhikarta.config import Settings

settings = Settings()
settings.database.type = "sqlite"
settings.database.sqlite_path = "./data/abhikarta.db"

db = DatabaseFacade(settings)
```

### PostgreSQL

```python
settings = Settings()
settings.database.type = "postgresql"
settings.database.pg_host = "localhost"
settings.database.pg_database = "abhikarta"

db = DatabaseFacade(settings)
```

## Provider Configuration

```python
from abhikarta.llm_provider import LLMFacade
from abhikarta.config import Settings

settings = Settings()
settings.llm.default_provider = "ollama"
settings.llm.default_model = "llama3.2:3b"

llm = LLMFacade(settings, db_facade)
```

## Related Packages

| Package | Description |
|---------|-------------|
| `abhikarta-web` | Web UI and REST API |
| `abhikarta-sdk-client` | Remote API client |
| `abhikarta-sdk-embedded` | Standalone SDK |

## Version History

- **v1.4.8** - Modular SDK architecture, Python Script Mode
- **v1.4.7** - Swarm Designer, AI Organizations
- **v1.4.6** - Notification system, HITL improvements
- **v1.4.5** - MCP integration, tool framework
- **v1.4.0** - Agent types (ReAct, Goal, Reflect, Hierarchical)

## License

Copyright © 2025-2030, All Rights Reserved  
Ashutosh Sinha  
Email: ajsinha@gmail.com

This software is proprietary and confidential.
