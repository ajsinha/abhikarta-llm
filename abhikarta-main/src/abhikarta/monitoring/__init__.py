"""
Abhikarta Monitoring Module - Prometheus Metrics & Observability.

This module provides comprehensive monitoring capabilities for Abhikarta-LLM
using Prometheus metrics. It tracks:

- Agent executions (count, duration, tokens, errors)
- Workflow executions (count, duration, node metrics)
- Swarm operations (tasks, events, agent counts)
- AI Organization metrics (delegations, HITL interventions)
- LLM provider metrics (requests, tokens, costs)
- Database operations (queries, connections)
- HTTP API metrics (requests, latency)
- Tool executions
- MCP server connections
- Actor system metrics
- Script executions
- Notifications

Usage:
    from abhikarta.monitoring import metrics
    
    # Track agent execution
    metrics.AGENT_EXECUTIONS.labels(
        agent_id='agent-123',
        agent_type='react',
        status='success'
    ).inc()
    
    # Track execution time
    with metrics.MetricsContext(
        metrics.AGENT_EXECUTION_DURATION,
        metrics.AGENT_EXECUTIONS,
        agent_id='agent-123',
        agent_type='react'
    ) as ctx:
        result = execute_agent()
        ctx.set_status('success')
    
    # Generate Prometheus output
    output = metrics.get_metrics_output()

Prometheus Endpoint:
    GET /metrics - Returns Prometheus-formatted metrics

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.4.8
"""

from .metrics import (
    # Availability check
    PROMETHEUS_AVAILABLE,
    
    # Application info
    APP_INFO,
    
    # Agent metrics
    AGENT_EXECUTIONS,
    AGENT_EXECUTION_DURATION,
    AGENT_TOKENS_USED,
    ACTIVE_AGENTS,
    AGENT_ERRORS,
    AGENT_TOOL_CALLS,
    
    # Workflow metrics
    WORKFLOW_EXECUTIONS,
    WORKFLOW_EXECUTION_DURATION,
    WORKFLOW_NODE_EXECUTIONS,
    WORKFLOW_NODE_DURATION,
    ACTIVE_WORKFLOWS,
    
    # Swarm metrics
    SWARM_EXECUTIONS,
    SWARM_EXECUTION_DURATION,
    SWARM_AGENT_TASKS,
    SWARM_EVENTS,
    ACTIVE_SWARMS,
    SWARM_AGENTS_COUNT,
    
    # AI Org metrics
    AIORG_EXECUTIONS,
    AIORG_TASK_DURATION,
    AIORG_DELEGATIONS,
    AIORG_HITL_INTERVENTIONS,
    ACTIVE_AIORGS,
    
    # LLM metrics
    LLM_REQUESTS,
    LLM_REQUEST_DURATION,
    LLM_TOKENS,
    LLM_ERRORS,
    LLM_COST,
    
    # Database metrics
    DB_OPERATIONS,
    DB_OPERATION_DURATION,
    DB_CONNECTIONS,
    DB_POOL_SIZE,
    
    # HTTP metrics
    HTTP_REQUESTS,
    HTTP_REQUEST_DURATION,
    HTTP_REQUEST_SIZE,
    HTTP_RESPONSE_SIZE,
    ACTIVE_REQUESTS,
    
    # Tool metrics
    TOOL_EXECUTIONS,
    TOOL_EXECUTION_DURATION,
    TOOL_ERRORS,
    REGISTERED_TOOLS,
    
    # MCP metrics
    MCP_CONNECTIONS,
    MCP_REQUESTS,
    MCP_REQUEST_DURATION,
    
    # Actor metrics
    ACTOR_MESSAGES,
    ACTOR_MESSAGE_DURATION,
    ACTIVE_ACTORS,
    ACTOR_MAILBOX_SIZE,
    DEAD_LETTERS,
    
    # Script metrics
    SCRIPT_EXECUTIONS,
    SCRIPT_EXECUTION_DURATION,
    
    # System metrics
    SYSTEM_UPTIME,
    SYSTEM_START_TIME,
    
    # Notification metrics
    NOTIFICATIONS_SENT,
    NOTIFICATION_DURATION,
    
    # Helper functions
    get_metrics_output,
    get_content_type,
    init_app_info,
    set_start_time,
    
    # Decorators and utilities
    track_execution_time,
    track_counter,
    MetricsContext,
)

__all__ = [
    # Availability
    'PROMETHEUS_AVAILABLE',
    
    # App info
    'APP_INFO',
    
    # Agent
    'AGENT_EXECUTIONS',
    'AGENT_EXECUTION_DURATION',
    'AGENT_TOKENS_USED',
    'ACTIVE_AGENTS',
    'AGENT_ERRORS',
    'AGENT_TOOL_CALLS',
    
    # Workflow
    'WORKFLOW_EXECUTIONS',
    'WORKFLOW_EXECUTION_DURATION',
    'WORKFLOW_NODE_EXECUTIONS',
    'WORKFLOW_NODE_DURATION',
    'ACTIVE_WORKFLOWS',
    
    # Swarm
    'SWARM_EXECUTIONS',
    'SWARM_EXECUTION_DURATION',
    'SWARM_AGENT_TASKS',
    'SWARM_EVENTS',
    'ACTIVE_SWARMS',
    'SWARM_AGENTS_COUNT',
    
    # AI Org
    'AIORG_EXECUTIONS',
    'AIORG_TASK_DURATION',
    'AIORG_DELEGATIONS',
    'AIORG_HITL_INTERVENTIONS',
    'ACTIVE_AIORGS',
    
    # LLM
    'LLM_REQUESTS',
    'LLM_REQUEST_DURATION',
    'LLM_TOKENS',
    'LLM_ERRORS',
    'LLM_COST',
    
    # Database
    'DB_OPERATIONS',
    'DB_OPERATION_DURATION',
    'DB_CONNECTIONS',
    'DB_POOL_SIZE',
    
    # HTTP
    'HTTP_REQUESTS',
    'HTTP_REQUEST_DURATION',
    'HTTP_REQUEST_SIZE',
    'HTTP_RESPONSE_SIZE',
    'ACTIVE_REQUESTS',
    
    # Tools
    'TOOL_EXECUTIONS',
    'TOOL_EXECUTION_DURATION',
    'TOOL_ERRORS',
    'REGISTERED_TOOLS',
    
    # MCP
    'MCP_CONNECTIONS',
    'MCP_REQUESTS',
    'MCP_REQUEST_DURATION',
    
    # Actor
    'ACTOR_MESSAGES',
    'ACTOR_MESSAGE_DURATION',
    'ACTIVE_ACTORS',
    'ACTOR_MAILBOX_SIZE',
    'DEAD_LETTERS',
    
    # Scripts
    'SCRIPT_EXECUTIONS',
    'SCRIPT_EXECUTION_DURATION',
    
    # System
    'SYSTEM_UPTIME',
    'SYSTEM_START_TIME',
    
    # Notifications
    'NOTIFICATIONS_SENT',
    'NOTIFICATION_DURATION',
    
    # Functions
    'get_metrics_output',
    'get_content_type',
    'init_app_info',
    'set_start_time',
    
    # Utilities
    'track_execution_time',
    'track_counter',
    'MetricsContext',
]

__version__ = '1.4.8'
