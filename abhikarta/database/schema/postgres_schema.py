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
"""

import logging

logger = logging.getLogger(__name__)


class PostgresSchema:
    """
    PostgreSQL database schema definitions.
    
    Provides SQL statements for creating and managing database tables
    optimized for PostgreSQL with native features like JSONB, UUID, and
    advanced indexing.
    """
    
    # ==========================================================================
    # SCHEMA VERSION
    # ==========================================================================
    
    SCHEMA_VERSION = "1.1.7"
    
    # ==========================================================================
    # EXTENSIONS
    # ==========================================================================
    
    CREATE_EXTENSIONS = """
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    """
    
    # ==========================================================================
    # CUSTOM TYPES
    # ==========================================================================
    
    CREATE_CUSTOM_TYPES = """
    DO $$ BEGIN
        CREATE TYPE agent_status AS ENUM (
            'draft', 'testing', 'pending_review', 'approved', 
            'published', 'deprecated', 'archived'
        );
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    
    DO $$ BEGIN
        CREATE TYPE execution_status AS ENUM (
            'pending', 'running', 'paused', 'completed', 
            'failed', 'cancelled', 'timeout'
        );
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    
    DO $$ BEGIN
        CREATE TYPE hitl_status AS ENUM (
            'pending', 'assigned', 'in_progress', 
            'completed', 'rejected', 'timeout', 'cancelled'
        );
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    
    DO $$ BEGIN
        CREATE TYPE difficulty_level AS ENUM (
            'beginner', 'intermediate', 'advanced'
        );
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """
    
    # ==========================================================================
    # TABLE DEFINITIONS
    # ==========================================================================
    
    # Schema version tracking table
    CREATE_SCHEMA_VERSION = """
    CREATE TABLE IF NOT EXISTS schema_version (
        id SERIAL PRIMARY KEY,
        version VARCHAR(20) NOT NULL,
        applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        description TEXT
    );
    """
    
    # Users table
    CREATE_USERS_TABLE = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        fullname VARCHAR(200) NOT NULL,
        email VARCHAR(255),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP WITH TIME ZONE,
        failed_login_attempts INTEGER DEFAULT 0,
        locked_until TIMESTAMP WITH TIME ZONE,
        preferences JSONB DEFAULT '{}'::jsonb,
        metadata JSONB DEFAULT '{}'::jsonb
    );
    """
    
    # Roles table
    CREATE_ROLES_TABLE = """
    CREATE TABLE IF NOT EXISTS roles (
        id SERIAL PRIMARY KEY,
        role_name VARCHAR(50) UNIQUE NOT NULL,
        display_name VARCHAR(100) NOT NULL,
        description TEXT,
        permissions JSONB DEFAULT '[]'::jsonb,
        is_system BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # User-Roles mapping table
    CREATE_USER_ROLES_TABLE = """
    CREATE TABLE IF NOT EXISTS user_roles (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(100) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
        role_name VARCHAR(50) NOT NULL REFERENCES roles(role_name) ON DELETE CASCADE,
        assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        assigned_by VARCHAR(100),
        UNIQUE(user_id, role_name)
    );
    """
    
    # Agents table
    CREATE_AGENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS agents (
        id SERIAL PRIMARY KEY,
        agent_id VARCHAR(100) UNIQUE NOT NULL,
        name VARCHAR(200) NOT NULL,
        description TEXT,
        agent_type VARCHAR(50) NOT NULL DEFAULT 'react',
        version VARCHAR(20) DEFAULT '1.0.0',
        status agent_status DEFAULT 'draft',
        config JSONB DEFAULT '{}'::jsonb,
        workflow JSONB DEFAULT '{}'::jsonb,
        llm_config JSONB DEFAULT '{}'::jsonb,
        tools JSONB DEFAULT '[]'::jsonb,
        hitl_config JSONB DEFAULT '{}'::jsonb,
        tags JSONB DEFAULT '[]'::jsonb,
        created_by VARCHAR(100) NOT NULL REFERENCES users(user_id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        published_at TIMESTAMP WITH TIME ZONE,
        deprecated_at TIMESTAMP WITH TIME ZONE,
        search_vector tsvector
    );
    """
    
    # Agent versions table (for version history)
    CREATE_AGENT_VERSIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS agent_versions (
        id SERIAL PRIMARY KEY,
        agent_id VARCHAR(100) NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
        version VARCHAR(20) NOT NULL,
        config_snapshot JSONB NOT NULL,
        workflow_snapshot JSONB,
        created_by VARCHAR(100) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        change_notes TEXT,
        UNIQUE(agent_id, version)
    );
    """
    
    # Agent templates table
    CREATE_AGENT_TEMPLATES_TABLE = """
    CREATE TABLE IF NOT EXISTS agent_templates (
        id SERIAL PRIMARY KEY,
        template_id VARCHAR(100) UNIQUE NOT NULL,
        name VARCHAR(200) NOT NULL,
        description TEXT,
        category VARCHAR(100) NOT NULL,
        agent_type VARCHAR(50) NOT NULL,
        icon VARCHAR(50) DEFAULT 'bi-robot',
        difficulty difficulty_level DEFAULT 'intermediate',
        workflow JSONB DEFAULT '{}'::jsonb,
        llm_config JSONB DEFAULT '{}'::jsonb,
        tools JSONB DEFAULT '[]'::jsonb,
        hitl_config JSONB DEFAULT '{}'::jsonb,
        sample_prompts JSONB DEFAULT '[]'::jsonb,
        tags JSONB DEFAULT '[]'::jsonb,
        is_system BOOLEAN DEFAULT FALSE,
        created_by VARCHAR(100) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        use_count INTEGER DEFAULT 0
    );
    """
    
    # Executions table
    CREATE_EXECUTIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS executions (
        id SERIAL PRIMARY KEY,
        execution_id VARCHAR(100) UNIQUE NOT NULL,
        agent_id VARCHAR(100) NOT NULL REFERENCES agents(agent_id),
        agent_version VARCHAR(20),
        user_id VARCHAR(100) NOT NULL REFERENCES users(user_id),
        status execution_status DEFAULT 'pending',
        input_data JSONB,
        output_data JSONB,
        error_message TEXT,
        execution_config JSONB DEFAULT '{}'::jsonb,
        started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP WITH TIME ZONE,
        duration_ms INTEGER,
        tokens_used INTEGER DEFAULT 0,
        cost_estimate DECIMAL(10, 6) DEFAULT 0.0,
        trace_data JSONB DEFAULT '[]'::jsonb,
        metadata JSONB DEFAULT '{}'::jsonb
    );
    """
    
    # Execution steps table (for detailed step tracking)
    CREATE_EXECUTION_STEPS_TABLE = """
    CREATE TABLE IF NOT EXISTS execution_steps (
        id SERIAL PRIMARY KEY,
        execution_id VARCHAR(100) NOT NULL REFERENCES executions(execution_id) ON DELETE CASCADE,
        step_number INTEGER NOT NULL,
        node_id VARCHAR(100),
        node_type VARCHAR(50),
        status execution_status DEFAULT 'pending',
        input_data JSONB,
        output_data JSONB,
        error_message TEXT,
        started_at TIMESTAMP WITH TIME ZONE,
        completed_at TIMESTAMP WITH TIME ZONE,
        duration_ms INTEGER,
        metadata JSONB DEFAULT '{}'::jsonb
    );
    """
    
    # LLM calls table (for tracking all LLM interactions)
    CREATE_LLM_CALLS_TABLE = """
    CREATE TABLE IF NOT EXISTS llm_calls (
        id SERIAL PRIMARY KEY,
        call_id VARCHAR(100) UNIQUE NOT NULL,
        execution_id VARCHAR(100) REFERENCES executions(execution_id),
        agent_id VARCHAR(100) REFERENCES agents(agent_id),
        user_id VARCHAR(100) NOT NULL REFERENCES users(user_id),
        provider VARCHAR(50) NOT NULL,
        model VARCHAR(100) NOT NULL,
        request_type VARCHAR(50) DEFAULT 'completion',
        system_prompt TEXT,
        user_prompt TEXT,
        messages JSONB,
        response_content TEXT,
        tool_calls JSONB,
        input_tokens INTEGER DEFAULT 0,
        output_tokens INTEGER DEFAULT 0,
        total_tokens INTEGER DEFAULT 0,
        cost_estimate DECIMAL(10, 6) DEFAULT 0.0,
        temperature DECIMAL(3, 2),
        max_tokens INTEGER,
        latency_ms INTEGER,
        status VARCHAR(20) DEFAULT 'success',
        error_message TEXT,
        metadata JSONB DEFAULT '{}'::jsonb,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Workflows table (for storing DAG workflows)
    CREATE_WORKFLOWS_TABLE = """
    CREATE TABLE IF NOT EXISTS workflows (
        id SERIAL PRIMARY KEY,
        workflow_id VARCHAR(100) UNIQUE NOT NULL,
        name VARCHAR(200) NOT NULL,
        description TEXT,
        version VARCHAR(20) DEFAULT '1.0.0',
        workflow_type VARCHAR(50) DEFAULT 'dag',
        dag_definition JSONB NOT NULL,
        python_modules JSONB DEFAULT '{}'::jsonb,
        entry_point VARCHAR(100),
        input_schema JSONB DEFAULT '{}'::jsonb,
        output_schema JSONB DEFAULT '{}'::jsonb,
        dependencies JSONB DEFAULT '[]'::jsonb,
        environment JSONB DEFAULT '{}'::jsonb,
        status agent_status DEFAULT 'draft',
        created_by VARCHAR(100) NOT NULL REFERENCES users(user_id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        last_executed_at TIMESTAMP WITH TIME ZONE,
        execution_count INTEGER DEFAULT 0,
        avg_duration_ms INTEGER,
        tags JSONB DEFAULT '[]'::jsonb
    );
    """
    
    # Workflow nodes table (for individual nodes in DAG)
    CREATE_WORKFLOW_NODES_TABLE = """
    CREATE TABLE IF NOT EXISTS workflow_nodes (
        id SERIAL PRIMARY KEY,
        node_id VARCHAR(100) UNIQUE NOT NULL,
        workflow_id VARCHAR(100) NOT NULL REFERENCES workflows(workflow_id) ON DELETE CASCADE,
        name VARCHAR(200) NOT NULL,
        node_type VARCHAR(50) NOT NULL,
        config JSONB DEFAULT '{}'::jsonb,
        python_code TEXT,
        position_x INTEGER DEFAULT 0,
        position_y INTEGER DEFAULT 0,
        dependencies JSONB DEFAULT '[]'::jsonb,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # HITL tasks table
    CREATE_HITL_TASKS_TABLE = """
    CREATE TABLE IF NOT EXISTS hitl_tasks (
        id SERIAL PRIMARY KEY,
        task_id VARCHAR(100) UNIQUE NOT NULL,
        execution_id VARCHAR(100) REFERENCES executions(execution_id),
        workflow_id VARCHAR(100),
        agent_id VARCHAR(100) REFERENCES agents(agent_id),
        node_id VARCHAR(100),
        task_type VARCHAR(50) NOT NULL DEFAULT 'approval',
        title VARCHAR(500) NOT NULL,
        description TEXT,
        status hitl_status DEFAULT 'pending',
        priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
        context JSONB DEFAULT '{}'::jsonb,
        request_data JSONB,
        input_schema JSONB DEFAULT '{}'::jsonb,
        response_data JSONB,
        resolution VARCHAR(50),
        assigned_to VARCHAR(100) REFERENCES users(user_id),
        assigned_at TIMESTAMP WITH TIME ZONE,
        due_at TIMESTAMP WITH TIME ZONE,
        completed_at TIMESTAMP WITH TIME ZONE,
        completed_by VARCHAR(100) REFERENCES users(user_id),
        created_by VARCHAR(100),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        timeout_minutes INTEGER DEFAULT 1440,
        notification_sent BOOLEAN DEFAULT FALSE,
        reminder_count INTEGER DEFAULT 0,
        last_reminder_at TIMESTAMP WITH TIME ZONE,
        tags JSONB DEFAULT '[]'::jsonb,
        metadata JSONB DEFAULT '{}'::jsonb
    );
    """
    
    # HITL comments table
    CREATE_HITL_COMMENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS hitl_comments (
        id SERIAL PRIMARY KEY,
        comment_id VARCHAR(100) UNIQUE NOT NULL,
        task_id VARCHAR(100) NOT NULL REFERENCES hitl_tasks(task_id) ON DELETE CASCADE,
        user_id VARCHAR(100) NOT NULL REFERENCES users(user_id),
        comment TEXT NOT NULL,
        comment_type VARCHAR(50) DEFAULT 'comment',
        attachments JSONB DEFAULT '[]'::jsonb,
        is_internal BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # HITL assignments history table
    CREATE_HITL_ASSIGNMENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS hitl_assignments (
        id SERIAL PRIMARY KEY,
        assignment_id VARCHAR(100) UNIQUE NOT NULL,
        task_id VARCHAR(100) NOT NULL REFERENCES hitl_tasks(task_id) ON DELETE CASCADE,
        assigned_from VARCHAR(100),
        assigned_to VARCHAR(100) NOT NULL REFERENCES users(user_id),
        assigned_by VARCHAR(100) NOT NULL REFERENCES users(user_id),
        reason TEXT,
        assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # MCP plugins table
    CREATE_MCP_PLUGINS_TABLE = """
    CREATE TABLE IF NOT EXISTS mcp_plugins (
        id SERIAL PRIMARY KEY,
        plugin_id VARCHAR(100) UNIQUE NOT NULL,
        name VARCHAR(200) NOT NULL,
        description TEXT,
        version VARCHAR(20) DEFAULT '1.0.0',
        plugin_type VARCHAR(50) DEFAULT 'tool',
        status VARCHAR(20) DEFAULT 'active',
        config JSONB DEFAULT '{}'::jsonb,
        manifest JSONB DEFAULT '{}'::jsonb,
        server_name VARCHAR(200),
        server_url VARCHAR(500),
        capabilities JSONB DEFAULT '[]'::jsonb,
        created_by VARCHAR(100) NOT NULL REFERENCES users(user_id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        last_health_check TIMESTAMP WITH TIME ZONE,
        health_status VARCHAR(20) DEFAULT 'unknown'
    );
    """
    
    # MCP Tool Servers table (external MCP servers with tools)
    CREATE_MCP_TOOL_SERVERS_TABLE = """
    CREATE TABLE IF NOT EXISTS mcp_tool_servers (
        id SERIAL PRIMARY KEY,
        server_id VARCHAR(100) UNIQUE NOT NULL,
        name VARCHAR(200) NOT NULL,
        description TEXT,
        base_url VARCHAR(500) NOT NULL,
        tools_endpoint VARCHAR(200) DEFAULT '/api/tools/list',
        auth_type VARCHAR(50) DEFAULT 'none',
        auth_config JSONB DEFAULT '{}'::jsonb,
        is_active BOOLEAN DEFAULT TRUE,
        auto_refresh BOOLEAN DEFAULT TRUE,
        refresh_interval_minutes INTEGER DEFAULT 60,
        last_refresh TIMESTAMP WITH TIME ZONE,
        last_refresh_status TEXT,
        tool_count INTEGER DEFAULT 0,
        cached_tools JSONB DEFAULT '[]'::jsonb,
        timeout_seconds INTEGER DEFAULT 30,
        created_by VARCHAR(100) NOT NULL REFERENCES users(user_id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Audit logs table
    CREATE_AUDIT_LOGS_TABLE = """
    CREATE TABLE IF NOT EXISTS audit_logs (
        id SERIAL PRIMARY KEY,
        log_id VARCHAR(100) UNIQUE NOT NULL,
        action VARCHAR(100) NOT NULL,
        entity_type VARCHAR(50) NOT NULL,
        entity_id VARCHAR(100),
        user_id VARCHAR(100) REFERENCES users(user_id),
        user_ip INET,
        user_agent TEXT,
        old_value JSONB,
        new_value JSONB,
        metadata JSONB DEFAULT '{}'::jsonb,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Sessions table
    CREATE_SESSIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS sessions (
        id SERIAL PRIMARY KEY,
        session_id VARCHAR(255) UNIQUE NOT NULL,
        user_id VARCHAR(100) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
        session_data JSONB DEFAULT '{}'::jsonb,
        ip_address INET,
        user_agent TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE
    );
    """
    
    # API keys table
    CREATE_API_KEYS_TABLE = """
    CREATE TABLE IF NOT EXISTS api_keys (
        id SERIAL PRIMARY KEY,
        key_id VARCHAR(100) UNIQUE NOT NULL,
        user_id VARCHAR(100) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
        key_hash VARCHAR(255) NOT NULL,
        name VARCHAR(200) NOT NULL,
        description TEXT,
        permissions JSONB DEFAULT '[]'::jsonb,
        rate_limit INTEGER DEFAULT 1000,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP WITH TIME ZONE,
        last_used_at TIMESTAMP WITH TIME ZONE,
        usage_count BIGINT DEFAULT 0
    );
    """
    
    # System settings table
    CREATE_SETTINGS_TABLE = """
    CREATE TABLE IF NOT EXISTS system_settings (
        id SERIAL PRIMARY KEY,
        setting_key VARCHAR(200) UNIQUE NOT NULL,
        setting_value TEXT,
        setting_type VARCHAR(20) DEFAULT 'string',
        description TEXT,
        is_encrypted BOOLEAN DEFAULT FALSE,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_by VARCHAR(100)
    );
    """
    
    # Metrics table (for Prometheus-style metrics storage)
    CREATE_METRICS_TABLE = """
    CREATE TABLE IF NOT EXISTS metrics (
        id SERIAL PRIMARY KEY,
        metric_name VARCHAR(200) NOT NULL,
        metric_type VARCHAR(20) NOT NULL,
        metric_value DOUBLE PRECISION NOT NULL,
        labels JSONB DEFAULT '{}'::jsonb,
        recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # ==========================================================================
    # INDEXES
    # ==========================================================================
    
    CREATE_INDEXES = [
        # Users indexes
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
        "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);",
        "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);",
        
        # User roles indexes
        "CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_user_roles_role_name ON user_roles(role_name);",
        
        # Agents indexes
        "CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);",
        "CREATE INDEX IF NOT EXISTS idx_agents_agent_type ON agents(agent_type);",
        "CREATE INDEX IF NOT EXISTS idx_agents_created_by ON agents(created_by);",
        "CREATE INDEX IF NOT EXISTS idx_agents_created_at ON agents(created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_agents_updated_at ON agents(updated_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_agents_tags ON agents USING GIN(tags);",
        "CREATE INDEX IF NOT EXISTS idx_agents_search ON agents USING GIN(search_vector);",
        
        # Executions indexes
        "CREATE INDEX IF NOT EXISTS idx_executions_agent_id ON executions(agent_id);",
        "CREATE INDEX IF NOT EXISTS idx_executions_user_id ON executions(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status);",
        "CREATE INDEX IF NOT EXISTS idx_executions_started_at ON executions(started_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_executions_agent_user ON executions(agent_id, user_id);",
        
        # Execution steps indexes
        "CREATE INDEX IF NOT EXISTS idx_execution_steps_execution_id ON execution_steps(execution_id);",
        "CREATE INDEX IF NOT EXISTS idx_execution_steps_status ON execution_steps(status);",
        
        # LLM calls indexes
        "CREATE INDEX IF NOT EXISTS idx_llm_calls_execution_id ON llm_calls(execution_id);",
        "CREATE INDEX IF NOT EXISTS idx_llm_calls_agent_id ON llm_calls(agent_id);",
        "CREATE INDEX IF NOT EXISTS idx_llm_calls_user_id ON llm_calls(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_llm_calls_provider ON llm_calls(provider);",
        "CREATE INDEX IF NOT EXISTS idx_llm_calls_model ON llm_calls(model);",
        "CREATE INDEX IF NOT EXISTS idx_llm_calls_created_at ON llm_calls(created_at DESC);",
        
        # Workflows indexes
        "CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);",
        "CREATE INDEX IF NOT EXISTS idx_workflows_created_by ON workflows(created_by);",
        "CREATE INDEX IF NOT EXISTS idx_workflows_created_at ON workflows(created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_workflows_tags ON workflows USING GIN(tags);",
        
        # Workflow nodes indexes
        "CREATE INDEX IF NOT EXISTS idx_workflow_nodes_workflow_id ON workflow_nodes(workflow_id);",
        "CREATE INDEX IF NOT EXISTS idx_workflow_nodes_node_type ON workflow_nodes(node_type);",
        
        # HITL tasks indexes
        "CREATE INDEX IF NOT EXISTS idx_hitl_tasks_status ON hitl_tasks(status);",
        "CREATE INDEX IF NOT EXISTS idx_hitl_tasks_assigned_to ON hitl_tasks(assigned_to);",
        "CREATE INDEX IF NOT EXISTS idx_hitl_tasks_execution_id ON hitl_tasks(execution_id);",
        "CREATE INDEX IF NOT EXISTS idx_hitl_tasks_priority ON hitl_tasks(priority DESC);",
        "CREATE INDEX IF NOT EXISTS idx_hitl_tasks_due_at ON hitl_tasks(due_at);",
        
        # Audit logs indexes
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_entity ON audit_logs(entity_type, entity_id);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);",
        
        # Sessions indexes
        "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);",
        "CREATE INDEX IF NOT EXISTS idx_sessions_is_active ON sessions(is_active);",
        
        # API keys indexes
        "CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_api_keys_is_active ON api_keys(is_active);",
        
        # MCP plugins indexes
        "CREATE INDEX IF NOT EXISTS idx_mcp_plugins_status ON mcp_plugins(status);",
        "CREATE INDEX IF NOT EXISTS idx_mcp_plugins_plugin_type ON mcp_plugins(plugin_type);",
        
        # Metrics indexes
        "CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name);",
        "CREATE INDEX IF NOT EXISTS idx_metrics_recorded_at ON metrics(recorded_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_metrics_labels ON metrics USING GIN(labels);",
    ]
    
    # ==========================================================================
    # DEFAULT DATA
    # ==========================================================================
    
    INSERT_DEFAULT_ROLES = """
    INSERT INTO roles (role_name, display_name, description, permissions, is_system) VALUES
        ('super_admin', 'Super Administrator', 'Full system access with all permissions', 
         '["*"]'::jsonb, TRUE),
        ('domain_admin', 'Domain Administrator', 'Administrative access within a domain', 
         '["users:read", "users:write", "agents:read", "agents:write", "agents:publish", "executions:*", "audit:read"]'::jsonb, TRUE),
        ('agent_developer', 'Agent Developer', 'Create and manage agents', 
         '["agents:read", "agents:write", "agents:test", "templates:read", "executions:read"]'::jsonb, TRUE),
        ('agent_publisher', 'Agent Publisher', 'Review and publish agents', 
         '["agents:read", "agents:review", "agents:publish", "executions:read"]'::jsonb, TRUE),
        ('hitl_reviewer', 'HITL Reviewer', 'Review and respond to human-in-the-loop tasks', 
         '["hitl:read", "hitl:respond", "executions:read"]'::jsonb, TRUE),
        ('agent_user', 'Agent User', 'Execute published agents', 
         '["agents:read:published", "executions:create", "executions:read:own"]'::jsonb, TRUE),
        ('viewer', 'Viewer', 'Read-only access to view dashboards and reports', 
         '["agents:read:published", "executions:read:own"]'::jsonb, TRUE)
    ON CONFLICT (role_name) DO NOTHING;
    """
    
    INSERT_SCHEMA_VERSION = """
    INSERT INTO schema_version (version, description) 
    VALUES ('{version}', 'Initial schema creation');
    """
    
    # ==========================================================================
    # FUNCTIONS
    # ==========================================================================
    
    CREATE_FUNCTIONS = [
        # Function to update updated_at timestamp
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """,
        
        # Function to update search vector for agents
        """
        CREATE OR REPLACE FUNCTION update_agent_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector = to_tsvector('english', 
                COALESCE(NEW.name, '') || ' ' || 
                COALESCE(NEW.description, '') || ' ' ||
                COALESCE(NEW.agent_type, '')
            );
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """,
        
        # Function to clean expired sessions
        """
        CREATE OR REPLACE FUNCTION clean_expired_sessions()
        RETURNS INTEGER AS $$
        DECLARE
            deleted_count INTEGER;
        BEGIN
            DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP;
            GET DIAGNOSTICS deleted_count = ROW_COUNT;
            RETURN deleted_count;
        END;
        $$ language 'plpgsql';
        """,
    ]
    
    # ==========================================================================
    # TRIGGERS
    # ==========================================================================
    
    CREATE_TRIGGERS = [
        # Update timestamp trigger for users
        """
        DROP TRIGGER IF EXISTS update_users_timestamp ON users;
        CREATE TRIGGER update_users_timestamp
            BEFORE UPDATE ON users
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """,
        
        # Update timestamp trigger for agents
        """
        DROP TRIGGER IF EXISTS update_agents_timestamp ON agents;
        CREATE TRIGGER update_agents_timestamp
            BEFORE UPDATE ON agents
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """,
        
        # Update search vector trigger for agents
        """
        DROP TRIGGER IF EXISTS update_agents_search ON agents;
        CREATE TRIGGER update_agents_search
            BEFORE INSERT OR UPDATE ON agents
            FOR EACH ROW
            EXECUTE FUNCTION update_agent_search_vector();
        """,
        
        # Update timestamp trigger for mcp_plugins
        """
        DROP TRIGGER IF EXISTS update_mcp_plugins_timestamp ON mcp_plugins;
        CREATE TRIGGER update_mcp_plugins_timestamp
            BEFORE UPDATE ON mcp_plugins
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """,
    ]
    
    # ==========================================================================
    # PARTITIONING (for high-volume tables)
    # ==========================================================================
    
    # Note: These are templates for partitioning if needed
    PARTITION_AUDIT_LOGS_TEMPLATE = """
    -- To enable partitioning, recreate the audit_logs table:
    -- CREATE TABLE audit_logs (
    --     ...columns...
    -- ) PARTITION BY RANGE (created_at);
    -- 
    -- CREATE TABLE audit_logs_2025_q1 PARTITION OF audit_logs
    --     FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
    """
    
    PARTITION_METRICS_TEMPLATE = """
    -- To enable partitioning for metrics:
    -- CREATE TABLE metrics (
    --     ...columns...
    -- ) PARTITION BY RANGE (recorded_at);
    """
    
    # ==========================================================================
    # METHODS
    # ==========================================================================
    
    def get_all_create_statements(self) -> list:
        """Get all CREATE TABLE statements in order."""
        return [
            self.CREATE_EXTENSIONS,
            self.CREATE_CUSTOM_TYPES,
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
            self.CREATE_METRICS_TABLE,
        ]
    
    def get_all_index_statements(self) -> list:
        """Get all CREATE INDEX statements."""
        return self.CREATE_INDEXES
    
    def get_all_function_statements(self) -> list:
        """Get all CREATE FUNCTION statements."""
        return self.CREATE_FUNCTIONS
    
    def get_all_trigger_statements(self) -> list:
        """Get all CREATE TRIGGER statements."""
        return self.CREATE_TRIGGERS
    
    def get_default_data_statements(self) -> list:
        """Get all INSERT statements for default data."""
        return [
            self.INSERT_DEFAULT_ROLES,
            self.INSERT_SCHEMA_VERSION.format(version=self.SCHEMA_VERSION),
        ]
    
    def initialize_database(self, connection) -> bool:
        """
        Initialize the database with all tables, indexes, functions, 
        triggers, and default data.
        
        Args:
            connection: PostgreSQL database connection
            
        Returns:
            True if successful
        """
        try:
            cursor = connection.cursor()
            
            # Create extensions and types
            logger.info("Creating PostgreSQL extensions and custom types...")
            cursor.execute(self.CREATE_EXTENSIONS)
            cursor.execute(self.CREATE_CUSTOM_TYPES)
            
            # Create tables
            logger.info("Creating PostgreSQL tables...")
            for stmt in self.get_all_create_statements()[2:]:  # Skip extensions and types
                cursor.execute(stmt)
            
            # Create functions
            logger.info("Creating PostgreSQL functions...")
            for stmt in self.get_all_function_statements():
                cursor.execute(stmt)
            
            # Create triggers
            logger.info("Creating PostgreSQL triggers...")
            for stmt in self.get_all_trigger_statements():
                cursor.execute(stmt)
            
            # Create indexes
            logger.info("Creating PostgreSQL indexes...")
            for stmt in self.get_all_index_statements():
                cursor.execute(stmt)
            
            # Insert default data
            logger.info("Inserting default data...")
            for stmt in self.get_default_data_statements():
                cursor.execute(stmt)
            
            connection.commit()
            logger.info(f"PostgreSQL database initialized successfully (schema v{self.SCHEMA_VERSION})")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing PostgreSQL database: {e}")
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
            'metrics',
        ]
    
    def get_full_text_search_query(self, search_term: str) -> str:
        """
        Generate a full-text search query for agents.
        
        Args:
            search_term: Search term
            
        Returns:
            SQL query string
        """
        return f"""
        SELECT * FROM agents 
        WHERE search_vector @@ plainto_tsquery('english', %s)
        ORDER BY ts_rank(search_vector, plainto_tsquery('english', %s)) DESC;
        """
