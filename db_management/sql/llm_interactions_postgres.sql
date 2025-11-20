-- ============================================================================
-- Abhikarta LLM Platform - PostgreSQL Schema for LLM Interaction Logging
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
    interaction_id BIGSERIAL PRIMARY KEY,

    -- User and Session Information
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    chat_session_id VARCHAR(255),  -- The chat session ID (chat_abc123_...)

    -- Interaction Metadata
    interaction_type VARCHAR(50) NOT NULL DEFAULT 'chat',
    interaction_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- LLM Provider Information
    provider_name VARCHAR(100) NOT NULL,
    model_name VARCHAR(100) NOT NULL,

    -- Request Data
    user_data TEXT NOT NULL,  -- User's message/prompt
    request_parameters JSONB,  -- JSON parameters (temperature, max_tokens, etc.)

    -- Response Data
    llm_response TEXT NOT NULL,  -- LLM's response
    response_metadata JSONB,      -- JSON metadata (usage, finish_reason, etc.)

    -- Performance Metrics
    response_time_ms INTEGER,     -- Response time in milliseconds
    prompt_tokens INTEGER,         -- Number of tokens in prompt
    completion_tokens INTEGER,     -- Number of tokens in completion
    total_tokens INTEGER,          -- Total tokens used

    -- Status and Error Handling
    status VARCHAR(20) NOT NULL DEFAULT 'success',  -- success, error, timeout
    error_message TEXT,            -- Error message if status != success

    -- Additional Metadata
    cached_facade BOOLEAN DEFAULT FALSE,  -- Was cached facade used?
    streaming BOOLEAN DEFAULT FALSE,      -- Was streaming used?
    client_ip INET,                       -- Client IP address
    user_agent TEXT,                      -- User agent string

    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_interaction_type CHECK (interaction_type IN ('chat', 'completion', 'embedding', 'vision', 'audio', 'tool_call')),
    CONSTRAINT chk_status CHECK (status IN ('success', 'error', 'timeout', 'cancelled')),
    CONSTRAINT chk_response_time CHECK (response_time_ms >= 0),
    CONSTRAINT chk_tokens CHECK (prompt_tokens >= 0 AND completion_tokens >= 0 AND total_tokens >= 0)
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Index on user_id for user-specific queries
CREATE INDEX idx_llm_interactions_user_id ON llm_interactions(user_id);

-- Index on session_id for session-specific queries
CREATE INDEX idx_llm_interactions_session_id ON llm_interactions(session_id);

-- Index on chat_session_id for chat session queries
CREATE INDEX idx_llm_interactions_chat_session_id ON llm_interactions(chat_session_id);

-- Index on timestamp for time-based queries (most recent first)
CREATE INDEX idx_llm_interactions_timestamp ON llm_interactions(interaction_timestamp DESC);

-- Composite index for user + timestamp (common query pattern)
CREATE INDEX idx_llm_interactions_user_timestamp ON llm_interactions(user_id, interaction_timestamp DESC);

-- Index on provider and model for analytics
CREATE INDEX idx_llm_interactions_provider_model ON llm_interactions(provider_name, model_name);

-- Index on interaction type
CREATE INDEX idx_llm_interactions_type ON llm_interactions(interaction_type);

-- Index on status for error tracking
CREATE INDEX idx_llm_interactions_status ON llm_interactions(status);

-- Partial index for errors only (more efficient for error queries)
CREATE INDEX idx_llm_interactions_errors ON llm_interactions(interaction_timestamp DESC)
WHERE status = 'error';

-- GIN index on JSONB columns for fast JSON queries
CREATE INDEX idx_llm_interactions_request_params ON llm_interactions USING GIN(request_parameters);
CREATE INDEX idx_llm_interactions_response_meta ON llm_interactions USING GIN(response_metadata);

-- Full-text search index (optional, for searching conversation content)
-- CREATE INDEX idx_llm_interactions_fulltext ON llm_interactions USING GIN(to_tsvector('english', user_data || ' ' || llm_response));

-- ============================================================================
-- Trigger for Auto-Update of updated_at
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_llm_interactions_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to call the function
DROP TRIGGER IF EXISTS trigger_llm_interactions_updated_at ON llm_interactions;
CREATE TRIGGER trigger_llm_interactions_updated_at
    BEFORE UPDATE ON llm_interactions
    FOR EACH ROW
    EXECUTE FUNCTION update_llm_interactions_timestamp();

-- ============================================================================
-- Views for Common Queries
-- ============================================================================

-- View: Recent interactions by user
CREATE OR REPLACE VIEW v_recent_user_interactions AS
SELECT
    interaction_id,
    user_id,
    session_id,
    chat_session_id,
    interaction_type,
    interaction_timestamp,
    provider_name,
    model_name,
    LEFT(user_data, 100) AS user_data_preview,
    LEFT(llm_response, 100) AS response_preview,
    response_time_ms,
    total_tokens,
    status,
    cached_facade
FROM llm_interactions
ORDER BY interaction_timestamp DESC;

-- View: Interaction statistics by provider/model
CREATE OR REPLACE VIEW v_provider_model_stats AS
SELECT
    provider_name,
    model_name,
    COUNT(*) AS total_interactions,
    COUNT(*) FILTER (WHERE status = 'success') AS successful_interactions,
    COUNT(*) FILTER (WHERE status = 'error') AS failed_interactions,
    ROUND(AVG(response_time_ms), 2) AS avg_response_time_ms,
    SUM(total_tokens) AS total_tokens_used,
    ROUND(AVG(total_tokens), 2) AS avg_tokens_per_interaction,
    COUNT(*) FILTER (WHERE cached_facade = TRUE) AS cached_facade_count,
    ROUND(COUNT(*) FILTER (WHERE cached_facade = TRUE) * 100.0 / COUNT(*), 2) AS cache_hit_rate
FROM llm_interactions
GROUP BY provider_name, model_name;

-- View: User activity summary
CREATE OR REPLACE VIEW v_user_activity_summary AS
SELECT
    user_id,
    COUNT(*) AS total_interactions,
    COUNT(DISTINCT chat_session_id) AS unique_sessions,
    MIN(interaction_timestamp) AS first_interaction,
    MAX(interaction_timestamp) AS last_interaction,
    SUM(total_tokens) AS total_tokens_used,
    ROUND(AVG(response_time_ms), 2) AS avg_response_time_ms,
    COUNT(*) FILTER (WHERE status = 'error') AS error_count
FROM llm_interactions
GROUP BY user_id;

-- View: Hourly interaction statistics
CREATE OR REPLACE VIEW v_hourly_interaction_stats AS
SELECT
    DATE_TRUNC('hour', interaction_timestamp) AS hour,
    COUNT(*) AS total_interactions,
    COUNT(*) FILTER (WHERE status = 'success') AS successful,
    COUNT(*) FILTER (WHERE status = 'error') AS errors,
    ROUND(AVG(response_time_ms), 2) AS avg_response_time_ms,
    SUM(total_tokens) AS total_tokens
FROM llm_interactions
GROUP BY DATE_TRUNC('hour', interaction_timestamp)
ORDER BY hour DESC;

-- ============================================================================
-- Materialized Views for Performance (Optional)
-- ============================================================================

-- Materialized view for daily statistics (refresh periodically)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_interaction_stats AS
SELECT
    DATE_TRUNC('day', interaction_timestamp) AS day,
    provider_name,
    model_name,
    COUNT(*) AS total_interactions,
    COUNT(*) FILTER (WHERE status = 'success') AS successful,
    COUNT(*) FILTER (WHERE status = 'error') AS errors,
    ROUND(AVG(response_time_ms), 2) AS avg_response_time_ms,
    SUM(total_tokens) AS total_tokens,
    COUNT(DISTINCT user_id) AS unique_users
FROM llm_interactions
GROUP BY DATE_TRUNC('day', interaction_timestamp), provider_name, model_name
ORDER BY day DESC;

-- Index on materialized view
CREATE INDEX idx_mv_daily_stats_day ON mv_daily_interaction_stats(day DESC);

-- Function to refresh materialized view (call this periodically, e.g., via cron)
-- SELECT refresh_daily_stats();
CREATE OR REPLACE FUNCTION refresh_daily_stats()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_interaction_stats;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Partitioning Setup (for very large datasets)
-- ============================================================================

-- Example: Partition by month
-- ALTER TABLE llm_interactions PARTITION BY RANGE (interaction_timestamp);
-- CREATE TABLE llm_interactions_2025_11 PARTITION OF llm_interactions
-- FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

-- ============================================================================
-- Sample Queries
-- ============================================================================

-- Get all interactions for a specific user (with pagination)
-- SELECT * FROM llm_interactions
-- WHERE user_id = 'user@example.com'
-- ORDER BY interaction_timestamp DESC
-- LIMIT 50 OFFSET 0;

-- Get interactions for a specific chat session
-- SELECT * FROM llm_interactions
-- WHERE chat_session_id = 'chat_abc123_1700000000'
-- ORDER BY interaction_timestamp;

-- Query JSON fields
-- SELECT user_id, request_parameters->>'temperature' as temperature
-- FROM llm_interactions
-- WHERE request_parameters->>'temperature' IS NOT NULL;

-- Get error rate by provider
-- SELECT provider_name,
--        COUNT(*) as total,
--        COUNT(*) FILTER (WHERE status = 'error') as errors,
--        ROUND(COUNT(*) FILTER (WHERE status = 'error') * 100.0 / COUNT(*), 2) as error_rate
-- FROM llm_interactions
-- GROUP BY provider_name;

-- Get top users by token usage
-- SELECT user_id, SUM(total_tokens) as total_tokens
-- FROM llm_interactions
-- GROUP BY user_id
-- ORDER BY total_tokens DESC
-- LIMIT 10;

-- Full-text search (if index created)
-- SELECT * FROM llm_interactions
-- WHERE to_tsvector('english', user_data || ' ' || llm_response) @@ to_tsquery('machine & learning');

-- ============================================================================
-- Maintenance Functions
-- ============================================================================

-- Archive old interactions (older than 90 days)
CREATE OR REPLACE FUNCTION archive_old_interactions(days_old INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    rows_archived INTEGER;
BEGIN
    -- Create archive table if not exists
    CREATE TABLE IF NOT EXISTS llm_interactions_archive (LIKE llm_interactions INCLUDING ALL);

    -- Move old records to archive
    WITH moved AS (
        DELETE FROM llm_interactions
        WHERE interaction_timestamp < CURRENT_TIMESTAMP - (days_old || ' days')::INTERVAL
        RETURNING *
    )
    INSERT INTO llm_interactions_archive
    SELECT * FROM moved;

    GET DIAGNOSTICS rows_archived = ROW_COUNT;
    RETURN rows_archived;
END;
$$ LANGUAGE plpgsql;

-- Clean up old sessions (optional)
-- SELECT archive_old_interactions(90);

-- Vacuum and analyze (run periodically)
-- VACUUM ANALYZE llm_interactions;

-- ============================================================================
-- Row-Level Security (Optional)
-- ============================================================================

-- Enable RLS
-- ALTER TABLE llm_interactions ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own interactions
-- CREATE POLICY user_isolation ON llm_interactions
-- FOR SELECT
-- USING (user_id = current_setting('app.current_user_id'));

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE llm_interactions IS 'Logs all user interactions with LLM facades';
COMMENT ON COLUMN llm_interactions.interaction_id IS 'Unique identifier for each interaction';
COMMENT ON COLUMN llm_interactions.user_id IS 'User who initiated the interaction';
COMMENT ON COLUMN llm_interactions.chat_session_id IS 'Chat session identifier from facade cache';
COMMENT ON COLUMN llm_interactions.request_parameters IS 'JSON parameters like temperature, max_tokens';
COMMENT ON COLUMN llm_interactions.response_metadata IS 'JSON metadata including usage statistics';
COMMENT ON COLUMN llm_interactions.cached_facade IS 'Whether a cached facade was used';

-- ============================================================================
-- Performance Tips
-- ============================================================================

-- 1. Use JSONB instead of JSON for better query performance
-- 2. Create partial indexes for frequently filtered conditions
-- 3. Use materialized views for complex aggregations
-- 4. Consider partitioning for tables with millions of rows
-- 5. Regularly vacuum and analyze tables
-- 6. Monitor slow queries and add indexes as needed
-- 7. Use connection pooling for better performance
-- 8. Consider read replicas for analytics queries