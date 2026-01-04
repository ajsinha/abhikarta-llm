# Abhikarta Web

Web UI module for Abhikarta-LLM - AI Agent Orchestration Platform.

## Overview

This module provides the Flask-based web interface for Abhikarta-LLM, including:

- Visual agent designer
- Workflow visual designer
- Swarm designer
- AI Organization designer
- HITL (Human-in-the-Loop) dashboard
- Administration interfaces
- Documentation & help system

## Installation

This module is typically installed as part of the full Abhikarta-LLM installation. For standalone installation:

```bash
pip install abhikarta-web
```

## Requirements

- abhikarta>=1.4.8 (core library)
- flask>=2.0.0
- flask-login>=0.6.0
- flask-session>=0.5.0

## Structure

```
abhikarta-web/
├── src/abhikarta_web/
│   ├── __init__.py
│   ├── abhikarta_llm_web.py    # Main web application class
│   ├── app.py                   # Flask app factory
│   ├── routes/                  # Flask route handlers
│   │   ├── abstract_routes.py   # Base route class
│   │   ├── auth_routes.py       # Authentication & help
│   │   ├── agent_routes.py      # Agent management
│   │   ├── workflow_routes.py   # Workflow management
│   │   ├── swarm_routes.py      # Swarm management
│   │   ├── aiorg_routes.py      # AI Organization management
│   │   ├── script_routes.py     # Python Script Mode
│   │   └── ...
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html            # Base template
│   │   ├── agents/              # Agent pages
│   │   ├── workflows/           # Workflow pages
│   │   ├── swarms/              # Swarm pages
│   │   ├── aiorg/               # AI Org pages
│   │   ├── scripts/             # Script pages
│   │   ├── help/                # Documentation
│   │   └── ...
│   └── static/                  # CSS, JS, images
│       ├── css/
│       ├── js/
│       └── img/
├── pyproject.toml
└── README.md
```

## Usage

The web module is initialized by `run_server.py`:

```python
from abhikarta_web import AbhikartaLLMWeb

# Initialize web application
web = AbhikartaLLMWeb(prop_conf)

# Get Flask app
app = web.get_app()

# Run server
app.run(host='0.0.0.0', port=5000)
```

## Key Pages

| URL | Description |
|-----|-------------|
| `/` | Dashboard |
| `/agents` | Agent management |
| `/workflows` | Workflow management |
| `/swarms` | Swarm management |
| `/aiorg` | AI Organization management |
| `/scripts` | Python Script Mode |
| `/help` | Documentation |
| `/admin` | Administration |

## Configuration

The web module uses configuration from `config/application.properties`:

```properties
# Server settings
server.host=0.0.0.0
server.port=5000

# Session settings
session.type=filesystem
session.secret_key=your-secret-key

# Template settings
templates.auto_reload=true
```

## Development

For development mode with auto-reload:

```bash
python run_server.py --app.debug=true
```

## License

MIT License - Copyright © 2025-2030 Ashutosh Sinha
