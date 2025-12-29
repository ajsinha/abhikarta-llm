# Abhikarta-LLM Documentation

**Version:** 1.4.0  
**Copyright:** © 2025-2030 Ashutosh Sinha. All Rights Reserved.

## Documentation Index

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Project overview and features |
| [QUICKSTART.md](QUICKSTART.md) | Quick start guide |
| [DESIGN.md](DESIGN.md) | Architecture and design |
| [REQUIREMENTS.md](REQUIREMENTS.md) | Requirements specification |
| [COT_TOT_TUTORIAL.md](COT_TOT_TUTORIAL.md) | Chain of Thought & Tree of Thought tutorial |
| [GOAL_BASED_AGENTS_TUTORIAL.md](GOAL_BASED_AGENTS_TUTORIAL.md) | Goal-Based Agents tutorial (autonomous, planning, learning) |
| [REACT_REFLECT_HIERARCHICAL_TUTORIAL.md](REACT_REFLECT_HIERARCHICAL_TUTORIAL.md) | ReAct, Reflect & Hierarchical Agents tutorial |
| [NOTIFICATION_QUICKSTART.md](NOTIFICATION_QUICKSTART.md) | Notifications quick start |
| [NOTIFICATION_ARCHITECTURE.md](NOTIFICATION_ARCHITECTURE.md) | Notifications architecture |
| [PATENT_APPLICATION.md](PATENT_APPLICATION.md) | Patent application (21 claims) |
| [PATENT_WORTHINESS_ANALYSIS.md](PATENT_WORTHINESS_ANALYSIS.md) | Patent worthiness analysis |

## Version 1.4.0 Features (Latest)

### Enterprise Notification System (NEW)
- **NotificationManager**: Central orchestrator for multi-channel routing
- **Slack Integration**: Channel messages, DMs, Block Kit formatting, thread replies
- **Microsoft Teams**: Incoming Webhooks, Adaptive Cards, MessageCard format
- **Email**: SMTP integration with templates
- **Rate Limiting**: Token bucket algorithm per channel
- **Retry Logic**: Exponential backoff for failed deliveries
- **Audit Logging**: Complete notification history

### Webhook Receiver (NEW)
- **Endpoint Registration**: Custom URL paths with authentication
- **Signature Verification**: HMAC-SHA256, JWT, API key, Basic auth
- **Replay Protection**: Nonce tracking and timestamp validation
- **Event Dispatching**: Trigger agents, workflows, or swarms
- **Event Logging**: Full request/response logging

### Chain of Thought & Tree of Thought (NEW Tutorial)
- **CoT Agent Type**: Pre-configured for step-by-step reasoning
- **ToT Workflows**: Parallel exploration with evaluation
- **Best Practices**: Temperature settings, token budgeting
- **Integration**: Works with agents, workflows, and swarms

### Database Updates
- 5 new tables for notifications (27 total)
- NotificationDelegate for all notification operations
- Schema version 1.4.0

## Version 1.3.0 Features

### Agent Swarms (Pekko-Inspired)
- **Master Actor**: LLM-powered choreography for task delegation
- **Agent Pools**: Pre-warmed instances with round-robin selection
- **Event Bus**: Internal pub/sub for swarm communication
- **Triggers**: Kafka, RabbitMQ, HTTP, Cron, Manual

### Messaging Module
- **Unified Interface**: Single API for Kafka, RabbitMQ, ActiveMQ
- **Backpressure**: Block, Drop Oldest/Newest, Sample strategies
- **Dead Letter Queue**: Failed message handling

### Actor System
- **ActorSystem**: Runtime for millions of concurrent actors
- **Supervision**: OneForOne, AllForOne, ExponentialBackoff
- **Dispatchers**: Default, Pinned, ForkJoin
- **Mailboxes**: Unbounded, Bounded, Priority

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
- `/help/prebuilt-tools` - Pre-built tools reference
- `/help/banking-solutions` - Banking solutions guide
- `/help/tools-system` - Tools system documentation
- `/help/about/architecture` - System architecture

### API Reference
- `/help/api-reference` - REST API documentation
- `/api/tools` - Tools list API
- `/api/tools/{name}` - Tool details API
- `/api/tools/{name}/execute` - Tool execution API

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                           │
│         Flask Web UI │ REST API │ Help Documentation            │
│         Tools Page (/tools) │ Notifications │ MCP Management    │
├─────────────────────────────────────────────────────────────────┤
│                     APPLICATION LAYER                            │
│    Agent Manager │ Workflow Engine │ Swarm Orchestrator         │
│    HITL Manager │ NotificationManager │ WebhookReceiver         │
├─────────────────────────────────────────────────────────────────┤
│                        TOOLS LAYER                               │
│  BaseTool │ FunctionTool │ MCPTool │ HTTPTool │ ToolsRegistry   │
│  Pre-built: Common(28)│Banking(13)│Integration(20)│General(24)  │
├─────────────────────────────────────────────────────────────────┤
│                     INTEGRATION LAYER                            │
│    LangChain │ LangGraph │ MCP │ Kafka/RabbitMQ │ Slack/Teams   │
├─────────────────────────────────────────────────────────────────┤
│                        DATA LAYER                                │
│         PostgreSQL/SQLite │ 27 Tables │ 9 Delegates             │
└─────────────────────────────────────────────────────────────────┘
```

## Key Statistics

| Metric | Count |
|--------|-------|
| LLM Providers | 11 |
| Pre-built Tools | 85 |
| Banking Agents | 10 |
| Banking Workflows | 7 |
| Database Tables | 27 |
| Database Delegates | 9 |
| Workflow Node Types | 10 |
| Patent Claims | 21 |
| Help Pages | 35+ |

## Quick Links

### In-App Help
- `/help` - Main documentation hub
- `/tools` - Tools registry browser
- `/admin/notifications` - Notification channels
- `/help/notifications` - Notifications guide
- `/help/cot-tot` - CoT/ToT tutorial
- `/help/swarms` - Agent swarms guide
- `/help/banking-solutions` - Banking solutions guide

### API Reference
- `/help/api-reference` - REST API documentation
- `/api/tools` - Tools list API
- `/api/notifications` - Notifications API
- `/api/webhooks` - Webhook receiver API

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 1.4.0 | Dec 2025 | Notifications (Slack/Teams/Webhooks), CoT/ToT Tutorial, 21 Patent Claims |
| 1.3.0 | Dec 2025 | Agent Swarms, Messaging (Kafka/RabbitMQ), Actor System |
| 1.2.0 | Jan 2025 | Database Schema docs (22 tables), Page glossaries |
| 1.1.8 | Jan 2025 | Tool View/Test pages, form-based testing |
| 1.1.7 | Jan 2025 | Pre-built tools (85), Tools page, MCP auto-sync |
| 1.1.0 | Dec 2024 | LLM Management, Visual Agent Designer |
| 1.0.0 | Dec 2024 | Initial release |

---

*For the most up-to-date documentation, access the in-app help at `/help`.*
