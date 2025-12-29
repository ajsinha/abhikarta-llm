# Abhikarta-LLM Documentation

**Version:** 1.2.5  
**Copyright:** © 2025-2030 Ashutosh Sinha. All Rights Reserved.

## Documentation Index

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Project overview and features |
| [QUICKSTART.md](QUICKSTART.md) | Quick start guide |
| [DESIGN.md](DESIGN.md) | Architecture and design |
| [REQUIREMENTS.md](REQUIREMENTS.md) | Requirements specification |

## Version 1.2.5 Features

### Actor System (NEW - Pekko-Inspired)
- **ActorSystem**: Complete runtime for creating and managing millions of actors
- **Actor Base Classes**: `Actor`, `TypedActor` with decorator-based handlers
- **Message Patterns**: Tell (fire-and-forget), Ask (request-response), Forward
- **Supervision Strategies**: OneForOneStrategy, AllForOneStrategy, ExponentialBackoff
- **Dispatchers**: Default, Pinned, ForkJoin for different workloads
- **Mailboxes**: Unbounded, Bounded (backpressure), Priority, ControlAware
- **Patterns**: Router (load balancing), EventBus (pub/sub), CircuitBreaker, Stashing
- **Scheduling**: Delayed and periodic message delivery
- **Fault Tolerance**: Automatic restart, supervision hierarchies, death watch
- **Acknowledgement**: Inspired by Apache Pekko (incubating)

### Tool View & Test Pages
- **Tool Detail Page** (`/tools/{name}`): Complete tool information with parameters, schema, and metadata
- **Tool Test Page** (`/tools/{name}/test`): Form-based parameter input with type-specific controls
- **JSON Schema Display**: View and copy complete tool schema
- **Breadcrumb Navigation**: Easy navigation between tools list, detail, and test pages
- **Result Display**: Formatted execution results with request/response info

### Pre-built Tools Library (85)
- **Common Tools (28)**: Date/time, math, text processing, validation, format conversion, ID generation
- **Banking Tools (13)**: KYC verification, credit scoring, loan processing, transaction analysis, compliance
- **Integration Tools (20)**: HTTP/API, notifications, data transformation, list/array operations, workflow helpers
- **General Tools (24)**: Web search, document handling, file operations, system utilities, network tools

### Tools Management Page
- **Centralized Tools View**: Browse all tools at `/tools`
- **Search & Filter**: Find tools by name, category, or source
- **DataTables Integration**: Pagination, sorting, search
- **Quick Actions**: View and Test buttons for each tool
- **MCP Auto-Sync**: Tools automatically sync when MCP servers connect/disconnect

### Banking Industry Solutions
- **10 Pre-built Agents**: KYC Verification, Loan Processing, Fraud Detection, Credit Risk, Customer Service, Account Opening, Compliance Officer, Investment Advisor, Collections, Document Processor
- **7 Pre-built Workflows**: Loan Application, Customer Onboarding, Transaction Monitoring, Mortgage Application, Credit Card Application, Wire Transfer, Dispute Resolution

### Auto-initialization at Startup
- Pre-built tools automatically registered on server start
- MCP servers auto-connect from database
- Background health monitor for MCP servers

## Previous Version Highlights

### v1.1.7: Pre-built Tools & Banking Solutions
- 85 pre-built tools (Common, Banking, Integration, General)
- 10 banking agents and 7 banking workflows
- Tools registry page with search/filter
- MCP auto-connect on startup

### v1.1.6: Tools System & MCP Integration
- Unified tools architecture with BaseTool
- ToolsRegistry for centralized management
- MCPServerManager for MCP lifecycle
- Format conversion for all LLM providers

### v1.1.5: Human-in-the-Loop
- HITL task management
- Execution progress monitoring
- Visual workflow designer

### v1.1.0: LLM Management
- Multi-provider LLM configuration
- Model permissions with RBAC
- Visual agent designer

### v1.0.1: Code Fragments
- db://, file://, s3:// URI support
- Reusable code modules

## Quick Links

### In-App Help
- `/help` - Main documentation hub
- `/tools` - Tools registry browser
- `/tools/{name}` - Tool detail page
- `/tools/{name}/test` - Tool test page
- `/help/page/prebuilt-tools` - Pre-built tools reference
- `/help/page/banking-solutions` - Banking solutions guide
- `/help/page/tools-system` - Tools system documentation
- `/help/about/architecture` - System architecture

### API Reference
- `/help/page/api-reference` - REST API documentation
- `/api/tools` - Tools list API
- `/api/tools/{name}` - Tool details API
- `/api/tools/{name}/execute` - Tool execution API

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                           │
│         Flask Web UI │ REST API │ Help Documentation            │
│         Tools Page (/tools) │ MCP Management                    │
├─────────────────────────────────────────────────────────────────┤
│                     APPLICATION LAYER                            │
│    Agent Manager │ Workflow Engine │ HITL Manager                │
├─────────────────────────────────────────────────────────────────┤
│                        TOOLS LAYER                               │
│  BaseTool │ FunctionTool │ MCPTool │ HTTPTool │ ToolsRegistry   │
│  Pre-built Tools: Common(28)│Banking(13)│Integration(20)│General(24)│
├─────────────────────────────────────────────────────────────────┤
│                     INTEGRATION LAYER                            │
│    LangChain │ LangGraph │ MCP Clients │ LLM Providers (11)     │
├─────────────────────────────────────────────────────────────────┤
│                        DATA LAYER                                │
│         PostgreSQL/SQLite │ 22 Tables │ Audit Logs              │
└─────────────────────────────────────────────────────────────────┘
```

## Key Statistics

| Metric | Count |
|--------|-------|
| LLM Providers | 11 |
| Pre-built Tools | 85 |
| Banking Agents | 10 |
| Banking Workflows | 7 |
| Database Tables | 22 |
| Workflow Node Types | 10 |
| Help Pages | 30+ |

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 1.2.5 | Jan 2025 | Modular Database Delegates (9 delegates), DatabaseDelegate abstract class |
| 1.2.0 | Jan 2025 | Database Schema docs (22 tables), Page glossaries, Enhanced help |
| 1.1.8 | Jan 2025 | Tool View/Test pages, dedicated tool detail UI, form-based testing |
| 1.1.7 | Jan 2025 | Pre-built tools (85), Tools page, General tools, MCP auto-sync |
| 1.1.6 | Jan 2025 | Tools System, MCP Integration, ToolsRegistry |
| 1.1.5 | Jan 2025 | HITL System, Execution Progress, Visual Workflow Designer |
| 1.1.0 | Dec 2024 | LLM Management, Visual Agent Designer, LangChain |
| 1.0.1 | Dec 2024 | Code Fragments (db://, file://, s3://) |
| 1.0.0 | Dec 2024 | Initial release |

---

*For the most up-to-date documentation, access the in-app help at `/help`.*
