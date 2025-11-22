-- Workflow Management System - PostgreSQL Database Schema
-- Copyright © 2025-2030, All Rights Reserved
-- Ashutosh Sinha | Email: ajsinha@gmail.com
-- 
-- Legal Notice: This module and the associated software architecture are proprietary and confidential.
-- Unauthorized copying, distribution, modification, or use is strictly prohibited without explicit 
-- written permission from the copyright holder.
-- 
-- Patent Pending: Certain architectural patterns and implementations described in this module 
-- may be subject to patent applications.

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM types
CREATE TYPE workflow_status AS ENUM ('draft', 'active', 'archived', 'deprecated');
CREATE TYPE execution_status AS ENUM ('pending', 'running', 'paused', 'completed', 'failed', 'cancelled');
CREATE TYPE node_execution_status AS ENUM ('pending', 'running', 'completed', 'failed', 'skipped', 'retrying');
CREATE TYPE task_type AS ENUM ('approval', 'input', 'review');
CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'rejected', 'timeout', 'escalated');
CREATE TYPE variable_scope AS ENUM ('workflow', 'node', 'iteration');
CREATE TYPE log_level AS ENUM ('DEBUG', 'INFO', 'WARN', 'ERROR');

-- Workflows Table
CREATE TABLE IF NOT EXISTS wf_workflows (
    workflow_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    definition_json JSONB NOT NULL,
    status workflow_status NOT NULL DEFAULT 'draft',
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tags JSONB,
    UNIQUE (name, version)
);

CREATE INDEX idx_wf_workflows_status ON wf_workflows(status);
CREATE INDEX idx_wf_workflows_created_by ON wf_workflows(created_by);
CREATE INDEX idx_wf_workflows_created_at ON wf_workflows(created_at);
CREATE INDEX idx_wf_workflows_definition_json ON wf_workflows USING GIN(definition_json);
CREATE INDEX idx_wf_workflows_tags ON wf_workflows USING GIN(tags);

-- Workflow Executions Table
CREATE TABLE IF NOT EXISTS wf_executions (
    execution_id UUID PRIMARY KEY,
    workflow_id UUID NOT NULL,
    workflow_version VARCHAR(20) NOT NULL,
    status execution_status NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    triggered_by VARCHAR(255) NOT NULL,
    input_parameters JSONB,
    output_results JSONB,
    error_message TEXT,
    execution_metadata JSONB,
    FOREIGN KEY (workflow_id) REFERENCES wf_workflows(workflow_id) ON DELETE CASCADE
);

CREATE INDEX idx_wf_executions_workflow_id ON wf_executions(workflow_id);
CREATE INDEX idx_wf_executions_status ON wf_executions(status);
CREATE INDEX idx_wf_executions_triggered_by ON wf_executions(triggered_by);
CREATE INDEX idx_wf_executions_started_at ON wf_executions(started_at);
CREATE INDEX idx_wf_executions_composite ON wf_executions(execution_id, started_at);
CREATE INDEX idx_wf_executions_input_params ON wf_executions USING GIN(input_parameters);
CREATE INDEX idx_wf_executions_output_results ON wf_executions USING GIN(output_results);

-- Node Executions Table
CREATE TABLE IF NOT EXISTS wf_node_executions (
    node_execution_id UUID PRIMARY KEY,
    execution_id UUID NOT NULL,
    node_id VARCHAR(255) NOT NULL,
    node_type VARCHAR(50) NOT NULL,
    status node_execution_status NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    input_data JSONB,
    output_data JSONB,
    error_details JSONB,
    retry_count INTEGER DEFAULT 0,
    iteration_index INTEGER,
    FOREIGN KEY (execution_id) REFERENCES wf_executions(execution_id) ON DELETE CASCADE
);

CREATE INDEX idx_wf_node_executions_execution_id ON wf_node_executions(execution_id);
CREATE INDEX idx_wf_node_executions_status ON wf_node_executions(status);
CREATE INDEX idx_wf_node_executions_node_type ON wf_node_executions(node_type);
CREATE INDEX idx_wf_node_executions_composite ON wf_node_executions(execution_id, started_at);
CREATE INDEX idx_wf_node_executions_input_data ON wf_node_executions USING GIN(input_data);
CREATE INDEX idx_wf_node_executions_output_data ON wf_node_executions USING GIN(output_data);

-- Human Tasks Table
CREATE TABLE IF NOT EXISTS wf_human_tasks (
    task_id UUID PRIMARY KEY,
    execution_id UUID NOT NULL,
    node_execution_id UUID NOT NULL,
    assigned_to VARCHAR(255) NOT NULL,
    task_type task_type NOT NULL,
    status task_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP WITH TIME ZONE,
    response_data JSONB,
    comments TEXT,
    timeout_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (execution_id) REFERENCES wf_executions(execution_id) ON DELETE CASCADE,
    FOREIGN KEY (node_execution_id) REFERENCES wf_node_executions(node_execution_id) ON DELETE CASCADE
);

CREATE INDEX idx_wf_human_tasks_execution_id ON wf_human_tasks(execution_id);
CREATE INDEX idx_wf_human_tasks_assigned_to ON wf_human_tasks(assigned_to);
CREATE INDEX idx_wf_human_tasks_status ON wf_human_tasks(status);
CREATE INDEX idx_wf_human_tasks_created_at ON wf_human_tasks(created_at);
CREATE INDEX idx_wf_human_tasks_response_data ON wf_human_tasks USING GIN(response_data);

-- Workflow Variables Table
CREATE TABLE IF NOT EXISTS wf_variables (
    variable_id UUID PRIMARY KEY,
    execution_id UUID NOT NULL,
    variable_name VARCHAR(255) NOT NULL,
    variable_value JSONB,
    scope variable_scope NOT NULL,
    node_execution_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES wf_executions(execution_id) ON DELETE CASCADE,
    FOREIGN KEY (node_execution_id) REFERENCES wf_node_executions(node_execution_id) ON DELETE CASCADE
);

CREATE INDEX idx_wf_variables_execution_id ON wf_variables(execution_id);
CREATE INDEX idx_wf_variables_variable_name ON wf_variables(variable_name);
CREATE INDEX idx_wf_variables_scope ON wf_variables(scope);
CREATE INDEX idx_wf_variables_value ON wf_variables USING GIN(variable_value);

-- Audit Logs Table
CREATE TABLE IF NOT EXISTS wf_audit_logs (
    log_id UUID PRIMARY KEY,
    execution_id UUID NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    log_level log_level NOT NULL,
    message TEXT NOT NULL,
    context_data JSONB,
    source VARCHAR(255),
    FOREIGN KEY (execution_id) REFERENCES wf_executions(execution_id) ON DELETE CASCADE
);

CREATE INDEX idx_wf_audit_logs_execution_id ON wf_audit_logs(execution_id);
CREATE INDEX idx_wf_audit_logs_log_level ON wf_audit_logs(log_level);
CREATE INDEX idx_wf_audit_logs_timestamp ON wf_audit_logs(timestamp);
CREATE INDEX idx_wf_audit_logs_composite ON wf_audit_logs(execution_id, timestamp);
CREATE INDEX idx_wf_audit_logs_context_data ON wf_audit_logs USING GIN(context_data);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for wf_workflows
CREATE TRIGGER update_wf_workflows_updated_at
BEFORE UPDATE ON wf_workflows
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger for wf_variables
CREATE TRIGGER update_wf_variables_updated_at
BEFORE UPDATE ON wf_variables
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
