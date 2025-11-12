# Abhikarta MCP Integration - Configuration Example
# Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)

"""
Example configuration for Abhikarta MCP Integration.

Copy this file to config.py and customize for your environment.
"""

# MCP Server Configuration
MCP_SERVER_CONFIG = {
    # Base URL of your MCP server
    "base_url": "http://localhost:3002",
    
    # MCP JSON-RPC endpoint
    "mcp_endpoint": "/mcp",
    
    # Authentication endpoints
    "login_endpoint": "/api/auth/login",
    
    # Tool discovery endpoints
    "tool_list_endpoint": "/api/tools/list",
    "tool_schema_endpoint_template": "/api/tools/{tool_name}/schema",
    
    # Authentication credentials
    "username": "admin",
    "password": "your_secure_password",
    
    # Refresh configuration
    "refresh_interval_seconds": 600,  # 10 minutes
    
    # HTTP timeout
    "timeout_seconds": 30.0,
    
    # Tool naming
    "tool_name_suffix": ":abhikartamcp"
}

# Registry Integration Configuration
REGISTRY_CONFIG = {
    # Group name for MCP tools in registry
    "group_name": "abhikarta_mcp",
    
    # Tags to apply to all MCP tools
    "tags": ["mcp", "abhikarta", "dynamic"],
    
    # Auto-sync configuration
    "auto_sync_enabled": True,
    "sync_interval_seconds": 120  # 2 minutes
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": [
        {
            "type": "console",
            "level": "INFO"
        },
        {
            "type": "file",
            "filename": "abhikarta_mcp.log",
            "level": "DEBUG",
            "max_bytes": 10485760,  # 10MB
            "backup_count": 5
        }
    ]
}

# Production Configuration Example
PRODUCTION_CONFIG = {
    "base_url": "https://mcp.production.com",
    "username": "prod_user",
    "password": "prod_secure_password",
    "refresh_interval_seconds": 300,  # 5 minutes
    "timeout_seconds": 60.0,
    "ssl_verify": True,
    "max_retries": 3,
    "retry_backoff_factor": 2.0
}

# Development Configuration Example
DEVELOPMENT_CONFIG = {
    "base_url": "http://localhost:3002",
    "username": "dev_user",
    "password": "dev_password",
    "refresh_interval_seconds": 60,  # 1 minute
    "timeout_seconds": 10.0,
    "ssl_verify": False,
    "debug_mode": True
}

# Environment-based configuration selector
import os

ENVIRONMENT = os.getenv("ABHIKARTA_ENV", "development")

if ENVIRONMENT == "production":
    ACTIVE_CONFIG = PRODUCTION_CONFIG
elif ENVIRONMENT == "development":
    ACTIVE_CONFIG = DEVELOPMENT_CONFIG
else:
    ACTIVE_CONFIG = MCP_SERVER_CONFIG
