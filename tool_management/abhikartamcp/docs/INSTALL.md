# Installation Guide

**Abhikarta MCP Integration**  
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 512MB RAM
- **Network**: Access to MCP server

### Python Dependencies

```bash
# Core dependencies
httpx>=0.27.0

# Development dependencies (optional)
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.0.0
mypy>=1.5.0
```

### Required Framework

This module requires the Abhikarta Tool Management Framework:
- `tool_management.core.base`
- `tool_management.core.types`
- `tool_management.core.parameters`
- `tool_management.core.results`
- `tool_management.registry.registry`

---

## Installation Methods

### Method 1: Direct Installation (Recommended)

```bash
# 1. Extract the archive
tar -xzf abhikarta_mcp_integration.tar.gz
cd abhikarta_mcp_integration

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install the package
pip install -e .

# 4. Verify installation
python -c "from abhikartamcp import AbhikartaMCPToolBuilder; print('Success!')"
```

### Method 2: Manual Integration

```bash
# 1. Extract the archive
tar -xzf abhikarta_mcp_integration.tar.gz

# 2. Copy the abhikartamcp module to your project
cp -r abhikarta_mcp_integration/abhikartamcp /path/to/your/project/

# 3. Install dependencies manually
pip install httpx

# 4. Import in your code
# from abhikartamcp import AbhikartaMCPToolBuilder
```

### Method 3: Development Installation

```bash
# For development with additional tools
cd abhikarta_mcp_integration
pip install -e ".[dev]"
```

---

## Configuration

### Step 1: Create Configuration File

```bash
# Copy the example configuration
cp config_example.py config.py

# Edit with your settings
nano config.py
```

### Step 2: Set Environment Variables

```bash
# Add to ~/.bashrc or ~/.zshrc
export ABHIKARTA_MCP_URL="http://your-server:3002"
export ABHIKARTA_MCP_USERNAME="your_username"
export ABHIKARTA_MCP_PASSWORD="your_password"
export ABHIKARTA_ENV="production"
```

### Step 3: Basic Configuration

Edit `config.py`:

```python
MCP_SERVER_CONFIG = {
    "base_url": "http://localhost:3002",
    "username": "admin",
    "password": "your_password",
    "refresh_interval_seconds": 600,
    "timeout_seconds": 30.0
}
```

---

## Verification

### Test Basic Import

```python
# test_import.py
from abhikartamcp import (
    AbhikartaMCPToolBuilder,
    AbhikartaBaseTool,
    MCPRegistryIntegration
)

print("✓ All imports successful")
```

Run:
```bash
python test_import.py
```

### Test Connection

```python
# test_connection.py
import asyncio
from abhikartamcp import AbhikartaMCPToolBuilder

async def test():
    builder = AbhikartaMCPToolBuilder()
    builder.configure(
        base_url="http://localhost:3002",
        username="admin",
        password="password"
    )
    
    try:
        await builder.start()
        print(f"✓ Connected to MCP server")
        print(f"✓ Found {len(builder.list_cached_tools())} tools")
        await builder.stop()
    except Exception as e:
        print(f"✗ Connection failed: {e}")

asyncio.run(test())
```

Run:
```bash
python test_connection.py
```

### Run Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/test_basic.py -v

# Run with coverage
pytest tests/ --cov=abhikartamcp --cov-report=html
```

---

## Troubleshooting

### Issue: Import Error

**Problem:**
```
ImportError: No module named 'abhikartamcp'
```

**Solution:**
```bash
# Ensure package is installed
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="/path/to/abhikarta_mcp_integration:$PYTHONPATH"
```

### Issue: httpx Not Found

**Problem:**
```
ImportError: No module named 'httpx'
```

**Solution:**
```bash
pip install httpx
```

### Issue: Connection Refused

**Problem:**
```
Connection refused to http://localhost:3002
```

**Solution:**
1. Verify MCP server is running
2. Check the URL and port
3. Test with curl:
   ```bash
   curl http://localhost:3002/mcp
   ```

### Issue: Authentication Failed

**Problem:**
```
Authentication failed: 401 Unauthorized
```

**Solution:**
1. Verify credentials are correct
2. Check if user account is active
3. Test login endpoint directly:
   ```bash
   curl -X POST http://localhost:3002/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"user_id":"admin","password":"password"}'
   ```

### Issue: No Tools Discovered

**Problem:**
```
Found 0 tools
```

**Solution:**
1. Check if MCP server has tools configured
2. Verify authentication is successful
3. Test tools/list endpoint:
   ```bash
   curl -X POST http://localhost:3002/mcp \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
   ```

---

## Advanced Configuration

### Using with Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY abhikarta_mcp_integration /app/abhikarta_mcp_integration
COPY requirements.txt /app/

RUN pip install -r requirements.txt
RUN pip install -e abhikarta_mcp_integration

CMD ["python", "your_application.py"]
```

### Systemd Service

```ini
# /etc/systemd/system/abhikarta-mcp.service
[Unit]
Description=Abhikarta MCP Integration Service
After=network.target

[Service]
Type=simple
User=abhikarta
WorkingDirectory=/opt/abhikarta
ExecStart=/usr/bin/python3 /opt/abhikarta/main.py
Restart=on-failure
Environment="ABHIKARTA_ENV=production"

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable abhikarta-mcp
sudo systemctl start abhikarta-mcp
sudo systemctl status abhikarta-mcp
```

---

## Next Steps

After successful installation:

1. Review the [README.md](README.md) for usage examples
2. Read [TECHNICAL.md](TECHNICAL.md) for architecture details
3. Try the examples in `examples/` directory
4. Configure for your environment
5. Integrate with your application

---

## Support

For installation issues or questions:

**Email:** ajsinha@gmail.com

Include the following information:
- Python version (`python --version`)
- Operating system
- Error messages
- Configuration (with sensitive data removed)

---

**Last Updated:** 2025-01-01  
**Version:** 1.0.0
