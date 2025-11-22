-- Workflow Management System - SQLite Database Schema
-- Copyright © 2025-2030, All Rights Reserved
-- Ashutosh Sinha | Email: ajsinha@gmail.com
-- 
-- Legal Notice: This module and the associated software architecture are proprietary and confidential.
-- Unauthorized copying, distribution, modification, or use is strictly prohibited without explicit 
-- written permission from the copyright holder.
-- 
-- Patent Pending: Certain architectural patterns and implementations described in this module 
-- may be subject to patent applications.

-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Workflows Table
CREATE TABLE IF NOT EXISTS wf_workflows (
    workflow_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    version TEXT NOT NULL DEFAULT '1.0.0',
    definition_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft', 'active', 'archived', 'deprecated')),
    created_by TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags TEXT,
    UNIQUE(name, version)
);

CREATE INDEX idx_wf_workflows_status ON wf_workflows(status);
CREATE INDEX idx_wf_workflows_created_by ON wf_workflows(created_by);
CREATE INDEX idx_wf_workflows_created_at ON wf_workflows(created_at);

-- Workflow Executions Table
CREATE TABLE IF NOT EXISTS wf_executions (
    execution_id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    workflow_version TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'paused', 'completed', 'failed', 'cancelled')),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    triggered_by TEXT NOT NULL,
    input_parameters TEXT,
    output_results TEXT,
    error_message TEXT,
    execution_metadata TEXT,
    FOREIGN KEY (workflow_id) REFERENCES wf_workflows(workflow_id) ON DELETE CASCADE
);

CREATE INDEX idx_wf_executions_workflow_id ON wf_executions(workflow_id);
CREATE INDEX idx_wf_executions_status ON wf_executions(status);
CREATE INDEX idx_wf_executions_triggered_by ON wf_executions(triggered_by);
CREATE INDEX idx_wf_executions_started_at ON wf_executions(started_at);
CREATE INDEX idx_wf_executions_composite ON wf_executions(execution_id, started_at);

-- Node Executions Table
CREATE TABLE IF NOT EXISTS wf_node_executions (
    node_execution_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    node_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'completed', 'failed', 'skipped', 'retrying')),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    input_data TEXT,
    output_data TEXT,
    error_details TEXT,
    retry_count INTEGER DEFAULT 0,
    iteration_index INTEGER,
    FOREIGN KEY (execution_id) REFERENCES wf_executions(execution_id) ON DELETE CASCADE
);

CREATE INDEX idx_wf_node_executions_execution_id ON wf_node_executions(execution_id);
CREATE INDEX idx_wf_node_executions_status ON wf_node_executions(status);
CREATE INDEX idx_wf_node_executions_node_type ON wf_node_executions(node_type);
CREATE INDEX idx_wf_node_executions_composite ON wf_node_executions(execution_id, started_at);

-- Human Tasks Table
CREATE TABLE IF NOT EXISTS wf_human_tasks (
    task_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    node_execution_id TEXT NOT NULL,
    assigned_to TEXT NOT NULL,
    task_type TEXT NOT NULL CHECK(task_type IN ('approval', 'input', 'review')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed', 'rejected', 'timeout', 'escalated')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    response_data TEXT,
    comments TEXT,
    timeout_at TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES wf_executions(execution_id) ON DELETE CASCADE,
    FOREIGN KEY (node_execution_id) REFERENCES wf_node_executions(node_execution_id) ON DELETE CASCADE
);

CREATE INDEX idx_wf_human_tasks_execution_id ON wf_human_tasks(execution_id);
CREATE INDEX idx_wf_human_tasks_assigned_to ON wf_human_tasks(assigned_to);
CREATE INDEX idx_wf_human_tasks_status ON wf_human_tasks(status);
CREATE INDEX idx_wf_human_tasks_created_at ON wf_human_tasks(created_at);

-- Workflow Variables Table
CREATE TABLE IF NOT EXISTS wf_variables (
    variable_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    variable_name TEXT NOT NULL,
    variable_value TEXT,
    scope TEXT NOT NULL CHECK(scope IN ('workflow', 'node', 'iteration')),
    node_execution_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES wf_executions(execution_id) ON DELETE CASCADE,
    FOREIGN KEY (node_execution_id) REFERENCES wf_node_executions(node_execution_id) ON DELETE CASCADE
);

CREATE INDEX idx_wf_variables_execution_id ON wf_variables(execution_id);
CREATE INDEX idx_wf_variables_variable_name ON wf_variables(variable_name);
CREATE INDEX idx_wf_variables_scope ON wf_variables(scope);

-- Audit Logs Table
CREATE TABLE IF NOT EXISTS wf_audit_logs (
    log_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    log_level TEXT NOT NULL CHECK(log_level IN ('DEBUG', 'INFO', 'WARN', 'ERROR')),
    message TEXT NOT NULL,
    context_data TEXT,
    source TEXT,
    FOREIGN KEY (execution_id) REFERENCES wf_executions(execution_id) ON DELETE CASCADE
);

CREATE INDEX idx_wf_audit_logs_execution_id ON wf_audit_logs(execution_id);
CREATE INDEX idx_wf_audit_logs_log_level ON wf_audit_logs(log_level);
CREATE INDEX idx_wf_audit_logs_timestamp ON wf_audit_logs(timestamp);
CREATE INDEX idx_wf_audit_logs_composite ON wf_audit_logs(execution_id, timestamp);

-- Trigger to update updated_at timestamp on wf_workflows
CREATE TRIGGER IF NOT EXISTS update_wf_workflows_timestamp 
AFTER UPDATE ON wf_workflows
BEGIN
    UPDATE wf_workflows SET updated_at = CURRENT_TIMESTAMP WHERE workflow_id = NEW.workflow_id;
END;

-- Trigger to update updated_at timestamp on wf_variables
CREATE TRIGGER IF NOT EXISTS update_wf_variables_timestamp 
AFTER UPDATE ON wf_variables
BEGIN
    UPDATE wf_variables SET updated_at = CURRENT_TIMESTAMP WHERE variable_id = NEW.variable_id;
END;
