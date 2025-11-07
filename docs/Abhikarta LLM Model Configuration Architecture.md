# Abhikarta LLM Model Configuration Architecture

**Version:** 1.0  
**Last Updated:** November 6, 2025  
**Document Type:** Technical Reference, Configuration Guide & API Documentation

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

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Configuration Schema](#configuration-schema)
4. [ModelCapability Enum System](#modelcapability-enum-system)
5. [Provider Configurations](#provider-configurations)
6. [Capability Hierarchy & Relationships](#capability-hierarchy--relationships)
7. [Cost Management](#cost-management)
8. [Implementation Guidelines](#implementation-guidelines)
9. [Quick Reference](#quick-reference)
10. [Appendices](#appendices)

---

## Executive Summary

The Abhikarta LLM Model Configuration Architecture is a comprehensive, provider-agnostic system for managing Large Language Model (LLM) configurations across multiple AI service providers. This architecture enables seamless integration, configuration management, and orchestration of diverse LLM services including Anthropic, OpenAI, Google, Meta, Mistral, Cohere, Groq, HuggingFace, Together AI, Replicate, AWS Bedrock, Ollama, and custom mock implementations.

### Key Features

- **Unified Configuration Schema**: Standardized JSON structure for all providers
- **Multi-Provider Support**: 13+ major LLM providers supported
- **Type-Safe Capability Enum**: 64 standardized capabilities with Python enum support
- **Capability-Based Selection**: Automatic model selection based on required capabilities
- **Cost Optimization**: Built-in cost tracking and optimization features
- **Feature Parity Mapping**: Comprehensive capability matrix across providers
- **Version Management**: Model versioning and lifecycle tracking
- **Extensible Architecture**: Easy addition of new providers and models

### Supported Providers (13)

1. **Anthropic** - Claude models (3.7, 3.5, 3.0)
2. **OpenAI** - GPT models (4o, O1, 3.5 Turbo)
3. **Google** - Gemini models (2.0, 1.5)
4. **Meta** - Llama models (3.3, 3.2, 3.1, Code Llama)
5. **Mistral** - Mistral models (Large, Medium, Small)
6. **Cohere** - Command and Embed models
7. **Groq** - LPU-accelerated inference
8. **HuggingFace** - Open-source model hub
9. **Together AI** - Open-source models
10. **Replicate** - Container-based models
11. **AWS Bedrock** - Multi-provider platform
12. **Ollama** - Local deployment
13. **Mock** - Testing provider

---

## Architecture Overview

### System Architecture

The Abhikarta LLM system follows a layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│          (Business Logic, User Interface)                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Abhikarta LLM Orchestration Layer              │
│  (Model Selection, Routing, Cost Optimization)              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Configuration Management Layer                  │
│     (JSON Config Loader, Validation, Caching)               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Provider Abstraction Layer                      │
│        (Unified API Interface, Protocol Adapters)           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌───────┬───────┬───────┬───────┬───────┬───────┬───────────┐
│Anthro │OpenAI │Google │ Meta  │Mistral│Cohere │  Others   │
│ pic   │       │       │       │       │       │  (10+)    │
└───────┴───────┴───────┴───────┴───────┴───────┴───────────┘
```

### Design Principles

1. **Provider Agnosticism**: No vendor lock-in, easy provider switching
2. **Declarative Configuration**: All settings defined in JSON
3. **Capability-Driven**: Select models based on required features
4. **Cost-Aware**: Built-in cost tracking and optimization
5. **Versioned Models**: Track model versions and deprecations
6. **Extensibility**: Easy to add new providers and capabilities
7. **Type Safety**: Strongly-typed configuration schema with Python enums

---

## Configuration Schema

### Root Schema Structure

Every provider configuration follows this top-level structure:

```json
{
  "provider": "string",              // Provider identifier (lowercase)
  "api_version": "string",           // API version (e.g., "v1", "2023-06-01")
  "base_url": "string",              // Primary API endpoint URL
  "notes": { ... },                  // Provider-specific documentation
  "models": [ ... ],                 // Array of model configurations
  "model_families": { ... },         // Optional: Model grouping
  "prompt_caching": { ... },         // Optional: Caching configuration
  "extended_thinking": { ... },      // Optional: Advanced reasoning features
  "batch_api": { ... },              // Optional: Batch processing features
  "vision_capabilities": { ... },    // Optional: Vision feature details
  "tool_use": { ... },               // Optional: Function calling details
  "deployment_options": { ... },     // Optional: Deployment configurations
  "best_practices": { ... }          // Optional: Usage recommendations
}
```

### Model Object Schema

Each model in the `models` array has this structure:

```json
{
  "name": "string",                    // Model identifier
  "model_id": "string",                // Optional: API-specific model ID
  "version": "string",                 // Model version
  "description": "string",             // Human-readable description
  "provider": "string",                // Optional: Original model provider
  "strengths": ["string"],             // Model's key strengths
  "context_window": number,            // Maximum input tokens
  "max_output": number,                // Maximum output tokens
  "parameters": "string",              // Optional: Model size (e.g., "70B")
  "license": "string",                 // Optional: Licensing information
  "cost": { ... },                     // Pricing structure
  "performance": { ... },              // Optional: Performance metrics
  "capabilities": { ... }              // Feature flags
}
```

### Cost Object Schema

Pricing varies by provider and model:

```json
{
  // Standard pricing (most common)
  "input_per_1k": number,              // Cost per 1K input tokens (USD)
  "output_per_1k": number,             // Cost per 1K output tokens (USD)
  
  // Alternative pricing scales
  "input_per_1m": number,              // Cost per 1M input tokens (Anthropic)
  "output_per_1m": number,             // Cost per 1M output tokens
  
  // Tiered pricing (Google)
  "input_per_1m_0_128k": number,       // First 128K tokens
  "input_per_1m_128k_plus": number,    // After 128K tokens
  
  // Cached pricing
  "cached_input_per_1k": number,       // Cached input cost (OpenAI)
  "cache_write_per_1m": number,        // Cache write cost (Anthropic)
  "cache_read_per_1m": number,         // Cache read cost (Anthropic)
  
  // Audio pricing (OpenAI)
  "audio_input_per_1m": number,        // Audio input per minute
  "audio_output_per_1m": number,       // Audio output per minute
  
  // Special notes
  "note": "string"                     // Additional pricing information
}
```

### Capabilities Object Schema

The capabilities object defines what each model can do:

```json
{
  // Core capabilities (boolean)
  "chat": boolean,
  "completion": boolean,
  "streaming": boolean,
  "function_calling": boolean,
  "tool_use": boolean,
  "vision": boolean,
  "audio_input": boolean,
  "audio_output": boolean,
  "video_input": boolean,
  "code_execution": boolean,
  "json_mode": boolean,
  "grounding": boolean,
  "prompt_caching": boolean,
  "extended_thinking": boolean,
  "batch_api": boolean,
  "thinking_mode": boolean,
  "embeddings": boolean,
  "moderation": boolean,
  "fine_tuning": boolean,
  // ... and 40+ more
  
  // Metadata fields (non-boolean)
  "dimensions": number,                // Embedding dimensions
  "embedding_types": array,            // Embedding types
  "languages": array,                  // Supported languages
  "quantization": array                // Quantization formats
}
```

---

## ModelCapability Enum System

### Overview

The `ModelCapability` enum provides a type-safe, comprehensive enumeration of all 64 LLM capabilities across supported providers.

```python
from abhikarta import ModelCapability, ProviderType

# Check capability
if ModelCapability.VISION.value in model["capabilities"]:
    process_image()

# Use helper methods
multimodal_caps = ModelCapability.get_multimodal_capabilities()
```

### All Capabilities (64)

#### Core Text Capabilities (3)
```
CHAT                    Conversational interactions
COMPLETION              Text completion
STREAMING               Real-time streaming
```

#### Function & Tool Capabilities (5)
```
FUNCTION_CALLING        Function/API calling
TOOL_USE                External tool integration
WEB_SEARCH              Built-in web search
GROUNDING               Real-time data grounding
GROUNDED_GENERATION     Document-grounded generation
```

#### Multimodal Capabilities (5)
```
VISION                  Image understanding
AUDIO_INPUT             Audio processing
AUDIO_OUTPUT            Audio generation
VIDEO_INPUT             Video understanding
MULTIMODAL              General multimodal
```

#### Audio Processing Capabilities (12)
```
AUDIO_TRANSCRIPTION     Speech-to-text
AUDIO_TRANSLATION       Audio translation
SPEECH_TO_TEXT          Voice transcription
TEXT_TO_SPEECH          Voice synthesis
TRANSCRIPTION           General transcription
TRANSLATION             Language translation
DIARIZATION             Speaker identification
TIMESTAMP               Timing information
WORD_TIMESTAMPS         Word-level timing
WORD_LEVEL_TIMESTAMPS   Detailed timing
VOICES                  TTS voices [metadata]
AUDIO_GENERATION        Audio content generation
```

#### Image Processing Capabilities (9)
```
IMAGE_GENERATION        Text-to-image
IMAGE_EDITING           Image modification
IMAGE_VARIATIONS        Create variations
IMAGE_CAPTIONING        Generate descriptions
IMAGE_ENHANCEMENT       Quality improvement
INPAINTING              Fill masked areas
OUTPAINTING             Extend boundaries
UPSCALING               Resolution enhancement
BACKGROUND_REMOVAL      Background extraction
```

#### Video Capabilities (1)
```
VIDEO_GENERATION        Video creation
```

#### Code Capabilities (2)
```
CODE_EXECUTION          Execute code
FILL_IN_MIDDLE          Code completion
```

#### Reasoning Capabilities (2)
```
EXTENDED_THINKING       Visible reasoning (Claude 3.7, O1)
THINKING_MODE           Problem-solving mode (Gemini)
```

#### Structured Output (1)
```
JSON_MODE               Guaranteed JSON output
```

#### Optimization Capabilities (4)
```
PROMPT_CACHING          Context caching (50-90% savings)
CACHING                 General caching
BATCH_API               Batch processing (50% discount)
QUANTIZATION            Model quantization [metadata]
```

#### Embedding & Search Capabilities (4)
```
EMBEDDINGS              Vector embeddings
EMBEDDING               General embedding
RERANKING               Search result reranking
RELEVANCE_SCORING       Relevance scoring
```

#### Question Answering (1)
```
QUESTION_ANSWERING      Answer from context
```

#### Safety & Moderation (3)
```
MODERATION              Content filtering
GUARDRAILS              Safety guardrails
CATEGORIES              Moderation categories [metadata]
```

#### Customization (2)
```
FINE_TUNING             Model fine-tuning
TUNING                  General tuning
```

#### Citation & Attribution (2)
```
CITATIONS               Source citations
ATTRIBUTION             Source attribution
```

#### Prompt Capabilities (1)
```
PROMPT_GENERATION       Generate optimized prompts
```

#### Metadata Fields (8)
These are non-boolean fields that contain data:
```
DIMENSIONS              Embedding dimensions [int]
EMBEDDING_TYPES         Embedding types [array]
MAX_DOCUMENTS           Document limit [int]
LANGUAGES               Supported languages [array]
TASK_TYPES              Task types [array]
ASPECT_RATIOS           Image ratios [array]
VOICES                  TTS voices [array]
CATEGORIES              Moderation categories [array]
```

#### Status Flags (1)
```
DEPRECATED              Model deprecation status
```

### Helper Methods

The enum provides helper methods for capability grouping:

```python
# Get capability groups
ModelCapability.get_core_capabilities()
# → [CHAT, COMPLETION, STREAMING]

ModelCapability.get_multimodal_capabilities()
# → [VISION, AUDIO_INPUT, AUDIO_OUTPUT, VIDEO_INPUT, MULTIMODAL]

ModelCapability.get_tool_capabilities()
# → [FUNCTION_CALLING, TOOL_USE, WEB_SEARCH, GROUNDING, GROUNDED_GENERATION]

ModelCapability.get_optimization_capabilities()
# → [PROMPT_CACHING, CACHING, BATCH_API, QUANTIZATION]

ModelCapability.get_reasoning_capabilities()
# → [EXTENDED_THINKING, THINKING_MODE]

ModelCapability.get_audio_capabilities()
# → [AUDIO_INPUT, AUDIO_OUTPUT, AUDIO_TRANSCRIPTION, ...]

ModelCapability.get_image_capabilities()
# → [IMAGE_GENERATION, IMAGE_EDITING, IMAGE_VARIATIONS, ...]

ModelCapability.get_embedding_capabilities()
# → [EMBEDDINGS, EMBEDDING, RERANKING, RELEVANCE_SCORING]

# Check if capability is metadata
ModelCapability.is_metadata_field(capability)
# → True if metadata (int/array), False if boolean
```

### Usage Patterns

#### Basic Capability Checking
```python
# Check single capability
if ModelCapability.VISION.value in model["capabilities"]:
    process_image()

# Check multiple capabilities
required = [ModelCapability.VISION, ModelCapability.FUNCTION_CALLING]
has_all = all(
    model["capabilities"].get(cap.value, False)
    for cap in required
)
```

#### Filter Models by Capability
```python
# Find all vision-capable models
vision_models = [
    m for m in models
    if m["capabilities"].get(ModelCapability.VISION.value, False)
]

# Find models with multiple capabilities
def filter_by_capabilities(models, required_caps):
    return [
        m for m in models
        if all(m["capabilities"].get(c.value, False) for c in required_caps)
    ]

suitable_models = filter_by_capabilities(models, [
    ModelCapability.CHAT,
    ModelCapability.VISION,
    ModelCapability.FUNCTION_CALLING
])
```

#### Handle Metadata Fields
```python
# Distinguish between boolean and metadata fields
if ModelCapability.is_metadata_field(cap):
    value = capabilities[cap.value]  # int, array, etc.
else:
    value = capabilities.get(cap.value, False)  # boolean
```

#### Compare Providers
```python
# Compare capability support across providers
from collections import defaultdict

def compare_capability(models, capability):
    providers = defaultdict(list)
    for model in models:
        if model["capabilities"].get(capability.value, False):
            providers[model["provider"]].append(model["name"])
    return dict(providers)

vision_support = compare_capability(models, ModelCapability.VISION)
# Output: {"anthropic": ["claude-3-7-sonnet", ...], "openai": ["gpt-4o", ...], ...}
```

---

## Provider Configurations

### Complete Provider Summary

This section provides detailed configuration information for all 13 supported providers.

| # | Provider | Type | Specialty | Base URL | Key Feature |
|---|----------|------|-----------|----------|-------------|
| 1 | Anthropic | Proprietary | Advanced reasoning | api.anthropic.com | Extended thinking |
| 2 | OpenAI | Proprietary | Multimodal | api.openai.com | Audio I/O, DALL-E |
| 3 | Google | Proprietary | Long context | generativelanguage.googleapis.com | 2M tokens, video |
| 4 | Meta | Open-source | Efficiency | Via platforms | Open models |
| 5 | Mistral | Proprietary | European AI | api.mistral.ai | Multilingual, MoE |
| 6 | Cohere | Proprietary | Enterprise RAG | api.cohere.ai | Reranking, citations |
| 7 | Groq | Platform | Speed | api.groq.com | LPU, sub-second |
| 8 | HuggingFace | Platform | Open-source hub | api-inference.huggingface.co | 100K+ models |
| 9 | Together AI | Platform | Open models | api.together.xyz | Fast, cost-effective |
| 10 | Replicate | Platform | Docker-based | api.replicate.com | Image/video gen |
| 11 | AWS Bedrock | Platform | Multi-provider | Regional AWS | Enterprise security |
| 12 | Ollama | Local | Privacy | localhost:11434 | Offline, free |
| 13 | Mock | Testing | Development | null | Testing only |

### Provider Comparison Matrix

| Feature | Anthropic | OpenAI | Google | Mistral | Cohere |
|---------|-----------|--------|--------|---------|--------|
| **Pricing Model** | Per 1M | Per 1K | Tiered | Per 1M | Per token |
| **Max Context** | 200K | 128K | 2M | 128K | 128K |
| **Best For** | Reasoning | Multimodal | Long context | Coding | Enterprise RAG |
| **Unique Feature** | Extended thinking | Audio I/O | Video | European | Reranking |
| **Enterprise** | AWS/GCP | Yes | Vertex AI | Yes | Yes |

| Feature | Groq | HuggingFace | Together | Replicate | Bedrock |
|---------|------|-------------|----------|-----------|---------|
| **Pricing Model** | Free (beta) | Free/Paid | Per token | Per prediction | AWS pricing |
| **Max Context** | 128K | Varies | Varies | Varies | Varies |
| **Best For** | Speed | Open source | Open models | Image/video | Multi-provider |
| **Unique Feature** | LPU speed | Self-hosting | Model variety | Docker-based | AWS integration |
| **Enterprise** | Yes | Yes | Yes | Flexible | Enterprise-grade |

### Capability Support Matrix

| Capability | Anthropic | OpenAI | Google | Groq | Meta (Various) |
|------------|-----------|--------|--------|------|----------------|
| **CHAT** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **STREAMING** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **FUNCTION_CALLING** | ✅ | ✅ | ✅ | ✅ | 3.1+ |
| **VISION** | ✅ (3+) | ✅ (4o) | ✅ | 3.2 | 3.2 Vision |
| **AUDIO_INPUT** | ❌ | ✅ (4o) | ✅ (2.0) | ❌ | ❌ |
| **AUDIO_OUTPUT** | ❌ | ✅ (4o) | ✅ (2.0) | ❌ | ❌ |
| **VIDEO_INPUT** | ❌ | ❌ | ✅ | ❌ | ❌ |
| **EXTENDED_THINKING** | ✅ (3.7) | ✅ (O1) | ✅ (2.0-T) | ❌ | ❌ |
| **PROMPT_CACHING** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **BATCH_API** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **JSON_MODE** | Prompting | ✅ | ✅ | ✅ | ❌ |
| **CODE_EXECUTION** | ❌ | Assistants | ✅ | ❌ | ❌ |
| **GROUNDING** | ❌ | ❌ | Vertex | ❌ | ❌ |
| **QUANTIZATION** | ❌ | ❌ | ❌ | ❌ | HF/Ollama |

### Anthropic (Claude)

**Specialty:** Advanced reasoning, extended thinking, vision, tool use  
**Base URL:** `https://api.anthropic.com`  
**API Version:** `2023-06-01`

**Key Models:**
- Claude 3.7 Sonnet (extended thinking)
- Claude 3.5 Sonnet (latest)
- Claude 3.5 Haiku (fast, cost-effective)
- Claude 3 Opus (most capable)

**Unique Features:**
- Extended thinking capabilities (Claude 3.7)
- Prompt caching (90% cost reduction on reads)
- Batch API (50% discount)
- Constitutional AI training
- 200K context window

**Pricing:** Per 1M tokens, with cache write/read pricing

### OpenAI (GPT)

**Specialty:** Multimodal (text, vision, audio), broad ecosystem  
**Base URL:** `https://api.openai.com`  
**API Version:** `v1`

**Key Models:**
- GPT-4o (multimodal flagship)
- GPT-4o mini (cost-effective)
- O1/O1-mini (reasoning)
- GPT-4 Turbo

**Unique Features:**
- Native audio input/output (GPT-4o)
- Real-time audio API (WebSocket)
- Structured outputs (JSON schema)
- DALL-E image generation
- Assistants API
- Whisper speech-to-text

**Pricing:** Per 1K tokens, 50% cache discount

### Google (Gemini)

**Specialty:** Extreme context (2M tokens), multimodal, video  
**Base URL:** `https://generativelanguage.googleapis.com`  
**API Version:** `v1`

**Key Models:**
- Gemini 2.0 Flash (latest, multimodal live)
- Gemini 2.0 Flash Thinking (extended reasoning)
- Gemini 1.5 Pro (2M context)
- Gemini 1.5 Flash (efficient)

**Unique Features:**
- 2M token context window (1.5 Pro)
- Native video understanding
- Built-in code execution (Python)
- Grounding with Google Search (Vertex AI)
- Thinking mode (2.0)
- Multimodal live API

**Pricing:** Tiered by context length (0-128K, 128K+)

### Meta (Llama)

**Specialty:** Open-source, efficient, widely available  
**Available Via:** Groq, HuggingFace, Together AI, Replicate, Ollama

**Key Models:**
- Llama 3.3 70B (latest)
- Llama 3.2 Vision (11B, 90B)
- Llama 3.1 (8B, 70B, 405B)
- Code Llama (specialized for code)

**Unique Features:**
- Open-source, permissive licensing
- Multiple size variants (1B to 405B)
- Vision models (3.2)
- Function calling (3.1)
- Available across multiple platforms

**Pricing:** Varies by platform (Groq free, others paid)

### Groq (LPU Platform)

**Specialty:** Ultra-fast inference (10x faster), low latency  
**Base URL:** `https://api.groq.com/openai/v1`  
**API Version:** `v1`

**Key Features:**
- LPU (Language Processing Unit) technology
- Sub-second response times
- 300-800 tokens/second throughput
- Time to first token: 30-100ms
- OpenAI-compatible API
- Currently free (beta)

**Models:** Llama 3.3, Llama 3.2, Mixtral, Gemma

### HuggingFace

**Specialty:** Open-source models, massive selection, self-hosting  
**Base URL:** `https://api-inference.huggingface.co`

**Key Features:**
- 100K+ models available
- Inference API (free tier)
- Inference Endpoints (dedicated)
- Quantization support (GPTQ, AWQ, GGUF)
- Parameter-efficient fine-tuning
- Self-hosting options

### Mistral

**Specialty:** European AI, strong coding, multilingual, efficient  
**Base URL:** `https://api.mistral.ai`  
**API Version:** `v1`

**Key Models:**
- Mistral Large 2 (128K context, function calling)
- Mistral Medium (balanced performance)
- Mistral Small (efficient, cost-effective)
- Codestral (code-specialized, 32K context)
- Mixtral 8x7B/8x22B (Mixture-of-Experts)
- Pixtral 12B (vision model)

**Unique Features:**
- European AI provider (data residency options)
- Strong multilingual support (European languages)
- Mixture-of-Experts architecture (Mixtral)
- Code-specialized model (Codestral)
- Function calling (Large, Small)
- Vision capabilities (Pixtral)
- La Plateforme API
- Competitive pricing

**Strengths:**
- Excellent code generation
- Strong European language support
- Fast inference
- Cost-effective
- Enterprise-ready

**Pricing:** Competitive per-token pricing, similar to OpenAI scale

**Use Cases:**
- European deployments with data residency requirements
- Multilingual applications
- Code generation and analysis
- Cost-sensitive production workloads

---

### Cohere

**Specialty:** Enterprise RAG, embeddings, reranking, classification  
**Base URL:** `https://api.cohere.ai`  
**API Version:** `v1`

**Key Models:**
- Command R+ (RAG-optimized, 128K context)
- Command R (efficient RAG)
- Command (general purpose)
- Embed v3 (multilingual embeddings)
- Embed English v3 (English-optimized)
- Rerank v3 (search result reranking)

**Unique Features:**
- RAG-optimized models (Command R series)
- Best-in-class reranking
- Multiple embedding types (search, classification, clustering)
- Built-in citation support
- Grounded generation
- Multiple embedding dimensions (1024, 384, 256, 128)
- Fine-tuning support
- Canadian provider

**Strengths:**
- Exceptional RAG performance
- Enterprise-grade embeddings
- Reranking capabilities
- Citation and attribution
- Multilingual embeddings
- Strong enterprise support

**Pricing:** Per-token for LLMs, per-request for embeddings/reranking

**Use Cases:**
- Enterprise search and RAG
- Question answering systems
- Document analysis
- Semantic search
- Content classification
- Citation-required applications

---

### Together AI

**Specialty:** Open-source models, fast inference, competitive pricing  
**Base URL:** `https://api.together.xyz`  
**API Version:** `v1`

**Key Models:**
- Llama 3.1 (8B, 70B, 405B)
- Mixtral 8x7B/8x22B
- Qwen 2.5 (multiple sizes)
- DeepSeek Coder
- Gemma 2 (9B, 27B)
- StripedHyena
- And 100+ more open-source models

**Unique Features:**
- Wide selection of open-source models
- Fast inference with optimized infrastructure
- Competitive pricing
- Function calling support
- Vision models available
- Flexible deployment options
- Research-friendly
- Regular model updates

**Strengths:**
- Extensive open-source model catalog
- Fast inference speeds
- Cost-effective
- Latest model versions
- Developer-friendly API
- Good documentation

**Pricing:** Competitive per-token pricing, varies by model

**Use Cases:**
- Open-source model experimentation
- Cost-sensitive production workloads
- Research and development
- Multi-model comparison
- Academic projects

---

### Replicate

**Specialty:** Run models via Docker, extensive model library, image/video generation  
**Base URL:** `https://api.replicate.com`  
**API Version:** `v1`

**Key Models:**
- Llama models (via Meta)
- Stable Diffusion (image generation)
- FLUX (advanced image generation)
- Whisper (speech-to-text)
- SDXL (high-res image generation)
- Video generation models
- 1000+ community models

**Unique Features:**
- Docker-based model deployment
- Pay-per-prediction pricing
- No server management
- Image and video generation models
- Custom model deployment
- Extensive community model library
- Version pinning
- Hardware flexibility

**Strengths:**
- Easy deployment (Docker)
- Diverse model types (text, image, video, audio)
- Community contributions
- No infrastructure management
- Flexible pricing
- Good for experimentation

**Pricing:** Pay-per-prediction, varies by model and hardware

**Use Cases:**
- Image and video generation
- Multi-modal applications
- Rapid prototyping
- Custom model deployment
- Creative applications
- Research projects

**Model Format:**
- Uses `provider/model-name:version` format
- Example: `meta/llama-3.1-70b-instruct:latest`

---

### AWS Bedrock

**Specialty:** Multi-model access, enterprise security, AWS integration  
**Base URL:** Regional AWS endpoint  
**API Version:** AWS API version

**Available Models:**
- Anthropic Claude (all versions)
- Meta Llama (multiple versions)
- Mistral models
- Cohere Command/Embed
- AI21 Jurassic
- Amazon Titan (text, embeddings, multimodal)
- Stability AI (image generation)

**Unique Features:**
- Multiple providers in one platform
- AWS security and compliance (VPC, KMS, IAM)
- Guardrails for responsible AI
- Model evaluation tools
- Knowledge bases (managed RAG)
- Agents framework
- Private endpoints
- Fine-tuning support (select models)
- No data leaves AWS
- Enterprise SLAs

**Strengths:**
- AWS native integration
- Enterprise security and compliance
- Multi-provider access
- Unified billing
- Managed infrastructure
- Guardrails and safety features
- Regional data residency

**Pricing:** Pay-per-use, varies by model (On-Demand or Provisioned Throughput)

**Use Cases:**
- Enterprise deployments
- Regulated industries (HIPAA, SOC 2, etc.)
- AWS-native applications
- Multi-model strategies
- Compliance-sensitive workloads

**Limitations:**
- Model availability varies by region
- Slight lag in latest model versions
- Some features not available (e.g., no prompt caching yet)
- Requires AWS account and IAM setup

**Authentication:** AWS credentials (IAM, STS, access keys)

---

### Ollama

**Specialty:** Local deployment, privacy, offline usage  
**Base URL:** `http://localhost:11434`

**Key Models:**
- Llama 3.2/3.1/3 (all sizes)
- Mistral/Mixtral
- Gemma 2
- Phi-3
- Code Llama
- Qwen 2.5
- And 100+ quantized models

**Unique Features:**
- Fully local deployment
- No internet required
- Complete privacy (data never leaves machine)
- Free and open-source
- Quantized models (GGUF format)
- Simple CLI and API
- macOS, Linux, Windows support
- GPU acceleration (CUDA, Metal)
- Model library management

**Strengths:**
- Complete privacy and security
- No API costs
- Offline capability
- Fast local inference
- Easy setup
- Multiple quantization levels
- Community-driven

**Quantization Options:**
- Q4_0, Q4_K_M (4-bit, balanced)
- Q5_0, Q5_K_M (5-bit, better quality)
- Q6_K (6-bit, high quality)
- Q8_0 (8-bit, highest quality)

**Pricing:** Free (only hardware costs)

**Use Cases:**
- Privacy-sensitive applications
- Offline environments
- Development and testing
- Cost-sensitive projects
- Air-gapped systems
- Personal AI assistants

**Hardware Requirements:**
- Minimum: 8GB RAM (for 7B models)
- Recommended: 16GB+ RAM, GPU with 8GB+ VRAM
- 405B models: 256GB+ RAM or multi-GPU

**Installation:**
```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.1

# Run
ollama run llama3.1
```

---

## Capability Hierarchy & Relationships

### Capability Dependency Graph

```
                        CHAT (Foundation)
                          │
                          ▼
                      STREAMING
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    FUNCTION_CALLING   VISION      AUDIO_INPUT
          │               │               │
          ▼               ▼               ▼
      TOOL_USE    IMAGE_GENERATION  TEXT_TO_SPEECH
          │               │               │
          ▼               ▼               ▼
    WEB_SEARCH      UPSCALING       DIARIZATION
          │               
          ▼               
     GROUNDING ──> GROUNDED_GENERATION


    PROMPT_CACHING ──┐
    BATCH_API ───────┼──> Cost Optimization
    QUANTIZATION ────┘


    EXTENDED_THINKING ──┐
    THINKING_MODE ──────┼──> Advanced Reasoning
                        │
                        └──> Complex Problem Solving
```

### Model Selection Decision Tree

```
User Request
    │
    ▼
┌─────────────────┐
│ Requires Vision?│
└────────┬────────┘
         │
    Yes  │  No
    ┌────┴────┐
    │         │
    ▼         ▼
Filter:    Text-only
VISION     models
    │         │
    └────┬────┘
         │
         ▼
┌──────────────────────┐
│ Function Calling?    │
└─────────┬────────────┘
          │
     Yes  │  No
     ┌────┴────┐
     │         │
     ▼         ▼
  Filter    Continue
  FUNC      without
     │         │
     └────┬────┘
          │
          ▼
┌──────────────────────┐
│ Budget Constraint?   │
└─────────┬────────────┘
          │
    Low   │   High
     ┌────┴────┐
     │         │
     ▼         ▼
  Cheapest  Best
  model     quality
     │         │
     └────┬────┘
          │
          ▼
   Selected Model
```

### Usage Flow

```
Application Request
         │
         ▼
Extract Required Capabilities
         │
         ▼
Query ModelCapability Enum
         │
         ▼
Filter Available Models
         │
         ▼
Score & Select Best Model
         │
         ▼
Execute Request
```

---

## Cost Management

### Cost Calculation Formulas

#### Standard Calculation
```
Total Cost = (Input Tokens / Scale) × Input Rate 
           + (Output Tokens / Scale) × Output Rate

Scale = 1000 (per 1K) or 1000000 (per 1M)
```

#### With Caching (Anthropic)
```
Cache Write Cost = (Cache Tokens / 1M) × Cache Write Rate (25% premium)
Cache Read Cost = (Cache Tokens / 1M) × Cache Read Rate (90% discount)
New Input Cost = (New Tokens / 1M) × Input Rate
```

#### Tiered Pricing (Google)
```
Input Cost = (First 128K / 1M) × Tier1 Rate
           + (Remaining / 1M) × Tier2 Rate
```

### Cost Optimization Strategies

1. **Model Selection by Task**
   - Simple tasks → Smaller models (Haiku, GPT-4o mini, Gemini Flash)
   - Complex reasoning → Premium models (Claude 3.7, O1, Gemini Pro)
   - Code → Specialized models (Codestral, Code Llama)

2. **Prompt Caching**
   - Cache system prompts and instructions
   - Cache document context in RAG
   - Savings: 50-90% on repeated content
   - Available: Anthropic, OpenAI, Google

3. **Batch Processing**
   - Use batch API for non-urgent requests
   - Savings: 50% off standard pricing
   - Trade-off: 24-hour processing time
   - Available: Anthropic, OpenAI, Google

4. **Context Management**
   - Minimize unnecessary tokens
   - Summarize long conversations
   - Use sliding windows for chat history

5. **Provider Arbitrage**
   - Compare costs across providers
   - Example Llama 3.1 70B:
     - Groq: Free (beta)
     - Together AI: $0.88/$0.88 per 1M
     - Replicate: $0.65/$2.60 per 1M

6. **Output Token Management**
   - Set appropriate `max_tokens`
   - Output costs 3-10x input
   - Avoid unnecessary verbosity

### Cost Comparison Examples

**Task: Document Analysis (100K context + 1K output)**

| Model | Provider | Cost |
|-------|----------|------|
| Claude 3.5 Sonnet | Anthropic | $1.80 |
| Claude 3.5 Sonnet (cached) | Anthropic | $0.33 |
| GPT-4o | OpenAI | $0.58 |
| Gemini 1.5 Pro | Google | $0.63 |
| Llama 3.1 70B | Groq | Free |

**Task: Simple Chat (2K input + 500 output)**

| Model | Provider | Cost |
|-------|----------|------|
| Claude 3.5 Haiku | Anthropic | $0.01 |
| GPT-4o mini | OpenAI | $0.0006 |
| Gemini 1.5 Flash | Google | $0.0015 |
| Llama 3.1 8B | Groq | Free |

---

## Implementation Guidelines

### Configuration Loader

```python
import json
from typing import Dict, List, Optional

class LLMConfigManager:
    """Manage LLM provider configurations"""
    
    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        self.providers = {}
        self.load_all_configs()
    
    def load_all_configs(self):
        """Load all provider configurations"""
        config_files = [
            "anthropic.json", "openai.json", "google.json",
            "meta.json", "groq.json", "huggingface.json",
            "mistral.json", "cohere.json", "together.json",
            "replicate.json", "awsbedrock.json", "ollama.json",
            "mock.json"
        ]
        
        for file in config_files:
            path = f"{self.config_dir}/{file}"
            try:
                with open(path, 'r') as f:
                    config = json.load(f)
                    provider = config['provider']
                    self.providers[provider] = config
            except FileNotFoundError:
                continue
    
    def get_model_config(self, provider: str, model: str) -> Optional[Dict]:
        """Get configuration for specific model"""
        provider_config = self.providers.get(provider, {})
        models = provider_config.get('models', [])
        
        for m in models:
            if m['name'] == model:
                return m
        return None
    
    def find_models_by_capability(self, capability: str) -> List[Dict]:
        """Find all models with specific capability"""
        from abhikarta import ModelCapability
        
        matching_models = []
        for provider_name, provider_config in self.providers.items():
            for model in provider_config.get('models', []):
                capabilities = model.get('capabilities', {})
                if capabilities.get(capability, False):
                    matching_models.append({
                        'provider': provider_name,
                        'model': model['name'],
                        'config': model
                    })
        return matching_models
    
    def find_cheapest_model(self, 
                           input_tokens: int,
                           output_tokens: int,
                           capabilities: Optional[List[str]] = None) -> Dict:
        """Find cheapest model matching requirements"""
        candidates = []
        
        for provider_name, provider_config in self.providers.items():
            for model in provider_config.get('models', []):
                # Check capabilities
                if capabilities:
                    model_caps = model.get('capabilities', {})
                    if not all(model_caps.get(cap) for cap in capabilities):
                        continue
                
                # Calculate cost
                cost = self._calculate_cost(
                    model.get('cost', {}), 
                    input_tokens, 
                    output_tokens
                )
                
                candidates.append({
                    'provider': provider_name,
                    'model': model['name'],
                    'cost': cost,
                    'config': model
                })
        
        candidates.sort(key=lambda x: x['cost'])
        return candidates[0] if candidates else None
    
    def _calculate_cost(self, cost_config: Dict, 
                       input_tokens: int, 
                       output_tokens: int) -> float:
        """Calculate cost for given token counts"""
        if 'input_per_1k' in cost_config:
            input_cost = (input_tokens / 1000) * cost_config['input_per_1k']
            output_cost = (output_tokens / 1000) * cost_config['output_per_1k']
        elif 'input_per_1m' in cost_config:
            input_cost = (input_tokens / 1_000_000) * cost_config['input_per_1m']
            output_cost = (output_tokens / 1_000_000) * cost_config['output_per_1m']
        else:
            return 0.0
        
        return input_cost + output_cost
```

### Model Router with Capability-Based Selection

```python
from abhikarta import ModelCapability
from typing import List, Dict

class ModelRouter:
    """Route requests to appropriate models based on capabilities"""
    
    def __init__(self, config_manager: LLMConfigManager):
        self.config_manager = config_manager
    
    def route_request(self, 
                     required_capabilities: List[ModelCapability],
                     budget: str = "medium",
                     latency: str = "normal") -> Dict:
        """
        Route request to appropriate model
        
        Args:
            required_capabilities: List of required ModelCapability enums
            budget: "low", "medium", or "high"
            latency: "realtime", "normal", or "batch"
            
        Returns:
            Selected model configuration
        """
        # Convert enums to strings
        cap_strings = [cap.value for cap in required_capabilities]
        
        # Get all models matching capabilities
        candidates = []
        for provider_name, provider_config in self.config_manager.providers.items():
            for model in provider_config.get('models', []):
                capabilities = model.get('capabilities', {})
                
                # Check if model has all required capabilities
                if all(capabilities.get(cap, False) for cap in cap_strings):
                    # Calculate estimated cost (1K input, 500 output)
                    cost = self.config_manager._calculate_cost(
                        model.get('cost', {}), 1000, 500
                    )
                    
                    candidates.append({
                        'provider': provider_name,
                        'model': model['name'],
                        'config': model,
                        'estimated_cost': cost
                    })
        
        if not candidates:
            raise ValueError(
                f"No models found with capabilities: {cap_strings}"
            )
        
        # Apply budget filter
        candidates = self._filter_by_budget(candidates, budget)
        
        # Select based on latency requirement
        if latency == "realtime":
            selected = self._select_fastest(candidates)
        elif latency == "batch":
            selected = self._select_cheapest(candidates)
        else:
            selected = self._select_balanced(candidates)
        
        return selected
    
    def _filter_by_budget(self, models: List[Dict], budget: str) -> List[Dict]:
        """Filter models by budget constraint"""
        models.sort(key=lambda x: x.get('estimated_cost', 0))
        
        if budget == "low":
            return models[:len(models)//3]
        elif budget == "high":
            return models[-len(models)//3:]
        else:
            third = len(models) // 3
            return models[third:2*third]
    
    def _select_fastest(self, models: List[Dict]) -> Dict:
        """Select fastest model (prioritize Groq LPU)"""
        groq_models = [m for m in models if m['provider'] == 'groq']
        return groq_models[0] if groq_models else models[0]
    
    def _select_cheapest(self, models: List[Dict]) -> Dict:
        """Select cheapest model"""
        models.sort(key=lambda x: x.get('estimated_cost', 0))
        return models[0]
    
    def _select_balanced(self, models: List[Dict]) -> Dict:
        """Select balanced model (capability/cost ratio)"""
        for model in models:
            config = model['config']
            capabilities = config.get('capabilities', {})
            
            # Count advanced capabilities
            advanced_caps = sum([
                capabilities.get('function_calling', False),
                capabilities.get('vision', False),
                capabilities.get('prompt_caching', False),
                capabilities.get('extended_thinking', False),
                capabilities.get('batch_api', False)
            ])
            
            cost = model.get('estimated_cost', 0)
            model['score'] = advanced_caps / (cost + 0.001)
        
        models.sort(key=lambda x: x['score'], reverse=True)
        return models[0]
```

### Usage Example

```python
from abhikarta import ModelCapability

# Initialize
config_manager = LLMConfigManager(config_dir="./configs")
router = ModelRouter(config_manager)

# Find models with specific capabilities
vision_models = config_manager.find_models_by_capability(
    ModelCapability.VISION.value
)
print(f"Found {len(vision_models)} models with vision")

# Route a request
selected = router.route_request(
    required_capabilities=[
        ModelCapability.CHAT,
        ModelCapability.VISION,
        ModelCapability.FUNCTION_CALLING
    ],
    budget="medium",
    latency="normal"
)
print(f"Selected: {selected['provider']}/{selected['model']}")

# Find cheapest model for a task
cheapest = config_manager.find_cheapest_model(
    input_tokens=5000,
    output_tokens=1000,
    capabilities=[
        ModelCapability.CHAT.value,
        ModelCapability.STREAMING.value
    ]
)
print(f"Cheapest: {cheapest['provider']}/{cheapest['model']} - ${cheapest['cost']:.4f}")
```

### Best Practices

#### Configuration Management
1. Store JSON configs in version control
2. Use JSON Schema validation
3. Document model selection criteria
4. Environment-specific configs (dev/staging/prod)

#### Security
1. Never commit API keys
2. Use environment variables or key management services
3. Rotate keys regularly
4. Review provider data policies

#### Error Handling
1. Implement exponential backoff for rate limits
2. Fallback to alternative providers
3. Log failures for monitoring
4. Handle model deprecation gracefully

#### Monitoring
1. Track token usage per model
2. Monitor costs and set budget alerts
3. Measure latency and error rates
4. Track cache hit rates
5. A/B test model performance

---

## Quick Reference

### Common Patterns

#### Pattern 1: Check Single Capability
```python
if ModelCapability.VISION.value in model["capabilities"]:
    process_image()
```

#### Pattern 2: Check Multiple Capabilities
```python
required = [ModelCapability.VISION, ModelCapability.FUNCTION_CALLING]
has_all = all(
    model["capabilities"].get(cap.value, False)
    for cap in required
)
```

#### Pattern 3: Use Capability Groups
```python
multimodal_caps = ModelCapability.get_multimodal_capabilities()
has_multimodal = any(
    caps.get(c.value, False) for c in multimodal_caps
)
```

#### Pattern 4: Filter Models
```python
vision_models = [
    m for m in models
    if m["capabilities"].get(ModelCapability.VISION.value, False)
]
```

#### Pattern 5: Handle Metadata
```python
if ModelCapability.is_metadata_field(cap):
    value = capabilities[cap.value]  # int, array, etc.
else:
    value = capabilities.get(cap.value, False)  # boolean
```

### Provider Quick Reference

| Provider | Chat | Vision | Audio | Thinking | Caching | Batch |
|----------|------|--------|-------|----------|---------|-------|
| Anthropic | ✅ | ✅ | ❌ | ✅ (3.7) | ✅ | ✅ |
| OpenAI | ✅ | ✅ | ✅ | ✅ (O1) | ✅ | ✅ |
| Google | ✅ | ✅ | ✅ | ✅ (2.0-T) | ✅ | ✅ |
| Groq | ✅ | 3.2 | ❌ | ❌ | ❌ | ❌ |
| HuggingFace | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

### Cost Quick Reference

**Per 1M Tokens (Input/Output):**
- Claude 3.5 Sonnet: $3/$15
- Claude 3.5 Haiku: $1/$5
- GPT-4o: $2.50/$10 (per 1K × 1000)
- GPT-4o mini: $0.15/$0.60 (per 1K × 1000)
- Gemini 1.5 Pro: $1.25-$2.50/$5
- Llama 3.1 70B (Groq): Free

**With Caching (90% discount):**
- Claude 3.5 Sonnet read: $0.30/$15
- GPT-4o cached: $1.25/$10

### Best Practices DO/DON'T

#### ✅ DO
- Use enum values for type safety
- Handle missing capabilities with `.get()`
- Check metadata fields appropriately
- Use helper methods for capability groups
- Implement exponential backoff
- Monitor costs and usage
- Use caching for repeated context

#### ❌ DON'T
- Hardcode capability strings
- Assume capabilities exist
- Mix metadata and boolean handling
- Forget to validate inputs
- Ignore rate limits
- Skip error handling
- Reproduce copyrighted content

---

## Appendices

### Appendix A: Complete Capability List

**Total: 64 capabilities organized into 17 categories**

See [ModelCapability Enum System](#modelcapability-enum-system) section for the complete hierarchical list.

### Appendix B: Field Reference Table

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider` | string | Yes | Provider identifier |
| `api_version` | string | Yes | API version |
| `base_url` | string | Yes* | API endpoint (*nullable for mock) |
| `models` | array | Yes | Model configurations |
| `name` | string | Yes | Model identifier |
| `version` | string | Yes | Model version |
| `capabilities` | object | Yes | Feature flags |
| `cost` | object | Yes | Pricing information |
| `context_window` | number | Yes | Max input tokens |
| `max_output` | number | Yes | Max output tokens |

### Appendix C: Provider Authentication

| Provider | Method | Environment Variable |
|----------|--------|---------------------|
| Anthropic | x-api-key header | ANTHROPIC_API_KEY |
| OpenAI | Authorization Bearer | OPENAI_API_KEY |
| Google | API Key / OAuth2 | GOOGLE_API_KEY |
| Groq | Authorization Bearer | GROQ_API_KEY |
| HuggingFace | Authorization Bearer | HF_TOKEN |
| Mistral | Authorization Bearer | MISTRAL_API_KEY |
| Cohere | Authorization Bearer | COHERE_API_KEY |
| Ollama | None (local) | - |

### Appendix D: Glossary

- **Context Window**: Maximum number of input tokens a model can process
- **Token**: Basic unit of text (~4 characters for English)
- **Streaming**: Real-time token-by-token output delivery
- **Function Calling**: Model's ability to call external APIs/functions
- **Vision**: Image understanding capability
- **Prompt Caching**: Caching repeated context for cost/latency reduction
- **Extended Thinking**: Internal reasoning process shown before final response
- **Batch API**: Asynchronous bulk processing with cost discount
- **Quantization**: Reduced precision model for efficiency
- **Fine-tuning**: Customizing model on specific data
- **Embedding**: Vector representation of text for semantic operations
- **Grounding**: Integration with real-time data sources
- **Multimodal**: Supporting multiple input types (text, image, audio, video)
- **LPU**: Language Processing Unit (Groq's specialized hardware)
- **RAG**: Retrieval-Augmented Generation

### Appendix E: Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-06 | Initial release |

### Appendix F: References

- **Anthropic API**: https://docs.anthropic.com
- **OpenAI API**: https://platform.openai.com/docs
- **Google AI**: https://ai.google.dev
- **Groq**: https://console.groq.com/docs
- **HuggingFace**: https://huggingface.co/docs

---

## Document End

**For support or questions, contact:**  
Ashutosh Sinha  
Email: ajsinha@gmail.com

**Copyright © 2025-2030, All Rights Reserved**  
**Patent Pending:** Certain architectural patterns may be subject to patent applications.