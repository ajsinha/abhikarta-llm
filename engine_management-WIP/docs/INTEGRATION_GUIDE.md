# Integration Guide for Abhikarta Components

## Overview

This guide explains how to integrate the Abhikarta LLM Execution System with the existing Abhikarta platform components.

## Provided Components

The `abhikarta_components/` directory contains the following modules:

### Core Components

1. **llm_facade.py** - LLMFacade abstract base class
   - Unified interface for LLM providers (OpenAI, Anthropic, Google, Meta, etc.)
   - Supports chat, streaming, tool calling, vision, embeddings, etc.

2. **base.py** - BaseTool abstract class
   - Base class for all tools in the framework
   - Execution tracking, parameter validation, schema generation

3. **registry.py** - ToolRegistry singleton
   - Central registry for managing all tools
   - Tool discovery, grouping, middleware support

4. **vector_store_base.py** - VectorStoreBase abstract class
   - Unified interface for vector databases
   - Similarity search, MMR, hybrid search, RAG operations

### Supporting Components

5. **pool_manager.py** - PoolManager for database connection pooling
6. **mcp_server_proxy.py** - MCP server integration
7. **mcp_server_manager.py** - MCP server lifecycle management
8. **parameters.py** - Parameter validation and JSON Schema support
9. **results.py** - ToolResult and result handling
10. **types.py** - Core type definitions and enumerations
11. **chromadb_vector_store.py** - ChromaDB implementation
12. **huggingface_facade.py** - HuggingFace LLM implementation

## Integration Steps

### 1. Install Dependencies

```bash
pip install langchain langgraph chromadb kafka-python
```

### 2. Initialize Components

```python
from abhikarta_components.llm_facade import LLMFacade
from abhikarta_components.registry import ToolRegistry
from abhikarta_components.vector_store_base import VectorStoreBase
from llm_execution_system.api import AbhikartaExecutionAPI

# Initialize your LLM facade implementation
llm_facade = YourLLMFacade(
    model_name="claude-sonnet-4-20250514",
    api_key="your_key"
)

# Initialize tool registry
tool_registry = ToolRegistry()

# Initialize vector store
vector_store = YourVectorStore(
    index_name="execution_kb",
    embedding_dim=1536
)

# Initialize execution API
api = AbhikartaExecutionAPI(
    db_path="llm_execution.db",
    llm_facade=llm_facade,
    tool_registry=tool_registry,
    vector_store=vector_store
)
```

### 3. Register Tools

```python
from abhikarta_components.base import BaseTool
from abhikarta_components.types import ToolType, ExecutionMode
from abhikarta_components.parameters import ToolParameter, ParameterType
from abhikarta_components.results import ToolResult

class WeatherTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="get_weather",
            description="Get current weather for a location",
            tool_type=ToolType.API,
            execution_mode=ExecutionMode.ASYNC
        )
        
        # Add parameters
        self.add_parameter(ToolParameter(
            name="location",
            param_type=ParameterType.STRING,
            description="City name",
            required=True
        ))
    
    def execute(self, location: str) -> ToolResult:
        # Implementation
        weather_data = get_weather_from_api(location)
        
        return ToolResult.success_result(
            data=weather_data,
            tool_name=self.name
        )

# Register tool
weather_tool = WeatherTool()
tool_registry.register(weather_tool, group="utilities", tags=["weather", "api"])
```

### 4. Execute Different Modes

#### Chat Mode

```python
import asyncio

async def chat_example():
    result = await api.execute_chat(
        user_id="user_123",
        message="What's the weather in Paris?",
        config={
            "llm_params": {
                "temperature": 0.7,
                "max_tokens": 1000
            }
        }
    )
    print(result['response'])

asyncio.run(chat_example())
```

#### ReAct Mode with Tools

```python
async def react_example():
    result = await api.execute_react(
        user_id="user_123",
        goal="Find weather in Paris and recommend activities",
        max_iterations=5,
        config={
            "available_tools": ["get_weather", "search_activities"]
        }
    )
    print(result['final_answer'])

asyncio.run(react_example())
```

#### RAG Mode with Vector Store

```python
async def rag_example():
    # First, add documents to vector store
    await vector_store.add_documents(
        documents=[
            {
                "id": "doc1",
                "content": "Paris is the capital of France...",
                "metadata": {"category": "geography"}
            }
        ]
    )
    
    # Execute RAG query
    result = await api.execute_rag(
        user_id="user_123",
        query="Tell me about Paris",
        collection_id="knowledge_base",
        top_k=3
    )
    print(result['answer'])

asyncio.run(rag_example())
```

#### Multi-Agent Mode

```python
# First, create agent definitions in database
with api.db_manager.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO agent_definitions (
            agent_id, name, description, agent_type,
            llm_provider, llm_model, system_prompt, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "analyst_agent",
        "Market Analyst",
        "Analyzes market trends",
        "analyst",
        "anthropic",
        "claude-sonnet-4-20250514",
        "You are an expert market analyst...",
        1
    ))
    conn.commit()

# Execute multi-agent task
from llm_execution_system.engines.multi_agent_engine import MultiAgentEngine

engine = MultiAgentEngine(
    user_id="user_123",
    llm_facade=llm_facade,
    tool_registry=tool_registry,
    db_manager=api.db_manager
)

result = await engine.execute(
    task="Analyze current tech stock trends",
    agent_ids=["analyst_agent", "researcher_agent"]
)
```

### 5. Background Execution

```python
# Submit background job
result = await api.execute_background(
    user_id="user_123",
    job_config={
        "type": "llm_generation",
        "prompts": [
            "Summarize article 1",
            "Summarize article 2",
            # ... more prompts
        ]
    }
)

job_id = result['job_id']

# Check status later
job_info = api.get_job_status(job_id)
print(f"Progress: {job_info['progress_percentage']}%")
```

### 6. Human-in-the-Loop

```python
result = await api.execute_hitl(
    user_id="user_123",
    task="Process sensitive customer data",
    approval_required=True,
    config={
        "approval_timeout": 300  # 5 minutes
    }
)

# Approver approves via separate endpoint
await api.approve_request(
    request_id=result['approval_request_id'],
    approver_user_id="manager_456",
    approved=True,
    feedback="Approved for processing"
)
```

### 7. Event-Driven (Kafka) Mode

```python
# Create event subscription
with api.db_manager.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO event_subscriptions (
            subscription_id, name, kafka_topic, kafka_group_id,
            kafka_config, handler_type, handler_config, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "customer_events_sub",
        "Customer Events Handler",
        "customer.events",
        "llm_execution_group",
        json.dumps({"bootstrap.servers": "localhost:9092"}),
        "planner",
        json.dumps({"max_iterations": 5}),
        1
    ))
    conn.commit()

# Start listening
from llm_execution_system.engines.listening_engine import ListeningEngine

engine = ListeningEngine(
    user_id="system",
    llm_facade=llm_facade,
    tool_registry=tool_registry,
    db_manager=api.db_manager
)

await engine.execute(subscription_id="customer_events_sub")
```

## Advanced Integration

### Custom Execution Mode

```python
from llm_execution_system.engines.base_engine import BaseExecutionEngine

class CustomEngine(BaseExecutionEngine):
    def get_mode_name(self) -> str:
        return "custom"
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        self.create_session_record()
        self.update_session_status("running")
        
        try:
            # Your custom logic here
            result = await self.custom_execution_logic(**kwargs)
            
            self.update_session_status("completed")
            return {
                "success": True,
                "result": result,
                "session_id": self.session_id
            }
        except Exception as e:
            self.update_session_status("failed", str(e))
            return {"success": False, "error": str(e)}
    
    async def custom_execution_logic(self, **kwargs):
        # Implement your logic
        pass
```

### Using PoolManager for Database Connections

```python
from abhikarta_components.pool_manager import PoolManager, get_pool_manager

# Get pool manager instance
pool_mgr = get_pool_manager()

# Create connection pool
from abhikarta_components.pool_config import SQLitePoolConfig

config = SQLitePoolConfig(
    pool_name="execution_pool",
    database_path="llm_execution.db",
    pool_size=5
)

pool_mgr.create_pool(config)

# Use pooled connection
with pool_mgr.get_connection_context("execution_pool") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM execution_sessions LIMIT 10")
    sessions = cursor.fetchall()
```

## Monitoring and Analytics

```python
# Get session statistics
stats = api.get_session_stats(session_id="abc123")
print(f"Total tokens: {stats['total_tokens']}")
print(f"Duration: {stats['duration_ms']}ms")

# List user sessions
sessions = api.list_sessions(
    user_id="user_123",
    status="completed",
    limit=20
)

# Get tool usage statistics
with api.db_manager.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tool_name, COUNT(*) as count,
               AVG(execution_time_ms) as avg_time
        FROM tool_executions
        WHERE status = 'success'
        GROUP BY tool_name
        ORDER BY count DESC
    """)
    tool_stats = cursor.fetchall()
```

## Error Handling

```python
try:
    result = await api.execute_chat(
        user_id="user_123",
        message="Test message"
    )
    
    if not result['success']:
        # Handle execution failure
        print(f"Error: {result.get('error')}")
        
except Exception as e:
    # Handle system errors
    print(f"System error: {e}")
```

## Best Practices

1. **Always use async/await** for LLM operations
2. **Handle errors gracefully** with try-except blocks
3. **Set appropriate timeouts** for long-running operations
4. **Monitor token usage** to control costs
5. **Use background mode** for batch processing
6. **Implement HITL** for sensitive operations
7. **Leverage state management** for recovery
8. **Use appropriate execution mode** for the task
9. **Register all tools** before execution
10. **Configure LLM parameters** based on use case

## Troubleshooting

### Issue: Database locked

**Solution**: Use connection pooling or ensure proper connection closing

```python
# Always use context managers
with api.db_manager.get_connection() as conn:
    # Your code here
    pass  # Connection automatically closed
```

### Issue: Tool not found

**Solution**: Verify tool is registered

```python
# Check if tool exists
if "weather_tool" in tool_registry:
    print("Tool registered")
else:
    # Register the tool
    tool_registry.register(weather_tool)
```

### Issue: LLM timeout

**Solution**: Increase timeout or use background mode

```python
# Increase timeout
llm_facade.timeout = 120  # 2 minutes

# Or use background mode for long operations
result = await api.execute_background(
    user_id="user_123",
    job_config={"type": "long_task", ...}
)
```

## Support

For additional support, refer to:
- [Architecture Documentation](ARCHITECTURE.md)
- [API Reference](API_REFERENCE.md)
- Source code examples in `examples/` directory
