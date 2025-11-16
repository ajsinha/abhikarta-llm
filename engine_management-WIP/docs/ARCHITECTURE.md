# Abhikarta LLM Execution System - Architecture

## System Overview

The Abhikarta LLM Execution Platform is a comprehensive, database-driven system for managing and executing LLM-based workflows across multiple execution paradigms.

## Core Components

### 1. Database Layer
- **SQLite Database**: Central persistence store
- **Schema**: Comprehensive tables for all execution modes
- **Connection Management**: Thread-safe connection pooling
- **Migrations**: Version-controlled schema evolution

### 2. Execution Engines
Each execution mode has a dedicated engine inheriting from `BaseExecutionEngine`:

- **BaseExecutionEngine**: Abstract base with common functionality
  - Session management
  - State persistence
  - Interaction logging
  - Error handling

- **Specialized Engines**:
  - ChatEngine: Conversational interactions
  - DAGEngine: Workflow graph execution
  - ReActEngine: Reasoning and acting loops
  - PlanningEngine: LLM-generated plans
  - AutonomousEngine: Self-directed execution
  - HITLEngine: Human approval workflows
  - BackgroundEngine: Async job processing
  - RAGEngine: Retrieval-augmented generation
  - CoTEngine: Chain of thought reasoning
  - ToolEngine: Function calling
  - MultiAgentEngine: Agent collaboration
  - HybridEngine: Combined execution modes
  - ListeningEngine: Event-driven execution

### 3. State Management
- **StateManager**: Save/load execution state
- **CheckpointManager**: Recovery points
- **ContextManager**: Conversation context windowing

### 4. Integration Layer
- **LangChainAdapter**: LangChain compatibility
- **LangGraphAdapter**: LangGraph workflows
- **KafkaConsumerAdapter**: Event consumption

### 5. API Layer
- **AbhikartaExecutionAPI**: Main entry point
- Unified interface across all modes
- Session management
- Query and analytics

## Data Flow

1. **Request Initiation**
   - User submits request via API
   - Session created in database
   - Appropriate engine instantiated

2. **Execution**
   - Engine executes mode-specific logic
   - Interactions logged to database
   - State checkpointed periodically
   - Tools invoked as needed

3. **Completion**
   - Final result saved
   - Session status updated
   - Metrics recorded

## Database Schema Design

### Core Tables
- `execution_sessions`: Master session records
- `interactions`: Individual turns/messages
- `execution_state`: State snapshots

### Mode-Specific Tables
- `dag_definitions`, `dag_executions`: DAG workflows
- `execution_plans`, `react_cycles`: Planning and reasoning
- `agent_definitions`, `agent_interactions`: Multi-agent
- `approval_requests`: HITL approvals
- `background_jobs`: Async execution
- `rag_collections`, `rag_retrievals`: RAG data
- `event_subscriptions`, `event_processing_log`: Kafka events

### Supporting Tables
- `tool_executions`: Tool call logs
- `thought_chains`: CoT tracking
- `execution_metrics`: Performance data
- `audit_log`: Full audit trail

## Design Patterns

### 1. Strategy Pattern
Each execution mode is a strategy implementing the engine interface.

### 2. Repository Pattern
Database access abstracted through managers.

### 3. Adapter Pattern
Integration adapters for external frameworks.

### 4. Singleton Pattern
Shared resources (DB manager, registries).

### 5. Observer Pattern
Callbacks and event handlers.

## Scalability Considerations

1. **Horizontal Scaling**
   - Stateless engine instances
   - Database as shared state
   - Can run multiple API instances

2. **Async Execution**
   - Background job processing
   - Non-blocking operations
   - Event-driven architecture

3. **Caching**
   - LLM response caching
   - Tool result caching
   - State caching

## Security

1. **Database Security**
   - Prepared statements (SQL injection prevention)
   - Input validation
   - Audit logging

2. **User Isolation**
   - User ID tracking
   - Session isolation
   - Access controls

3. **Error Handling**
   - Graceful degradation
   - Error logging
   - Retry mechanisms

## Monitoring and Observability

1. **Metrics**
   - Token usage tracking
   - Execution time monitoring
   - Success/failure rates
   - Tool call frequencies

2. **Logging**
   - Comprehensive audit trail
   - Interaction history
   - Error logs

3. **Debugging**
   - State inspection
   - Execution replay
   - Checkpoint analysis

## Extension Points

1. **Custom Engines**
   - Inherit from BaseExecutionEngine
   - Implement execute() method
   - Register in mode factory

2. **Custom Tools**
   - Register in ToolRegistry
   - Follow BaseTool interface
   - Automatic integration

3. **Custom State**
   - Extend GraphState
   - Custom serialization
   - Domain-specific fields
