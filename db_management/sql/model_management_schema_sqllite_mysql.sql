-- ==================================================================================
-- Abhikarta LLM Model Management Database Schema
-- MySQL Compatible Version
--
-- Copyright © 2025-2030, All Rights Reserved
-- Ashutosh Sinha
-- Email: ajsinha@gmail.com
-- ==================================================================================

-- Providers Table
CREATE TABLE IF NOT EXISTS providers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    provider VARCHAR(255) NOT NULL UNIQUE,
    api_version VARCHAR(50) NOT NULL,
    base_url TEXT,
    notes TEXT,
    enabled TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Models Table
CREATE TABLE IF NOT EXISTS models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    provider_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    model_id VARCHAR(255),
    replicate_model VARCHAR(255),
    context_window INT NOT NULL,
    max_output INT NOT NULL,
    parameters TEXT,
    license VARCHAR(255),
    enabled TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE CASCADE,
    UNIQUE KEY unique_provider_model (provider_id, name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Model Strengths Table
CREATE TABLE IF NOT EXISTS model_strengths (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_id INT NOT NULL,
    strength VARCHAR(255) NOT NULL,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
    UNIQUE KEY unique_model_strength (model_id, strength)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Model Capabilities Table
CREATE TABLE IF NOT EXISTS model_capabilities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_id INT NOT NULL,
    capability_name VARCHAR(255) NOT NULL,
    capability_value TEXT NOT NULL,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
    UNIQUE KEY unique_model_capability (model_id, capability_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Model Cost Table
CREATE TABLE IF NOT EXISTS model_costs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_id INT NOT NULL UNIQUE,
    input_per_1k DOUBLE,
    output_per_1k DOUBLE,
    input_per_1m DOUBLE,
    output_per_1m DOUBLE,
    input_per_1m_0_128k DOUBLE,
    input_per_1m_128k_plus DOUBLE,
    cost_json TEXT,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Model Performance Table
CREATE TABLE IF NOT EXISTS model_performance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_id INT NOT NULL UNIQUE,
    performance_json TEXT,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Indexes for performance
CREATE INDEX idx_models_provider_id ON models(provider_id);
CREATE INDEX idx_models_enabled ON models(enabled);
CREATE INDEX idx_models_name ON models(name);
CREATE INDEX idx_providers_provider ON providers(provider);
CREATE INDEX idx_providers_enabled ON providers(enabled);
CREATE INDEX idx_model_capabilities_name ON model_capabilities(capability_name);
CREATE INDEX idx_model_strengths_strength ON model_strengths(strength);