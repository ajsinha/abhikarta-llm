# Abhikarta-LLM v1.4.5

[![Version](https://img.shields.io/badge/version-1.4.5-blue.svg)](https://github.com/abhikarta-llm)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

**Enterprise-grade AI Agent & Workflow Orchestration Platform with Agent Swarms and Enterprise Notifications**

Abhikarta-LLM is a comprehensive platform for building, deploying, and managing AI agents, workflows, and intelligent agent swarms with multi-provider LLM support, visual designers, human-in-the-loop controls, enterprise notifications, and industry-specific solutions.

---

## 🚀 What's New in v1.4.5

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

### Pre-built Tools Library (85 Tools)
- **Common Tools (28)**: Date/time, math, text processing, validation, format conversion
- **Banking Tools (13)**: KYC verification, credit scoring, loan processing, compliance
- **Integration Tools (20)**: HTTP/API, notifications, data transformation, workflow helpers
- **General Tools (24)**: Web search, document handling, file operations, system utilities

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

### ⚡ Actor System (v1.4.5 NEW)
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
- **85+ Pre-built Tools**: Ready for immediate use
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

### 🏦 Banking Solutions (v1.4.5+)
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
abhikarta-llm-v1.4.5/
├── abhikarta/
│   ├── __init__.py
│   ├── agent/                    # Agent management
│   │   ├── agent_manager.py      # Agent CRUD operations
│   │   └── agent_template.py     # Agent templates
│   ├── config/                   # Configuration
│   │   └── settings.py           # App settings
│   ├── core/                     # Core utilities
│   │   └── config/               # Properties configuration
│   ├── database/                 # Database layer
│   │   ├── db_facade.py          # Database abstraction
│   │   ├── sqlite_handler.py     # SQLite implementation
│   │   ├── postgres_handler.py   # PostgreSQL implementation
│   │   └── schema/               # 22 database tables
│   ├── hitl/                     # Human-in-the-Loop (v1.1.5)
│   │   └── hitl_manager.py       # HITL task management
│   ├── langchain/                # LangChain integration
│   │   ├── agents.py             # LangChain agent factory
│   │   ├── llm_factory.py        # LLM provider factory
│   │   ├── tools.py              # Tool adapters
│   │   └── workflow_graph.py     # LangGraph integration
│   ├── llm/                      # LLM Adapter (v1.4.5) NEW!
│   │   ├── __init__.py           # Module exports
│   │   └── adapter.py            # LLMAdapter, async interface
│   ├── llm_provider/             # LLM abstraction
│   │   └── llm_facade.py         # Multi-provider facade
│   ├── mcp/                      # MCP Integration (v1.1.6)
│   │   ├── server.py             # MCPServer, MCPServerConfig
│   │   ├── client.py             # HTTP/WebSocket clients
│   │   └── manager.py            # MCPServerManager singleton
│   ├── rbac/                     # Role-based access control
│   │   └── __init__.py           # RBAC decorators
│   ├── tools/                    # Tools System (v1.1.6)
│   │   ├── base_tool.py          # BaseTool, ToolSchema, ToolResult
│   │   ├── function_tool.py      # FunctionTool, @tool decorator
│   │   ├── mcp_tool.py           # MCPTool wrapper
│   │   ├── http_tool.py          # HTTPTool, WebhookTool
│   │   ├── code_fragment_tool.py # CodeFragmentTool
│   │   ├── langchain_tool.py     # LangChain integration
│   │   ├── registry.py           # ToolsRegistry singleton
│   │   └── prebuilt/             # Pre-built tools (v1.4.5)
│   │       ├── common_tools.py   # 28 common utilities
│   │       ├── banking_tools.py  # 13 banking tools
│   │       ├── integration_tools.py  # 20 integration tools
│   │       └── general_tools.py  # 24 general-purpose tools
│   ├── user_management/          # User management
│   │   └── user_facade.py        # User CRUD operations
│   ├── utils/                    # Utilities
│   │   ├── code_loader.py        # Code fragment loader
│   │   ├── helpers.py            # Helper functions
│   │   ├── llm_logger.py         # LLM call logging
│   │   └── logger.py             # Application logging
│   ├── web/                      # Web application
│   │   ├── app.py                # Flask app factory
│   │   ├── routes/               # Route blueprints
│   │   │   ├── admin_routes.py   # Admin endpoints
│   │   │   ├── agent_routes.py   # Agent endpoints
│   │   │   ├── api_routes.py     # REST API
│   │   │   ├── auth_routes.py    # Authentication
│   │   │   ├── mcp_routes.py     # MCP management
│   │   │   ├── user_routes.py    # User endpoints + Tools
│   │   │   └── workflow_routes.py # Workflow endpoints
│   │   ├── static/               # CSS, JS, images
│   │   └── templates/            # Jinja2 templates (50+ files)
│   │       ├── admin/            # Admin UI
│   │       ├── agents/           # Agent UI
│   │       ├── help/             # Documentation (30+ pages)
│   │       ├── user/             # User UI + tools.html
│   │       └── workflows/        # Workflow UI
│   └── workflow/                 # Workflow engine
│       ├── dag_parser.py         # DAG parsing
│       ├── executor.py           # Workflow execution
│       └── node_types.py         # Node implementations
├── config/
│   └── application.properties    # Configuration file
├── data/
│   └── prebuilt/                 # Pre-built solutions (v1.4.5)
│       ├── agents/
│       │   └── banking/          # 10 banking agents
│       └── workflows/
│           └── banking/          # 7 banking workflows
├── docs/
│   ├── README.md                 # Documentation index
│   ├── QUICKSTART.md             # Quick start guide
│   ├── DESIGN.md                 # Architecture design
│   └── REQUIREMENTS.md           # Requirements spec
├── logs/                         # Application logs
├── tests/                        # Test suite
├── requirements.txt              # Python dependencies
├── run_server.py                 # Application entry point
└── LICENSE                       # License file
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

The platform uses 22 tables across these categories:

| Category | Tables |
|----------|--------|
| **Core** | agents, workflows, executions, execution_steps |
| **Users** | users, api_keys, audit_logs |
| **LLM** | llm_providers, llm_models, llm_model_permissions, llm_logs |
| **Tools** | mcp_servers, mcp_tools, code_fragments |
| **HITL** | hitl_tasks, hitl_comments, hitl_assignments |
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

## 🔧 Pre-built Tools (85 Total)

### Common Tools (28)
- **Date/Time**: get_current_datetime, parse_date, calculate_date_difference, add_days_to_date, get_business_days
- **Math**: calculate_expression, calculate_percentage, calculate_compound_interest, calculate_loan_emi, convert_currency
- **Text**: extract_text_patterns, clean_text, extract_entities, generate_summary_stats, mask_sensitive_data
- **Validation**: validate_email, validate_phone, validate_credit_card, validate_iban, validate_ssn
- **Conversion**: json_to_csv, csv_to_json, base64_encode, base64_decode, generate_hash
- **ID Generation**: generate_uuid, generate_reference_number, generate_account_number

### Banking Tools (13)
- **KYC**: verify_identity_document, calculate_kyc_risk_score, verify_address
- **Credit**: calculate_credit_score, assess_debt_to_income
- **Loan**: calculate_loan_eligibility, generate_amortization_schedule
- **Transaction**: analyze_transaction, detect_transaction_patterns, calculate_transaction_limits
- **Compliance**: check_sanctions_list, generate_aml_report, validate_regulatory_compliance

### Integration Tools (20)
- **HTTP/API**: make_http_request, build_query_string, parse_json_response, validate_api_response
- **Notifications**: format_email_template, create_notification, format_sms_message
- **Data Transform**: map_fields, flatten_nested_dict, unflatten_dict, merge_dicts, filter_dict_keys
- **List/Array**: filter_list, sort_list, group_by, aggregate_list, paginate_list
- **Workflow**: create_workflow_context, update_workflow_context, evaluate_condition

### General Tools (24) - NEW
- **Web/Search**: web_search, web_fetch, intranet_search, news_search
- **Document Handling**: read_document, write_document, convert_document, extract_document_metadata
- **File Operations**: list_files, copy_file, move_file, delete_file
- **System Utilities**: get_system_info, execute_shell_command, get_environment_variable, set_environment_variable
- **Network Tools**: check_url_status, ping_host, dns_lookup, parse_url
- **Encoding**: url_encode, url_decode, html_encode, html_decode

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
| 1.4.5 | 2025-01 | AI Organizations: AI-powered org charts with hierarchical delegation, HITL, visual designer, task aggregation |
| 1.4.0 | 2025-01 | Visual Designer bug fixes (MCP tool nodes), Tool selection in properties, Agent Designer How-To Guide |
| 1.2.3 | 2025-01 | Template Libraries (36 agent, 33 workflow), Code Fragment URIs, Actor System, Modular Database Delegates |
| 1.2.0 | 2025-01 | Database Schema documentation (22 tables), Page glossaries, Enhanced help system |
| 1.1.8 | 2025-01 | Tool View/Test pages, dedicated tool detail UI, form-based testing |
| 1.1.7 | 2025-01 | Pre-built tools (85), Tools page, General tools, MCP auto-sync, Banking solutions |
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
