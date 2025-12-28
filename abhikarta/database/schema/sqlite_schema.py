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
    
    SCHEMA_VERSION = "1.2.2"
    
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
        ('openai', 'OpenAI', 'OpenAI GPT models including GPT-4 and GPT-3.5', 'openai', 'OPENAI_API_KEY', 1, 1, '{"base_url": "https://api.openai.com/v1"}'),
        ('anthropic', 'Anthropic', 'Claude models from Anthropic', 'anthropic', 'ANTHROPIC_API_KEY', 1, 0, '{"base_url": "https://api.anthropic.com"}'),
        ('google', 'Google AI', 'Google Gemini models', 'google', 'GOOGLE_API_KEY', 1, 0, '{}'),
        ('azure', 'Azure OpenAI', 'Azure-hosted OpenAI models', 'azure', 'AZURE_OPENAI_KEY', 0, 0, '{"api_version": "2024-02-15-preview"}'),
        ('mistral', 'Mistral AI', 'Mistral open-weight models', 'mistral', 'MISTRAL_API_KEY', 1, 0, '{"base_url": "https://api.mistral.ai/v1"}'),
        ('groq', 'Groq', 'Groq high-speed inference', 'groq', 'GROQ_API_KEY', 1, 0, '{"base_url": "https://api.groq.com/openai/v1"}'),
        ('together', 'Together AI', 'Together AI hosted models', 'together', 'TOGETHER_API_KEY', 1, 0, '{"base_url": "https://api.together.xyz/v1"}'),
        ('cohere', 'Cohere', 'Cohere Command models', 'cohere', 'COHERE_API_KEY', 1, 0, '{}'),
        ('bedrock', 'AWS Bedrock', 'Amazon Bedrock managed AI service', 'bedrock', 'AWS_ACCESS_KEY_ID', 0, 0, '{"region": "us-east-1"}'),
        ('ollama', 'Ollama', 'Local Ollama instance', 'ollama', '', 1, 0, '{"base_url": "http://localhost:11434"}'),
        ('huggingface', 'Hugging Face', 'Hugging Face Inference API', 'huggingface', 'HF_API_TOKEN', 1, 0, '{"base_url": "https://api-inference.huggingface.co"}');
    """
    
    # Default LLM Models
    INSERT_DEFAULT_MODELS = """
    INSERT OR IGNORE INTO llm_models (model_id, provider_id, name, display_name, description, context_window, max_output_tokens, input_cost_per_1k, output_cost_per_1k, supports_vision, supports_functions, is_active, is_default) VALUES
        ('gpt-4o', 'openai', 'gpt-4o', 'GPT-4o', 'Most capable OpenAI model with vision', 128000, 4096, 0.005, 0.015, 1, 1, 1, 1),
        ('gpt-4o-mini', 'openai', 'gpt-4o-mini', 'GPT-4o Mini', 'Fast and affordable GPT-4o variant', 128000, 16384, 0.00015, 0.0006, 1, 1, 1, 0),
        ('gpt-4-turbo', 'openai', 'gpt-4-turbo', 'GPT-4 Turbo', 'GPT-4 Turbo with vision', 128000, 4096, 0.01, 0.03, 1, 1, 1, 0),
        ('gpt-3.5-turbo', 'openai', 'gpt-3.5-turbo', 'GPT-3.5 Turbo', 'Fast and cost-effective', 16385, 4096, 0.0005, 0.0015, 0, 1, 1, 0),
        ('claude-3-5-sonnet-20241022', 'anthropic', 'claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet', 'Latest Claude 3.5 Sonnet', 200000, 8192, 0.003, 0.015, 1, 1, 1, 0),
        ('claude-3-opus-20240229', 'anthropic', 'claude-3-opus-20240229', 'Claude 3 Opus', 'Most powerful Claude model', 200000, 4096, 0.015, 0.075, 1, 1, 1, 0),
        ('claude-3-haiku-20240307', 'anthropic', 'claude-3-haiku-20240307', 'Claude 3 Haiku', 'Fast and compact Claude', 200000, 4096, 0.00025, 0.00125, 1, 1, 1, 0),
        ('gemini-1.5-pro', 'google', 'gemini-1.5-pro', 'Gemini 1.5 Pro', 'Google advanced multimodal model', 1000000, 8192, 0.00125, 0.005, 1, 1, 1, 0),
        ('gemini-1.5-flash', 'google', 'gemini-1.5-flash', 'Gemini 1.5 Flash', 'Fast Google model', 1000000, 8192, 0.000075, 0.0003, 1, 1, 1, 0),
        ('mistral-large-latest', 'mistral', 'mistral-large-latest', 'Mistral Large', 'Flagship Mistral model', 128000, 4096, 0.004, 0.012, 0, 1, 1, 0),
        ('mistral-small-latest', 'mistral', 'mistral-small-latest', 'Mistral Small', 'Cost-effective Mistral', 32000, 4096, 0.001, 0.003, 0, 1, 1, 0),
        ('mixtral-8x7b-32768', 'groq', 'mixtral-8x7b-32768', 'Mixtral 8x7B (Groq)', 'Fast Mixtral on Groq', 32768, 4096, 0.00027, 0.00027, 0, 1, 1, 0),
        ('llama-3.1-70b-versatile', 'groq', 'llama-3.1-70b-versatile', 'Llama 3.1 70B (Groq)', 'Llama 3.1 on Groq', 131072, 4096, 0.00059, 0.00079, 0, 1, 1, 0),
        ('command-r-plus', 'cohere', 'command-r-plus', 'Command R+', 'Cohere flagship model', 128000, 4096, 0.003, 0.015, 0, 1, 1, 0),
        ('command-r', 'cohere', 'command-r', 'Command R', 'Cohere standard model', 128000, 4096, 0.0005, 0.0015, 0, 1, 1, 0);
    """
    
    # Default Model Permissions (all roles can use all models by default)
    INSERT_DEFAULT_MODEL_PERMISSIONS = """
    INSERT OR IGNORE INTO model_permissions (model_id, role_name, can_use, daily_limit, monthly_limit) VALUES
        ('gpt-4o', 'super_admin', 1, -1, -1),
        ('gpt-4o', 'domain_admin', 1, -1, -1),
        ('gpt-4o', 'agent_developer', 1, 100, 3000),
        ('gpt-4o', 'agent_user', 1, 50, 1000),
        ('gpt-4o-mini', 'super_admin', 1, -1, -1),
        ('gpt-4o-mini', 'domain_admin', 1, -1, -1),
        ('gpt-4o-mini', 'agent_developer', 1, -1, -1),
        ('gpt-4o-mini', 'agent_user', 1, -1, -1),
        ('gpt-4o-mini', 'viewer', 1, 20, 500),
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
        ]
