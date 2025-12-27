# Abhikarta-LLM

## AI Agent Design & Orchestration Platform

**Version:** 1.1.6  
**Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.**

---

## Overview

Abhikarta-LLM is an enterprise-grade AI agent design and orchestration platform built on low-code/no-code principles. The platform enables administrators to design, configure, and publish AI agents while providing controlled access for end users through RBAC-governed interfaces with full Human-in-the-Loop (HITL) support.

## Features

- **Visual Agent Designer** - Drag-and-drop interface for building AI agents
- **Visual Workflow Designer** - Design workflows with node-based canvas
- **LangChain Integration** - Agent execution using LangChain (ReAct, Tool-Calling, Structured Chat)
- **LangGraph Workflows** - DAG workflow execution with state management and conditional branching
- **Multi-LLM Support** - 11+ providers: OpenAI, Anthropic, Google, Mistral, Groq, Ollama, and more
- **LLM Provider Management** - Configure providers, models, and access via Admin UI
- **Model RBAC** - Role-based access control for models with usage limits
- **Centralized Tools System** - BaseTool abstraction with FunctionTool, MCPTool, HTTPTool, CodeFragmentTool
- **ToolsRegistry** - Centralized tool management with automatic discovery and registration
- **MCP Server Manager** - Centralized MCP server lifecycle management with auto-connect and health monitoring
- **MCP Tool Servers** - Dynamic tool loading from external MCP servers at runtime
- **Code Fragments** - Reusable code modules via db://, file://, s3:// URIs
- **MCP Plugin Framework** - Extensible tool integration via Model Context Protocol
- **Enterprise RBAC** - Role-based access control with fine-grained permissions
- **Human-in-the-Loop (HITL)** - Full task management with assignment, comments, approval/rejection workflow
- **Execution Progress Tracking** - Real-time visual execution monitoring
- **Dual Database Support** - SQLite for development, PostgreSQL for production
- **Admin Portal** - Comprehensive management interface
- **Complete LLM Logging** - Track tokens, costs, and latency for all calls

## Quick Start

### Prerequisites

- Python 3.11+
- pip
- (Optional) PostgreSQL 16+
- (Optional) Redis 7+

### Installation

1. **Clone or extract the project:**
   ```bash
   unzip abhikarta-llm-v1.1.6.zip
   cd abhikarta-llm-v1.1.6
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application:**
   ```bash
   # Edit config/application.properties as needed
   # For LLM providers, set environment variables:
   export OPENAI_API_KEY="your-openai-key"
   export ANTHROPIC_API_KEY="your-anthropic-key"
   ```

5. **Run the application:**
   ```bash
   python run_server.py
   
   # Or with command line overrides:
   python run_server.py --server.port=8080 --app.debug=true
   ```

6. **Access the application:**
   Open http://localhost:5000 in your browser

### Default Credentials

| User | Password | Role |
|------|----------|------|
| admin | admin123 | Super Admin |
| domain_admin | domain123 | Domain Admin |
| developer | dev123 | Agent Developer |
| user | user123 | Agent User |

## Configuration

### Properties Files

Configuration is managed through `config/application.properties`:

```properties
# Database (sqlite or postgresql)
database.type=sqlite
database.sqlite.path=./data/abhikarta.db

# Server
server.host=0.0.0.0
server.port=5000

# LLM Providers
llm.openai.api.key=${OPENAI_API_KEY}
llm.anthropic.api.key=${ANTHROPIC_API_KEY}
```

### Configuration Precedence

Properties can be overridden with precedence (highest to lowest):
1. **Command line arguments** (`--key=value`)
2. **Environment variables**
3. **Property files**

### Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask secret key for sessions |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `OLLAMA_BASE_URL` | Ollama server URL |
| `PG_HOST` | PostgreSQL host |
| `PG_DATABASE` | PostgreSQL database name |
| `PG_USER` | PostgreSQL user |
| `PG_PASSWORD` | PostgreSQL password |

## Project Structure

```
abhikarta-llm-v1.1.6/
├── abhikarta/                  # Main package
│   ├── core/                   # Core utilities
│   │   └── config/             # PropertiesConfigurator (singleton)
│   ├── config/                 # Settings management
│   ├── database/               # Database facade (SQLite/PostgreSQL)
│   ├── user_management/        # User facade (users.json)
│   ├── rbac/                   # Role-based access control
│   ├── llm_provider/           # LLM abstraction layer (legacy)
│   ├── tools/                  # Centralized Tools System
│   │   ├── base_tool.py        # BaseTool abstract class
│   │   ├── function_tool.py    # Python function tools
│   │   ├── mcp_tool.py         # MCP server tools
│   │   ├── http_tool.py        # HTTP/REST API tools
│   │   ├── code_fragment_tool.py  # Database code fragment tools
│   │   ├── langchain_tool.py   # LangChain tool wrappers
│   │   └── registry.py         # ToolsRegistry singleton
│   ├── langchain/              # LangChain & LangGraph integration
│   │   ├── llm_factory.py      # LangChain LLM creation
│   │   ├── tools.py            # Tool creation & MCP integration
│   │   ├── agents.py           # Agent execution
│   │   └── workflow_graph.py   # LangGraph workflow execution
│   ├── mcp/                    # MCP Server Management
│   │   ├── server.py           # MCPServer, MCPServerConfig models
│   │   ├── client.py           # HTTP & WebSocket MCP clients
│   │   └── manager.py          # MCPServerManager singleton
│   ├── workflow/               # Workflow execution
│   ├── agent/                  # Agent management
│   ├── hitl/                   # Human-in-the-loop
│   ├── web/                    # Flask web application
│   │   ├── abhikarta_llm_web.py  # Main application class
│   │   ├── routes/             # Route handlers
│   │   ├── templates/          # Jinja2 templates
│   │   │   ├── auth/           # Authentication pages
│   │   │   ├── admin/          # Admin dashboard pages
│   │   │   ├── user/           # User dashboard pages
│   │   │   ├── agents/         # Agent management pages
│   │   │   ├── workflows/      # Workflow designer pages
│   │   │   ├── mcp/            # MCP plugin pages
│   │   │   ├── help/           # Help & About pages
│   │   │   └── errors/         # Error pages
│   │   └── static/             # CSS, JS, images
│   └── utils/                  # Utilities
├── config/                     # Configuration files
│   └── application.properties  # Main configuration
├── data/                       # Data directory
│   └── users.json              # User credentials
├── logs/                       # Log files
├── docs/                       # Documentation
│   ├── REQUIREMENTS.md         # Product requirements
│   └── DESIGN.md               # Detailed design
├── tests/                      # Test suite
├── run_server.py               # Entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── LICENSE                     # License
```

## User Roles

| Role | Description |
|------|-------------|
| Super Admin | Full system access |
| Domain Admin | Domain-level administration |
| Agent Developer | Create and test agents |
| Agent Publisher | Approve and publish agents |
| HITL Reviewer | Handle human intervention requests |
| Agent User | Execute assigned agents |
| Viewer | Read-only access |

## API Documentation

### Authentication

All API endpoints require authentication via session cookie.

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/logout` | User logout |
| GET | `/api/agents` | List agents |
| GET | `/api/agents/{id}` | Get agent details |
| POST | `/api/agents` | Create agent |
| POST | `/api/agents/{id}/execute` | Execute agent |

## Development

### Running in Debug Mode

```bash
python run_server.py --app.debug=true
```

### Running Tests

```bash
pytest tests/
```

## Help & About

The application includes comprehensive built-in documentation:

- **Help Page** (`/help`) - Full documentation with architecture diagrams, examples, and tutorials
- **About Page** (`/about`) - Platform overview with competitive analysis

## Security Considerations

1. **Change default passwords** before deployment
2. **Set a strong SECRET_KEY** in production
3. **Use PostgreSQL** for production deployments
4. **Enable HTTPS** in production
5. **Review RBAC permissions** for your organization

## License

This software is proprietary and confidential. See LICENSE file for details.

## Legal Notice

Copyright © 2025-2030, All Rights Reserved  
Ashutosh Sinha  
Email: ajsinha@gmail.com

This document and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use of this document or the software system it describes is strictly prohibited without explicit written permission from the copyright holder.

**Patent Pending:** Certain architectural patterns and implementations may be subject to patent applications.

## Support

For support inquiries, contact: ajsinha@gmail.com
