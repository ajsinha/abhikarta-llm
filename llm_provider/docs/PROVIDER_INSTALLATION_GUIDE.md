# Complete Provider Installation Guide

## All Providers Implemented ✅

This system now includes **FULL implementations for 13 providers**:

1. ✅ **Anthropic** (Claude 3.x family)
2. ✅ **OpenAI** (GPT-4, GPT-3.5, DALL-E, Embeddings)
3. ✅ **Google** (Gemini 1.5, 2.0)
4. ✅ **Cohere** (Command, Command-R, Embeddings)
5. ✅ **Mistral** (Mixtral, Mistral, Embeddings)
6. ✅ **Groq** (Ultra-fast Llama, Mixtral, Gemma)
7. ✅ **Meta/Replicate** (Llama 2, 3, Code Llama)
8. ✅ **HuggingFace** (Inference API)
9. ✅ **Together AI** (Open-source models)
10. ✅ **Ollama** (Local models)
11. ✅ **AWS Bedrock** (Claude, Llama on AWS)
12. ✅ **Replicate** (Meta models)
13. ✅ **Mock** (Testing and development)

---

## Installation by Provider

### 1. Anthropic (Claude)

```bash
pip install anthropic
```

**Environment Variable:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Usage:**
```python
facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
```

**Features:**
- ✓ Chat completion
- ✓ Streaming
- ✓ Vision
- ✓ Tool use / function calling
- ✓ Prompt caching
- ✓ Extended thinking (3.7 Sonnet)

---

### 2. OpenAI (GPT)

```bash
pip install openai
```

**Environment Variable:**
```bash
export OPENAI_API_KEY="sk-..."
```

**Usage:**
```python
facade = factory.create_facade("openai", "gpt-4-turbo-preview")
```

**Features:**
- ✓ Chat completion
- ✓ Streaming
- ✓ Vision (GPT-4 Vision)
- ✓ Function calling
- ✓ Embeddings (text-embedding models)
- ✓ Image generation (DALL-E)
- ✓ Content moderation
- ✓ JSON mode

---

### 3. Google (Gemini)

```bash
pip install google-generativeai
```

**Environment Variable:**
```bash
export GOOGLE_API_KEY="..."
```

**Usage:**
```python
facade = factory.create_facade("google", "gemini-2.0-flash-exp")
```

**Features:**
- ✓ Chat completion
- ✓ Streaming
- ✓ Vision
- ✓ Function calling
- ✓ Code execution
- ✓ JSON mode
- ✓ Thinking mode (2.0)
- ✓ Multimodal (text, images, audio, video)

---

### 4. Cohere

```bash
pip install cohere
```

**Environment Variable:**
```bash
export COHERE_API_KEY="..."
```

**Usage:**
```python
facade = factory.create_facade("cohere", "command-r-plus")
```

**Features:**
- ✓ Chat completion
- ✓ Streaming
- ✓ Tool use
- ✓ Embeddings
- ✓ RAG support

---

### 5. Mistral

```bash
pip install mistralai
```

**Environment Variable:**
```bash
export MISTRAL_API_KEY="..."
```

**Usage:**
```python
facade = factory.create_facade("mistral", "mistral-large-latest")
```

**Features:**
- ✓ Chat completion
- ✓ Streaming
- ✓ Function calling
- ✓ Embeddings
- ✓ JSON mode

---

### 6. Groq

```bash
pip install groq
```

**Environment Variable:**
```bash
export GROQ_API_KEY="gsk_..."
```

**Usage:**
```python
facade = factory.create_facade("groq", "llama-3.1-70b-versatile")
```

**Features:**
- ✓ Ultra-fast inference
- ✓ Chat completion
- ✓ Streaming
- ✓ Function calling
- ✓ Vision (some models)

---

### 7. Meta/Replicate

```bash
pip install replicate
```

**Environment Variable:**
```bash
export REPLICATE_API_TOKEN="r8_..."
```

**Usage:**
```python
facade = factory.create_facade("meta", "llama-3.1-70b-instruct")
```

**Features:**
- ✓ Chat completion
- ✓ Streaming
- ✓ Llama 2, 3, Code Llama
- ✓ Vision (Llama 3.2)

---

### 8. HuggingFace

```bash
pip install huggingface_hub
```

**Environment Variable:**
```bash
export HUGGINGFACE_API_KEY="hf_..."
```

**Usage:**
```python
facade = factory.create_facade("huggingface", "mistralai/Mistral-7B-Instruct-v0.2")
```

**Features:**
- ✓ Chat completion
- ✓ Streaming
- ✓ Access to 100,000+ models

---

### 9. Together AI

```bash
pip install together
```

**Environment Variable:**
```bash
export TOGETHER_API_KEY="..."
```

**Usage:**
```python
facade = factory.create_facade("together", "meta-llama/Llama-3-70b-chat-hf")
```

**Features:**
- ✓ Chat completion
- ✓ Streaming
- ✓ Open-source models
- ✓ Fast inference

---

### 10. Ollama (Local)

```bash
pip install ollama

# Also install Ollama itself
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.1
```

**Environment Variable (optional):**
```bash
export OLLAMA_HOST="http://localhost:11434"
```

**Usage:**
```python
facade = factory.create_facade("ollama", "llama3.1")
```

**Features:**
- ✓ Run models locally
- ✓ Chat completion
- ✓ Streaming
- ✓ Vision (some models)
- ✓ Embeddings
- ✓ No API key needed

---

### 11. AWS Bedrock

```bash
pip install boto3
```

**AWS Credentials:**
```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"
```

**Usage:**
```python
facade = factory.create_facade(
    "awsbedrock",
    "anthropic.claude-3-sonnet-20240229-v1:0",
    region="us-east-1"
)
```

**Features:**
- ✓ Claude, Llama, and other models on AWS
- ✓ Chat completion
- ✓ Streaming
- ✓ Enterprise security
- ✓ VPC integration

---

### 12. Mock (Testing)

```bash
# No installation needed - pure Python
```

**Usage:**
```python
facade = factory.create_facade("mock", "mock-advanced")
```

**Features:**
- ✓ No API key needed
- ✓ Instant responses
- ✓ Configurable latency
- ✓ All capabilities simulated
- ✓ Perfect for testing

---

## Quick Provider Comparison

| Provider | Cost | Speed | Quality | Vision | Tools | Local |
|----------|------|-------|---------|--------|-------|-------|
| Anthropic | 💰💰💰 | ⚡⚡ | ⭐⭐⭐⭐⭐ | ✅ | ✅ | ❌ |
| OpenAI | 💰💰💰 | ⚡⚡ | ⭐⭐⭐⭐⭐ | ✅ | ✅ | ❌ |
| Google | 💰💰 | ⚡⚡⚡ | ⭐⭐⭐⭐ | ✅ | ✅ | ❌ |
| Cohere | 💰💰 | ⚡⚡ | ⭐⭐⭐⭐ | ❌ | ✅ | ❌ |
| Mistral | 💰💰 | ⚡⚡⚡ | ⭐⭐⭐⭐ | ❌ | ✅ | ❌ |
| Groq | 💰 | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | ⚠️ | ✅ | ❌ |
| Meta | 💰 | ⚡⚡ | ⭐⭐⭐ | ⚠️ | ❌ | ❌ |
| HuggingFace | 💰 | ⚡ | ⭐⭐⭐ | ⚠️ | ❌ | ❌ |
| Together | 💰 | ⚡⚡ | ⭐⭐⭐ | ❌ | ❌ | ❌ |
| Ollama | Free | ⚡⚡ | ⭐⭐⭐ | ⚠️ | ❌ | ✅ |
| AWS Bedrock | 💰💰💰 | ⚡⚡ | ⭐⭐⭐⭐⭐ | ✅ | ✅ | ❌ |
| Mock | Free | ⚡⚡⚡⚡⚡ | N/A | ✅ | ✅ | ✅ |

---

## Complete Installation Script

```bash
# Install all providers
pip install anthropic openai google-generativeai cohere mistralai groq replicate \
            huggingface_hub together ollama boto3

# For local development
pip install pillow tiktoken  # Image processing and tokenization

# Set up environment variables
cat >> ~/.bashrc << 'ENV'
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."
export COHERE_API_KEY="..."
export MISTRAL_API_KEY="..."
export GROQ_API_KEY="gsk_..."
export REPLICATE_API_TOKEN="r8_..."
export HUGGINGFACE_API_KEY="hf_..."
export TOGETHER_API_KEY="..."
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"
ENV

source ~/.bashrc
```

---

## Verification Script

Test all providers:

```python
import register_facades
from facade_factory import FacadeFactory

def test_all_providers():
    """Test all provider facades."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    
    providers = factory.list_providers()
    print(f"Found {len(providers)} providers\n")
    
    test_message = [{"role": "user", "content": "Say 'Hello World'"}]
    
    for provider_name in providers.keys():
        try:
            models = factory.list_models(provider_name)
            if provider_name in models and models[provider_name]:
                model_name = models[provider_name][0]
                print(f"Testing {provider_name}/{model_name}...")
                
                facade = factory.create_facade(provider_name, model_name)
                response = facade.chat_completion(test_message, max_tokens=50)
                
                print(f"  ✅ Success: {response['content'][:50]}...")
                print(f"  Tokens: {response['usage'].total_tokens}\n")
        except Exception as e:
            print(f"  ❌ Failed: {str(e)}\n")

if __name__ == "__main__":
    test_all_providers()
```

---

## Provider-Specific Notes

### Anthropic
- Best for: Complex reasoning, coding, analysis
- Models: Claude 3.7, 3.5, 3.0 (Opus, Sonnet, Haiku)
- Context: Up to 200K tokens
- Special: Extended thinking, prompt caching

### OpenAI
- Best for: General purpose, embeddings, images
- Models: GPT-4, GPT-3.5, DALL-E, text-embedding
- Context: Up to 128K tokens
- Special: JSON mode, function calling, DALL-E

### Google
- Best for: Multimodal, code execution, thinking
- Models: Gemini 2.0, 1.5 Pro/Flash
- Context: Up to 2M tokens
- Special: Video/audio input, built-in code execution

### Groq
- Best for: Ultra-fast inference
- Models: Llama, Mixtral, Gemma
- Speed: 500+ tokens/second
- Special: Lowest latency

### Ollama
- Best for: Local deployment, privacy
- Models: Any Ollama model
- Cost: Free (local compute)
- Special: No internet required

---

## Troubleshooting

### Import Errors
```python
# If you get import errors, install the specific SDK:
pip install <sdk_name>

# Example:
pip install anthropic  # For Anthropic
pip install openai      # For OpenAI
```

### Authentication Errors
```python
# Check environment variables:
import os
print("Anthropic:", "✓" if os.getenv("ANTHROPIC_API_KEY") else "✗")
print("OpenAI:", "✓" if os.getenv("OPENAI_API_KEY") else "✗")
# ... etc
```

### Model Not Found
```python
# List available models:
factory = FacadeFactory(config_source="json", config_path="./config")
models = factory.list_models("anthropic")
print(models["anthropic"])
```

---

## Next Steps

1. **Install Required SDKs** - Only install SDKs for providers you'll use
2. **Set API Keys** - Configure environment variables
3. **Test with Mock** - Verify system works with mock provider
4. **Add One Provider** - Start with your primary provider
5. **Expand Gradually** - Add more providers as needed

---

For complete documentation, see `Abhikarta_Model_Facade_README_and_Quickguide.md`

**Copyright © 2025-2030 | Ashutosh Sinha | ajsinha@gmail.com**
