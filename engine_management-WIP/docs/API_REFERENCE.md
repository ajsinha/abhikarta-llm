# API Reference

## AbhikartaExecutionAPI

Main entry point for the execution system.

### Initialization

```python
api = AbhikartaExecutionAPI(
    db_path="llm_execution.db",
    llm_facade=your_llm_facade,
    tool_registry=your_tool_registry,
    vector_store=your_vector_store
)
```

### Methods

#### execute_chat()

Execute chat mode.

```python
result = await api.execute_chat(
    user_id: str,
    message: str,
    session_id: str = None,
    config: Dict = None
) -> Dict[str, Any]
```

**Parameters:**
- `user_id`: User identifier
- `message`: User message
- `session_id`: Optional session ID for multi-turn
- `config`: Optional configuration override

**Returns:**
- `success`: Boolean
- `response`: Assistant response
- `session_id`: Session identifier

#### execute_react()

Execute ReAct mode.

```python
result = await api.execute_react(
    user_id: str,
    goal: str,
    max_iterations: int = 10,
    config: Dict = None
) -> Dict[str, Any]
```

**Parameters:**
- `user_id`: User identifier
- `goal`: Goal to accomplish
- `max_iterations`: Maximum reasoning iterations
- `config`: Optional configuration

**Returns:**
- `success`: Boolean
- `final_answer`: Final result
- `iterations`: Number of iterations used
- `session_id`: Session identifier

#### execute_rag()

Execute RAG mode.

```python
result = await api.execute_rag(
    user_id: str,
    query: str,
    collection_id: str,
    top_k: int = 5,
    config: Dict = None
) -> Dict[str, Any]
```

**Parameters:**
- `user_id`: User identifier
- `query`: Query text
- `collection_id`: Vector collection ID
- `top_k`: Number of documents to retrieve
- `config`: Optional configuration

**Returns:**
- `success`: Boolean
- `answer`: Generated answer
- `retrieved_documents`: Number of documents used
- `session_id`: Session identifier

#### execute_dag()

Execute DAG workflow.

```python
result = await api.execute_dag(
    user_id: str,
    dag_id: str,
    inputs: Dict[str, Any] = None,
    config: Dict = None
) -> Dict[str, Any]
```

**Parameters:**
- `user_id`: User identifier
- `dag_id`: DAG definition ID
- `inputs`: Input values for DAG
- `config`: Optional configuration

**Returns:**
- `success`: Boolean
- `result`: Final DAG output
- `execution_id`: Execution identifier
- `session_id`: Session identifier

### Session Management

#### get_session_info()

Get session information.

```python
session = api.get_session_info(session_id: str) -> Dict
```

#### list_sessions()

List user sessions.

```python
sessions = api.list_sessions(
    user_id: str,
    status: str = None,
    limit: int = 50
) -> List[Dict]
```

## Database Manager

### DatabaseManager

Manages database connections and operations.

```python
from database.db_manager import DatabaseManager

db_manager = DatabaseManager("database.db")
db_manager.initialize_schema("schema.sql")
```

### Methods

#### get_connection()

Get database connection context manager.

```python
with db_manager.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions")
```

#### verify_schema()

Verify database schema.

```python
info = db_manager.verify_schema()
# Returns: table_count, tables, indexes, etc.
```

## Repositories

### SessionRepository

```python
from database.repositories import SessionRepository

repo = SessionRepository(db_manager)
session_id = repo.create_session(
    user_id="user_123",
    execution_mode="chat",
    configuration={}
)
```

### InteractionRepository

```python
from database.repositories import InteractionRepository

repo = InteractionRepository(db_manager)
interaction_id = repo.create_interaction(
    session_id=session_id,
    user_id="user_123",
    role="user",
    content="Hello"
)
```

## State Management

### StateManager

```python
from state_management.state_manager import StateManager

state_mgr = StateManager(db_manager)
state_id = state_mgr.save_state(session_id, {"data": "value"})
state = state_mgr.load_state(session_id)
```

### CheckpointManager

```python
from state_management.checkpoint_manager import CheckpointManager

checkpoint_mgr = CheckpointManager(db_manager)
checkpoint_id = checkpoint_mgr.create_checkpoint(
    session_id,
    state_data,
    description="Checkpoint 1"
)
```

## Utilities

### Logging

```python
from utils.logging_utils import setup_logging, ExecutionLogger

logger = setup_logging(log_level="INFO", log_file="app.log")

exec_logger = ExecutionLogger(session_id)
exec_logger.log_start("chat", "user_123")
exec_logger.log_step("processing", {"detail": "value"})
```

### Metrics

```python
from utils.metrics_utils import MetricsCollector, PerformanceTracker

metrics = MetricsCollector(db_manager)
metrics.record_metric(session_id, "latency", 150.5, "ms")

tracker = PerformanceTracker(session_id, metrics)
tracker.start_timer("llm_call")
# ... operation ...
duration = tracker.end_timer("llm_call")
```

## Configuration

### Mode Configurations

```python
from config.mode_configs import get_mode_config, merge_configs

# Get default config
config = get_mode_config("chat")

# Merge with custom config
custom = {"llm_params": {"temperature": 0.9}}
final_config = merge_configs(config, custom)
```

## Exceptions

All engines may raise:
- `ValueError`: Invalid parameters
- `RuntimeError`: Execution errors
- `TimeoutError`: Operation timeout

Handle appropriately:

```python
try:
    result = await api.execute_chat(...)
except ValueError as e:
    print(f"Invalid input: {e}")
except RuntimeError as e:
    print(f"Execution failed: {e}")
```
