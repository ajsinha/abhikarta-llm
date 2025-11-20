-- ============================================================================
-- Abhikarta LLM Platform - SQLite Schema for LLM Interaction Logging
--
-- Copyright © 2025-2030, All Rights Reserved
-- Ashutosh Sinha | Email: ajsinha@gmail.com
-- ============================================================================

-- ============================================================================
-- Table: llm_interactions
-- Purpose: Log all user interactions with LLM facades
-- ============================================================================

CREATE TABLE IF NOT EXISTS llm_interactions (
    -- Primary Key
    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- User and Session Information
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    chat_session_id VARCHAR(255),  -- The chat session ID (chat_abc123_...)

    -- Interaction Metadata
    interaction_type VARCHAR(50) NOT NULL DEFAULT 'chat',
    interaction_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- LLM Provider Information
    provider_name VARCHAR(100) NOT NULL,
    model_name VARCHAR(100) NOT NULL,

    -- Request Data
    user_data TEXT NOT NULL,  -- User's message/prompt
    request_parameters TEXT,   -- JSON string of parameters (temperature, max_tokens, etc.)

    -- Response Data
    llm_response TEXT NOT NULL,  -- LLM's response
    response_metadata TEXT,       -- JSON string of metadata (usage, finish_reason, etc.)

    -- Performance Metrics
    response_time_ms INTEGER,     -- Response time in milliseconds
    prompt_tokens INTEGER,         -- Number of tokens in prompt
    completion_tokens INTEGER,     -- Number of tokens in completion
    total_tokens INTEGER,          -- Total tokens used

    -- Status and Error Handling
    status VARCHAR(20) NOT NULL DEFAULT 'success',  -- success, error, timeout
    error_message TEXT,            -- Error message if status != success

    -- Additional Metadata
    cached_facade BOOLEAN DEFAULT 0,  -- Was cached facade used?
    streaming BOOLEAN DEFAULT 0,      -- Was streaming used?
    client_ip VARCHAR(45),            -- Client IP address
    user_agent TEXT,                  -- User agent string

    -- Audit Fields
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Index on user_id for user-specific queries
CREATE INDEX IF NOT EXISTS idx_llm_interactions_user_id
ON llm_interactions(user_id);

-- Index on session_id for session-specific queries
CREATE INDEX IF NOT EXISTS idx_llm_interactions_session_id
ON llm_interactions(session_id);

-- Index on chat_session_id for chat session queries
CREATE INDEX IF NOT EXISTS idx_llm_interactions_chat_session_id
ON llm_interactions(chat_session_id);

-- Index on timestamp for time-based queries
CREATE INDEX IF NOT EXISTS idx_llm_interactions_timestamp
ON llm_interactions(interaction_timestamp);

-- Composite index for user + timestamp (common query pattern)
CREATE INDEX IF NOT EXISTS idx_llm_interactions_user_timestamp
ON llm_interactions(user_id, interaction_timestamp DESC);

-- Index on provider and model for analytics
CREATE INDEX IF NOT EXISTS idx_llm_interactions_provider_model
ON llm_interactions(provider_name, model_name);

-- Index on interaction type
CREATE INDEX IF NOT EXISTS idx_llm_interactions_type
ON llm_interactions(interaction_type);

-- Index on status for error tracking
CREATE INDEX IF NOT EXISTS idx_llm_interactions_status
ON llm_interactions(status);

-- ============================================================================
-- Triggers for Auto-Update
-- ============================================================================

-- Trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS trigger_llm_interactions_updated_at
AFTER UPDATE ON llm_interactions
FOR EACH ROW
BEGIN
    UPDATE llm_interactions
    SET updated_at = CURRENT_TIMESTAMP
    WHERE interaction_id = NEW.interaction_id;
END;

-- ============================================================================
-- Views for Common Queries
-- ============================================================================

-- View: Recent interactions by user
CREATE VIEW IF NOT EXISTS v_recent_user_interactions AS
SELECT
    interaction_id,
    user_id,
    session_id,
    chat_session_id,
    interaction_type,
    interaction_timestamp,
    provider_name,
    model_name,
    SUBSTR(user_data, 1, 100) AS user_data_preview,
    SUBSTR(llm_response, 1, 100) AS response_preview,
    response_time_ms,
    total_tokens,
    status,
    cached_facade
FROM llm_interactions
ORDER BY interaction_timestamp DESC;

-- View: Interaction statistics by provider/model
CREATE VIEW IF NOT EXISTS v_provider_model_stats AS
SELECT
    provider_name,
    model_name,
    COUNT(*) AS total_interactions,
    COUNT(CASE WHEN status = 'success' THEN 1 END) AS successful_interactions,
    COUNT(CASE WHEN status = 'error' THEN 1 END) AS failed_interactions,
    AVG(response_time_ms) AS avg_response_time_ms,
    SUM(total_tokens) AS total_tokens_used,
    AVG(total_tokens) AS avg_tokens_per_interaction,
    COUNT(CASE WHEN cached_facade = 1 THEN 1 END) AS cached_facade_count
FROM llm_interactions
GROUP BY provider_name, model_name;

-- View: User activity summary
CREATE VIEW IF NOT EXISTS v_user_activity_summary AS
SELECT
    user_id,
    COUNT(*) AS total_interactions,
    COUNT(DISTINCT chat_session_id) AS unique_sessions,
    MIN(interaction_timestamp) AS first_interaction,
    MAX(interaction_timestamp) AS last_interaction,
    SUM(total_tokens) AS total_tokens_used,
    AVG(response_time_ms) AS avg_response_time_ms
FROM llm_interactions
GROUP BY user_id;

-- ============================================================================
-- Sample Queries
-- ============================================================================

-- Get all interactions for a specific user
-- SELECT * FROM llm_interactions WHERE user_id = 'user@example.com' ORDER BY interaction_timestamp DESC;

-- Get interactions for a specific chat session
-- SELECT * FROM llm_interactions WHERE chat_session_id = 'chat_abc123_1700000000' ORDER BY interaction_timestamp;

-- Get error rate by provider
-- SELECT provider_name,
--        COUNT(*) as total,
--        COUNT(CASE WHEN status = 'error' THEN 1 END) as errors,
--        ROUND(COUNT(CASE WHEN status = 'error' THEN 1 END) * 100.0 / COUNT(*), 2) as error_rate
-- FROM llm_interactions
-- GROUP BY provider_name;

-- Get average response time by model
-- SELECT model_name, AVG(response_time_ms) as avg_ms FROM llm_interactions GROUP BY model_name;

-- Get most active users
-- SELECT user_id, COUNT(*) as interaction_count FROM llm_interactions GROUP BY user_id ORDER BY interaction_count DESC LIMIT 10;

-- ============================================================================
-- Notes
-- ============================================================================

-- 1. This schema is designed for SQLite 3.8.3+
-- 2. JSON fields (request_parameters, response_metadata) are stored as TEXT
-- 3. Use JSON1 extension for JSON queries if needed: json_extract(request_parameters, '$.temperature')
-- 4. Timestamps are stored in UTC
-- 5. Consider partitioning for very large datasets (use separate tables by date)
-- 6. For production, implement regular cleanup/archival of old data
-- 7. Monitor index usage and adjust as needed
-- 8. Consider adding full-text search on user_data and llm_response if needed

-- ============================================================================
-- Maintenance Queries
-- ============================================================================

-- Archive old interactions (older than 90 days)
-- INSERT INTO llm_interactions_archive SELECT * FROM llm_interactions
-- WHERE interaction_timestamp < datetime('now', '-90 days');
-- DELETE FROM llm_interactions WHERE interaction_timestamp < datetime('now', '-90 days');

-- Vacuum to reclaim space (run periodically)
-- VACUUM;

-- Analyze tables for query optimization
-- ANALYZE;