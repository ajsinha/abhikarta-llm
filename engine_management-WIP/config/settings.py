"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


import os
from pathlib import Path

class Settings:
    """Global settings for execution system"""
    
    # Database
    DATABASE_PATH = os.getenv("ABHIKARTA_DB_PATH", "llm_execution.db")
    
    # LLM Defaults
    DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "anthropic")
    DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "claude-sonnet-4-20250514")
    DEFAULT_CONTEXT_WINDOW = int(os.getenv("DEFAULT_CONTEXT_WINDOW", "10"))
    
    # Execution
    MAX_REACT_ITERATIONS = int(os.getenv("MAX_REACT_ITERATIONS", "10"))
    MAX_AUTONOMOUS_ITERATIONS = int(os.getenv("MAX_AUTONOMOUS_ITERATIONS", "20"))
    
    # Background Jobs
    BACKGROUND_JOB_POLL_INTERVAL = int(os.getenv("BG_JOB_POLL_INTERVAL", "5"))
    MAX_JOB_RETRIES = int(os.getenv("MAX_JOB_RETRIES", "3"))
    
    # HITL
    APPROVAL_TIMEOUT_SECONDS = int(os.getenv("APPROVAL_TIMEOUT", "300"))
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
    
    # Vector Store
    DEFAULT_VECTOR_STORE = os.getenv("DEFAULT_VECTOR_STORE", "chromadb")
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./vector_store")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "llm_execution.log")
