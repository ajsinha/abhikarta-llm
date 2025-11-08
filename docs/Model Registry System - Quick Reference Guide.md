# Model Registry System - Quick Reference Guide

**Abhikarta LLM Model Management System v2.1**

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email:** ajsinha@gmail.com

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Basic Usage](#basic-usage)
5. [Database Implementation](#database-implementation)
6. [JSON Implementation](#json-implementation)
7. [Common Operations](#common-operations)
8. [API Reference](#api-reference)
9. [Code Examples](#code-examples)
10. [Deployment Guide](#deployment-guide)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)
13. [Performance Tuning](#performance-tuning)
14. [Migration Guide](#migration-guide)

---

## Quick Start

### 30-Second Start

**Option 1: Database (Recommended for Production)**
```python
from model_registry_db import ModelRegistryDB

# Initialize
registry = ModelRegistryDB.get_instance(db_path="./models.db")

# Import JSON configs (one-time)
registry.load_json_directory("./json_configs")

# Use it
provider, model, cost = registry.get_cheapest_model_for_capability("chat")
print(f"{provider}/{model.name}: ${cost:.4f}")
```

**Option 2: JSON (Recommended for Development)**
```python
from model_registry_json import ModelRegistryJSON

# Initialize with auto-reload
registry = ModelRegistryJSON.get_instance("./json_configs")
registry.start_auto_reload(interval_seconds=300)

# Use it
provider, model, cost = registry.get_cheapest_model_for_capability("vision")
print(f"{provider}/{model.name}: ${cost:.4f}")
```

### Which One Should I Use?

| Use Case | Recommended |
|----------|-------------|
| Production | Database (`ModelRegistryDB`) |
| Development | JSON (`ModelRegistryJSON`) |
| High volume (100+ models) | Database |
| Simple setup (<50 models) | JSON |
| Need auto-reload | JSON |
| Need complex queries | Database |

---

## Installation

### Requirements

- Python 3.8+
- No external dependencies (uses standard library only)

### File Structure

```
your_project/
├── model_provider.py              # Abstract base class
├── model_registry.py              # Abstract base class
├── model_provider_db.py           # Database implementation
├── model_registry_db.py           # Database implementation
├── model_provider_json.py         # JSON implementation
├── model_registry_json.py         # JSON implementation
├── model_management_db_handler.py # Database handler
├── model_management.py            # Enums and constants
├── exceptions.py                  # Exception classes
└── json_configs/                  # JSON configuration files
    ├── anthropic.json
    ├── openai.json
    └── google.json
```

### Setup Steps

1. **Copy Files**
   ```bash
   # Copy all Python files to your project directory
   cp *.py /path/to/your/project/
   ```

2. **Create Config Directory**
   ```bash
   mkdir -p /path/to/your/project/json_configs
   ```

3. **Add JSON Configurations**
   ```bash
   # Copy your provider JSON files
   cp provider_configs/*.json /path/to/your/project/json_configs/
   ```

4. **Initialize (Database Only)**
   ```python
   from model_registry_db import ModelRegistryDB
   
   registry = ModelRegistryDB.get_instance(db_path="./models.db")
   registry.load_json_directory("./json_configs")
   ```

---

## Configuration

### JSON Configuration Format

Each provider has a JSON configuration file:

```json
{
  "provider": "anthropic",
  "api_version": "2023-06-01",
  "base_url": "https://api.anthropic.com",
  "notes": {
    "description": "Anthropic's Claude models"
  },
  "models": [
    {
      "name": "claude-opus-4",
      "version": "4.0",
      "description": "Most capable Claude model",
      "model_id": "claude-opus-4-20250514",
      "context_window": 200000,
      "max_output": 16384,
      "parameters": "Unknown",
      "license": "Proprietary",
      "strengths": [
        "Complex reasoning",
        "Long context",
        "Multimodal"
      ],
      "capabilities": {
        "chat": true,
        "vision": true,
        "function_calling": true,
        "streaming": true,
        "json_mode": true
      },
      "cost": {
        "input_per_1m": 15.0,
        "output_per_1m": 75.0
      },
      "performance": {
        "mmlu": 0.887,
        "gsm8k": 0.956
      },
      "enabled": true
    }
  ]
}
```

### Model Capabilities

Standard capabilities defined in `ModelCapability` enum:

```python
from model_management import ModelCapability

# Text capabilities
ModelCapability.CHAT              # Chat/completion
ModelCapability.INSTRUCT          # Instruction following
ModelCapability.CODE              # Code generation
ModelCapability.RETRIEVAL         # RAG/retrieval

# Multimodal
ModelCapability.VISION            # Image understanding
ModelCapability.IMAGE_GEN         # Image generation
ModelCapability.AUDIO             # Audio processing

# Advanced features
ModelCapability.FUNCTION_CALLING  # Tool use
ModelCapability.JSON_MODE         # Structured output
ModelCapability.STREAMING         # Streaming responses
ModelCapability.EMBEDDINGS        # Text embeddings

# Context sizes
ModelCapability.LONG_CONTEXT      # >100k tokens
ModelCapability.EXTENDED_CONTEXT  # >32k tokens
```

---

## Basic Usage

### Initializing the Registry

**Database Implementation:**
```python
from model_registry_db import ModelRegistryDB

# First time - provide path
registry = ModelRegistryDB.get_instance(db_path="./models.db")

# Subsequent calls - path not needed
registry = ModelRegistryDB.get_instance()

# Reset (testing only)
ModelRegistryDB.reset_instance()
```

**JSON Implementation:**
```python
from model_registry_json import ModelRegistryJSON

# First time - provide directory
registry = ModelRegistryJSON.get_instance("./json_configs")

# Subsequent calls - directory not needed
registry = ModelRegistryJSON.get_instance()

# Reset (testing only)
ModelRegistryJSON.reset_instance()
```

### Getting Providers

```python
# Get specific provider
provider = registry.get_provider_by_name("anthropic")
print(f"Provider: {provider.provider}")
print(f"Models: {provider.get_model_count()}")

# Get all providers
providers = registry.get_all_providers()
for name, provider in providers.items():
    print(f"{name}: {provider.get_model_count()} models")

# Include disabled providers
all_providers = registry.get_all_providers(include_disabled=True)
```

### Getting Models

```python
# Get specific model from provider
model = registry.get_model_from_provider_by_name(
    "anthropic",
    "claude-opus-4"
)
print(f"Model: {model.name}")
print(f"Context: {model.context_window} tokens")

# Get all models from provider
models = registry.get_all_models_from_provider("anthropic")
for model in models:
    print(f"- {model.name}")

# Get models by capability (all providers)
vision_models = registry.get_all_models_for_capability("vision")
for provider_name, model in vision_models:
    print(f"{provider_name}/{model.name}")
```

### Cost Optimization

```python
from model_management import ModelCapability

# Find cheapest model globally
provider_name, model, cost = registry.get_cheapest_model_for_capability(
    ModelCapability.CHAT.value,
    input_tokens=100000,
    output_tokens=1000
)
print(f"Cheapest: {provider_name}/{model.name}")
print(f"Cost for 100k input, 1k output: ${cost:.4f}")

# Find cheapest model from specific provider
model, cost = registry.get_cheapest_model_for_provider_and_capability(
    "anthropic",
    ModelCapability.VISION.value,
    input_tokens=5000,
    output_tokens=500
)
print(f"Cheapest Anthropic vision model: {model.name}")
print(f"Cost: ${cost:.4f}")
```

### Enable/Disable

```python
# Enable/disable provider
registry.enable_provider("anthropic")
registry.disable_provider("mock")

# Enable/disable specific model
registry.enable_model("anthropic", "claude-opus-4")
registry.disable_model("anthropic", "claude-instant-1.2")

# Check status
provider = registry.get_provider_by_name("anthropic")
print(f"Provider enabled: {provider.enabled}")

model = provider.get_model_by_name("claude-opus-4")
print(f"Model enabled: {model.enabled}")
```

---

## Database Implementation

### Initialization

```python
from model_registry_db import ModelRegistryDB

# Initialize with database
registry = ModelRegistryDB.get_instance(db_path="./models.db")

# Import JSON configurations (one-time)
loaded = registry.load_json_directory("./json_configs")
print(f"Loaded {len(loaded)} providers")

# Or import single file
provider_name = registry.load_json_file("./json_configs/anthropic.json")
print(f"Loaded provider: {provider_name}")
```

### Database Operations

```python
# Get database handler for advanced operations
db_handler = registry.get_database_handler()

# Get statistics
stats = db_handler.get_statistics()
print(f"Total providers: {stats['total_providers']}")
print(f"Enabled providers: {stats['enabled_providers']}")
print(f"Total models: {stats['total_models']}")

# Direct database queries (advanced)
providers = db_handler.get_all_providers()
models = db_handler.get_models_by_provider("anthropic")
```

### Reloading Data

```python
# Reload all providers from database
registry.reload_from_storage()

# Reload specific provider
provider = registry.get_provider_by_name("anthropic")
provider.reload()
```

### Database File Management

```python
import shutil
from pathlib import Path

# Backup database
db_path = Path("./models.db")
backup_path = Path("./backups/models_backup.db")
shutil.copy2(db_path, backup_path)

# Check database size
size_mb = db_path.stat().st_size / (1024 * 1024)
print(f"Database size: {size_mb:.2f} MB")
```

---

## JSON Implementation

### Initialization with Auto-Reload

```python
from model_registry_json import ModelRegistryJSON

# Initialize
registry = ModelRegistryJSON.get_instance("./json_configs")

# Start auto-reload (checks every 5 minutes)
registry.start_auto_reload(interval_seconds=300)

# Stop auto-reload when done
registry.stop_auto_reload()
```

### Manual Reload

```python
# Reload all providers from JSON files
registry.reload_from_storage()

# Changes will be detected automatically:
# - New files added
# - Existing files modified
# - Files removed
```

### Auto-Reload Configuration

```python
# Start with custom interval (10 minutes)
registry.start_auto_reload(interval_seconds=600)

# Check if auto-reload is running
summary = registry.get_registry_summary()
print(f"Auto-reload: {summary['auto_reload_enabled']}")
print(f"Interval: {summary['auto_reload_interval']} seconds")
```

### File Watching

The JSON implementation automatically detects:
- **New files** - Providers added automatically
- **Modified files** - Providers reloaded with new data
- **Deleted files** - Providers removed from registry

Files are tracked using MD5 hashes, so only changed files are reloaded.

---

## Common Operations

### 1. Find Best Model for Task

```python
from model_management import ModelCapability

# Find cheapest vision model
provider, model, cost = registry.get_cheapest_model_for_capability(
    ModelCapability.VISION.value,
    input_tokens=10000,
    output_tokens=500
)

# Check if it has other capabilities
if model.has_capability(ModelCapability.FUNCTION_CALLING.value):
    print("Model supports function calling!")

# Calculate actual cost
actual_cost = model.calculate_cost(
    input_tokens=15000,
    output_tokens=750
)
print(f"Actual cost: ${actual_cost:.4f}")
```

### 2. List All Models with Capability

```python
# Get all models with vision capability
vision_models = registry.get_all_models_for_capability("vision")

print("Vision-capable models:")
for provider_name, model in vision_models:
    cost = model.calculate_cost(10000, 500)
    print(f"  {provider_name:15} {model.name:30} ${cost:.4f}")
```

### 3. Compare Providers

```python
providers = ["anthropic", "openai", "google"]

print("Provider Comparison:")
for provider_name in providers:
    try:
        provider = registry.get_provider_by_name(provider_name)
        model_count = provider.get_model_count()
        caps = provider.get_capabilities_summary()
        
        print(f"\n{provider_name}:")
        print(f"  Models: {model_count}")
        print(f"  Vision models: {caps.get('vision', 0)}")
        print(f"  Function calling: {caps.get('function_calling', 0)}")
    except Exception as e:
        print(f"{provider_name}: Not available")
```

### 4. Get Registry Statistics

```python
summary = registry.get_registry_summary()

print("Registry Summary:")
print(f"  Providers: {summary['provider_count']}")
print(f"  Total models: {summary['total_model_count']}")

for provider_info in summary['providers']:
    print(f"\n  {provider_info['name']}:")
    print(f"    Enabled: {provider_info['enabled']}")
    print(f"    Models: {provider_info['model_count']}")
    print(f"    API: {provider_info['api_version']}")
```

### 5. Filter Models by Multiple Capabilities

```python
# Find models with vision AND function calling
provider = registry.get_provider_by_name("anthropic")
multimodal = provider.get_models_for_capabilities([
    "vision",
    "function_calling"
])

print("Multimodal models with tools:")
for model in multimodal:
    print(f"  {model.name}")
```

### 6. Working with Model Metadata

```python
model = registry.get_model_from_provider_by_name(
    "anthropic",
    "claude-opus-4"
)

# Basic info
print(f"Name: {model.name}")
print(f"Version: {model.version}")
print(f"Description: {model.description}")

# Context and output
print(f"Context window: {model.context_window:,} tokens")
print(f"Max output: {model.max_output:,} tokens")

# Strengths
print("Strengths:")
for strength in model.strengths:
    print(f"  - {strength}")

# Performance metrics
if model.performance:
    print("Performance:")
    for metric, value in model.performance.items():
        print(f"  {metric}: {value}")

# Cost structure
print("Cost:")
for key, value in model.cost.items():
    print(f"  {key}: ${value}")
```

---

## API Reference

### ModelRegistry Methods

#### Provider Methods

```python
# Get provider by name
get_provider_by_name(provider_name: str) -> ModelProvider

# Get all providers
get_all_providers(include_disabled: bool = False) -> Dict[str, ModelProvider]

# Enable/disable provider
enable_provider(provider_name: str) -> bool
disable_provider(provider_name: str) -> bool
```

#### Model Query Methods

```python
# Get specific model
get_model_from_provider_by_name(
    provider_name: str,
    model_name: str
) -> Model

# Get all models from provider
get_all_models_from_provider(
    provider_name: str,
    include_disabled: bool = False
) -> List[Model]

# Get models by capability (all providers)
get_all_models_for_capability(
    capability: str,
    include_disabled_providers: bool = False
) -> List[Tuple[str, Model]]
```

#### Cost Optimization Methods

```python
# Find cheapest model globally
get_cheapest_model_for_capability(
    capability: str,
    input_tokens: int = 100000,
    output_tokens: int = 1000
) -> Tuple[str, Model, float]

# Find cheapest model from provider
get_cheapest_model_for_provider_and_capability(
    provider_name: str,
    capability: str,
    input_tokens: int = 100000,
    output_tokens: int = 1000
) -> Tuple[Model, float]
```

#### Model Enable/Disable Methods

```python
# Enable/disable specific model
enable_model(provider_name: str, model_name: str) -> bool
disable_model(provider_name: str, model_name: str) -> bool
```

#### Statistics Methods

```python
# Get provider count
get_provider_count(include_disabled: bool = False) -> int

# Get total model count
get_total_model_count(include_disabled: bool = False) -> int

# Get registry summary
get_registry_summary() -> Dict[str, Any]

# Reload from storage
reload_from_storage() -> None
```

### ModelProvider Methods

```python
# Get model by name
get_model_by_name(model_name: str) -> Optional[Model]

# Get models by capability
get_models_for_capability(capability: str) -> List[Model]

# Get models by multiple capabilities
get_models_for_capabilities(capabilities: List[str]) -> List[Model]

# Get cheapest model for capability
get_cheapest_model_for_capability(
    capability: str,
    input_tokens: int = 100000,
    output_tokens: int = 1000
) -> Optional[Model]

# Get all models
get_all_models(include_disabled: bool = False) -> List[Model]

# Model count
get_model_count(include_disabled: bool = False) -> int

# Enable/disable models
enable_model(model_name: str) -> bool
disable_model(model_name: str) -> bool

# Capabilities summary
get_capabilities_summary() -> Dict[str, int]

# Convert to dict
to_dict() -> Dict[str, Any]

# Reload from storage
reload() -> None
```

### Model Methods

```python
# Check capability
has_capability(capability: str) -> bool

# Check multiple capabilities
has_all_capabilities(capabilities: List[str]) -> bool

# Calculate cost
calculate_cost(input_tokens: int, output_tokens: int) -> float

# Get capability value
get_capability_value(capability: str) -> Any

# Convert to dict
to_dict() -> Dict[str, Any]
```

---

## Code Examples

### Example 1: Simple Model Selection

```python
from model_registry_db import ModelRegistryDB
from model_management import ModelCapability

def select_model_for_task(task_type: str, budget_per_100k: float):
    """Select the best model for a task within budget."""
    registry = ModelRegistryDB.get_instance()
    
    # Find cheapest model for capability
    provider, model, cost = registry.get_cheapest_model_for_capability(
        task_type,
        input_tokens=100000,
        output_tokens=1000
    )
    
    # Check if within budget
    if cost <= budget_per_100k:
        print(f"✓ Selected: {provider}/{model.name}")
        print(f"  Cost: ${cost:.4f} per 100k tokens")
        return provider, model
    else:
        print(f"✗ Cheapest model (${cost:.4f}) exceeds budget (${budget_per_100k})")
        return None, None

# Use it
provider, model = select_model_for_task(
    ModelCapability.CHAT.value,
    budget_per_100k=0.50
)
```

### Example 2: Multi-Capability Search

```python
def find_multimodal_models():
    """Find models that support both vision and function calling."""
    registry = ModelRegistryDB.get_instance()
    
    # Get all vision models
    vision_models = registry.get_all_models_for_capability("vision")
    
    # Filter for function calling
    results = []
    for provider_name, model in vision_models:
        if model.has_capability("function_calling"):
            cost = model.calculate_cost(10000, 1000)
            results.append({
                'provider': provider_name,
                'model': model.name,
                'cost': cost,
                'context': model.context_window
            })
    
    # Sort by cost
    results.sort(key=lambda x: x['cost'])
    
    # Display
    print("Multimodal models with function calling:")
    for r in results:
        print(f"  {r['provider']:12} {r['model']:30} "
              f"${r['cost']:.4f}  {r['context']:,} ctx")
    
    return results

# Use it
models = find_multimodal_models()
```

### Example 3: Cost Comparison

```python
def compare_costs(capability: str, input_tokens: int, output_tokens: int):
    """Compare costs across all providers for a capability."""
    registry = ModelRegistryDB.get_instance()
    
    models = registry.get_all_models_for_capability(capability)
    
    costs = []
    for provider_name, model in models:
        cost = model.calculate_cost(input_tokens, output_tokens)
        costs.append({
            'provider': provider_name,
            'model': model.name,
            'cost': cost,
            'cost_per_1k': (cost / (input_tokens + output_tokens)) * 1000
        })
    
    # Sort by cost
    costs.sort(key=lambda x: x['cost'])
    
    print(f"\nCost comparison for {capability}:")
    print(f"Input: {input_tokens:,} tokens, Output: {output_tokens:,} tokens\n")
    print(f"{'Provider':<15} {'Model':<30} {'Total':<10} {'Per 1k tokens'}")
    print("-" * 70)
    
    for c in costs:
        print(f"{c['provider']:<15} {c['model']:<30} "
              f"${c['cost']:<9.4f} ${c['cost_per_1k']:.6f}")
    
    return costs

# Use it
costs = compare_costs("chat", 50000, 2000)
```

### Example 4: Dynamic Provider Selection

```python
class ModelSelector:
    """Intelligent model selector based on requirements."""
    
    def __init__(self):
        self.registry = ModelRegistryDB.get_instance()
    
    def select_model(self, 
                     capabilities: List[str],
                     max_cost: float = None,
                     min_context: int = None,
                     preferred_providers: List[str] = None):
        """
        Select best model based on requirements.
        
        Args:
            capabilities: Required capabilities
            max_cost: Maximum cost per 100k tokens
            min_context: Minimum context window
            preferred_providers: Preferred provider names
        """
        # Get candidates with primary capability
        candidates = self.registry.get_all_models_for_capability(
            capabilities[0]
        )
        
        # Filter by additional capabilities
        if len(capabilities) > 1:
            candidates = [
                (p, m) for p, m in candidates
                if m.has_all_capabilities(capabilities[1:])
            ]
        
        # Filter by context window
        if min_context:
            candidates = [
                (p, m) for p, m in candidates
                if m.context_window >= min_context
            ]
        
        # Filter by cost
        if max_cost:
            candidates = [
                (p, m) for p, m in candidates
                if m.calculate_cost(100000, 1000) <= max_cost
            ]
        
        # Sort by preferred providers, then cost
        def sort_key(item):
            provider, model = item
            cost = model.calculate_cost(100000, 1000)
            
            if preferred_providers and provider in preferred_providers:
                priority = preferred_providers.index(provider)
            else:
                priority = 999
            
            return (priority, cost)
        
        candidates.sort(key=sort_key)
        
        if candidates:
            return candidates[0]
        return None, None

# Use it
selector = ModelSelector()
provider, model = selector.select_model(
    capabilities=["vision", "function_calling"],
    max_cost=0.50,
    min_context=100000,
    preferred_providers=["anthropic", "openai"]
)

if model:
    print(f"Selected: {provider}/{model.name}")
else:
    print("No model found matching requirements")
```

### Example 5: Batch Processing

```python
def process_multiple_tasks(tasks: List[Dict]):
    """Process multiple tasks with optimal model selection."""
    registry = ModelRegistryDB.get_instance()
    results = []
    
    for task in tasks:
        # Select model for this task
        provider, model, cost = registry.get_cheapest_model_for_capability(
            task['capability'],
            input_tokens=task['input_tokens'],
            output_tokens=task['output_tokens']
        )
        
        results.append({
            'task_id': task['id'],
            'provider': provider,
            'model': model.name,
            'estimated_cost': cost
        })
    
    # Calculate total cost
    total_cost = sum(r['estimated_cost'] for r in results)
    
    print(f"Batch Processing Plan:")
    print(f"  Total tasks: {len(tasks)}")
    print(f"  Estimated cost: ${total_cost:.4f}")
    print(f"\nTask breakdown:")
    for r in results:
        print(f"  {r['task_id']}: {r['provider']}/{r['model']} "
              f"(${r['estimated_cost']:.4f})")
    
    return results

# Use it
tasks = [
    {'id': 'task1', 'capability': 'chat', 'input_tokens': 5000, 'output_tokens': 500},
    {'id': 'task2', 'capability': 'vision', 'input_tokens': 10000, 'output_tokens': 1000},
    {'id': 'task3', 'capability': 'code', 'input_tokens': 20000, 'output_tokens': 2000},
]

results = process_multiple_tasks(tasks)
```

---

## Deployment Guide

### Production Deployment

#### 1. Database Setup

```bash
#!/bin/bash
# setup_production.sh

# Create data directory
mkdir -p /var/lib/abhikarta
chmod 700 /var/lib/abhikarta

# Initialize database
python3 << EOF
from model_registry_db import ModelRegistryDB

registry = ModelRegistryDB.get_instance("/var/lib/abhikarta/models.db")
registry.load_json_directory("/etc/abhikarta/configs")
print("Database initialized successfully")
EOF

# Set proper permissions
chown appuser:appuser /var/lib/abhikarta/models.db
chmod 600 /var/lib/abhikarta/models.db
```

#### 2. Application Integration

```python
# config.py
import os

# Database path from environment
DB_PATH = os.getenv('ABHIKARTA_DB_PATH', '/var/lib/abhikarta/models.db')

# Initialize on app startup
from model_registry_db import ModelRegistryDB

def init_model_registry():
    """Initialize model registry on application startup."""
    registry = ModelRegistryDB.get_instance(db_path=DB_PATH)
    return registry

# Use in your application
registry = init_model_registry()
```

#### 3. Docker Deployment

```dockerfile
FROM python:3.11-slim

# Create app user
RUN useradd -r -s /bin/false -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy application files
COPY *.py /app/
COPY json_configs/ /app/json_configs/

# Create data directory
RUN mkdir -p /app/data && \
    chown -R appuser:appuser /app && \
    chmod 700 /app/data

# Switch to app user
USER appuser

# Environment variables
ENV ABHIKARTA_DB_PATH=/app/data/models.db
ENV PYTHONUNBUFFERED=1

# Volume for persistent data
VOLUME /app/data

# Initialize database on first run
RUN python3 -c "from model_registry_db import ModelRegistryDB; \
    registry = ModelRegistryDB.get_instance('/app/data/models.db'); \
    registry.load_json_directory('/app/json_configs')"

# Run your application
CMD ["python3", "your_app.py"]
```

Build and run:
```bash
docker build -t abhikarta-app .
docker run -v abhikarta_data:/app/data abhikarta-app
```

#### 4. Kubernetes Deployment

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: abhikarta-configs
data:
  anthropic.json: |
    {
      "provider": "anthropic",
      ...
    }
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: abhikarta-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: abhikarta-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: abhikarta
  template:
    metadata:
      labels:
        app: abhikarta
    spec:
      containers:
      - name: app
        image: abhikarta-app:latest
        env:
        - name: ABHIKARTA_DB_PATH
          value: /data/models.db
        volumeMounts:
        - name: data
          mountPath: /data
        - name: configs
          mountPath: /app/json_configs
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: abhikarta-data
      - name: configs
        configMap:
          name: abhikarta-configs
```

### Development Deployment

#### 1. JSON Setup

```bash
#!/bin/bash
# setup_development.sh

# Create config directory
mkdir -p ./json_configs

# Copy example configs
cp examples/*.json ./json_configs/

# Start with auto-reload
python3 << EOF
from model_registry_json import ModelRegistryJSON

registry = ModelRegistryJSON.get_instance("./json_configs")
registry.start_auto_reload(interval_seconds=60)  # Check every minute
print("Development environment ready with auto-reload")
EOF
```

#### 2. Hot Reload Example

```python
# dev_server.py
from model_registry_json import ModelRegistryJSON
import time

def main():
    # Initialize with auto-reload
    registry = ModelRegistryJSON.get_instance("./json_configs")
    registry.start_auto_reload(interval_seconds=30)
    
    print("Development server running with hot reload...")
    print("Modify JSON files in ./json_configs/ to see changes")
    
    try:
        while True:
            # Your application logic here
            summary = registry.get_registry_summary()
            print(f"\rProviders: {summary['provider_count']}, "
                  f"Models: {summary['total_model_count']}", end='')
            time.sleep(5)
    except KeyboardInterrupt:
        registry.stop_auto_reload()
        print("\nShutdown complete")

if __name__ == "__main__":
    main()
```

### Backup and Restore

#### Database Backup

```python
import shutil
from datetime import datetime
from pathlib import Path

def backup_database(db_path: str, backup_dir: str):
    """Backup the database with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(backup_dir) / f"models_backup_{timestamp}.db"
    
    shutil.copy2(db_path, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path

# Use it
backup_path = backup_database(
    "/var/lib/abhikarta/models.db",
    "/var/backups/abhikarta"
)
```

#### JSON Backup

```bash
#!/bin/bash
# backup_configs.sh

BACKUP_DIR="/var/backups/abhikarta"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Tar the configs
tar -czf "$BACKUP_DIR/configs_$TIMESTAMP.tar.gz" json_configs/

echo "Backup created: $BACKUP_DIR/configs_$TIMESTAMP.tar.gz"
```

---

## Best Practices

### 1. Use Singleton Pattern

```python
# ✓ Good
registry = ModelRegistryDB.get_instance()

# ✗ Bad
registry = ModelRegistryDB("/path/to/db")  # Don't instantiate directly
```

### 2. Handle Exceptions

```python
from exceptions import (
    ProviderNotFoundException,
    ModelNotFoundException,
    NoModelsAvailableException
)

try:
    model = registry.get_model_from_provider_by_name("anthropic", "claude-opus-4")
except ProviderNotFoundException as e:
    print(f"Provider not found: {e.provider_name}")
except ModelNotFoundException as e:
    print(f"Model not found: {e.model_name}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 3. Cache Registry Instance

```python
# application.py
from model_registry_db import ModelRegistryDB

# Initialize once at module level
_registry = None

def get_registry():
    """Get or create registry instance."""
    global _registry
    if _registry is None:
        _registry = ModelRegistryDB.get_instance()
    return _registry

# Use throughout application
registry = get_registry()
```

### 4. Use Enums for Capabilities

```python
from model_management import ModelCapability

# ✓ Good - Type safe
models = registry.get_all_models_for_capability(ModelCapability.VISION.value)

# ✗ Bad - Prone to typos
models = registry.get_all_models_for_capability("vison")  # Typo!
```

### 5. Batch Operations

```python
# ✓ Good - Single query
all_models = registry.get_all_models_for_capability("chat")

# ✗ Bad - Multiple queries
for provider_name in ["anthropic", "openai", "google"]:
    models = registry.get_all_models_from_provider(provider_name)
```

### 6. Calculate Costs with Real Tokens

```python
# ✓ Good - Use actual token counts
actual_input = count_tokens(user_message)
actual_output = count_tokens(assistant_response)
cost = model.calculate_cost(actual_input, actual_output)

# ✗ Bad - Hardcoded estimates
cost = model.calculate_cost(1000, 500)  # Inaccurate!
```

### 7. Enable Only Required Models

```python
# Disable expensive models if not needed
registry.disable_model("anthropic", "claude-opus-4")

# Enable only when required
if require_advanced_reasoning:
    registry.enable_model("anthropic", "claude-opus-4")
```

### 8. Regular Backups

```python
import schedule
import time

def backup_job():
    backup_database(
        "/var/lib/abhikarta/models.db",
        "/var/backups/abhikarta"
    )

# Schedule daily backups
schedule.every().day.at("02:00").do(backup_job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## Troubleshooting

### Common Issues

#### 1. Provider Not Found

**Error:**
```
ProviderNotFoundException: Provider 'anthropic' not found in registry
```

**Solutions:**
```python
# Check available providers
providers = registry.get_all_providers(include_disabled=True)
print("Available providers:", list(providers.keys()))

# For database: Import JSON
registry.load_json_file("./json_configs/anthropic.json")

# For JSON: Check file exists
import os
if not os.path.exists("./json_configs/anthropic.json"):
    print("File not found!")
```

#### 2. Model Not Found

**Error:**
```
ModelNotFoundException: Model 'claude-opus-4' not found in provider 'anthropic'
```

**Solutions:**
```python
# List available models
provider = registry.get_provider_by_name("anthropic")
models = provider.get_all_models(include_disabled=True)
print("Available models:")
for model in models:
    print(f"  - {model.name} (enabled: {model.enabled})")
```

#### 3. Database Locked

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Solutions:**
```python
# Close other connections
ModelRegistryDB.reset_instance()

# Increase timeout
# (Edit model_management_db_handler.py)
sqlite3.connect(db_path, timeout=30.0)

# Check for zombie processes
# $ lsof models.db
```

#### 4. No Models Available

**Error:**
```
NoModelsAvailableException: No models available for capability: vision
```

**Solutions:**
```python
# Check if models are disabled
models = registry.get_all_models_for_capability("vision")
if not models:
    # Enable vision-capable models
    registry.enable_model("anthropic", "claude-opus-4")
    
# Check provider is enabled
providers = registry.get_all_providers()
if "anthropic" not in providers:
    registry.enable_provider("anthropic")
```

#### 5. Auto-Reload Not Working

**Problem:** JSON changes not detected

**Solutions:**
```python
# Check if auto-reload is running
summary = registry.get_registry_summary()
print(f"Auto-reload enabled: {summary['auto_reload_enabled']}")

# Manually reload
registry.reload_from_storage()

# Check interval
print(f"Reload interval: {summary['auto_reload_interval']} seconds")

# Restart auto-reload
registry.stop_auto_reload()
registry.start_auto_reload(interval_seconds=60)
```

### Debugging

#### Enable Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now you'll see detailed logs
registry = ModelRegistryDB.get_instance()
```

#### Check Registry State

```python
def debug_registry():
    """Print comprehensive registry state."""
    registry = ModelRegistryDB.get_instance()
    
    summary = registry.get_registry_summary()
    print("=== Registry State ===")
    print(f"Providers: {summary['provider_count']}")
    print(f"Total models: {summary['total_model_count']}")
    
    print("\n=== Provider Details ===")
    for p in summary['providers']:
        print(f"\n{p['name']}:")
        print(f"  Enabled: {p['enabled']}")
        print(f"  Models: {p['model_count']}")
        print(f"  API: {p['api_version']}")
        
        # Get models
        try:
            provider = registry.get_provider_by_name(p['name'])
            models = provider.get_all_models(include_disabled=True)
            print(f"  Model list:")
            for model in models:
                status = "✓" if model.enabled else "✗"
                print(f"    {status} {model.name}")
        except Exception as e:
            print(f"  Error loading models: {e}")

# Run it
debug_registry()
```

---

## Performance Tuning

### Database Optimization

```python
# Use get_database_handler for bulk operations
db_handler = registry.get_database_handler()

# Batch enable/disable
models_to_enable = ["model1", "model2", "model3"]
for model_name in models_to_enable:
    registry.enable_model("anthropic", model_name)

# Or use database directly for bulk updates
# (Advanced - requires SQL knowledge)
```

### Caching Results

```python
from functools import lru_cache

class CachedRegistry:
    def __init__(self):
        self.registry = ModelRegistryDB.get_instance()
    
    @lru_cache(maxsize=128)
    def get_cheapest_cached(self, capability: str):
        """Cached version of get_cheapest_model."""
        return self.registry.get_cheapest_model_for_capability(capability)
    
    def clear_cache(self):
        """Clear cache when data changes."""
        self.get_cheapest_cached.cache_clear()

# Use it
cached = CachedRegistry()
provider, model, cost = cached.get_cheapest_cached("chat")
```

### Minimize Queries

```python
# ✓ Good - Single query
all_models = registry.get_all_models_for_capability("chat")
for provider_name, model in all_models:
    process(provider_name, model)

# ✗ Bad - Multiple queries
for provider_name in provider_names:
    provider = registry.get_provider_by_name(provider_name)
    models = provider.get_models_for_capability("chat")
    for model in models:
        process(provider_name, model)
```

---

## Migration Guide

### From Old Code to Refactored Architecture

#### Old Code (Single Implementation)
```python
from model_registry import ModelRegistry

registry = ModelRegistry.get_instance("/path/to/configs")
```

#### New Code (Choose Implementation)

**Option 1: Database**
```python
from model_registry_db import ModelRegistryDB

registry = ModelRegistryDB.get_instance(db_path="./models.db")
registry.load_json_directory("/path/to/configs")  # One-time
```

**Option 2: JSON**
```python
from model_registry_json import ModelRegistryJSON

registry = ModelRegistryJSON.get_instance("/path/to/configs")
registry.start_auto_reload()
```

### API Changes

All APIs remain the same! The refactoring is backward compatible:

```python
# These work with BOTH implementations
provider = registry.get_provider_by_name("anthropic")
model = registry.get_model_from_provider_by_name("anthropic", "claude-opus-4")
provider, model, cost = registry.get_cheapest_model_for_capability("chat")
```

### Migration Steps

1. **Choose Implementation**
   - Production → Database
   - Development → JSON

2. **Update Imports**
   ```python
   # Old
   from model_registry import ModelRegistry
   
   # New (Database)
   from model_registry_db import ModelRegistryDB as ModelRegistry
   
   # OR New (JSON)
   from model_registry_json import ModelRegistryJSON as ModelRegistry
   ```

3. **Update Initialization**
   ```python
   # Old
   registry = ModelRegistry.get_instance(config_dir)
   
   # New (Database)
   registry = ModelRegistry.get_instance(db_path="./models.db")
   registry.load_json_directory(config_dir)
   
   # New (JSON)
   registry = ModelRegistry.get_instance(config_dir)
   registry.start_auto_reload()
   ```

4. **Test**
   - All other code remains unchanged
   - Test thoroughly before deployment

---

## Support

For questions, issues, or support:

**Email:** ajsinha@gmail.com

**Topics:**
- API usage questions
- Deployment assistance
- Performance optimization
- Bug reports
- Feature requests

---

## Appendix: Complete Example

Here's a complete working example:

```python
"""
Complete example of Abhikarta Model Registry usage.
"""

from model_registry_db import ModelRegistryDB
from model_management import ModelCapability
from exceptions import (
    ProviderNotFoundException,
    ModelNotFoundException,
    NoModelsAvailableException
)

def main():
    # 1. Initialize registry
    print("Initializing registry...")
    registry = ModelRegistryDB.get_instance(db_path="./models.db")
    
    # 2. Import configurations (first time only)
    print("Loading configurations...")
    loaded = registry.load_json_directory("./json_configs")
    print(f"Loaded {len(loaded)} providers")
    
    # 3. Get registry summary
    summary = registry.get_registry_summary()
    print(f"\nRegistry summary:")
    print(f"  Providers: {summary['provider_count']}")
    print(f"  Total models: {summary['total_model_count']}")
    
    # 4. List all providers
    print("\nAvailable providers:")
    providers = registry.get_all_providers()
    for name, provider in providers.items():
        print(f"  - {name}: {provider.get_model_count()} models")
    
    # 5. Get specific model
    try:
        model = registry.get_model_from_provider_by_name(
            "anthropic",
            "claude-opus-4"
        )
        print(f"\nModel details:")
        print(f"  Name: {model.name}")
        print(f"  Context: {model.context_window:,} tokens")
        print(f"  Output: {model.max_output:,} tokens")
    except (ProviderNotFoundException, ModelNotFoundException) as e:
        print(f"Error: {e}")
    
    # 6. Find cheapest chat model
    try:
        provider_name, model, cost = registry.get_cheapest_model_for_capability(
            ModelCapability.CHAT.value,
            input_tokens=100000,
            output_tokens=1000
        )
        print(f"\nCheapest chat model:")
        print(f"  Provider: {provider_name}")
        print(f"  Model: {model.name}")
        print(f"  Cost: ${cost:.4f} per 100k input + 1k output")
    except NoModelsAvailableException as e:
        print(f"Error: {e}")
    
    # 7. Find all vision models
    vision_models = registry.get_all_models_for_capability("vision")
    print(f"\nVision-capable models: {len(vision_models)}")
    for provider_name, model in vision_models[:5]:  # Show first 5
        cost = model.calculate_cost(10000, 1000)
        print(f"  {provider_name:15} {model.name:30} ${cost:.4f}")
    
    # 8. Compare costs
    print("\nCost comparison for 50k input, 2k output:")
    models_to_compare = [
        ("anthropic", "claude-opus-4"),
        ("anthropic", "claude-sonnet-4"),
        ("openai", "gpt-4o"),
    ]
    
    for provider_name, model_name in models_to_compare:
        try:
            model = registry.get_model_from_provider_by_name(
                provider_name,
                model_name
            )
            cost = model.calculate_cost(50000, 2000)
            print(f"  {provider_name:12} {model_name:25} ${cost:.4f}")
        except Exception as e:
            print(f"  {provider_name:12} {model_name:25} Error: {e}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
```

---

**Copyright © 2025-2030 Ashutosh Sinha - All Rights Reserved**

**End of Quick Reference Guide**