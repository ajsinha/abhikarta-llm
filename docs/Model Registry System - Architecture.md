# Model Registry System - Architecture

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha** | ajsinha@gmail.com

---

## Legal Notice

This document and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use of this document or the software system it describes is strictly prohibited without explicit written permission from the copyright holder.

This document is provided "as is" without warranty of any kind, either expressed or implied. The copyright holder shall not be liable for any damages arising from the use of this document or the software system it describes.

**Patent Pending**: Certain architectural patterns and implementations described in this document may be subject to patent applications.

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Installation & Setup](#installation--setup)
5. [Thread Safety Model](#thread-safety-model)
6. [Auto-Reload System](#auto-reload-system)
7. [Exception Handling](#exception-handling)
8. [Configuration Format](#configuration-format)
9. [Usage Examples](#usage-examples)
10. [API Reference](#api-reference)
11. [Features Checklist](#features-checklist)
12. [Performance Considerations](#performance-considerations)
13. [Best Practices](#best-practices)
14. [Troubleshooting](#troubleshooting)

---

## Overview

The Model Registry is a comprehensive, thread-safe singleton system for managing LLM model providers and their configurations. It provides:

- **Singleton Pattern**: Single global instance ensuring consistent state
- **Thread-Safe Operations**: All methods protected with RLock for concurrent access
- **Auto-Reload**: Background thread automatically reloads configurations at configurable intervals
- **Change Detection**: Only reloads providers when JSON files are added, modified, or removed
- **Exception Handling**: Custom exceptions for disabled providers/models
- **Cross-Provider Search**: Find cheapest models across all providers
- **Comprehensive API**: Rich set of convenience methods for model discovery

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          ModelRegistry (Singleton)                      │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Thread-Safe Operations (RLock)                                   │  │
│  │  • _lock: threading.RLock                                         │  │
│  │  • _providers: Dict[str, ModelProvider]                           │  │
│  │  • _file_hashes: Dict[str, str] (MD5 change detection)            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Auto-Reload System                                               │  │
│  │  • _auto_reload_thread: Background daemon thread                  │  │
│  │  • _auto_reload_interval: Configurable (default: 10 min)          │  │
│  │  • _stop_auto_reload: Event for graceful shutdown                 │  │
│  │  • Monitors: New files, Modified files, Deleted files             │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Public API Methods                                               │  │
│  │  ├─ get_all_providers()                                           │  │
│  │  ├─ get_provider_by_name(name)                                    │  │
│  │  ├─ get_model_from_provider_by_name(provider, model)              │  │
│  │  ├─ get_model_from_provider_by_name_capability(p, m, cap)         │  │
│  │  ├─ get_cheapest_model_for_capability(capability)                 │  │
│  │  ├─ get_cheapest_model_for_provider_and_capability(p, cap)        │  │
│  │  ├─ get_all_models_for_capability(capability)                     │  │
│  │  ├─ start_auto_reload(interval)                                   │  │
│  │  └─ stop_auto_reload()                                            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ manages multiple
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                          ModelProvider (Thread-Safe)                    │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Thread-Safe Operations (RLock)                                   │  │
│  │  • _lock: threading.RLock                                         │  │
│  │  • _enabled: bool (with property decorators)                      │  │
│  │  • models: List[Model]                                            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Provider Configuration                                           │  │
│  │  • provider: str (e.g., "anthropic", "google")                    │  │
│  │  • api_version: str                                               │  │
│  │  • base_url: str                                                  │  │
│  │  • notes: Dict[str, str]                                          │  │
│  │  • config_path: Path                                              │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Methods                                                          │  │
│  │  • get_model_by_name(name)                                        │  │
│  │  • get_cheapest_model_for_capability(capability)                  │  │
│  │  • get_models_for_capability(capability)                          │  │
│  │  • enable_model(name) / disable_model(name)                       │  │
│  │  • reload() - Reloads configuration from JSON                     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ contains multiple
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                              Model (Thread-Safe)                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Thread-Safe Operations (RLock)                                   │  │
│  │  • _lock: threading.RLock                                         │  │
│  │  • _enabled: bool (with property decorators)                      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Model Configuration                                              │  │
│  │  • name: str                                                      │  │
│  │  • version: str                                                   │  │
│  │  • description: str                                               │  │
│  │  • context_window: int                                            │  │
│  │  • max_output: int                                                │  │
│  │  • capabilities: Dict[str, Any]                                   │  │
│  │  • cost: Dict[str, Any]                                           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Methods                                                          │  │
│  │  • has_capability(capability) -> bool                             │  │
│  │  • has_all_capabilities(capabilities) -> bool                     │  │
│  │  • calculate_cost(input_tokens, output_tokens) -> float           │  │
│  │  • to_dict() -> Dict                                              │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### File System Interaction

```
Configuration Directory (/path/to/config/)
│
├── anthropic.json  ──┐
├── google.json     ──┤
├── mistral.json    ──┼─→ Monitored by Auto-Reload Thread
├── cohere.json     ──┤    • Checks every N seconds (default: 600)
├── groq.json       ──┤    • Calculates MD5 hash
└── huggingface.json ─┘    • Detects: New, Modified, Deleted
                           │
                           ├─→ New file detected
                           │   └─→ Load provider, add to registry
                           │
                           ├─→ File modified (hash changed)
                           │   └─→ Reload provider, update registry
                           │
                           └─→ File deleted
                               └─→ Remove provider from registry
```

---

## Core Components

### 1. model_management.py (from __init__.py)

Provides foundational enums and types:

- **ModelCapability**: Enum of all LLM capabilities (100+ values)
  - Core: chat, completion, streaming
  - Multimodal: vision, audio, video
  - Tools: function_calling, web_search, grounding
  - Optimization: caching, batch_api
  - And many more...

- **ProviderType**: Enum of supported providers
  - ANTHROPIC, OPENAI, GOOGLE, MISTRAL, COHERE, GROQ, HUGGINGFACE, etc.

### 2. exceptions.py

Custom exception classes for clear error handling:

- **ModelRegistryException**: Base exception class
- **ProviderNotFoundException**: Provider not found in registry
- **ProviderDisabledException**: Provider exists but is disabled
- **ModelNotFoundException**: Model not found in provider
- **ModelDisabledException**: Model exists but is disabled
- **NoModelsAvailableException**: No models match criteria
- **ConfigurationError**: Configuration file parsing error

### 3. model_provider.py (Thread-Safe)

Core classes for provider and model management:

- **Model**: Represents individual LLM models
  - Thread-safe with RLock
  - Capability checking
  - Cost calculation
  - Enable/disable state management

- **ModelProvider**: Manages models from a single provider
  - Thread-safe with RLock
  - JSON configuration loading
  - Model filtering by capability
  - Cost-based model selection
  - Property decorators for thread-safe enabled status

### 4. model_registry.py (Main Component)

The singleton registry managing all providers:

- **ModelRegistry**: Thread-safe singleton
  - Manages multiple ModelProvider instances
  - Auto-reload capability with background thread
  - MD5-based change detection
  - Cross-provider search and comparison
  - Comprehensive convenience methods

---

## Installation & Setup

### File Structure

```
project/
├── model_management.py      # Capability and provider enums
├── exceptions.py             # Custom exception classes
├── model_provider.py         # Thread-safe provider classes
├── model_registry.py         # Main registry singleton
├── test_model_registry.py    # Comprehensive test suite
└── config/                   # Configuration directory
    ├── anthropic.json
    ├── google.json
    ├── mistral.json
    ├── cohere.json
    ├── groq.json
    └── huggingface.json
```

### Dependencies

```python
# Standard library only - no external dependencies required
import json
import os
import threading
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
```

---

## Thread Safety Model

### Thread Safety Architecture

```
Multiple Threads
    │
    ├─→ Thread 1 ──┐
    ├─→ Thread 2 ──┤
    ├─→ Thread 3 ──┼─→ All call registry.get_cheapest_model_for_capability()
    ├─→ Thread 4 ──┤
    └─→ Thread 5 ──┘
                │
                ↓
        [ModelRegistry._lock]
                │
                ├─→ Thread acquires lock
                │   ├─→ Accesses _providers dict
                │   ├─→ Calls ModelProvider methods
                │   │       │
                │   │       ↓
                │   │   [ModelProvider._lock]
                │   │       │
                │   │       ├─→ Accesses models list
                │   │       ├─→ Reads capabilities
                │   │       └─→ Calculates costs
                │   │
                │   └─→ Returns result
                │
                └─→ Lock released, next thread proceeds

All operations are serialized through locks, ensuring:
• No race conditions
• Consistent state
• Safe concurrent access
```

### Implementation Details

#### ModelRegistry - Singleton Thread Safety

```python
class ModelRegistry:
    _instance: Optional['ModelRegistry'] = None
    _instance_lock = threading.RLock()  # Class-level lock for singleton
    
    def __init__(self, config_directory: str, auto_reload_interval: int = 600):
        # Thread safety
        self._lock = threading.RLock()  # Instance-level lock for operations
        
        # Provider storage
        self._providers: Dict[str, ModelProvider] = {}
        
        # File tracking
        self._file_hashes: Dict[str, str] = {}
        
        # ... initialization
    
    @classmethod
    def get_instance(cls, config_directory: str = None) -> 'ModelRegistry':
        """Thread-safe singleton instance creation."""
        with cls._instance_lock:
            if cls._instance is None:
                if config_directory is None:
                    raise ValueError("config_directory required on first call")
                cls._instance = cls(config_directory)
            return cls._instance
    
    def get_all_providers(self) -> Dict[str, ModelProvider]:
        """Thread-safe provider retrieval."""
        with self._lock:
            return {
                name: provider
                for name, provider in self._providers.items()
                if provider.enabled
            }
```

#### ModelProvider - Thread-Safe Operations

```python
class ModelProvider:
    def __init__(self, config_path: str, enabled: bool = True):
        # Thread safety lock - must be created first
        self._lock = threading.RLock()
        
        self.config_path = Path(config_path)
        self._enabled = enabled
        self._load_config()
    
    @property
    def enabled(self) -> bool:
        """Thread-safe getter for enabled status."""
        with self._lock:
            return self._enabled
    
    @enabled.setter
    def enabled(self, value: bool):
        """Thread-safe setter for enabled status."""
        with self._lock:
            self._enabled = value
    
    def _load_config(self) -> None:
        """Thread-safe configuration loading."""
        with self._lock:
            # Load and parse JSON
            # Create Model instances
            # Store in self.models
```

#### Model - Thread-Safe State Management

```python
class Model:
    def __init__(self, config: Dict[str, Any], enabled: bool = True):
        # Thread safety lock
        self._lock = threading.RLock()
        
        # Load configuration
        self.name = config['name']
        self.version = config['version']
        # ... other fields
        
        # State
        self._enabled = enabled
    
    @property
    def enabled(self) -> bool:
        """Thread-safe getter for enabled status."""
        with self._lock:
            return self._enabled
    
    @enabled.setter
    def enabled(self, value: bool):
        """Thread-safe setter for enabled status."""
        with self._lock:
            self._enabled = value
```

### Thread Safety Testing

All operations are thread-safe and tested with concurrent access:

```python
import threading

def worker(thread_id):
    registry = ModelRegistry.get_instance()
    
    # All these operations are thread-safe
    providers = registry.get_all_providers()
    model = registry.get_model_from_provider_by_name("google", "gemini-1.5-pro")
    provider, model, cost = registry.get_cheapest_model_for_capability("chat")

# Create multiple threads
threads = []
for i in range(10):
    thread = threading.Thread(target=worker, args=(i,))
    threads.append(thread)
    thread.start()

# Wait for completion
for thread in threads:
    thread.join()
```

---

## Auto-Reload System

### Auto-Reload Architecture

The auto-reload system continuously monitors the configuration directory for changes and automatically updates the registry.

### Auto-Reload Sequence Diagram

```
Main Thread                     Auto-Reload Thread (Daemon)
    │                                   │
    │ start_auto_reload()               │
    ├────────────────────────────────→  │
    │                                   │ Start loop
    │                                   │
    │                                   ├─→ Wait(interval seconds)
    │                                   │
    │                                   ├─→ Scan config directory
    │                                   │       │
    │                                   │       ├─→ Get all *.json files
    │                                   │       │
    │                                   │       ├─→ Calculate MD5 hashes
    │                                   │       │
    │                                   │       ├─→ Compare with previous
    │                                   │       │
    │                                   │       ├─→ New file?
    │                                   │       │   └─→ Load provider
    │                                   │       │
    │                                   │       ├─→ Modified file?
    │                                   │       │   └─→ Reload provider
    │                                   │       │
    │                                   │       └─→ Deleted file?
    │                                   │           └─→ Remove provider
    │                                   │
    │                                   └─→ Loop continues...
    │                                   
    │ stop_auto_reload()                │
    ├────────────────────────────────→  │
    │                                   │ Set stop flag
    │                                   │
    │                                   └─→ Thread exits
    │                                   
    │ Application continues...
    │
```

### Change Detection Implementation

#### MD5 Hash Calculation

```python
def _calculate_file_hash(self, file_path: Path) -> str:
    """
    Calculate MD5 hash of a file to detect changes.
    
    Args:
        file_path: Path to the file
    
    Returns:
        MD5 hash as hex string
    """
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()
```

#### Reload Logic

```python
def _load_all_providers(self) -> None:
    """
    Load all provider configurations from JSON files.
    
    This method:
    - Scans for all .json files
    - Loads new providers
    - Updates modified providers
    - Removes providers for deleted files
    """
    with self._lock:
        json_files = set(self._config_dir.glob("*.json"))
        current_files = {f.stem: f for f in json_files}
        
        # Track which providers to remove
        providers_to_remove = set(self._providers.keys()) - set(current_files.keys())
        
        # Remove providers for deleted files
        for provider_name in providers_to_remove:
            print(f"Removing provider '{provider_name}' (file deleted)")
            del self._providers[provider_name]
            if provider_name in self._file_hashes:
                del self._file_hashes[provider_name]
        
        # Load or update providers
        for file_stem, file_path in current_files.items():
            try:
                # Calculate file hash
                current_hash = self._calculate_file_hash(file_path)
                previous_hash = self._file_hashes.get(file_stem)
                
                # Only load/reload if file is new or changed
                if previous_hash is None:
                    # New file
                    print(f"Loading new provider from: {file_path.name}")
                    provider = ModelProvider(str(file_path))
                    self._providers[provider.provider] = provider
                    self._file_hashes[file_stem] = current_hash
                elif current_hash != previous_hash:
                    # File changed
                    print(f"Reloading modified provider from: {file_path.name}")
                    provider = ModelProvider(str(file_path))
                    self._providers[provider.provider] = provider
                    self._file_hashes[file_stem] = current_hash
                # else: file unchanged, skip reload
                
            except Exception as e:
                print(f"Error loading provider from {file_path.name}: {e}")
```

### Auto-Reload Control Methods

#### Starting Auto-Reload

```python
def start_auto_reload(self, interval_seconds: Optional[int] = None) -> None:
    """
    Start the auto-reload background thread.
    
    Args:
        interval_seconds: Reload interval in seconds (uses configured value if None)
    
    Example:
        >>> registry.start_auto_reload(600)  # Reload every 10 minutes
    """
    with self._lock:
        if self._auto_reload_enabled:
            print("Auto-reload is already running")
            return
        
        if interval_seconds is not None:
            self._auto_reload_interval = interval_seconds
        
        self._stop_auto_reload.clear()
        self._auto_reload_thread = threading.Thread(
            target=self._auto_reload_worker,
            daemon=True,
            name="ModelRegistry-AutoReload"
        )
        self._auto_reload_enabled = True
        self._auto_reload_thread.start()
        print(f"Auto-reload started with interval: {self._auto_reload_interval} seconds")
```

#### Stopping Auto-Reload

```python
def stop_auto_reload(self) -> None:
    """
    Stop the auto-reload background thread.
    
    Example:
        >>> registry.stop_auto_reload()
    """
    with self._lock:
        if not self._auto_reload_enabled:
            return
        
        self._stop_auto_reload.set()
        self._auto_reload_enabled = False
        
        if self._auto_reload_thread and self._auto_reload_thread.is_alive():
            self._auto_reload_thread.join(timeout=5)
        
        print("Auto-reload stopped")
```

### Auto-Reload Behavior

The auto-reload system:

1. **Tracks File Changes**: Uses MD5 hashing to detect modifications
2. **Adds New Providers**: Automatically loads new JSON files
3. **Removes Old Providers**: Removes providers when JSON files are deleted
4. **Updates Changed Providers**: Reloads only modified files
5. **Preserves Unchanged**: Skips files that haven't changed (efficiency)
6. **Runs in Background**: Daemon thread doesn't block application exit
7. **Configurable Interval**: Default 10 minutes, customizable
8. **Graceful Shutdown**: Proper cleanup on stop

---

## Exception Handling

### Exception Hierarchy

```
Exception
    │
    └─→ ModelRegistryException (base)
            │
            ├─→ ProviderNotFoundException
            │       Raised when: provider not in registry
            │
            ├─→ ProviderDisabledException
            │       Raised when: provider.enabled == False
            │
            ├─→ ModelNotFoundException
            │       Raised when: model not found in provider
            │
            ├─→ ModelDisabledException
            │       Raised when: model.enabled == False
            │
            ├─→ NoModelsAvailableException
            │       Raised when: no models match criteria
            │
            └─→ ConfigurationError
                    Raised when: JSON parsing/validation fails
```

### Exception Usage

```python
from exceptions import (
    ModelRegistryException,         # Base exception
    ProviderNotFoundException,      # Provider not found
    ProviderDisabledException,      # Provider disabled
    ModelNotFoundException,         # Model not found
    ModelDisabledException,         # Model disabled
    NoModelsAvailableException,     # No models match criteria
    ConfigurationError              # Configuration file error
)

try:
    model = registry.get_model_from_provider_by_name("anthropic", "claude-opus-4")
except ProviderNotFoundException:
    print("Provider 'anthropic' not found")
except ProviderDisabledException:
    print("Provider 'anthropic' is disabled")
except ModelNotFoundException:
    print("Model 'claude-opus-4' not found")
except ModelDisabledException:
    print("Model 'claude-opus-4' is disabled")
except ModelRegistryException as e:
    print(f"Registry error: {e}")
```

---

## Configuration Format

### JSON Configuration Structure

Each provider is defined in a JSON file with the following structure:

```json
{
  "provider": "string",          // Required: Provider identifier
  "api_version": "string",       // Required: API version
  "base_url": "string",          // Optional: Base URL for API
  "notes": {},                   // Optional: Provider documentation
  "models": [                    // Required: Array of models
    {
      "name": "string",          // Required: Model identifier
      "version": "string",       // Required: Model version
      "description": "string",   // Required: Human-readable description
      "context_window": int,     // Required: Maximum input tokens
      "max_output": int,         // Required: Maximum output tokens
      "cost": {                  // Required: Pricing structure
        "input_per_1m": float,   // Cost per 1M input tokens
        "output_per_1m": float   // Cost per 1M output tokens
      },
      "capabilities": {          // Required: Feature flags
        "chat": bool,            // Supports chat
        "vision": bool,          // Supports vision
        "function_calling": bool, // Supports function calling
        "streaming": bool        // Supports streaming
        // ... more capabilities
      },
      "provider": "string",      // Optional: Original provider
      "model_id": "string",      // Optional: API model ID
      "strengths": ["string"],   // Optional: Key strengths
      "parameters": "string",    // Optional: Model size (e.g., "70B")
      "license": "string"        // Optional: License information
    }
  ]
}
```

### Example Configuration File

**anthropic.json**:
```json
{
  "provider": "anthropic",
  "api_version": "2023-06-01",
  "base_url": "https://api.anthropic.com",
  "notes": {
    "authentication": "API key required",
    "rate_limits": "Varies by tier"
  },
  "models": [
    {
      "name": "claude-opus-4",
      "version": "4.0",
      "description": "Most capable Claude model with extended context",
      "context_window": 200000,
      "max_output": 16384,
      "cost": {
        "input_per_1m": 15.0,
        "output_per_1m": 75.0
      },
      "capabilities": {
        "chat": true,
        "completion": false,
        "streaming": true,
        "function_calling": true,
        "vision": true,
        "prompt_caching": true
      },
      "strengths": ["reasoning", "analysis", "long-context", "multimodal"],
      "parameters": "Unknown"
    },
    {
      "name": "claude-sonnet-4",
      "version": "4.0",
      "description": "Balanced model for everyday tasks",
      "context_window": 200000,
      "max_output": 16384,
      "cost": {
        "input_per_1m": 3.0,
        "output_per_1m": 15.0
      },
      "capabilities": {
        "chat": true,
        "completion": false,
        "streaming": true,
        "function_calling": true,
        "vision": true,
        "prompt_caching": true
      },
      "strengths": ["speed", "efficiency", "versatility"],
      "parameters": "Unknown"
    }
  ]
}
```

---

## Usage Examples

### Basic Initialization

```python
from model_registry import ModelRegistry

# First initialization (required config directory)
registry = ModelRegistry.get_instance("/path/to/config")

# Subsequent access (no parameters needed)
registry = ModelRegistry.get_instance()
```

### Start Auto-Reload

```python
# Start auto-reload with 10-minute interval (default: 600 seconds)
registry.start_auto_reload(interval_seconds=600)

# The registry will automatically:
# - Detect new JSON files and load them
# - Detect modified JSON files and reload them
# - Detect removed JSON files and remove providers
# - Only reload changed files (uses MD5 hash tracking)

# Stop auto-reload when done
registry.stop_auto_reload()
```

### Get All Providers

```python
# Get only enabled providers
providers = registry.get_all_providers()

for name, provider in providers.items():
    print(f"{name}: {provider.get_model_count()} models")

# Include disabled providers
all_providers = registry.get_all_providers(include_disabled=True)
```

### Get Specific Provider

```python
from exceptions import ProviderNotFoundException, ProviderDisabledException

try:
    provider = registry.get_provider_by_name("anthropic")
    print(f"Found: {provider}")
    print(f"API Version: {provider.api_version}")
    print(f"Models: {provider.get_model_count()}")
except ProviderNotFoundException as e:
    print(f"Provider not found: {e}")
except ProviderDisabledException as e:
    print(f"Provider disabled: {e}")
```

### Get Model from Provider

```python
from exceptions import ModelNotFoundException, ModelDisabledException

# Get model by name
try:
    model = registry.get_model_from_provider_by_name(
        "anthropic",
        "claude-opus-4"
    )
    print(f"Model: {model.name}")
    print(f"Context window: {model.context_window:,}")
    print(f"Description: {model.description}")
except (ModelNotFoundException, ModelDisabledException) as e:
    print(f"Error: {e}")

# Get model with specific capability
try:
    model = registry.get_model_from_provider_by_name_capability(
        "google",
        "gemini-1.5-pro",
        "vision"
    )
    print(f"Found vision-capable model: {model.name}")
    print(f"Has vision: {model.has_capability('vision')}")
except ModelNotFoundException as e:
    print(f"Model not found or doesn't have capability: {e}")
```

### Find Cheapest Model Across All Providers

```python
from exceptions import NoModelsAvailableException

# Find cheapest model across ALL providers
try:
    provider_name, model, cost = registry.get_cheapest_model_for_capability(
        capability="chat",
        input_tokens=1_000_000,
        output_tokens=10_000
    )
    print(f"Cheapest chat model: {provider_name}/{model.name}")
    print(f"Cost for 1M input + 10K output: ${cost:.4f}")
except NoModelsAvailableException as e:
    print(f"No models available: {e}")
```

### Find Cheapest Model Within Provider

```python
# Find cheapest model within specific provider
try:
    model, cost = registry.get_cheapest_model_for_provider_and_capability(
        provider_name="anthropic",
        capability="vision",
        input_tokens=500_000,
        output_tokens=5_000
    )
    print(f"Cheapest Anthropic vision model: {model.name}")
    print(f"Cost for 500K input + 5K output: ${cost:.4f}")
except NoModelsAvailableException as e:
    print(f"No models available: {e}")
```

### Search Across Providers

```python
# Get all models with a capability across all providers
models = registry.get_all_models_for_capability("vision")

print(f"Found {len(models)} vision-capable models:")
for provider_name, model in models:
    cost = model.calculate_cost(100000, 1000)
    print(f"  {provider_name}/{model.name}: ${cost:.4f}")
```

### Registry Summary

```python
summary = registry.get_registry_summary()

print(f"Configuration Directory: {summary['config_directory']}")
print(f"Enabled Providers: {summary['provider_count']}")
print(f"Total Providers: {summary['total_provider_count']}")
print(f"Total Models: {summary['total_model_count']}")
print(f"Auto-reload: {summary['auto_reload_enabled']}")
print(f"Auto-reload Interval: {summary['auto_reload_interval']} seconds")

print("\nProvider Details:")
for provider in summary['providers']:
    status = "✓" if provider['enabled'] else "✗"
    print(f"  {status} {provider['name']}: {provider['model_count']} models")
```

### Data Flow: Finding Cheapest Model

```
User Request
    │
    └─→ registry.get_cheapest_model_for_capability("vision")
            │
            ├─→ Acquire registry._lock
            │
            ├─→ Call get_all_models_for_capability("vision")
            │       │
            │       ├─→ Get all enabled providers
            │       │
            │       └─→ For each provider:
            │               ├─→ Acquire provider._lock
            │               ├─→ Get models with "vision" capability
            │               ├─→ Release provider._lock
            │               └─→ Collect (provider_name, model) tuples
            │
            ├─→ Calculate cost for each model
            │       │
            │       └─→ For each (provider_name, model):
            │               ├─→ Acquire model._lock
            │               ├─→ Call model.calculate_cost()
            │               ├─→ Release model._lock
            │               └─→ Store (cost, provider_name, model)
            │
            ├─→ Sort by cost
            │
            ├─→ Return (provider_name, model, cost)
            │
            └─→ Release registry._lock
```

---

## API Reference

### ModelRegistry Class

#### Singleton Access

```python
@classmethod
def get_instance(cls, config_directory: str = None, auto_reload_interval: int = 600) -> 'ModelRegistry'
```
Get the singleton instance of ModelRegistry.

**Parameters:**
- `config_directory`: Directory containing JSON configuration files (required on first call)
- `auto_reload_interval`: Auto-reload interval in seconds (default: 600)

**Returns:** The singleton ModelRegistry instance

**Raises:** `ValueError` if config_directory is None on first call

---

#### Provider Access Methods

```python
def get_all_providers(self, include_disabled: bool = False) -> Dict[str, ModelProvider]
```
Get all providers in the registry.

**Parameters:**
- `include_disabled`: Whether to include disabled providers (default: False)

**Returns:** Dictionary mapping provider names to ModelProvider instances

---

```python
def get_provider_by_name(self, provider_name: str) -> ModelProvider
```
Get a provider by name.

**Parameters:**
- `provider_name`: Name of the provider

**Returns:** ModelProvider instance

**Raises:**
- `ProviderNotFoundException`: If provider not found
- `ProviderDisabledException`: If provider is disabled

---

#### Model Access Methods

```python
def get_model_from_provider_by_name(self, provider_name: str, model_name: str) -> Model
```
Get a specific model from a specific provider.

**Parameters:**
- `provider_name`: Name of the provider
- `model_name`: Name of the model

**Returns:** Model instance

**Raises:**
- `ProviderNotFoundException`: If provider not found
- `ProviderDisabledException`: If provider is disabled
- `ModelNotFoundException`: If model not found
- `ModelDisabledException`: If model is disabled

---

```python
def get_model_from_provider_by_name_capability(
    self,
    provider_name: str,
    model_name: str,
    capability: str
) -> Model
```
Get a model from a provider only if it has a specific capability.

**Parameters:**
- `provider_name`: Name of the provider
- `model_name`: Name of the model
- `capability`: Required capability

**Returns:** Model instance

**Raises:**
- `ProviderNotFoundException`: If provider not found
- `ProviderDisabledException`: If provider is disabled
- `ModelNotFoundException`: If model not found or doesn't have capability
- `ModelDisabledException`: If model is disabled

---

#### Cross-Provider Search Methods

```python
def get_all_models_for_capability(
    self,
    capability: str,
    include_disabled_providers: bool = False
) -> List[Tuple[str, Model]]
```
Get all models across all providers that support a capability.

**Parameters:**
- `capability`: Required capability
- `include_disabled_providers`: Whether to include disabled providers

**Returns:** List of tuples (provider_name, Model instance)

---

```python
def get_cheapest_model_for_capability(
    self,
    capability: str,
    input_tokens: int = 100000,
    output_tokens: int = 1000
) -> Tuple[str, Model, float]
```
Find the cheapest model across all providers for a given capability.

**Parameters:**
- `capability`: Required capability
- `input_tokens`: Number of input tokens for cost calculation (default: 100000)
- `output_tokens`: Number of output tokens for cost calculation (default: 1000)

**Returns:** Tuple of (provider_name, Model instance, cost)

**Raises:** `NoModelsAvailableException` if no models support the capability

---

```python
def get_cheapest_model_for_provider_and_capability(
    self,
    provider_name: str,
    capability: str,
    input_tokens: int = 100000,
    output_tokens: int = 1000
) -> Tuple[Model, float]
```
Find the cheapest model from a specific provider for a given capability.

**Parameters:**
- `provider_name`: Name of the provider
- `capability`: Required capability
- `input_tokens`: Number of input tokens for cost calculation (default: 100000)
- `output_tokens`: Number of output tokens for cost calculation (default: 1000)

**Returns:** Tuple of (Model instance, cost)

**Raises:**
- `ProviderNotFoundException`: If provider not found
- `ProviderDisabledException`: If provider is disabled
- `NoModelsAvailableException`: If no models support the capability

---

#### Auto-Reload Methods

```python
def start_auto_reload(self, interval_seconds: Optional[int] = None) -> None
```
Start the auto-reload background thread.

**Parameters:**
- `interval_seconds`: Reload interval in seconds (uses configured value if None)

---

```python
def stop_auto_reload(self) -> None
```
Stop the auto-reload background thread.

---

```python
def reload_all_providers(self) -> int
```
Manually trigger a reload of all provider configurations.

**Returns:** Number of providers currently loaded

---

#### Utility Methods

```python
def get_provider_count(self, include_disabled: bool = False) -> int
```
Get the count of providers in the registry.

**Parameters:**
- `include_disabled`: Whether to include disabled providers

**Returns:** Number of providers

---

```python
def get_total_model_count(self, include_disabled: bool = False) -> int
```
Get the total count of models across all providers.

**Parameters:**
- `include_disabled`: Whether to include disabled models/providers

**Returns:** Total number of models

---

```python
def get_registry_summary(self) -> Dict[str, Any]
```
Get a summary of the registry state.

**Returns:** Dictionary with registry statistics including:
- provider_count
- total_provider_count
- total_model_count
- auto_reload_enabled
- auto_reload_interval
- config_directory
- providers (list of provider info)

---

### ModelProvider Class

```python
def get_model_by_name(self, model_name: str) -> Optional[Model]
```
Get a model by its name.

**Parameters:**
- `model_name`: The name of the model to retrieve

**Returns:** Model instance if found and enabled, None otherwise

---

```python
def get_cheapest_model_for_capability(
    self,
    capability: str,
    input_tokens: int = 100000,
    output_tokens: int = 1000
) -> Optional[Model]
```
Find the cheapest model in this provider for a given capability.

---

```python
def get_models_for_capability(self, capability: str) -> List[Model]
```
Get all models that support a specific capability.

---

### Model Class

```python
def has_capability(self, capability: str) -> bool
```
Check if the model has a specific capability.

---

```python
def has_all_capabilities(self, capabilities: List[str]) -> bool
```
Check if the model has all specified capabilities.

---

```python
def calculate_cost(self, input_tokens: int, output_tokens: int) -> float
```
Calculate the cost for a given number of input and output tokens.

**Returns:** Total cost in USD

---

## Features Checklist

### Core Features
- ✅ Singleton pattern implementation
- ✅ Thread-safe operations with RLock
- ✅ Auto-reload at configurable intervals (default: 10 minutes)
- ✅ File change detection via MD5 hashing
- ✅ Automatic provider addition/removal/update
- ✅ Only reloads changed files for efficiency

### API Methods
- ✅ `get_all_providers()` method
- ✅ `get_provider_by_name()` method
- ✅ `get_model_from_provider_by_name()` method
- ✅ `get_model_from_provider_by_name_capability()` method
- ✅ `get_cheapest_model_for_capability()` method
- ✅ `get_cheapest_model_for_provider_and_capability()` method
- ✅ `get_all_models_for_capability()` method
- ✅ `start_auto_reload()` and `stop_auto_reload()` methods
- ✅ `reload_all_providers()` method
- ✅ `get_registry_summary()` method

### Exception Handling
- ✅ Custom exceptions for disabled providers/models
- ✅ ProviderNotFoundException
- ✅ ProviderDisabledException
- ✅ ModelNotFoundException
- ✅ ModelDisabledException
- ✅ NoModelsAvailableException
- ✅ ConfigurationError

### Advanced Features
- ✅ Cross-provider model search
- ✅ Cost-based model selection
- ✅ Capability-based filtering
- ✅ Provider and model enable/disable support
- ✅ Comprehensive test suite
- ✅ Full documentation with examples

### Legal & Copyright
- ✅ Copyright notice (© 2025-2030, Ashutosh Sinha)
- ✅ Legal disclaimer
- ✅ Patent pending notice
- ✅ Proprietary and confidential notice

---

## Performance Considerations

### Optimization Strategies

1. **Change Detection**
   - Only reloads modified files (O(1) hash comparison)
   - Skips unchanged files entirely
   - MD5 hashing is fast for typical config files (<1ms)

2. **Thread Safety**
   - RLock overhead is minimal for read operations
   - Lock contention is low due to short critical sections
   - Property decorators add negligible overhead

3. **Memory Efficiency**
   - Stores only hash of files, not full content
   - Providers and models use shared string interning
   - Dictionaries for O(1) provider lookup

4. **Lazy Loading**
   - Providers loaded on-demand during initialization
   - Models created only when needed
   - Configuration parsed once per file

5. **Background Thread**
   - Auto-reload runs in daemon thread
   - Doesn't block main application
   - Configurable interval balances freshness vs overhead

### Performance Metrics

For typical usage:
- **Provider lookup**: O(1) dictionary access
- **Model lookup**: O(n) linear search within provider (typically <100 models)
- **Capability filtering**: O(n×m) where n=models, m=providers
- **Cost calculation**: O(n) for n candidate models
- **File reload**: ~1-10ms per JSON file depending on size
- **Hash calculation**: <1ms per file for typical config sizes

---

## Best Practices

### 1. Initialize Once at Startup

```python
# Good: Initialize at application startup
registry = ModelRegistry.get_instance("/path/to/config")
registry.start_auto_reload()

# Bad: Creating new instances repeatedly (violates singleton)
# Don't do this!
for i in range(10):
    registry = ModelRegistry("/path/to/config")  # Wrong!
```

### 2. Enable Auto-Reload for Production

```python
# Good: Enable auto-reload for production systems
registry = ModelRegistry.get_instance("/path/to/config")
registry.start_auto_reload(interval_seconds=600)  # 10 minutes

# Consider: Stop auto-reload during shutdown
import atexit
atexit.register(registry.stop_auto_reload)
```

### 3. Always Handle Exceptions

```python
# Good: Proper exception handling
try:
    model = registry.get_model_from_provider_by_name("anthropic", "claude-opus-4")
except ProviderDisabledException:
    # Handle disabled provider
    logger.warning("Provider disabled, using fallback")
    model = get_fallback_model()
except ModelNotFoundException:
    # Handle missing model
    logger.error("Model not found")
    raise

# Bad: Ignoring exceptions
model = registry.get_model_from_provider_by_name("anthropic", "claude-opus-4")  # May fail!
```

### 4. Use Capability-Based Selection

```python
# Good: Let registry find best model for capability
provider, model, cost = registry.get_cheapest_model_for_capability("vision")

# Good: Filter by specific requirements
models = registry.get_all_models_for_capability("function_calling")
suitable_models = [m for _, m in models if m.context_window >= 100000]

# Bad: Hard-coding model names
model = registry.get_model_from_provider_by_name("anthropic", "claude-opus-4")  # Brittle!
```

### 5. Validate Configuration Files

```python
# Good: Test configurations before deployment
import json
from pathlib import Path

def validate_config(config_path):
    """Validate a configuration file."""
    with open(config_path) as f:
        config = json.load(f)
    
    required_fields = ['provider', 'api_version', 'models']
    for field in required_fields:
        assert field in config, f"Missing required field: {field}"
    
    for model in config['models']:
        assert 'name' in model
        assert 'cost' in model
        assert 'capabilities' in model

# Validate before deploying
for config_file in Path("/path/to/config").glob("*.json"):
    validate_config(config_file)
```

### 6. Monitor Logs

```python
# Good: Implement proper logging
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# The registry already prints to stdout, but you can capture:
# - "Loading new provider from: ..."
# - "Reloading modified provider from: ..."
# - "Removing provider '...' (file deleted)"
# - "Auto-reload started with interval: ..."

# Consider redirecting stdout to logger for production
```

### 7. Test Before Production

```python
# Good: Use reset_instance() for testing
def test_registry():
    # Reset singleton for clean test
    ModelRegistry.reset_instance()
    
    # Create test instance
    registry = ModelRegistry.get_instance("/test/config")
    
    # Run tests
    assert registry.get_provider_count() > 0
    
    # Cleanup
    ModelRegistry.reset_instance()
```

### 8. Graceful Shutdown

```python
# Good: Proper shutdown sequence
import signal
import sys

def shutdown_handler(signum, frame):
    logger.info("Shutting down...")
    registry.stop_auto_reload()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)
```

### 9. Use Context Managers (Optional)

```python
# Good: Wrap in context manager for automatic cleanup
class RegistryContext:
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.registry = None
    
    def __enter__(self):
        self.registry = ModelRegistry.get_instance(self.config_dir)
        self.registry.start_auto_reload()
        return self.registry
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.registry.stop_auto_reload()

# Usage
with RegistryContext("/path/to/config") as registry:
    # Use registry
    model = registry.get_cheapest_model_for_capability("chat")
# Auto-reload stopped automatically
```

### 10. Cache Expensive Queries

```python
# Good: Cache frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cheapest_vision_model():
    """Cached lookup for cheapest vision model."""
    provider, model, cost = registry.get_cheapest_model_for_capability("vision")
    return (provider, model.name, cost)

# Invalidate cache after reload if needed
def on_reload():
    get_cheapest_vision_model.cache_clear()
```

---

## Troubleshooting

### Problem: Provider not loading

**Symptoms:**
- Provider missing from `get_all_providers()`
- ProviderNotFoundException raised

**Solutions:**
1. Check JSON syntax with a validator
2. Ensure required fields present:
   - `provider` (string)
   - `api_version` (string)
   - `models` (array)
3. Check file permissions (must be readable)
4. Verify file has `.json` extension
5. Check console for error messages during load

**Debug:**
```python
# Manual load to see detailed error
from model_provider import ModelProvider
try:
    provider = ModelProvider("/path/to/config/provider.json")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

---

### Problem: Models showing as disabled

**Symptoms:**
- ModelDisabledException raised
- Models not appearing in searches

**Solutions:**
1. Check `enabled` field in Model configuration (should be true or absent)
2. Check provider `enabled` status
3. Enable programmatically:
   ```python
   provider = registry.get_provider_by_name("anthropic")
   provider.enable_model("claude-opus-4")
   ```

**Debug:**
```python
# Check model status
provider = registry.get_provider_by_name("anthropic")
models = provider.get_all_models(include_disabled=True)
for model in models:
    print(f"{model.name}: enabled={model.enabled}")
```

---

### Problem: Auto-reload not working

**Symptoms:**
- File changes not detected
- Providers not updating

**Solutions:**
1. Verify `start_auto_reload()` was called
2. Check file permissions (must be readable)
3. Ensure interval has elapsed (default: 10 minutes)
4. Check console for reload messages
5. Verify files are actually changing (MD5 hash different)

**Debug:**
```python
# Check auto-reload status
summary = registry.get_registry_summary()
print(f"Auto-reload enabled: {summary['auto_reload_enabled']}")
print(f"Interval: {summary['auto_reload_interval']} seconds")

# Manual reload to test
count = registry.reload_all_providers()
print(f"Loaded {count} providers")
```

---

### Problem: Thread safety issues

**Symptoms:**
- Race conditions
- Inconsistent data
- Deadlocks

**Solutions:**
1. Verify using latest version (all methods are thread-safe)
2. Don't access internal `_` prefixed attributes directly
3. Use property decorators for `enabled` attributes
4. Report as bug - all operations should be thread-safe

**Debug:**
```python
# Test thread safety
import threading

def worker():
    for i in range(100):
        providers = registry.get_all_providers()
        model = registry.get_cheapest_model_for_capability("chat")

threads = [threading.Thread(target=worker) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("Thread safety test passed")
```

---

### Problem: High memory usage

**Symptoms:**
- Memory growing over time
- Out of memory errors

**Solutions:**
1. Check for memory leaks in application code
2. Registry itself is memory-efficient
3. Stop auto-reload if not needed
4. Consider reducing number of providers/models

**Debug:**
```python
import sys

# Check registry size
summary = registry.get_registry_summary()
print(f"Providers: {summary['total_provider_count']}")
print(f"Models: {summary['total_model_count']}")

# Rough memory estimate
print(f"Registry object size: {sys.getsizeof(registry)} bytes")
```

---

### Problem: Slow performance

**Symptoms:**
- Long query times
- High CPU usage

**Solutions:**
1. Cache expensive queries (see Best Practices)
2. Reduce auto-reload frequency
3. Filter results early
4. Use provider-specific queries when possible

**Debug:**
```python
import time

# Measure query performance
start = time.time()
provider, model, cost = registry.get_cheapest_model_for_capability("vision")
elapsed = time.time() - start
print(f"Query took {elapsed*1000:.2f}ms")

# Should be <100ms for typical configurations
```

---

### Problem: Configuration errors

**Symptoms:**
- ConfigurationError raised
- JSON parsing failures

**Solutions:**
1. Validate JSON syntax with `json.loads()`
2. Check required fields exist
3. Verify data types (int for tokens, float for costs)
4. Check for duplicate provider names

**Debug:**
```python
import json
from pathlib import Path

# Validate all configs
config_dir = Path("/path/to/config")
for json_file in config_dir.glob("*.json"):
    try:
        with open(json_file) as f:
            config = json.load(f)
        print(f"✓ {json_file.name} is valid")
    except Exception as e:
        print(f"✗ {json_file.name}: {e}")
```

---

### Problem: Cannot find cheapest model

**Symptoms:**
- NoModelsAvailableException raised
- Empty results from search

**Solutions:**
1. Verify models exist with required capability
2. Check models are enabled
3. Check providers are enabled
4. Verify capability string matches exactly

**Debug:**
```python
# Check what models exist for capability
models = registry.get_all_models_for_capability("vision")
print(f"Found {len(models)} vision models")
for provider, model in models:
    print(f"  {provider}/{model.name}")

# If empty, check capabilities
all_providers = registry.get_all_providers(include_disabled=True)
for name, provider in all_providers.items():
    for model in provider.get_all_models(include_disabled=True):
        print(f"{name}/{model.name}: {list(model.capabilities.keys())}")
```

---

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha** | ajsinha@gmail.com