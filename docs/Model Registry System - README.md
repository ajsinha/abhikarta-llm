# Abhikarta LLM Model Registry System

**Version:** 2.1 - Refactored Architecture  
**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha** | ajsinha@gmail.com

---

## 📖 Documentation

This system provides comprehensive documentation in **two main documents**:

### 1. [Model Registry System - Architecture.md](Model%20Registry%20System%20-%20Architecture.md) 📐

**Read this to understand:**
- System design and architecture
- Why the system is designed this way
- Class hierarchies and relationships
- Database schema
- Design patterns used
- Extension mechanisms
- Thread safety model
- Security considerations

**Perfect for:**
- Architects and senior developers
- Understanding system internals
- Extending with new storage backends
- Making architectural decisions

### 2. [Model Registry System - Quick Reference Guide.md](Model%20Registry%20System%20-%20Quick%20Reference%20Guide.md) 🚀

**Read this to learn:**
- How to install and configure
- Quick start examples
- Complete API reference
- Common usage patterns
- Deployment procedures
- Troubleshooting guide
- Performance tuning
- Migration from old versions

**Perfect for:**
- Developers using the system
- Getting started quickly
- Finding API examples
- Deployment and operations
- Day-to-day usage

---

## 🚀 Quick Start (30 seconds)

### Database Implementation (Production)

```python
from model_registry_db import ModelRegistryDB

# Initialize once
registry = ModelRegistryDB.get_instance(db_path="./models.db")
registry.load_json_directory("./json_configs")  # First time only

# Use it
provider, model, cost = registry.get_cheapest_model_for_capability("chat")
print(f"{provider}/{model.name}: ${cost:.4f}")
```

### JSON Implementation (Development)

```python
from model_registry_json import ModelRegistryJSON

# Initialize with auto-reload
registry = ModelRegistryJSON.get_instance("./json_configs")
registry.start_auto_reload(interval_seconds=300)

# Use it
provider, model, cost = registry.get_cheapest_model_for_capability("vision")
print(f"{provider}/{model.name}: ${cost:.4f}")
```

---

## 📦 What's Included

### Python Modules (10 files)

**Abstract Base Classes:**
- `model_provider.py` - Abstract ModelProvider + Model class
- `model_registry.py` - Abstract ModelRegistry

**Database Implementation:**
- `model_management_db_handler.py` - Database operations
- `model_provider_db.py` - ModelProviderDB
- `model_registry_db.py` - ModelRegistryDB

**JSON Implementation:**
- `model_provider_json.py` - ModelProviderJSON  
- `model_registry_json.py` - ModelRegistryJSON

**Supporting:**
- `exceptions.py` - Exception hierarchy
- `model_management.py` - Enums and constants

**Examples:**
- `sample_usage.py` - Working demonstrations

### Documentation (2 files)

- **Model Registry System - Architecture.md** (75KB) - Complete architecture guide
- **Model Registry System - Quick Reference Guide.md** (130KB) - Complete usage guide

---

## 🎯 Key Features

- ✅ **Dual Implementation** - Choose Database or JSON based on needs
- ✅ **Abstract Base Classes** - Clean, extensible architecture
- ✅ **Cost Optimization** - Find cheapest models automatically
- ✅ **Capability Search** - Filter models by features
- ✅ **Thread-Safe** - Safe for concurrent use
- ✅ **Auto-Reload** - JSON implementation watches for changes
- ✅ **Zero Dependencies** - Uses Python standard library only
- ✅ **Production Ready** - Optimized, tested, documented

---

## 🎓 Architecture Overview

```
Application Code
    ↓
Abstract Base Classes (ModelRegistry, ModelProvider)
    ↓
├─ Database Implementation (SQLite)
│  - ModelRegistryDB
│  - ModelProviderDB
│
└─ JSON Implementation (File-based)
   - ModelRegistryJSON
   - ModelProviderJSON (with auto-reload)
```

**Key Design Patterns:**
- Strategy Pattern (swappable implementations)
- Singleton Pattern (registry instances)
- Template Method Pattern (abstract base classes)
- Repository Pattern (data access abstraction)

---

## 📊 When to Use Each Implementation

| Scenario | Use This |
|----------|----------|
| Production deployment | **Database** (`ModelRegistryDB`) |
| Development/testing | **JSON** (`ModelRegistryJSON`) |
| 100+ models | **Database** |
| <50 models | **JSON** |
| Complex queries | **Database** |
| Simple setup | **JSON** |
| Need auto-reload | **JSON** |
| Multiple processes | **Database** |

---

## 🔧 System Requirements

- **Python:** 3.8 or higher
- **OS:** Linux, macOS, Windows
- **Dependencies:** None (standard library only)
- **Database:** SQLite (included with Python)
- **Disk Space:** ~1MB for code, varies for database

---

## 📞 Support

**Email:** ajsinha@gmail.com

**For help with:**
- Installation and setup
- API usage questions
- Architecture decisions
- Deployment assistance
- Performance optimization
- Bug reports
- Feature requests

---

## ⚖️ Legal Notice

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**

This document and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use is strictly prohibited without explicit written permission from the copyright holder.

**Patent Pending:** Certain architectural patterns and implementations described in this system may be subject to patent applications.

---

## 🎉 Getting Started

1. **Choose your path:**
   - Want to understand the system? → Read [Architecture.md](Model%20Registry%20System%20-%20Architecture.md)
   - Want to use the system? → Read [Quick Reference Guide.md](Model%20Registry%20System%20-%20Quick%20Reference%20Guide.md)

2. **Install:**
   - Copy all `.py` files to your project
   - Set up JSON configs or database

3. **Start coding:**
   - Use the 30-second quick start above
   - Refer to API examples in the Quick Reference Guide

4. **Deploy:**
   - Follow the Deployment Guide section
   - Choose Database for production

---

**Abhikarta LLM Model Registry System v2.1**  
**Professional, Extensible, Production-Ready**