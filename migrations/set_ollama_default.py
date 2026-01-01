#!/usr/bin/env python3
"""
Migration Script: Set Ollama as Default Provider
Version: 1.4.6

This script:
1. Adds Ollama provider if not exists
2. Adds llama3.2:3b model if not exists
3. Sets Ollama as the default provider
4. Sets llama3.2:3b as the default model

Run from project root: python migrations/set_ollama_default.py
"""

import sqlite3
import uuid
from datetime import datetime

# Configuration - update this path if needed
DATABASE_PATH = 'abhikarta.db'
OLLAMA_HOST = 'http://192.168.2.36:11434'

def run_migration(db_path: str = DATABASE_PATH):
    """Run the migration."""
    print(f"Running migration on: {db_path}")
    print(f"Ollama host: {OLLAMA_HOST}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if llm_providers table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='llm_providers'
        """)
        if not cursor.fetchone():
            print("Warning: llm_providers table does not exist. Schema may need to be created first.")
            return False
        
        # 1. Reset all providers to non-default
        cursor.execute("UPDATE llm_providers SET is_default = 0")
        print("Reset all providers to non-default")
        
        # 2. Check if Ollama provider exists
        cursor.execute("SELECT provider_id FROM llm_providers WHERE provider_type = 'ollama'")
        ollama_row = cursor.fetchone()
        
        if ollama_row:
            provider_id = ollama_row[0]
            # Update existing Ollama provider - set both api_endpoint and config
            config_json = f'{{"base_url": "{OLLAMA_HOST}"}}'
            cursor.execute("""
                UPDATE llm_providers 
                SET is_default = 1, 
                    is_active = 1,
                    api_endpoint = ?,
                    config = ?,
                    updated_at = ?
                WHERE provider_id = ?
            """, (OLLAMA_HOST, config_json, datetime.utcnow().isoformat(), provider_id))
            print(f"Updated existing Ollama provider: {provider_id}")
            print(f"  - api_endpoint: {OLLAMA_HOST}")
            print(f"  - config: {config_json}")
        else:
            # Insert new Ollama provider
            provider_id = f"ollama_{str(uuid.uuid4())[:8]}"
            cursor.execute("""
                INSERT INTO llm_providers (
                    provider_id, name, description, provider_type,
                    api_endpoint, is_active, is_default, config,
                    created_at, updated_at, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                provider_id,
                'Ollama',
                'Local Ollama LLM provider',
                'ollama',
                OLLAMA_HOST,
                1,  # is_active
                1,  # is_default
                '{"host": "' + OLLAMA_HOST + '"}',
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat(),
                'system'
            ))
            print(f"Created new Ollama provider: {provider_id}")
        
        # 3. Check if llm_models table exists and add llama3.2:3b
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='llm_models'
        """)
        if cursor.fetchone():
            # Reset all models to non-default
            cursor.execute("UPDATE llm_models SET is_default = 0")
            
            # Check if llama3.2:3b model exists
            cursor.execute("""
                SELECT model_id FROM llm_models 
                WHERE model_id = 'llama3.2:3b' OR name = 'llama3.2:3b'
            """)
            model_row = cursor.fetchone()
            
            if model_row:
                model_id = model_row[0]
                cursor.execute("""
                    UPDATE llm_models 
                    SET is_default = 1, is_active = 1, updated_at = ?
                    WHERE model_id = ?
                """, (datetime.utcnow().isoformat(), model_id))
                print(f"Updated existing llama3.2:3b model: {model_id}")
            else:
                # Insert new model
                model_id = f"llama32_3b_{str(uuid.uuid4())[:8]}"
                cursor.execute("""
                    INSERT INTO llm_models (
                        model_id, provider_id, model_name, display_name,
                        description, is_active, is_default, context_length,
                        created_at, updated_at, created_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    model_id,
                    provider_id,
                    'llama3.2:3b',
                    'Llama 3.2 (3B)',
                    'Meta Llama 3.2 3B parameter model',
                    1,  # is_active
                    1,  # is_default
                    8192,  # context_length
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat(),
                    'system'
                ))
                print(f"Created new llama3.2:3b model: {model_id}")
        else:
            print("Warning: llm_models table does not exist")
        
        conn.commit()
        print("\n✓ Migration completed successfully!")
        print(f"  - Default provider: Ollama")
        print(f"  - Default model: llama3.2:3b")
        print(f"  - Ollama host: {OLLAMA_HOST}")
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else DATABASE_PATH
    
    success = run_migration(db_path)
    sys.exit(0 if success else 1)
