# Abhikarta-LLM v1.2.5 - Quick Start Guide

This guide will help you get started with Abhikarta-LLM in under 15 minutes.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [First Steps](#first-steps)
4. [Create Your First Agent](#create-your-first-agent)
5. [Create Your First Workflow](#create-your-first-workflow)
6. [Use Pre-built Banking Solutions](#use-pre-built-banking-solutions)
7. [Using Tools](#using-tools)
8. [Key Features Overview](#key-features-overview)

---

## Installation

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 12+ (recommended) or SQLite
- Git
- 4GB RAM minimum

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/abhikarta-llm.git
cd abhikarta-llm

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Database

Edit `config/application.properties`:

```properties
# For SQLite (quick start)
db.type=sqlite
db.database=data/abhikarta.db

# For PostgreSQL (production)
# db.type=postgres
# db.host=localhost
# db.port=5432
# db.database=abhikarta
# db.user=your_user
# db.password=your_password
```

### Step 3: Start the Server

```bash
python run_server.py
```

Access the application at: **http://localhost:5000**

Default credentials: `admin` / `admin123`

---

## Configuration

### LLM Provider Setup

1. Navigate to **Admin → LLM Providers**
2. Add your preferred provider:

| Provider | Required Configuration |
|----------|----------------------|
| OpenAI | API Key |
| Anthropic | API Key |
| Google | API Key |
| Azure OpenAI | Endpoint, API Key, Deployment |
| AWS Bedrock | Access Key, Secret Key, Region |
| Ollama | Base URL (default: http://localhost:11434) |

3. Add models for your provider
4. Set role permissions for model access

### MCP Plugin Setup (Optional)

1. Navigate to **Admin → MCP Tool Servers**
2. Add external tool servers:
   - Name: descriptive name
   - URL: server endpoint
   - Transport: HTTP, WebSocket, SSE, or STDIO
   - Auto-connect: Enable for automatic connection

---

## First Steps

### Dashboard Overview

After login, you'll see the main dashboard with:

- **Recent Executions**: Latest agent/workflow runs
- **Quick Stats**: Agents, workflows, executions count
- **Quick Actions**: Create agent, create workflow, view HITL tasks

### Navigation

| Menu | Description |
|------|-------------|
| **Agents** | Create and manage AI agents |
| **Workflows** | Design and execute workflows |
| **Executions** | View execution history and logs |
| **Tools** | Browse, search, and test all tools |
| **HITL Tasks** | Human-in-the-loop pending tasks |
| **Admin** | User, LLM, and system management |
| **Help** | Documentation and guides |

---

## Create Your First Agent

### Option 1: Visual Designer

1. Go to **Agents → Create Agent**
2. Use the drag-and-drop designer:
   - Add a **Start** node
   - Add an **LLM** node (select your model)
   - Add tool nodes as needed
   - Connect nodes with edges
3. Configure the agent properties:
   - Name and description
   - System prompt
   - Temperature and max tokens
4. Click **Save Agent**

### Option 2: JSON Definition

```json
{
  "name": "My First Agent",
  "description": "A simple Q&A agent",
  "agent_type": "react",
  "model_id": "gpt-4o",
  "system_prompt": "You are a helpful assistant. Answer questions clearly and concisely.",
  "tools": ["calculate_expression", "get_current_datetime"],
  "temperature": 0.7,
  "max_tokens": 1024
}
```

### Test Your Agent

1. Go to **Agents → [Your Agent] → Test**
2. Enter a prompt
3. View the response and execution trace

---

## Create Your First Workflow

### Visual Workflow Designer

1. Go to **Workflows → Create Workflow**
2. Use the canvas to design:

```
[Start] → [LLM: Analyze Input] → [Condition: Is Valid?]
                                        ↓
                              [Yes] → [Tool: Process]
                                        ↓
                              [No] → [LLM: Request Clarification]
                                        ↓
                              [End]
```

### Node Types Available

| Node Type | Description |
|-----------|-------------|
| **Start** | Entry point |
| **End** | Exit point |
| **LLM** | Call an LLM model |
| **Agent** | Invoke another agent |
| **Tool** | Execute a tool |
| **Code** | Run Python code |
| **Condition** | Branch based on condition |
| **Passthrough** | Pass data unchanged |
| **RAG** | Retrieval-augmented generation |
| **HITL** | Human-in-the-loop checkpoint |

### Execute Workflow

1. Go to **Workflows → [Your Workflow] → Execute**
2. Provide input JSON
3. Monitor execution progress in real-time

---

## Use Pre-built Template Solutions

### Browse Agent Templates

1. Go to **Agents → Templates**
2. Browse 36 templates across 15 categories:
   - **Analytics**: Data Pipeline, ML Inference, Report Generator
   - **Banking**: KYC Verification, Loan Processing, Fraud Detection
   - **Development**: Code Reviewer, Debug Assistant, API Tester
   - **Healthcare**: Medical Assistant, Claims Processor
   - **Legal**: Contract Analyst, Compliance Monitor
   - **Customer Service**: Support Agent, FAQ Bot
   - And more...
3. Click **Use Template** to create your copy
4. Customize as needed

### Browse Workflow Templates

1. Go to **Workflows → Templates**
2. Browse 33 templates across 11 industries:
   - **Document Processing**: PDF Extraction, Invoice Processing
   - **Data Processing**: ETL Pipeline, CSV Analyzer, Data Quality
   - **Financial Processing**: Loan Application, Fraud Detection
   - **Healthcare**: Claims Processing, Patient Intake
   - **Human Resources**: Resume Screening, Onboarding
   - **Legal**: Contract Review, Compliance Check
   - **Technology**: Code Review, API Testing
3. Click **Use Template** and customize

### Code Fragment URIs

Templates reference reusable code using URI schemes:
```json
{
  "code_fragments": [
    "db://code_fragments/data_validator",
    "s3://abhikarta-fragments/ml_processor.py",
    "file:///opt/abhikarta/fragments/custom.py"
  ]
}
```

### Banking Tools Available

```python
# KYC Tools
verify_identity_document(document_type, document_number, issuing_country)
calculate_kyc_risk_score(customer_data)
verify_address(address_data)
check_sanctions_list(entity_name, entity_type)

# Credit Tools
calculate_credit_score(credit_data)
assess_debt_to_income(monthly_income, monthly_debts)
calculate_loan_eligibility(applicant_data)
generate_amortization_schedule(principal, rate, term)

# Transaction Tools
analyze_transaction(transaction)
detect_transaction_patterns(transactions)
calculate_transaction_limits(account_data)

# Compliance Tools
generate_aml_report(customer_id, transactions)
validate_regulatory_compliance(account_data)
```

---

## Using Tools

### Pre-built Tools (85)

Abhikarta comes with 85 pre-built tools organized in categories:

#### Common Tools (28)
```python
# Date/Time
get_current_datetime(format="%Y-%m-%d")
calculate_date_difference("2025-01-01", "2025-12-31")
get_business_days("2025-01-01", "2025-01-31")

# Math
calculate_expression("sqrt(16) + pow(2, 3)")
calculate_loan_emi(100000, 7.5, 60)
calculate_compound_interest(10000, 5, 10)

# Text
extract_entities("Contact: john@example.com, 555-1234")
mask_sensitive_data("SSN: 123-45-6789")
clean_text("<p>Hello World</p>", remove_html=True)

# Validation
validate_email("user@example.com")
validate_credit_card("4111111111111111")
validate_iban("DE89370400440532013000")
```

#### General Tools (24) - NEW
```python
# Web/Search
web_search("AI trends 2025", num_results=10)
web_fetch("https://example.com/api/data")
news_search("technology", days_back=7)

# Document Handling
read_document("/path/to/document.txt")
write_document("/path/to/output.md", content)
convert_document("input.txt", "md")

# File Operations
list_files("/data", pattern="*.json", recursive=True)
copy_file("source.txt", "destination.txt")

# System/Network
get_system_info()
check_url_status("https://api.example.com/health")
ping_host("google.com")
dns_lookup("example.com")
```

#### Integration Tools (20)
```python
# Data Transformation
map_fields(source, {"old_name": "new_name"})
flatten_nested_dict({"a": {"b": 1}})  # → {"a.b": 1}
merge_dicts(dict1, dict2, strategy="override")

# List Operations
filter_list(items, "status", "eq", "active")
sort_list(items, "created_at", descending=True)
aggregate_list(items, "amount", "sum")
paginate_list(items, page=1, page_size=10)
```

### Tools Management Page

Browse all available tools at **/tools**:
- View all registered tools (pre-built, MCP, code fragments)
- Search and filter by category or source
- Test tools with custom parameters
- Refresh MCP server connections

### Register Custom Tools

```python
from abhikarta.tools import tool, get_tools_registry

@tool(name="my_tool", description="Does something useful")
def my_custom_tool(input_data: str) -> str:
    return f"Processed: {input_data}"

# Register with system
registry = get_tools_registry()
registry.register(my_custom_tool)
```

### Use Tools in Agents

Add tool names to agent configuration:

```json
{
  "tools": [
    "calculate_loan_emi",
    "validate_email",
    "mask_sensitive_data",
    "my_custom_tool"
  ]
}
```

---

## Key Features Overview

### Feature Summary

| Feature | Description | Version |
|---------|-------------|---------|
| **Visual Agent Designer** | Drag-and-drop agent creation | v1.1.0 |
| **Visual Workflow Designer** | Canvas-based workflow design | v1.1.5 |
| **Multi-LLM Support** | 11 provider integrations | v1.0.0 |
| **Code Fragments** | db://, file://, s3:// URIs | v1.0.1 |
| **HITL System** | Human approval workflows | v1.1.5 |
| **Execution Progress** | Real-time monitoring | v1.1.5 |
| **Tools System** | Unified tool architecture | v1.1.6 |
| **MCP Integration** | External tool servers | v1.1.6 |
| **Pre-built Tools** | 85 ready-to-use tools | v1.1.7 |
| **Tools Page** | Browse, search, filter tools | v1.1.7 |
| **Tool View/Test Pages** | Dedicated tool detail & testing UI | v1.1.8 |
| **Database Schema Docs** | 22 tables documented with ER diagram | v1.2.0 |
| **Page Glossaries** | Contextual help on 22 templates | v1.2.0 |
| **Database Delegates** | 9 modular delegates for DB operations | v1.2.1 |
| **Actor System** | Pekko-inspired concurrency (millions of actors) | v1.2.5 |
| **Agent Templates** | 36 templates across 15 categories | v1.2.5 |
| **Workflow Templates** | 33 templates across 11 industries | v1.2.5 |
| **Code Fragment URIs** | Templates use db://, s3://, file:// URIs | v1.2.5 |

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│         Flask Web UI │ REST API │ Help Documentation        │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                         │
│    Agent Manager │ Workflow Engine │ HITL Manager            │
├─────────────────────────────────────────────────────────────┤
│                 Actor System Layer (v1.2.5)                  │
│  ActorSystem │ Dispatchers │ Supervision │ Routers │ Events │
├─────────────────────────────────────────────────────────────┤
│                      Tools Layer                             │
│  BaseTool │ FunctionTool │ MCPTool │ HTTPTool │ Registry    │
├─────────────────────────────────────────────────────────────┤
│                   Integration Layer                          │
│    LangChain │ LangGraph │ MCP Clients │ LLM Providers      │
├─────────────────────────────────────────────────────────────┤
│                      Data Layer (v1.2.1)                     │
│  DatabaseFacade │ 9 Delegates │ SQLite/PostgreSQL │ 22 Tables│
└─────────────────────────────────────────────────────────────┘
```

### User Roles

| Role | Permissions |
|------|-------------|
| **Super Admin** | Full system access |
| **Domain Admin** | Manage users, LLM config, limited system access |
| **Agent Developer** | Create/edit agents and workflows |
| **Agent User** | Execute agents and workflows, view results |

---

## Next Steps

1. **Browse Tools**: Visit `/tools` to explore all 85 pre-built tools
2. **Explore Help**: Click **Help** in navigation for detailed guides
3. **Try Banking Agents**: Clone and test pre-built banking solutions
4. **Build Custom Tools**: Create domain-specific tools
5. **Set Up MCP**: Connect external tool servers
6. **Configure HITL**: Add human approval points to workflows

---

## Getting Help

- **In-App Help**: `/help` - Comprehensive documentation
- **Tools Browser**: `/tools` - Browse and test all tools
- **Architecture**: `/help/about/architecture` - System design
- **API Reference**: `/help/page/api-reference` - REST API docs
- **Banking Guide**: `/help/page/banking-solutions` - Banking solutions

---

## File Structure Reference

```
abhikarta-llm-v1.2.5/
├── abhikarta/
│   ├── agent/          # Agent management
│   ├── config/         # Configuration
│   ├── database/       # Database layer (22 tables)
│   ├── hitl/           # Human-in-the-loop
│   ├── langchain/      # LangChain/LangGraph integration
│   ├── llm_provider/   # Multi-provider LLM facade
│   ├── mcp/            # MCP server management
│   ├── tools/          # Tools system + prebuilt (85)
│   │   └── prebuilt/   # Common(28), Banking(13), Integration(20), General(24)
│   ├── web/            # Flask application
│   └── workflow/       # DAG execution engine
├── config/             # Application properties
├── data/
│   └── prebuilt/       # Pre-built agents & workflows
├── docs/               # Documentation
└── run_server.py       # Entry point
```

---

*Version 1.2.5 - Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.*
