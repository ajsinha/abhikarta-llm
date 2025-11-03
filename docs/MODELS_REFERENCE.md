# Complete Models & Providers Reference

**LLM Abstraction System**  
**© 2025-2030 All Rights Reserved | Ashutosh Sinha | ajsinha@gmail.com**

## Overview

This system supports **8 providers** with **25+ models** including multiple Llama variants.

---

## 1. AWS Bedrock

**Provider Code:** `bedrock`  
**Configuration Prefix:** `provider.bedrock`

### Models

| Model ID | Full Model ID | Description | Context Length | Streaming | Use Case |
|----------|---------------|-------------|----------------|-----------|----------|
| `claude-3-opus` | `anthropic.claude-3-opus-20240229-v1:0` | Most capable Claude model | 200,000 | ✅ | Complex reasoning, analysis |
| `claude-3-sonnet` | `anthropic.claude-3-sonnet-20240229-v1:0` | Balanced performance | 200,000 | ✅ | General purpose |
| `claude-3-haiku` | `anthropic.claude-3-haiku-20240307-v1:0` | Fast and efficient | 200,000 | ✅ | High-volume, low-latency |
| `llama2-70b` | `meta.llama2-70b-chat-v1` | **Meta Llama 2 70B** | 4,096 | ✅ | Open-source, powerful |
| `llama3-8b` | `meta.llama3-8b-instruct-v1:0` | **Meta Llama 3 8B** | 8,192 | ✅ | Latest Llama, efficient |
| `mistral-7b` | `mistral.mistral-7b-instruct-v0:2` | Mistral 7B Instruct | 8,192 | ✅ | Cost-effective |

### Configuration

```properties
provider.bedrock.enabled=true
provider.bedrock.region=us-east-1
provider.bedrock.access_key=YOUR_AWS_ACCESS_KEY
provider.bedrock.secret_key=YOUR_AWS_SECRET_KEY
provider.bedrock.models=claude-3-sonnet,claude-3-haiku,llama2-70b,llama3-8b,mistral-7b
```

### Usage Example

```python
# Claude on Bedrock
response = facade.generate(
    "Analyze this code",
    provider="bedrock",
    model_name="claude-3-sonnet"
)

# Llama 2 on Bedrock
response = facade.generate(
    "Write a function",
    provider="bedrock",
    model_name="llama2-70b"
)

# Llama 3 on Bedrock
response = facade.generate(
    "Explain this concept",
    provider="bedrock",
    model_name="llama3-8b"
)
```

---

## 2. Together AI

**Provider Code:** `together`  
**Configuration Prefix:** `provider.together`

### Models

| Model ID | Full Model ID | Description | Context Length | Streaming | Cost/1M tokens |
|----------|---------------|-------------|----------------|-----------|----------------|
| `llama-2-70b-chat` | `meta-llama/Llama-2-70b-chat-hf` | **Llama 2 70B Chat** | 4,096 | ✅ | $0.90 |
| `llama-3-8b-instruct` | `meta-llama/Llama-3-8b-chat-hf` | **Llama 3 8B Instruct** | 8,192 | ✅ | $0.20 |
| `llama-3-70b-instruct` | `meta-llama/Llama-3-70b-chat-hf` | **Llama 3 70B Instruct** | 8,192 | ✅ | $0.90 |
| `mistral-7b-instruct` | `mistralai/Mistral-7B-Instruct-v0.2` | Mistral 7B Instruct | 8,192 | ✅ | $0.20 |

### Configuration

```properties
provider.together.enabled=true
provider.together.api_key=YOUR_TOGETHER_API_KEY
provider.together.base_url=https://api.together.xyz/v1
provider.together.models=llama-2-70b-chat,llama-3-8b-instruct,mistral-7b-instruct
```

### Usage Example

```python
# Llama 2 on Together
response = facade.generate(
    "Write a story",
    provider="together",
    model_name="llama-2-70b-chat"
)

# Llama 3 on Together
response = facade.generate(
    "Code a solution",
    provider="together",
    model_name="llama-3-8b-instruct"
)
```

---

## 3. Hugging Face

**Provider Code:** `huggingface`  
**Configuration Prefix:** `provider.huggingface`

### Models

| Model ID | Description | Context Length | Streaming | Type |
|----------|-------------|----------------|-----------|------|
| `meta-llama/Llama-2-70b-chat-hf` | **Llama 2 70B** from HF Hub | 4,096 | ✅ | Causal LM |
| `meta-llama/Llama-3-8b-instruct` | **Llama 3 8B** from HF Hub | 8,192 | ✅ | Causal LM |
| `tiiuae/falcon-40b-instruct` | Falcon 40B Instruct | 2,048 | ✅ | Causal LM |
| `mistralai/Mistral-7B-Instruct-v0.2` | Mistral 7B | 8,192 | ✅ | Causal LM |
| `google/flan-t5-xxl` | FLAN T5 XXL | 512 | ❌ | Seq2Seq |

### Configuration

```properties
provider.huggingface.enabled=true
provider.huggingface.api_key=YOUR_HF_API_KEY
provider.huggingface.base_url=https://api-inference.huggingface.co/models
provider.huggingface.models=meta-llama/Llama-2-70b-chat-hf,tiiuae/falcon-40b-instruct
```

### Usage Example

```python
# Llama 2 on Hugging Face
response = facade.generate(
    "Summarize this text",
    provider="huggingface",
    model_name="meta-llama/Llama-2-70b-chat-hf"
)

# Llama 3 on Hugging Face
response = facade.generate(
    "Translate to French",
    provider="huggingface",
    model_name="meta-llama/Llama-3-8b-instruct"
)
```

---

## 4. OpenAI

**Provider Code:** `openai`  
**Configuration Prefix:** `provider.openai`

### Models

| Model ID | Description | Context Length | Streaming | Cost/1K tokens |
|----------|-------------|----------------|-----------|----------------|
| `gpt-4` | Most capable GPT-4 | 8,192 | ✅ | $0.03 |
| `gpt-4-turbo` | Faster, larger context GPT-4 | 128,000 | ✅ | $0.01 |
| `gpt-3.5-turbo` | Fast and affordable | 16,385 | ✅ | $0.0015 |
| `gpt-4o` | Optimized GPT-4 | 128,000 | ✅ | $0.005 |

### Configuration

```properties
provider.openai.enabled=true
provider.openai.api_key=YOUR_OPENAI_API_KEY
provider.openai.organization=YOUR_ORG_ID
provider.openai.models=gpt-4,gpt-3.5-turbo,gpt-4-turbo
```

### Usage Example

```python
# GPT-4
response = facade.generate(
    "Write detailed analysis",
    provider="openai",
    model_name="gpt-4"
)

# GPT-3.5 Turbo (fast and cheap)
response = facade.generate(
    "Quick answer",
    provider="openai",
    model_name="gpt-3.5-turbo"
)
```

---

## 5. Anthropic

**Provider Code:** `anthropic`  
**Configuration Prefix:** `provider.anthropic`

### Models

| Model ID | Description | Context Length | Streaming | Cost/1M tokens |
|----------|-------------|----------------|-----------|----------------|
| `claude-3-opus` | Most capable Claude | 200,000 | ✅ | $15.00 |
| `claude-3-sonnet` | Balanced Claude | 200,000 | ✅ | $3.00 |
| `claude-3-haiku` | Fast Claude | 200,000 | ✅ | $0.25 |
| `claude-2.1` | Previous generation | 200,000 | ✅ | $8.00 |

### Configuration

```properties
provider.anthropic.enabled=true
provider.anthropic.api_key=YOUR_ANTHROPIC_API_KEY
provider.anthropic.models=claude-3-opus,claude-3-sonnet,claude-3-haiku
```

### Usage Example

```python
# Claude 3 Opus (most capable)
response = facade.generate(
    "Complex reasoning task",
    provider="anthropic",
    model_name="claude-3-opus"
)

# Claude 3 Haiku (fast)
response = facade.generate(
    "Quick task",
    provider="anthropic",
    model_name="claude-3-haiku"
)
```

---

## 6. Cohere

**Provider Code:** `cohere`  
**Configuration Prefix:** `provider.cohere`

### Models

| Model ID | Description | Context Length | Streaming | Cost/1M tokens |
|----------|-------------|----------------|-----------|----------------|
| `command` | Main Cohere model | 4,096 | ✅ | $1.00 |
| `command-light` | Faster variant | 4,096 | ✅ | $0.50 |
| `command-r` | Long context | 128,000 | ✅ | $0.50 |
| `command-r-plus` | Enhanced version | 128,000 | ✅ | $3.00 |

### Configuration

```properties
provider.cohere.enabled=true
provider.cohere.api_key=YOUR_COHERE_API_KEY
provider.cohere.models=command,command-light,command-r
```

### Usage Example

```python
# Cohere Command
response = facade.generate(
    "Generate text",
    provider="cohere",
    model_name="command"
)

# Long context
response = facade.generate(
    "Long document analysis",
    provider="cohere",
    model_name="command-r"
)
```

---

## 7. Google

**Provider Code:** `google`  
**Configuration Prefix:** `provider.google`

### Models

| Model ID | Description | Context Length | Streaming | Cost/1M tokens |
|----------|-------------|----------------|-----------|----------------|
| `gemini-pro` | Google's flagship | 32,768 | ✅ | $0.50 |
| `gemini-ultra` | Most capable Gemini | 32,768 | ✅ | $2.00 |
| `gemini-1.5-pro` | Long context (1M tokens!) | 1,000,000 | ✅ | $1.25 |
| `palm-2` | Previous generation | 8,192 | ❌ | $1.00 |

### Configuration

```properties
provider.google.enabled=true
provider.google.api_key=YOUR_GOOGLE_API_KEY
provider.google.project_id=YOUR_PROJECT_ID
provider.google.models=gemini-pro,gemini-ultra,palm-2
```

### Usage Example

```python
# Gemini Pro
response = facade.generate(
    "Analyze image and text",
    provider="google",
    model_name="gemini-pro"
)

# Gemini 1.5 Pro (huge context)
response = facade.generate(
    "Analyze entire book",
    provider="google",
    model_name="gemini-1.5-pro"
)
```

---

## 8. Mock (Testing)

**Provider Code:** `mock`  
**Configuration Prefix:** `provider.mock`

### Models

| Model ID | Description | Free | Use Case |
|----------|-------------|------|----------|
| `mock-model-1` | Mock Model 1 | ✅ | Testing, development |
| `mock-model-2` | Mock Model 2 | ✅ | Testing, development |

### Configuration

```properties
provider.mock.enabled=true
provider.mock.models=mock-model-1,mock-model-2
```

### Usage Example

```python
# No API keys needed!
response = facade.generate(
    "Test prompt",
    provider="mock",
    model_name="mock-model-1"
)
```

---

## Llama Models Summary

The system supports **6 different Llama model configurations**:

### Llama 2 (3 variants)
1. **AWS Bedrock**: `llama2-70b` → `meta.llama2-70b-chat-v1`
2. **Together AI**: `llama-2-70b-chat` → `meta-llama/Llama-2-70b-chat-hf`
3. **Hugging Face**: `meta-llama/Llama-2-70b-chat-hf`

### Llama 3 (3 variants)
1. **AWS Bedrock**: `llama3-8b` → `meta.llama3-8b-instruct-v1:0`
2. **Together AI**: `llama-3-8b-instruct` → `meta-llama/Llama-3-8b-chat-hf`
3. **Hugging Face**: `meta-llama/Llama-3-8b-instruct`

---

## Quick Reference Table

### All Models by Provider

| Provider | # Models | Key Models | Llama Support |
|----------|----------|------------|---------------|
| AWS Bedrock | 6 | Claude 3, Llama 2/3, Mistral | ✅ Llama 2 & 3 |
| Together AI | 4 | Llama 2/3, Mistral | ✅ Llama 2 & 3 |
| Hugging Face | 5 | Llama 2/3, Falcon, Mistral | ✅ Llama 2 & 3 |
| OpenAI | 4 | GPT-4, GPT-3.5 | ❌ |
| Anthropic | 4 | Claude 3 (Opus/Sonnet/Haiku) | ❌ |
| Cohere | 4 | Command, Command R | ❌ |
| Google | 4 | Gemini Pro/Ultra, PaLM 2 | ❌ |
| Mock | 2 | Testing models | ❌ |
| **Total** | **33** | **Diverse selection** | **6 Llama variants** |

---

## Provider Selection Guide

### By Use Case

**Complex Reasoning:**
- OpenAI GPT-4
- Anthropic Claude 3 Opus
- AWS Bedrock Claude 3 Opus

**Balanced Performance:**
- Anthropic Claude 3 Sonnet
- AWS Bedrock Claude 3 Sonnet
- Google Gemini Pro

**Cost-Effective:**
- OpenAI GPT-3.5 Turbo
- Together AI Llama 3 8B
- Anthropic Claude 3 Haiku
- AWS Bedrock Mistral 7B

**Open Source:**
- Together AI Llama 2/3
- Hugging Face Llama 2/3
- AWS Bedrock Llama 2/3

**Long Context:**
- Google Gemini 1.5 Pro (1M tokens!)
- Cohere Command R (128K tokens)
- Anthropic Claude 3 (200K tokens)

**Testing/Development:**
- Mock Models (free, no API needed)

### By Cost (Approximate)

**Free:**
- Mock Models

**Very Low ($0.20-0.50/1M tokens):**
- Together AI Llama 3 8B
- Anthropic Claude 3 Haiku
- Google Gemini Pro

**Low ($0.50-2.00/1M tokens):**
- OpenAI GPT-3.5 Turbo
- Cohere Command Light
- Together AI Mistral 7B

**Medium ($2.00-5.00/1M tokens):**
- Anthropic Claude 3 Sonnet
- Google Gemini Ultra
- Cohere Command R Plus

**High ($5.00-15.00/1M tokens):**
- OpenAI GPT-4
- Anthropic Claude 3 Opus

---

## Provider Feature Matrix

| Feature | Bedrock | Together | HuggingFace | OpenAI | Anthropic | Cohere | Google | Mock |
|---------|---------|----------|-------------|--------|-----------|--------|--------|------|
| Llama Models | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Streaming | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Chat API | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 100K+ Context | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Free Tier | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Open Source Models | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | N/A |

---

## Configuration Examples

### Minimal Configuration (Mock Only)

```properties
llm.default.provider=mock
llm.default.model=mock-model-1
provider.mock.enabled=true
```

### Production Configuration (Multiple Providers)

```properties
# Defaults
llm.default.provider=bedrock
llm.default.model=claude-3-sonnet

# AWS Bedrock
provider.bedrock.enabled=true
provider.bedrock.region=us-east-1
provider.bedrock.access_key=${AWS_ACCESS_KEY}
provider.bedrock.secret_key=${AWS_SECRET_KEY}

# Together AI
provider.together.enabled=true
provider.together.api_key=${TOGETHER_API_KEY}

# OpenAI
provider.openai.enabled=true
provider.openai.api_key=${OPENAI_API_KEY}

# Mock for testing
provider.mock.enabled=true
```

---

## Usage Patterns

### 1. Single Provider
```python
facade = LLMClientFacade('config.properties')
response = facade.generate("Your prompt")  # Uses default
```

### 2. Multiple Providers (Comparison)
```python
providers = [
    ("bedrock", "llama2-70b"),
    ("together", "llama-2-70b-chat"),
    ("huggingface", "meta-llama/Llama-2-70b-chat-hf")
]

for provider, model in providers:
    response = facade.generate(prompt, provider=provider, model_name=model)
    print(f"{provider}: {response}")
```

### 3. Fallback Strategy
```python
try:
    response = facade.generate(prompt, provider="openai", model_name="gpt-4")
except:
    response = facade.generate(prompt, provider="mock", model_name="mock-model-1")
```

---

**© 2025-2030 All Rights Reserved | Ashutosh Sinha | ajsinha@gmail.com**
