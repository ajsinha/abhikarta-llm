-- ============================================================================
-- Abhikarta LLM Platform - Execution System Database Schema
-- Copyright © 2025-2030, All Rights Reserved
-- Ashutosh Sinha (ajsinha@gmail.com)
-- ============================================================================

PRAGMA foreign_keys = ON;

-- Core execution sessions
CREATE TABLE IF NOT EXISTS execution_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    execution_mode TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    configuration TEXT,
    context_window_size INTEGER DEFAULT 10,
    llm_provider TEXT,
    llm_model TEXT,
    llm_config TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_tokens_used INTEGER DEFAULT 0,
    total_cost REAL DEFAULT 0.0,
    execution_duration_ms INTEGER,
    error_message TEXT,
    error_type TEXT,
    parent_session_id TEXT,
    tags TEXT,
    metadata TEXT
);

CREATE INDEX idx_sessions_user ON execution_sessions(user_id);
CREATE INDEX idx_sessions_status ON execution_sessions(status);
CREATE INDEX idx_sessions_mode ON execution_sessions(execution_mode);

-- Interactions within sessions
CREATE TABLE IF NOT EXISTS interactions (
    interaction_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    interaction_type TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    role TEXT NOT NULL,
    content TEXT,
    tool_calls TEXT,
    tool_results TEXT,
    model TEXT,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    FOREIGN KEY (session_id) REFERENCES execution_sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_interactions_session ON interactions(session_id);
CREATE INDEX idx_interactions_sequence ON interactions(session_id, sequence_number);

-- Execution state snapshots
CREATE TABLE IF NOT EXISTS execution_state (
    state_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    state_type TEXT NOT NULL,
    state_data TEXT NOT NULL,
    state_version INTEGER DEFAULT 1,
    langgraph_state TEXT,
    node_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    FOREIGN KEY (session_id) REFERENCES execution_sessions(session_id) ON DELETE CASCADE
);

-- DAG definitions and executions
CREATE TABLE IF NOT EXISTS dag_definitions (
    dag_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    graph_definition TEXT NOT NULL,
    entry_point TEXT NOT NULL,
    configuration TEXT,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dag_executions (
    execution_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    dag_id TEXT NOT NULL,
    current_node TEXT,
    execution_path TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    node_results TEXT,
    final_output TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES execution_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (dag_id) REFERENCES dag_definitions(dag_id)
);

-- Planning and ReAct
CREATE TABLE IF NOT EXISTS execution_plans (
    plan_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    goal TEXT NOT NULL,
    plan_type TEXT NOT NULL,
    plan_structure TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    current_step INTEGER DEFAULT 0,
    total_steps INTEGER,
    step_results TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES execution_sessions(session_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS react_cycles (
    cycle_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    cycle_number INTEGER NOT NULL,
    thought TEXT,
    action TEXT,
    action_input TEXT,
    observation TEXT,
    is_final BOOLEAN DEFAULT 0,
    final_answer TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES execution_sessions(session_id) ON DELETE CASCADE
);

-- Tool executions
CREATE TABLE IF NOT EXISTS tool_executions (
    execution_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    interaction_id TEXT,
    tool_name TEXT NOT NULL,
    tool_type TEXT,
    input_parameters TEXT,
    output_result TEXT,
    status TEXT NOT NULL,
    error_message TEXT,
    execution_time_ms INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES execution_sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_tool_exec_session ON tool_executions(session_id);
CREATE INDEX idx_tool_exec_name ON tool_executions(tool_name);

-- Agent definitions and interactions
CREATE TABLE IF NOT EXISTS agent_definitions (
    agent_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    agent_type TEXT NOT NULL,
    capabilities TEXT,
    llm_provider TEXT,
    llm_model TEXT,
    llm_config TEXT,
    available_tools TEXT,
    system_prompt TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_interactions (
    interaction_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    sender_agent_id TEXT,
    receiver_agent_id TEXT,
    message_type TEXT NOT NULL,
    message_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES execution_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (sender_agent_id) REFERENCES agent_definitions(agent_id),
    FOREIGN KEY (receiver_agent_id) REFERENCES agent_definitions(agent_id)
);

-- Human-in-the-Loop
CREATE TABLE IF NOT EXISTS approval_requests (
    request_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    request_type TEXT NOT NULL,
    request_content TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    approver_user_id TEXT,
    approval_response TEXT,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    timeout_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES execution_sessions(session_id) ON DELETE CASCADE
);

-- Background jobs
CREATE TABLE IF NOT EXISTS background_jobs (
    job_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    job_type TEXT NOT NULL,
    job_configuration TEXT NOT NULL,
    scheduled_at TIMESTAMP,
    priority INTEGER DEFAULT 5,
    status TEXT NOT NULL DEFAULT 'queued',
    progress_percentage REAL DEFAULT 0.0,
    result_data TEXT,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES execution_sessions(session_id) ON DELETE CASCADE
);

-- RAG collections and retrievals
CREATE TABLE IF NOT EXISTS rag_collections (
    collection_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    vector_store_type TEXT NOT NULL,
    vector_store_config TEXT,
    embedding_model TEXT,
    document_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rag_retrievals (
    retrieval_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    collection_id TEXT NOT NULL,
    query_text TEXT NOT NULL,
    top_k INTEGER DEFAULT 5,
    retrieved_documents TEXT,
    retrieval_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES execution_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (collection_id) REFERENCES rag_collections(collection_id)
);

-- Event subscriptions for Kafka
CREATE TABLE IF NOT EXISTS event_subscriptions (
    subscription_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    kafka_topic TEXT NOT NULL,
    kafka_group_id TEXT,
    kafka_config TEXT,
    event_filter TEXT,
    handler_type TEXT NOT NULL,
    handler_config TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_processing_log (
    log_id TEXT PRIMARY KEY,
    subscription_id TEXT NOT NULL,
    session_id TEXT,
    event_id TEXT,
    event_topic TEXT NOT NULL,
    event_data TEXT,
    status TEXT NOT NULL DEFAULT 'received',
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    result_data TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subscription_id) REFERENCES event_subscriptions(subscription_id) ON DELETE CASCADE
);

-- Chain of Thought tracking
CREATE TABLE IF NOT EXISTS thought_chains (
    chain_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    chain_type TEXT NOT NULL,
    thoughts TEXT NOT NULL,
    reasoning_depth INTEGER,
    confidence_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES execution_sessions(session_id) ON DELETE CASCADE
);

-- Execution metrics
CREATE TABLE IF NOT EXISTS execution_metrics (
    metric_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metric_unit TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES execution_sessions(session_id) ON DELETE CASCADE
);

-- Audit log
CREATE TABLE IF NOT EXISTS audit_log (
    log_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    action TEXT NOT NULL,
    user_id TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_user ON audit_log(user_id);
