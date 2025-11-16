# Quick Start Guide

## Installation

```bash
# Clone or extract the system
cd llm_execution_system

# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 -c "from database.db_manager import DatabaseManager; \
            mgr = DatabaseManager(); \
            mgr.initialize_schema('database/schema.sql')"
```

## Basic Usage

### 1. Simple Chat

```python
import asyncio
from api import AbhikartaExecutionAPI

async def main():
    # Initialize API
    api = AbhikartaExecutionAPI(db_path="test.db")
    
    # Execute chat (note: requires LLM facade)
    # result = await api.execute_chat(
    #     user_id="user_1",
    #     message="Hello, world!"
    # )
    
if __name__ == "__main__":
    asyncio.run(main())
```

### 2. With Real LLM

```python
from api import AbhikartaExecutionAPI
from abhikarta_components.llm_facade import LLMFacade

# Implement your LLM facade
class MyLLMFacade(LLMFacade):
    # Implement required methods
    pass

llm = MyLLMFacade(model_name="claude-sonnet-4-20250514")
api = AbhikartaExecutionAPI(llm_facade=llm)

result = await api.execute_chat(
    user_id="user_1",
    message="What is 2+2?"
)
```

## Next Steps

1. Review [Integration Guide](INTEGRATION_GUIDE.md)
2. Explore examples in `examples/` directory
3. Read [Architecture Documentation](ARCHITECTURE.md)
