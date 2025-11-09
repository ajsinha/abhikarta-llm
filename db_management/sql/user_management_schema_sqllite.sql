-- Database Schema for Abhikarta LLM User Management System
-- SQLite Version
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
-- SQLITE VERSION
-- =============================================================================

-- Enable foreign key support (must be done for each connection)
PRAGMA foreign_keys = ON;

-- Drop existing tables if they exist (for clean installation)
DROP TABLE IF EXISTS user_roles;
DROP TABLE IF EXISTS role_resources;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS resources;

-- =============================================================================
-- RESOURCES TABLE
-- Stores information about system resources that can be accessed
-- System resources that can be accessed through RBAC
-- =============================================================================
CREATE TABLE resources (
    resource_name TEXT PRIMARY KEY,
    resource_type TEXT NOT NULL,
    description TEXT,
    enabled INTEGER DEFAULT 1 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    metadata TEXT,

    CHECK (resource_name <> ''),
    CHECK (resource_type <> ''),
    CHECK (enabled IN (0, 1))
);

CREATE INDEX idx_resources_type ON resources(resource_type);
CREATE INDEX idx_resources_enabled ON resources(enabled);

-- =============================================================================
-- ROLES TABLE
-- Stores role definitions
-- Role definitions for RBAC
-- =============================================================================
CREATE TABLE roles (
    role_name TEXT PRIMARY KEY,
    description TEXT,
    enabled INTEGER DEFAULT 1 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    metadata TEXT,

    CHECK (role_name <> ''),
    CHECK (enabled IN (0, 1))
);

CREATE INDEX idx_roles_enabled ON roles(enabled);

-- =============================================================================
-- ROLE_RESOURCES TABLE
-- Maps roles to resources with specific permissions
-- =============================================================================
CREATE TABLE role_resources (
    role_name TEXT NOT NULL,
    resource_name TEXT NOT NULL,
    can_create INTEGER DEFAULT 0 NOT NULL,
    can_read INTEGER DEFAULT 0 NOT NULL,
    can_update INTEGER DEFAULT 0 NOT NULL,
    can_delete INTEGER DEFAULT 0 NOT NULL,
    can_execute INTEGER DEFAULT 0 NOT NULL,

    PRIMARY KEY (role_name, resource_name),
    FOREIGN KEY (role_name) REFERENCES roles(role_name) ON DELETE CASCADE,
    -- Note: resource_name may contain patterns like '*' or 'yahoo*'
    -- so we don't enforce a foreign key constraint

    CHECK (can_create IN (0, 1)),
    CHECK (can_read IN (0, 1)),
    CHECK (can_update IN (0, 1)),
    CHECK (can_delete IN (0, 1)),
    CHECK (can_execute IN (0, 1)),
    CHECK (can_create OR can_read OR can_update OR can_delete OR can_execute)
);

CREATE INDEX idx_role_resources_role ON role_resources(role_name);
CREATE INDEX idx_role_resources_resource ON role_resources(resource_name);

-- =============================================================================
-- USERS TABLE
-- Stores user account information
-- User accounts in the system
-- =============================================================================
CREATE TABLE users (
    userid TEXT PRIMARY KEY,
    fullname TEXT NOT NULL,
    emailaddress TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    enabled INTEGER DEFAULT 1 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login TIMESTAMP,
    metadata TEXT,

    CHECK (userid <> ''),
    CHECK (fullname <> ''),
    CHECK (emailaddress <> ''),
    CHECK (password_hash <> ''),
    CHECK (enabled IN (0, 1))
);

CREATE INDEX idx_users_emailaddress ON users(emailaddress);
CREATE INDEX idx_users_enabled ON users(enabled);
CREATE INDEX idx_users_last_login ON users(last_login);

-- Trigger to auto-update updated_at timestamp
CREATE TRIGGER trigger_users_updated_at
    AFTER UPDATE ON users
    FOR EACH ROW
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE userid = NEW.userid;
END;

-- =============================================================================
-- USER_ROLES TABLE
-- Maps users to their assigned roles
-- =============================================================================
CREATE TABLE user_roles (
    userid TEXT NOT NULL,
    role_name TEXT NOT NULL,

    PRIMARY KEY (userid, role_name),
    FOREIGN KEY (userid) REFERENCES users(userid) ON DELETE CASCADE,
    FOREIGN KEY (role_name) REFERENCES roles(role_name) ON DELETE CASCADE
);

CREATE INDEX idx_user_roles_user ON user_roles(userid);
CREATE INDEX idx_user_roles_role ON user_roles(role_name);

-- =============================================================================
-- INITIAL DATA
-- Insert default admin role and admin user
-- =============================================================================

-- Insert admin role with full permissions
INSERT INTO roles (role_name, description, enabled, created_at, metadata)
VALUES (
    'admin',
    'Administrator role with full system access',
    1,
    CURRENT_TIMESTAMP,
    '{"is_system_role": true, "cannot_be_deleted": true}'
);

-- Admin role has access to all resources (pattern *)
INSERT INTO role_resources (role_name, resource_name, can_create, can_read, can_update, can_delete, can_execute)
VALUES ('admin', '*', 1, 1, 1, 1, 1);

-- Insert admin user (default password: admin123 - MUST BE CHANGED)
-- Password hash for "admin123" using bcrypt
INSERT INTO users (userid, fullname, emailaddress, password_hash, enabled, created_at, updated_at, metadata)
VALUES (
    'admin',
    'System Administrator',
    'admin@abhikarta.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbRCvO.6i',
    1,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    '{"is_system_user": true, "must_change_password": true}'
);

-- Assign admin role to admin user
INSERT INTO user_roles (userid, role_name)
VALUES ('admin', 'admin');

-- =============================================================================
-- SAMPLE DATA (Optional - can be removed for production)
-- =============================================================================

-- Sample Resources
INSERT INTO resources (resource_name, resource_type, description, enabled, metadata) VALUES
('model_api', 'api', 'Core LLM model API endpoint', 1, '{"endpoint": "/api/v1/model", "version": "1.0"}'),
('public_model_api', 'api', 'Public LLM model API with rate limiting', 1, '{"endpoint": "/api/v1/public/model", "version": "1.0"}'),
('training_data', 'data', 'Training datasets for model fine-tuning', 1, '{"storage_location": "s3://abhikarta-training-data"}'),
('model_management', 'admin', 'Model management and configuration system', 1, '{"allows_deployment": true}'),
('analytics_dashboard', 'dashboard', 'Analytics and monitoring dashboard', 1, '{"url": "https://analytics.abhikarta.local"}'),
('user_management', 'admin', 'User and role management system', 1, '{"sensitive": true}'),
('yahoo_finance', 'external', 'Yahoo Finance API integration', 1, '{"external_service": true, "api_key_required": true}'),
('yahoo_news', 'external', 'Yahoo News API integration', 1, '{"external_service": true, "api_key_required": true}');

-- Sample Roles
INSERT INTO roles (role_name, description, enabled, metadata) VALUES
('developer', 'Developer role with API and model access', 1, '{"max_api_calls_per_day": 10000}'),
('analyst', 'Data analyst role with read-only access', 1, '{"max_api_calls_per_day": 5000}'),
('external_api_user', 'External API user with limited access', 1, '{"max_api_calls_per_day": 1000, "rate_limit_per_minute": 10}');

-- Sample Role-Resource Mappings
INSERT INTO role_resources (role_name, resource_name, can_create, can_read, can_update, can_delete, can_execute) VALUES
-- Developer permissions
('developer', 'model_api', 0, 1, 0, 0, 1),
('developer', 'training_data', 0, 1, 0, 0, 0),
('developer', 'model_management', 1, 1, 1, 0, 1),

-- Analyst permissions
('analyst', 'model_api', 0, 1, 0, 0, 1),
('analyst', 'training_data', 0, 1, 0, 0, 0),
('analyst', 'analytics_dashboard', 0, 1, 0, 0, 0),

-- External API user permissions
('external_api_user', 'public_model_api', 0, 1, 0, 0, 1);

-- Sample Users
INSERT INTO users (userid, fullname, emailaddress, password_hash, enabled, metadata) VALUES
('john_developer', 'John Smith', 'john.smith@example.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbRCvO.6i',
 1, '{"department": "Engineering", "location": "San Francisco"}'),
('jane_analyst', 'Jane Doe', 'jane.doe@example.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbRCvO.6i',
 1, '{"department": "Data Science", "location": "New York"}');

-- Sample User-Role Mappings
INSERT INTO user_roles (userid, role_name) VALUES
('john_developer', 'developer'),
('jane_analyst', 'analyst');

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
-- WHERE u.userid = 'john_developer' AND u.enabled = 1;

-- Query to find all users who can access a specific resource
-- SELECT DISTINCT u.userid, u.fullname
-- FROM users u
-- JOIN user_roles ur ON u.userid = ur.userid
-- JOIN role_resources rr ON ur.role_name = rr.role_name
-- WHERE rr.resource_name = 'model_api' AND u.enabled = 1;

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================