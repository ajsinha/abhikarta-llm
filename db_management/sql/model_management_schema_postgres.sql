-- ==================================================================================
-- Abhikarta LLM Model Management Database Schema
-- PostgreSQL Compatible Version
--
-- Copyright © 2025-2030, All Rights Reserved
-- Ashutosh Sinha
-- Email: ajsinha@gmail.com
-- ==================================================================================

-- Providers Table
CREATE TABLE IF NOT EXISTS providers (
    id SERIAL PRIMARY KEY,
    provider TEXT NOT NULL UNIQUE,
    api_version TEXT NOT NULL,
    base_url TEXT,
    notes TEXT,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Models Table
CREATE TABLE IF NOT EXISTS models (
    id SERIAL PRIMARY KEY,
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
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE CASCADE,
    UNIQUE(provider_id, name)
);

-- Model Strengths Table
CREATE TABLE IF NOT EXISTS model_strengths (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL,
    strength TEXT NOT NULL,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
    UNIQUE(model_id, strength)
);

-- Model Capabilities Table
CREATE TABLE IF NOT EXISTS model_capabilities (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL,
    capability_name TEXT NOT NULL,
    capability_value TEXT NOT NULL,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
    UNIQUE(model_id, capability_name)
);

-- Model Cost Table
CREATE TABLE IF NOT EXISTS model_costs (
    id SERIAL PRIMARY KEY,
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
    id SERIAL PRIMARY KEY,
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

-- Trigger to auto-update updated_at timestamp for providers
CREATE OR REPLACE FUNCTION update_providers_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_providers_updated_at
    BEFORE UPDATE ON providers
    FOR EACH ROW
    EXECUTE FUNCTION update_providers_updated_at();

-- Trigger to auto-update updated_at timestamp for models
CREATE OR REPLACE FUNCTION update_models_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_models_updated_at
    BEFORE UPDATE ON models
    FOR EACH ROW
    EXECUTE FUNCTION update_models_updated_at();