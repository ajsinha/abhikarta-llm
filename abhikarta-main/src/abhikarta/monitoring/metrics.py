"""
Prometheus Metrics Definitions for Abhikarta-LLM.

This module defines all Prometheus metrics used throughout the application
for monitoring agents, workflows, swarms, AI organizations, and system health.

Usage:
    from abhikarta.monitoring import metrics
    
    # Increment a counter
    metrics.AGENT_EXECUTIONS.labels(agent_type='react', status='success').inc()
    
    # Observe a histogram value
    metrics.AGENT_EXECUTION_DURATION.labels(agent_type='react').observe(1.5)
    
    # Set a gauge value
    metrics.ACTIVE_AGENTS.set(10)

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.4.8
"""

import logging
from typing import Optional
from functools import wraps
import time

try:
    from prometheus_client import (
        Counter,
        Histogram,
        Gauge,
        Summary,
        Info,
        CollectorRegistry,
        REGISTRY,
        generate_latest,
        CONTENT_TYPE_LATEST,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Create dummy classes for when prometheus_client is not installed
    class DummyMetric:
        def labels(self, **kwargs):
            return self
        def inc(self, amount=1):
            pass
        def dec(self, amount=1):
            pass
        def set(self, value):
            pass
        def observe(self, value):
            pass
        def info(self, val):
            pass
        def time(self):
            return DummyTimer()
    
    class DummyTimer:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    
    Counter = Histogram = Gauge = Summary = Info = lambda *args, **kwargs: DummyMetric()
    REGISTRY = None
    generate_latest = lambda r=None: b""
    CONTENT_TYPE_LATEST = "text/plain"

logger = logging.getLogger(__name__)

# =============================================================================
# APPLICATION INFO
# =============================================================================

APP_INFO = Info(
    'abhikarta_app',
    'Abhikarta-LLM application information'
)

# =============================================================================
# AGENT METRICS
# =============================================================================

AGENT_EXECUTIONS = Counter(
    'abhikarta_agent_executions_total',
    'Total number of agent executions',
    ['agent_id', 'agent_type', 'status']
)

AGENT_EXECUTION_DURATION = Histogram(
    'abhikarta_agent_execution_duration_seconds',
    'Agent execution duration in seconds',
    ['agent_id', 'agent_type'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0)
)

AGENT_TOKENS_USED = Counter(
    'abhikarta_agent_tokens_total',
    'Total tokens used by agents',
    ['agent_id', 'agent_type', 'token_type']  # token_type: input, output
)

ACTIVE_AGENTS = Gauge(
    'abhikarta_active_agents',
    'Number of currently active agents',
    ['agent_type']
)

AGENT_ERRORS = Counter(
    'abhikarta_agent_errors_total',
    'Total number of agent errors',
    ['agent_id', 'agent_type', 'error_type']
)

AGENT_TOOL_CALLS = Counter(
    'abhikarta_agent_tool_calls_total',
    'Total number of tool calls by agents',
    ['agent_id', 'tool_name', 'status']
)

# =============================================================================
# WORKFLOW METRICS
# =============================================================================

WORKFLOW_EXECUTIONS = Counter(
    'abhikarta_workflow_executions_total',
    'Total number of workflow executions',
    ['workflow_id', 'status']
)

WORKFLOW_EXECUTION_DURATION = Histogram(
    'abhikarta_workflow_execution_duration_seconds',
    'Workflow execution duration in seconds',
    ['workflow_id'],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0, 1800.0, 3600.0)
)

WORKFLOW_NODE_EXECUTIONS = Counter(
    'abhikarta_workflow_node_executions_total',
    'Total number of workflow node executions',
    ['workflow_id', 'node_id', 'node_type', 'status']
)

WORKFLOW_NODE_DURATION = Histogram(
    'abhikarta_workflow_node_duration_seconds',
    'Workflow node execution duration in seconds',
    ['workflow_id', 'node_type'],
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 120.0)
)

ACTIVE_WORKFLOWS = Gauge(
    'abhikarta_active_workflows',
    'Number of currently running workflows'
)

# =============================================================================
# SWARM METRICS
# =============================================================================

SWARM_EXECUTIONS = Counter(
    'abhikarta_swarm_executions_total',
    'Total number of swarm executions',
    ['swarm_id', 'status']
)

SWARM_EXECUTION_DURATION = Histogram(
    'abhikarta_swarm_execution_duration_seconds',
    'Swarm execution duration in seconds',
    ['swarm_id'],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0)
)

SWARM_AGENT_TASKS = Counter(
    'abhikarta_swarm_agent_tasks_total',
    'Total number of tasks assigned to swarm agents',
    ['swarm_id', 'agent_id', 'status']
)

SWARM_EVENTS = Counter(
    'abhikarta_swarm_events_total',
    'Total number of swarm events',
    ['swarm_id', 'event_type']
)

ACTIVE_SWARMS = Gauge(
    'abhikarta_active_swarms',
    'Number of currently active swarms'
)

SWARM_AGENTS_COUNT = Gauge(
    'abhikarta_swarm_agents_count',
    'Number of agents in each swarm',
    ['swarm_id']
)

# =============================================================================
# AI ORGANIZATION METRICS
# =============================================================================

AIORG_EXECUTIONS = Counter(
    'abhikarta_aiorg_executions_total',
    'Total number of AI organization task executions',
    ['org_id', 'status']
)

AIORG_TASK_DURATION = Histogram(
    'abhikarta_aiorg_task_duration_seconds',
    'AI organization task execution duration in seconds',
    ['org_id', 'node_id'],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0)
)

AIORG_DELEGATIONS = Counter(
    'abhikarta_aiorg_delegations_total',
    'Total number of task delegations in AI organizations',
    ['org_id', 'from_node', 'to_node']
)

AIORG_HITL_INTERVENTIONS = Counter(
    'abhikarta_aiorg_hitl_interventions_total',
    'Total number of human-in-the-loop interventions',
    ['org_id', 'action_type']  # action_type: approve, reject, modify, escalate
)

ACTIVE_AIORGS = Gauge(
    'abhikarta_active_aiorgs',
    'Number of currently active AI organizations'
)

# =============================================================================
# LLM PROVIDER METRICS
# =============================================================================

LLM_REQUESTS = Counter(
    'abhikarta_llm_requests_total',
    'Total number of LLM API requests',
    ['provider', 'model', 'status']
)

LLM_REQUEST_DURATION = Histogram(
    'abhikarta_llm_request_duration_seconds',
    'LLM API request duration in seconds',
    ['provider', 'model'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
)

LLM_TOKENS = Counter(
    'abhikarta_llm_tokens_total',
    'Total tokens processed by LLM providers',
    ['provider', 'model', 'token_type']  # token_type: prompt, completion
)

LLM_ERRORS = Counter(
    'abhikarta_llm_errors_total',
    'Total number of LLM API errors',
    ['provider', 'model', 'error_type']
)

LLM_COST = Counter(
    'abhikarta_llm_cost_dollars',
    'Estimated LLM API cost in dollars',
    ['provider', 'model']
)

# =============================================================================
# DATABASE METRICS
# =============================================================================

DB_OPERATIONS = Counter(
    'abhikarta_db_operations_total',
    'Total number of database operations',
    ['operation', 'table', 'status']  # operation: select, insert, update, delete
)

DB_OPERATION_DURATION = Histogram(
    'abhikarta_db_operation_duration_seconds',
    'Database operation duration in seconds',
    ['operation', 'table'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

DB_CONNECTIONS = Gauge(
    'abhikarta_db_connections',
    'Number of active database connections',
    ['db_type']  # sqlite, postgresql
)

DB_POOL_SIZE = Gauge(
    'abhikarta_db_pool_size',
    'Database connection pool size',
    ['db_type']
)

# =============================================================================
# API/HTTP METRICS
# =============================================================================

HTTP_REQUESTS = Counter(
    'abhikarta_http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

HTTP_REQUEST_DURATION = Histogram(
    'abhikarta_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

HTTP_REQUEST_SIZE = Histogram(
    'abhikarta_http_request_size_bytes',
    'HTTP request body size in bytes',
    ['method', 'endpoint'],
    buckets=(100, 1000, 10000, 100000, 1000000)
)

HTTP_RESPONSE_SIZE = Histogram(
    'abhikarta_http_response_size_bytes',
    'HTTP response body size in bytes',
    ['method', 'endpoint'],
    buckets=(100, 1000, 10000, 100000, 1000000)
)

ACTIVE_REQUESTS = Gauge(
    'abhikarta_active_requests',
    'Number of currently active HTTP requests'
)

# =============================================================================
# TOOL METRICS
# =============================================================================

TOOL_EXECUTIONS = Counter(
    'abhikarta_tool_executions_total',
    'Total number of tool executions',
    ['tool_name', 'tool_type', 'status']
)

TOOL_EXECUTION_DURATION = Histogram(
    'abhikarta_tool_execution_duration_seconds',
    'Tool execution duration in seconds',
    ['tool_name', 'tool_type'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)
)

TOOL_ERRORS = Counter(
    'abhikarta_tool_errors_total',
    'Total number of tool execution errors',
    ['tool_name', 'tool_type', 'error_type']
)

REGISTERED_TOOLS = Gauge(
    'abhikarta_registered_tools',
    'Number of registered tools',
    ['tool_type']
)

# =============================================================================
# MCP METRICS
# =============================================================================

MCP_CONNECTIONS = Gauge(
    'abhikarta_mcp_connections',
    'Number of active MCP server connections',
    ['server_name']
)

MCP_REQUESTS = Counter(
    'abhikarta_mcp_requests_total',
    'Total number of MCP requests',
    ['server_name', 'method', 'status']
)

MCP_REQUEST_DURATION = Histogram(
    'abhikarta_mcp_request_duration_seconds',
    'MCP request duration in seconds',
    ['server_name', 'method'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

# =============================================================================
# ACTOR SYSTEM METRICS
# =============================================================================

ACTOR_MESSAGES = Counter(
    'abhikarta_actor_messages_total',
    'Total number of actor messages processed',
    ['actor_type', 'message_type']
)

ACTOR_MESSAGE_DURATION = Histogram(
    'abhikarta_actor_message_duration_seconds',
    'Actor message processing duration in seconds',
    ['actor_type'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

ACTIVE_ACTORS = Gauge(
    'abhikarta_active_actors',
    'Number of active actors',
    ['actor_type']
)

ACTOR_MAILBOX_SIZE = Gauge(
    'abhikarta_actor_mailbox_size',
    'Actor mailbox queue size',
    ['actor_path']
)

DEAD_LETTERS = Counter(
    'abhikarta_dead_letters_total',
    'Total number of dead letters',
    ['reason']
)

# =============================================================================
# SCRIPT EXECUTION METRICS
# =============================================================================

SCRIPT_EXECUTIONS = Counter(
    'abhikarta_script_executions_total',
    'Total number of Python script executions',
    ['script_id', 'status']
)

SCRIPT_EXECUTION_DURATION = Histogram(
    'abhikarta_script_execution_duration_seconds',
    'Python script execution duration in seconds',
    ['script_id'],
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0)
)

# =============================================================================
# SYSTEM METRICS
# =============================================================================

SYSTEM_UPTIME = Gauge(
    'abhikarta_system_uptime_seconds',
    'System uptime in seconds'
)

SYSTEM_START_TIME = Gauge(
    'abhikarta_system_start_time_seconds',
    'System start time as Unix timestamp'
)

# =============================================================================
# NOTIFICATION METRICS
# =============================================================================

NOTIFICATIONS_SENT = Counter(
    'abhikarta_notifications_sent_total',
    'Total number of notifications sent',
    ['channel', 'status']  # channel: email, slack, teams, webhook
)

NOTIFICATION_DURATION = Histogram(
    'abhikarta_notification_duration_seconds',
    'Notification sending duration in seconds',
    ['channel'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_metrics_output() -> bytes:
    """
    Generate Prometheus metrics output.
    
    Returns:
        bytes: Prometheus-formatted metrics
    """
    if not PROMETHEUS_AVAILABLE:
        return b"# Prometheus client not installed\n"
    return generate_latest(REGISTRY)


def get_content_type() -> str:
    """
    Get the content type for Prometheus metrics.
    
    Returns:
        str: Content type string
    """
    return CONTENT_TYPE_LATEST


def init_app_info(version: str, environment: str = "production"):
    """
    Initialize application info metric.
    
    Args:
        version: Application version
        environment: Deployment environment
    """
    if PROMETHEUS_AVAILABLE:
        APP_INFO.info({
            'version': version,
            'environment': environment,
            'python_version': __import__('sys').version.split()[0]
        })


def set_start_time():
    """Set the system start time metric."""
    if PROMETHEUS_AVAILABLE:
        SYSTEM_START_TIME.set(time.time())


# =============================================================================
# DECORATORS
# =============================================================================

def track_execution_time(metric: Histogram, **labels):
    """
    Decorator to track function execution time.
    
    Args:
        metric: Histogram metric to observe
        **labels: Labels to apply to the metric
    
    Usage:
        @track_execution_time(AGENT_EXECUTION_DURATION, agent_type='react')
        def execute_agent():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                metric.labels(**labels).observe(duration)
        return wrapper
    return decorator


def track_counter(metric: Counter, **labels):
    """
    Decorator to increment a counter on function call.
    
    Args:
        metric: Counter metric to increment
        **labels: Labels to apply to the metric
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            metric.labels(**labels).inc()
            return func(*args, **kwargs)
        return wrapper
    return decorator


class MetricsContext:
    """
    Context manager for tracking metrics.
    
    Usage:
        with MetricsContext(AGENT_EXECUTION_DURATION, agent_type='react') as ctx:
            # Do work
            ctx.set_status('success')
    """
    
    def __init__(self, duration_metric: Optional[Histogram] = None,
                 counter_metric: Optional[Counter] = None,
                 **labels):
        self.duration_metric = duration_metric
        self.counter_metric = counter_metric
        self.labels = labels
        self.start_time = None
        self.status = 'success'
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is not None:
            self.status = 'error'
        
        if self.duration_metric:
            self.duration_metric.labels(**self.labels).observe(duration)
        
        if self.counter_metric:
            counter_labels = {**self.labels, 'status': self.status}
            self.counter_metric.labels(**counter_labels).inc()
        
        return False  # Don't suppress exceptions
    
    def set_status(self, status: str):
        """Set the status label value."""
        self.status = status


# Log availability
if PROMETHEUS_AVAILABLE:
    logger.info("Prometheus metrics initialized successfully")
else:
    logger.warning("prometheus_client not installed - metrics will be disabled")
