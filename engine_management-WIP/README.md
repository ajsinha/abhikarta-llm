# Abhikarta LLM Execution Platform

**Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)**

## Overview

A comprehensive, production-grade LLM execution system supporting multiple execution modes including Chat, DAG, ReAct, Planning, Autonomous, Human-in-the-Loop, Background, RAG, Chain of Thought, Tool Calling, Multi-Agent, Hybrid, and Event-Driven (Kafka Listening).

## Features

- **14 Execution Modes**: Comprehensive support for all LLM interaction patterns
- **Database-Driven State**: SQLite-based state management and audit trails
- **LangChain/LangGraph Integration**: Seamless integration with popular frameworks
- **Event-Driven Architecture**: Kafka integration for reactive systems
- **Professional Architecture**: Enterprise-grade design patterns and error handling
- **Complete Traceability**: Full audit logging and metrics tracking

## Architecture

```
llm_execution_system/
├── database/           # Database schema and management
├── engines/           # Execution engines for each mode
├── state_management/  # State and checkpoint management
├── integrations/      # LangChain, LangGraph, Kafka
├── config/            # Configuration management
├── examples/          # Usage examples
└── docs/             # Comprehensive documentation
```

## Supported Execution Modes

1. **Chat Mode**: Simple conversational interactions
2. **DAG Mode**: Pre-defined workflow graphs with conditional branching
3. **ReAct Mode**: Reasoning and Acting in iterative cycles
4. **Planning Mode**: LLM-generated execution plans
5. **Autonomous Mode**: Self-directed multi-step execution
6. **Human-in-the-Loop**: Approval gates and human feedback
7. **Background Mode**: Async execution with status tracking
8. **RAG Mode**: Retrieval-Augmented Generation
9. **Chain of Thought**: Explicit reasoning chains
10. **Tool/Function Calling**: Direct tool invocation
11. **Multi-Agent**: Swarm/collaborative agent execution
12. **Hybrid Mode**: Chaining multiple execution patterns
13. **Listening Mode**: Event-driven Kafka execution
14. **Custom**: Extensible for custom patterns

## Quick Start

```python
import asyncio
from llm_execution_system.api import AbhikartaExecutionAPI

# Initialize
api = AbhikartaExecutionAPI(
    db_path="execution.db",
    llm_facade=your_llm_facade,
    tool_registry=your_tool_registry
)

# Execute chat
async def chat_example():
    result = await api.execute_chat(
        user_id="user_123",
        message="Explain quantum computing"
    )
    print(result['response'])

asyncio.run(chat_example())
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from llm_execution_system.database.db_manager import initialize_database; initialize_database()"
```

## Requirements

- Python 3.10+
- SQLite 3
- LangChain
- LangGraph
- kafka-python (optional, for Kafka integration)

## Database Schema

The system uses a comprehensive SQLite database with tables for:
- Execution sessions and interactions
- State management and checkpoints
- DAG definitions and executions
- Agent configurations
- Tool execution logs
- Approval requests
- Background jobs
- RAG collections
- Event processing
- Audit trails

See `database/schema.sql` for complete schema.

## Integration with Existing Components

The system integrates with:
- **LLMFacade**: Unified LLM interface
- **BaseTool**: Tool execution framework
- **ToolRegistry**: Tool management
- **VectorStoreBase**: Vector database operations
- **MCPServerProxy**: MCP server integration
- **PoolManager**: Database connection pooling

## Usage Examples

### Chat Mode
```python
result = await api.execute_chat(
    user_id="user_123",
    message="What is machine learning?"
)
```

### ReAct Mode
```python
result = await api.execute_react(
    user_id="user_123",
    goal="Research and summarize recent AI developments",
    max_iterations=10
)
```

### RAG Mode
```python
result = await api.execute_rag(
    user_id="user_123",
    query="What are the key findings?",
    collection_id="research_papers",
    top_k=5
)
```

### Multi-Agent Mode
```python
from llm_execution_system.engines.multi_agent_engine import MultiAgentEngine

engine = MultiAgentEngine(...)
result = await engine.execute(
    task="Analyze market trends",
    agent_ids=["analyst", "researcher", "critic"]
)
```

## Configuration

Configure via environment variables or `config/settings.py`:

```python
# Database
DATABASE_PATH="llm_execution.db"

# LLM Defaults
DEFAULT_LLM_PROVIDER="anthropic"
DEFAULT_LLM_MODEL="claude-sonnet-4-20250514"

# Execution
MAX_REACT_ITERATIONS=10
APPROVAL_TIMEOUT_SECONDS=300

# Kafka
KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
```

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Usage Guide](docs/USAGE_GUIDE.md)

## License

Copyright © 2025-2030, All Rights Reserved  
Ashutosh Sinha (ajsinha@gmail.com)

This software and the associated architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.

## Support

For questions or issues, contact: ajsinha@gmail.com
