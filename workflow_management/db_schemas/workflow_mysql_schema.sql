-- Workflow Management System - MySQL Database Schema
-- Copyright © 2025-2030, All Rights Reserved
-- Ashutosh Sinha | Email: ajsinha@gmail.com
-- 
-- Legal Notice: This module and the associated software architecture are proprietary and confidential.
-- Unauthorized copying, distribution, modification, or use is strictly prohibited without explicit 
-- written permission from the copyright holder.
-- 
-- Patent Pending: Certain architectural patterns and implementations described in this module 
-- may be subject to patent applications.

-- Workflows Table
CREATE TABLE IF NOT EXISTS wf_workflows (
    workflow_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    definition_json JSON NOT NULL,
    status ENUM('draft', 'active', 'archived', 'deprecated') NOT NULL DEFAULT 'draft',
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    tags JSON,
    UNIQUE KEY unique_workflow_version (name, version),
    INDEX idx_status (status),
    INDEX idx_created_by (created_by),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Workflow Executions Table
CREATE TABLE IF NOT EXISTS wf_executions (
    execution_id VARCHAR(36) PRIMARY KEY,
    workflow_id VARCHAR(36) NOT NULL,
    workflow_version VARCHAR(20) NOT NULL,
    status ENUM('pending', 'running', 'paused', 'completed', 'failed', 'cancelled') NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    triggered_by VARCHAR(255) NOT NULL,
    input_parameters JSON,
    output_results JSON,
    error_message TEXT,
    execution_metadata JSON,
    INDEX idx_workflow_id (workflow_id),
    INDEX idx_status (status),
    INDEX idx_triggered_by (triggered_by),
    INDEX idx_started_at (started_at),
    INDEX idx_composite (execution_id, started_at),
    FOREIGN KEY (workflow_id) REFERENCES wf_workflows(workflow_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Node Executions Table
CREATE TABLE IF NOT EXISTS wf_node_executions (
    node_execution_id VARCHAR(36) PRIMARY KEY,
    execution_id VARCHAR(36) NOT NULL,
    node_id VARCHAR(255) NOT NULL,
    node_type VARCHAR(50) NOT NULL,
    status ENUM('pending', 'running', 'completed', 'failed', 'skipped', 'retrying') NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    duration_ms INT,
    input_data JSON,
    output_data JSON,
    error_details JSON,
    retry_count INT DEFAULT 0,
    iteration_index INT,
    INDEX idx_execution_id (execution_id),
    INDEX idx_status (status),
    INDEX idx_node_type (node_type),
    INDEX idx_composite (execution_id, started_at),
    FOREIGN KEY (execution_id) REFERENCES wf_executions(execution_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Human Tasks Table
CREATE TABLE IF NOT EXISTS wf_human_tasks (
    task_id VARCHAR(36) PRIMARY KEY,
    execution_id VARCHAR(36) NOT NULL,
    node_execution_id VARCHAR(36) NOT NULL,
    assigned_to VARCHAR(255) NOT NULL,
    task_type ENUM('approval', 'input', 'review') NOT NULL,
    status ENUM('pending', 'in_progress', 'completed', 'rejected', 'timeout', 'escalated') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP NULL,
    response_data JSON,
    comments TEXT,
    timeout_at TIMESTAMP NULL,
    INDEX idx_execution_id (execution_id),
    INDEX idx_assigned_to (assigned_to),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (execution_id) REFERENCES wf_executions(execution_id) ON DELETE CASCADE,
    FOREIGN KEY (node_execution_id) REFERENCES wf_node_executions(node_execution_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Workflow Variables Table
CREATE TABLE IF NOT EXISTS wf_variables (
    variable_id VARCHAR(36) PRIMARY KEY,
    execution_id VARCHAR(36) NOT NULL,
    variable_name VARCHAR(255) NOT NULL,
    variable_value JSON,
    scope ENUM('workflow', 'node', 'iteration') NOT NULL,
    node_execution_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_execution_id (execution_id),
    INDEX idx_variable_name (variable_name),
    INDEX idx_scope (scope),
    FOREIGN KEY (execution_id) REFERENCES wf_executions(execution_id) ON DELETE CASCADE,
    FOREIGN KEY (node_execution_id) REFERENCES wf_node_executions(node_execution_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Audit Logs Table
CREATE TABLE IF NOT EXISTS wf_audit_logs (
    log_id VARCHAR(36) PRIMARY KEY,
    execution_id VARCHAR(36) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    log_level ENUM('DEBUG', 'INFO', 'WARN', 'ERROR') NOT NULL,
    message TEXT NOT NULL,
    context_data JSON,
    source VARCHAR(255),
    INDEX idx_execution_id (execution_id),
    INDEX idx_log_level (log_level),
    INDEX idx_timestamp (timestamp),
    INDEX idx_composite (execution_id, timestamp),
    FOREIGN KEY (execution_id) REFERENCES wf_executions(execution_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
