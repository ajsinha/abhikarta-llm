-- ============================================================================
-- Abhikarta LLM Platform - MySQL Schema for LLM Interaction Logging
--
-- Copyright © 2025-2030, All Rights Reserved
-- Ashutosh Sinha | Email: ajsinha@gmail.com
-- ============================================================================

-- Set character set for proper text handling
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- ============================================================================
-- Table: llm_interactions
-- Purpose: Log all user interactions with LLM facades
-- ============================================================================

CREATE TABLE IF NOT EXISTS llm_interactions (
    -- Primary Key
    interaction_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    -- User and Session Information
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    chat_session_id VARCHAR(255),  -- The chat session ID (chat_abc123_...)

    -- Interaction Metadata
    interaction_type VARCHAR(50) NOT NULL DEFAULT 'chat',
    interaction_timestamp DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),

    -- LLM Provider Information
    provider_name VARCHAR(100) NOT NULL,
    model_name VARCHAR(100) NOT NULL,

    -- Request Data
    user_data TEXT NOT NULL,  -- User's message/prompt
    request_parameters JSON,   -- JSON parameters (temperature, max_tokens, etc.)

    -- Response Data
    llm_response MEDIUMTEXT NOT NULL,  -- LLM's response (can be long)
    response_metadata JSON,             -- JSON metadata (usage, finish_reason, etc.)

    -- Performance Metrics
    response_time_ms INT UNSIGNED,      -- Response time in milliseconds
    prompt_tokens INT UNSIGNED,         -- Number of tokens in prompt
    completion_tokens INT UNSIGNED,     -- Number of tokens in completion
    total_tokens INT UNSIGNED,          -- Total tokens used

    -- Status and Error Handling
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    error_message TEXT,                 -- Error message if status != success

    -- Additional Metadata
    cached_facade BOOLEAN DEFAULT FALSE,  -- Was cached facade used?
    streaming BOOLEAN DEFAULT FALSE,      -- Was streaming used?
    client_ip VARCHAR(45),                -- Client IP address (IPv4/IPv6)
    user_agent TEXT,                      -- User agent string

    -- Audit Fields
    created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),

    -- Constraints
    CONSTRAINT chk_interaction_type CHECK (interaction_type IN ('chat', 'completion', 'embedding', 'vision', 'audio', 'tool_call')),
    CONSTRAINT chk_status CHECK (status IN ('success', 'error', 'timeout', 'cancelled')),

    -- Indexes defined inline for better organization
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_chat_session_id (chat_session_id),
    INDEX idx_timestamp (interaction_timestamp DESC),
    INDEX idx_user_timestamp (user_id, interaction_timestamp DESC),
    INDEX idx_provider_model (provider_name, model_name),
    INDEX idx_interaction_type (interaction_type),
    INDEX idx_status (status),
    INDEX idx_cached_facade (cached_facade)

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Logs all user interactions with LLM facades';

-- ============================================================================
-- Full-Text Search Index (Optional)
-- ============================================================================

-- Add fulltext index for searching conversation content
-- ALTER TABLE llm_interactions ADD FULLTEXT INDEX idx_fulltext_content (user_data, llm_response);

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
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS successful_interactions,
    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) AS failed_interactions,
    ROUND(AVG(response_time_ms), 2) AS avg_response_time_ms,
    SUM(total_tokens) AS total_tokens_used,
    ROUND(AVG(total_tokens), 2) AS avg_tokens_per_interaction,
    SUM(CASE WHEN cached_facade = TRUE THEN 1 ELSE 0 END) AS cached_facade_count,
    ROUND(SUM(CASE WHEN cached_facade = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS cache_hit_rate
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
    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) AS error_count
FROM llm_interactions
GROUP BY user_id;

-- View: Hourly interaction statistics
CREATE OR REPLACE VIEW v_hourly_interaction_stats AS
SELECT
    DATE_FORMAT(interaction_timestamp, '%Y-%m-%d %H:00:00') AS hour,
    COUNT(*) AS total_interactions,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS successful,
    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) AS errors,
    ROUND(AVG(response_time_ms), 2) AS avg_response_time_ms,
    SUM(total_tokens) AS total_tokens
FROM llm_interactions
GROUP BY DATE_FORMAT(interaction_timestamp, '%Y-%m-%d %H:00:00')
ORDER BY hour DESC;

-- View: Daily statistics
CREATE OR REPLACE VIEW v_daily_interaction_stats AS
SELECT
    DATE(interaction_timestamp) AS day,
    provider_name,
    model_name,
    COUNT(*) AS total_interactions,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS successful,
    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) AS errors,
    ROUND(AVG(response_time_ms), 2) AS avg_response_time_ms,
    SUM(total_tokens) AS total_tokens,
    COUNT(DISTINCT user_id) AS unique_users
FROM llm_interactions
GROUP BY DATE(interaction_timestamp), provider_name, model_name
ORDER BY day DESC;

-- ============================================================================
-- Stored Procedures
-- ============================================================================

DELIMITER //

-- Procedure to archive old interactions
CREATE PROCEDURE archive_old_interactions(IN days_old INT)
BEGIN
    DECLARE rows_affected INT;

    -- Create archive table if not exists
    CREATE TABLE IF NOT EXISTS llm_interactions_archive LIKE llm_interactions;

    -- Start transaction
    START TRANSACTION;

    -- Move old records to archive
    INSERT INTO llm_interactions_archive
    SELECT * FROM llm_interactions
    WHERE interaction_timestamp < DATE_SUB(NOW(), INTERVAL days_old DAY);

    -- Get affected rows
    SET rows_affected = ROW_COUNT();

    -- Delete from main table
    DELETE FROM llm_interactions
    WHERE interaction_timestamp < DATE_SUB(NOW(), INTERVAL days_old DAY);

    -- Commit transaction
    COMMIT;

    -- Return result
    SELECT CONCAT('Archived ', rows_affected, ' rows') AS result;
END //

-- Procedure to get user statistics
CREATE PROCEDURE get_user_stats(IN p_user_id VARCHAR(255))
BEGIN
    SELECT
        user_id,
        COUNT(*) AS total_interactions,
        COUNT(DISTINCT chat_session_id) AS unique_sessions,
        MIN(interaction_timestamp) AS first_interaction,
        MAX(interaction_timestamp) AS last_interaction,
        SUM(total_tokens) AS total_tokens_used,
        ROUND(AVG(response_time_ms), 2) AS avg_response_time_ms,
        SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) AS error_count,
        SUM(CASE WHEN cached_facade = TRUE THEN 1 ELSE 0 END) AS cached_requests
    FROM llm_interactions
    WHERE user_id = p_user_id;
END //

-- Procedure to get session interactions
CREATE PROCEDURE get_session_interactions(IN p_chat_session_id VARCHAR(255))
BEGIN
    SELECT
        interaction_id,
        user_id,
        interaction_timestamp,
        provider_name,
        model_name,
        user_data,
        llm_response,
        response_time_ms,
        total_tokens,
        status
    FROM llm_interactions
    WHERE chat_session_id = p_chat_session_id
    ORDER BY interaction_timestamp;
END //

DELIMITER ;

-- ============================================================================
-- Events for Automatic Maintenance (Optional)
-- ============================================================================

-- Enable event scheduler
-- SET GLOBAL event_scheduler = ON;

-- Event to archive old data monthly
-- CREATE EVENT IF NOT EXISTS archive_monthly
-- ON SCHEDULE EVERY 1 MONTH
-- STARTS CURRENT_TIMESTAMP + INTERVAL 1 MONTH
-- DO CALL archive_old_interactions(90);

-- Event to optimize tables weekly
-- CREATE EVENT IF NOT EXISTS optimize_weekly
-- ON SCHEDULE EVERY 1 WEEK
-- STARTS CURRENT_TIMESTAMP + INTERVAL 1 WEEK
-- DO OPTIMIZE TABLE llm_interactions;

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

-- Query JSON fields (MySQL 5.7+)
-- SELECT user_id, JSON_EXTRACT(request_parameters, '$.temperature') as temperature
-- FROM llm_interactions
-- WHERE JSON_EXTRACT(request_parameters, '$.temperature') IS NOT NULL;

-- Get error rate by provider
-- SELECT provider_name,
--        COUNT(*) as total,
--        SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors,
--        ROUND(SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as error_rate
-- FROM llm_interactions
-- GROUP BY provider_name;

-- Get top users by token usage
-- SELECT user_id, SUM(total_tokens) as total_tokens
-- FROM llm_interactions
-- GROUP BY user_id
-- ORDER BY total_tokens DESC
-- LIMIT 10;

-- Full-text search (if fulltext index created)
-- SELECT * FROM llm_interactions
-- WHERE MATCH(user_data, llm_response) AGAINST('machine learning' IN NATURAL LANGUAGE MODE);

-- ============================================================================
-- Partitioning Setup (for very large datasets - MySQL 8.0+)
-- ============================================================================

-- Example: Partition by range on timestamp (monthly)
/*
ALTER TABLE llm_interactions PARTITION BY RANGE (TO_DAYS(interaction_timestamp)) (
    PARTITION p202511 VALUES LESS THAN (TO_DAYS('2025-12-01')),
    PARTITION p202512 VALUES LESS THAN (TO_DAYS('2026-01-01')),
    PARTITION p202601 VALUES LESS THAN (TO_DAYS('2026-02-01')),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
*/

-- ============================================================================
-- Performance Optimization Tips
-- ============================================================================

-- 1. Use InnoDB engine for ACID compliance and better performance
-- 2. Set appropriate buffer pool size: innodb_buffer_pool_size
-- 3. Use JSON columns for structured metadata
-- 4. Create covering indexes for frequently queried columns
-- 5. Use partitioning for very large tables (> 10M rows)
-- 6. Regularly run OPTIMIZE TABLE to defragment
-- 7. Monitor slow query log and optimize queries
-- 8. Use prepared statements to prevent SQL injection
-- 9. Consider read replicas for analytics queries
-- 10. Use connection pooling for better concurrency

-- ============================================================================
-- Backup Recommendations
-- ============================================================================

-- Regular backups using mysqldump
-- mysqldump -u username -p abhikarta_db llm_interactions > backup.sql

-- Point-in-time recovery with binary logs
-- mysqlbinlog --start-datetime="2025-11-20 00:00:00" binlog.000001 | mysql -u username -p

-- ============================================================================
-- Monitoring Queries
-- ============================================================================

-- Check table size
-- SELECT
--     table_name AS `Table`,
--     ROUND(((data_length + index_length) / 1024 / 1024), 2) AS `Size (MB)`
-- FROM information_schema.TABLES
-- WHERE table_schema = DATABASE()
-- AND table_name = 'llm_interactions';

-- Check index usage
-- SELECT * FROM sys.schema_unused_indexes WHERE object_schema = DATABASE();

-- Check slow queries
-- SELECT * FROM mysql.slow_log ORDER BY query_time DESC LIMIT 10;