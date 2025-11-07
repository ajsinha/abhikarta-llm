# Model Registry System - Quick Reference Guide

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha** | ajsinha@gmail.com

---

## Quick Start (3 Steps)

```python
# 1. Initialize registry (once at startup)
from model_registry import ModelRegistry
registry = ModelRegistry.get_instance("/path/to/config")

# 2. Start auto-reload (optional but recommended)
registry.start_auto_reload(interval_seconds=600)  # 10 minutes

# 3. Use the registry
provider, model, cost = registry.get_cheapest_model_for_capability("chat")
print(f"{provider}/{model.name}: ${cost:.4f}")
```

---

## Most Common Operations

### Get All Providers
```python
providers = registry.get_all_providers()
for name, provider in providers.items():
    print(f"{name}: {provider.get_model_count()} models")
```

### Get Specific Model
```python
model = registry.get_model_from_provider_by_name("anthropic", "claude-opus-4")
print(f"Context: {model.context_window:,}, Cost: {model.calculate_cost(100000, 1000)}")
```

### Find Cheapest Model (All Providers)
```python
provider, model, cost = registry.get_cheapest_model_for_capability(
    "vision",
    input_tokens=1_000_000,
    output_tokens=10_000
)
```

### Find Cheapest Model (Specific Provider)
```python
model, cost = registry.get_cheapest_model_for_provider_and_capability(
    "anthropic",
    "vision",
    input_tokens=500_000,
    output_tokens=5_000
)
```

### Search All Models with Capability
```python
models = registry.get_all_models_for_capability("vision")
for provider_name, model in models:
    print(f"{provider_name}/{model.name}")
```

---

## Exception Handling Pattern

```python
from exceptions import (
    ProviderNotFoundException,
    ProviderDisabledException,
    ModelNotFoundException,
    ModelDisabledException,
    NoModelsAvailableException
)

try:
    model = registry.get_model_from_provider_by_name("provider", "model")
except ProviderNotFoundException:
    # Provider doesn't exist
    pass
except ProviderDisabledException:
    # Provider is disabled
    pass
except ModelNotFoundException:
    # Model doesn't exist
    pass
except ModelDisabledException:
    # Model is disabled
    pass
```

---

## Auto-Reload Management

```python
# Start auto-reload
registry.start_auto_reload(interval_seconds=600)  # 10 minutes

# Check status
summary = registry.get_registry_summary()
print(f"Auto-reload: {summary['auto_reload_enabled']}")

# Manual reload
count = registry.reload_all_providers()
print(f"Loaded {count} providers")

# Stop auto-reload
registry.stop_auto_reload()
```

---

## Registry Information

```python
# Get summary
summary = registry.get_registry_summary()
print(f"Providers: {summary['provider_count']}")
print(f"Models: {summary['total_model_count']}")
print(f"Directory: {summary['config_directory']}")

# Get counts
provider_count = registry.get_provider_count()
model_count = registry.get_total_model_count()
```

---

## Configuration File Template

Create JSON files in your config directory:

```json
{
  "provider": "provider_name",
  "api_version": "v1",
  "base_url": "https://api.example.com",
  "models": [
    {
      "name": "model-name",
      "version": "1.0",
      "description": "Model description",
      "context_window": 200000,
      "max_output": 16384,
      "cost": {
        "input_per_1m": 3.0,
        "output_per_1m": 15.0
      },
      "capabilities": {
        "chat": true,
        "vision": true,
        "function_calling": true,
        "streaming": true
      }
    }
  ]
}
```

---

## Key Features

✅ **Singleton** - One instance across application  
✅ **Thread-Safe** - Safe for concurrent access  
✅ **Auto-Reload** - Background monitoring of config changes  
✅ **Change Detection** - MD5 hashing, only reloads modified files  
✅ **Dynamic Updates** - Adds/removes/updates providers automatically  
✅ **Rich Exceptions** - Specific exceptions for every error case  
✅ **Cross-Provider Search** - Find cheapest models across all providers  

---

## Common Capabilities

Use these capability strings for searching:

- `"chat"` - Conversational chat
- `"vision"` - Image understanding
- `"function_calling"` - Call external functions
- `"streaming"` - Real-time token streaming
- `"code_execution"` - Execute code
- `"json_mode"` - Structured JSON output
- `"caching"` - Context caching
- `"batch_api"` - Batch processing

See `model_management.py` for complete list of 100+ capabilities.

---

## Performance Tips

1. **Initialize once** at startup
2. **Enable auto-reload** for production
3. **Cache expensive queries** with `@lru_cache`
4. **Use capability-based search** instead of hard-coding models
5. **Filter early** to reduce search space
6. **Handle exceptions** properly

---

## Thread Safety Guarantee

All public methods are thread-safe:
- ✅ Multiple threads can read simultaneously
- ✅ Writes are serialized with RLock
- ✅ No race conditions
- ✅ Consistent state guaranteed

---

## File System Behavior

**New JSON file added** → Provider automatically loaded  
**JSON file modified** → Provider automatically reloaded  
**JSON file deleted** → Provider automatically removed  
**JSON file unchanged** → Skipped (efficient)

---

## Essential Methods Summary

| Method | Purpose |
|--------|---------|
| `get_instance()` | Get singleton instance |
| `get_all_providers()` | List all providers |
| `get_provider_by_name()` | Get specific provider |
| `get_model_from_provider_by_name()` | Get specific model |
| `get_cheapest_model_for_capability()` | Find cheapest across all |
| `get_cheapest_model_for_provider_and_capability()` | Find cheapest in provider |
| `get_all_models_for_capability()` | Search by capability |
| `start_auto_reload()` | Enable background monitoring |
| `stop_auto_reload()` | Disable background monitoring |
| `reload_all_providers()` | Manual reload trigger |
| `get_registry_summary()` | Get status information |

---

## Troubleshooting Quick Fixes

**Provider not loading?**
→ Check JSON syntax, required fields, file permissions

**Model disabled?**
→ Check `enabled` field in JSON or call `provider.enable_model(name)`

**Auto-reload not working?**
→ Verify `start_auto_reload()` was called, check interval

**High memory?**
→ Stop auto-reload if not needed, reduce provider count

**Slow queries?**
→ Cache results, filter early, use provider-specific searches

---

## Best Practice Checklist

- [ ] Initialize registry once at startup
- [ ] Enable auto-reload for production
- [ ] Always handle exceptions
- [ ] Use capability-based selection
- [ ] Validate configs before deployment
- [ ] Monitor logs for errors
- [ ] Implement graceful shutdown
- [ ] Cache expensive queries
- [ ] Test configurations
- [ ] Don't hard-code model names

---

## Testing Commands

```bash
# Run comprehensive test suite
python test_model_registry.py

# Validate JSON configurations
python -m json.tool config/provider.json

# Check file permissions
ls -la config/
```

---

## Support & Documentation

📖 **Full Documentation**: See `Model Registry System - Architecture.md`  
🧪 **Test Suite**: Run `test_model_registry.py`  
📝 **Delivery Summary**: See `DELIVERY_SUMMARY.md`

---

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha** | ajsinha@gmail.com

**Legal Notice**: This document and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use is strictly prohibited without explicit written permission from the copyright holder.

**Patent Pending**: Certain architectural patterns and implementations may be subject to patent applications.