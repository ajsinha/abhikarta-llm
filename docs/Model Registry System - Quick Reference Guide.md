# Abhikarta LLM Model Registry System - Complete Quick Reference Guide

**Version 2.4 - Comprehensive API Reference & Practical Usage Guide**

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

---

## Table of Contents

1. [Installation Guide](#installation-guide)
2. [5-Minute Quick Start](#5-minute-quick-start)
3. [Complete API Reference](#complete-api-reference)
4. [CRUD Operations Guide](#crud-operations-guide)
5. [Advanced Features](#advanced-features)
6. [Production Deployment](#production-deployment)
7. [Best Practices](#best-practices)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Configuration Reference](#configuration-reference)
10. [Code Examples](#code-examples)

---

## Installation Guide

### System Requirements

- **Python:** 3.8 or higher
- **Operating System:** Linux, macOS, Windows
- **Dependencies:** None (uses Python standard library only)
- **Storage:** Minimal (< 1MB for code, variable for data)

### Installation Steps

**Step 1: Create Project Directory**
```bash
mkdir abhikarta-registry
cd abhikarta-registry
```

**Step 2: Copy Files**
```bash
# Copy all 11 Python modules
# Copy test files
# Copy example configuration
```

**Step 3: Verify Installation**
```bash
python quick_test.py
```

Expected output:
```
🎉 ALL TESTS PASSED - System is working correctly!
```

### Directory Structure

```
abhikarta-registry/
├── exceptions.py
├── model_management.py
├── model_management_db_handler.py
├── model_provider.py
├── model_provider_db.py
├── model_provider_json.py
├── model_registry.py
├── model_registry_db.py
├── model_registry_db_crud.py
├── model_registry_json.py
├── sample_usage.py
├── quick_test.py
├── test_model_crud.py
└── example_provider_config.json
```

### Configuration Setup

**For Production (Database):**
```bash
mkdir -p data configs
# Database created automatically on first use
```

**For Development (JSON):**
```bash
mkdir -p json_configs
cp example_provider_config.json json_configs/my_provider.json
```

---

## 5-Minute Quick Start

### Step 1: Choose Implementation (1 minute)

**For Production - Database:**

```python
from model_registry_db import ModelRegistryDB

registry = ModelRegistryDB.get_instance(db_connection_pool_name="./data/models.db_management")
```

**For Development - JSON:**
```python
from model_registry_json import ModelRegistryJSON

registry = ModelRegistryJSON.get_instance("./json_configs")
registry.start_auto_reload(interval_minutes=5)  # Auto-reload changes
```

### Step 2: Create Configuration (2 minutes)

Create `openai.json`:
```json
{
  "provider": "openai",
  "api_base_url": "https://api.openai.com/v1",
  "enabled": true,
  "models": [
    {
      "name": "gpt-4o",
      "description": "High-intelligence flagship model",
      "version": "2024-11-20",
      "enabled": true,
      "context_window": 128000,
      "max_output": 16384,
      "cost": {
        "input_per_1m": 2.50,
        "output_per_1m": 10.00
      },
      "capabilities": {
        "chat": true,
        "vision": true,
        "streaming": true,
        "function_calling": true
      },
      "strengths": [
        "Excellent reasoning",
        "Vision capabilities",
        "Large context window"
      ],
      "release_date": "2024-11-20"
    },
    {
      "name": "gpt-4o-mini",
      "description": "Affordable and intelligent small model",
      "version": "2024-07-18",
      "enabled": true,
      "context_window": 128000,
      "max_output": 16384,
      "cost": {
        "input_per_1m": 0.15,
        "output_per_1m": 0.60
      },
      "capabilities": {
        "chat": true,
        "vision": true,
        "streaming": true,
        "function_calling": true
      },
      "release_date": "2024-07-18"
    }
  ]
}
```

### Step 3: Query Models (2 minutes)

```python
# Get summary
summary = registry.get_registry_summary()
print(f"Providers: {summary['provider_count']}")
print(f"Models: {summary['total_model_count']}")

# Find cheapest chat model
provider_name, model, cost = registry.get_cheapest_model_for_capability(
    "chat",
    input_tokens=10000,
    output_tokens=1000
)
print(f"Cheapest: {provider_name}/{model.name}")
print(f"Cost: ${cost:.4f}")

# Get model with capability validation (v2.3)
model = registry.get_model_from_provider_by_name_capability(
    "openai",
    "gpt-4o",
    "vision"
)
print(f"Vision model: {model.name}")
print(f"Context window: {model.context_window:,} tokens")

# Calculate cost for specific workload
cost = model.calculate_cost(5000, 500)
print(f"Cost for 5k input + 500 output: ${cost:.4f}")
```

---

## Complete API Reference

### Provider Management (8 Methods)

#### 1. get_provider_by_name(provider_name: str) -> ModelProvider

Get a specific provider by name.

```python
provider = registry.get_provider_by_name("openai")
print(f"Provider: {provider.provider_name}")
print(f"Enabled: {provider.enabled}")
print(f"Models: {provider.get_model_count()}")
```

**Parameters:**
- `provider_name` (str): Provider identifier

**Returns:** `ModelProvider` instance

**Raises:** `ProviderNotFoundException` if not found

#### 2. get_all_providers(include_disabled: bool = False) -> Dict[str, ModelProvider]

Get all providers.

```python
providers = registry.get_all_providers(include_disabled=False)
for name, provider in providers.items():
    model_count = provider.get_model_count()
    print(f"{name}: {model_count} models")
```

**Parameters:**
- `include_disabled` (bool): Include disabled providers (default: False)

**Returns:** Dictionary of provider_name -> ModelProvider

#### 3. enable_provider(provider_name: str)

Enable a provider.

```python
registry.enable_provider("openai")
```

**Parameters:**
- `provider_name` (str): Provider to enable

**Raises:** `ProviderNotFoundException` if not found

#### 4. disable_provider(provider_name: str)

Disable a provider.

```python
registry.disable_provider("legacy_provider")
```

**Parameters:**
- `provider_name` (str): Provider to disable

**Raises:** `ProviderNotFoundException` if not found

#### 5. get_provider_count(include_disabled: bool = False) -> int

Get total number of providers.

```python
active_count = registry.get_provider_count(include_disabled=False)
total_count = registry.get_provider_count(include_disabled=True)
print(f"Active: {active_count}, Total: {total_count}")
```

**Parameters:**
- `include_disabled` (bool): Include disabled providers

**Returns:** Integer count

#### 6. enable_all_providers()

Enable all providers.

```python
registry.enable_all_providers()
```

#### 7. disable_all_providers()

Disable all providers.

```python
registry.disable_all_providers()
```

#### 8. get_enabled_provider_names() -> List[str]

Get list of enabled provider names.

```python
enabled = registry.get_enabled_provider_names()
print(f"Enabled providers: {', '.join(enabled)}")
```

**Returns:** List of provider names

### Model Query Methods (15 Methods)

#### 1. get_model_from_provider_by_name(provider_name: str, model_name: str) -> Model

Get a specific model from a provider.

```python
model = registry.get_model_from_provider_by_name("openai", "gpt-4o")
print(f"Model: {model.name}")
print(f"Version: {model.version}")
print(f"Context: {model.context_window:,} tokens")
print(f"Max output: {model.max_output:,} tokens")
print(f"Enabled: {model.enabled}")
```

**Parameters:**
- `provider_name` (str): Provider identifier
- `model_name` (str): Model name

**Returns:** `Model` instance

**Raises:**
- `ProviderNotFoundException` if provider not found
- `ModelNotFoundException` if model not found

#### 2. get_model_from_provider_by_name_capability(provider_name: str, model_name: str, capability: str) -> Model

Get model and validate it has required capability (v2.3).

```python
# Ensures model has vision capability
model = registry.get_model_from_provider_by_name_capability(
    "openai",
    "gpt-4o",
    "vision"
)
print(f"✓ {model.name} has vision capability")
```

**Parameters:**
- `provider_name` (str): Provider identifier
- `model_name` (str): Model name
- `capability` (str): Required capability

**Returns:** `Model` instance

**Raises:**
- `ProviderNotFoundException` if provider not found
- `ModelNotFoundException` if model not found
- `NoModelsAvailableException` if model doesn't have capability

**Use Case:**
```python
try:
    model = registry.get_model_from_provider_by_name_capability(
        "google", "gemini-1.5-pro", "vision"
    )
    # Use model knowing it has vision capability
    process_image_with_model(model, image)
except NoModelsAvailableException:
    # Fallback to non-vision model
    model = get_fallback_model()
```

#### 3. get_all_models_from_provider(provider_name: str, include_disabled: bool = False) -> Dict[str, Model]

Get all models from a provider.

```python
models = registry.get_all_models_from_provider(
    "anthropic",
    include_disabled=False
)
for name, model in models.items():
    print(f"{name}: {model.context_window:,} tokens")
```

**Parameters:**
- `provider_name` (str): Provider identifier
- `include_disabled` (bool): Include disabled models

**Returns:** Dictionary of model_name -> Model

**Raises:** `ProviderNotFoundException` if provider not found

#### 4. get_all_models_for_capability(capability: str) -> List[Tuple[str, Model]]

Get all models with a specific capability.

```python
vision_models = registry.get_all_models_for_capability("vision")
print(f"Found {len(vision_models)} vision-capable models:")
for provider_name, model in vision_models:
    cost = model.calculate_cost(10000, 1000)
    print(f"  {provider_name}/{model.name} - ${cost:.4f}")
```

**Parameters:**
- `capability` (str): Required capability

**Returns:** List of tuples (provider_name, Model)

**Use Case:**
```python
# Find all streaming models
streaming_models = registry.get_all_models_for_capability("streaming")

# Find all function-calling models
function_models = registry.get_all_models_for_capability("function_calling")

# Find all chat models
chat_models = registry.get_all_models_for_capability("chat")
```

#### 5. get_total_model_count(include_disabled: bool = False) -> int

Get total number of models across all providers.

```python
active = registry.get_total_model_count(include_disabled=False)
total = registry.get_total_model_count(include_disabled=True)
print(f"Active: {active}, Total: {total}")
```

**Parameters:**
- `include_disabled` (bool): Include disabled models

**Returns:** Integer count

#### 6. enable_model(provider_name: str, model_name: str)

Enable a specific model.

```python
registry.enable_model("openai", "gpt-4o")
```

**Parameters:**
- `provider_name` (str): Provider identifier
- `model_name` (str): Model name

**Raises:**
- `ProviderNotFoundException`
- `ModelNotFoundException`

#### 7. disable_model(provider_name: str, model_name: str)

Disable a specific model.

```python
registry.disable_model("openai", "old-model")
```

**Parameters:**
- `provider_name` (str): Provider identifier
- `model_name` (str): Model name

**Raises:**
- `ProviderNotFoundException`
- `ModelNotFoundException`

#### 8-15. Additional Query Methods

```python
# Get models by multiple criteria
models = registry.get_models_with_min_context_window(100000)
models = registry.get_models_with_max_output_min(4096)

# Get enabled models only
enabled_models = registry.get_all_enabled_models()

# Get specific provider models
openai_models = registry.get_all_models_from_provider("openai")
```

### Cost Optimization Methods (5 Methods)

#### 1. get_cheapest_model_for_capability(capability: str, input_tokens: int, output_tokens: int) -> Tuple[str, Model, float]

Find the cheapest model for a specific capability.

```python
provider_name, model, total_cost = registry.get_cheapest_model_for_capability(
    capability="chat",
    input_tokens=10000,
    output_tokens=1000
)

print(f"Cheapest chat model:")
print(f"  Provider: {provider_name}")
print(f"  Model: {model.name}")
print(f"  Cost: ${total_cost:.4f}")
print(f"  Context window: {model.context_window:,} tokens")
print(f"  Max output: {model.max_output:,} tokens")
```

**Parameters:**
- `capability` (str): Required capability
- `input_tokens` (int): Number of input tokens
- `output_tokens` (int): Number of output tokens

**Returns:** Tuple of (provider_name, Model, cost)

**Raises:** `NoModelsAvailableException` if no suitable model found

**Use Cases:**
```python
# Find cheapest for small workload
provider, model, cost = registry.get_cheapest_model_for_capability(
    "chat", 1000, 100
)

# Find cheapest for large workload
provider, model, cost = registry.get_cheapest_model_for_capability(
    "chat", 1000000, 10000
)

# Find cheapest vision model
provider, model, cost = registry.get_cheapest_model_for_capability(
    "vision", 5000, 500
)
```

#### 2. get_cheapest_model_for_provider_and_capability(provider_name: str, capability: str, input_tokens: int, output_tokens: int) -> Tuple[str, Model, float]

Find cheapest model for a specific provider and capability.

```python
provider_name, model, cost = registry.get_cheapest_model_for_provider_and_capability(
    provider_name="anthropic",
    capability="chat",
    input_tokens=50000,
    output_tokens=2000
)

print(f"Cheapest Anthropic chat model: {model.name} (${cost:.4f})")
```

**Parameters:**
- `provider_name` (str): Specific provider
- `capability` (str): Required capability
- `input_tokens` (int): Input tokens
- `output_tokens` (int): Output tokens

**Returns:** Tuple of (provider_name, Model, cost)

**Raises:**
- `ProviderNotFoundException`
- `NoModelsAvailableException`

#### 3. compare_model_costs(models: List[Tuple[str, Model]], input_tokens: int, output_tokens: int) -> List[Tuple[str, str, float]]

Compare costs across multiple models.

```python
# Get all chat models
chat_models = registry.get_all_models_for_capability("chat")

# Compare costs
comparisons = registry.compare_model_costs(
    chat_models,
    input_tokens=10000,
    output_tokens=1000
)

# Display sorted by cost
comparisons.sort(key=lambda x: x[2])
for provider, model_name, cost in comparisons[:5]:
    print(f"{provider:15} {model_name:25} ${cost:.4f}")
```

**Parameters:**
- `models` (List[Tuple[str, Model]]): Models to compare
- `input_tokens` (int): Input tokens
- `output_tokens` (int): Output tokens

**Returns:** List of (provider, model_name, cost) tuples

#### 4-5. Additional Cost Methods

```python
# Calculate total cost for batch processing
total_cost = registry.calculate_batch_cost(
    provider_name="openai",
    model_name="gpt-4o-mini",
    requests=[(10000, 1000), (5000, 500), (20000, 2000)]
)

# Get cost summary
summary = registry.get_cost_summary_for_capability("chat")
```

### CRUD Operations (18 Methods) [v2.4]

#### 1. create_model(provider_name: str, model_data: Dict[str, Any]) -> Model

Create a new model programmatically.

```python
model_data = {
    'name': 'gpt-5',
    'description': 'Next generation model',
    'version': '1.0',
    'enabled': True,
    'context_window': 128000,
    'max_output': 4096,
    'cost': {
        'input_per_1m': 5.0,
        'output_per_1m': 15.0
    },
    'capabilities': {
        'chat': True,
        'streaming': True,
        'function_calling': True,
        'vision': True
    },
    'strengths': [
        'Exceptional reasoning',
        'Multilingual support',
        'Advanced code generation'
    ],
    'release_date': '2025-01-01'
}

model = registry.create_model('openai', model_data)
print(f"✓ Created: {model.name} v{model.version}")
```

**Required Fields:**
- `name` - Model name
- `description` - Description
- `version` - Version string
- `enabled` - Boolean
- `context_window` - Integer
- `max_output` - Integer
- `cost` - Dictionary with 'input_per_1m' and 'output_per_1m'
- `capabilities` - Dictionary
- `release_date` - ISO date string

**Optional Fields:**
- `strengths` - List of strings
- `supports_streaming` - Boolean
- `supports_function_calling` - Boolean

**Raises:** `ModelAlreadyExistsException` if model exists

#### 2. update_model(provider_name: str, model_name: str, updates: Dict[str, Any]) -> Model

Update multiple attributes at once (batch update).

```python
updates = {
    'description': 'Updated model with new features',
    'version': '2.0',
    'context_window': 256000,
    'max_output': 16384
}

model = registry.update_model('openai', 'gpt-5', updates)
print(f"✓ Updated {len(updates)} attributes")
```

**Parameters:**
- `provider_name` (str): Provider identifier
- `model_name` (str): Model name
- `updates` (Dict): Key-value pairs to update

**Returns:** Updated Model instance

#### 3. update_model_description(provider_name: str, model_name: str, description: str) -> Model

Update model description.

```python
model = registry.update_model_description(
    'openai',
    'gpt-5',
    'Enhanced with improved reasoning capabilities'
)
```

#### 4. update_model_version(provider_name: str, model_name: str, version: str) -> Model

Update model version.

```python
model = registry.update_model_version('openai', 'gpt-5', '2.0')
```

#### 5. update_model_context_window(provider_name: str, model_name: str, context_window: int) -> Model

Update context window size.

```python
model = registry.update_model_context_window('openai', 'gpt-5', 200000)
```

**Validates:** Context window must be positive

#### 6. update_model_max_output(provider_name: str, model_name: str, max_output: int) -> Model

Update maximum output tokens.

```python
model = registry.update_model_max_output('openai', 'gpt-5', 8192)
```

**Validates:** Max output must be positive

#### 7. update_model_costs(provider_name: str, model_name: str, input_cost_per_million: float, output_cost_per_million: float) -> Model

Update model pricing.

```python
model = registry.update_model_costs(
    'openai',
    'gpt-5',
    input_cost_per_million=3.0,
    output_cost_per_million=9.0
)
print(f"✓ Updated costs: ${model.cost}")
```

**Validates:** Costs cannot be negative

#### 8. add_model_capability(provider_name: str, model_name: str, capability: str, value: Any = True) -> Model

Add or update a capability.

```python
# Add boolean capability
model = registry.add_model_capability('openai', 'gpt-5', 'vision', True)

# Add capability with value
model = registry.add_model_capability('openai', 'gpt-5', 'max_images', 50)
```

#### 9. remove_model_capability(provider_name: str, model_name: str, capability: str) -> Model

Remove a capability.

```python
model = registry.remove_model_capability('openai', 'gpt-5', 'vision')
```

#### 10. update_model_capability(provider_name: str, model_name: str, capability: str, value: Any) -> Model

Update capability value.

```python
model = registry.update_model_capability('openai', 'gpt-5', 'max_images', 100)
```

#### 11. update_model_capabilities(provider_name: str, model_name: str, capabilities: Dict[str, Any]) -> Model

Replace all capabilities.

```python
capabilities = {
    'chat': True,
    'vision': True,
    'streaming': True,
    'function_calling': True,
    'json_mode': True,
    'max_images': 50
}

model = registry.update_model_capabilities('openai', 'gpt-5', capabilities)
```

#### 12. add_model_strength(provider_name: str, model_name: str, strength: str) -> Model

Add a strength description.

```python
model = registry.add_model_strength(
    'openai',
    'gpt-5',
    'Excellent code generation'
)
```

#### 13. remove_model_strength(provider_name: str, model_name: str, strength: str) -> Model

Remove a strength description.

```python
model = registry.remove_model_strength('openai', 'gpt-5', 'Old strength')
```

#### 14. update_model_strengths(provider_name: str, model_name: str, strengths: List[str]) -> Model

Replace all strengths.

```python
strengths = [
    'Best-in-class reasoning',
    'Multilingual excellence',
    'Long context handling',
    'Advanced code generation'
]

model = registry.update_model_strengths('openai', 'gpt-5', strengths)
```

#### 15. delete_model(provider_name: str, model_name: str) -> None

Permanently delete a model.

```python
registry.delete_model('openai', 'old-model')
print("✓ Model permanently deleted")
```

**Warning:** This is permanent and cannot be undone! Consider disabling first.

### Auto-Reload API (3 Methods) [v2.2]

#### 1. start_auto_reload(interval_minutes: int = 10)

Start automatic configuration reloading.

```python
# Database implementation (no-op)
registry.start_auto_reload(interval_minutes=10)

# JSON implementation (active monitoring)
registry.start_auto_reload(interval_minutes=5)
print("Auto-reload started - monitoring for changes")
```

**Parameters:**
- `interval_minutes` (int): Check interval in minutes (default: 10)

**Behavior:**
- **Database:** No-op (changes reflected immediately)
- **JSON:** Starts background thread monitoring files

#### 2. stop_auto_reload()

Stop automatic reloading.

```python
registry.stop_auto_reload()
print("Auto-reload stopped")
```

#### 3. reload_from_storage()

Manually reload from storage.

```python
registry.reload_from_storage()
print("Reloaded from storage")
```

### Utility Methods

#### get_registry_summary() -> Dict

Get comprehensive registry statistics.

```python
summary = registry.get_registry_summary()
print(f"Total providers: {summary['total_provider_count']}")
print(f"Enabled providers: {summary['provider_count']}")
print(f"Total models: {summary['total_model_count']}")
print(f"Enabled models: {summary['enabled_model_count']}")

# JSON implementation includes auto-reload info
if 'auto_reload_enabled' in summary:
    print(f"Auto-reload: {summary['auto_reload_enabled']}")
    print(f"Check interval: {summary['auto_reload_interval_minutes']} min")
```

**Returns:** Dictionary with:
- `total_provider_count` - All providers
- `provider_count` - Enabled providers
- `enabled_provider_count` - Same as provider_count
- `total_model_count` - All models
- `enabled_model_count` - Enabled models
- `auto_reload_enabled` - Auto-reload status (JSON only)
- `auto_reload_interval_minutes` - Check interval (JSON only)

---

## CRUD Operations Guide

### Complete Model Lifecycle

```python
from model_registry_db import ModelRegistryDB
from exceptions import *

registry = ModelRegistryDB.get_instance(db_connection_pool_name="./models.db_management")

# 1. CREATE
model_data = {
    'name': 'custom-model',
    'description': 'Custom model for specific use case',
    'version': '1.0',
    'enabled': True,
    'context_window': 8192,
    'max_output': 4096,
    'cost': {
        'input_per_1m': 1.0,
        'output_per_1m': 2.0
    },
    'capabilities': {
        'chat': True,
        'streaming': True
    },
    'strengths': [
        'Fast inference',
        'Cost effective'
    ],
    'release_date': '2024-01-01'
}

try:
    model = registry.create_model('my_provider', model_data)
    print(f"✓ Created: {model.name}")
except ModelAlreadyExistsException:
    print("Model exists, updating instead...")
    model = registry.update_model('my_provider', model_data['name'], model_data)

# 2. READ
model = registry.get_model_from_provider_by_name('my_provider', 'custom-model')
print(f"Current version: {model.version}")
print(f"Capabilities: {list(model.capabilities.keys())}")

# 3. UPDATE
# Update basic properties
registry.update_model_version('my_provider', 'custom-model', '2.0')
registry.update_model_context_window('my_provider', 'custom-model', 16384)
registry.update_model_costs('my_provider', 'custom-model', 0.8, 1.5)

# Manage capabilities
registry.add_model_capability('my_provider', 'custom-model', 'function_calling', True)
registry.add_model_capability('my_provider', 'custom-model', 'vision', True)

# Manage strengths
registry.add_model_strength('my_provider', 'custom-model', 'Excellent accuracy')
registry.add_model_strength('my_provider', 'custom-model', 'Low latency')

# Batch update
updates = {
    'description': 'Updated custom model with new features',
    'max_output': 8192
}
registry.update_model('my_provider', 'custom-model', updates)

# 4. DELETE
# Soft delete first (reversible)
registry.disable_model('my_provider', 'custom-model')
print("✓ Model disabled")

# Later, if truly not needed (hard delete - permanent)
confirm = input("Permanently delete? (yes/no): ")
if confirm.lower() == 'yes':
    registry.delete_model('my_provider', 'custom-model')
    print("✓ Model deleted permanently")
```

### Error Handling

```python
from exceptions import *

try:
    model = registry.create_model('provider', model_data)
    
except ModelAlreadyExistsException as e:
    print(f"Model '{e.model_name}' already exists in '{e.provider_name}'")
    # Option 1: Update instead
    model = registry.update_model('provider', e.model_name, model_data)
    # Option 2: Use existing
    model = registry.get_model_from_provider_by_name('provider', e.model_name)
    
except ProviderNotFoundException as e:
    print(f"Provider '{e.provider_name}' not found")
    print("Create provider first or check spelling")
    
except ValueError as e:
    print(f"Invalid value: {e}")
    # Fix data and retry
    
except Exception as e:
    print(f"Unexpected error: {e}")
    # Log and handle appropriately
```

---

## Advanced Features

### Auto-Reload for Development

Perfect when configuration changes frequently:

```python
from model_registry_json import ModelRegistryJSON

# Initialize with auto-reload
registry = ModelRegistryJSON.get_instance("./json_configs")
registry.start_auto_reload(interval_minutes=2)

print("Registry is monitoring configuration files...")
print("Edit JSON files and changes will be detected automatically!")

# Your application runs here...
# Configuration changes are automatically picked up

# Clean shutdown
registry.stop_auto_reload()
```

### Capability Validation in Queries

Ensure models have required capabilities:

```python
from exceptions import NoModelsAvailableException

# Old way (2 steps - v2.2 and earlier)
model = registry.get_model_from_provider_by_name("google", "gemini-1.5-pro")
if not model.has_capability("vision"):
    raise Exception("No vision support")

# New way (1 step - v2.3+)
try:
    model = registry.get_model_from_provider_by_name_capability(
        "google",
        "gemini-1.5-pro",
        "vision"
    )
    print(f"✓ {model.name} has vision capability")
    # Use model with confidence
    process_image(model, image_data)
    
except NoModelsAvailableException:
    print("✗ Model doesn't support vision")
    # Use fallback or different model
    model = get_fallback_model()
```

### Cost Comparison

Compare models for specific workloads:

```python
# Define workload
workload = {
    'input_tokens': 10000,
    'output_tokens': 1000
}

# Get all chat models
chat_models = registry.get_all_models_for_capability("chat")

# Calculate and compare costs
costs = []
for provider_name, model in chat_models:
    cost = model.calculate_cost(
        workload['input_tokens'],
        workload['output_tokens']
    )
    costs.append((provider_name, model.name, cost, model.context_window))

# Sort by cost
costs.sort(key=lambda x: x[2])

# Display results
print(f"Cost comparison for {workload['input_tokens']} input + {workload['output_tokens']} output tokens:")
print(f"{'Provider':<15} {'Model':<25} {'Cost':>10} {'Context':>12}")
print("-" * 65)
for provider, model_name, cost, context in costs[:10]:
    print(f"{provider:<15} {model_name:<25} ${cost:>9.4f} {context:>11,}")
```

### Dynamic Model Management

Monitor and adjust based on usage:

```python
def optimize_model_selection(usage_stats: Dict[Tuple[str, str], int]):
    """Dynamically enable/disable models based on usage."""
    
    low_usage_threshold = 100
    high_usage_threshold = 10000
    
    for (provider_name, model_name), usage in usage_stats.items():
        if usage < low_usage_threshold:
            # Disable low-usage models
            registry.disable_model(provider_name, model_name)
            print(f"Disabled {provider_name}/{model_name} (usage: {usage})")
        
        elif usage > high_usage_threshold:
            # Ensure high-usage models are enabled
            registry.enable_model(provider_name, model_name)
            print(f"Enabled {provider_name}/{model_name} (usage: {usage})")

# Example usage
usage_stats = {
    ('openai', 'gpt-4o'): 50000,
    ('openai', 'gpt-3.5-turbo'): 25,
    ('anthropic', 'claude-3-5-sonnet-20241022'): 15000,
}

optimize_model_selection(usage_stats)
```

---

## Production Deployment

### Pre-Deployment Checklist

**Testing:**
- [ ] All tests pass (`python quick_test.py`)
- [ ] CRUD tests pass (`python test_model_crud.py`)
- [ ] Provider configurations validated
- [ ] JSON files validated (if using JSON implementation)

**Environment:**
- [ ] Python 3.8+ installed on server
- [ ] All .py files deployed
- [ ] Data directory created with correct permissions
- [ ] Database path configured
- [ ] Logging configured

**Backups:**
- [ ] Backup strategy defined
- [ ] Backup scripts in place
- [ ] Recovery procedures documented

### Production Setup (Database Implementation)

```bash
# Create directory structure
sudo mkdir -p /opt/abhikarta/{data,configs,logs,backups}
sudo chown appuser:appuser /opt/abhikarta -R

# Copy files
sudo cp *.py /opt/abhikarta/
sudo cp configs/*.json /opt/abhikarta/configs/

# Set permissions
sudo chmod 755 /opt/abhikarta
sudo chmod 644 /opt/abhikarta/*.py
sudo chmod 755 /opt/abhikarta/data
sudo chmod 755 /opt/abhikarta/logs

# Initialize database
cd /opt/abhikarta
python3 << EOF
from model_registry_db import ModelRegistryDB
registry = ModelRegistryDB.get_instance('/opt/abhikarta/data/models.db')
registry.load_json_directory('/opt/abhikarta/configs')
summary = registry.get_registry_summary()
print(f'Initialized: {summary["provider_count"]} providers, {summary["total_model_count"]} models')
EOF
```

### Health Check Implementation

```python
def health_check():
    """Health check endpoint for monitoring."""
    try:
        summary = registry.get_registry_summary()
        
        # Check basic functionality
        providers = registry.get_all_providers()
        models = registry.get_total_model_count()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'providers': summary['provider_count'],
            'models': summary['total_model_count'],
            'enabled_providers': summary['enabled_provider_count'],
            'enabled_models': summary['enabled_model_count']
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }

# Use in Flask/FastAPI
@app.get("/health")
def health():
    return health_check()
```

### Logging Configuration

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
log_file = '/opt/abhikarta/logs/registry.log'
handler = RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

logger = logging.getLogger('abhikarta_registry')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Log operations
logger.info("Registry initialized")
logger.info(f"Loaded {provider_count} providers")
```

### Backup Script

```bash
#!/bin/bash
# backup_registry.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/abhikarta/backups"
DATA_DIR="/opt/abhikarta/data"
CONFIG_DIR="/opt/abhikarta/configs"

# Backup database
cp $DATA_DIR/models.db_management $BACKUP_DIR/models_${DATE}.db_management
echo "✓ Database backed up"

# Backup configurations
tar -czf $BACKUP_DIR/configs_${DATE}.tar.gz $CONFIG_DIR/*.json
echo "✓ Configurations backed up"

# Cleanup old backups (keep last 30 days)
find $BACKUP_DIR -name "models_*.db" -mtime +30 -delete
find $BACKUP_DIR -name "configs_*.tar.gz" -mtime +30 -delete
echo "✓ Old backups cleaned up"

echo "Backup completed: ${DATE}"
```

Make executable and schedule:
```bash
chmod +x backup_registry.sh
# Add to crontab: daily at 2 AM
echo "0 2 * * * /opt/abhikarta/backup_registry.sh" | crontab -
```

### Monitoring

```python
def collect_metrics():
    """Collect metrics for monitoring system."""
    summary = registry.get_registry_summary()
    
    metrics = {
        'registry.providers.total': summary['total_provider_count'],
        'registry.providers.enabled': summary['provider_count'],
        'registry.models.total': summary['total_model_count'],
        'registry.models.enabled': summary['enabled_model_count'],
    }
    
    # Add to your monitoring system (Prometheus, CloudWatch, etc.)
    return metrics
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy application files
COPY *.py /app/
COPY configs/ /app/configs/

# Create data directory
RUN mkdir -p /app/data

# Initialize database
RUN python3 -c "from model_registry_db import ModelRegistryDB; \
                registry = ModelRegistryDB.get_instance('/app/data/models.db'); \
                registry.load_json_directory('/app/configs'); \
                print('Database initialized')"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV REGISTRY_DB_PATH=/app/data/models.db

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python3 -c "from model_registry_db import ModelRegistryDB; \
                  r = ModelRegistryDB.get_instance('/app/data/models.db'); \
                  print('OK' if r.get_provider_count() > 0 else 'FAIL')"

# Your application entry point
CMD ["python3", "your_app.py"]
```

Build and run:
```bash
docker build -t abhikarta-registry .
docker run -d \
  -v /path/to/data:/app/data \
  -v /path/to/configs:/app/configs \
  --name registry \
  abhikarta-registry
```

---

## Best Practices

### 1. Use Batch Updates

**Bad:**
```python
# Multiple individual updates (slow, multiple transactions)
registry.update_model_version('provider', 'model', '2.0')
registry.update_model_description('provider', 'model', 'New description')
registry.update_model_context_window('provider', 'model', 16384)
registry.update_model_max_output('provider', 'model', 8192)
```

**Good:**
```python
# Single batch update (fast, single transaction)
updates = {
    'version': '2.0',
    'description': 'New description',
    'context_window': 16384,
    'max_output': 8192
}
registry.update_model('provider', 'model', updates)
```

### 2. Validate Before Creating

**Good:**
```python
try:
    # Try to get existing model
    model = registry.get_model_from_provider_by_name('provider', 'model')
    print("Model exists, updating...")
    registry.update_model('provider', 'model', model_data)
except ModelNotFoundException:
    print("Creating new model...")
    registry.create_model('provider', model_data)
```

### 3. Soft Delete Before Hard Delete

**Good:**
```python
# Step 1: Soft delete (reversible)
registry.disable_model('provider', 'model')
print("Model disabled - can be re-enabled if needed")

# Test system without the model...

# Step 2: Hard delete only if truly not needed
confirm = input("Permanently delete? (yes/no): ")
if confirm.lower() == 'yes':
    registry.delete_model('provider', 'model')
    print("Model permanently deleted")
```

### 4. Use Appropriate Implementation

**Development:**
```python
# JSON implementation with auto-reload
registry = ModelRegistryJSON.get_instance("./configs")
registry.start_auto_reload(interval_minutes=2)
# Changes detected automatically
```

**Production:**
```python
# Database implementation for performance
registry = ModelRegistryDB.get_instance("/opt/app/data/models.db_management")
# No polling overhead
```

### 5. Handle All Exceptions

**Good:**
```python
from exceptions import *

try:
    model = registry.get_model_from_provider_by_name_capability(
        provider, model_name, capability
    )
    # Use model
    result = process_with_model(model, data)
    
except ModelNotFoundException:
    logger.error(f"Model not found: {model_name}")
    model = get_fallback_model()
    
except NoModelsAvailableException:
    logger.error(f"Model lacks capability: {capability}")
    model = get_alternative_model()
    
except ProviderNotFoundException:
    logger.error(f"Provider not found: {provider}")
    raise  # Re-raise critical errors
    
except Exception as e:
    logger.exception("Unexpected error")
    raise
```

### 6. Keep Configurations in Version Control

**Good:**
```bash
# Track configuration changes
git add json_configs/*.json
git commit -m "Updated GPT-4 pricing for November 2025"
git push

# Tag releases
git tag -a v1.2.3 -m "Production configuration 2025-11"
git push --tags
```

### 7. Validate Before Deployment

**Good:**
```python
def validate_config(config_file: str) -> bool:
    """Validate provider configuration."""
    import json
    
    try:
        with open(config_file) as f:
            data = json.load(f)
        
        # Check required fields
        required = ['provider', 'api_base_url', 'enabled', 'models']
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate each model
        for model in data['models']:
            required_model = [
                'name', 'description', 'version', 'enabled',
                'context_window', 'max_output', 'cost'
            ]
            for field in required_model:
                if field not in model:
                    raise ValueError(f"Model missing field: {field}")
            
            # Validate cost structure
            if 'input_per_1m' not in model['cost']:
                raise ValueError("Cost missing input_per_1m")
            if 'output_per_1m' not in model['cost']:
                raise ValueError("Cost missing output_per_1m")
        
        print(f"✓ {config_file} is valid")
        return True
        
    except Exception as e:
        print(f"✗ {config_file} validation failed: {e}")
        return False

# Validate before loading
if validate_config('new_provider.json'):
    registry.load_json_file('new_provider.json')
else:
    print("Fix configuration errors before deploying")
```

---

## Troubleshooting Guide

### Common Issues

#### 1. ModuleNotFoundError

**Error:**
```
ModuleNotFoundError: No module named 'model_registry'
```

**Solutions:**
```python
# Add to Python path
import sys
sys.path.append('/path/to/abhikarta-registry')

# Or ensure all .py files in same directory as your script
```

#### 2. ProviderNotFoundException

**Error:**
```
ProviderNotFoundException: Provider 'openai' not found in registry
```

**Solutions:**
```python
# Check provider name spelling
providers = registry.get_all_providers(include_disabled=True)
print("Available providers:", list(providers.keys()))

# Check if provider is disabled
registry.enable_provider('openai')

# Reload configurations
registry.reload_from_storage()

# For JSON implementation: check file exists
# ls json_configs/openai.json
```

#### 3. ModelNotFoundException

**Error:**
```
ModelNotFoundException: Model 'gpt-5' not found in provider 'openai'
```

**Solutions:**
```python
# Check model name spelling
models = registry.get_all_models_from_provider('openai', include_disabled=True)
print("Available models:", list(models.keys()))

# Check if model is disabled
registry.enable_model('openai', 'gpt-5')

# Create model if it doesn't exist
if needed:
    registry.create_model('openai', model_data)
```

#### 4. NoModelsAvailableException

**Error:**
```
NoModelsAvailableException: No models available for criteria: capability vision
```

**Solutions:**
```python
# Check which models have the capability
all_models = registry.get_all_models_for_capability('vision')
print(f"Found {len(all_models)} vision models")

# Add capability to existing model
registry.add_model_capability('provider', 'model', 'vision', True)

# Use different capability
models = registry.get_all_models_for_capability('chat')
```

#### 5. Database Locked

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Solutions:**
```python
# Close and reinitialize
registry = None
ModelRegistryDB.reset_instance()
registry = ModelRegistryDB.get_instance(db_path)

# Or increase timeout
import sqlite3
conn = sqlite3.connect('models.db_management', timeout=30.0)
```

#### 6. Invalid JSON Configuration

**Error:**
```
json.JSONDecodeError: Expecting property name enclosed in double quotes
```

**Solutions:**
```bash
# Validate JSON syntax
python3 -m json.tool config.json

# Common issues:
# - Trailing commas
# - Single quotes instead of double quotes
# - Missing commas between items
# - Unescaped special characters
```

#### 7. Auto-Reload Not Working

**Problem:** File changes not detected

**Solutions:**
```python
# Only works with JSON implementation, not database
from model_registry_json import ModelRegistryJSON

registry = ModelRegistryJSON.get_instance("./configs")
registry.start_auto_reload(interval_minutes=5)

# Check status
summary = registry.get_registry_summary()
print(f"Auto-reload enabled: {summary.get('auto_reload_enabled', False)}")

# Manually trigger reload
registry.reload_from_storage()
```

#### 8. Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied: '/opt/app/data/models.db'
```

**Solutions:**
```bash
# Fix file permissions
chmod 644 /opt/app/data/models.db_management
chmod 755 /opt/app/data

# Or run with appropriate user
sudo -u appuser python3 app.py

# Check ownership
ls -l /opt/app/data/models.db_management
```

### Debug Mode

Enable detailed logging:

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now operations will log detailed information
model = registry.get_model_from_provider_by_name('openai', 'gpt-4o')
```

### Performance Issues

**Slow Queries:**

```python
import time

# Profile query performance
start = time.time()
models = registry.get_all_models_for_capability("chat")
elapsed = time.time() - start
print(f"Query took {elapsed:.3f} seconds")

# If slow with database:
# - Ensure indexes are created (automatic on init)
# - Check database size
# - Consider VACUUM operation
# - Use connection pooling

# If slow with JSON:
# - Reduce number of JSON files (combine providers)
# - Consider switching to database for 100+ models
# - Disable auto-reload in production
```

### Getting Help

If issues persist:

1. **Check documentation** - Architecture Guide for design details
2. **Review test files** - `quick_test.py` and `test_model_crud.py` for examples
3. **Enable debug logging** - See detailed operation info
4. **Contact support** - ajsinha@gmail.com

---

## Configuration Reference

### Provider Configuration Format

```json
{
  "provider": "provider_name",
  "api_base_url": "https://api.provider.com/v1",
  "authentication_type": "bearer_token",
  "enabled": true,
  "models": [
    {
      "name": "model-name",
      "description": "Model description",
      "version": "1.0",
      "enabled": true,
      "context_window": 128000,
      "max_output": 4096,
      "cost": {
        "input_per_1m": 2.50,
        "output_per_1m": 10.00
      },
      "capabilities": {
        "chat": true,
        "vision": false,
        "streaming": true,
        "function_calling": true
      },
      "strengths": [
        "Fast inference",
        "Good reasoning"
      ],
      "release_date": "2024-01-01"
    }
  ]
}
```

### Required Fields

**Provider Level:**
- `provider` - Provider identifier (string)
- `api_base_url` - API endpoint (string)
- `enabled` - Enabled status (boolean)
- `models` - Array of model configurations

**Model Level:**
- `name` - Model name (string)
- `description` - Model description (string)
- `version` - Version string (string)
- `enabled` - Enabled status (boolean)
- `context_window` - Context window size (integer)
- `max_output` - Maximum output tokens (integer)
- `cost` - Cost dictionary with `input_per_1m` and `output_per_1m` (floats)
- `capabilities` - Capabilities dictionary
- `release_date` - ISO date string

### Optional Fields

**Model Level:**
- `strengths` - Array of strength descriptions
- `supports_streaming` - Streaming support (boolean)
- `supports_function_calling` - Function calling support (boolean)
- `parameters` - Model parameter count (string)
- `license` - License type (string)

---

## Code Examples

### Example 1: Basic Usage

```python
from model_registry_db import ModelRegistryDB

# Initialize
registry = ModelRegistryDB.get_instance("./models.db_management")

# Load configurations
registry.load_json_directory("./configs")

# Get summary
summary = registry.get_registry_summary()
print(f"Providers: {summary['provider_count']}")
print(f"Models: {summary['total_model_count']}")

# Query specific model
model = registry.get_model_from_provider_by_name("openai", "gpt-4o")
print(f"\nModel: {model.name}")
print(f"Context: {model.context_window:,} tokens")
print(f"Max output: {model.max_output:,} tokens")

# Calculate cost
cost = model.calculate_cost(10000, 1000)
print(f"Cost for 10k input + 1k output: ${cost:.4f}")

# Find cheapest
provider, model, cost = registry.get_cheapest_model_for_capability(
    "chat", 10000, 1000
)
print(f"\nCheapest: {provider}/{model.name} - ${cost:.4f}")
```

### Example 2: Cost Comparison

```python
# Compare costs across providers
workload = (10000, 1000)  # input, output tokens

chat_models = registry.get_all_models_for_capability("chat")
print(f"Comparing {len(chat_models)} chat models:\n")

costs = []
for provider, model in chat_models:
    cost = model.calculate_cost(*workload)
    costs.append((provider, model.name, cost))

costs.sort(key=lambda x: x[2])

print(f"{'Provider':<15} {'Model':<30} {'Cost':>10}")
print("-" * 57)
for provider, model_name, cost in costs[:10]:
    print(f"{provider:<15} {model_name:<30} ${cost:>9.4f}")
```

### Example 3: Dynamic Model Management

```python
# Monitor usage and adjust
usage_data = load_usage_statistics()

for (provider, model_name), count in usage_data.items():
    if count < 10:  # Low usage
        print(f"Disabling low-usage model: {provider}/{model_name}")
        registry.disable_model(provider, model_name)
    elif count > 1000:  # High usage
        print(f"Ensuring high-usage model is enabled: {provider}/{model_name}")
        registry.enable_model(provider, model_name)
```

### Example 4: Capability-Based Selection

```python
def select_model_for_task(task_type: str, requires_vision: bool = False):
    """Select best model for task."""
    
    # Determine required capability
    capability = "chat"
    if requires_vision:
        capability = "vision"
    
    # Get models with capability
    models = registry.get_all_models_for_capability(capability)
    
    if not models:
        raise Exception(f"No models available for {capability}")
    
    # Find cheapest for typical workload
    provider, model, cost = registry.get_cheapest_model_for_capability(
        capability, 10000, 1000
    )
    
    print(f"Selected: {provider}/{model.name} (${cost:.4f})")
    return model

# Use
model = select_model_for_task("chat", requires_vision=True)
result = process_with_model(model, data)
```

### Example 5: Batch Processing

```python
def process_batch(items: List[str]):
    """Process batch with cost optimization."""
    
    # Find cheapest model
    provider, model, _ = registry.get_cheapest_model_for_capability(
        "chat", 5000, 500
    )
    
    print(f"Using: {provider}/{model.name}")
    
    total_cost = 0
    results = []
    
    for item in items:
        # Process item
        result = process_item(model, item)
        results.append(result)
        
        # Track cost
        cost = model.calculate_cost(5000, 500)
        total_cost += cost
    
    print(f"Processed {len(items)} items")
    print(f"Total cost: ${total_cost:.4f}")
    
    return results
```

---

**Abhikarta Model Registry System v2.4**  
**Professional • Production-Ready • Comprehensively Documented**

**Copyright © 2025-2030 Ashutosh Sinha - All Rights Reserved**  
**Email:** ajsinha@gmail.com

**Last Updated: November 8, 2025**