# Abhikarta-LLM Quick Start Guide

**Version:** 1.1.0  
**Date:** December 2025

---

## Copyright Notice

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha** | ajsinha@gmail.com

---

## Overview

This guide will help you get Abhikarta-LLM up and running in minutes.

---

## Prerequisites

- **Python 3.10+** installed
- **pip** package manager
- **Git** (optional, for cloning)

---

## Installation

### Step 1: Extract the Archive

```bash
unzip abhikarta-llm-v1.1.0.zip
cd abhikarta-llm-v1.1.0
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Start the Server

```bash
python run_server.py
```

The server will start at: **http://localhost:5000**

---

## First Login

1. Open your browser and go to: `http://localhost:5000`
2. Login with default admin credentials:
   - **Username:** `admin`
   - **Password:** `admin123`

> ⚠️ **Security Note:** Change the default password immediately after first login!

---

## Quick Tour

### Admin Dashboard
After login, you'll see the Admin Dashboard with:
- User statistics
- Agent counts
- Recent activity

### Key Features

| Feature | URL | Description |
|---------|-----|-------------|
| **Agent Management** | `/admin/agents` | Create, edit, and manage agents |
| **Visual Designer** | `/admin/agents/<id>/designer` | Drag-and-drop workflow builder |
| **Template Library** | `/admin/agents/templates` | Pre-built agent templates |
| **User Management** | `/admin/users` | Manage users and roles |
| **Help & Docs** | `/help` | Built-in documentation |

---

## Creating Your First Agent

### Option 1: From Template (Recommended)

1. Go to **Agent Management** → **Template Library**
2. Browse available templates:
   - Basic ReAct Agent
   - Customer Support Agent
   - Data Analysis Agent
   - Research Assistant
   - Code Assistant
   - Workflow Automation
3. Click **"Use This Template"**
4. Enter a name for your agent
5. Click **Create Agent**
6. Customize in the Visual Designer

### Option 2: From Scratch

1. Go to **Agent Management**
2. Click **"Create Agent"**
3. Fill in:
   - Agent Name
   - Agent Type (ReAct, Plan & Execute, etc.)
   - LLM Provider
   - Model
4. Click **Create Agent**
5. Open the **Visual Designer** to build your workflow

---

## Visual Agent Designer

The Visual Designer allows you to create agent workflows using drag-and-drop:

### Node Types

| Node | Purpose |
|------|---------|
| **Input** | Entry point for user messages |
| **Output** | Final response to user |
| **LLM Node** | Large language model processing |
| **Tool Node** | External tool/API call |
| **Condition** | Branching logic |
| **Loop** | Iterative processing |
| **HITL Checkpoint** | Human approval point |

### Basic Workflow

1. Drag an **Input** node onto the canvas
2. Add an **LLM Node** for processing
3. Add any **Tool Nodes** needed
4. Connect with an **Output** node
5. Click **Save** to save your workflow
6. Click **Test** to try it out

---

## Configuration

### Database Configuration

Edit `config/application.properties`:

```properties
# For development (SQLite - default)
database.type=sqlite
database.sqlite.path=./data/abhikarta.db

# For production (PostgreSQL)
# database.type=postgresql
# database.postgres.host=localhost
# database.postgres.port=5432
# database.postgres.database=abhikarta
# database.postgres.user=postgres
# database.postgres.password=your_password
```

### LLM Provider Configuration

```properties
# OpenAI
llm.default_provider=openai
llm.openai.api_key=your_api_key_here
llm.openai.default_model=gpt-4o

# Anthropic
# llm.default_provider=anthropic
# llm.anthropic.api_key=your_api_key_here

# Ollama (Local)
# llm.default_provider=ollama
# llm.ollama.base_url=http://localhost:11434
```

### Server Configuration

```properties
server.host=0.0.0.0
server.port=5000
server.debug=true
```

---

## Default Users

| Username | Password | Roles |
|----------|----------|-------|
| admin | admin123 | super_admin |
| developer | dev123 | agent_developer |
| user | user123 | agent_user |

---

## Roles and Permissions

| Role | Permissions |
|------|-------------|
| **super_admin** | Full system access |
| **domain_admin** | User and agent management |
| **agent_developer** | Create and test agents |
| **agent_publisher** | Review and publish agents |
| **hitl_reviewer** | Review HITL tasks |
| **agent_user** | Execute published agents |
| **viewer** | Read-only access |

---

## Troubleshooting

### Server Won't Start

1. Check Python version: `python --version` (needs 3.10+)
2. Ensure dependencies installed: `pip install -r requirements.txt`
3. Check port 5000 is available

### Login Failed

1. Verify credentials (default: admin/admin123)
2. Check `data/users.json` exists
3. Try clearing browser cookies

### Database Errors

1. For SQLite: Ensure `data/` directory exists
2. For PostgreSQL: Verify connection settings
3. Check database permissions

---

## Getting Help

- **Built-in Help:** `/help` in the application
- **About Page:** `/about` for version information
- **Documentation:** See `docs/` folder

---

## Next Steps

1. ✅ Change default passwords
2. ✅ Configure your LLM provider API keys
3. ✅ Create your first agent from a template
4. ✅ Explore the Visual Designer
5. ✅ Set up additional users with appropriate roles

---

## File Structure

```
abhikarta-llm-v1.1.0/
├── abhikarta/           # Main application package
│   ├── agent/           # Agent management
│   ├── config/          # Configuration
│   ├── core/            # Core utilities
│   ├── database/        # Database layer
│   │   └── schema/      # SQL schema definitions
│   ├── user_management/ # User management
│   └── web/             # Web application
│       ├── routes/      # Route handlers
│       ├── static/      # CSS, JS, images
│       └── templates/   # HTML templates
├── config/              # Configuration files
├── data/                # Data files
├── docs/                # Documentation
├── logs/                # Log files
├── tests/               # Test files
├── requirements.txt     # Python dependencies
└── run_server.py        # Entry point
```

---

*Happy Building! 🚀*
