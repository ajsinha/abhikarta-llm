# Abhikarta-LLM v1.4.9

[![Version](https://img.shields.io/badge/version-1.4.8-blue.svg)](https://github.com/abhikarta-llm)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

**Enterprise-grade AI Agent & Workflow Orchestration Platform with Agent Swarms and Enterprise Notifications**

Abhikarta-LLM is a comprehensive platform for building, deploying, and managing AI agents, workflows, and intelligent agent swarms with multi-provider LLM support, visual designers, human-in-the-loop controls, enterprise notifications, and industry-specific solutions.

---

## 🚀 What's New in v1.4.9

### 📦 Modular SDK Architecture
Abhikarta-LLM now provides **three standalone packages** for maximum flexibility:

| Package | Description | PyPI |
|---------|-------------|------|
| **abhikarta-sdk-client** | Connect to deployed Abhikarta server | `pip install abhikarta-sdk-client` |
| **abhikarta-sdk-embedded** | Standalone usage - no server needed | `pip install abhikarta-sdk-embedded` |
| **abhikarta-web** | Web UI module for the platform | Part of full installation |

### 🔌 SDK Client (Server Mode)
```python
from abhikarta_client import AbhikartaClient

client = AbhikartaClient("http://localhost:5000")
agent = client.agents.get("my-agent")
result = agent.execute("Research AI trends")
```

### 🚀 SDK Embedded (Standalone Mode)
```python
from abhikarta_embedded import Agent

# Create an agent in 3 lines - no server required!
agent = Agent.create("react", model="ollama/llama3.2:3b")
result = agent.run("What is quantum computing?")
print(result.response)
```

### 🎨 Decorator-Based API
```python
from abhikarta_embedded import agent, tool

@tool(description="Search the web")
def web_search(query: str) -> dict:
    return {"results": ["Result 1", "Result 2"]}

@agent(type="react", model="ollama/llama3.2:3b", tools=[web_search])
class ResearchAgent:
    system_prompt = "You are a research assistant."

my_agent = ResearchAgent()
result = my_agent.run("Find AI trends")
```

### 📁 Reorganized Project Structure (v1.4.9)
```
abhikarta-llm/
├── abhikarta-main/               # Core library package
│   ├── src/abhikarta/            #   Agents, workflows, swarms, orgs, actor system
│   ├── entity_definitions/       #   JSON templates (agents, workflows, swarms, etc.)
│   └── examples/                 #   Example code and usage patterns
├── abhikarta-web/                # Web UI module
│   └── src/abhikarta_web/        #   Flask routes, templates, static files
├── abhikarta-sdk-client/         # API client SDK
│   └── src/abhikarta_client/     #   Remote server connectivity
├── abhikarta-sdk-embedded/       # Standalone embedded SDK
│   └── src/abhikarta_embedded/   #   No-server agent development
├── docs/sdk/                     # SDK documentation
└── run_server.py                 # Application entry point
```

### 🐍 Python Script Mode (v1.4.9)
Power users can now define agents, workflows, swarms, and AI organizations using Python scripts instead of JSON/visual designers. See `docs/sdk/` for details.

---

## 🏢 What's New in v1.4.7

### 🏢 AI Organizations - Major New Feature
Introducing **AI Org** - create AI-powered digital twins of organizational structures:

- **Visual Org Chart Designer**: Drag-and-drop interface to design AI organizational hierarchies
- **Hierarchical Task Delegation**: CEO delegates to managers who delegate to analysts - just like real orgs
- **Response Aggregation**: AI synthesizes subordinate responses into consolidated summaries at each level
- **Human-in-the-Loop (HITL)**: Human mirrors can view, approve, override, or reject AI decisions
- **Multi-Channel Notifications**: Email, Teams, Slack notifications per node when tasks complete
- **Complete Audit Trail**: Full traceability of all tasks, responses, and interventions

### 🔗 Key AI Org Concepts
- **AI Node**: Position in org chart with AI agent and human mirror
- **Task Flow**: Tasks flow down through delegation, responses flow up through aggregation
- **HITL Dashboard**: Central view for human employees to manage their AI mirrors
- **Chain-of-Thought + Tree-of-Thoughts**: Combined reasoning patterns in organizational context

### 📬 Enterprise Notification System (v1.4.0)
Introducing the **Notification Module** - unified multi-channel notifications for agents, workflows, and swarms:

- **Slack Integration**: Channel messages, direct messages, Block Kit rich formatting, thread replies
- **Microsoft Teams Integration**: Incoming webhooks, Adaptive Cards, MessageCard format, action buttons
- **Webhook Receiver**: Accept external webhooks with HMAC/JWT/API key authentication
- **NotificationManager**: Central orchestrator for routing notifications across channels
- **Rate Limiting**: Per-channel rate limiting with token bucket algorithm
- **Retry Logic**: Exponential backoff for failed notification delivery
- **Audit Logging**: Full notification history stored in database

### 🔌 Webhook Endpoints
New module for receiving external events:

- **Endpoint Registration**: Register custom webhook endpoints with path and auth
- **Signature Verification**: HMAC-SHA256, JWT, API key, Basic auth support
- **Replay Protection**: Nonce and timestamp validation
- **Event Dispatching**: Trigger agents, workflows, or swarms from webhooks
- **Rate Limiting**: Per-endpoint configurable rate limits

### Database Schema Updates
- 5 new notification tables: `notification_channels`, `notification_logs`, `webhook_endpoints`, `webhook_events`, `user_notification_preferences`
- Schema version updated to 1.4.0

### New abhikarta.notification Module
```
abhikarta/notification/
├── __init__.py          # Module exports
├── base.py              # Data models and enums
├── manager.py           # NotificationManager
├── slack_adapter.py     # Slack integration
├── teams_adapter.py     # Teams integration
└── webhook_receiver.py  # Webhook handling
```

### 🧠 Chain of Thought & Tree of Thought Tutorial
New comprehensive tutorial for advanced reasoning patterns:

- **Chain of Thought (CoT)**: Step-by-step reasoning for complex problems
- **Tree of Thought (ToT)**: Parallel exploration of multiple solution paths
- **Agent Types**: Pre-configured CoT and ToT agent templates
- **Workflow Integration**: CoT/ToT nodes for visual workflows
- **Swarm Choreography**: Master Actors using CoT for delegation decisions
- **Best Practices**: Temperature settings, token budgeting, prompt engineering

**Documentation**: `docs/COT_TOT_TUTORIAL.md` (940 lines)

---

## 📋 Previous Version Highlights

### v1.3.0 - Agent Swarms & Messaging
- **Agent Swarms**: Master Actor choreography, event-driven architecture, on-demand scaling
- **Messaging Module**: Unified Kafka/RabbitMQ/ActiveMQ abstraction
- **Visual Swarm Designer**: Drag-and-drop swarm building
- **Playground Menu**: Combined Agents, Workflows, Swarms navigation

### v1.2.0 - Visual Designer Enhancements
- **Workflow Visual Designer**: Complete rewrite matching Agent Visual Designer look and feel
  - Same node styles, connectors, canvas, and minimap as Agent Designer
  - Tool namespacing support (`builtin:toolname`, `mcp:server:toolname`)
  - Browse Tools modal for adding tool nodes
  - All node types: Start, End, Condition, Loop, Parallel, LLM, Agent, Tool, Code, Transform, RAG Query, Memory, HITL Review
- **Dynamic LLM Provider/Model Dropdowns**: Both designers now load providers and models from backend
  - No more hardcoded provider/model lists
  - Only active providers shown
  - Models dynamically filtered by selected provider
  - Default provider/model selection supported

### Agent Visual Designer Improvements
- **Bug Fixes**: MCP Tool nodes from Browse modal now properly draggable and connectable
- **Tool Selection**: MCP Tool nodes now have a dropdown to select available tools in Properties Panel
- **Enhanced Editor**: Full tool configuration in node edit modal with schema preview
- **Better UX**: Nodes from MCP modal now appear in center of visible canvas area

### Comprehensive Designer Documentation
- **Agent Visual Designer Guide**: Step-by-step tutorials, node reference, workflow patterns
- **Workflow Visual Designer Guide**: Complete how-to documentation with examples
- **Keyboard shortcuts** and best practices for both designers

### New API Endpoints
- `GET /api/llm/providers` - List all active LLM providers
- `GET /api/llm/providers/<id>/models` - List models for a specific provider
- `GET /api/llm/models` - List all models grouped by provider

### Additional Enhancements
- Extended properties panel for all node types (Loop, Transform, Parallel, Memory, Retrieval)
- Improved MCP plugin page (separate add page instead of modal)
- Fixed `agents_list` endpoint reference error

---

## 📋 Previous Version Highlights

### v1.2.4 - Template Libraries & Actor System
- **36 Agent Templates** across 15 categories (Analytics, Banking, Development, Healthcare, Legal, etc.)
- **33 Workflow Templates** across 11 industries (Finance, Healthcare, HR, Legal, Sales, Technology, etc.)
- **Code Fragment URI Support**: Templates now reference code fragments using proper URIs (`db://`, `s3://`, `file://`)
- **Actor System**: Pekko-inspired concurrency framework with supervision, dispatchers, mailboxes

### Modular Database Delegate Architecture (from v1.2.1)
- **DatabaseDelegate Abstract Base**: New abstract class for domain-specific database operations
- **9 Specialized Delegates**: Modular handlers for each database domain
  - `UserDelegate`: Users, Roles, Sessions, API Keys
  - `LLMDelegate`: Providers, Models, Permissions, Calls
  - `AgentDelegate`: Agents, Versions, Templates
  - `WorkflowDelegate`: Workflows, Nodes
  - `ExecutionDelegate`: Executions, Steps
  - `HITLDelegate`: Tasks, Comments, Assignments
  - `MCPDelegate`: Plugins, Tool Servers
  - `AuditDelegate`: Audit Logs, Settings
  - `CodeFragmentDelegate`: Code Fragments
- **Clean API**: `db_facade.users.get_user_by_id()`, `db_facade.agents.create_agent()`, etc.
- **Encapsulated SQL**: All database queries confined to delegate layer

### Database Schema Documentation (from v1.2.0)
- **Comprehensive ER Diagram**: Visual representation of all 22 database tables
- **Table Reference Guide**: Detailed column descriptions for every table
- **Relationship Mapping**: Entity relationships clearly documented

### Tool View & Test Pages (from v1.1.8)
- **Dedicated Tool Detail Page**: Full tool information with parameters, schema, metadata
- **Tool Test Page**: Form-based parameter input with type-specific controls
- **JSON Schema Display**: View complete tool schema with copy functionality

### Tool Framework Architecture
- **10 Extensible Base Classes**: BaseTool, FunctionTool, HTTPTool, MCPTool, CodeFragmentTool, etc.
- **Banking Tool Classes (5)**: KYC, Credit, Loan, Compliance, Fraud detection base classes
- **Integration Tool Classes (4)**: HTTP/API, notifications, data transformation, workflow helpers
- **Example Implementations**: Sample tools demonstrating each base class

### Tools Management Page
- **Centralized Tools View**: Browse all available tools (pre-built, MCP, code fragments)
- **Search & Filter**: Find tools by name, category, or source
- **DataTables Integration**: Pagination, sorting, search
- **Quick Actions**: View details or test directly from listing
- **Auto-Refresh**: MCP server tools automatically sync on connect/disconnect

### Industry Template Solutions
- **36 Agent Templates**: Across 15 categories including Analytics, Banking, Development, Healthcare, Legal, HR
- **33 Workflow Templates**: Across 11 industries including Finance, Healthcare, HR, Legal, Technology
- **Code Fragment Support**: 16 workflow templates and 9 agent templates with URI-based code fragments
- **Clone & Customize**: All solutions can be cloned, modified, and deployed immediately

### Auto-initialization at Startup
- All pre-built tools automatically registered on server start
- MCP servers auto-connect and load tools from database
- Health monitor runs in background for MCP server availability

---

## ✨ Key Features

### ⚡ Actor System (v1.4.7 NEW)
- **Pekko-Inspired Design**: Lightweight actors for massive concurrency
- **Message-Driven**: Fire-and-forget (tell) and request-response (ask) patterns
- **Fault Tolerance**: Supervision strategies with automatic recovery
- **Routers**: Round-robin, random, broadcast, consistent hashing
- **Patterns**: Circuit breaker, event bus, aggregator, stashing

### 🤖 Agent Management
- **Visual Agent Designer**: Drag-and-drop interface with 14 node types
- **Multiple Agent Types**: ReAct, Chain-of-Thought, Plan-and-Execute, Custom
- **Tool Integration**: Function tools, MCP tools, HTTP tools, code fragments
- **36 Pre-built Templates**: Across 15 categories ready for deployment
- **Code Fragment URIs**: Reference code via `db://`, `s3://`, `file://` schemes

### 📊 Workflow Orchestration
- **Visual Workflow Designer**: 10 node types (Start, End, LLM, Agent, Tool, Code, RAG, Condition, Passthrough, HITL)
- **DAG Execution Engine**: JSON-defined workflows with Python execution
- **Parallel Processing**: Fork/join patterns, conditional routing
- **33 Pre-built Templates**: Across 11 industries with HITL integration

### 🔧 Tools System (v1.1.6+)
- **BaseTool Architecture**: Abstract base class for all tool types
- **Tool Types**: FunctionTool, MCPTool, HTTPTool, CodeFragmentTool, LangChainTool
- **ToolsRegistry**: Centralized registration, discovery, and execution
- **Format Conversion**: OpenAI, Anthropic, LangChain compatible outputs
- **Tool Framework**: 10 extensible base classes for custom tools
- **Tools Page**: Browse, search, filter, and test all tools

### 🔌 MCP Integration (v1.1.6+)
- **MCPServerManager**: Centralized server lifecycle management
- **Multiple Transports**: HTTP, WebSocket, SSE, STDIO
- **Auto-connect**: Automatic connection on startup and server add
- **Health Monitoring**: Background health checks with auto-reconnect
- **Tool Discovery**: Automatic tool registration from MCP servers
- **Auto-sync**: Tools automatically added/removed based on server availability

### 👤 Human-in-the-Loop (v1.1.5+)
- **Task Management**: Create, assign, track approval tasks
- **Priority Levels**: Low, Medium, High, Critical
- **Comments & History**: Full audit trail of decisions
- **Workflow Integration**: HITL nodes pause execution for human input
- **User & Admin Interfaces**: Separate views for different roles

### 🏦 Banking Solutions (v1.4.7+)
- **KYC/AML Tools**: Identity verification, sanctions screening, risk scoring
- **Credit Assessment**: Credit scoring, DTI calculation, eligibility
- **Loan Processing**: EMI calculation, amortization schedules
- **Fraud Detection**: Transaction analysis, pattern detection
- **Compliance**: AML reporting, regulatory validation

### 🏭 Industry Template Categories

#### Workflow Templates (33 total)
| Category | Count | Examples |
|----------|-------|----------|
| Document Processing | 4 | PDF Extraction, Invoice Processing, Classification |
| Data Processing | 4 | ETL Pipeline, CSV Analyzer, Data Quality |
| Automation | 5 | Email Routing, Report Generator, Web Scraper |
| Financial Processing | 4 | Loan Application, Fraud Detection, KYC |
| Healthcare | 2 | Claims Processing, Patient Intake |
| Human Resources | 3 | Resume Screening, Onboarding, Performance Review |
| Legal | 2 | Contract Review, Compliance Check |
| Technology | 3 | Code Review, Incident Response, API Testing |

#### Agent Templates (36 total)
| Category | Count | Examples |
|----------|-------|----------|
| Analytics | 6 | Data Pipeline, ML Inference, Report Generator |
| Development | 4 | Code Reviewer, Debug Assistant, API Tester |
| Banking | 3 | Loan Processor, Fraud Detector, KYC Verification |
| Healthcare | 2 | Medical Assistant, Claims Processor |
| Legal | 2 | Contract Analyst, Compliance Monitor |
| Customer Service | 3 | Support Agent, FAQ Bot, Complaint Handler |

### 🔐 Security & RBAC
- **Role-Based Access**: Super Admin, Domain Admin, Agent Developer, Agent User
- **LLM Permissions**: Model-level access control
- **API Key Management**: Secure key generation and rotation
- **Audit Logging**: Complete activity tracking

### 🤝 LLM Provider Support
| Provider | Models | Status |
|----------|--------|--------|
| OpenAI | GPT-4o, GPT-4 Turbo, GPT-3.5 | ✅ Full |
| Anthropic | Claude 3.5, Claude 3 | ✅ Full |
| Google | Gemini Pro, Gemini Ultra | ✅ Full |
| Azure OpenAI | All GPT models | ✅ Full |
| AWS Bedrock | Claude, Titan, Llama | ✅ Full |
| Mistral | All models | ✅ Full |
| Groq | Llama, Mixtral | ✅ Full |
| Together AI | Open source models | ✅ Full |
| Cohere | Command models | ✅ Full |
| Hugging Face | Inference API | ✅ Full |
| Ollama | Local models | ✅ Full |

---

## 📁 Project Structure

```
abhikarta-llm-v1.4.9/
├── abhikarta-main/                   # Core library package
│   ├── src/abhikarta/                # Core library
│   │   ├── agent/                    # Agent management
│   │   ├── aiorg/                    # AI Organizations (v1.4.7)
│   │   ├── actor/                    # Actor system (v1.3.0)
│   │   ├── config/                   # Configuration
│   │   ├── core/                     # Core utilities
│   │   ├── database/                 # Database layer (44 tables)
│   │   │   ├── db_facade.py          # Database abstraction
│   │   │   ├── delegates/            # 10 delegate classes
│   │   │   └── schema/               # SQLite/PostgreSQL schemas
│   │   ├── hitl/                     # Human-in-the-Loop (v1.1.5)
│   │   ├── langchain/                # LangChain integration
│   │   ├── llm/                      # LLM Adapter
│   │   ├── llm_provider/             # LLM provider facade
│   │   ├── mcp/                      # MCP Integration (v1.1.6)
│   │   ├── messaging/                # Messaging (v1.3.0)
│   │   ├── notification/             # Notifications (v1.4.0)
│   │   ├── scripts/                  # Script template manager
│   │   ├── swarm/                    # Swarm orchestration (v1.3.0)
│   │   ├── tools/                    # Tool framework (10 types)
│   │   ├── user_management/          # User management
│   │   ├── utils/                    # Utilities
│   │   └── workflow/                 # Workflow engine
│   │
│   ├── entity_definitions/           # JSON entity templates
│   │   ├── agents/                   # Agent templates (12)
│   │   ├── workflows/                # Workflow templates (22)
│   │   ├── swarms/                   # Swarm templates (5)
│   │   ├── aiorg/                    # AI Org templates (5)
│   │   └── scripts/                  # Script templates (7)
│   │
│   ├── examples/                     # Python/JSON examples
│   ├── pyproject.toml                # Package configuration
│   └── README.md                     # Core library docs
│
├── abhikarta-web/                    # Web UI module (v1.4.9)
│   └── src/abhikarta_web/
│       ├── routes/                   # Flask route handlers
│       ├── templates/                # Jinja2 templates (60+ files)
│       └── static/                   # CSS, JS, images
│
├── abhikarta-sdk-client/             # API Client SDK (v1.4.9)
│   └── src/abhikarta_client/
│       ├── client.py                 # Main client class
│       ├── agents.py                 # Agents API
│       ├── workflows.py              # Workflows API
│       ├── swarms.py                 # Swarms API
│       └── organizations.py          # Organizations API
│
├── abhikarta-sdk-embedded/           # Embedded SDK (v1.4.9)
│   └── src/abhikarta_embedded/
│       ├── core.py                   # Main Abhikarta class
│       ├── agents/                   # Agent implementations
│       ├── workflows/                # Workflow engine
│       ├── swarms/                   # Swarm engine
│       ├── orgs/                     # Organization engine
│       ├── providers/                # LLM providers
│       ├── tools/                    # Tool framework
│       └── decorators.py             # @agent, @tool, etc.
│
├── config/
│   └── application.properties        # Configuration
├── data/                             # Runtime data
├── docs/
│   ├── sdk/                          # SDK documentation
│   ├── DESIGN.md                     # Architecture design
│   └── QUICKSTART.md                 # Quick start guide
├── logs/                             # Application logs
├── tests/                            # Test suite
├── requirements.txt                  # Python dependencies
├── run_server.py                     # Application entry point
└── LICENSE                           # License file
```

---

## 🛠 Installation

### Prerequisites
- Python 3.9+
- PostgreSQL 12+ (recommended) or SQLite
- 4GB+ RAM

### Quick Install

```bash
# Clone repository
git clone https://github.com/your-org/abhikarta-llm.git
cd abhikarta-llm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure application
cp config/application.properties.example config/application.properties
# Edit config/application.properties with your settings

# Run server (database auto-initializes)
python run_server.py
```

### Access the Application
- **Web UI**: http://localhost:5000
- **Default Login**: admin / admin123 (change immediately)
- **Tools Page**: http://localhost:5000/tools

---

## 📊 Database Schema

The platform uses 45 tables across these categories:

| Category | Tables |
|----------|--------|
| **Core** | agents, workflows, executions, execution_steps |
| **Users** | users, api_keys, audit_logs |
| **LLM** | llm_providers, llm_models, llm_model_permissions, llm_logs |
| **Tools** | mcp_servers, mcp_tools, code_fragments |
| **HITL** | hitl_tasks, hitl_comments, hitl_assignments |
| **Swarms** | swarms, swarm_agents, swarm_executions (v1.3.0) |
| **AI Orgs** | ai_organizations, ai_org_nodes, ai_org_tasks (v1.4.7) |
| **Notifications** | notification_channels, notification_templates (v1.4.0) |
| **Scripts** | python_scripts, script_executions (v1.4.9) |
| **Config** | settings, templates |

---

## 🏦 Banking Industry Solutions

### Pre-built Agents

| Agent | Use Case |
|-------|----------|
| KYC Verification | Identity verification, risk scoring, sanctions screening |
| Loan Processing | Credit evaluation, eligibility, amortization |
| Fraud Detection | Transaction analysis, pattern detection, SAR |
| Credit Risk | Risk assessment, tier classification, pricing |
| Customer Service | Account inquiries, product info, disputes |
| Account Opening | Guided onboarding, document verification |
| Compliance Officer | Regulatory monitoring, AML reporting |
| Investment Advisor | Portfolio recommendations, risk profiling |
| Collections | Debt recovery, payment plans |
| Document Processor | Document classification, data extraction |

### Pre-built Workflows

| Workflow | Description |
|----------|-------------|
| Loan Application | End-to-end loan processing with HITL |
| Customer Onboarding | KYC → Verification → Account Creation |
| Transaction Monitoring | Real-time fraud detection and AML |
| Mortgage Application | Full underwriting workflow |
| Credit Card Application | Application to issuance |
| Wire Transfer | OFAC screening, execution, CTR |
| Dispute Resolution | Classification, investigation, resolution |

---

## 🔧 Tool Framework Architecture

Abhikarta provides a **comprehensive tool framework** with 10 extensible base classes. The platform does NOT include pre-packaged tools - instead it provides the infrastructure for you to build custom tools.

### Tool Base Classes

| Class | Purpose |
|-------|---------|
| `BaseTool` | Abstract base for all tools |
| `FunctionTool` | Python function wrapper |
| `HTTPTool` | REST API integration |
| `MCPTool` | Model Context Protocol tools |
| `CodeFragmentTool` | Database-stored code |
| `LangChainTool` | LangChain integration |

### Banking Tool Classes (Example Implementations)
- **KYCTool**: Identity verification, risk scoring
- **CreditTool**: Credit assessment, scoring
- **LoanTool**: Loan processing, EMI calculation
- **ComplianceTool**: AML, sanctions screening
- **FraudTool**: Transaction analysis

### Integration Tool Patterns
- **HTTP/API**: REST client patterns with retry
- **Notifications**: Email, SMS, webhook patterns
- **Data Transform**: Field mapping, conversion
- **Workflow**: Context management, conditions

### Creating Custom Tools
```python
from abhikarta.tools import BaseTool

class MyTool(BaseTool):
    name = "my_tool"
    description = "My custom tool"
    
    def execute(self, **params):
        # Your implementation
        return {"result": "success"}
```

---

## 📚 API Reference

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/agents` | List agents |
| POST | `/api/agents` | Create agent |
| GET | `/api/agents/{id}` | Get agent |
| PUT | `/api/agents/{id}` | Update agent |
| DELETE | `/api/agents/{id}` | Delete agent |
| POST | `/api/agents/{id}/execute` | Execute agent |
| GET | `/api/workflows` | List workflows |
| POST | `/api/workflows` | Create workflow |
| POST | `/api/workflows/{id}/execute` | Execute workflow |
| GET | `/api/executions` | List executions |
| GET | `/api/executions/{id}` | Get execution details |
| GET | `/api/hitl/tasks` | List HITL tasks |
| POST | `/api/hitl/tasks/{id}/complete` | Complete HITL task |
| GET | `/api/tools` | List all tools |
| GET | `/api/tools/{name}` | Get tool details |
| POST | `/api/tools/{name}/execute` | Execute tool |
| POST | `/api/tools/refresh-mcp` | Refresh MCP tools (admin) |

---

## 🔒 Security

- **Authentication**: Session-based with secure cookies
- **Password Hashing**: bcrypt with salt
- **RBAC**: Four-tier role system
- **API Keys**: Secure generation with rotation
- **Audit Logging**: Complete activity tracking
- **Input Validation**: Comprehensive sanitization

---

## 📈 Version History

| Version | Date | Highlights |
|---------|------|------------|
| 1.4.8 | 2025-01 | Modular SDK Architecture: SDK Client, SDK Embedded, abhikarta-web module, Python Script Mode enhancements, decorator-based API |
| 1.4.7 | 2025-01 | AI Organizations: AI-powered org charts with hierarchical delegation, HITL, visual designer, task aggregation |
| 1.4.0 | 2025-01 | Visual Designer bug fixes (MCP tool nodes), Tool selection in properties, Agent Designer How-To Guide |
| 1.2.3 | 2025-01 | Template Libraries (36 agent, 33 workflow), Code Fragment URIs, Actor System, Modular Database Delegates |
| 1.2.0 | 2025-01 | Database Schema documentation (44 tables), Page glossaries, Enhanced help system |
| 1.1.8 | 2025-01 | Tool View/Test pages, dedicated tool detail UI, form-based testing |
| 1.1.7 | 2025-01 | Tool framework (10 base classes), Tools page, MCP auto-sync, Banking tool classes |
| 1.1.6 | 2025-01 | Tools System, MCP Integration, ToolsRegistry |
| 1.1.5 | 2025-01 | HITL System, Execution Progress, Visual Workflow Designer |
| 1.1.0 | 2024-12 | LLM Management, Visual Agent Designer, LangChain integration |
| 1.0.1 | 2024-12 | Code Fragments (db://, file://, s3://) |
| 1.0.0 | 2024-12 | Initial release |

---

## 📄 License

Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.

This software is proprietary. See [LICENSE](LICENSE) for details.

---

## 🤝 Support

- **Documentation**: Access in-app help at `/help`
- **Issues**: Report via GitHub Issues
- **Email**: support@abhikarta.com

---

*Built with ❤️ for enterprise AI automation*
