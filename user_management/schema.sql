-- Database Schema for Abhikarta LLM User Management System
-- 
-- Copyright © 2025-2030, All Rights Reserved
-- Ashutosh Sinha
-- Email: ajsinha@gmail.com
--
-- Legal Notice:
-- This document and the associated software architecture are proprietary and confidential.
-- Unauthorized copying, distribution, modification, or use of this document or the software
-- system it describes is strictly prohibited without explicit written permission from the
-- copyright holder. This document is provided "as is" without warranty of any kind, either
-- expressed or implied. The copyright holder shall not be liable for any damages arising
-- from the use of this document or the software system it describes.
--
-- Patent Pending: Certain architectural patterns and implementations described in this
-- document may be subject to patent applications.

-- =============================================================================
-- POSTGRESQL VERSION
-- =============================================================================

-- Drop existing tables if they exist (for clean installation)
DROP TABLE IF EXISTS user_roles CASCADE;
DROP TABLE IF EXISTS role_resources CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS roles CASCADE;
DROP TABLE IF EXISTS resources CASCADE;

-- =============================================================================
-- RESOURCES TABLE
-- Stores information about system resources that can be accessed
-- =============================================================================
CREATE TABLE resources (
    resource_name VARCHAR(255) PRIMARY KEY,
    resource_type VARCHAR(100) NOT NULL,
    description TEXT,
    enabled BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    metadata JSONB,
    
    CONSTRAINT chk_resource_name_not_empty CHECK (resource_name <> ''),
    CONSTRAINT chk_resource_type_not_empty CHECK (resource_type <> '')
);

CREATE INDEX idx_resources_type ON resources(resource_type);
CREATE INDEX idx_resources_enabled ON resources(enabled);

COMMENT ON TABLE resources IS 'System resources that can be accessed through RBAC';
COMMENT ON COLUMN resources.resource_name IS 'Unique identifier for the resource';
COMMENT ON COLUMN resources.resource_type IS 'Type/category of the resource (api, data, admin, etc.)';
COMMENT ON COLUMN resources.description IS 'Human-readable description of the resource';
COMMENT ON COLUMN resources.enabled IS 'Whether the resource is currently enabled';
COMMENT ON COLUMN resources.created_at IS 'Timestamp when the resource was created';
COMMENT ON COLUMN resources.metadata IS 'Additional metadata as JSON';

-- =============================================================================
-- ROLES TABLE
-- Stores role definitions
-- =============================================================================
CREATE TABLE roles (
    role_name VARCHAR(255) PRIMARY KEY,
    description TEXT,
    enabled BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    metadata JSONB,
    
    CONSTRAINT chk_role_name_not_empty CHECK (role_name <> '')
);

CREATE INDEX idx_roles_enabled ON roles(enabled);

COMMENT ON TABLE roles IS 'Role definitions for RBAC';
COMMENT ON COLUMN roles.role_name IS 'Unique identifier for the role';
COMMENT ON COLUMN roles.description IS 'Human-readable description of the role';
COMMENT ON COLUMN roles.enabled IS 'Whether the role is currently enabled';
COMMENT ON COLUMN roles.created_at IS 'Timestamp when the role was created';
COMMENT ON COLUMN roles.metadata IS 'Additional metadata as JSON';

-- =============================================================================
-- ROLE_RESOURCES TABLE
-- Maps roles to resources with specific permissions
-- =============================================================================
CREATE TABLE role_resources (
    role_name VARCHAR(255) NOT NULL,
    resource_name VARCHAR(255) NOT NULL,
    can_create BOOLEAN DEFAULT FALSE NOT NULL,
    can_read BOOLEAN DEFAULT FALSE NOT NULL,
    can_update BOOLEAN DEFAULT FALSE NOT NULL,
    can_delete BOOLEAN DEFAULT FALSE NOT NULL,
    can_execute BOOLEAN DEFAULT FALSE NOT NULL,
    
    PRIMARY KEY (role_name, resource_name),
    FOREIGN KEY (role_name) REFERENCES roles(role_name) ON DELETE CASCADE,
    -- Note: resource_name may contain patterns like '*' or 'yahoo*'
    -- so we don't enforce a foreign key constraint
    
    CONSTRAINT chk_at_least_one_permission CHECK (
        can_create OR can_read OR can_update OR can_delete OR can_execute
    )
);

CREATE INDEX idx_role_resources_role ON role_resources(role_name);
CREATE INDEX idx_role_resources_resource ON role_resources(resource_name);

COMMENT ON TABLE role_resources IS 'Maps roles to resources with specific permissions';
COMMENT ON COLUMN role_resources.role_name IS 'Role that has access to the resource';
COMMENT ON COLUMN role_resources.resource_name IS 'Resource name or pattern (e.g., *, yahoo*)';
COMMENT ON COLUMN role_resources.can_create IS 'Permission to create the resource';
COMMENT ON COLUMN role_resources.can_read IS 'Permission to read the resource';
COMMENT ON COLUMN role_resources.can_update IS 'Permission to update/modify the resource';
COMMENT ON COLUMN role_resources.can_delete IS 'Permission to delete the resource';
COMMENT ON COLUMN role_resources.can_execute IS 'Permission to execute operations on the resource';

-- =============================================================================
-- USERS TABLE
-- Stores user account information
-- =============================================================================
CREATE TABLE users (
    userid VARCHAR(255) PRIMARY KEY,
    fullname VARCHAR(500) NOT NULL,
    emailaddress VARCHAR(500) NOT NULL,
    password_hash VARCHAR(500) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login TIMESTAMP,
    metadata JSONB,
    
    CONSTRAINT chk_userid_not_empty CHECK (userid <> ''),
    CONSTRAINT chk_fullname_not_empty CHECK (fullname <> ''),
    CONSTRAINT chk_emailaddress_not_empty CHECK (emailaddress <> ''),
    CONSTRAINT chk_password_hash_not_empty CHECK (password_hash <> '')
);

CREATE INDEX idx_users_emailaddress ON users(emailaddress);
CREATE INDEX idx_users_enabled ON users(enabled);
CREATE INDEX idx_users_last_login ON users(last_login);

COMMENT ON TABLE users IS 'User accounts in the system';
COMMENT ON COLUMN users.userid IS 'Unique identifier for the user';
COMMENT ON COLUMN users.fullname IS 'Full name of the user';
COMMENT ON COLUMN users.emailaddress IS 'Email address of the user';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hash of the user password';
COMMENT ON COLUMN users.enabled IS 'Whether the user account is enabled';
COMMENT ON COLUMN users.created_at IS 'Timestamp when the user was created';
COMMENT ON COLUMN users.updated_at IS 'Timestamp when the user was last updated';
COMMENT ON COLUMN users.last_login IS 'Timestamp of the last successful login';
COMMENT ON COLUMN users.metadata IS 'Additional user metadata as JSON';

-- =============================================================================
-- USER_ROLES TABLE
-- Maps users to their assigned roles
-- =============================================================================
CREATE TABLE user_roles (
    userid VARCHAR(255) NOT NULL,
    role_name VARCHAR(255) NOT NULL,
    
    PRIMARY KEY (userid, role_name),
    FOREIGN KEY (userid) REFERENCES users(userid) ON DELETE CASCADE,
    FOREIGN KEY (role_name) REFERENCES roles(role_name) ON DELETE CASCADE
);

CREATE INDEX idx_user_roles_user ON user_roles(userid);
CREATE INDEX idx_user_roles_role ON user_roles(role_name);

COMMENT ON TABLE user_roles IS 'Maps users to their assigned roles';
COMMENT ON COLUMN user_roles.userid IS 'User identifier';
COMMENT ON COLUMN user_roles.role_name IS 'Role assigned to the user';

-- =============================================================================
-- INITIAL DATA
-- Insert default admin role and admin user
-- =============================================================================

-- Insert admin role with full permissions
INSERT INTO roles (role_name, description, enabled, created_at, metadata)
VALUES (
    'admin',
    'Administrator role with full system access',
    TRUE,
    CURRENT_TIMESTAMP,
    '{"is_system_role": true, "cannot_be_deleted": true}'::JSONB
);

-- Admin role has access to all resources (pattern *)
INSERT INTO role_resources (role_name, resource_name, can_create, can_read, can_update, can_delete, can_execute)
VALUES ('admin', '*', TRUE, TRUE, TRUE, TRUE, TRUE);

-- Insert admin user (default password: admin123 - MUST BE CHANGED)
-- Password hash for "admin123" using bcrypt
INSERT INTO users (userid, fullname, emailaddress, password_hash, enabled, created_at, updated_at, metadata)
VALUES (
    'admin',
    'System Administrator',
    'admin@abhikarta.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbRCvO.6i',
    TRUE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    '{"is_system_user": true, "must_change_password": true}'::JSONB
);

-- Assign admin role to admin user
INSERT INTO user_roles (userid, role_name)
VALUES ('admin', 'admin');

-- =============================================================================
-- SAMPLE DATA (Optional - can be removed for production)
-- =============================================================================

-- Sample Resources
INSERT INTO resources (resource_name, resource_type, description, enabled, metadata) VALUES
('model_api', 'api', 'Core LLM model API endpoint', TRUE, '{"endpoint": "/api/v1/model", "version": "1.0"}'::JSONB),
('public_model_api', 'api', 'Public LLM model API with rate limiting', TRUE, '{"endpoint": "/api/v1/public/model", "version": "1.0"}'::JSONB),
('training_data', 'data', 'Training datasets for model fine-tuning', TRUE, '{"storage_location": "s3://abhikarta-training-data"}'::JSONB),
('model_management', 'admin', 'Model management and configuration system', TRUE, '{"allows_deployment": true}'::JSONB),
('analytics_dashboard', 'dashboard', 'Analytics and monitoring dashboard', TRUE, '{"url": "https://analytics.abhikarta.local"}'::JSONB),
('user_management', 'admin', 'User and role management system', TRUE, '{"sensitive": true}'::JSONB),
('yahoo_finance', 'external', 'Yahoo Finance API integration', TRUE, '{"external_service": true, "api_key_required": true}'::JSONB),
('yahoo_news', 'external', 'Yahoo News API integration', TRUE, '{"external_service": true, "api_key_required": true}'::JSONB);

-- Sample Roles
INSERT INTO roles (role_name, description, enabled, metadata) VALUES
('developer', 'Developer role with API and model access', TRUE, '{"max_api_calls_per_day": 10000}'::JSONB),
('analyst', 'Data analyst role with read-only access', TRUE, '{"max_api_calls_per_day": 5000}'::JSONB),
('external_api_user', 'External API user with limited access', TRUE, '{"max_api_calls_per_day": 1000, "rate_limit_per_minute": 10}'::JSONB);

-- Sample Role-Resource Mappings
INSERT INTO role_resources (role_name, resource_name, can_create, can_read, can_update, can_delete, can_execute) VALUES
-- Developer permissions
('developer', 'model_api', FALSE, TRUE, FALSE, FALSE, TRUE),
('developer', 'training_data', FALSE, TRUE, FALSE, FALSE, FALSE),
('developer', 'model_management', TRUE, TRUE, TRUE, FALSE, TRUE),

-- Analyst permissions
('analyst', 'model_api', FALSE, TRUE, FALSE, FALSE, TRUE),
('analyst', 'training_data', FALSE, TRUE, FALSE, FALSE, FALSE),
('analyst', 'analytics_dashboard', FALSE, TRUE, FALSE, FALSE, FALSE),

-- External API user permissions
('external_api_user', 'public_model_api', FALSE, TRUE, FALSE, FALSE, TRUE);

-- Sample Users
INSERT INTO users (userid, fullname, emailaddress, password_hash, enabled, metadata) VALUES
('john_developer', 'John Smith', 'john.smith@example.com', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbRCvO.6i',
 TRUE, '{"department": "Engineering", "location": "San Francisco"}'::JSONB),
('jane_analyst', 'Jane Doe', 'jane.doe@example.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbRCvO.6i',
 TRUE, '{"department": "Data Science", "location": "New York"}'::JSONB);

-- Sample User-Role Mappings
INSERT INTO user_roles (userid, role_name) VALUES
('john_developer', 'developer'),
('jane_analyst', 'analyst');

-- =============================================================================
-- MYSQL VERSION (Separate section)
-- =============================================================================
-- For MySQL, replace the following:
-- 1. JSONB -> JSON
-- 2. CURRENT_TIMESTAMP -> NOW()
-- 3. Remove CASCADE from DROP TABLE
-- 4. Adjust varchar lengths if needed (MySQL has different limits)
-- 5. Boolean type: BOOLEAN is alias for TINYINT(1)
--
-- Example MySQL equivalent for resources table:
-- CREATE TABLE resources (
--     resource_name VARCHAR(255) PRIMARY KEY,
--     resource_type VARCHAR(100) NOT NULL,
--     description TEXT,
--     enabled BOOLEAN DEFAULT TRUE NOT NULL,
--     created_at TIMESTAMP DEFAULT NOW() NOT NULL,
--     metadata JSON,
--     
--     CONSTRAINT chk_resource_name_not_empty CHECK (resource_name <> ''),
--     CONSTRAINT chk_resource_type_not_empty CHECK (resource_type <> '')
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- SQLITE VERSION (Separate section)
-- =============================================================================
-- For SQLite, make the following changes:
-- 1. Remove CASCADE from foreign keys
-- 2. JSONB -> TEXT (store as JSON string)
-- 3. BOOLEAN -> INTEGER (0 or 1)
-- 4. VARCHAR -> TEXT
-- 5. Remove CHECK constraints (SQLite has limited support)
-- 6. Remove INDEX names (SQLite auto-names)

-- =============================================================================
-- USEFUL QUERIES
-- =============================================================================

-- Query to find all users with a specific role
-- SELECT u.userid, u.fullname, u.emailaddress
-- FROM users u
-- JOIN user_roles ur ON u.userid = ur.userid
-- WHERE ur.role_name = 'developer';

-- Query to find all permissions for a user
-- SELECT DISTINCT rr.resource_name, rr.can_create, rr.can_read, rr.can_update, 
--                 rr.can_delete, rr.can_execute
-- FROM users u
-- JOIN user_roles ur ON u.userid = ur.userid
-- JOIN role_resources rr ON ur.role_name = rr.role_name
-- WHERE u.userid = 'john_developer' AND u.enabled = TRUE;

-- Query to find all users who can access a specific resource
-- SELECT DISTINCT u.userid, u.fullname
-- FROM users u
-- JOIN user_roles ur ON u.userid = ur.userid
-- JOIN role_resources rr ON ur.role_name = rr.role_name
-- WHERE rr.resource_name = 'model_api' AND u.enabled = TRUE;

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
