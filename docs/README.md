# Abhikarta-LLM Documentation

**Version:** 1.1.7  
**Copyright:** © 2025-2030 Ashutosh Sinha. All Rights Reserved.

## Documentation Index

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Project overview and features |
| [QUICKSTART.md](QUICKSTART.md) | Quick start guide |
| [DESIGN.md](DESIGN.md) | Architecture and design |
| [REQUIREMENTS.md](REQUIREMENTS.md) | Requirements specification |

## Version 1.1.7 Features

### Pre-built Tools Library (60+)
- **Common Tools (28)**: Date/time, math, text processing, validation, format conversion, ID generation
- **Banking Tools (13)**: KYC verification, credit scoring, loan processing, transaction analysis, compliance
- **Integration Tools (20)**: HTTP/API, notifications, data transformation, list/array operations, workflow helpers

### Banking Industry Solutions
- **10 Pre-built Agents**: KYC Verification, Loan Processing, Fraud Detection, Credit Risk, Customer Service, Account Opening, Compliance Officer, Investment Advisor, Collections, Document Processor
- **7 Pre-built Workflows**: Loan Application, Customer Onboarding, Transaction Monitoring, Mortgage Application, Credit Card Application, Wire Transfer, Dispute Resolution

### Comprehensive Documentation
- Updated help pages for all features
- Banking solutions guide
- Pre-built tools reference

## Previous Version Highlights

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
- `/help/page/prebuilt-tools` - Pre-built tools reference
- `/help/page/banking-solutions` - Banking solutions guide
- `/help/page/tools-system` - Tools system documentation
- `/help/about/architecture` - System architecture

### API Reference
- `/help/page/api-reference` - REST API documentation

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                           │
│         Flask Web UI │ REST API │ Help Documentation            │
├─────────────────────────────────────────────────────────────────┤
│                     APPLICATION LAYER                            │
│    Agent Manager │ Workflow Engine │ HITL Manager                │
├─────────────────────────────────────────────────────────────────┤
│                        TOOLS LAYER                               │
│  BaseTool │ FunctionTool │ MCPTool │ HTTPTool │ ToolsRegistry   │
│  Pre-built Tools: Common (28) │ Banking (13) │ Integration (20) │
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
| Pre-built Tools | 60+ |
| Banking Agents | 10 |
| Banking Workflows | 7 |
| Database Tables | 22 |
| Workflow Node Types | 10 |
| Help Pages | 30+ |

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 1.1.7 | Jan 2025 | Pre-built tools (60+), banking solutions, comprehensive docs |
| 1.1.6 | Jan 2025 | Tools System, MCP Integration, ToolsRegistry |
| 1.1.5 | Jan 2025 | HITL System, Execution Progress, Visual Workflow Designer |
| 1.1.0 | Dec 2024 | LLM Management, Visual Agent Designer, LangChain |
| 1.0.1 | Dec 2024 | Code Fragments (db://, file://, s3://) |
| 1.0.0 | Dec 2024 | Initial release |

---

*For the most up-to-date documentation, access the in-app help at `/help`.*
