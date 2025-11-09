-- ==================================================================================
-- Abhikarta LLM Model Management Database Schema
-- SQLite Compatible Version
--
-- Copyright © 2025-2030, All Rights Reserved
-- Ashutosh Sinha
-- Email: ajsinha@gmail.com
-- ==================================================================================

-- Providers Table
CREATE TABLE IF NOT EXISTS providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL UNIQUE,
    api_version TEXT NOT NULL,
    base_url TEXT,
    notes TEXT,
    enabled BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Models Table
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    description TEXT NOT NULL,
    model_id TEXT,
    replicate_model TEXT,
    context_window INTEGER NOT NULL,
    max_output INTEGER NOT NULL,
    parameters TEXT,
    license TEXT,
    enabled BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE CASCADE,
    UNIQUE(provider_id, name)
);

-- Model Strengths Table
CREATE TABLE IF NOT EXISTS model_strengths (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    strength TEXT NOT NULL,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
    UNIQUE(model_id, strength)
);

-- Model Capabilities Table
CREATE TABLE IF NOT EXISTS model_capabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    capability_name TEXT NOT NULL,
    capability_value TEXT NOT NULL,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
    UNIQUE(model_id, capability_name)
);

-- Model Cost Table
CREATE TABLE IF NOT EXISTS model_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL UNIQUE,
    input_per_1k REAL,
    output_per_1k REAL,
    input_per_1m REAL,
    output_per_1m REAL,
    input_per_1m_0_128k REAL,
    input_per_1m_128k_plus REAL,
    cost_json TEXT,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

-- Model Performance Table
CREATE TABLE IF NOT EXISTS model_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL UNIQUE,
    performance_json TEXT,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_models_provider_id ON models(provider_id);
CREATE INDEX IF NOT EXISTS idx_models_enabled ON models(enabled);
CREATE INDEX IF NOT EXISTS idx_models_name ON models(name);
CREATE INDEX IF NOT EXISTS idx_providers_provider ON providers(provider);
CREATE INDEX IF NOT EXISTS idx_providers_enabled ON providers(enabled);
CREATE INDEX IF NOT EXISTS idx_model_capabilities_name ON model_capabilities(capability_name);
CREATE INDEX IF NOT EXISTS idx_model_strengths_strength ON model_strengths(strength);

-- Triggers to auto-update updated_at timestamp for providers
CREATE TRIGGER IF NOT EXISTS trigger_update_providers_updated_at
    AFTER UPDATE ON providers
    FOR EACH ROW
BEGIN
    UPDATE providers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Triggers to auto-update updated_at timestamp for models
CREATE TRIGGER IF NOT EXISTS trigger_update_models_updated_at
    AFTER UPDATE ON models
    FOR EACH ROW
BEGIN
    UPDATE models SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;