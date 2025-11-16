# Abhikarta Model Facade - Complete README and Quick Guide

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha** | Email: ajsinha@gmail.com

**Legal Notice:** This module and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use is strictly prohibited without explicit written permission from the copyright holder.

**Patent Pending:** Certain architectural patterns and implementations described in this module may be subject to patent applications.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Key Features](#key-features)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Quick Start](#quick-start)
7. [Detailed Usage](#detailed-usage)
8. [Provider-Specific Details](#provider-specific-details)
9. [API Reference](#api-reference)
10. [Examples](#examples)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)
13. [Extending the System](#extending-the-system)

---

## Overview

The Abhikarta Model Facade system provides a **unified, provider-agnostic interface** for interacting with Large Language Models (LLMs) from various providers. The system features:

- **Zero Hardcoded Configuration**: All model details, capabilities, and pricing are loaded dynamically from either JSON files or database
- **Flexible Configuration Sources**: Support for both JSON files and database backends
- **Provider Abstraction**: Write once, run with any provider
- **Automatic Capability Detection**: Models expose their capabilities dynamically
- **Cost Optimization**: Automatic selection of cheapest models for given capabilities
- **Production Ready**: Comprehensive error handling, retry logic, and monitoring

### Supported Providers

- **Anthropic** (Claude 3.x family) ✅ Fully Implemented
- **OpenAI** (GPT-4, GPT-3.5, DALL-E, Embeddings) ✅ Fully Implemented
- **Google** (Gemini, PaLM) 🔄 Template Available
- **Meta** (Llama 2/3 via Replicate) 🔄 Template Available
- **Cohere** (Command, Command-R) 🔄 Template Available
- **Mistral** (Mixtral, Mistral) 🔄 Template Available
- **Groq** 🔄 Template Available
- **HuggingFace** 🔄 Template Available
- **Together AI** 🔄 Template Available
- **Replicate** 🔄 Template Available
- **AWS Bedrock** 🔄 Template Available
- **Ollama** (Local models) 🔄 Template Available
- **Mock** (Testing) 🔄 Template Available

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      User Application                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FacadeFactory                            │
│  - Configuration Source Selection (JSON/DB)                 │
│  - Provider Detection                                       │
│  - Facade Creation                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Anthropic    │  │   OpenAI     │  │   Google     │
│  Facade      │  │   Facade     │  │   Facade     │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              BaseProviderFacade                             │
│  - Dynamic Configuration Loading                            │
│  - Capability Detection                                     │
│  - Cost Calculation                                         │
│  - Common Operations                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌─────────────────┐              ┌─────────────────┐
│ ModelProvider   │              │ ModelProvider   │
│     (JSON)      │              │      (DB)       │
│                 │              │                 │
│ - JSON Files    │              │ - SQLite        │
│ - File Loader   │              │ - DB Handler    │
└─────────────────┘              └─────────────────┘
```

### Key Classes

#### 1. **LLMFacade** (Abstract Base)
- Defines the unified interface for all LLM operations
- 50+ abstract methods covering all LLM capabilities
- Standard types and exceptions

#### 2. **BaseProviderFacade** (Base Implementation)
- Implements common functionality
- Loads configuration from ModelProvider instances
- Provides capability detection and cost calculation
- Zero hardcoded configuration

#### 3. **Provider-Specific Facades** (e.g., AnthropicFacade, OpenAIFacade)
- Implement provider-specific SDK integration
- Handle provider-specific request/response formats
- Provide provider-specific optimizations

#### 4. **FacadeFactory**
- Creates facade instances
- Manages configuration sources (JSON/DB)
- Provides convenience methods for facade creation

#### 5. **ModelProvider** (Abstract)
- Defines interface for provider configuration
- Manages models for a provider
- Supports enable/disable functionality

#### 6. **ModelProviderJSON / ModelProviderDB**
- Concrete implementations of ModelProvider
- Load from JSON files or database
- Provide consistent interface regardless of source

---

## Key Features

### 1. Dynamic Configuration Loading

**No hardcoded configuration!** All model details are loaded at runtime:

```python
# All of this comes from JSON/DB:
- Model capabilities (chat, vision, tools, etc.)
- Context windows and max output tokens
- Pricing (input/output costs per million tokens)
- Model versions and descriptions
- API endpoints and authentication requirements
- Provider-specific features
```

### 2. Dual Configuration Sources

**JSON Files:**
```python
factory = FacadeFactory(
    config_source="json",
    config_path="./config"
)
```

**Database:**
```python
from model_management.model_management_db_handler import ModelManagementDBHandler

db_handler = ModelManagementDBHandler.get_instance("./db_management.sqlite")
factory = FacadeFactory(
    config_source="db",
    db_handler=db_handler
)
```

### 3. Automatic Capability Detection

Models automatically expose their capabilities based on configuration:

```python
capabilities = facade.get_capabilities()
# Returns: [ModelCapability.CHAT_COMPLETION, ModelCapability.VISION, 
#           ModelCapability.TOOL_USE, ModelCapability.STREAMING, ...]

if facade.supports_capability(ModelCapability.VISION):
    response = facade.chat_completion_with_vision(messages, images)
```

### 4. Cost Optimization

Find the cheapest model for your needs:

```python
# Get cheapest model across ALL providers for a capability
facade, cost = factory.create_cheapest_facade(
    capability="chat",
    input_tokens=100000,
    output_tokens=1000
)
print(f"Using {facade.model_name} at ${cost:.4f}")
```

### 5. Unified Interface

Same code works with any provider:

```python
# Works with Anthropic, OpenAI, Google, etc.
response = facade.chat_completion(
    messages=[{"role": "user", "content": "Hello!"}],
    temperature=0.7,
    max_tokens=1000
)
print(response["content"])
```

---

## Installation

### Requirements

```bash
# Core dependencies
pip install anthropic openai  # Provider SDKs as needed

# Optional dependencies
pip install tiktoken  # For OpenAI token counting
pip install pillow   # For image processing

# Your Abhikarta model management system
# (Already includes ModelProvider, Model classes, etc.)
```

### File Structure

```
your_project/
├── config/                    # JSON configuration (if using JSON)
│   ├── anthropic.json
│   ├── openai.json
│   ├── google.json
│   └── ...
├── facades/                   # Facade implementations
│   ├── llm_facade.py         # Abstract base class
│   ├── base_provider_facade.py
│   ├── facade_factory.py
│   ├── anthropic_facade.py
│   ├── openai_facade.py
│   └── register_facades.py
└── model_management/          # Your model management system
    ├── model_provider.py
    ├── model_provider_json.py
    ├── model_provider_db.py
    └── ...
```

---

## Configuration

### JSON Configuration Format

Each provider has a JSON file with this structure:

```json
{
  "provider": "anthropic",
  "api_version": "2023-06-01",
  "base_url": "https://api.anthropic.com",
  "notes": {
    "authentication": "Requires ANTHROPIC_API_KEY",
    "pricing": "Prices per 1M tokens",
    "features": "Supports vision, tools, streaming"
  },
  "models": [
    {
      "name": "claude-3-5-sonnet-20241022",
      "version": "3.5",
      "description": "Latest Claude with improved capabilities",
      "strengths": ["coding", "reasoning", "vision"],
      "context_window": 200000,
      "max_output": 8192,
      "cost": {
        "input_per_1m": 3.0,
        "output_per_1m": 15.0
      },
      "capabilities": {
        "chat": true,
        "completion": false,
        "streaming": true,
        "function_calling": true,
        "tool_use": true,
        "vision": true
      }
    }
  ]
}
```

### Database Schema

The database approach uses the existing Abhikarta model management schema:

- **providers** table: Provider configurations
- **models** table: Model details and capabilities
- **Relationships**: Foreign keys linking models to providers

See your existing `ModelManagementDBHandler` documentation for schema details.

---

## Quick Start

### 1. Basic Setup (JSON)

```python
# Import and register facades
import register_facades  # Automatically registers all facades

from facade_factory import FacadeFactory

# Create factory with JSON configuration
factory = FacadeFactory(
    config_source="json",
    config_path="./config"
)

# Create a facade
facade = factory.create_facade(
    provider_name="anthropic",
    model_name="claude-3-5-sonnet-20241022"
    # API key read from ANTHROPIC_API_KEY env var
)

# Use it!
response = facade.chat_completion(
    messages=[{"role": "user", "content": "Explain quantum computing"}]
)
print(response["content"])
```

### 2. Basic Setup (Database)

```python
import register_facades
from facade_factory import FacadeFactory
from model_management.model_management_db_handler import ModelManagementDBHandler

# Initialize database handler
db_handler = ModelManagementDBHandler.get_instance("./db_management.sqlite")

# Create factory with database configuration
factory = FacadeFactory(
    config_source="db",
    db_handler=db_handler
)

# Rest is identical to JSON approach
facade = factory.create_facade(
    provider_name="anthropic",
    model_name="claude-3-5-sonnet-20241022"
)

response = facade.chat_completion(
    messages=[{"role": "user", "content": "Hello!""}]
)
```

### 3. List Available Providers and Models

```python
# List all providers
providers = factory.list_providers()
for name, info in providers.items():
    print(f"{name}: {info['model_count']} models")

# List models for a provider
models = factory.list_models("anthropic")
print(f"Anthropic models: {models['anthropic']}")

# List all models across all providers
all_models = factory.list_models()
for provider, model_list in all_models.items():
    print(f"\n{provider}:")
    for model in model_list:
        print(f"  - {model}")
```

---

## Detailed Usage

### Chat Completion

```python
# Basic chat
response = facade.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is machine learning?"}
    ],
    temperature=0.7,
    max_tokens=1000
)
print(response["content"])
print(f"Tokens used: {response['usage'].total_tokens}")
```

### Streaming Responses

```python
# Stream response chunks
for chunk in facade.stream_chat_completion(
    messages=[{"role": "user", "content": "Write a story"}],
    temperature=0.8
):
    print(chunk, end="", flush=True)
```

### Async Operations

```python
import asyncio

async def main():
    response = await facade.achat_completion(
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response["content"])

asyncio.run(main())
```

### Vision Capabilities

```python
from PIL import Image

# Load image
image = Image.open("diagram.png")

# Chat with vision
response = facade.chat_completion_with_vision(
    messages=[{"role": "user", "content": "What's in this image?"}],
    images=[image],
    max_tokens=1000
)
print(response["content"])
```

### Function Calling / Tool Use

```python
# Define tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

# Request with tools
response = facade.chat_completion(
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools
)

# Check for tool calls
if response["tool_calls"]:
    for tool_call in response["tool_calls"]:
        print(f"Tool: {tool_call['function']['name']}")
        print(f"Args: {tool_call['function']['arguments']}")
```

### Cost Estimation

```python
# Estimate cost before making request
estimated_cost = facade.estimate_cost(
    prompt_tokens=1000,
    completion_tokens=500
)
print(f"Estimated cost: ${estimated_cost:.6f}")

# Get cost per token
input_cost, output_cost = facade.get_cost_per_token()
print(f"Input: ${input_cost:.8f}/token")
print(f"Output: ${output_cost:.8f}/token")
```

### Model Information

```python
# Get comprehensive model info
info = facade.get_model_info()
print(f"Provider: {info['provider']}")
print(f"Model: {info['name']}")
print(f"Context Window: {info['context_window']:,} tokens")
print(f"Max Output: {info['max_output']:,} tokens")
print(f"Capabilities: {info['capabilities']}")
print(f"Input Cost: ${info['pricing']['input_per_1m_tokens']}/1M tokens")
```

### Finding Optimal Models

```python
# Find cheapest model for a capability
facade, cost = factory.create_cheapest_facade(
    capability="chat",
    input_tokens=10000,
    output_tokens=500
)
print(f"Cheapest option: {facade.provider_name}/{facade.model_name}")
print(f"Cost: ${cost:.6f}")

# Get model info without creating facade
info = factory.get_model_info("anthropic", "claude-3-haiku-20240307")
print(f"Context: {info['context_window']}")
print(f"Cost: ${info['pricing']['input_per_1m']}/1M input tokens")
```

---

## Provider-Specific Details

### Anthropic (Claude)

**Key Features:**
- Extended context windows (200K tokens)
- Vision capabilities across all Claude 3.x models
- Tool use / function calling
- Prompt caching (reduces costs for repeated context)
- Extended thinking mode (Claude 3.7 Sonnet)

**Configuration:**
```python
facade = factory.create_facade(
    provider_name="anthropic",
    model_name="claude-3-5-sonnet-20241022"
    # API key from ANTHROPIC_API_KEY env var
)
```

**Unique Features:**
```python
# System prompts
response = facade.chat_completion(
    messages=[{"role": "user", "content": "Hello"}],
    system="You are a Python expert"  # Anthropic-specific parameter
)

# Prompt caching (if supported by model)
# Automatically used when you send repeated context
```

**Models Available:**
- claude-3-7-sonnet-20250219 (Extended Thinking)
- claude-3-5-sonnet-20241022 (Latest, Best)
- claude-3-5-haiku-20241022 (Fast, Cheap)
- claude-3-opus-20240229 (Most Capable)
- claude-3-sonnet-20240229 (Balanced)
- claude-3-haiku-20240307 (Fast)

### OpenAI (GPT)

**Key Features:**
- GPT-4 family with vision
- Function calling / tool use
- JSON mode for structured output
- Embeddings generation
- DALL-E image generation
- Content moderation

**Configuration:**
```python
facade = factory.create_facade(
    provider_name="openai",
    model_name="gpt-4-turbo-preview"
    # API key from OPENAI_API_KEY env var
)
```

**Unique Features:**
```python
# JSON mode
response = facade.chat_completion(
    messages=[{"role": "user", "content": "List 3 colors"}],
    response_format={"type": "json_object"}
)

# Embeddings
embedding = facade.generate_embeddings("Hello world")
print(f"Embedding dimensions: {len(embedding)}")

# Image generation (DALL-E models)
image_url = facade.generate_image(
    prompt="A sunset over mountains",
    size="1024x1024",
    quality="hd"
)

# Content moderation
moderation = facade.moderate_content("Some text to check")
print(f"Flagged: {moderation['flagged']}")
```

**Models Available:**
- gpt-4-turbo-preview (Latest GPT-4)
- gpt-4-vision-preview (With vision)
- gpt-4 (Standard)
- gpt-3.5-turbo (Fast, cheap)
- text-embedding-3-large (Embeddings)
- dall-e-3 (Image generation)

---

## API Reference

### FacadeFactory

#### Methods

**`__init__(config_source, config_path=None, db_handler=None)`**
- Initialize factory with configuration source

**`create_facade(provider_name, model_name, api_key=None, **kwargs)`**
- Create a facade instance for specified provider/model

**`create_cheapest_facade(capability, input_tokens, output_tokens, **kwargs)`**
- Create facade for cheapest model supporting a capability

**`list_providers()`**
- List all available providers with details

**`list_models(provider_name=None)`**
- List models for provider(s)

**`get_provider(provider_name)`**
- Get ModelProvider instance

**`get_model_info(provider_name, model_name)`**
- Get detailed model information

**`reload_providers()`**
- Reload configuration from source

**`register_facade(provider_name, facade_class)` (class method)**
- Register a provider-specific facade class

### LLMFacade (Base Interface)

#### Core Methods

**`chat_completion(messages, temperature, max_tokens, tools, **kwargs)`**
- Generate chat completion

**`achat_completion(...)`** (async)
- Async chat completion

**`stream_chat_completion(...)`**
- Stream chat responses

**`astream_chat_completion(...)`** (async)
- Async streaming

**`chat_completion_with_vision(messages, images, **kwargs)`**
- Chat with image inputs

**`text_completion(prompt, **kwargs)`**
- Simple text completion

#### Capability Methods

**`get_capabilities()`**
- Get list of supported capabilities

**`supports_capability(capability)`**
- Check if capability supported

**`get_model_info()`**
- Get comprehensive model information

**`get_context_window_size()`**
- Get max context tokens

**`get_max_output_tokens()`**
- Get max output tokens

#### Cost Methods

**`estimate_cost(prompt_tokens, completion_tokens, cached_tokens)`**
- Estimate cost for request

**`get_cost_per_token()`**
- Get input/output cost per token

#### Utility Methods

**`count_tokens(text)`**
- Count tokens in text

**`format_messages(messages)`**
- Convert messages to prompt string

**`parse_tool_calls(response)`**
- Extract tool calls from response

**`validate_config(config)`**
- Validate configuration

**`health_check()`**
- Check if service is healthy

**`close()`**
- Cleanup resources

### Model & ModelProvider

See your existing Abhikarta model management documentation for:
- `ModelProvider` interface
- `Model` class
- `ModelProviderJSON` implementation
- `ModelProviderDB` implementation

---

## Examples

### Example 1: Simple Chat Application

```python
import register_facades
from facade_factory import FacadeFactory

def main():
    # Setup
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    # Chat loop
    messages = []
    print("Chat with Claude (type 'quit' to exit)")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
        
        messages.append({"role": "user", "content": user_input})
        
        response = facade.chat_completion(messages)
        assistant_message = response["content"]
        
        messages.append({"role": "assistant", "content": assistant_message})
        
        print(f"\nAssistant: {assistant_message}")
        print(f"Tokens: {response['usage'].total_tokens}")

if __name__ == "__main__":
    main()
```

### Example 2: Cost-Optimized Multi-Provider System

```python
import register_facades
from facade_factory import FacadeFactory

def get_response(factory, capability, messages, max_budget=0.01):
    """Get response using cheapest model within budget."""
    
    # Find cheapest model
    facade, cost = factory.create_cheapest_facade(
        capability=capability,
        input_tokens=len(str(messages)) * 0.25,  # Rough estimate
        output_tokens=1000
    )
    
    if cost > max_budget:
        print(f"Warning: Estimated cost ${cost:.6f} exceeds budget ${max_budget}")
    
    print(f"Using: {facade.provider_name}/{facade.model_name} (${cost:.6f})")
    
    response = facade.chat_completion(messages, max_tokens=1000)
    
    # Calculate actual cost
    actual_cost = facade.estimate_cost(
        response['usage'].prompt_tokens,
        response['usage'].completion_tokens
    )
    print(f"Actual cost: ${actual_cost:.6f}")
    
    return response

def main():
    factory = FacadeFactory(config_source="json", config_path="./config")
    
    messages = [{"role": "user", "content": "Explain photosynthesis"}]
    
    response = get_response(factory, "chat", messages, max_budget=0.01)
    print(f"\n{response['content']}")

if __name__ == "__main__":
    main()
```

### Example 3: Image Analysis

```python
import register_facades
from facade_factory import FacadeFactory
from PIL import Image

def analyze_image(image_path, question):
    factory = FacadeFactory(config_source="json", config_path="./config")
    
    # Get vision-capable model
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    # Check capability
    if not facade.supports_capability(ModelCapability.VISION):
        raise ValueError(f"{facade.model_name} doesn't support vision")
    
    # Load image
    image = Image.open(image_path)
    
    # Analyze
    response = facade.chat_completion_with_vision(
        messages=[{"role": "user", "content": question}],
        images=[image]
    )
    
    return response["content"]

# Usage
result = analyze_image(
    "chart.png",
    "What are the key insights from this chart?"
)
print(result)
```

### Example 4: Tool Use / Function Calling

```python
import register_facades
from facade_factory import FacadeFactory
import json

def execute_tool(tool_name, arguments):
    """Simulate tool execution."""
    if tool_name == "calculator":
        return eval(arguments["expression"])
    elif tool_name == "weather":
        return f"Weather in {arguments['location']}: Sunny, 72°F"
    return "Unknown tool"

def chat_with_tools():
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Evaluate math expressions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string"}
                    },
                    "required": ["expression"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "weather",
                "description": "Get weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    
    messages = [
        {"role": "user", "content": "What's 25 * 17? Also, what's the weather in Tokyo?"}
    ]
    
    response = facade.chat_completion(messages, tools=tools)
    
    # Process tool calls
    if response["tool_calls"]:
        for tool_call in response["tool_calls"]:
            func_name = tool_call["function"]["name"]
            func_args = json.loads(tool_call["function"]["arguments"])
            
            result = execute_tool(func_name, func_args)
            print(f"Tool {func_name}: {result}")
            
            # Add tool result to messages
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": str(result)
            })
        
        # Get final response
        final_response = facade.chat_completion(messages)
        print(f"\nFinal: {final_response['content']}")
    else:
        print(response["content"])

if __name__ == "__main__":
    chat_with_tools()
```

### Example 5: Database-Backed Configuration

```python
import register_facades
from facade_factory import FacadeFactory
from model_management.model_management_db_handler import ModelManagementDBHandler

def main():
    # Initialize database
    db_handler = ModelManagementDBHandler.get_instance("./db_management.sqlite")
    
    # Create factory with DB backend
    factory = FacadeFactory(config_source="db", db_handler=db_handler)
    
    # Rest is identical to JSON approach
    facade = factory.create_facade("openai", "gpt-4-turbo-preview")
    
    response = facade.chat_completion(
        messages=[{"role": "user", "content": "Hello!"}]
    )
    
    print(response["content"])
    
    # Update model in database (changes reflected immediately)
    db_handler.update_model(
        "openai",
        "gpt-4-turbo-preview",
        {"enabled": False}
    )
    
    # Reload to see changes
    factory.reload_providers()

if __name__ == "__main__":
    main()
```

---

## Best Practices

### 1. Configuration Management

**Use Environment Variables for API Keys:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
```

**Choose Configuration Source Based on Needs:**
- **JSON**: Simple deployments, version control friendly
- **Database**: Dynamic updates, multi-tenant systems, central management

### 2. Error Handling

```python
from llm_facade import (
    AuthenticationException,
    RateLimitException,
    ContextLengthExceededException,
    CapabilityNotSupportedException
)

try:
    response = facade.chat_completion(messages)
except AuthenticationException as e:
    print("Invalid API key")
except RateLimitException as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ContextLengthExceededException as e:
    print(f"Input too long: {e.provided} > {e.maximum}")
except CapabilityNotSupportedException as e:
    print(f"Model doesn't support: {e.capability}")
```

### 3. Cost Optimization

```python
# Always estimate before expensive operations
cost = facade.estimate_cost(
    prompt_tokens=len(messages) * 100,  # Rough estimate
    completion_tokens=1000
)

if cost > BUDGET_LIMIT:
    # Use cheaper model or reduce tokens
    facade_cheap, _ = factory.create_cheapest_facade("chat")
    facade = facade_cheap
```

### 4. Context Window Management

```python
# Check limits before sending
context_limit = facade.get_context_window_size()
token_count = facade.count_tokens(prompt_text)

if token_count > context_limit * 0.8:  # Use 80% threshold
    print("Warning: Approaching context limit")
    # Implement truncation or summarization
```

### 5. Capability Checking

```python
# Always check before using advanced features
if facade.supports_capability(ModelCapability.VISION):
    response = facade.chat_completion_with_vision(messages, images)
else:
    print(f"{facade.model_name} doesn't support vision")
    # Fallback to text-only
```

### 6. Resource Cleanup

```python
# Use context manager for automatic cleanup
with factory.create_facade("anthropic", "claude-3-5-sonnet-20241022") as facade:
    response = facade.chat_completion(messages)
# Automatically closed

# Or manual cleanup
facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
try:
    response = facade.chat_completion(messages)
finally:
    facade.close()
```

### 7. Monitoring and Logging

```python
import time

start = time.time()
response = facade.chat_completion(messages)
latency = (time.time() - start) * 1000

facade.log_request(
    method="chat_completion",
    input_data=messages,
    response=response,
    latency_ms=latency,
    metadata={"user_id": "user123", "session_id": "sess456"}
)
```

---

## Troubleshooting

### Issue: "Provider 'X' not found"

**Cause:** Provider not loaded from configuration source

**Solution:**
```python
# Check available providers
providers = factory.list_providers()
print(providers)

# Ensure JSON file exists or DB has provider entry
# Reload if needed
factory.reload_providers()
```

### Issue: "Model 'X' not found in provider 'Y'"

**Cause:** Model not in provider's configuration

**Solution:**
```python
# List available models
models = factory.list_models("anthropic")
print(models)

# Check model name spelling
# For DB: add model using ModelManagementDBHandler
# For JSON: add to provider JSON file
```

### Issue: "No facade implementation found for provider 'X'"

**Cause:** Provider-specific facade not registered

**Solution:**
```python
# Make sure to import register_facades
import register_facades

# Or register manually
from facade_factory import FacadeFactory
from your_facade import YourProviderFacade

FacadeFactory.register_facade("your_provider", YourProviderFacade)
```

### Issue: API Authentication Failures

**Cause:** Missing or invalid API keys

**Solution:**
```python
# Set environment variables
export ANTHROPIC_API_KEY="sk-ant-..."

# Or pass explicitly
facade = factory.create_facade(
    "anthropic",
    "claude-3-5-sonnet-20241022",
    api_key="your-key-here"
)
```

### Issue: Context Length Exceeded

**Cause:** Input + output tokens exceed model's context window

**Solution:**
```python
# Check limits
context_size = facade.get_context_window_size()
max_output = facade.get_max_output_tokens()

# Reduce input or use model with larger context
facade = factory.create_facade("anthropic", "claude-3-opus-20240229")  # 200K context
```

---

## Extending the System

### Adding a New Provider Facade

1. **Create JSON Configuration**

Create `config/newprovider.json`:
```json
{
  "provider": "newprovider",
  "api_version": "v1",
  "base_url": "https://api.newprovider.com",
  "models": [
    {
      "name": "model-v1",
      "version": "1.0",
      "description": "New provider model",
      "context_window": 8192,
      "max_output": 4096,
      "cost": {
        "input_per_1m": 1.0,
        "output_per_1m": 2.0
      },
      "capabilities": {
        "chat": true,
        "streaming": true
      }
    }
  ]
}
```

2. **Implement Facade Class**

Create `newprovider_facade.py`:
```python
from base_provider_facade import BaseProviderFacade
from llm_facade import *

class NewProviderFacade(BaseProviderFacade):
    def _initialize_client(self):
        # Initialize provider SDK
        import newprovider_sdk
        api_key = self.api_key or os.getenv("NEWPROVIDER_API_KEY")
        self.client = newprovider_sdk.Client(api_key=api_key)
    
    def chat_completion(self, messages, **kwargs):
        # Implement chat completion
        request = {
            "model": self.model_name,
            "messages": messages,
            **kwargs
        }
        response = self.client.chat.create(**request)
        return self._convert_response(response)
    
    def _convert_response(self, response):
        # Convert to standard format
        return {
            "content": response.text,
            "usage": TokenUsage(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.total_tokens
            ),
            "metadata": CompletionMetadata(
                model=response.model,
                finish_reason=response.stop_reason
            )
        }
    
    # Implement other required methods...
```

3. **Register Facade**

Add to `register_facades.py`:
```python
from newprovider_facade import NewProviderFacade

FacadeFactory.register_facade("newprovider", NewProviderFacade)
```

4. **Use It**

```python
import register_facades
from facade_factory import FacadeFactory

factory = FacadeFactory(config_source="json", config_path="./config")
facade = factory.create_facade("newprovider", "model-v1")
response = facade.chat_completion([{"role": "user", "content": "Hello!"}])
```

### Adding Custom Capabilities

Extend `ModelCapability` enum in `llm_facade.py`:
```python
class ModelCapability(Enum):
    # ... existing capabilities ...
    CUSTOM_FEATURE = "custom_feature"
```

Update JSON configuration:
```json
{
  "capabilities": {
    "chat": true,
    "custom_feature": true
  }
}
```

Implement in facade:
```python
def custom_feature_method(self, **kwargs):
    if not self.supports_capability(ModelCapability.CUSTOM_FEATURE):
        raise CapabilityNotSupportedException("custom_feature", self.model_name)
    # Implementation...
```

---

## Conclusion

The Abhikarta Model Facade system provides a **production-ready, flexible, and maintainable** solution for working with multiple LLM providers. Key benefits:

✅ **Zero Hardcoded Configuration** - All data loaded dynamically  
✅ **Dual Configuration Sources** - JSON or Database  
✅ **Provider Agnostic** - Same code works everywhere  
✅ **Cost Optimized** - Automatic cheapest model selection  
✅ **Production Ready** - Comprehensive error handling  
✅ **Extensible** - Easy to add new providers  
✅ **Type Safe** - Full type hints throughout  
✅ **Well Documented** - Comprehensive docs and examples  

For questions, issues, or contributions, contact: ajsinha@gmail.com

---

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**
