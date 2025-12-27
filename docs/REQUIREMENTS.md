# Abhikarta-LLM
## AI Agent Design & Orchestration Platform
### Product Requirements Document

**Version:** 2.0  
**Date:** December 2025  
**Classification:** CONFIDENTIAL

---

## Copyright and Legal Notice

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email:** ajsinha@gmail.com

### Legal Notice

This document and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use of this document or the software system it describes is strictly prohibited without explicit written permission from the copyright holder. This document is provided "as is" without warranty of any kind, either expressed or implied. The copyright holder shall not be liable for any damages arising from the use of this document or the software system it describes.

**Patent Pending:** Certain architectural patterns and implementations described in this document may be subject to patent applications.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Vision & Strategic Goals](#2-vision--strategic-goals)
3. [System Architecture](#3-system-architecture)
4. [Technical Stack & Requirements](#4-technical-stack--requirements)
5. [Functional Requirements](#5-functional-requirements)
6. [Admin Portal & Agent Management](#6-admin-portal--agent-management)
7. [Role-Based Access Control (RBAC)](#7-role-based-access-control-rbac)
8. [Human-in-the-Loop (HITL) Framework](#8-human-in-the-loop-hitl-framework)
9. [LLM Abstraction Layer (Facade)](#9-llm-abstraction-layer-facade)
10. [MCP Plugin Framework](#10-mcp-plugin-framework)
11. [UI/UX Requirements](#11-uiux-requirements)
12. [Non-Functional Requirements](#12-non-functional-requirements)
13. [Deployment & Infrastructure](#13-deployment--infrastructure)
14. [Project Timeline & Milestones](#14-project-timeline--milestones)
15. [Success Metrics & KPIs](#15-success-metrics--kpis)
16. [Risk Assessment & Mitigation](#16-risk-assessment--mitigation)
17. [Appendices](#17-appendices)

---

## 1. Executive Summary

Abhikarta-LLM is a next-generation, enterprise-grade AI agent design and orchestration platform built on low-code/no-code principles. The platform features a comprehensive Admin Portal where administrators design, configure, and publish AI agents, while end users interact with approved agents through a controlled, RBAC-governed interface with full Human-in-the-Loop (HITL) support throughout the entire agent lifecycle.

### 1.1 Problem Statement

Current AI agent development faces critical challenges: high technical barriers, vendor lock-in with specific LLM providers, complex orchestration requirements, inadequate governance models, lack of human oversight in critical workflows, and poor separation between agent development and agent consumption. Organizations need a platform that separates concerns—administrators build agents, users consume them—with proper controls at every step.

### 1.2 Proposed Solution

Abhikarta-LLM addresses these challenges through:

- Visual drag-and-drop agent designer in Admin Portal with production-ready code generation
- Admin-controlled agent publishing workflow—agents are built, tested, and approved before user access
- LLM-agnostic architecture via unified facade supporting **OpenAI, Anthropic, Ollama, and AWS Bedrock**
- Enterprise RBAC controlling which users can execute which agents
- End-to-end Human-in-the-Loop (HITL) support for approval, intervention, and oversight
- MCP Plugin Framework—any MCP server integrates via configuration as a plugin
- LangGraph-powered orchestration supporting all agent types and patterns
- Built-in Prometheus monitoring for real-time observability
- **Dual database support: SQLite and PostgreSQL** (configurable)

### 1.3 Key Differentiators

| Differentiator | Description |
|----------------|-------------|
| Admin-First Architecture | Clear separation: Admins build/configure agents; Users consume approved agents only |
| End-to-End HITL | Human oversight at every critical decision point—approvals, interventions, overrides |
| MCP Plugin System | Any MCP server integrates as a plugin via configuration—no code changes required |
| LLM Portability | Switch between OpenAI, Anthropic, Ollama, AWS Bedrock with zero code changes |
| All Agent Types | Supports every agent pattern: ReAct, Plan-Execute, Multi-Agent, Swarm, Custom |
| Enterprise RBAC | Granular control over who can run which agents with full audit logging |
| Prometheus Native | Out-of-the-box Prometheus metrics for monitoring, alerting, and observability |
| Database Flexibility | Configurable database backend: SQLite for development, PostgreSQL for production |

---

## 2. Vision & Strategic Goals

### 2.1 Product Vision

> *"To become the industry-standard platform for enterprise AI agent orchestration, where administrators effortlessly design and govern intelligent agents, users safely interact with approved agents under human oversight, and organizations maintain complete control over their AI operations."*

### 2.2 Strategic Objectives

1. **Market Leadership:** Achieve #1 market position in enterprise AI agent platforms within 24 months
2. **Governance Excellence:** Set industry standard for AI agent governance with HITL and RBAC
3. **Admin Productivity:** Enable 10x faster agent development through visual low-code tools
4. **Enterprise Adoption:** Secure 100+ enterprise customers in first 18 months post-launch
5. **Plugin Ecosystem:** Build marketplace with 200+ MCP plugins and agent templates

### 2.3 User Personas

| Persona | Profile | Key Needs |
|---------|---------|-----------|
| Platform Admin | IT/Platform team managing Abhikarta-LLM deployment | System config, user management, security, monitoring |
| Agent Developer | Technical staff designing and building agents | Visual designer, testing tools, version control |
| Agent Publisher | Manager who approves agents for production | Review workflows, approval gates, audit trails |
| Business User | End user who runs approved agents | Simple interface, clear instructions, HITL prompts |
| HITL Reviewer | Staff member handling human intervention requests | Clear task queue, context, decision support |

---

## 3. System Architecture

### 3.1 Architecture Overview

Abhikarta-LLM employs a modular, Python-based architecture designed for flexibility and ease of deployment. The system uses Flask for web serving, supports both SQLite and PostgreSQL databases (configurable), and Apache Kafka for event-driven messaging.

### 3.2 Module Structure

```
abhikarta/
├── __init__.py
├── config/                 # Configuration management
│   ├── __init__.py
│   ├── settings.py         # Application settings
│   └── database_config.py  # Database configuration
├── database/               # Database abstraction layer
│   ├── __init__.py
│   ├── db_facade.py        # Database facade (SQLite/PostgreSQL)
│   ├── sqlite_handler.py   # SQLite implementation
│   └── postgres_handler.py # PostgreSQL implementation
├── user_management/        # User and authentication
│   ├── __init__.py
│   ├── user_facade.py      # User management facade
│   ├── user_manager.py     # User operations
│   └── auth_manager.py     # Authentication logic
├── rbac/                   # Role-based access control
│   ├── __init__.py
│   ├── role_manager.py     # Role management
│   └── permission_manager.py
├── llm_provider/           # LLM abstraction layer
│   ├── __init__.py
│   ├── llm_facade.py       # Unified LLM interface
│   ├── llm_facade_factory.py
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   ├── ollama_provider.py
│   └── bedrock_provider.py
├── mcp/                    # MCP plugin framework
│   ├── __init__.py
│   ├── mcp_facade.py       # MCP abstraction
│   ├── mcp_server_manager.py
│   └── mcp_plugin_registry.py
├── agent/                  # Agent management
│   ├── __init__.py
│   ├── agent_manager.py
│   ├── agent_executor.py
│   └── agent_registry.py
├── hitl/                   # Human-in-the-loop
│   ├── __init__.py
│   ├── hitl_manager.py
│   └── hitl_queue.py
├── web/                    # Flask web application
│   ├── __init__.py
│   ├── app.py              # Flask app initialization
│   ├── routes/             # Route handlers
│   │   ├── __init__.py
│   │   ├── abstract_routes.py
│   │   ├── auth_routes.py
│   │   ├── admin_routes.py
│   │   ├── user_routes.py
│   │   ├── agent_routes.py
│   │   ├── mcp_routes.py
│   │   └── api_routes.py
│   ├── templates/          # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── admin/
│   │   ├── user/
│   │   ├── agents/
│   │   └── mcp/
│   └── static/             # Static assets
│       ├── css/
│       ├── js/
│       └── img/
└── utils/                  # Utilities
    ├── __init__.py
    ├── logger.py
    └── helpers.py
```

### 3.3 Architecture Layers

| Layer | Components & Responsibilities |
|-------|-------------------------------|
| Presentation Layer | Flask templates (Jinja2), jQuery/Bootstrap SPA, WebSocket connections |
| Application Layer | Flask REST APIs, WebSocket handlers, business logic, RBAC enforcement |
| Orchestration Layer | LangGraph execution engine, workflow state management, HITL checkpoints |
| Integration Layer | LLM Facade, MCP Plugin Framework, Apache Kafka event bus |
| Data Layer | Database Facade (SQLite/PostgreSQL), Redis (cache/sessions), File storage |
| Monitoring Layer | Prometheus metrics (native), logging, audit trails |

### 3.4 Database Architecture

#### 3.4.1 Database Flexibility

The system supports two database backends, selectable via configuration:

| Database | Use Case | Configuration |
|----------|----------|---------------|
| SQLite | Development, testing, small deployments | `DB_TYPE=sqlite` |
| PostgreSQL | Production, multi-user, scalability | `DB_TYPE=postgresql` |

#### 3.4.2 Schema Design Principles

- **Simple Design:** No foreign keys, primary indexes only
- **JSONB/TEXT:** Flexible metadata storage using JSON
- **Soft Deletes:** `is_active` flag instead of hard deletes
- **Timestamps:** `created_at`, `updated_at` on all tables

#### 3.4.3 Core Tables

| Table | Purpose |
|-------|---------|
| users | User accounts and profiles |
| roles | Role definitions |
| user_roles | User-role assignments |
| agents | Agent definitions |
| agent_versions | Agent version history |
| executions | Execution records |
| hitl_requests | HITL intervention requests |
| mcp_plugins | MCP plugin configurations |
| audit_logs | Audit trail |

---

## 4. Technical Stack & Requirements

### 4.1 Core Technology Stack

| Category | Technology | Justification |
|----------|------------|---------------|
| Backend Framework | Python 3.11+ / Flask 3.x | Native LangChain/LangGraph support |
| Frontend Framework | jQuery 3.7+ / Bootstrap 5.3+ | Proven stability, rapid development |
| AI Orchestration | LangChain 0.3+ / LangGraph | Industry-standard agent framework |
| Database | SQLite 3 / PostgreSQL 16+ | Configurable: dev vs. production |
| Caching | Redis 7+ | Session management, pub/sub |
| Message Queue | Apache Kafka 3.6+ | Event streaming, async processing |
| API Protocol | REST + WebSocket | CRUD operations, real-time streaming |
| Tool Protocol | Model Context Protocol (MCP) | Anthropic's standard for tools |
| Monitoring | Prometheus + Grafana | Native metrics, dashboards |

### 4.2 LLM Providers (4 Supported)

| Provider | Models | Capabilities |
|----------|--------|--------------|
| OpenAI | GPT-4o, GPT-4 Turbo, GPT-3.5, o1, o3 | Chat, vision, embeddings, function calling |
| Anthropic | Claude 3.5 Sonnet, Claude 3 Opus/Haiku | Chat, vision, long context, MCP native |
| Ollama (Local) | Llama 3, Mistral, Phi, Gemma, custom | On-premise, air-gapped, custom models |
| AWS Bedrock | Claude, Llama, Titan, Mistral | VPC deployment, AWS integration |

### 4.3 Python Package Requirements

```
flask>=3.0.0
flask-socketio>=5.3.0
flask-cors>=4.0.0
langchain>=0.3.0
langgraph>=0.2.0
langchain-community>=0.3.0
pydantic>=2.5.0
redis>=5.0.0
celery>=5.3.0
confluent-kafka>=2.3.0
openai>=1.1.6
anthropic>=0.18.0
boto3>=1.34.0
mcp>=1.1.6
pyjwt>=2.8.0
prometheus-client>=0.19.0
psycopg2-binary>=2.9.9
```

### 4.4 Frontend Technology Stack

| Component | Technology |
|-----------|------------|
| Core Framework | jQuery 3.7.1+ |
| UI Framework | Bootstrap 5.3+ |
| Icons | Bootstrap Icons 1.11+, Font Awesome 6+ |
| Visual Designer | jsPlumb Community 6+, Interact.js |
| Data Tables | DataTables 2.0+ |
| Charts | Chart.js 4+ |
| Real-time | Socket.IO client |
| Code Editor | CodeMirror 6 |

---

## 5. Functional Requirements

### 5.1 Visual Agent Designer (Low-Code/No-Code)

| ID | Feature | Description |
|----|---------|-------------|
| FR-001 | Drag-Drop Canvas | Infinite canvas with zoom, pan, grid snapping |
| FR-002 | Component Library | Categorized palette: LLM, Memory, Tool, Logic nodes |
| FR-003 | Visual Wiring | Connect components with typed edges |
| FR-004 | Property Panels | Bootstrap-based configuration panels |
| FR-005 | Template Gallery | Pre-built templates for all agent types |
| FR-006 | Real-time Preview | Live agent execution preview |
| FR-007 | Code Generation | Auto-generate Python/LangGraph code |
| FR-008 | Version Control | Git-like versioning |
| FR-009 | HITL Checkpoints | Visual designation of intervention points |

### 5.2 Supported Agent Types

| Agent Type | Description |
|------------|-------------|
| ReAct Agent | Reasoning and Acting loop; iterative tool use |
| Plan-and-Execute | Creates plan first, then executes steps |
| Tool-Calling Agent | Focused on invoking external tools/APIs |
| Conversational Agent | Multi-turn dialogue with memory |
| RAG Agent | Retrieval-Augmented Generation |
| Multi-Agent System | Multiple specialized agents collaborating |
| Hierarchical Agent | Supervisor delegates to workers |
| Swarm Agent | Dynamic agent creation/termination |
| State Machine Agent | Explicit state transitions |
| Custom Agent | User-defined agent logic |

### 5.3 Agent Execution Engine

| ID | Feature | Description |
|----|---------|-------------|
| FR-020 | LangGraph Runtime | Native execution with state persistence |
| FR-021 | Streaming Execution | Real-time streaming via WebSocket |
| FR-022 | Parallel Execution | Multiple branches concurrently |
| FR-023 | HITL Integration | Pause for human approval/input |
| FR-024 | Error Recovery | Automatic retry, fallback paths |
| FR-025 | Resource Limits | Timeouts, token limits, cost caps |
| FR-026 | Execution History | Complete audit trail |
| FR-027 | Kafka Events | All events published to Kafka |

---

## 6. Admin Portal & Agent Management

### 6.1 Admin Portal Overview

The Admin Portal is the central hub where administrators design, configure, test, and publish AI agents. Only approved, tested agents are made available to end users.

### 6.2 Admin Portal Modules

| Module | Capabilities |
|--------|--------------|
| Dashboard | System health, active executions, pending approvals |
| Agent Designer | Visual canvas, component palette, preview |
| Agent Library | All agents (draft, testing, published, archived) |
| Template Manager | Create, edit, share templates |
| Testing Console | Agent sandbox testing, debug mode |
| Publishing Center | Publish workflow, version management |
| User Management | Users, teams, roles, permissions |
| Agent Permissions | Assign which users can execute which agents |
| LLM Configuration | Provider setup, API keys, fallback rules |
| MCP Plugins | Plugin registry, configuration |
| HITL Management | Intervention queue config, SLA settings |
| Monitoring | Prometheus dashboards, audit logs |
| System Settings | Global configuration, backup/restore |

### 6.3 Agent Lifecycle Workflow

1. **Draft:** Agent being designed; not executable
2. **Development:** Can be tested in sandbox by developer
3. **Review:** Submitted for approval; reviewers test
4. **Approved:** Approved but not yet published
5. **Published:** Available to authorized users
6. **Deprecated:** Marked for retirement
7. **Archived:** No longer accessible; retained for audit

---

## 7. Role-Based Access Control (RBAC)

### 7.1 RBAC Architecture

Abhikarta-LLM implements a comprehensive RBAC system. Administrators build and publish agents; RBAC controls which users can execute which published agents.

### 7.2 Permission Model

Permissions follow a **Resource:Action:Scope** pattern:

- **Resource:** agents, executions, users, teams, llm_configs, mcp_plugins, hitl_requests
- **Action:** create, read, update, delete, execute, publish, approve
- **Scope:** own, team, domain, global

### 7.3 Default Role Definitions

| Role | Description | Key Permissions |
|------|-------------|-----------------|
| Super Admin | Platform administrator | All permissions; system configuration |
| Domain Admin | Domain owner (formerly Org Admin) | Full control within domain; user management |
| Agent Developer | Builds agents | Create/edit/test agents; submit for review |
| Agent Publisher | Approves agents | Review/approve/reject; publish to users |
| HITL Reviewer | Handles interventions | View/respond to HITL requests |
| Agent User | Runs agents | Execute assigned agents; view history |
| Viewer | Read-only access | View agent catalog; no execution |

### 7.4 Initial User Configuration (users.json)

For initial deployment, users are managed via `users.json`:

```json
{
  "users": [
    {
      "user_id": "admin",
      "password": "admin123",
      "fullname": "System Administrator",
      "email": "admin@abhikarta.local",
      "roles": ["super_admin"],
      "is_active": true
    }
  ]
}
```

---

## 8. Human-in-the-Loop (HITL) Framework

### 8.1 HITL Overview

End-to-end Human-in-the-Loop support enables human oversight at every critical decision point in agent execution.

### 8.2 HITL Trigger Types

| Trigger Type | Description |
|--------------|-------------|
| Explicit Checkpoint | Designer-defined points where execution pauses |
| Confidence Threshold | Pause when LLM confidence below threshold |
| Cost Threshold | Pause when cost exceeds limit |
| Tool Approval | Require approval before executing specific tools |
| Output Validation | Human reviews output before delivery |
| Error Escalation | Escalate on errors or uncertainty |
| Periodic Review | Pause every N steps |
| Content Flagging | Pause on sensitive content detection |

### 8.3 HITL Workflow

1. **Trigger:** Execution reaches checkpoint; pauses
2. **Notification:** Reviewers notified (email, in-app, Slack)
3. **Context Display:** Reviewer sees full context
4. **Decision:** Approve, Reject, Modify, Escalate, Provide Input
5. **Resume:** Agent continues with decision incorporated
6. **Audit:** All interactions logged

---

## 9. LLM Abstraction Layer (Facade)

### 9.1 Facade Pattern Implementation

The LLM Facade provides a unified interface for interacting with multiple LLM providers: **OpenAI, Anthropic, Ollama, AWS Bedrock**.

### 9.2 Facade API Specification

| Method | Description |
|--------|-------------|
| `chat_completion(messages, config)` | Standard chat with streaming |
| `embed(texts, config)` | Generate embeddings |
| `function_call(messages, functions, config)` | Tool/function calling |
| `vision(messages, images, config)` | Image understanding |
| `get_capabilities(provider)` | Query provider capabilities |
| `health_check(provider)` | Check provider availability |

### 9.3 Advanced Routing Features

| Feature | Description |
|---------|-------------|
| Automatic Fallback | Route to fallback if primary fails |
| Load Balancing | Distribute by latency, cost, or round-robin |
| Cost Optimization | Use cheaper models for simple tasks |
| Rate Limit Management | Track limits; queue when approached |
| Token Tracking | Unified counting; cost attribution |
| Response Caching | Semantic caching for repeated queries |

---

## 10. MCP Plugin Framework

### 10.1 Plugin Architecture Overview

The MCP Plugin Framework abstracts MCP servers behind a facade, allowing any MCP-compliant server to integrate via configuration alone.

### 10.2 Plugin Registration & Configuration

| Configuration Field | Description |
|---------------------|-------------|
| Plugin ID | Unique identifier |
| Name & Description | Human-readable info |
| Server Type | stdio, http, or websocket |
| Connection Config | Command/args, URL, auth |
| Environment Variables | Env vars for MCP process |
| RBAC Permissions | Which roles can use this plugin |
| Resource Limits | Timeout, rate limits |

### 10.3 Plugin Facade Interface

| Method | Description |
|--------|-------------|
| `list_plugins()` | Get all registered plugins |
| `get_plugin(plugin_id)` | Get plugin details |
| `list_tools(plugin_id)` | List tools from plugin |
| `call_tool(plugin_id, tool_name, args)` | Execute a tool |
| `list_resources(plugin_id)` | List resources |
| `read_resource(plugin_id, uri)` | Read a resource |

---

## 11. UI/UX Requirements

### 11.1 Design Principles

- **Bootstrap Standard:** Leverage Bootstrap 5 components
- **BMO Theme:** Dark blue header/navigation from bmo.com
- **Light Blue Backgrounds:** Pleasing light blue on all pages
- **Progressive Disclosure:** Simple options first
- **Accessibility:** WCAG 2.1 AA compliance
- **Responsive Design:** Desktop, tablet, mobile

### 11.2 Color Scheme (BMO-Inspired)

| Element | Color |
|---------|-------|
| Primary (Header/Nav) | #0075BE (BMO Blue) |
| Secondary | #003865 (Dark Blue) |
| Background | #E8F4FC (Light Blue) |
| Cards | #FFFFFF (White) |
| Text | #333333 (Dark Gray) |
| Success | #28A745 |
| Warning | #FFC107 |
| Danger | #DC3545 |

---

## 12. Non-Functional Requirements

### 12.1 Performance Requirements

| Metric | Target |
|--------|--------|
| API Response Time (P50) | < 100ms |
| API Response Time (P99) | < 500ms |
| Agent Start Latency | < 2 seconds |
| Concurrent Executions | 1,000+ per instance |
| UI Time to Interactive | < 3 seconds |

### 12.2 Reliability & Availability

| Requirement | Target |
|-------------|--------|
| Uptime SLA | 99.9% |
| RTO | < 30 minutes |
| RPO | < 5 minutes |

### 12.3 Security

- JWT token authentication
- Password-based auth (users.json initially)
- RBAC with per-request enforcement
- Audit logging

---

## 13. Deployment & Infrastructure

### 13.1 Deployment Options

| Model | Description |
|-------|-------------|
| Single Server | All components on one host; dev, POC |
| Docker Compose | Containerized deployment |
| Cloud VMs | AWS EC2, GCP Compute, Azure VMs |
| On-Premise | Air-gapped with Ollama |

### 13.2 Database Configuration

```yaml
# config.yaml
database:
  type: "sqlite"  # or "postgresql"
  sqlite:
    path: "./data/abhikarta.db"
  postgresql:
    host: "localhost"
    port: 5432
    database: "abhikarta"
    user: "abhikarta_user"
    password: "secure_password"
```

---

## 14. Project Timeline & Milestones

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Foundation | 10 weeks | Flask APIs, DB facade, basic RBAC, LLM Facade |
| Phase 2: Admin Portal | 10 weeks | jQuery/Bootstrap UI, visual designer |
| Phase 3: Execution | 8 weeks | LangGraph engine, all agent types |
| Phase 4: HITL | 6 weeks | Full HITL framework |
| Phase 5: MCP Plugins | 6 weeks | MCP Plugin Framework |
| Phase 6: Enterprise | 8 weeks | Advanced RBAC, audit logging |
| Phase 7: Polish | 4 weeks | Documentation, testing |

---

## 15. Success Metrics & KPIs

| Metric | 6-Month | 12-Month |
|--------|---------|----------|
| Monthly Active Users | 1,000 | 5,000 |
| Agents Published | 500 | 2,500 |
| Agent Executions/Day | 10,000 | 100,000 |
| Platform Uptime | ≥ 99.9% | ≥ 99.9% |

---

## 16. Risk Assessment & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LLM API Instability | High | Medium | 4-provider fallback, Ollama backup |
| Security Breach | Critical | Low | RBAC, encryption, audit logging |
| HITL Bottleneck | High | Medium | SLA monitoring, auto-escalation |
| Database Scale | Medium | Low | PostgreSQL for production |

---

## 17. Appendices

### 17.1 Glossary

| Term | Definition |
|------|------------|
| Agent | Autonomous AI entity that perceives, decides, and acts |
| LangGraph | LangChain's framework for stateful LLM applications |
| MCP | Model Context Protocol—Anthropic's standard for tools |
| HITL | Human-in-the-Loop—human oversight in AI workflows |
| RBAC | Role-Based Access Control |
| Facade | Design pattern providing unified interface |

### 17.2 Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2025 | Ashutosh Sinha | Initial PRD |
| 2.0 | Dec 2025 | Ashutosh Sinha | Renamed to Abhikarta-LLM, dual DB support |
| 2.1 | Dec 2025 | Ashutosh Sinha | Added Visual Agent Designer, Template Library, Enhanced User Management, Database Schema Module |

---

### 17.3 Version 1.1.6 Implementation Notes

The following features have been implemented in version 1.1.6:

#### LLM Provider & Model Management (NEW)
- Admin UI for managing LLM providers (/admin/llm-providers)
- Admin UI for managing LLM models (/admin/llm-models)
- Role-based model permissions with daily/monthly limits
- 11 pre-configured providers (OpenAI, Anthropic, Google, Mistral, Groq, etc.)
- 15+ pre-configured models with cost and capability data
- Database tables: llm_providers, llm_models, model_permissions

#### Code Fragments (NEW)
- Reusable code modules with URI-based loading
- Support for db://, file://, s3:// URIs
- Admin UI for creating and managing fragments
- Usage tracking and version control
- Integration with workflow executor

#### Visual Agent Designer (ENHANCED)
- Drag-and-drop workflow canvas with SVG connections
- 14 node types: Input, Output, LLM, Python, Tool, HTTP, Transform, Condition, Loop, Parallel, HITL, Approval, Memory, Retrieval
- Real-time connection drawing with curved bezier paths
- Properties panel for node configuration
- Minimap for large workflow navigation
- Zoom controls (0.3x to 2x)
- Auto-layout algorithm
- Import/export workflow as JSON
- Integrated test execution modal
- LLM provider/model selection from database

#### Template Library
- 6 built-in agent templates:
  - Basic ReAct Agent (beginner)
  - Customer Support Agent (intermediate)
  - Data Analysis Agent (advanced)
  - Research Assistant (intermediate)
  - Code Assistant (intermediate)
  - Workflow Automation (advanced)
- Category and difficulty filtering
- One-click agent creation from templates
- Custom template saving

#### Enhanced User Management
- Modal-based user CRUD operations
- Role-based filtering and search
- Password reset functionality
- User status toggle (activate/deactivate)
- Statistics dashboard

#### Database Schema Module
- Separate schema definitions for SQLite and PostgreSQL
- 22 tables with comprehensive indexes
- Automatic timestamp triggers
- Full-text search support (PostgreSQL)
- JSONB support for flexible configuration storage

---

*— End of Document —*
