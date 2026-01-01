"""
SQLite Schema - Database schema definitions for SQLite backend.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.

Patent Pending: Certain architectural patterns and implementations described in this
software may be subject to patent applications.
"""

import logging

logger = logging.getLogger(__name__)


class SQLiteSchema:
    """
    SQLite database schema definitions.
    
    Provides SQL statements for creating and managing database tables
    optimized for SQLite.
    """
    
    # ==========================================================================
    # SCHEMA VERSION
    # ==========================================================================
    
    SCHEMA_VERSION = "1.4.6"
    
    # ==========================================================================
    # TABLE DEFINITIONS
    # ==========================================================================
    
    # Schema version tracking table
    CREATE_SCHEMA_VERSION = """
    CREATE TABLE IF NOT EXISTS schema_version (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        version TEXT NOT NULL,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        description TEXT
    );
    """
    
    # Users table
    CREATE_USERS_TABLE = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        fullname TEXT NOT NULL,
        email TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        failed_login_attempts INTEGER DEFAULT 0,
        locked_until TIMESTAMP,
        preferences TEXT DEFAULT '{}'
    );
    """
    
    # Roles table
    CREATE_ROLES_TABLE = """
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_name TEXT UNIQUE NOT NULL,
        display_name TEXT NOT NULL,
        description TEXT,
        permissions TEXT DEFAULT '[]',
        is_system INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # User-Roles mapping table
    CREATE_USER_ROLES_TABLE = """
    CREATE TABLE IF NOT EXISTS user_roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        role_name TEXT NOT NULL,
        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        assigned_by TEXT,
        UNIQUE(user_id, role_name),
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (role_name) REFERENCES roles(role_name) ON DELETE CASCADE
    );
    """
    
    # Agents table
    CREATE_AGENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        agent_type TEXT NOT NULL DEFAULT 'react',
        version TEXT DEFAULT '1.0.0',
        status TEXT DEFAULT 'draft',
        config TEXT DEFAULT '{}',
        workflow TEXT DEFAULT '{}',
        llm_config TEXT DEFAULT '{}',
        tools TEXT DEFAULT '[]',
        hitl_config TEXT DEFAULT '{}',
        tags TEXT DEFAULT '[]',
        created_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        published_at TIMESTAMP,
        deprecated_at TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(user_id)
    );
    """
    
    # Agent versions table (for version history)
    CREATE_AGENT_VERSIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS agent_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id TEXT NOT NULL,
        version TEXT NOT NULL,
        config_snapshot TEXT NOT NULL,
        workflow_snapshot TEXT,
        created_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        change_notes TEXT,
        UNIQUE(agent_id, version),
        FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE
    );
    """
    
    # Agent templates table
    CREATE_AGENT_TEMPLATES_TABLE = """
    CREATE TABLE IF NOT EXISTS agent_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT NOT NULL,
        agent_type TEXT NOT NULL,
        icon TEXT DEFAULT 'bi-robot',
        difficulty TEXT DEFAULT 'intermediate',
        workflow TEXT DEFAULT '{}',
        llm_config TEXT DEFAULT '{}',
        tools TEXT DEFAULT '[]',
        hitl_config TEXT DEFAULT '{}',
        sample_prompts TEXT DEFAULT '[]',
        tags TEXT DEFAULT '[]',
        is_system INTEGER DEFAULT 0,
        created_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        use_count INTEGER DEFAULT 0
    );
    """
    
    # Executions table
    CREATE_EXECUTIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS executions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        execution_id TEXT UNIQUE NOT NULL,
        agent_id TEXT NOT NULL,
        agent_version TEXT,
        user_id TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        input_data TEXT,
        output_data TEXT,
        error_message TEXT,
        execution_config TEXT DEFAULT '{}',
        metadata TEXT DEFAULT '{}',
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        duration_ms INTEGER,
        tokens_used INTEGER DEFAULT 0,
        cost_estimate REAL DEFAULT 0.0,
        trace_data TEXT DEFAULT '[]',
        FOREIGN KEY (agent_id) REFERENCES agents(agent_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    """
    
    # Agent executions table (for detailed agent-specific execution logging)
    CREATE_AGENT_EXECUTIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS agent_executions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        execution_id TEXT UNIQUE NOT NULL,
        agent_id TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        input_data TEXT,
        output_data TEXT,
        error_message TEXT,
        duration_ms INTEGER,
        metadata TEXT DEFAULT '{}',
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        created_by TEXT DEFAULT 'system',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
    );
    """
    
    # Execution steps table (for detailed step tracking)
    CREATE_EXECUTION_STEPS_TABLE = """
    CREATE TABLE IF NOT EXISTS execution_steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        execution_id TEXT NOT NULL,
        step_number INTEGER NOT NULL,
        node_id TEXT,
        node_type TEXT,
        status TEXT DEFAULT 'pending',
        input_data TEXT,
        output_data TEXT,
        error_message TEXT,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        duration_ms INTEGER,
        FOREIGN KEY (execution_id) REFERENCES executions(execution_id) ON DELETE CASCADE
    );
    """
    
    # LLM calls table (for tracking all LLM interactions)
    CREATE_LLM_CALLS_TABLE = """
    CREATE TABLE IF NOT EXISTS llm_calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        call_id TEXT UNIQUE NOT NULL,
        execution_id TEXT,
        agent_id TEXT,
        user_id TEXT NOT NULL,
        provider TEXT NOT NULL,
        model TEXT NOT NULL,
        request_type TEXT DEFAULT 'completion',
        system_prompt TEXT,
        user_prompt TEXT,
        messages TEXT,
        response_content TEXT,
        tool_calls TEXT,
        input_tokens INTEGER DEFAULT 0,
        output_tokens INTEGER DEFAULT 0,
        total_tokens INTEGER DEFAULT 0,
        cost_estimate REAL DEFAULT 0.0,
        temperature REAL,
        max_tokens INTEGER,
        latency_ms INTEGER,
        status TEXT DEFAULT 'success',
        error_message TEXT,
        metadata TEXT DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (execution_id) REFERENCES executions(execution_id),
        FOREIGN KEY (agent_id) REFERENCES agents(agent_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    """
    
    # Workflows table (for storing DAG workflows)
    CREATE_WORKFLOWS_TABLE = """
    CREATE TABLE IF NOT EXISTS workflows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workflow_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        version TEXT DEFAULT '1.0.0',
        workflow_type TEXT DEFAULT 'dag',
        dag_definition TEXT NOT NULL,
        python_modules TEXT DEFAULT '{}',
        entry_point TEXT,
        input_schema TEXT DEFAULT '{}',
        output_schema TEXT DEFAULT '{}',
        dependencies TEXT DEFAULT '[]',
        environment TEXT DEFAULT '{}',
        status TEXT DEFAULT 'draft',
        created_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_executed_at TIMESTAMP,
        execution_count INTEGER DEFAULT 0,
        avg_duration_ms INTEGER,
        tags TEXT DEFAULT '[]',
        FOREIGN KEY (created_by) REFERENCES users(user_id)
    );
    """
    
    # Workflow nodes table (for individual nodes in DAG)
    CREATE_WORKFLOW_NODES_TABLE = """
    CREATE TABLE IF NOT EXISTS workflow_nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id TEXT UNIQUE NOT NULL,
        workflow_id TEXT NOT NULL,
        name TEXT NOT NULL,
        node_type TEXT NOT NULL,
        config TEXT DEFAULT '{}',
        python_code TEXT,
        position_x INTEGER DEFAULT 0,
        position_y INTEGER DEFAULT 0,
        dependencies TEXT DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON DELETE CASCADE
    );
    """
    
    # HITL tasks table
    CREATE_HITL_TASKS_TABLE = """
    CREATE TABLE IF NOT EXISTS hitl_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        context TEXT DEFAULT '{}',
        request_data TEXT,
        input_schema TEXT DEFAULT '{}',
        response_data TEXT,
        resolution TEXT,
        assigned_to TEXT,
        assigned_at TIMESTAMP,
        due_at TIMESTAMP,
        completed_at TIMESTAMP,
        completed_by TEXT,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        timeout_minutes INTEGER DEFAULT 1440,
        notification_sent INTEGER DEFAULT 0,
        reminder_count INTEGER DEFAULT 0,
        last_reminder_at TIMESTAMP,
        tags TEXT DEFAULT '[]',
        metadata TEXT DEFAULT '{}',
        FOREIGN KEY (execution_id) REFERENCES executions(execution_id),
        FOREIGN KEY (agent_id) REFERENCES agents(agent_id),
        FOREIGN KEY (assigned_to) REFERENCES users(user_id),
        FOREIGN KEY (completed_by) REFERENCES users(user_id)
    );
    """
    
    # HITL comments table
    CREATE_HITL_COMMENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS hitl_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        comment_id TEXT UNIQUE NOT NULL,
        task_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        comment TEXT NOT NULL,
        comment_type TEXT DEFAULT 'comment',
        attachments TEXT DEFAULT '[]',
        is_internal INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES hitl_tasks(task_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    """
    
    # HITL assignments history table
    CREATE_HITL_ASSIGNMENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS hitl_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id TEXT UNIQUE NOT NULL,
        task_id TEXT NOT NULL,
        assigned_from TEXT,
        assigned_to TEXT NOT NULL,
        assigned_by TEXT NOT NULL,
        reason TEXT,
        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES hitl_tasks(task_id) ON DELETE CASCADE,
        FOREIGN KEY (assigned_to) REFERENCES users(user_id),
        FOREIGN KEY (assigned_by) REFERENCES users(user_id)
    );
    """
    
    # MCP plugins table
    CREATE_MCP_PLUGINS_TABLE = """
    CREATE TABLE IF NOT EXISTS mcp_plugins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plugin_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        version TEXT DEFAULT '1.0.0',
        plugin_type TEXT DEFAULT 'tool',
        status TEXT DEFAULT 'active',
        config TEXT DEFAULT '{}',
        manifest TEXT DEFAULT '{}',
        server_name TEXT,
        server_url TEXT,
        capabilities TEXT DEFAULT '[]',
        created_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_health_check TIMESTAMP,
        health_status TEXT DEFAULT 'unknown',
        FOREIGN KEY (created_by) REFERENCES users(user_id)
    );
    """
    
    # MCP Tool Servers table (external MCP servers with tools)
    CREATE_MCP_TOOL_SERVERS_TABLE = """
    CREATE TABLE IF NOT EXISTS mcp_tool_servers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        base_url TEXT NOT NULL,
        tools_endpoint TEXT DEFAULT '/api/tools/list',
        auth_type TEXT DEFAULT 'none',
        auth_config TEXT DEFAULT '{}',
        auth_endpoint TEXT DEFAULT '',
        is_active INTEGER DEFAULT 1,
        auto_refresh INTEGER DEFAULT 1,
        refresh_interval_minutes INTEGER DEFAULT 60,
        last_refresh TIMESTAMP,
        last_refresh_status TEXT,
        tool_count INTEGER DEFAULT 0,
        cached_tools TEXT DEFAULT '[]',
        timeout_seconds INTEGER DEFAULT 30,
        created_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(user_id)
    );
    """
    
    # Audit logs table
    CREATE_AUDIT_LOGS_TABLE = """
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        log_id TEXT UNIQUE NOT NULL,
        action TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT,
        user_id TEXT,
        user_ip TEXT,
        user_agent TEXT,
        old_value TEXT,
        new_value TEXT,
        metadata TEXT DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    """
    
    # Sessions table
    CREATE_SESSIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        user_id TEXT NOT NULL,
        session_data TEXT DEFAULT '{}',
        ip_address TEXT,
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """
    
    # API keys table
    CREATE_API_KEYS_TABLE = """
    CREATE TABLE IF NOT EXISTS api_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key_id TEXT UNIQUE NOT NULL,
        user_id TEXT NOT NULL,
        key_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        permissions TEXT DEFAULT '[]',
        rate_limit INTEGER DEFAULT 1000,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        last_used_at TIMESTAMP,
        usage_count INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """
    
    # System settings table
    CREATE_SETTINGS_TABLE = """
    CREATE TABLE IF NOT EXISTS system_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_key TEXT UNIQUE NOT NULL,
        setting_value TEXT,
        setting_type TEXT DEFAULT 'string',
        description TEXT,
        is_encrypted INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_by TEXT
    );
    """
    
    # Code fragments table (for reusable code modules)
    CREATE_CODE_FRAGMENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS code_fragments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fragment_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        language TEXT DEFAULT 'python',
        code TEXT NOT NULL,
        version TEXT DEFAULT '1.0.0',
        category TEXT DEFAULT 'general',
        tags TEXT DEFAULT '[]',
        dependencies TEXT DEFAULT '[]',
        is_active INTEGER DEFAULT 1,
        is_system INTEGER DEFAULT 0,
        created_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_by TEXT,
        usage_count INTEGER DEFAULT 0,
        FOREIGN KEY (created_by) REFERENCES users(user_id)
    );
    """
    
    # LLM Providers table
    CREATE_LLM_PROVIDERS_TABLE = """
    CREATE TABLE IF NOT EXISTS llm_providers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        provider_type TEXT NOT NULL,
        api_endpoint TEXT,
        api_key_name TEXT,
        is_active INTEGER DEFAULT 1,
        is_default INTEGER DEFAULT 0,
        config TEXT DEFAULT '{}',
        rate_limit_rpm INTEGER DEFAULT 60,
        rate_limit_tpm INTEGER DEFAULT 100000,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT,
        FOREIGN KEY (created_by) REFERENCES users(user_id)
    );
    """
    
    # LLM Models table
    CREATE_LLM_MODELS_TABLE = """
    CREATE TABLE IF NOT EXISTS llm_models (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_id TEXT UNIQUE NOT NULL,
        provider_id TEXT NOT NULL,
        name TEXT NOT NULL,
        display_name TEXT,
        description TEXT,
        model_type TEXT DEFAULT 'chat',
        context_window INTEGER DEFAULT 4096,
        max_output_tokens INTEGER DEFAULT 4096,
        input_cost_per_1k REAL DEFAULT 0.0,
        output_cost_per_1k REAL DEFAULT 0.0,
        supports_vision INTEGER DEFAULT 0,
        supports_functions INTEGER DEFAULT 0,
        supports_streaming INTEGER DEFAULT 1,
        is_active INTEGER DEFAULT 1,
        is_default INTEGER DEFAULT 0,
        config TEXT DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (provider_id) REFERENCES llm_providers(provider_id)
    );
    """
    
    # Model Permissions table (RBAC for models)
    CREATE_MODEL_PERMISSIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS model_permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_id TEXT NOT NULL,
        role_name TEXT NOT NULL,
        can_use INTEGER DEFAULT 1,
        daily_limit INTEGER DEFAULT -1,
        monthly_limit INTEGER DEFAULT -1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT,
        UNIQUE(model_id, role_name),
        FOREIGN KEY (model_id) REFERENCES llm_models(model_id),
        FOREIGN KEY (role_name) REFERENCES roles(role_name)
    );
    """
    
    # ==========================================================================
    # SWARM TABLES (v1.3.0)
    # ==========================================================================
    
    # Swarms table - Main swarm definitions
    CREATE_SWARMS_TABLE = """
    CREATE TABLE IF NOT EXISTS swarms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        swarm_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        version TEXT DEFAULT '1.0.0',
        status TEXT DEFAULT 'draft',
        category TEXT DEFAULT 'general',
        tags TEXT DEFAULT '[]',
        definition_json TEXT,
        config_json TEXT,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_executions INTEGER DEFAULT 0,
        successful_executions INTEGER DEFAULT 0,
        failed_executions INTEGER DEFAULT 0,
        total_events_processed INTEGER DEFAULT 0,
        FOREIGN KEY (created_by) REFERENCES users(user_id)
    );
    """
    
    # Swarm agents membership table
    CREATE_SWARM_AGENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS swarm_agents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        membership_id TEXT UNIQUE NOT NULL,
        swarm_id TEXT NOT NULL,
        agent_id TEXT NOT NULL,
        agent_name TEXT,
        role TEXT DEFAULT 'worker',
        description TEXT,
        subscriptions_json TEXT DEFAULT '[]',
        max_instances INTEGER DEFAULT 10,
        min_instances INTEGER DEFAULT 0,
        auto_scale INTEGER DEFAULT 1,
        idle_timeout INTEGER DEFAULT 300,
        is_active INTEGER DEFAULT 1,
        current_instances INTEGER DEFAULT 0,
        total_tasks_processed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (swarm_id) REFERENCES swarms(swarm_id) ON DELETE CASCADE,
        FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
    );
    """
    
    # Swarm triggers table
    CREATE_SWARM_TRIGGERS_TABLE = """
    CREATE TABLE IF NOT EXISTS swarm_triggers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trigger_id TEXT UNIQUE NOT NULL,
        swarm_id TEXT NOT NULL,
        trigger_type TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        config_json TEXT DEFAULT '{}',
        filter_expression TEXT,
        is_active INTEGER DEFAULT 1,
        last_triggered TIMESTAMP,
        trigger_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (swarm_id) REFERENCES swarms(swarm_id) ON DELETE CASCADE
    );
    """
    
    # Swarm executions table
    CREATE_SWARM_EXECUTIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS swarm_executions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        execution_id TEXT UNIQUE NOT NULL,
        swarm_id TEXT NOT NULL,
        trigger_type TEXT,
        trigger_data TEXT,
        correlation_id TEXT,
        status TEXT DEFAULT 'pending',
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        duration_ms INTEGER,
        iterations INTEGER DEFAULT 0,
        events_processed INTEGER DEFAULT 0,
        result_json TEXT,
        error_message TEXT,
        user_id TEXT,
        FOREIGN KEY (swarm_id) REFERENCES swarms(swarm_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    """
    
    # Swarm events log table
    CREATE_SWARM_EVENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS swarm_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT UNIQUE NOT NULL,
        swarm_id TEXT NOT NULL,
        execution_id TEXT,
        event_type TEXT NOT NULL,
        source TEXT,
        target TEXT,
        payload_json TEXT,
        headers_json TEXT DEFAULT '{}',
        priority INTEGER DEFAULT 1,
        correlation_id TEXT,
        parent_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (swarm_id) REFERENCES swarms(swarm_id),
        FOREIGN KEY (execution_id) REFERENCES swarm_executions(execution_id)
    );
    """
    
    # Swarm decisions log table (Master Actor decisions)
    CREATE_SWARM_DECISIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS swarm_decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        decision_id TEXT UNIQUE NOT NULL,
        swarm_id TEXT NOT NULL,
        execution_id TEXT,
        decision_type TEXT NOT NULL,
        trigger_event_id TEXT,
        event_type TEXT,
        target_agents TEXT DEFAULT '[]',
        payload_json TEXT,
        reasoning TEXT,
        confidence REAL DEFAULT 1.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (swarm_id) REFERENCES swarms(swarm_id),
        FOREIGN KEY (execution_id) REFERENCES swarm_executions(execution_id)
    );
    """
    
    # ==========================================================================
    # NOTIFICATION TABLES (v1.4.0)
    # ==========================================================================
    
    CREATE_NOTIFICATION_CHANNELS = """
    CREATE TABLE IF NOT EXISTS notification_channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_id TEXT UNIQUE NOT NULL,
        channel_type TEXT NOT NULL,
        name TEXT NOT NULL,
        config TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_NOTIFICATION_LOGS = """
    CREATE TABLE IF NOT EXISTS notification_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        sent_at TIMESTAMP,
        delivered_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_WEBHOOK_ENDPOINTS = """
    CREATE TABLE IF NOT EXISTS webhook_endpoints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        endpoint_id TEXT UNIQUE NOT NULL,
        path TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        auth_method TEXT DEFAULT 'hmac',
        secret_hash TEXT,
        target_type TEXT,
        target_id TEXT,
        rate_limit INTEGER DEFAULT 100,
        is_active INTEGER DEFAULT 1,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_WEBHOOK_EVENTS = """
    CREATE TABLE IF NOT EXISTS webhook_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT UNIQUE NOT NULL,
        endpoint_id TEXT NOT NULL,
        event_type TEXT,
        payload TEXT,
        headers TEXT,
        source_ip TEXT,
        verified INTEGER DEFAULT 0,
        processed INTEGER DEFAULT 0,
        process_result TEXT,
        error_message TEXT,
        received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed_at TIMESTAMP,
        FOREIGN KEY (endpoint_id) REFERENCES webhook_endpoints(endpoint_id)
    );
    """
    
    CREATE_USER_NOTIFICATION_PREFS = """
    CREATE TABLE IF NOT EXISTS user_notification_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        channel_type TEXT NOT NULL,
        channel_address TEXT,
        enabled INTEGER DEFAULT 1,
        min_level TEXT DEFAULT 'info',
        quiet_hours_start TEXT,
        quiet_hours_end TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, channel_type)
    );
    """
    
    # ==========================================================================
    # AI ORGANIZATIONS (v1.4.6)
    # ==========================================================================
    
    CREATE_AI_ORGS_TABLE = """
    CREATE TABLE IF NOT EXISTS ai_orgs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'draft',
        config TEXT DEFAULT '{}',
        event_bus_channel TEXT,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_AI_NODES_TABLE = """
    CREATE TABLE IF NOT EXISTS ai_nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id TEXT UNIQUE NOT NULL,
        org_id TEXT NOT NULL,
        parent_node_id TEXT,
        role_name TEXT NOT NULL,
        role_type TEXT DEFAULT 'analyst',
        description TEXT,
        agent_id TEXT,
        agent_config TEXT DEFAULT '{}',
        human_name TEXT,
        human_email TEXT,
        human_teams_id TEXT,
        human_slack_id TEXT,
        hitl_enabled INTEGER DEFAULT 0,
        hitl_approval_required INTEGER DEFAULT 0,
        hitl_review_delegation INTEGER DEFAULT 0,
        hitl_timeout_hours INTEGER DEFAULT 24,
        hitl_auto_proceed INTEGER DEFAULT 1,
        notification_channels TEXT DEFAULT '["email"]',
        notification_triggers TEXT DEFAULT '[]',
        position_x INTEGER DEFAULT 0,
        position_y INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active',
        current_task_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (org_id) REFERENCES ai_orgs(org_id) ON DELETE CASCADE
    );
    """
    
    CREATE_AI_TASKS_TABLE = """
    CREATE TABLE IF NOT EXISTS ai_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT UNIQUE NOT NULL,
        org_id TEXT NOT NULL,
        parent_task_id TEXT,
        assigned_node_id TEXT,
        title TEXT NOT NULL,
        description TEXT,
        priority TEXT DEFAULT 'medium',
        input_data TEXT DEFAULT '{}',
        output_data TEXT,
        context TEXT DEFAULT '{}',
        attachments TEXT DEFAULT '[]',
        status TEXT DEFAULT 'pending',
        delegation_strategy TEXT DEFAULT 'parallel',
        expected_responses INTEGER DEFAULT 0,
        received_responses INTEGER DEFAULT 0,
        deadline TIMESTAMP,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        error_message TEXT,
        retry_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (org_id) REFERENCES ai_orgs(org_id) ON DELETE CASCADE,
        FOREIGN KEY (assigned_node_id) REFERENCES ai_nodes(node_id) ON DELETE SET NULL
    );
    """
    
    CREATE_AI_RESPONSES_TABLE = """
    CREATE TABLE IF NOT EXISTS ai_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        response_id TEXT UNIQUE NOT NULL,
        task_id TEXT NOT NULL,
        node_id TEXT NOT NULL,
        response_type TEXT DEFAULT 'analysis',
        content TEXT DEFAULT '{}',
        summary TEXT,
        reasoning TEXT,
        confidence_score REAL DEFAULT 0.0,
        quality_score REAL DEFAULT 0.0,
        is_human_modified INTEGER DEFAULT 0,
        original_ai_content TEXT,
        modification_reason TEXT,
        modified_by TEXT,
        modified_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES ai_tasks(task_id) ON DELETE CASCADE,
        FOREIGN KEY (node_id) REFERENCES ai_nodes(node_id) ON DELETE CASCADE
    );
    """
    
    CREATE_AI_HITL_ACTIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS ai_hitl_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_id TEXT UNIQUE NOT NULL,
        org_id TEXT NOT NULL,
        node_id TEXT NOT NULL,
        task_id TEXT,
        response_id TEXT,
        user_id TEXT,
        action_type TEXT NOT NULL,
        original_content TEXT,
        modified_content TEXT,
        reason TEXT,
        message TEXT,
        ip_address TEXT,
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (org_id) REFERENCES ai_orgs(org_id) ON DELETE CASCADE,
        FOREIGN KEY (task_id) REFERENCES ai_tasks(task_id) ON DELETE SET NULL,
        FOREIGN KEY (node_id) REFERENCES ai_nodes(node_id) ON DELETE CASCADE
    );
    """
    
    CREATE_AI_EVENT_LOGS_TABLE = """
    CREATE TABLE IF NOT EXISTS ai_event_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT UNIQUE NOT NULL,
        org_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        source_node_id TEXT,
        target_node_id TEXT,
        task_id TEXT,
        payload TEXT DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (org_id) REFERENCES ai_orgs(org_id) ON DELETE CASCADE
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
        # AI Organizations indexes (v1.4.6)
        "CREATE INDEX IF NOT EXISTS idx_ai_orgs_status ON ai_orgs(status);",
        "CREATE INDEX IF NOT EXISTS idx_ai_orgs_created_by ON ai_orgs(created_by);",
        "CREATE INDEX IF NOT EXISTS idx_ai_nodes_org_id ON ai_nodes(org_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_nodes_parent_node_id ON ai_nodes(parent_node_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_nodes_human_email ON ai_nodes(human_email);",
        "CREATE INDEX IF NOT EXISTS idx_ai_tasks_org_id ON ai_tasks(org_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_tasks_assigned_node_id ON ai_tasks(assigned_node_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_tasks_status ON ai_tasks(status);",
        "CREATE INDEX IF NOT EXISTS idx_ai_tasks_parent_task_id ON ai_tasks(parent_task_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_responses_task_id ON ai_responses(task_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_responses_node_id ON ai_responses(node_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_hitl_actions_org_id ON ai_hitl_actions(org_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_hitl_actions_task_id ON ai_hitl_actions(task_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_hitl_actions_node_id ON ai_hitl_actions(node_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_event_logs_org_id ON ai_event_logs(org_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_event_logs_event_type ON ai_event_logs(event_type);",
        # Agent executions indexes (v1.4.6.1)
        "CREATE INDEX IF NOT EXISTS idx_agent_executions_agent_id ON agent_executions(agent_id);",
        "CREATE INDEX IF NOT EXISTS idx_agent_executions_status ON agent_executions(status);",
        "CREATE INDEX IF NOT EXISTS idx_agent_executions_created_at ON agent_executions(created_at);",
    ]
    
    # ==========================================================================
    # DEFAULT DATA
    # ==========================================================================
    
    INSERT_DEFAULT_ROLES = """
    INSERT OR IGNORE INTO roles (role_name, display_name, description, permissions, is_system) VALUES
        ('super_admin', 'Super Administrator', 'Full system access with all permissions', 
         '["*"]', 1),
        ('domain_admin', 'Domain Administrator', 'Administrative access within a domain', 
         '["users:read", "users:write", "agents:read", "agents:write", "agents:publish", "executions:*", "audit:read"]', 1),
        ('agent_developer', 'Agent Developer', 'Create and manage agents', 
         '["agents:read", "agents:write", "agents:test", "templates:read", "executions:read"]', 1),
        ('agent_publisher', 'Agent Publisher', 'Review and publish agents', 
         '["agents:read", "agents:review", "agents:publish", "executions:read"]', 1),
        ('hitl_reviewer', 'HITL Reviewer', 'Review and respond to human-in-the-loop tasks', 
         '["hitl:read", "hitl:respond", "executions:read"]', 1),
        ('agent_user', 'Agent User', 'Execute published agents', 
         '["agents:read:published", "executions:create", "executions:read:own"]', 1),
        ('viewer', 'Viewer', 'Read-only access to view dashboards and reports', 
         '["agents:read:published", "executions:read:own"]', 1);
    """
    
    INSERT_SCHEMA_VERSION = """
    INSERT INTO schema_version (version, description) 
    VALUES ('{version}', 'Initial schema creation');
    """
    
    # Default LLM Providers
    INSERT_DEFAULT_PROVIDERS = """
    INSERT OR IGNORE INTO llm_providers (provider_id, name, description, provider_type, api_key_name, is_active, is_default, config) VALUES
        ('openai', 'OpenAI', 'OpenAI GPT models including GPT-4 and GPT-3.5', 'openai', 'OPENAI_API_KEY', 1, 0, '{"base_url": "https://api.openai.com/v1"}'),
        ('anthropic', 'Anthropic', 'Claude models from Anthropic', 'anthropic', 'ANTHROPIC_API_KEY', 1, 0, '{"base_url": "https://api.anthropic.com"}'),
        ('google', 'Google AI', 'Google Gemini models', 'google', 'GOOGLE_API_KEY', 1, 0, '{}'),
        ('azure', 'Azure OpenAI', 'Azure-hosted OpenAI models', 'azure', 'AZURE_OPENAI_KEY', 0, 0, '{"api_version": "2024-02-15-preview"}'),
        ('mistral', 'Mistral AI', 'Mistral open-weight models', 'mistral', 'MISTRAL_API_KEY', 1, 0, '{"base_url": "https://api.mistral.ai/v1"}'),
        ('groq', 'Groq', 'Groq high-speed inference', 'groq', 'GROQ_API_KEY', 1, 0, '{"base_url": "https://api.groq.com/openai/v1"}'),
        ('together', 'Together AI', 'Together AI hosted models', 'together', 'TOGETHER_API_KEY', 1, 0, '{"base_url": "https://api.together.xyz/v1"}'),
        ('cohere', 'Cohere', 'Cohere Command models', 'cohere', 'COHERE_API_KEY', 1, 0, '{}'),
        ('bedrock', 'AWS Bedrock', 'Amazon Bedrock managed AI service', 'bedrock', 'AWS_ACCESS_KEY_ID', 0, 0, '{"region": "us-east-1"}'),
        ('ollama', 'Ollama', 'Local Ollama instance - free and private', 'ollama', '', 1, 1, '{"base_url": "http://192.168.2.36:11434"}'),
        ('huggingface', 'Hugging Face', 'Hugging Face Inference API', 'huggingface', 'HF_API_TOKEN', 1, 0, '{"base_url": "https://api-inference.huggingface.co"}');
    """
    
    # Default LLM Models
    INSERT_DEFAULT_MODELS = """
    INSERT OR IGNORE INTO llm_models (model_id, provider_id, name, display_name, description, context_window, max_output_tokens, input_cost_per_1k, output_cost_per_1k, supports_vision, supports_functions, is_active, is_default) VALUES
        -- Ollama Models (Default Provider - FREE)
        ('llama3.2:3b', 'ollama', 'llama3.2:3b', 'Llama 3.2 3B', 'Lightweight 3B model - RECOMMENDED DEFAULT', 131072, 4096, 0, 0, 0, 1, 1, 1),
        ('llama3.2', 'ollama', 'llama3.2', 'Llama 3.2 3B', 'Lightweight, fast, edge deployment', 131072, 4096, 0, 0, 0, 1, 1, 0),
        ('llama3.2:1b', 'ollama', 'llama3.2:1b', 'Llama 3.2 1B', 'Ultra-lightweight, mobile', 131072, 4096, 0, 0, 0, 1, 1, 0),
        ('llama3.2-vision', 'ollama', 'llama3.2-vision', 'Llama 3.2 Vision 11B', 'Multimodal with image understanding', 131072, 4096, 0, 0, 1, 1, 1, 0),
        ('llama3.3', 'ollama', 'llama3.3', 'Llama 3.3 70B', 'Best open model, matches 405B quality (42GB)', 131072, 4096, 0, 0, 0, 1, 1, 0),
        ('llama3.1', 'ollama', 'llama3.1', 'Llama 3.1 8B', 'General purpose, production ready', 131072, 4096, 0, 0, 0, 1, 1, 0),
        ('llama3.1:70b', 'ollama', 'llama3.1:70b', 'Llama 3.1 70B', 'High quality general purpose', 131072, 4096, 0, 0, 0, 1, 1, 0),
        ('deepseek-r1', 'ollama', 'deepseek-r1', 'DeepSeek R1 7B', 'Reasoning model, rivals o1', 65536, 8192, 0, 0, 0, 1, 1, 0),
        ('deepseek-r1:8b', 'ollama', 'deepseek-r1:8b', 'DeepSeek R1 8B', 'Reasoning with chain-of-thought', 65536, 8192, 0, 0, 0, 1, 1, 0),
        ('deepseek-r1:14b', 'ollama', 'deepseek-r1:14b', 'DeepSeek R1 14B', 'Enhanced reasoning model', 65536, 8192, 0, 0, 0, 1, 1, 0),
        ('deepseek-r1:32b', 'ollama', 'deepseek-r1:32b', 'DeepSeek R1 32B', 'Large reasoning model', 65536, 8192, 0, 0, 0, 1, 1, 0),
        ('deepseek-r1:70b', 'ollama', 'deepseek-r1:70b', 'DeepSeek R1 70B', 'Largest reasoning model', 65536, 8192, 0, 0, 0, 1, 1, 0),
        ('deepseek-coder-v2', 'ollama', 'deepseek-coder-v2', 'DeepSeek Coder V2', 'Code generation and analysis', 65536, 4096, 0, 0, 0, 1, 1, 0),
        ('qwen2.5', 'ollama', 'qwen2.5', 'Qwen 2.5 7B', 'Multilingual, Chinese support', 131072, 4096, 0, 0, 0, 1, 1, 0),
        ('qwen2.5:14b', 'ollama', 'qwen2.5:14b', 'Qwen 2.5 14B', 'Larger multilingual model', 131072, 4096, 0, 0, 0, 1, 1, 0),
        ('qwen2.5:32b', 'ollama', 'qwen2.5:32b', 'Qwen 2.5 32B', 'High quality multilingual', 131072, 4096, 0, 0, 0, 1, 1, 0),
        ('qwen2.5:72b', 'ollama', 'qwen2.5:72b', 'Qwen 2.5 72B', 'Flagship multilingual', 131072, 4096, 0, 0, 0, 1, 1, 0),
        ('qwen2.5-coder', 'ollama', 'qwen2.5-coder', 'Qwen 2.5 Coder 7B', 'Best open-source coding model', 131072, 4096, 0, 0, 0, 1, 1, 0),
        ('qwen2.5-coder:14b', 'ollama', 'qwen2.5-coder:14b', 'Qwen 2.5 Coder 14B', 'Enhanced coding model', 131072, 4096, 0, 0, 0, 1, 1, 0),
        ('qwen2.5-coder:32b', 'ollama', 'qwen2.5-coder:32b', 'Qwen 2.5 Coder 32B', 'Large coding model', 131072, 4096, 0, 0, 0, 1, 1, 0),
        ('qwq', 'ollama', 'qwq', 'QwQ 32B', 'Reasoning and problem solving', 131072, 4096, 0, 0, 0, 1, 1, 0),
        ('mistral', 'ollama', 'mistral', 'Mistral 7B', 'Balanced performance and speed', 32768, 4096, 0, 0, 0, 1, 1, 0),
        ('mistral-nemo', 'ollama', 'mistral-nemo', 'Mistral Nemo 12B', 'Improved Mistral with longer context', 131072, 4096, 0, 0, 0, 1, 1, 0),
        ('mixtral', 'ollama', 'mixtral', 'Mixtral 8x7B', 'MoE architecture, complex tasks', 32768, 4096, 0, 0, 0, 1, 1, 0),
        ('mixtral:8x22b', 'ollama', 'mixtral:8x22b', 'Mixtral 8x22B', 'Large MoE model', 65536, 4096, 0, 0, 0, 1, 1, 0),
        ('codellama', 'ollama', 'codellama', 'Code Llama 7B', 'Code generation and completion', 16384, 4096, 0, 0, 0, 1, 1, 0),
        ('codellama:13b', 'ollama', 'codellama:13b', 'Code Llama 13B', 'Enhanced code model', 16384, 4096, 0, 0, 0, 1, 1, 0),
        ('codellama:34b', 'ollama', 'codellama:34b', 'Code Llama 34B', 'Large code model', 16384, 4096, 0, 0, 0, 1, 1, 0),
        ('codellama:70b', 'ollama', 'codellama:70b', 'Code Llama 70B', 'Largest code model', 16384, 4096, 0, 0, 0, 1, 1, 0),
        ('gemma2', 'ollama', 'gemma2', 'Gemma 2 9B', 'Google open model', 8192, 4096, 0, 0, 0, 1, 1, 0),
        ('gemma2:27b', 'ollama', 'gemma2:27b', 'Gemma 2 27B', 'Large Google model', 8192, 4096, 0, 0, 0, 1, 1, 0),
        ('phi4', 'ollama', 'phi4', 'Phi 4 14B', 'Microsoft latest small model', 16384, 4096, 0, 0, 0, 1, 1, 0),
        ('phi3', 'ollama', 'phi3', 'Phi 3 3B', 'Small but capable', 4096, 4096, 0, 0, 0, 1, 1, 0),
        ('phi3:14b', 'ollama', 'phi3:14b', 'Phi 3 14B', 'Larger Phi model', 4096, 4096, 0, 0, 0, 1, 1, 0),
        ('command-r', 'ollama', 'command-r', 'Command R 35B', 'RAG and retrieval tasks', 131072, 4096, 0, 0, 0, 1, 1, 0),
        ('yi', 'ollama', 'yi', 'Yi 6B', 'Bilingual EN/CN', 4096, 4096, 0, 0, 0, 1, 1, 0),
        ('yi:34b', 'ollama', 'yi:34b', 'Yi 34B', 'Large bilingual model', 4096, 4096, 0, 0, 0, 1, 1, 0),
        ('nomic-embed-text', 'ollama', 'nomic-embed-text', 'Nomic Embed Text', 'Text embeddings 768d', 8192, 768, 0, 0, 0, 0, 1, 0),
        ('mxbai-embed-large', 'ollama', 'mxbai-embed-large', 'MxBai Embed Large', 'High quality embeddings 1024d', 512, 1024, 0, 0, 0, 0, 1, 0),
        ('snowflake-arctic-embed', 'ollama', 'snowflake-arctic-embed', 'Snowflake Arctic Embed', 'Retrieval optimized embeddings', 512, 1024, 0, 0, 0, 0, 1, 0),
        ('all-minilm', 'ollama', 'all-minilm', 'All MiniLM', 'Lightweight embeddings 384d', 512, 384, 0, 0, 0, 0, 1, 0),
        -- OpenAI Models
        ('gpt-4o', 'openai', 'gpt-4o', 'GPT-4o', 'Most capable OpenAI model with vision', 128000, 4096, 0.005, 0.015, 1, 1, 1, 0),
        ('gpt-4o-mini', 'openai', 'gpt-4o-mini', 'GPT-4o Mini', 'Fast and affordable GPT-4o variant', 128000, 16384, 0.00015, 0.0006, 1, 1, 1, 0),
        ('gpt-4-turbo', 'openai', 'gpt-4-turbo', 'GPT-4 Turbo', 'GPT-4 Turbo with vision', 128000, 4096, 0.01, 0.03, 1, 1, 1, 0),
        ('gpt-3.5-turbo', 'openai', 'gpt-3.5-turbo', 'GPT-3.5 Turbo', 'Fast and cost-effective', 16385, 4096, 0.0005, 0.0015, 0, 1, 1, 0),
        -- Anthropic Claude 4.5 Models (Latest)
        ('claude-opus-4-5-20251101', 'anthropic', 'claude-opus-4-5-20251101', 'Claude 4.5 Opus', 'Most intelligent Claude model', 200000, 8192, 0.015, 0.075, 1, 1, 1, 0),
        ('claude-sonnet-4-5-20250929', 'anthropic', 'claude-sonnet-4-5-20250929', 'Claude 4.5 Sonnet', 'Best balance of capability and speed', 200000, 8192, 0.003, 0.015, 1, 1, 1, 0),
        -- Anthropic Claude 4 Models
        ('claude-opus-4-20250514', 'anthropic', 'claude-opus-4-20250514', 'Claude 4 Opus', 'Powerful Claude 4 model', 200000, 8192, 0.015, 0.075, 1, 1, 1, 0),
        ('claude-sonnet-4-20250514', 'anthropic', 'claude-sonnet-4-20250514', 'Claude 4 Sonnet', 'Balanced Claude 4 model', 200000, 8192, 0.003, 0.015, 1, 1, 1, 0),
        -- Anthropic Claude 3.5 Models
        ('claude-3-5-sonnet-20241022', 'anthropic', 'claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet', 'Previous generation best overall', 200000, 8192, 0.003, 0.015, 1, 1, 1, 0),
        ('claude-3-5-haiku-20241022', 'anthropic', 'claude-3-5-haiku-20241022', 'Claude 3.5 Haiku', 'Fast and cost-effective', 200000, 8192, 0.0008, 0.004, 1, 1, 1, 0),
        -- Anthropic Claude 3 Models (Legacy)
        ('claude-3-opus-20240229', 'anthropic', 'claude-3-opus-20240229', 'Claude 3 Opus', 'Legacy powerful Claude model', 200000, 4096, 0.015, 0.075, 1, 1, 1, 0),
        ('claude-3-haiku-20240307', 'anthropic', 'claude-3-haiku-20240307', 'Claude 3 Haiku', 'Legacy fast and compact Claude', 200000, 4096, 0.00025, 0.00125, 1, 1, 1, 0),
        -- Google Models
        ('gemini-1.5-pro', 'google', 'gemini-1.5-pro', 'Gemini 1.5 Pro', 'Google advanced multimodal model', 1000000, 8192, 0.00125, 0.005, 1, 1, 1, 0),
        ('gemini-1.5-flash', 'google', 'gemini-1.5-flash', 'Gemini 1.5 Flash', 'Fast Google model', 1000000, 8192, 0.000075, 0.0003, 1, 1, 1, 0),
        ('gemini-2.0-flash', 'google', 'gemini-2.0-flash', 'Gemini 2.0 Flash', 'Latest fast Google model', 1000000, 8192, 0.0001, 0.0004, 1, 1, 1, 0),
        -- Mistral Models
        ('mistral-large-latest', 'mistral', 'mistral-large-latest', 'Mistral Large', 'Flagship Mistral model', 128000, 4096, 0.004, 0.012, 0, 1, 1, 0),
        ('mistral-small-latest', 'mistral', 'mistral-small-latest', 'Mistral Small', 'Cost-effective Mistral', 32000, 4096, 0.001, 0.003, 0, 1, 1, 0),
        -- Groq Models
        ('mixtral-8x7b-32768', 'groq', 'mixtral-8x7b-32768', 'Mixtral 8x7B (Groq)', 'Fast Mixtral on Groq', 32768, 4096, 0.00027, 0.00027, 0, 1, 1, 0),
        ('llama-3.1-70b-versatile', 'groq', 'llama-3.1-70b-versatile', 'Llama 3.1 70B (Groq)', 'Llama 3.1 on Groq', 131072, 4096, 0.00059, 0.00079, 0, 1, 1, 0),
        ('llama-3.3-70b-versatile', 'groq', 'llama-3.3-70b-versatile', 'Llama 3.3 70B (Groq)', 'Latest Llama on Groq', 131072, 4096, 0.00059, 0.00079, 0, 1, 1, 0),
        -- Cohere Models
        ('command-r-plus', 'cohere', 'command-r-plus', 'Command R+', 'Cohere flagship model', 128000, 4096, 0.003, 0.015, 0, 1, 1, 0),
        ('command-r', 'cohere', 'command-r', 'Command R', 'Cohere standard model', 128000, 4096, 0.0005, 0.0015, 0, 1, 1, 0),
        -- AWS Bedrock Models (Anthropic)
        ('anthropic.claude-opus-4-5-20251101-v1:0', 'bedrock', 'anthropic.claude-opus-4-5-20251101-v1:0', 'Claude 4.5 Opus (Bedrock)', 'Most intelligent Claude on Bedrock', 200000, 8192, 0.015, 0.075, 1, 1, 1, 0),
        ('anthropic.claude-sonnet-4-5-20250929-v1:0', 'bedrock', 'anthropic.claude-sonnet-4-5-20250929-v1:0', 'Claude 4.5 Sonnet (Bedrock)', 'Best Claude on Bedrock', 200000, 8192, 0.003, 0.015, 1, 1, 1, 0),
        ('anthropic.claude-opus-4-20250514-v1:0', 'bedrock', 'anthropic.claude-opus-4-20250514-v1:0', 'Claude 4 Opus (Bedrock)', 'Claude 4 Opus on Bedrock', 200000, 8192, 0.015, 0.075, 1, 1, 1, 0),
        ('anthropic.claude-sonnet-4-20250514-v1:0', 'bedrock', 'anthropic.claude-sonnet-4-20250514-v1:0', 'Claude 4 Sonnet (Bedrock)', 'Claude 4 Sonnet on Bedrock', 200000, 8192, 0.003, 0.015, 1, 1, 1, 0),
        ('anthropic.claude-3-5-sonnet-20241022-v2:0', 'bedrock', 'anthropic.claude-3-5-sonnet-20241022-v2:0', 'Claude 3.5 Sonnet v2 (Bedrock)', 'Claude 3.5 Sonnet on Bedrock', 200000, 8192, 0.003, 0.015, 1, 1, 1, 0),
        ('anthropic.claude-3-5-haiku-20241022-v1:0', 'bedrock', 'anthropic.claude-3-5-haiku-20241022-v1:0', 'Claude 3.5 Haiku (Bedrock)', 'Fast Claude on Bedrock', 200000, 8192, 0.0008, 0.004, 1, 1, 1, 0),
        -- AWS Bedrock Models (Meta Llama)
        ('meta.llama3-3-70b-instruct-v1:0', 'bedrock', 'meta.llama3-3-70b-instruct-v1:0', 'Llama 3.3 70B (Bedrock)', 'Latest Llama on Bedrock', 131072, 4096, 0.00099, 0.00099, 0, 1, 1, 0),
        ('meta.llama3-2-90b-instruct-v1:0', 'bedrock', 'meta.llama3-2-90b-instruct-v1:0', 'Llama 3.2 90B (Bedrock)', 'Multimodal Llama on Bedrock', 131072, 4096, 0.002, 0.002, 1, 1, 1, 0),
        ('meta.llama3-2-11b-instruct-v1:0', 'bedrock', 'meta.llama3-2-11b-instruct-v1:0', 'Llama 3.2 11B (Bedrock)', 'Lightweight multimodal Llama', 131072, 4096, 0.00035, 0.00035, 1, 1, 1, 0),
        ('meta.llama3-2-3b-instruct-v1:0', 'bedrock', 'meta.llama3-2-3b-instruct-v1:0', 'Llama 3.2 3B (Bedrock)', 'Fast lightweight Llama', 131072, 4096, 0.00015, 0.00015, 0, 1, 1, 0),
        ('meta.llama3-1-405b-instruct-v1:0', 'bedrock', 'meta.llama3-1-405b-instruct-v1:0', 'Llama 3.1 405B (Bedrock)', 'Largest open model', 131072, 4096, 0.00532, 0.016, 0, 1, 1, 0),
        ('meta.llama3-1-70b-instruct-v1:0', 'bedrock', 'meta.llama3-1-70b-instruct-v1:0', 'Llama 3.1 70B (Bedrock)', 'Strong general purpose', 131072, 4096, 0.00099, 0.00099, 0, 1, 1, 0),
        ('meta.llama3-1-8b-instruct-v1:0', 'bedrock', 'meta.llama3-1-8b-instruct-v1:0', 'Llama 3.1 8B (Bedrock)', 'Fast efficient Llama', 131072, 4096, 0.0003, 0.0006, 0, 1, 1, 0),
        -- AWS Bedrock Models (Mistral)
        ('mistral.mistral-large-2411-v1:0', 'bedrock', 'mistral.mistral-large-2411-v1:0', 'Mistral Large Nov 2024 (Bedrock)', 'Latest Mistral on Bedrock', 128000, 4096, 0.004, 0.012, 0, 1, 1, 0),
        ('mistral.mistral-large-2407-v1:0', 'bedrock', 'mistral.mistral-large-2407-v1:0', 'Mistral Large Jul 2024 (Bedrock)', 'Mistral Large on Bedrock', 128000, 4096, 0.004, 0.012, 0, 1, 1, 0),
        -- AWS Bedrock Models (Amazon)
        ('amazon.titan-text-premier-v2:0', 'bedrock', 'amazon.titan-text-premier-v2:0', 'Titan Text Premier v2', 'AWS native premier model', 32000, 4096, 0.0008, 0.0024, 0, 1, 1, 0),
        ('amazon.nova-pro-v1:0', 'bedrock', 'amazon.nova-pro-v1:0', 'Amazon Nova Pro', 'Multimodal Amazon model', 300000, 5000, 0.0008, 0.0032, 1, 1, 1, 0),
        ('amazon.nova-lite-v1:0', 'bedrock', 'amazon.nova-lite-v1:0', 'Amazon Nova Lite', 'Lightweight multimodal', 300000, 5000, 0.00006, 0.00024, 1, 1, 1, 0);
    """
    
    # Default Model Permissions (all roles can use all models by default)
    INSERT_DEFAULT_MODEL_PERMISSIONS = """
    INSERT OR IGNORE INTO model_permissions (model_id, role_name, can_use, daily_limit, monthly_limit) VALUES
        -- Ollama models (no limits - free local models)
        ('llama3.2:3b', 'super_admin', 1, -1, -1),
        ('llama3.2:3b', 'domain_admin', 1, -1, -1),
        ('llama3.2:3b', 'agent_developer', 1, -1, -1),
        ('llama3.2:3b', 'agent_user', 1, -1, -1),
        ('llama3.2:3b', 'viewer', 1, -1, -1),
        ('llama3.2', 'super_admin', 1, -1, -1),
        ('llama3.2', 'domain_admin', 1, -1, -1),
        ('llama3.2', 'agent_developer', 1, -1, -1),
        ('llama3.2', 'agent_user', 1, -1, -1),
        ('llama3.2', 'viewer', 1, -1, -1),
        ('llama3.3', 'super_admin', 1, -1, -1),
        ('llama3.3', 'domain_admin', 1, -1, -1),
        ('llama3.3', 'agent_developer', 1, -1, -1),
        ('llama3.3', 'agent_user', 1, -1, -1),
        ('llama3.3', 'viewer', 1, -1, -1),
        ('deepseek-r1', 'super_admin', 1, -1, -1),
        ('deepseek-r1', 'domain_admin', 1, -1, -1),
        ('deepseek-r1', 'agent_developer', 1, -1, -1),
        ('deepseek-r1', 'agent_user', 1, -1, -1),
        ('qwen2.5-coder', 'super_admin', 1, -1, -1),
        ('qwen2.5-coder', 'domain_admin', 1, -1, -1),
        ('qwen2.5-coder', 'agent_developer', 1, -1, -1),
        ('qwen2.5-coder', 'agent_user', 1, -1, -1),
        ('mistral', 'super_admin', 1, -1, -1),
        ('mistral', 'domain_admin', 1, -1, -1),
        ('mistral', 'agent_developer', 1, -1, -1),
        ('mistral', 'agent_user', 1, -1, -1),
        ('mistral', 'viewer', 1, -1, -1),
        -- OpenAI models (with limits for paid API)
        ('gpt-4o', 'super_admin', 1, -1, -1),
        ('gpt-4o', 'domain_admin', 1, -1, -1),
        ('gpt-4o', 'agent_developer', 1, 100, 3000),
        ('gpt-4o', 'agent_user', 1, 50, 1000),
        ('gpt-4o-mini', 'super_admin', 1, -1, -1),
        ('gpt-4o-mini', 'domain_admin', 1, -1, -1),
        ('gpt-4o-mini', 'agent_developer', 1, -1, -1),
        ('gpt-4o-mini', 'agent_user', 1, -1, -1),
        ('gpt-4o-mini', 'viewer', 1, 20, 500),
        -- Anthropic models (with limits for paid API)
        ('claude-opus-4-5-20251101', 'super_admin', 1, -1, -1),
        ('claude-opus-4-5-20251101', 'domain_admin', 1, -1, -1),
        ('claude-opus-4-5-20251101', 'agent_developer', 1, 50, 1500),
        ('claude-sonnet-4-5-20250929', 'super_admin', 1, -1, -1),
        ('claude-sonnet-4-5-20250929', 'domain_admin', 1, -1, -1),
        ('claude-sonnet-4-5-20250929', 'agent_developer', 1, 100, 3000),
        ('claude-sonnet-4-5-20250929', 'agent_user', 1, 50, 1000),
        ('claude-3-5-sonnet-20241022', 'super_admin', 1, -1, -1),
        ('claude-3-5-sonnet-20241022', 'domain_admin', 1, -1, -1),
        ('claude-3-5-sonnet-20241022', 'agent_developer', 1, 100, 3000),
        ('claude-3-5-sonnet-20241022', 'agent_user', 1, 50, 1000);
    """
    
    # ==========================================================================
    # TRIGGERS
    # ==========================================================================
    
    CREATE_TRIGGERS = [
        # Update timestamp trigger for users
        """
        CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
        AFTER UPDATE ON users
        BEGIN
            UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        """,
        # Update timestamp trigger for agents
        """
        CREATE TRIGGER IF NOT EXISTS update_agents_timestamp 
        AFTER UPDATE ON agents
        BEGIN
            UPDATE agents SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        """,
        # Update timestamp trigger for mcp_plugins
        """
        CREATE TRIGGER IF NOT EXISTS update_mcp_plugins_timestamp 
        AFTER UPDATE ON mcp_plugins
        BEGIN
            UPDATE mcp_plugins SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        """,
        # Update timestamp trigger for mcp_tool_servers
        """
        CREATE TRIGGER IF NOT EXISTS update_mcp_tool_servers_timestamp 
        AFTER UPDATE ON mcp_tool_servers
        BEGIN
            UPDATE mcp_tool_servers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        """,
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
            self.CREATE_AGENT_EXECUTIONS_TABLE,
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
            # Swarm tables (v1.3.0)
            self.CREATE_SWARMS_TABLE,
            self.CREATE_SWARM_AGENTS_TABLE,
            self.CREATE_SWARM_TRIGGERS_TABLE,
            self.CREATE_SWARM_EXECUTIONS_TABLE,
            self.CREATE_SWARM_EVENTS_TABLE,
            self.CREATE_SWARM_DECISIONS_TABLE,
            # Notification tables (v1.4.0)
            self.CREATE_NOTIFICATION_CHANNELS,
            self.CREATE_NOTIFICATION_LOGS,
            self.CREATE_WEBHOOK_ENDPOINTS,
            self.CREATE_WEBHOOK_EVENTS,
            self.CREATE_USER_NOTIFICATION_PREFS,
            # AI Organizations tables (v1.4.6)
            self.CREATE_AI_ORGS_TABLE,
            self.CREATE_AI_NODES_TABLE,
            self.CREATE_AI_TASKS_TABLE,
            self.CREATE_AI_RESPONSES_TABLE,
            self.CREATE_AI_HITL_ACTIONS_TABLE,
            self.CREATE_AI_EVENT_LOGS_TABLE,
        ]
    
    def get_all_index_statements(self) -> list:
        """Get all CREATE INDEX statements."""
        return self.CREATE_INDEXES
    
    def get_all_trigger_statements(self) -> list:
        """Get all CREATE TRIGGER statements."""
        return self.CREATE_TRIGGERS
    
    def get_default_data_statements(self) -> list:
        """Get all INSERT statements for default data."""
        return [
            self.INSERT_DEFAULT_ROLES,
            self.INSERT_SCHEMA_VERSION.format(version=self.SCHEMA_VERSION),
            self.INSERT_DEFAULT_PROVIDERS,
            self.INSERT_DEFAULT_MODELS,
            self.INSERT_DEFAULT_MODEL_PERMISSIONS,
        ]
    
    def initialize_database(self, connection) -> bool:
        """
        Initialize the database with all tables, indexes, and default data.
        
        Args:
            connection: SQLite database connection
            
        Returns:
            True if successful
        """
        try:
            cursor = connection.cursor()
            
            # Create tables
            logger.info("Creating SQLite tables...")
            for stmt in self.get_all_create_statements():
                cursor.execute(stmt)
            
            # Create indexes
            logger.info("Creating SQLite indexes...")
            for stmt in self.get_all_index_statements():
                cursor.execute(stmt)
            
            # Create triggers
            logger.info("Creating SQLite triggers...")
            for stmt in self.get_all_trigger_statements():
                cursor.execute(stmt)
            
            # Insert default data
            logger.info("Inserting default data...")
            for stmt in self.get_default_data_statements():
                cursor.execute(stmt)
            
            connection.commit()
            logger.info(f"SQLite database initialized successfully (schema v{self.SCHEMA_VERSION})")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {e}")
            connection.rollback()
            raise
    
    def get_table_list(self) -> list:
        """Get list of all table names."""
        return [
            'schema_version',
            'users',
            'roles',
            'user_roles',
            'agents',
            'agent_versions',
            'agent_templates',
            'executions',
            'agent_executions',
            'execution_steps',
            'llm_calls',
            'workflows',
            'workflow_nodes',
            'hitl_tasks',
            'mcp_plugins',
            'audit_logs',
            'sessions',
            'api_keys',
            'system_settings',
            'code_fragments',
            'llm_providers',
            'llm_models',
            'model_permissions',
            # Swarm tables (v1.3.0)
            'swarms',
            'swarm_agents',
            'swarm_triggers',
            'swarm_executions',
            'swarm_events',
            'swarm_decisions',
            # AI Organizations tables (v1.4.6)
            'ai_orgs',
            'ai_nodes',
            'ai_tasks',
            'ai_responses',
            'ai_hitl_actions',
            'ai_event_logs',
        ]
