"""
PostgreSQL Schema - Database schema definitions for PostgreSQL backend.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.

Patent Pending: Certain architectural patterns and implementations described in this
software may be subject to patent applications.

Note: This schema mirrors the SQLite schema with PostgreSQL-specific syntax:
- SERIAL instead of INTEGER PRIMARY KEY AUTOINCREMENT
- BOOLEAN instead of INTEGER for boolean fields
- JSONB instead of TEXT for JSON storage
- TIMESTAMP WITH TIME ZONE for timestamps
- ON CONFLICT for upserts instead of INSERT OR IGNORE
"""

import logging

logger = logging.getLogger(__name__)


class PostgresSchema:
    """
    PostgreSQL database schema definitions.
    
    Provides SQL statements for creating and managing database tables
    optimized for PostgreSQL.
    """
    
    # ==========================================================================
    # SCHEMA VERSION
    # ==========================================================================
    
    SCHEMA_VERSION = "1.4.0"
    
    # ==========================================================================
    # TABLE DEFINITIONS
    # ==========================================================================
    
    CREATE_SCHEMA_VERSION = """
    CREATE TABLE IF NOT EXISTS schema_version (
        id SERIAL PRIMARY KEY,
        version TEXT NOT NULL,
        applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        description TEXT
    );
    """
    
    CREATE_USERS_TABLE = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        user_id TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        fullname TEXT NOT NULL,
        email TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP WITH TIME ZONE,
        failed_login_attempts INTEGER DEFAULT 0,
        locked_until TIMESTAMP WITH TIME ZONE,
        preferences JSONB DEFAULT '{}'
    );
    """
    
    CREATE_ROLES_TABLE = """
    CREATE TABLE IF NOT EXISTS roles (
        id SERIAL PRIMARY KEY,
        role_name TEXT UNIQUE NOT NULL,
        display_name TEXT NOT NULL,
        description TEXT,
        permissions JSONB DEFAULT '[]',
        is_system BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_USER_ROLES_TABLE = """
    CREATE TABLE IF NOT EXISTS user_roles (
        id SERIAL PRIMARY KEY,
        user_id TEXT NOT NULL,
        role_name TEXT NOT NULL,
        assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        assigned_by TEXT,
        UNIQUE(user_id, role_name),
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (role_name) REFERENCES roles(role_name) ON DELETE CASCADE
    );
    """
    
    CREATE_AGENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS agents (
        id SERIAL PRIMARY KEY,
        agent_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        agent_type TEXT NOT NULL DEFAULT 'react',
        version TEXT DEFAULT '1.0.0',
        status TEXT DEFAULT 'draft',
        config JSONB DEFAULT '{}',
        workflow JSONB DEFAULT '{}',
        llm_config JSONB DEFAULT '{}',
        tools JSONB DEFAULT '[]',
        hitl_config JSONB DEFAULT '{}',
        tags JSONB DEFAULT '[]',
        created_by TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        published_at TIMESTAMP WITH TIME ZONE,
        deprecated_at TIMESTAMP WITH TIME ZONE,
        FOREIGN KEY (created_by) REFERENCES users(user_id)
    );
    """
    
    CREATE_AGENT_VERSIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS agent_versions (
        id SERIAL PRIMARY KEY,
        agent_id TEXT NOT NULL,
        version TEXT NOT NULL,
        config_snapshot JSONB NOT NULL,
        workflow_snapshot JSONB,
        created_by TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        change_notes TEXT,
        UNIQUE(agent_id, version),
        FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE
    );
    """
    
    CREATE_AGENT_TEMPLATES_TABLE = """
    CREATE TABLE IF NOT EXISTS agent_templates (
        id SERIAL PRIMARY KEY,
        template_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT NOT NULL,
        agent_type TEXT NOT NULL,
        icon TEXT DEFAULT 'bi-robot',
        difficulty TEXT DEFAULT 'intermediate',
        workflow JSONB DEFAULT '{}',
        llm_config JSONB DEFAULT '{}',
        tools JSONB DEFAULT '[]',
        hitl_config JSONB DEFAULT '{}',
        sample_prompts JSONB DEFAULT '[]',
        tags JSONB DEFAULT '[]',
        is_system BOOLEAN DEFAULT FALSE,
        created_by TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        use_count INTEGER DEFAULT 0
    );
    """
    
    CREATE_EXECUTIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS executions (
        id SERIAL PRIMARY KEY,
        execution_id TEXT UNIQUE NOT NULL,
        agent_id TEXT NOT NULL,
        agent_version TEXT,
        user_id TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        input_data JSONB,
        output_data JSONB,
        error_message TEXT,
        execution_config JSONB DEFAULT '{}',
        started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP WITH TIME ZONE,
        duration_ms INTEGER,
        tokens_used INTEGER DEFAULT 0,
        cost_estimate DECIMAL(10,6) DEFAULT 0.0,
        trace_data JSONB DEFAULT '[]',
        FOREIGN KEY (agent_id) REFERENCES agents(agent_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    """
    
    CREATE_EXECUTION_STEPS_TABLE = """
    CREATE TABLE IF NOT EXISTS execution_steps (
        id SERIAL PRIMARY KEY,
        execution_id TEXT NOT NULL,
        step_number INTEGER NOT NULL,
        node_id TEXT,
        node_type TEXT,
        status TEXT DEFAULT 'pending',
        input_data JSONB,
        output_data JSONB,
        error_message TEXT,
        started_at TIMESTAMP WITH TIME ZONE,
        completed_at TIMESTAMP WITH TIME ZONE,
        duration_ms INTEGER,
        FOREIGN KEY (execution_id) REFERENCES executions(execution_id) ON DELETE CASCADE
    );
    """
    
    CREATE_LLM_CALLS_TABLE = """
    CREATE TABLE IF NOT EXISTS llm_calls (
        id SERIAL PRIMARY KEY,
        call_id TEXT UNIQUE NOT NULL,
        execution_id TEXT,
        agent_id TEXT,
        user_id TEXT NOT NULL,
        provider TEXT NOT NULL,
        model TEXT NOT NULL,
        request_type TEXT DEFAULT 'completion',
        system_prompt TEXT,
        user_prompt TEXT,
        messages JSONB,
        response_content TEXT,
        tool_calls JSONB,
        input_tokens INTEGER DEFAULT 0,
        output_tokens INTEGER DEFAULT 0,
        total_tokens INTEGER DEFAULT 0,
        cost_estimate DECIMAL(10,6) DEFAULT 0.0,
        temperature DECIMAL(3,2),
        max_tokens INTEGER,
        latency_ms INTEGER,
        status TEXT DEFAULT 'success',
        error_message TEXT,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (execution_id) REFERENCES executions(execution_id),
        FOREIGN KEY (agent_id) REFERENCES agents(agent_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    """
    
    CREATE_WORKFLOWS_TABLE = """
    CREATE TABLE IF NOT EXISTS workflows (
        id SERIAL PRIMARY KEY,
        workflow_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        version TEXT DEFAULT '1.0.0',
        workflow_type TEXT DEFAULT 'dag',
        dag_definition JSONB NOT NULL,
        python_modules JSONB DEFAULT '{}',
        entry_point TEXT,
        input_schema JSONB DEFAULT '{}',
        output_schema JSONB DEFAULT '{}',
        dependencies JSONB DEFAULT '[]',
        environment JSONB DEFAULT '{}',
        status TEXT DEFAULT 'draft',
        created_by TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        last_executed_at TIMESTAMP WITH TIME ZONE,
        execution_count INTEGER DEFAULT 0,
        avg_duration_ms INTEGER,
        tags JSONB DEFAULT '[]',
        FOREIGN KEY (created_by) REFERENCES users(user_id)
    );
    """
    
    CREATE_WORKFLOW_NODES_TABLE = """
    CREATE TABLE IF NOT EXISTS workflow_nodes (
        id SERIAL PRIMARY KEY,
        node_id TEXT UNIQUE NOT NULL,
        workflow_id TEXT NOT NULL,
        name TEXT NOT NULL,
        node_type TEXT NOT NULL,
        config JSONB DEFAULT '{}',
        python_code TEXT,
        position_x INTEGER DEFAULT 0,
        position_y INTEGER DEFAULT 0,
        dependencies JSONB DEFAULT '[]',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON DELETE CASCADE
    );
    """
    
    CREATE_HITL_TASKS_TABLE = """
    CREATE TABLE IF NOT EXISTS hitl_tasks (
        id SERIAL PRIMARY KEY,
        task_id TEXT UNIQUE NOT NULL,
        execution_id TEXT,
        workflow_id TEXT,
        agent_id TEXT,
        node_id TEXT,
        task_type TEXT NOT NULL DEFAULT 'approval',
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'pending',
        priority INTEGER DEFAULT 5,
        context JSONB DEFAULT '{}',
        request_data JSONB,
        input_schema JSONB DEFAULT '{}',
        response_data JSONB,
        resolution TEXT,
        assigned_to TEXT,
        assigned_at TIMESTAMP WITH TIME ZONE,
        due_at TIMESTAMP WITH TIME ZONE,
        completed_at TIMESTAMP WITH TIME ZONE,
        completed_by TEXT,
        created_by TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        timeout_minutes INTEGER DEFAULT 1440,
        notification_sent BOOLEAN DEFAULT FALSE,
        reminder_count INTEGER DEFAULT 0,
        last_reminder_at TIMESTAMP WITH TIME ZONE,
        tags JSONB DEFAULT '[]',
        metadata JSONB DEFAULT '{}',
        FOREIGN KEY (execution_id) REFERENCES executions(execution_id),
        FOREIGN KEY (agent_id) REFERENCES agents(agent_id),
        FOREIGN KEY (assigned_to) REFERENCES users(user_id),
        FOREIGN KEY (completed_by) REFERENCES users(user_id)
    );
    """
    
    CREATE_HITL_COMMENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS hitl_comments (
        id SERIAL PRIMARY KEY,
        comment_id TEXT UNIQUE NOT NULL,
        task_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        comment TEXT NOT NULL,
        comment_type TEXT DEFAULT 'comment',
        attachments JSONB DEFAULT '[]',
        is_internal BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES hitl_tasks(task_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    """
    
    CREATE_HITL_ASSIGNMENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS hitl_assignments (
        id SERIAL PRIMARY KEY,
        assignment_id TEXT UNIQUE NOT NULL,
        task_id TEXT NOT NULL,
        assigned_from TEXT,
        assigned_to TEXT NOT NULL,
        assigned_by TEXT NOT NULL,
        reason TEXT,
        assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES hitl_tasks(task_id) ON DELETE CASCADE,
        FOREIGN KEY (assigned_to) REFERENCES users(user_id),
        FOREIGN KEY (assigned_by) REFERENCES users(user_id)
    );
    """
    
    CREATE_MCP_PLUGINS_TABLE = """
    CREATE TABLE IF NOT EXISTS mcp_plugins (
        id SERIAL PRIMARY KEY,
        plugin_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        version TEXT DEFAULT '1.0.0',
        plugin_type TEXT DEFAULT 'tool',
        status TEXT DEFAULT 'active',
        config JSONB DEFAULT '{}',
        manifest JSONB DEFAULT '{}',
        server_name TEXT,
        server_url TEXT,
        capabilities JSONB DEFAULT '[]',
        created_by TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        last_health_check TIMESTAMP WITH TIME ZONE,
        health_status TEXT DEFAULT 'unknown',
        FOREIGN KEY (created_by) REFERENCES users(user_id)
    );
    """
    
    CREATE_MCP_TOOL_SERVERS_TABLE = """
    CREATE TABLE IF NOT EXISTS mcp_tool_servers (
        id SERIAL PRIMARY KEY,
        server_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        base_url TEXT NOT NULL,
        tools_endpoint TEXT DEFAULT '/api/tools/list',
        auth_type TEXT DEFAULT 'none',
        auth_config JSONB DEFAULT '{}',
        is_active BOOLEAN DEFAULT TRUE,
        auto_refresh BOOLEAN DEFAULT TRUE,
        refresh_interval_minutes INTEGER DEFAULT 60,
        last_refresh TIMESTAMP WITH TIME ZONE,
        last_refresh_status TEXT,
        tool_count INTEGER DEFAULT 0,
        cached_tools JSONB DEFAULT '[]',
        timeout_seconds INTEGER DEFAULT 30,
        created_by TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(user_id)
    );
    """
    
    CREATE_AUDIT_LOGS_TABLE = """
    CREATE TABLE IF NOT EXISTS audit_logs (
        id SERIAL PRIMARY KEY,
        log_id TEXT UNIQUE NOT NULL,
        action TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT,
        user_id TEXT,
        user_ip TEXT,
        user_agent TEXT,
        old_value JSONB,
        new_value JSONB,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    """
    
    CREATE_SESSIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS sessions (
        id SERIAL PRIMARY KEY,
        session_id TEXT UNIQUE NOT NULL,
        user_id TEXT NOT NULL,
        session_data JSONB DEFAULT '{}',
        ip_address TEXT,
        user_agent TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """
    
    CREATE_API_KEYS_TABLE = """
    CREATE TABLE IF NOT EXISTS api_keys (
        id SERIAL PRIMARY KEY,
        key_id TEXT UNIQUE NOT NULL,
        user_id TEXT NOT NULL,
        key_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        permissions JSONB DEFAULT '[]',
        rate_limit INTEGER DEFAULT 1000,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP WITH TIME ZONE,
        last_used_at TIMESTAMP WITH TIME ZONE,
        usage_count INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """
    
    CREATE_SETTINGS_TABLE = """
    CREATE TABLE IF NOT EXISTS system_settings (
        id SERIAL PRIMARY KEY,
        setting_key TEXT UNIQUE NOT NULL,
        setting_value TEXT,
        setting_type TEXT DEFAULT 'string',
        description TEXT,
        is_encrypted BOOLEAN DEFAULT FALSE,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_by TEXT
    );
    """
    
    CREATE_CODE_FRAGMENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS code_fragments (
        id SERIAL PRIMARY KEY,
        fragment_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        language TEXT DEFAULT 'python',
        code TEXT NOT NULL,
        version TEXT DEFAULT '1.0.0',
        category TEXT DEFAULT 'general',
        tags JSONB DEFAULT '[]',
        dependencies JSONB DEFAULT '[]',
        is_active BOOLEAN DEFAULT TRUE,
        is_system BOOLEAN DEFAULT FALSE,
        created_by TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_by TEXT,
        usage_count INTEGER DEFAULT 0,
        FOREIGN KEY (created_by) REFERENCES users(user_id)
    );
    """
    
    CREATE_LLM_PROVIDERS_TABLE = """
    CREATE TABLE IF NOT EXISTS llm_providers (
        id SERIAL PRIMARY KEY,
        provider_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        provider_type TEXT NOT NULL,
        api_endpoint TEXT,
        api_key_name TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        is_default BOOLEAN DEFAULT FALSE,
        config JSONB DEFAULT '{}',
        rate_limit_rpm INTEGER DEFAULT 60,
        rate_limit_tpm INTEGER DEFAULT 100000,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT,
        FOREIGN KEY (created_by) REFERENCES users(user_id)
    );
    """
    
    CREATE_LLM_MODELS_TABLE = """
    CREATE TABLE IF NOT EXISTS llm_models (
        id SERIAL PRIMARY KEY,
        model_id TEXT UNIQUE NOT NULL,
        provider_id TEXT NOT NULL,
        name TEXT NOT NULL,
        display_name TEXT,
        description TEXT,
        model_type TEXT DEFAULT 'chat',
        context_window INTEGER DEFAULT 4096,
        max_output_tokens INTEGER DEFAULT 4096,
        input_cost_per_1k DECIMAL(10,6) DEFAULT 0.0,
        output_cost_per_1k DECIMAL(10,6) DEFAULT 0.0,
        supports_vision BOOLEAN DEFAULT FALSE,
        supports_functions BOOLEAN DEFAULT FALSE,
        supports_streaming BOOLEAN DEFAULT TRUE,
        is_active BOOLEAN DEFAULT TRUE,
        is_default BOOLEAN DEFAULT FALSE,
        config JSONB DEFAULT '{}',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (provider_id) REFERENCES llm_providers(provider_id)
    );
    """
    
    CREATE_MODEL_PERMISSIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS model_permissions (
        id SERIAL PRIMARY KEY,
        model_id TEXT NOT NULL,
        role_name TEXT NOT NULL,
        can_use BOOLEAN DEFAULT TRUE,
        daily_limit INTEGER DEFAULT -1,
        monthly_limit INTEGER DEFAULT -1,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT,
        UNIQUE(model_id, role_name),
        FOREIGN KEY (model_id) REFERENCES llm_models(model_id),
        FOREIGN KEY (role_name) REFERENCES roles(role_name)
    );
    """
    
    # ==========================================================================
    # SWARM TABLES (v1.3.0)
    # ==========================================================================
    
    CREATE_SWARMS_TABLE = """
    CREATE TABLE IF NOT EXISTS swarms (
        id SERIAL PRIMARY KEY,
        swarm_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        version TEXT DEFAULT '1.0.0',
        status TEXT DEFAULT 'draft',
        category TEXT DEFAULT 'general',
        tags JSONB DEFAULT '[]',
        definition_json JSONB,
        config_json JSONB,
        created_by TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        total_executions INTEGER DEFAULT 0,
        successful_executions INTEGER DEFAULT 0,
        failed_executions INTEGER DEFAULT 0,
        total_events_processed INTEGER DEFAULT 0,
        FOREIGN KEY (created_by) REFERENCES users(user_id)
    );
    """
    
    CREATE_SWARM_AGENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS swarm_agents (
        id SERIAL PRIMARY KEY,
        membership_id TEXT UNIQUE NOT NULL,
        swarm_id TEXT NOT NULL,
        agent_id TEXT NOT NULL,
        agent_name TEXT,
        role TEXT DEFAULT 'worker',
        description TEXT,
        subscriptions_json JSONB DEFAULT '[]',
        max_instances INTEGER DEFAULT 10,
        min_instances INTEGER DEFAULT 0,
        auto_scale BOOLEAN DEFAULT TRUE,
        idle_timeout INTEGER DEFAULT 300,
        is_active BOOLEAN DEFAULT TRUE,
        current_instances INTEGER DEFAULT 0,
        total_tasks_processed INTEGER DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (swarm_id) REFERENCES swarms(swarm_id) ON DELETE CASCADE,
        FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
    );
    """
    
    CREATE_SWARM_TRIGGERS_TABLE = """
    CREATE TABLE IF NOT EXISTS swarm_triggers (
        id SERIAL PRIMARY KEY,
        trigger_id TEXT UNIQUE NOT NULL,
        swarm_id TEXT NOT NULL,
        trigger_type TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        config_json JSONB DEFAULT '{}',
        filter_expression TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        last_triggered TIMESTAMP WITH TIME ZONE,
        trigger_count INTEGER DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (swarm_id) REFERENCES swarms(swarm_id) ON DELETE CASCADE
    );
    """
    
    CREATE_SWARM_EXECUTIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS swarm_executions (
        id SERIAL PRIMARY KEY,
        execution_id TEXT UNIQUE NOT NULL,
        swarm_id TEXT NOT NULL,
        trigger_type TEXT,
        trigger_data JSONB,
        correlation_id TEXT,
        status TEXT DEFAULT 'pending',
        started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP WITH TIME ZONE,
        duration_ms INTEGER,
        iterations INTEGER DEFAULT 0,
        events_processed INTEGER DEFAULT 0,
        result_json JSONB,
        error_message TEXT,
        user_id TEXT,
        FOREIGN KEY (swarm_id) REFERENCES swarms(swarm_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    """
    
    CREATE_SWARM_EVENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS swarm_events (
        id SERIAL PRIMARY KEY,
        event_id TEXT UNIQUE NOT NULL,
        swarm_id TEXT NOT NULL,
        execution_id TEXT,
        event_type TEXT NOT NULL,
        source TEXT,
        target TEXT,
        payload_json JSONB,
        headers_json JSONB DEFAULT '{}',
        priority INTEGER DEFAULT 1,
        correlation_id TEXT,
        parent_id TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (swarm_id) REFERENCES swarms(swarm_id),
        FOREIGN KEY (execution_id) REFERENCES swarm_executions(execution_id)
    );
    """
    
    CREATE_SWARM_DECISIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS swarm_decisions (
        id SERIAL PRIMARY KEY,
        decision_id TEXT UNIQUE NOT NULL,
        swarm_id TEXT NOT NULL,
        execution_id TEXT,
        decision_type TEXT NOT NULL,
        trigger_event_id TEXT,
        event_type TEXT,
        target_agents JSONB DEFAULT '[]',
        payload_json JSONB,
        reasoning TEXT,
        confidence DECIMAL(3,2) DEFAULT 1.0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (swarm_id) REFERENCES swarms(swarm_id),
        FOREIGN KEY (execution_id) REFERENCES swarm_executions(execution_id)
    );
    """
    
    # ==========================================================================
    # NOTIFICATION TABLES (v1.4.0)
    # ==========================================================================
    
    CREATE_NOTIFICATION_CHANNELS = """
    CREATE TABLE IF NOT EXISTS notification_channels (
        id SERIAL PRIMARY KEY,
        channel_id TEXT UNIQUE NOT NULL,
        channel_type TEXT NOT NULL,
        name TEXT NOT NULL,
        config JSONB NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        created_by TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_NOTIFICATION_LOGS = """
    CREATE TABLE IF NOT EXISTS notification_logs (
        id SERIAL PRIMARY KEY,
        notification_id TEXT UNIQUE NOT NULL,
        channel_id TEXT,
        channel_type TEXT NOT NULL,
        recipient TEXT,
        title TEXT,
        body TEXT,
        level TEXT DEFAULT 'info',
        status TEXT DEFAULT 'pending',
        error_message TEXT,
        source TEXT,
        source_type TEXT,
        correlation_id TEXT,
        sent_at TIMESTAMP WITH TIME ZONE,
        delivered_at TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_WEBHOOK_ENDPOINTS = """
    CREATE TABLE IF NOT EXISTS webhook_endpoints (
        id SERIAL PRIMARY KEY,
        endpoint_id TEXT UNIQUE NOT NULL,
        path TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        auth_method TEXT DEFAULT 'hmac',
        secret_hash TEXT,
        target_type TEXT,
        target_id TEXT,
        rate_limit INTEGER DEFAULT 100,
        is_active BOOLEAN DEFAULT TRUE,
        created_by TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_WEBHOOK_EVENTS = """
    CREATE TABLE IF NOT EXISTS webhook_events (
        id SERIAL PRIMARY KEY,
        event_id TEXT UNIQUE NOT NULL,
        endpoint_id TEXT NOT NULL,
        event_type TEXT,
        payload JSONB,
        headers JSONB,
        source_ip TEXT,
        verified BOOLEAN DEFAULT FALSE,
        processed BOOLEAN DEFAULT FALSE,
        process_result JSONB,
        error_message TEXT,
        received_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        processed_at TIMESTAMP WITH TIME ZONE,
        FOREIGN KEY (endpoint_id) REFERENCES webhook_endpoints(endpoint_id)
    );
    """
    
    CREATE_USER_NOTIFICATION_PREFS = """
    CREATE TABLE IF NOT EXISTS user_notification_preferences (
        id SERIAL PRIMARY KEY,
        user_id TEXT NOT NULL,
        channel_type TEXT NOT NULL,
        channel_address TEXT,
        enabled BOOLEAN DEFAULT TRUE,
        min_level TEXT DEFAULT 'info',
        quiet_hours_start TEXT,
        quiet_hours_end TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, channel_type)
    );
    """
    
    # ==========================================================================
    # INDEXES
    # ==========================================================================
    
    CREATE_INDEXES = [
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
        "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);",
        "CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_user_roles_role_name ON user_roles(role_name);",
        "CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);",
        "CREATE INDEX IF NOT EXISTS idx_agents_agent_type ON agents(agent_type);",
        "CREATE INDEX IF NOT EXISTS idx_agents_created_by ON agents(created_by);",
        "CREATE INDEX IF NOT EXISTS idx_agents_created_at ON agents(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_executions_agent_id ON executions(agent_id);",
        "CREATE INDEX IF NOT EXISTS idx_executions_user_id ON executions(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status);",
        "CREATE INDEX IF NOT EXISTS idx_executions_started_at ON executions(started_at);",
        "CREATE INDEX IF NOT EXISTS idx_execution_steps_execution_id ON execution_steps(execution_id);",
        "CREATE INDEX IF NOT EXISTS idx_llm_calls_execution_id ON llm_calls(execution_id);",
        "CREATE INDEX IF NOT EXISTS idx_llm_calls_agent_id ON llm_calls(agent_id);",
        "CREATE INDEX IF NOT EXISTS idx_llm_calls_user_id ON llm_calls(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_llm_calls_provider ON llm_calls(provider);",
        "CREATE INDEX IF NOT EXISTS idx_llm_calls_created_at ON llm_calls(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);",
        "CREATE INDEX IF NOT EXISTS idx_workflows_created_by ON workflows(created_by);",
        "CREATE INDEX IF NOT EXISTS idx_workflow_nodes_workflow_id ON workflow_nodes(workflow_id);",
        "CREATE INDEX IF NOT EXISTS idx_hitl_tasks_status ON hitl_tasks(status);",
        "CREATE INDEX IF NOT EXISTS idx_hitl_tasks_assigned_to ON hitl_tasks(assigned_to);",
        "CREATE INDEX IF NOT EXISTS idx_hitl_tasks_execution_id ON hitl_tasks(execution_id);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_type ON audit_logs(entity_type);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);",
        "CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_mcp_plugins_status ON mcp_plugins(status);",
        "CREATE INDEX IF NOT EXISTS idx_mcp_tool_servers_is_active ON mcp_tool_servers(is_active);",
        "CREATE INDEX IF NOT EXISTS idx_code_fragments_category ON code_fragments(category);",
        "CREATE INDEX IF NOT EXISTS idx_code_fragments_language ON code_fragments(language);",
        "CREATE INDEX IF NOT EXISTS idx_code_fragments_is_active ON code_fragments(is_active);",
        "CREATE INDEX IF NOT EXISTS idx_llm_providers_is_active ON llm_providers(is_active);",
        "CREATE INDEX IF NOT EXISTS idx_llm_models_provider_id ON llm_models(provider_id);",
        "CREATE INDEX IF NOT EXISTS idx_llm_models_is_active ON llm_models(is_active);",
        "CREATE INDEX IF NOT EXISTS idx_model_permissions_model_id ON model_permissions(model_id);",
        "CREATE INDEX IF NOT EXISTS idx_model_permissions_role_name ON model_permissions(role_name);",
        # Swarm indexes (v1.3.0)
        "CREATE INDEX IF NOT EXISTS idx_swarms_status ON swarms(status);",
        "CREATE INDEX IF NOT EXISTS idx_swarms_created_by ON swarms(created_by);",
        "CREATE INDEX IF NOT EXISTS idx_swarms_category ON swarms(category);",
        "CREATE INDEX IF NOT EXISTS idx_swarm_agents_swarm_id ON swarm_agents(swarm_id);",
        "CREATE INDEX IF NOT EXISTS idx_swarm_agents_agent_id ON swarm_agents(agent_id);",
        "CREATE INDEX IF NOT EXISTS idx_swarm_triggers_swarm_id ON swarm_triggers(swarm_id);",
        "CREATE INDEX IF NOT EXISTS idx_swarm_triggers_trigger_type ON swarm_triggers(trigger_type);",
        "CREATE INDEX IF NOT EXISTS idx_swarm_executions_swarm_id ON swarm_executions(swarm_id);",
        "CREATE INDEX IF NOT EXISTS idx_swarm_executions_status ON swarm_executions(status);",
        "CREATE INDEX IF NOT EXISTS idx_swarm_executions_correlation_id ON swarm_executions(correlation_id);",
        "CREATE INDEX IF NOT EXISTS idx_swarm_events_swarm_id ON swarm_events(swarm_id);",
        "CREATE INDEX IF NOT EXISTS idx_swarm_events_execution_id ON swarm_events(execution_id);",
        "CREATE INDEX IF NOT EXISTS idx_swarm_events_event_type ON swarm_events(event_type);",
        "CREATE INDEX IF NOT EXISTS idx_swarm_events_correlation_id ON swarm_events(correlation_id);",
        "CREATE INDEX IF NOT EXISTS idx_swarm_decisions_swarm_id ON swarm_decisions(swarm_id);",
        "CREATE INDEX IF NOT EXISTS idx_swarm_decisions_execution_id ON swarm_decisions(execution_id);",
        # Notification indexes (v1.4.0)
        "CREATE INDEX IF NOT EXISTS idx_notification_logs_channel_type ON notification_logs(channel_type);",
        "CREATE INDEX IF NOT EXISTS idx_notification_logs_status ON notification_logs(status);",
        "CREATE INDEX IF NOT EXISTS idx_notification_logs_source ON notification_logs(source);",
        "CREATE INDEX IF NOT EXISTS idx_notification_logs_created_at ON notification_logs(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_webhook_endpoints_path ON webhook_endpoints(path);",
        "CREATE INDEX IF NOT EXISTS idx_webhook_endpoints_is_active ON webhook_endpoints(is_active);",
        "CREATE INDEX IF NOT EXISTS idx_webhook_events_endpoint_id ON webhook_events(endpoint_id);",
        "CREATE INDEX IF NOT EXISTS idx_webhook_events_received_at ON webhook_events(received_at);",
        "CREATE INDEX IF NOT EXISTS idx_user_notification_prefs_user_id ON user_notification_preferences(user_id);",
    ]
    
    # ==========================================================================
    # DEFAULT DATA
    # ==========================================================================
    
    INSERT_DEFAULT_ROLES = """
    INSERT INTO roles (role_name, display_name, description, permissions, is_system) VALUES
        ('super_admin', 'Super Administrator', 'Full system access', '["*"]', TRUE),
        ('domain_admin', 'Domain Administrator', 'Domain-level admin access', '["users:read", "users:write", "agents:read", "agents:write", "agents:publish", "executions:*", "audit:read"]', TRUE),
        ('agent_developer', 'Agent Developer', 'Create and manage agents', '["agents:read", "agents:write", "agents:test", "templates:read", "executions:read"]', TRUE),
        ('agent_publisher', 'Agent Publisher', 'Review and publish agents', '["agents:read", "agents:review", "agents:publish", "executions:read"]', TRUE),
        ('hitl_reviewer', 'HITL Reviewer', 'Review HITL tasks', '["hitl:read", "hitl:respond", "executions:read"]', TRUE),
        ('agent_user', 'Agent User', 'Execute published agents', '["agents:read:published", "executions:create", "executions:read:own"]', TRUE),
        ('viewer', 'Viewer', 'Read-only access', '["agents:read:published", "executions:read:own"]', TRUE)
    ON CONFLICT (role_name) DO NOTHING;
    """
    
    INSERT_SCHEMA_VERSION = """
    INSERT INTO schema_version (version, description) VALUES ('{version}', 'Initial schema creation');
    """
    
    INSERT_DEFAULT_PROVIDERS = """
    INSERT INTO llm_providers (provider_id, name, description, provider_type, api_key_name, is_active, is_default, config) VALUES
        ('openai', 'OpenAI', 'OpenAI GPT models', 'openai', 'OPENAI_API_KEY', TRUE, TRUE, '{"base_url": "https://api.openai.com/v1"}'),
        ('anthropic', 'Anthropic', 'Claude models', 'anthropic', 'ANTHROPIC_API_KEY', TRUE, FALSE, '{"base_url": "https://api.anthropic.com"}'),
        ('google', 'Google AI', 'Gemini models', 'google', 'GOOGLE_API_KEY', TRUE, FALSE, '{}'),
        ('azure', 'Azure OpenAI', 'Azure-hosted models', 'azure', 'AZURE_OPENAI_KEY', FALSE, FALSE, '{"api_version": "2024-02-15-preview"}'),
        ('mistral', 'Mistral AI', 'Mistral models', 'mistral', 'MISTRAL_API_KEY', TRUE, FALSE, '{"base_url": "https://api.mistral.ai/v1"}'),
        ('groq', 'Groq', 'Groq inference', 'groq', 'GROQ_API_KEY', TRUE, FALSE, '{"base_url": "https://api.groq.com/openai/v1"}'),
        ('together', 'Together AI', 'Together AI models', 'together', 'TOGETHER_API_KEY', TRUE, FALSE, '{"base_url": "https://api.together.xyz/v1"}'),
        ('cohere', 'Cohere', 'Cohere models', 'cohere', 'COHERE_API_KEY', TRUE, FALSE, '{}'),
        ('bedrock', 'AWS Bedrock', 'Amazon Bedrock', 'bedrock', 'AWS_ACCESS_KEY_ID', FALSE, FALSE, '{"region": "us-east-1"}'),
        ('ollama', 'Ollama', 'Local Ollama', 'ollama', '', TRUE, FALSE, '{"base_url": "http://localhost:11434"}'),
        ('huggingface', 'Hugging Face', 'HF Inference API', 'huggingface', 'HF_API_TOKEN', TRUE, FALSE, '{"base_url": "https://api-inference.huggingface.co"}')
    ON CONFLICT (provider_id) DO NOTHING;
    """
    
    INSERT_DEFAULT_MODELS = """
    INSERT INTO llm_models (model_id, provider_id, name, display_name, description, context_window, max_output_tokens, input_cost_per_1k, output_cost_per_1k, supports_vision, supports_functions, is_active, is_default) VALUES
        ('gpt-4o', 'openai', 'gpt-4o', 'GPT-4o', 'Most capable OpenAI model', 128000, 4096, 0.005, 0.015, TRUE, TRUE, TRUE, TRUE),
        ('gpt-4o-mini', 'openai', 'gpt-4o-mini', 'GPT-4o Mini', 'Fast GPT-4o variant', 128000, 16384, 0.00015, 0.0006, TRUE, TRUE, TRUE, FALSE),
        ('gpt-4-turbo', 'openai', 'gpt-4-turbo', 'GPT-4 Turbo', 'GPT-4 Turbo with vision', 128000, 4096, 0.01, 0.03, TRUE, TRUE, TRUE, FALSE),
        ('gpt-3.5-turbo', 'openai', 'gpt-3.5-turbo', 'GPT-3.5 Turbo', 'Fast and cost-effective', 16385, 4096, 0.0005, 0.0015, FALSE, TRUE, TRUE, FALSE),
        ('claude-3-5-sonnet-20241022', 'anthropic', 'claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet', 'Latest Claude 3.5', 200000, 8192, 0.003, 0.015, TRUE, TRUE, TRUE, FALSE),
        ('claude-3-opus-20240229', 'anthropic', 'claude-3-opus-20240229', 'Claude 3 Opus', 'Most powerful Claude', 200000, 4096, 0.015, 0.075, TRUE, TRUE, TRUE, FALSE),
        ('claude-3-haiku-20240307', 'anthropic', 'claude-3-haiku-20240307', 'Claude 3 Haiku', 'Fast Claude', 200000, 4096, 0.00025, 0.00125, TRUE, TRUE, TRUE, FALSE),
        ('gemini-1.5-pro', 'google', 'gemini-1.5-pro', 'Gemini 1.5 Pro', 'Google multimodal', 1000000, 8192, 0.00125, 0.005, TRUE, TRUE, TRUE, FALSE),
        ('gemini-1.5-flash', 'google', 'gemini-1.5-flash', 'Gemini 1.5 Flash', 'Fast Google model', 1000000, 8192, 0.000075, 0.0003, TRUE, TRUE, TRUE, FALSE),
        ('mistral-large-latest', 'mistral', 'mistral-large-latest', 'Mistral Large', 'Flagship Mistral', 128000, 4096, 0.004, 0.012, FALSE, TRUE, TRUE, FALSE),
        ('mistral-small-latest', 'mistral', 'mistral-small-latest', 'Mistral Small', 'Cost-effective Mistral', 32000, 4096, 0.001, 0.003, FALSE, TRUE, TRUE, FALSE),
        ('mixtral-8x7b-32768', 'groq', 'mixtral-8x7b-32768', 'Mixtral 8x7B (Groq)', 'Fast Mixtral', 32768, 4096, 0.00027, 0.00027, FALSE, TRUE, TRUE, FALSE),
        ('llama-3.1-70b-versatile', 'groq', 'llama-3.1-70b-versatile', 'Llama 3.1 70B (Groq)', 'Llama on Groq', 131072, 4096, 0.00059, 0.00079, FALSE, TRUE, TRUE, FALSE),
        ('command-r-plus', 'cohere', 'command-r-plus', 'Command R+', 'Cohere flagship', 128000, 4096, 0.003, 0.015, FALSE, TRUE, TRUE, FALSE),
        ('command-r', 'cohere', 'command-r', 'Command R', 'Cohere standard', 128000, 4096, 0.0005, 0.0015, FALSE, TRUE, TRUE, FALSE)
    ON CONFLICT (model_id) DO NOTHING;
    """
    
    INSERT_DEFAULT_MODEL_PERMISSIONS = """
    INSERT INTO model_permissions (model_id, role_name, can_use, daily_limit, monthly_limit) VALUES
        ('gpt-4o', 'super_admin', TRUE, -1, -1),
        ('gpt-4o', 'domain_admin', TRUE, -1, -1),
        ('gpt-4o', 'agent_developer', TRUE, 100, 3000),
        ('gpt-4o', 'agent_user', TRUE, 50, 1000),
        ('gpt-4o-mini', 'super_admin', TRUE, -1, -1),
        ('gpt-4o-mini', 'domain_admin', TRUE, -1, -1),
        ('gpt-4o-mini', 'agent_developer', TRUE, -1, -1),
        ('gpt-4o-mini', 'agent_user', TRUE, -1, -1),
        ('gpt-4o-mini', 'viewer', TRUE, 20, 500),
        ('claude-3-5-sonnet-20241022', 'super_admin', TRUE, -1, -1),
        ('claude-3-5-sonnet-20241022', 'domain_admin', TRUE, -1, -1),
        ('claude-3-5-sonnet-20241022', 'agent_developer', TRUE, 100, 3000),
        ('claude-3-5-sonnet-20241022', 'agent_user', TRUE, 50, 1000)
    ON CONFLICT (model_id, role_name) DO NOTHING;
    """
    
    # ==========================================================================
    # TRIGGERS
    # ==========================================================================
    
    CREATE_UPDATE_TIMESTAMP_FUNCTION = """
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """
    
    CREATE_TRIGGERS = [
        CREATE_UPDATE_TIMESTAMP_FUNCTION,
        "DROP TRIGGER IF EXISTS update_users_timestamp ON users; CREATE TRIGGER update_users_timestamp BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();",
        "DROP TRIGGER IF EXISTS update_agents_timestamp ON agents; CREATE TRIGGER update_agents_timestamp BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();",
        "DROP TRIGGER IF EXISTS update_workflows_timestamp ON workflows; CREATE TRIGGER update_workflows_timestamp BEFORE UPDATE ON workflows FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();",
        "DROP TRIGGER IF EXISTS update_mcp_plugins_timestamp ON mcp_plugins; CREATE TRIGGER update_mcp_plugins_timestamp BEFORE UPDATE ON mcp_plugins FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();",
        "DROP TRIGGER IF EXISTS update_mcp_tool_servers_timestamp ON mcp_tool_servers; CREATE TRIGGER update_mcp_tool_servers_timestamp BEFORE UPDATE ON mcp_tool_servers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();",
        "DROP TRIGGER IF EXISTS update_swarms_timestamp ON swarms; CREATE TRIGGER update_swarms_timestamp BEFORE UPDATE ON swarms FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();",
        "DROP TRIGGER IF EXISTS update_notification_channels_timestamp ON notification_channels; CREATE TRIGGER update_notification_channels_timestamp BEFORE UPDATE ON notification_channels FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();",
        "DROP TRIGGER IF EXISTS update_webhook_endpoints_timestamp ON webhook_endpoints; CREATE TRIGGER update_webhook_endpoints_timestamp BEFORE UPDATE ON webhook_endpoints FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();",
    ]
    
    # ==========================================================================
    # METHODS
    # ==========================================================================
    
    def get_all_create_statements(self) -> list:
        """Get all CREATE TABLE statements in order."""
        return [
            self.CREATE_SCHEMA_VERSION,
            self.CREATE_USERS_TABLE,
            self.CREATE_ROLES_TABLE,
            self.CREATE_USER_ROLES_TABLE,
            self.CREATE_AGENTS_TABLE,
            self.CREATE_AGENT_VERSIONS_TABLE,
            self.CREATE_AGENT_TEMPLATES_TABLE,
            self.CREATE_EXECUTIONS_TABLE,
            self.CREATE_EXECUTION_STEPS_TABLE,
            self.CREATE_LLM_CALLS_TABLE,
            self.CREATE_WORKFLOWS_TABLE,
            self.CREATE_WORKFLOW_NODES_TABLE,
            self.CREATE_HITL_TASKS_TABLE,
            self.CREATE_HITL_COMMENTS_TABLE,
            self.CREATE_HITL_ASSIGNMENTS_TABLE,
            self.CREATE_MCP_PLUGINS_TABLE,
            self.CREATE_MCP_TOOL_SERVERS_TABLE,
            self.CREATE_AUDIT_LOGS_TABLE,
            self.CREATE_SESSIONS_TABLE,
            self.CREATE_API_KEYS_TABLE,
            self.CREATE_SETTINGS_TABLE,
            self.CREATE_CODE_FRAGMENTS_TABLE,
            self.CREATE_LLM_PROVIDERS_TABLE,
            self.CREATE_LLM_MODELS_TABLE,
            self.CREATE_MODEL_PERMISSIONS_TABLE,
            self.CREATE_SWARMS_TABLE,
            self.CREATE_SWARM_AGENTS_TABLE,
            self.CREATE_SWARM_TRIGGERS_TABLE,
            self.CREATE_SWARM_EXECUTIONS_TABLE,
            self.CREATE_SWARM_EVENTS_TABLE,
            self.CREATE_SWARM_DECISIONS_TABLE,
            self.CREATE_NOTIFICATION_CHANNELS,
            self.CREATE_NOTIFICATION_LOGS,
            self.CREATE_WEBHOOK_ENDPOINTS,
            self.CREATE_WEBHOOK_EVENTS,
            self.CREATE_USER_NOTIFICATION_PREFS,
        ]
    
    def get_all_index_statements(self) -> list:
        return self.CREATE_INDEXES
    
    def get_all_trigger_statements(self) -> list:
        return self.CREATE_TRIGGERS
    
    def get_default_data_statements(self) -> list:
        return [
            self.INSERT_DEFAULT_ROLES,
            self.INSERT_SCHEMA_VERSION.format(version=self.SCHEMA_VERSION),
            self.INSERT_DEFAULT_PROVIDERS,
            self.INSERT_DEFAULT_MODELS,
            self.INSERT_DEFAULT_MODEL_PERMISSIONS,
        ]
    
    def initialize_database(self, connection) -> bool:
        try:
            cursor = connection.cursor()
            logger.info("Creating PostgreSQL tables...")
            for stmt in self.get_all_create_statements():
                cursor.execute(stmt)
            logger.info("Creating PostgreSQL indexes...")
            for stmt in self.get_all_index_statements():
                cursor.execute(stmt)
            logger.info("Creating PostgreSQL triggers...")
            for stmt in self.get_all_trigger_statements():
                cursor.execute(stmt)
            logger.info("Inserting default data...")
            for stmt in self.get_default_data_statements():
                cursor.execute(stmt)
            connection.commit()
            logger.info(f"PostgreSQL database initialized (schema v{self.SCHEMA_VERSION})")
            return True
        except Exception as e:
            logger.error(f"Error initializing PostgreSQL database: {e}")
            connection.rollback()
            raise
    
    def get_table_list(self) -> list:
        return [
            'schema_version', 'users', 'roles', 'user_roles', 'agents', 'agent_versions',
            'agent_templates', 'executions', 'execution_steps', 'llm_calls', 'workflows',
            'workflow_nodes', 'hitl_tasks', 'hitl_comments', 'hitl_assignments', 'mcp_plugins',
            'mcp_tool_servers', 'audit_logs', 'sessions', 'api_keys', 'system_settings',
            'code_fragments', 'llm_providers', 'llm_models', 'model_permissions', 'swarms',
            'swarm_agents', 'swarm_triggers', 'swarm_executions', 'swarm_events', 'swarm_decisions',
            'notification_channels', 'notification_logs', 'webhook_endpoints', 'webhook_events',
            'user_notification_preferences',
        ]
