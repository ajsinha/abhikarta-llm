# Abhikarta-LLM v1.1.7 - Architecture Design Document

## Table of Contents

1. [Overview](#1-overview)
2. [System Architecture](#2-system-architecture)
3. [Database Design](#3-database-design)
4. [Agent System Design](#4-agent-system-design)
5. [Workflow Engine Design](#5-workflow-engine-design)
6. [LLM Provider Integration](#6-llm-provider-integration)
7. [Human-in-the-Loop System](#7-human-in-the-loop-system)
8. [Tools System Design](#8-tools-system-design)
9. [MCP Plugin Framework](#9-mcp-plugin-framework)
10. [Pre-built Solutions](#10-pre-built-solutions)
11. [Security Architecture](#11-security-architecture)
12. [API Design](#12-api-design)

---

## 1. Overview

### 1.1 Purpose

Abhikarta-LLM is an enterprise-grade platform for building, deploying, and managing AI agents and workflows. It provides:

- Multi-provider LLM abstraction
- Visual agent and workflow designers
- Human-in-the-loop capabilities
- Comprehensive tools system
- Banking industry solutions

### 1.2 Design Principles

- **Modularity**: Components are loosely coupled and independently deployable
- **Extensibility**: Easy to add providers, tools, and integrations
- **Security**: Role-based access with audit trails
- **Scalability**: Supports horizontal scaling
- **Reliability**: Fault tolerance with retry mechanisms

### 1.3 Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Flask + Jinja2 + Bootstrap 5 |
| Backend | Python 3.9+ |
| Database | PostgreSQL / SQLite |
| LLM Integration | LangChain, LangGraph |
| External Tools | MCP (Model Context Protocol) |

---

## 2. System Architecture

### 2.1 Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Web UI    │  │  REST API   │  │  Help Documentation     │  │
│  │  (Flask)    │  │  Endpoints  │  │  (30+ pages)            │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                     APPLICATION LAYER                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │ Agent        │ │ Workflow     │ │ HITL         │             │
│  │ Manager      │ │ Engine       │ │ Manager      │             │
│  └──────────────┘ └──────────────┘ └──────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│                        TOOLS LAYER                               │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────────┐  │
│  │ BaseTool  │ │ MCPTool   │ │ HTTPTool  │ │ ToolsRegistry   │  │
│  └───────────┘ └───────────┘ └───────────┘ └─────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Pre-built Tools (60+)                       │    │
│  │   Common (28) │ Banking (13) │ Integration (20)          │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│                     INTEGRATION LAYER                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │ LangChain    │ │ MCP Clients  │ │ LLM Provider Facade      │ │
│  │ LangGraph    │ │ (HTTP/WS)    │ │ (11 providers)           │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                        DATA LAYER                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │           PostgreSQL / SQLite (22 Tables)                  │ │
│  │  Core │ Users │ LLM │ Tools │ HITL │ Audit │ Config       │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Diagram

```
                    ┌─────────────────┐
                    │   Web Browser   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Flask App     │
                    │   (Routes)      │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
│ Agent Manager │   │Workflow Engine│   │ HITL Manager  │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        └─────────┬─────────┴─────────┬─────────┘
                  │                   │
         ┌────────▼────────┐  ┌──────▼──────┐
         │ ToolsRegistry   │  │ LLM Facade  │
         └────────┬────────┘  └──────┬──────┘
                  │                  │
    ┌─────────────┼─────────────┐   │
    │             │             │   │
┌───▼───┐  ┌─────▼─────┐  ┌────▼───┐
│PreBuilt│  │ MCP Tools │  │ Custom │
│ Tools  │  │           │  │ Tools  │
└────────┘  └───────────┘  └────────┘
```

---

## 3. Database Design

### 3.1 Schema Overview (22 Tables)

```
┌─────────────────────────────────────────────────────────────────┐
│                        CORE TABLES                               │
├─────────────────┬───────────────────────────────────────────────┤
│ agents          │ Agent definitions and configurations           │
│ workflows       │ Workflow DAG definitions                       │
│ executions      │ Execution records and status                   │
│ execution_steps │ Individual step results                        │
├─────────────────┴───────────────────────────────────────────────┤
│                        USER TABLES                               │
├─────────────────┬───────────────────────────────────────────────┤
│ users           │ User accounts and profiles                     │
│ api_keys        │ API key management                             │
│ audit_logs      │ Activity audit trail                           │
├─────────────────┴───────────────────────────────────────────────┤
│                         LLM TABLES                               │
├─────────────────┬───────────────────────────────────────────────┤
│ llm_providers   │ LLM provider configurations                    │
│ llm_models      │ Available models per provider                  │
│ llm_model_perms │ Role-based model permissions                   │
│ llm_logs        │ LLM call logging                               │
├─────────────────┴───────────────────────────────────────────────┤
│                        TOOL TABLES                               │
├─────────────────┬───────────────────────────────────────────────┤
│ mcp_servers     │ MCP server configurations                      │
│ mcp_tools       │ Tools discovered from MCP servers              │
│ code_fragments  │ Reusable code snippets                         │
├─────────────────┴───────────────────────────────────────────────┤
│                        HITL TABLES                               │
├─────────────────┬───────────────────────────────────────────────┤
│ hitl_tasks      │ Human-in-the-loop tasks                        │
│ hitl_comments   │ Task comments and discussions                  │
│ hitl_assignments│ Task assignments to users                      │
├─────────────────┴───────────────────────────────────────────────┤
│                       CONFIG TABLES                              │
├─────────────────┬───────────────────────────────────────────────┤
│ settings        │ Application settings                           │
│ templates       │ Agent/workflow templates                       │
└─────────────────┴───────────────────────────────────────────────┘
```

### 3.2 Key Table Schemas

#### agents
```sql
CREATE TABLE agents (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    agent_type VARCHAR(50),        -- react, cot, pae, custom
    model_id VARCHAR(100),
    system_prompt TEXT,
    tools TEXT,                    -- JSON array of tool names
    config TEXT,                   -- JSON configuration
    status VARCHAR(50),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### workflows
```sql
CREATE TABLE workflows (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    definition TEXT NOT NULL,      -- JSON DAG definition
    status VARCHAR(50),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### hitl_tasks
```sql
CREATE TABLE hitl_tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE NOT NULL,
    execution_id VARCHAR(100),
    task_type VARCHAR(50),
    title VARCHAR(255),
    description TEXT,
    input_data TEXT,               -- JSON
    output_data TEXT,              -- JSON
    status VARCHAR(50),            -- pending, in_progress, completed, rejected
    priority VARCHAR(20),          -- low, medium, high, critical
    assigned_to INTEGER REFERENCES users(id),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

---

## 4. Agent System Design

### 4.1 Agent Types

| Type | Description | Use Case |
|------|-------------|----------|
| **ReAct** | Reasoning + Acting loop | General purpose |
| **Chain-of-Thought** | Step-by-step reasoning | Complex reasoning |
| **Plan-and-Execute** | Plan then execute | Multi-step tasks |
| **Custom** | User-defined | Specialized needs |

### 4.2 Agent Configuration Schema

```json
{
  "agent_id": "unique_identifier",
  "name": "Agent Name",
  "description": "What the agent does",
  "agent_type": "react",
  "model_id": "gpt-4o",
  "system_prompt": "You are a helpful assistant...",
  "tools": ["tool1", "tool2"],
  "temperature": 0.7,
  "max_tokens": 1024,
  "max_iterations": 10,
  "input_schema": {},
  "output_schema": {}
}
```

### 4.3 Visual Agent Designer

The designer supports 14 node types with drag-and-drop functionality:

- **Input/Output**: Start, End
- **Processing**: LLM, Agent, Tool, Code, RAG
- **Control Flow**: Condition, Loop, Passthrough
- **Human**: HITL
- **Data**: Transform, Filter, Aggregate

---

## 5. Workflow Engine Design

### 5.1 DAG Execution Model

```
Workflow Definition (JSON)
         │
         ▼
    ┌────────────┐
    │ DAG Parser │
    └─────┬──────┘
          │
          ▼
    ┌────────────┐
    │  Executor  │──────► Context
    └─────┬──────┘          │
          │                 │
    ┌─────▼─────┐          │
    │ Node Exec │◄─────────┘
    └─────┬─────┘
          │
          ▼
    ┌────────────┐
    │  Results   │
    └────────────┘
```

### 5.2 Node Types

| Node Type | Description | Implementation |
|-----------|-------------|----------------|
| `start` | Entry point | Initializes context |
| `end` | Exit point | Returns final output |
| `llm` | LLM call | Uses LLM facade |
| `agent` | Agent invocation | Calls agent executor |
| `tool` | Tool execution | Uses ToolsRegistry |
| `code` | Python execution | Sandboxed execution |
| `condition` | Branching | Expression evaluation |
| `passthrough` | Data pass | Merges contexts |
| `rag` | RAG query | Vector store lookup |
| `hitl` | Human task | Creates HITL task |

### 5.3 Workflow Definition Format

```json
{
  "workflow_id": "loan_processing",
  "name": "Loan Application Workflow",
  "nodes": [
    {
      "id": "start",
      "type": "start",
      "config": {}
    },
    {
      "id": "credit_check",
      "type": "tool",
      "config": {
        "tool_name": "calculate_credit_score"
      }
    },
    {
      "id": "decision",
      "type": "condition",
      "config": {
        "condition": "credit_score >= 700"
      }
    }
  ],
  "edges": [
    {"from": "start", "to": "credit_check"},
    {"from": "credit_check", "to": "decision"}
  ]
}
```

---

## 6. LLM Provider Integration

### 6.1 Provider Facade

```python
class LLMFacade:
    """Unified interface for all LLM providers."""
    
    def get_completion(self, model_id, messages, **kwargs):
        """Get completion from configured provider."""
        provider = self._get_provider(model_id)
        return provider.complete(messages, **kwargs)
    
    def get_streaming_completion(self, model_id, messages, **kwargs):
        """Get streaming completion."""
        provider = self._get_provider(model_id)
        return provider.stream(messages, **kwargs)
```

### 6.2 Supported Providers

| Provider | Module | Features |
|----------|--------|----------|
| OpenAI | `langchain_openai` | Full support, function calling |
| Anthropic | `langchain_anthropic` | Claude models, tools |
| Google | `langchain_google_genai` | Gemini models |
| Azure OpenAI | `langchain_openai` | Enterprise deployment |
| AWS Bedrock | `langchain_aws` | Multi-model access |
| Mistral | `langchain_mistral` | Open-weight models |
| Groq | `langchain_groq` | Fast inference |
| Together | `langchain_together` | Open source models |
| Cohere | `langchain_cohere` | Command models |
| Hugging Face | `langchain_huggingface` | Inference API |
| Ollama | `langchain_community` | Local deployment |

### 6.3 LangChain Integration

```python
# LLM Factory
from abhikarta.langchain import create_llm, create_agent

llm = create_llm(provider="openai", model="gpt-4o")
agent = create_agent(llm, tools, agent_type="react")

# LangGraph Workflow
from abhikarta.langchain import create_workflow_graph

graph = create_workflow_graph(workflow_definition)
result = graph.invoke(input_data)
```

---

## 7. Human-in-the-Loop System

### 7.1 HITL Architecture

```
Workflow Execution
        │
        ▼
┌───────────────┐
│  HITL Node    │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Create Task   │
└───────┬───────┘
        │
        ▼
┌───────────────┐         ┌──────────────┐
│ Task Queue    │◄────────│ User Action  │
└───────┬───────┘         └──────────────┘
        │
        ▼
┌───────────────┐
│Resume Workflow│
└───────────────┘
```

### 7.2 Task Lifecycle

```
PENDING ──► IN_PROGRESS ──► COMPLETED
                │                │
                │                ▼
                └──────► REJECTED
```

### 7.3 HITL Manager API

```python
class HITLManager:
    def create_task(self, execution_id, task_type, data) -> str
    def get_pending_tasks(self, user_id=None) -> List[Task]
    def assign_task(self, task_id, user_id) -> bool
    def complete_task(self, task_id, output, user_id) -> bool
    def reject_task(self, task_id, reason, user_id) -> bool
    def add_comment(self, task_id, user_id, comment) -> bool
```

---

## 8. Tools System Design

### 8.1 BaseTool Architecture

```python
class BaseTool(ABC):
    """Abstract base class for all tools."""
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass
    
    @abstractmethod
    def get_schema(self) -> ToolSchema:
        """Return tool schema for LLM function calling."""
        pass
    
    def to_openai_function(self) -> Dict:
        """Convert to OpenAI function format."""
        pass
    
    def to_anthropic_tool(self) -> Dict:
        """Convert to Anthropic tool format."""
        pass
    
    def to_langchain_tool(self) -> LangChainTool:
        """Convert to LangChain tool."""
        pass
```

### 8.2 Tool Implementations

| Tool Type | Description | Use Case |
|-----------|-------------|----------|
| `FunctionTool` | Python function wrapper | Simple tools |
| `MCPTool` | MCP server tool wrapper | External tools |
| `HTTPTool` | REST API caller | API integrations |
| `CodeFragmentTool` | Database code execution | Dynamic tools |
| `LangChainTool` | LangChain integration | LangChain ecosystem |

### 8.3 ToolsRegistry

```python
class ToolsRegistry:
    """Centralized tool registration and discovery."""
    
    def register(self, tool: BaseTool) -> bool
    def get(self, name: str) -> Optional[BaseTool]
    def list_tools(self) -> List[BaseTool]
    def search(self, query: str) -> List[BaseTool]
    def execute(self, name: str, **kwargs) -> ToolResult
    
    # Format conversion
    def to_openai_functions(self) -> List[Dict]
    def to_anthropic_tools(self) -> List[Dict]
    def to_langchain_tools(self) -> List[LangChainTool]
```

### 8.4 Pre-built Tools (60+)

#### Common Tools (28)
- Date/Time: 5 tools
- Math/Calculator: 5 tools
- Text Processing: 5 tools
- Validation: 5 tools
- Format Conversion: 5 tools
- ID Generation: 3 tools

#### Banking Tools (13)
- KYC: 4 tools
- Credit: 2 tools
- Loan: 2 tools
- Transaction: 3 tools
- Compliance: 2 tools

#### Integration Tools (20)
- HTTP/API: 4 tools
- Notifications: 3 tools
- Data Transform: 5 tools
- List/Array: 5 tools
- Workflow: 3 tools

---

## 9. MCP Plugin Framework

### 9.1 MCPServerManager

```python
class MCPServerManager:
    """Centralized MCP server lifecycle management."""
    
    def add_server(self, config: MCPServerConfig) -> str
    def connect_server(self, server_id: str) -> bool
    def disconnect_server(self, server_id: str) -> bool
    def get_server_tools(self, server_id: str) -> List[MCPTool]
    
    # Health monitoring
    def start_health_monitor(self, interval: int = 30)
    def check_health(self, server_id: str) -> bool
    
    # Database persistence
    def load_from_database(self)
    def save_to_database(self)
```

### 9.2 Transport Types

| Transport | Protocol | Use Case |
|-----------|----------|----------|
| HTTP | REST over HTTP/HTTPS | Standard web services |
| WebSocket | Full-duplex connection | Real-time tools |
| SSE | Server-Sent Events | Streaming responses |
| STDIO | Standard I/O | Local processes |

### 9.3 Tool Registration Flow

```
MCP Server Connect
        │
        ▼
┌──────────────────┐
│ List Tools API   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Create MCPTool   │
│ for each tool    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Register with    │
│ ToolsRegistry    │
└──────────────────┘
```

---

## 10. Pre-built Solutions

### 10.1 Banking Agents (10)

| Agent | Description | Tools Used |
|-------|-------------|------------|
| KYC Verification | Identity/document verification | verify_identity_document, calculate_kyc_risk_score |
| Loan Processor | Loan application evaluation | calculate_loan_eligibility, generate_amortization_schedule |
| Fraud Detection | Transaction fraud analysis | analyze_transaction, detect_transaction_patterns |
| Credit Risk | Credit risk assessment | calculate_credit_score, assess_debt_to_income |
| Customer Service | General customer support | Common tools |
| Account Opening | New account onboarding | verify_identity_document, verify_address |
| Compliance Officer | Regulatory compliance | generate_aml_report, check_sanctions_list |
| Investment Advisor | Investment recommendations | calculate_compound_interest |
| Collections | Debt collection | calculate_loan_emi |
| Document Processor | Document processing | extract_entities, clean_text |

### 10.2 Banking Workflows (7)

| Workflow | Nodes | Features |
|----------|-------|----------|
| Loan Application | 12 | Credit check, DTI, HITL review |
| Customer Onboarding | 15 | KYC, verification, parallel processing |
| Transaction Monitoring | 14 | Real-time fraud, AML reporting |
| Mortgage Application | 13 | Appraisal, underwriting |
| Credit Card Application | 15 | Product selection, fraud screening |
| Wire Transfer | 17 | OFAC, fraud, CTR |
| Dispute Resolution | 13 | Classification, investigation |

---

## 11. Security Architecture

### 11.1 Authentication & Authorization

```
┌─────────────────────────────────────────┐
│           User Request                   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      Session/API Key Validation         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│           RBAC Check                     │
│  ┌─────────────────────────────────┐    │
│  │ super_admin > domain_admin >    │    │
│  │ agent_developer > agent_user    │    │
│  └─────────────────────────────────┘    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         Resource Access                  │
└─────────────────────────────────────────┘
```

### 11.2 Role Permissions

| Permission | super_admin | domain_admin | agent_developer | agent_user |
|------------|:-----------:|:------------:|:---------------:|:----------:|
| Manage Users | ✅ | ✅ | ❌ | ❌ |
| Configure LLM | ✅ | ✅ | ❌ | ❌ |
| Create Agents | ✅ | ✅ | ✅ | ❌ |
| Execute Agents | ✅ | ✅ | ✅ | ✅ |
| View Logs | ✅ | ✅ | ✅ | ✅ |
| System Config | ✅ | ❌ | ❌ | ❌ |

### 11.3 Security Features

- **Password Hashing**: bcrypt with salt
- **Session Management**: Secure cookies, timeout
- **API Keys**: Secure generation, rotation support
- **Audit Logging**: All actions logged
- **Input Validation**: SQL injection prevention
- **HTTPS**: TLS encryption support

---

## 12. API Design

### 12.1 REST API Endpoints

#### Agents
```
GET    /api/agents              # List agents
POST   /api/agents              # Create agent
GET    /api/agents/{id}         # Get agent
PUT    /api/agents/{id}         # Update agent
DELETE /api/agents/{id}         # Delete agent
POST   /api/agents/{id}/execute # Execute agent
```

#### Workflows
```
GET    /api/workflows              # List workflows
POST   /api/workflows              # Create workflow
GET    /api/workflows/{id}         # Get workflow
PUT    /api/workflows/{id}         # Update workflow
DELETE /api/workflows/{id}         # Delete workflow
POST   /api/workflows/{id}/execute # Execute workflow
```

#### Executions
```
GET    /api/executions           # List executions
GET    /api/executions/{id}      # Get execution
GET    /api/executions/{id}/logs # Get execution logs
```

#### HITL
```
GET    /api/hitl/tasks           # List tasks
GET    /api/hitl/tasks/{id}      # Get task
POST   /api/hitl/tasks/{id}/complete # Complete task
POST   /api/hitl/tasks/{id}/reject   # Reject task
```

#### Tools
```
GET    /api/tools                # List tools
GET    /api/tools/{name}         # Get tool details
POST   /api/tools/{name}/execute # Execute tool
```

### 12.2 Response Format

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## Appendix A: Module Structure

```
abhikarta/
├── agent/              # Agent management (2 files)
├── config/             # Configuration (1 file)
├── core/               # Core utilities (2 files)
├── database/           # Database layer (5 files)
├── hitl/               # HITL system (1 file)
├── langchain/          # LangChain integration (4 files)
├── llm_provider/       # LLM facade (1 file)
├── mcp/                # MCP integration (3 files)
├── rbac/               # Access control (1 file)
├── tools/              # Tools system (8 files)
│   └── prebuilt/       # Pre-built tools (4 files)
├── user_management/    # User management (1 file)
├── utils/              # Utilities (4 files)
├── web/                # Web application (50+ files)
└── workflow/           # Workflow engine (3 files)
```

---

*Version 1.1.7 - Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.*
