# Abhikarta SDK - Provider Configuration

Guide for configuring LLM providers in both SDK packages.

## Supported Providers

| Provider | SDK Client | SDK Embedded | Notes |
|----------|------------|--------------|-------|
| Ollama | ✅ | ✅ | Local/self-hosted |
| OpenAI | ✅ | ✅ | Requires API key |
| Anthropic | ✅ | ✅ | Requires API key |
| Google | ✅ | ❌ | Server only |
| Azure OpenAI | ✅ | ❌ | Server only |
| AWS Bedrock | ✅ | ❌ | Server only |
| Mistral | ✅ | ❌ | Server only |
| Hugging Face | ✅ | ❌ | Server only |

## SDK Embedded - Provider Configuration

### Ollama (Default - Local)

Ollama is the default provider for local, privacy-focused AI:

```python
from abhikarta_embedded import Abhikarta, AbhikartaConfig

# Default configuration (localhost:11434)
app = Abhikarta()

# Custom Ollama URL
config = AbhikartaConfig(
    default_provider="ollama",
    ollama_base_url="http://localhost:11434",
    default_model="llama3.2:3b"
)
app = Abhikarta(config)

# Or configure after initialization
app.configure_provider("ollama", base_url="http://remote-ollama:11434")
```

#### Popular Ollama Models

| Model | Size | Description |
|-------|------|-------------|
| `llama3.2:3b` | 3B | Fast, good for general tasks |
| `llama3.2:1b` | 1B | Lightweight, quick responses |
| `mistral:7b` | 7B | Balanced performance |
| `mixtral:8x7b` | 47B | High quality, slower |
| `codellama:7b` | 7B | Code-focused |
| `phi3:mini` | 3.8B | Microsoft's efficient model |

### OpenAI

```python
from abhikarta_embedded import AbhikartaConfig, Abhikarta

# Via configuration
config = AbhikartaConfig(
    default_provider="openai",
    openai_api_key="sk-...",
    default_model="gpt-4o-mini"
)
app = Abhikarta(config)

# Or via environment variable
import os
os.environ["OPENAI_API_KEY"] = "sk-..."

app = Abhikarta()
app.configure_provider("openai")
```

#### OpenAI Models

| Model | Description |
|-------|-------------|
| `gpt-4o` | Most capable |
| `gpt-4o-mini` | Fast, cost-effective |
| `gpt-4-turbo` | High capability, vision |
| `gpt-3.5-turbo` | Fast, affordable |

### Anthropic (Claude)

```python
config = AbhikartaConfig(
    default_provider="anthropic",
    anthropic_api_key="sk-ant-...",
    default_model="claude-sonnet-4-20250514"
)
app = Abhikarta(config)

# Or via environment
import os
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."
```

#### Anthropic Models

| Model | Description |
|-------|-------------|
| `claude-sonnet-4-20250514` | Balanced capability |
| `claude-opus-4-20250514` | Most capable |
| `claude-haiku-3-5-20250514` | Fast, efficient |

### Direct Provider Usage

For more control, use providers directly:

```python
from abhikarta_embedded.providers import (
    Provider,
    OllamaProvider,
    OpenAIProvider,
    AnthropicProvider,
    ProviderConfig
)

# Factory method
provider = Provider.create("ollama", base_url="http://localhost:11434")

# Direct instantiation
config = ProviderConfig(
    name="ollama",
    base_url="http://localhost:11434",
    default_model="llama3.2:3b",
    timeout=300
)
provider = OllamaProvider(config)

# Use provider
response = provider.chat([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
])
print(response)

# Completion API
response = provider.complete("Tell me about AI")
```

### Provider Config Options

```python
@dataclass
class ProviderConfig:
    name: str                    # Provider name
    base_url: Optional[str]      # API base URL
    api_key: Optional[str]       # API key
    default_model: str = ""      # Default model
    timeout: int = 300           # Request timeout (seconds)
```

## SDK Client - Provider Configuration

The SDK Client uses providers configured on the server. To specify which model to use:

```python
from abhikarta_client import AbhikartaClient

client = AbhikartaClient("http://localhost:5000")

# Create agent with specific provider/model
agent = client.agents.create(
    name="My Agent",
    agent_type="react",
    provider="ollama",         # Provider configured on server
    model="llama3.2:3b"        # Model available in provider
)
```

### Server Provider Configuration

On the server side, configure providers in the Admin UI:

1. Navigate to **Admin → LLM Providers**
2. Add provider with required configuration
3. Add models for the provider
4. Configure role-based access if needed

## Best Practices

### 1. Use Environment Variables for API Keys

```python
import os

# Don't hardcode API keys
config = AbhikartaConfig(
    openai_api_key=os.environ.get("OPENAI_API_KEY"),
    anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY")
)
```

### 2. Configure Provider Once

```python
# Good: Configure once at startup
app = Abhikarta()
app.configure_provider("ollama", base_url="http://localhost:11434")

# Then reuse
agent1 = app.agent("Agent1").type("react").build()
agent2 = app.agent("Agent2").type("goal").build()
```

### 3. Handle Provider Errors

```python
from abhikarta_embedded import Agent
from abhikarta_embedded.providers import Provider

try:
    provider = Provider.create("ollama")
    agent = Agent.create("react", model="llama3.2:3b")
    agent.provider = provider
    result = agent.run("Hello")
except ConnectionError:
    print("Could not connect to Ollama. Is it running?")
except TimeoutError:
    print("Request timed out. Try increasing timeout.")
```

### 4. Use Model Shortcuts

```python
# Provider/model shortcut format
agent = Agent.create("react", model="ollama/llama3.2:3b")
agent = Agent.create("react", model="openai/gpt-4o-mini")
agent = Agent.create("react", model="anthropic/claude-sonnet-4-20250514")
```

## Troubleshooting

### Ollama Connection Issues

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Pull model if not available
ollama pull llama3.2:3b
```

### API Key Issues

```python
# Verify API key is set
import os
print(os.environ.get("OPENAI_API_KEY", "NOT SET"))
```

### Timeout Issues

```python
# Increase timeout for large models
config = AbhikartaConfig(timeout=600)  # 10 minutes
```
