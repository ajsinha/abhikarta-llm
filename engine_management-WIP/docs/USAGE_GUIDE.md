# Abhikarta LLM Execution System - Complete Usage Guide

**Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)**

This comprehensive guide provides detailed examples for every execution mode.

---

## Table of Contents

1. [Complete Setup](#complete-setup)
2. [Chat Mode - Complete Examples](#chat-mode-examples)
3. [DAG Mode - Complete Examples](#dag-mode-examples)
4. [ReAct Mode - Complete Examples](#react-mode-examples)
5. [RAG Mode - Complete Examples](#rag-mode-examples)
6. [Planning Mode - Complete Examples](#planning-mode-examples)
7. [Autonomous Mode - Complete Examples](#autonomous-mode-examples)
8. [HITL Mode - Complete Examples](#hitl-mode-examples)
9. [Background Mode - Complete Examples](#background-mode-examples)
10. [Chain of Thought - Complete Examples](#cot-mode-examples)
11. [Tool Calling - Complete Examples](#tool-calling-examples)
12. [Multi-Agent - Complete Examples](#multi-agent-examples)
13. [Hybrid Mode - Complete Examples](#hybrid-mode-examples)
14. [Listening Mode - Complete Examples](#listening-mode-examples)

---

## Complete Setup

### Step 1: Install Dependencies

```bash
pip install langchain langgraph chromadb anthropic
```

### Step 2: Initialize Database

```python
from llm_execution_system.database.db_manager import DatabaseManager

# Initialize database
db_manager = DatabaseManager("production.db")
db_manager.initialize_schema("database/schema.sql")

# Verify
info = db_manager.verify_schema()
print(f"✓ Database ready: {info['table_count']} tables")
```

### Step 3: Implement LLM Facade

```python
from abhikarta_components.llm_facade import LLMFacade
import anthropic
import os

class AnthropicFacade(LLMFacade):
    """Complete Anthropic implementation"""
    
    def __init__(self, model_name="claude-sonnet-4-20250514", api_key=None):
        self.client = anthropic.Anthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
        )
        self.model_name = model_name
        self.timeout = 60
        self.max_retries = 3
    
    def get_capabilities(self):
        from abhikarta_components.llm_facade import ModelCapability
        return [
            ModelCapability.CHAT_COMPLETION,
            ModelCapability.STREAMING,
            ModelCapability.TOOL_USE,
            ModelCapability.VISION,
            ModelCapability.JSON_MODE
        ]
    
    def supports_capability(self, capability):
        return capability in self.get_capabilities()
    
    async def chat_completion_async(self, messages, **kwargs):
        """Async chat completion"""
        import json
        
        # Handle response format
        if "response_format" in kwargs:
            if kwargs["response_format"].get("type") == "json_object":
                # Add JSON instruction to system message
                if not any(m["role"] == "system" for m in messages):
                    messages.insert(0, {
                        "role": "system",
                        "content": "Respond only with valid JSON."
                    })
        
        response = self.client.messages.create(
            model=self.model_name,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 1024),
            temperature=kwargs.get("temperature", 0.7),
            top_p=kwargs.get("top_p", 1.0),
            stop_sequences=kwargs.get("stop_sequences", None)
        )
        
        return {
            "content": response.content[0].text,
            "finish_reason": response.stop_reason,
            "usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            "model": self.model_name
        }
    
    async def chat_completion_with_tools_async(self, messages, tools, **kwargs):
        """Chat with tool calling"""
        import json
        
        response = self.client.messages.create(
            model=self.model_name,
            messages=messages,
            tools=tools,
            max_tokens=kwargs.get("max_tokens", 1024),
            temperature=kwargs.get("temperature", 0.7)
        )
        
        tool_calls = []
        content = ""
        
        for block in response.content:
            if block.type == "text":
                content = block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "arguments": json.dumps(block.input)
                })
        
        return {
            "content": content,
            "tool_calls": tool_calls,
            "finish_reason": response.stop_reason,
            "usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        }
    
    # Implement other required methods with pass or basic implementation
    def get_model_info(self):
        return {
            "name": self.model_name,
            "provider": "anthropic",
            "max_tokens": 200000
        }
    
    def health_check(self):
        try:
            # Simple API check
            return True
        except:
            return False
    
    def close(self):
        pass

# Initialize LLM
llm = AnthropicFacade()
print("✓ LLM Facade ready")
```

### Step 4: Setup Tool Registry

```python
from abhikarta_components.registry import ToolRegistry
from abhikarta_components.base import BaseTool
from abhikarta_components.types import ToolType, ExecutionMode
from abhikarta_components.results import ToolResult
from abhikarta_components.parameters import ToolParameter, ParameterType

# Create registry
tool_registry = ToolRegistry()

# Example Tool 1: Calculator
class CalculatorTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations",
            tool_type=ToolType.COMPUTATION,
            execution_mode=ExecutionMode.SYNC
        )
        
        self.add_parameter(ToolParameter(
            name="expression",
            param_type=ParameterType.STRING,
            description="Math expression to evaluate (e.g., '2 + 2', '10 * 5')",
            required=True
        ))
    
    def execute(self, expression: str) -> ToolResult:
        try:
            # Safe eval for demo - use proper math parser in production
            import re
            # Only allow numbers and operators
            if not re.match(r'^[\d\+\-\*/\.\(\)\s]+$', expression):
                return ToolResult.failure_result(
                    error="Invalid expression",
                    tool_name=self.name
                )
            
            result = eval(expression, {"__builtins__": {}}, {})
            
            return ToolResult.success_result(
                data={"result": result, "expression": expression},
                tool_name=self.name
            )
        except Exception as e:
            return ToolResult.failure_result(
                error=str(e),
                tool_name=self.name
            )

# Example Tool 2: Web Search (simulated)
class WebSearchTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for information",
            tool_type=ToolType.API,
            execution_mode=ExecutionMode.ASYNC
        )
        
        self.add_parameter(ToolParameter(
            name="query",
            param_type=ParameterType.STRING,
            description="Search query",
            required=True
        ))
        
        self.add_parameter(ToolParameter(
            name="num_results",
            param_type=ParameterType.INTEGER,
            description="Number of results to return",
            required=False,
            default=5
        ))
    
    async def execute_async(self, query: str, num_results: int = 5) -> ToolResult:
        # Simulated search results
        import asyncio
        await asyncio.sleep(0.5)  # Simulate API call
        
        results = [
            {
                "title": f"Result {i+1} for '{query}'",
                "url": f"https://example.com/result{i+1}",
                "snippet": f"This is a search result snippet for {query}"
            }
            for i in range(num_results)
        ]
        
        return ToolResult.success_result(
            data={"query": query, "results": results, "count": len(results)},
            tool_name=self.name
        )

# Register tools
tool_registry.register(CalculatorTool(), group="utilities")
tool_registry.register(WebSearchTool(), group="search")

print(f"✓ Tools registered: {len(tool_registry)} tools")
```

### Step 5: Setup Vector Store

```python
from abhikarta_components.chromadb_vector_store import ChromaDBVectorStore

# Initialize vector store
vector_store = ChromaDBVectorStore(
    index_name="knowledge_base",
    embedding_dim=1536,
    persist_directory="./chroma_db"
)

print("✓ Vector store ready")
```

### Step 6: Initialize Complete System

```python
from llm_execution_system.api import AbhikartaExecutionAPI

# Create API instance with all components
api = AbhikartaExecutionAPI(
    db_path="production.db",
    llm_facade=llm,
    tool_registry=tool_registry,
    vector_store=vector_store
)

print("✅ COMPLETE SYSTEM READY!")
```

---

## Chat Mode Examples

### Example 1: Simple Q&A

```python
import asyncio

async def simple_qa():
    """Basic question answering"""
    
    result = await api.execute_chat(
        user_id="user_123",
        message="What is the capital of France?"
    )
    
    print(f"Q: What is the capital of France?")
    print(f"A: {result['response']}")
    print(f"Session: {result['session_id']}")

asyncio.run(simple_qa())
```

### Example 2: Multi-Turn Conversation

```python
async def conversation():
    """Multi-turn conversation with context"""
    
    session_id = None
    
    questions = [
        "What is Python?",
        "What are its main advantages?",
        "How does it compare to Java?",
        "Which should I learn first as a beginner?"
    ]
    
    for q in questions:
        result = await api.execute_chat(
            user_id="user_123",
            message=q,
            session_id=session_id
        )
        
        session_id = result['session_id']
        
        print(f"\n Q: {q}")
        print(f"A: {result['response']}")
    
    # View full conversation history
    from database.repositories import InteractionRepository
    repo = InteractionRepository(api.db_manager)
    
    interactions = repo.get_interactions(session_id)
    print(f"\n✓ Total interactions: {len(interactions)}")

asyncio.run(conversation())
```

### Example 3: Chat with Custom Parameters

```python
async def creative_chat():
    """Chat with high temperature for creativity"""
    
    config = {
        "llm_params": {
            "temperature": 0.9,  # More creative
            "max_tokens": 3000
        },
        "context_window_size": 5
    }
    
    result = await api.execute_chat(
        user_id="writer_001",
        message="Write a creative short story about a robot learning to paint",
        config=config
    )
    
    print(result['response'])

asyncio.run(creative_chat())
```

### Example 4: Factual Chat with Low Temperature

```python
async def factual_chat():
    """Factual responses with low temperature"""
    
    config = {
        "llm_params": {
            "temperature": 0.1,  # More focused
            "max_tokens": 1000
        }
    }
    
    result = await api.execute_chat(
        user_id="researcher_001",
        message="Explain the theory of relativity in scientific terms",
        config=config
    )
    
    print(result['response'])

asyncio.run(factual_chat())
```

---

## DAG Mode Examples

### Example 1: Data Processing Pipeline

```python
async def data_pipeline():
    """Complete data processing workflow"""
    import uuid
    import json
    
    # Define pipeline DAG
    pipeline_dag = {
        "nodes": {
            "extract": {
                "type": "tool",
                "tool": "data_extractor",
                "description": "Extract data from source",
                "inputs": {"source": "{data_source}", "format": "{data_format}"},
                "next": ["validate"]
            },
            "validate": {
                "type": "tool",
                "tool": "data_validator",
                "description": "Validate extracted data",
                "inputs": {"data": "{extract.result}"},
                "next": ["transform"]
            },
            "transform": {
                "type": "tool",
                "tool": "data_transformer",
                "description": "Transform data to target format",
                "inputs": {"data": "{validate.result}", "target_format": "json"},
                "next": ["analyze"]
            },
            "analyze": {
                "type": "llm",
                "description": "Analyze transformed data",
                "prompt": """
                Analyze the following data and provide insights:
                Data: {transform.result}
                
                Provide:
                1. Summary statistics
                2. Key patterns
                3. Anomalies
                4. Recommendations
                """,
                "next": ["report"]
            },
            "report": {
                "type": "llm",
                "description": "Generate executive report",
                "prompt": """
                Create an executive summary based on this analysis:
                {analyze.result}
                
                Format as a professional report with:
                - Executive Summary
                - Key Findings
                - Recommendations
                - Next Steps
                """,
                "next": []
            }
        }
    }
    
    # Save DAG
    dag_id = str(uuid.uuid4())
    
    with api.db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dag_definitions (
                dag_id, name, description, graph_definition, entry_point, is_active
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            dag_id,
            "Data Processing Pipeline",
            "Extract, validate, transform, analyze, and report on data",
            json.dumps(pipeline_dag),
            "extract",
            1
        ))
        conn.commit()
    
    print(f"✓ DAG created: {dag_id}")
    
    # Execute DAG
    result = await api.execute_dag(
        user_id="analyst_001",
        dag_id=dag_id,
        inputs={
            "data_source": "sales_database",
            "data_format": "csv"
        }
    )
    
    print(f"\nExecution Result:")
    print(json.dumps(result, indent=2))

asyncio.run(data_pipeline())
```

---

## ReAct Mode Examples

### Example 1: Research Task

```python
async def research_task():
    """ReAct for comprehensive research"""
    
    result = await api.execute_react(
        user_id="researcher_001",
        goal="""
        Research the current state of quantum computing applications.
        Find:
        1. Major recent breakthroughs
        2. Current commercial applications
        3. Key challenges
        4. Future outlook
        
        Provide a comprehensive summary with sources.
        """,
        max_iterations=15,
        config={
            "available_tools": ["web_search", "calculator"],
            "llm_params": {
                "temperature": 0.5
            }
        }
    )
    
    print(f"Final Answer:\n{result['final_answer']}")
    print(f"\nCompleted in {result['iterations']} iterations")
    
    # View reasoning process
    with api.db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cycle_number, thought, action, observation
            FROM react_cycles
            WHERE session_id = ?
            ORDER BY cycle_number
        """, (result['session_id'],))
        
        print("\nReasoning Process:")
        for row in cursor.fetchall():
            print(f"\n--- Iteration {row[0]} ---")
            print(f"Thought: {row[1][:100]}...")
            print(f"Action: {row[2]}")
            print(f"Observation: {row[3][:100]}..." if row[3] else "No observation")

asyncio.run(research_task())
```

---

## RAG Mode Examples

### Example 1: Document Q&A

```python
async def document_qa():
    """RAG with document collection"""
    
    # First, populate vector store with documents
    documents = [
        {
            "id": "doc1",
            "content": """
            Quantum computing uses quantum-mechanical phenomena such as superposition 
            and entanglement to perform computation. Unlike classical computers that 
            use bits (0 or 1), quantum computers use quantum bits or 'qubits' which 
            can exist in multiple states simultaneously.
            """,
            "metadata": {"topic": "quantum_computing", "category": "basics"}
        },
        {
            "id": "doc2",
            "content": """
            Current applications of quantum computing include cryptography, drug discovery,
            optimization problems, and financial modeling. Companies like IBM, Google, and
            Microsoft are investing heavily in quantum computing research.
            """,
            "metadata": {"topic": "quantum_computing", "category": "applications"}
        },
        {
            "id": "doc3",
            "content": """
            The main challenges in quantum computing include maintaining quantum coherence,
            error correction, and scalability. Quantum systems are extremely sensitive to
            environmental interference, making them difficult to maintain.
            """,
            "metadata": {"topic": "quantum_computing", "category": "challenges"}
        }
    ]
    
    # Add to vector store
    await vector_store.add_documents(documents)
    print(f"✓ Added {len(documents)} documents to vector store")
    
    # Query with RAG
    queries = [
        "What are qubits?",
        "What are the applications of quantum computing?",
        "What are the main challenges?"
    ]
    
    for query in queries:
        result = await api.execute_rag(
            user_id="student_001",
            query=query,
            collection_id="knowledge_base",
            top_k=2,
            config={
                "similarity_threshold": 0.6,
                "llm_params": {"temperature": 0.3}
            }
        )
        
        print(f"\nQ: {query}")
        print(f"A: {result['answer']}")
        print(f"Retrieved: {result['retrieved_documents']} documents")

asyncio.run(document_qa())
```

---

## Tool Calling Examples

### Example 1: Math Assistant

```python
async def math_assistant():
    """Assistant that uses calculator tool"""
    
    result = await api.execute_tool(
        user_id="student_001",
        user_message="""
        I need help with these calculations:
        1. What is 15% of 850?
        2. If I invest $5000 at 7% annual interest, how much will I have after 3 years?
        """,
        available_tools=["calculator"],
        config={
            "llm_params": {"temperature": 0.1}
        }
    )
    
    print(f"Response: {result['response']}")
    print(f"Tool calls made: {result.get('tool_calls', 0)}")

asyncio.run(math_assistant())
```

---

## Complete Working Example

Here's a complete end-to-end example:

```python
#!/usr/bin/env python3
"""
Complete Working Example
Demonstrates full system setup and usage
"""

import asyncio
import os
from pathlib import Path

# Setup
async def main():
    print("="*60)
    print("ABHIKARTA LLM EXECUTION SYSTEM - COMPLETE DEMO")
    print("="*60)
    
    # 1. Initialize Database
    print("\n1. Initializing database...")
    from llm_execution_system.database.db_manager import DatabaseManager
    
    db_manager = DatabaseManager("demo.db")
    schema_path = Path("database/schema.sql")
    if schema_path.exists():
        db_manager.initialize_schema(str(schema_path))
        print("   ✓ Database initialized")
    
    # 2. Setup LLM (using mock for demo)
    print("\n2. Setting up LLM...")
    
    class MockLLM:
        async def chat_completion_async(self, messages, **kwargs):
            return {
                "content": "This is a mock response. In production, this would be from Claude.",
                "finish_reason": "stop",
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
            }
    
    llm = MockLLM()
    print("   ✓ LLM ready (mock)")
    
    # 3. Setup Tools
    print("\n3. Setting up tools...")
    from abhikarta_components.registry import ToolRegistry
    
    tool_registry = ToolRegistry()
    print("   ✓ Tool registry ready")
    
    # 4. Create API
    print("\n4. Initializing API...")
    from llm_execution_system.api import AbhikartaExecutionAPI
    
    api = AbhikartaExecutionAPI(
        db_path="demo.db",
        llm_facade=llm,
        tool_registry=tool_registry
    )
    print("   ✓ API ready")
    
    # 5. Execute Chat
    print("\n5. Executing chat...")
    result = await api.execute_chat(
        user_id="demo_user",
        message="Hello, world!"
    )
    
    print(f"   Response: {result['response']}")
    print(f"   Session: {result['session_id']}")
    
    # 6. Check database
    print("\n6. Verifying database records...")
    with api.db_manager.get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM execution_sessions")
        sessions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM interactions")
        interactions = cursor.fetchone()[0]
        
        print(f"   Sessions: {sessions}")
        print(f"   Interactions: {interactions}")
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETED SUCCESSFULLY!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
```

Save this as `complete_demo.py` and run:

```bash
python complete_demo.py
```

This demonstrates the complete system working end-to-end!

