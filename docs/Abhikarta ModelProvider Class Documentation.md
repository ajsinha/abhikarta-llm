# Abhikarta ModelProvider Class Documentation

**Version:** 1.0.0  
**Last Updated:** November 6, 2025  
**Module:** `model_provider.py`

---

## Copyright and Legal Notice

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email:** ajsinha@gmail.com

### Legal Notice

This document and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use of this document or the software system it describes is strictly prohibited without explicit written permission from the copyright holder. This document is provided "as is" without warranty of any kind, either expressed or implied. The copyright holder shall not be liable for any damages arising from the use of this document or the software system it describes.

**Patent Pending:** Certain architectural patterns and implementations described in this document may be subject to patent applications.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Class Reference](#class-reference)
4. [Usage Examples](#usage-examples)
5. [Method Reference](#method-reference)
6. [Integration Guide](#integration-guide)
7. [Best Practices](#best-practices)
8. [Error Handling](#error-handling)

---

## Overview

The `ModelProvider` class is a comprehensive Python implementation for managing LLM provider configurations loaded from JSON files. It provides a structured, object-oriented interface for:

- Loading provider configurations from JSON
- Managing collections of models
- Querying models by name and capabilities
- Finding cost-optimized models
- Enable/disable functionality for providers and models
- Hot-reloading configurations

### Key Features

✅ **JSON-based Configuration** - Load from standard JSON format  
✅ **Type-Safe** - Full type hints and dataclass support  
✅ **Enable/Disable** - Granular control over providers and models  
✅ **Capability-Based Queries** - Find models by required capabilities  
✅ **Cost Optimization** - Automatically find cheapest models  
✅ **Hot Reload** - Update configuration without restart  
✅ **Comprehensive API** - Rich set of query methods  
✅ **Production Ready** - Error handling and validation  

---

## Architecture

### Class Hierarchy

```
ModelProvider (main class)
├── provider_name: str
├── api_version: str
├── base_url: Optional[str]
├── notes: Dict[str, Any]
├── enabled: bool
├── config_file: Path
├── raw_config: Dict[str, Any]
└── models: Dict[str, Model]
        │
        └── Model (inner class)
            ├── name: str
            ├── version: str
            ├── description: str
            ├── context_window: int
            ├── max_output: int
            ├── cost: Dict[str, Any]
            ├── capabilities: Dict[str, Any]
            ├── strengths: List[str]
            ├── enabled: bool
            └── raw_data: Dict[str, Any]
```

### Data Flow

```
JSON Config File
      │
      ▼
ModelProvider.__init__()
      │
      ▼
ModelProvider.reload()
      │
      ├─── Validate JSON structure
      ├─── Load provider metadata
      ├─── Create Model objects
      └─── Store in models dict
      │
      ▼
Ready for Queries
      │
      ├─── get_model_by_name()
      ├─── get_models_for_capability()
      ├─── get_cheapest_model_for_capability()
      └─── etc.
```

---

## Class Reference

### Model Class

The `Model` class represents a single LLM model with all its configuration.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | str | Unique model identifier |
| `version` | str | Model version string |
| `description` | str | Human-readable description |
| `context_window` | int | Maximum input tokens |
| `max_output` | int | Maximum output tokens |
| `cost` | Dict | Pricing information |
| `capabilities` | Dict | Capability flags |
| `strengths` | List[str] | Key strengths |
| `provider` | Optional[str] | Original provider |
| `model_id` | Optional[str] | Alternative API ID |
| `parameters` | Optional[str] | Model size (e.g., "70B") |
| `license` | Optional[str] | License information |
| `performance` | Optional[Dict] | Performance metrics |
| `enabled` | bool | Enable/disable flag |
| `raw_data` | Dict | Complete raw JSON |

#### Key Methods

**`has_capability(capability: Union[str, ModelCapability]) -> bool`**
- Check if model supports a capability
- Accepts string or enum
- Returns True/False

**`get_estimated_cost(input_tokens: int, output_tokens: int) -> float`**
- Calculate cost for token counts
- Handles per-1K, per-1M, and tiered pricing
- Returns cost in USD

**`get_capabilities_list() -> List[str]`**
- Get list of all capabilities
- Returns only enabled capabilities
- Useful for display/debugging

**`enable() / disable()`**
- Enable or disable the model
- Affects queries that filter by enabled state

---

### ModelProvider Class

The `ModelProvider` class manages a collection of models from a single provider.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `provider_name` | str | Provider identifier |
| `api_version` | str | API version |
| `base_url` | Optional[str] | API endpoint |
| `notes` | Dict | Provider documentation |
| `models` | Dict[str, Model] | Models keyed by name |
| `enabled` | bool | Provider enable/disable |
| `config_file` | Path | Path to JSON config |
| `raw_config` | Dict | Complete JSON data |

#### Constructor

```python
ModelProvider(config_file: Union[str, Path], auto_load: bool = True)
```

**Parameters:**
- `config_file`: Path to JSON configuration file
- `auto_load`: Whether to load immediately (default: True)

**Raises:**
- `FileNotFoundError`: If config file doesn't exist
- `json.JSONDecodeError`: If invalid JSON
- `ValueError`: If missing required fields

---

## Usage Examples

### Example 1: Basic Usage

```python
from model_management import ModelProvider

# Load provider
provider = ModelProvider("configs/anthropic.json")

# Get basic info
print(f"Provider: {provider.provider_name}")
print(f"Models: {provider.get_model_count()}")
print(f"API Version: {provider.api_version}")

# Get a specific model
model = provider.get_model_by_name("claude-3-7-sonnet-20250219")
if model:
    print(f"Model: {model.description}")
    print(f"Context: {model.context_window} tokens")
    print(f"Capabilities: {model.get_capabilities_list()}")
```

**Output:**
```
Provider: anthropic
Models: 10
API Version: 2023-06-01
Model: Most intelligent Claude model with extended thinking
Context: 200000 tokens
Capabilities: ['chat', 'streaming', 'vision', 'function_calling', ...]
```

### Example 2: Capability-Based Queries

```python
# Find all models with vision
vision_models = provider.get_models_for_capability("vision")
print(f"Found {len(vision_models)} models with vision:")
for model in vision_models:
    print(f"  - {model.name}")

# Get model only if it has specific capability
model = provider.get_model_by_name_and_capability(
    "claude-3-5-haiku-20241022",
    "vision"
)
if model:
    print(f"{model.name} supports vision")
else:
    print("Model doesn't support vision or doesn't exist")
```

**Output:**
```
Found 7 models with vision:
  - claude-3-7-sonnet-20250219
  - claude-3-5-sonnet-20241022
  - claude-3-5-haiku-20241022
  - claude-3-opus-20240229
  - claude-3-sonnet-20240229
  - claude-3-haiku-20240307
claude-3-5-haiku-20241022 supports vision
```

### Example 3: Cost Optimization

```python
# Find cheapest model for vision capability
cheapest = provider.get_cheapest_model_for_capability(
    "vision",
    input_tokens=10000,
    output_tokens=2000
)

if cheapest:
    cost = cheapest.get_estimated_cost(10000, 2000)
    print(f"Cheapest vision model: {cheapest.name}")
    print(f"Estimated cost: ${cost:.4f}")
    print(f"Description: {cheapest.description}")
```

**Output:**
```
Cheapest vision model: claude-3-haiku-20240307
Estimated cost: $0.0275
Description: Fast and compact Claude 3 model
```

### Example 4: Enable/Disable Models

```python
# Disable expensive models
provider.disable_model("claude-3-opus-20240229")

# Check enabled models
enabled_count = provider.get_model_count()
total_count = provider.get_model_count(include_disabled=True)
print(f"Enabled: {enabled_count}/{total_count} models")

# Get model (won't return disabled models)
model = provider.get_model_by_name("claude-3-opus-20240229")
print(f"Opus model available: {model is not None}")  # False

# Re-enable
provider.enable_model("claude-3-opus-20240229")
model = provider.get_model_by_name("claude-3-opus-20240229")
print(f"Opus model available: {model is not None}")  # True
```

### Example 5: Hot Reload Configuration

```python
# Initial load
provider = ModelProvider("configs/anthropic.json")
print(f"Initial models: {provider.get_model_count()}")

# ... JSON file is modified externally ...

# Reload configuration
provider.reload()
print(f"After reload: {provider.get_model_count()}")
print("Configuration reloaded successfully!")
```

### Example 6: Cost Calculation

```python
model = provider.get_model_by_name("claude-3-5-sonnet-20241022")

# Calculate cost for different scenarios
scenarios = [
    (1000, 500, "Short chat"),
    (10000, 2000, "Medium task"),
    (100000, 5000, "Long document analysis"),
]

for input_tok, output_tok, desc in scenarios:
    cost = model.get_estimated_cost(input_tok, output_tok)
    print(f"{desc}: ${cost:.4f}")
```

**Output:**
```
Short chat: $0.0105
Medium task: $0.0600
Long document analysis: $1.0500
```

### Example 7: Capability Summary

```python
# Get summary of all capabilities
summary = provider.get_capabilities_summary()

print("Capability Support Summary:")
for capability, count in sorted(summary.items()):
    print(f"  {capability}: {count} models")
```

**Output:**
```
Capability Support Summary:
  batch_api: 7 models
  chat: 10 models
  function_calling: 7 models
  prompt_caching: 7 models
  streaming: 10 models
  vision: 7 models
  ...
```

### Example 8: Load Multiple Providers

```python
from model_management import load_providers

# Load all providers from directory
providers = load_providers("configs/")

print(f"Loaded {len(providers)} providers:")
for name, provider in providers.items():
    print(f"  {name}: {provider.get_model_count()} models")

# Find cheapest vision model across all providers
cheapest_overall = None
min_cost = float('inf')

for provider in providers.values():
    cheapest = provider.get_cheapest_model_for_capability("vision")
    if cheapest:
        cost = cheapest.get_estimated_cost(5000, 1000)
        if cost < min_cost:
            min_cost = cost
            cheapest_overall = (provider.provider_name, cheapest)

if cheapest_overall:
    provider_name, model = cheapest_overall
    print(f"\nCheapest vision model overall:")
    print(f"  Provider: {provider_name}")
    print(f"  Model: {model.name}")
    print(f"  Cost: ${min_cost:.4f}")
```

---

## Method Reference

### ModelProvider Methods

#### `__init__(config_file, auto_load=True)`
Initialize provider from JSON file.

**Parameters:**
- `config_file` (str | Path): Path to JSON config
- `auto_load` (bool): Load immediately (default: True)

**Raises:** FileNotFoundError, JSONDecodeError, ValueError

---

#### `reload() -> None`
Reload configuration from JSON file.

**Use Case:** Hot-reload config changes  
**Raises:** FileNotFoundError, JSONDecodeError, ValueError

---

#### `get_model_by_name(model_name) -> Optional[Model]`
Get model by name.

**Parameters:**
- `model_name` (str): Model identifier

**Returns:** Model object or None

**Example:**
```python
model = provider.get_model_by_name("claude-3-7-sonnet-20250219")
```

---

#### `get_model_by_name_and_capability(model_name, capability) -> Optional[Model]`
Get model by name only if it has the capability.

**Parameters:**
- `model_name` (str): Model identifier
- `capability` (str | ModelCapability): Required capability

**Returns:** Model object or None

**Example:**
```python
model = provider.get_model_by_name_and_capability(
    "claude-3-5-haiku-20241022",
    "vision"
)
```

---

#### `get_models_for_capability(capability) -> List[Model]`
Get all models supporting a capability.

**Parameters:**
- `capability` (str | ModelCapability): Required capability

**Returns:** List of Model objects

**Example:**
```python
vision_models = provider.get_models_for_capability("vision")
```

---

#### `get_cheapest_model_for_capability(capability, input_tokens=1000, output_tokens=500) -> Optional[Model]`
Get most cost-effective model for a capability.

**Parameters:**
- `capability` (str | ModelCapability): Required capability
- `input_tokens` (int): Input token count for cost calc (default: 1000)
- `output_tokens` (int): Output token count for cost calc (default: 500)

**Returns:** Model object with lowest cost or None

**Example:**
```python
cheapest = provider.get_cheapest_model_for_capability(
    "vision",
    input_tokens=10000,
    output_tokens=2000
)
```

---

#### `get_all_models(include_disabled=False) -> List[Model]`
Get all models from provider.

**Parameters:**
- `include_disabled` (bool): Include disabled models (default: False)

**Returns:** List of Model objects

---

#### `get_model_count(include_disabled=False) -> int`
Get count of models.

**Parameters:**
- `include_disabled` (bool): Include disabled models (default: False)

**Returns:** Number of models

---

#### `enable() / disable() -> None`
Enable or disable the entire provider.

**Effect:** When disabled, all query methods return empty results

---

#### `enable_model(model_name) -> bool`
Enable a specific model.

**Parameters:**
- `model_name` (str): Model to enable

**Returns:** True if found and enabled, False otherwise

---

#### `disable_model(model_name) -> bool`
Disable a specific model.

**Parameters:**
- `model_name` (str): Model to disable

**Returns:** True if found and disabled, False otherwise

---

#### `get_capabilities_summary() -> Dict[str, int]`
Get capability support summary.

**Returns:** Dict mapping capability names to count of supporting models

**Example:**
```python
summary = provider.get_capabilities_summary()
# {'vision': 7, 'chat': 10, 'streaming': 10, ...}
```

---

### Model Methods

#### `has_capability(capability) -> bool`
Check if model has a capability.

**Parameters:**
- `capability` (str | ModelCapability): Capability to check

**Returns:** True if model has capability, False otherwise

---

#### `get_estimated_cost(input_tokens, output_tokens) -> float`
Calculate estimated cost.

**Parameters:**
- `input_tokens` (int): Input token count
- `output_tokens` (int): Output token count

**Returns:** Estimated cost in USD

**Pricing Support:**
- Per-1K pricing (OpenAI style)
- Per-1M pricing (Anthropic style)
- Tiered pricing (Google Gemini style)

---

#### `get_capabilities_list() -> List[str]`
Get list of all capabilities.

**Returns:** List of capability names (strings)

---

#### `enable() / disable() -> None`
Enable or disable the model.

---

## Integration Guide

### Step 1: Prepare Configuration Files

Ensure your JSON config files follow the standard format:

```json
{
  "provider": "anthropic",
  "api_version": "2023-06-01",
  "base_url": "https://api.anthropic.com",
  "models": [
    {
      "name": "claude-3-7-sonnet-20250219",
      "version": "3.7",
      "description": "...",
      "context_window": 200000,
      "max_output": 8192,
      "cost": { ... },
      "capabilities": { ... }
    }
  ]
}
```

### Step 2: Initialize Provider

```python
from model_management import ModelProvider

# Single provider
provider = ModelProvider("configs/anthropic.json")

# Multiple providers
from model_management import load_providers

providers = load_providers("configs/")
```

### Step 3: Query Models

```python
# Get specific model
model = provider.get_model_by_name("claude-3-7-sonnet-20250219")

# Find by capability
vision_models = provider.get_models_for_capability("vision")

# Find cheapest
cheapest = provider.get_cheapest_model_for_capability("vision")
```

### Step 4: Use Model Information

```python
# Check capabilities
if model.has_capability("vision"):
    # Process with vision

# Calculate cost
cost = model.get_estimated_cost(input_tokens, output_tokens)

# Get details
print(f"Context window: {model.context_window}")
print(f"Max output: {model.max_output}")
```

### Step 5: Handle Enable/Disable

```python
# Disable expensive models
provider.disable_model("claude-3-opus-20240229")

# Disable entire provider temporarily
provider.disable()

# Re-enable when needed
provider.enable()
```

---

## Best Practices

### 1. Configuration Management

✅ **DO:**
- Store config files in a dedicated directory
- Use version control for config files
- Validate JSON before deployment
- Document any custom fields

❌ **DON'T:**
- Hardcode file paths
- Mix test and production configs
- Modify configs without validation

### 2. Error Handling

✅ **DO:**
```python
try:
    provider = ModelProvider("configs/anthropic.json")
    model = provider.get_model_by_name("model-name")
    if model:
        # Use model
        pass
    else:
        # Handle missing model
        print("Model not found or disabled")
except FileNotFoundError:
    print("Config file not found")
except json.JSONDecodeError:
    print("Invalid JSON format")
except ValueError as e:
    print(f"Invalid config: {e}")
```

### 3. Performance Optimization

✅ **DO:**
- Cache ModelProvider instances
- Load providers once at startup
- Use `get_model_count()` before iterating
- Filter by enabled state in queries

❌ **DON'T:**
- Create new ModelProvider for each request
- Load entire provider just to check one model
- Iterate over all models when filtered query available

### 4. Cost Optimization

✅ **DO:**
```python
# Use cheapest model finder
cheapest = provider.get_cheapest_model_for_capability(
    "vision",
    input_tokens=expected_input,
    output_tokens=expected_output
)

# Calculate before using
cost = model.get_estimated_cost(input_tokens, output_tokens)
if cost > budget_threshold:
    # Use cheaper alternative
    pass
```

### 5. Hot Reload

✅ **DO:**
```python
# Periodic reload for long-running services
import schedule

def reload_configs():
    for provider in providers.values():
        try:
            provider.reload()
            print(f"Reloaded {provider.provider_name}")
        except Exception as e:
            print(f"Failed to reload {provider.provider_name}: {e}")

schedule.every(1).hour.do(reload_configs)
```

### 6. Capability Queries

✅ **DO:**

```python
# Use enum for type safety
from model_management import ModelCapability

models = provider.get_models_for_capability(ModelCapability.VISION)

# Check before use
if model.has_capability(ModelCapability.FUNCTION_CALLING):
    # Safe to use function calling
    pass
```

---

## Error Handling

### Common Errors and Solutions

#### FileNotFoundError
**Cause:** Config file doesn't exist  
**Solution:**
```python
from pathlib import Path

config_file = Path("configs/anthropic.json")
if not config_file.exists():
    print(f"Config file not found: {config_file}")
    # Handle gracefully
```

#### json.JSONDecodeError
**Cause:** Invalid JSON syntax  
**Solution:**
- Validate JSON with linter
- Check for trailing commas
- Ensure proper escaping

#### ValueError: Missing required field
**Cause:** Config missing 'provider', 'api_version', or 'models'  
**Solution:**
```python
required = ["provider", "api_version", "models"]
with open(config_file) as f:
    data = json.load(f)
    for field in required:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
```

#### Model Returns None
**Causes:**
1. Model name doesn't exist
2. Model is disabled
3. Provider is disabled
4. Model doesn't have required capability

**Solution:**
```python
model = provider.get_model_by_name("model-name")
if model is None:
    # Check if model exists
    all_models = provider.get_all_models(include_disabled=True)
    if any(m.name == "model-name" for m in all_models):
        print("Model exists but is disabled")
    else:
        print("Model doesn't exist")
```

---

## Appendix A: Complete Example Application

```python
#!/usr/bin/env python3
"""
Example application using ModelProvider
"""

from model_management import ModelProvider, load_providers
from typing import Optional


def main():
    # Load all providers
    print("Loading providers...")
    providers = load_providers("configs/")
    print(f"Loaded {len(providers)} providers\n")

    # Display provider summary
    for name, provider in providers.items():
        model_count = provider.get_model_count()
        print(f"📦 {name}: {model_count} models")

    print("\n" + "=" * 50 + "\n")

    # Find cheapest vision model across all providers
    print("Finding cheapest vision model across all providers...")

    cheapest_model = None
    cheapest_provider = None
    min_cost = float('inf')

    for provider in providers.values():
        model = provider.get_cheapest_model_for_capability(
            "vision",
            input_tokens=5000,
            output_tokens=1000
        )
        if model:
            cost = model.get_estimated_cost(5000, 1000)
            if cost < min_cost:
                min_cost = cost
                cheapest_model = model
                cheapest_provider = provider

    if cheapest_model:
        print(f"\n✅ Cheapest Vision Model Found:")
        print(f"   Provider: {cheapest_provider.provider_name}")
        print(f"   Model: {cheapest_model.name}")
        print(f"   Cost: ${min_cost:.4f}")
        print(f"   Description: {cheapest_model.description}")

    print("\n" + "=" * 50 + "\n")

    # Find all models with extended thinking
    print("Models with extended thinking capability:")

    thinking_models = []
    for provider in providers.values():
        models = provider.get_models_for_capability("extended_thinking")
        for model in models:
            thinking_models.append((provider.provider_name, model))

    if thinking_models:
        for provider_name, model in thinking_models:
            print(f"  • {provider_name}: {model.name}")
    else:
        print("  No models found with extended thinking")


if __name__ == "__main__":
    main()
```

---

## Appendix B: Testing

```python
import unittest
from model_management import ModelProvider, Model
from pathlib import Path


class TestModelProvider(unittest.TestCase):

    def setUp(self):
        self.provider = ModelProvider("configs/anthropic.json")

    def test_provider_loaded(self):
        self.assertEqual(self.provider.provider_name, "anthropic")
        self.assertGreater(self.provider.get_model_count(), 0)

    def test_get_model_by_name(self):
        model = self.provider.get_model_by_name("claude-3-7-sonnet-20250219")
        self.assertIsNotNone(model)
        self.assertEqual(model.version, "3.7")

    def test_get_models_for_capability(self):
        vision_models = self.provider.get_models_for_capability("vision")
        self.assertGreater(len(vision_models), 0)
        for model in vision_models:
            self.assertTrue(model.has_capability("vision"))

    def test_cost_calculation(self):
        model = self.provider.get_model_by_name("claude-3-7-sonnet-20250219")
        cost = model.get_estimated_cost(1000, 500)
        self.assertGreater(cost, 0)

    def test_enable_disable(self):
        model_name = "claude-3-opus-20240229"

        # Disable
        self.provider.disable_model(model_name)
        model = self.provider.get_model_by_name(model_name)
        self.assertIsNone(model)

        # Enable
        self.provider.enable_model(model_name)
        model = self.provider.get_model_by_name(model_name)
        self.assertIsNotNone(model)


if __name__ == '__main__':
    unittest.main()
```

---

## Document End

**Version:** 1.0.0  
**Status:** Production Ready  
**Last Updated:** November 6, 2025

**For support or questions, contact:**  
Ashutosh Sinha  
Email: ajsinha@gmail.com

**Copyright © 2025-2030, All Rights Reserved**  
**Patent Pending:** Certain architectural patterns may be subject to patent applications.