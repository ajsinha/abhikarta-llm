# Design Patterns Implementation

**LLM Abstraction System**  
**© 2025-2030 All Rights Reserved | Ashutosh Sinha | ajsinha@gmail.com**

## Overview

This document details how the Factory, Facade, and Delegation patterns are implemented in the LLM Abstraction System, for both Models and Clients.

## 1. Factory Pattern

### Purpose
Create objects without specifying their exact classes. The factory decides which class to instantiate based on configuration.

### Implementation

#### A. LLMModelFactory (`models/model_factory.py`)

**Responsibilities:**
- Register model implementations for each provider
- Create model instances based on provider name
- Maintain a registry of available models

**Key Methods:**
```python
class LLMModelFactory:
    _model_registry: Dict[str, Type[BaseLLMModel]] = {}
    
    def register_model(provider: str, model_class: Type[BaseLLMModel])
        """Register a new model implementation"""
    
    def create_model(config: ModelConfig) -> BaseLLMModel
        """Create model instance based on config"""
    
    def get_available_providers() -> list
        """List all registered providers"""
```

**Usage Example:**
```python
factory = LLMModelFactory()
config = ModelConfig(name="claude", provider="bedrock", model_id="claude-3-sonnet")
model = factory.create_model(config)  # Returns BedrockModel instance
```

**Providers Registered:**
- BedrockModel
- TogetherModel
- HuggingfaceModel
- OpenaiModel
- AnthropicModel
- CohereModel
- GoogleModel
- MockModel

#### B. LLMClientFactory (`clients/client_factory.py`)

**Responsibilities:**
- Register client implementations for each provider
- Create client instances based on model's provider
- Maintain a registry of available clients

**Key Methods:**
```python
class LLMClientFactory:
    _client_registry: Dict[str, Type[BaseLLMClient]] = {}
    
    def register_client(provider: str, client_class: Type[BaseLLMClient])
        """Register a new client implementation"""
    
    def create_client(model: BaseLLMModel, config: Dict) -> BaseLLMClient
        """Create client instance for given model"""
    
    def get_available_providers() -> list
        """List all registered providers"""
```

**Usage Example:**
```python
factory = LLMClientFactory()
client = factory.create_client(model, config)  # Returns appropriate client
```

**Providers Registered:**
- BedrockClient
- TogetherClient
- HuggingfaceClient
- OpenaiClient
- AnthropicClient
- CohereClient
- GoogleClient
- MockClient

### Benefits of Factory Pattern
✅ Loose coupling between client code and concrete classes  
✅ Easy to add new providers without modifying existing code  
✅ Centralized object creation logic  
✅ Runtime provider selection  

## 2. Facade Pattern

### Purpose
Provide a simplified, unified interface to a complex subsystem. Hide implementation details from clients.

### Implementation

#### A. LLMModelFacade (`models/model_facade.py`)

**Responsibilities:**
- Simplify model creation and management
- Handle configuration loading
- Provide caching for model instances
- Abstract away factory and configuration complexity

**Key Methods:**
```python
class LLMModelFacade:
    def __init__(config_path: Optional[str])
        """Initialize with configuration"""
    
    def get_default_model() -> BaseLLMModel
        """Get model from config"""
    
    def get_model(provider: str, model_name: str, **kwargs) -> BaseLLMModel
        """Get or create model instance"""
    
    def list_available_providers() -> list
        """List all providers"""
```

**Internal Complexity Hidden:**
- Configuration parsing
- Model factory usage
- Instance caching
- Parameter defaulting

**Usage Example:**
```python
# Without Facade (Complex)
config = PropertiesConfigurator()
config.load_properties('config.properties')
factory = LLMModelFactory()
model_config = ModelConfig(...)  # Many parameters
model = factory.create_model(model_config)
model.initialize()

# With Facade (Simple)
facade = LLMModelFacade('config.properties')
model = facade.get_model('bedrock', 'claude-3-sonnet')
```

#### B. LLMClientFacade (`clients/client_facade.py`)

**Responsibilities:**
- Main entry point for the entire system
- Simplify client creation and usage
- Coordinate between model facade and client factory
- Provide high-level methods for generation and chat

**Key Methods:**
```python
class LLMClientFacade:
    def __init__(config_path: Optional[str])
        """Initialize system"""
    
    def get_default_client() -> BaseLLMClient
        """Get client from config"""
    
    def get_client(provider: str, model_name: str) -> BaseLLMClient
        """Get or create client"""
    
    def generate(prompt: str, provider: str, model_name: str, **kwargs) -> str
        """Generate text (simplified interface)"""
    
    def chat(messages: List, provider: str, model_name: str, **kwargs) -> str
        """Chat completion (simplified interface)"""
    
    def list_available_providers() -> List[str]
        """List enabled providers"""
```

**Internal Complexity Hidden:**
- Model creation via ModelFacade
- Client creation via ClientFactory
- Configuration management
- Instance caching
- Provider-specific details

**Usage Example:**
```python
# Without Facade (Very Complex)
config = PropertiesConfigurator()
config.load_properties('config.properties')
model_config = ModelConfig(...)
model_factory = LLMModelFactory()
model = model_factory.create_model(model_config)
model.initialize()
provider_config = {...}  # Extract from properties
client_factory = LLMClientFactory()
client = client_factory.create_client(model, provider_config)
client.initialize()
response = client.generate(prompt, max_tokens=..., temperature=...)

# With Facade (Very Simple)
facade = LLMClientFacade('config.properties')
response = facade.generate("Your prompt here")
```

### Benefits of Facade Pattern
✅ Dramatically simplified API for clients  
✅ Hides complex subsystem interactions  
✅ Reduces dependencies on internal components  
✅ Makes system easier to use and understand  
✅ Provides sensible defaults  

## 3. Delegation Pattern

### Purpose
One object relies on another to perform specific tasks. The delegate handles implementation details.

### Implementation

#### A. Client Delegates to Model

**BaseLLMClient** delegates to **BaseLLMModel** for:
- Getting provider information
- Checking streaming support
- Getting model configuration
- Model-specific metadata

```python
class BaseLLMClient:
    def __init__(self, model: BaseLLMModel, config: Dict):
        self.model = model  # Composition - client HAS-A model
    
    def get_provider(self) -> str:
        return self.model.get_provider()  # DELEGATES to model
    
    def supports_streaming(self) -> bool:
        return self.model.supports_streaming()  # DELEGATES to model
    
    def get_model(self) -> BaseLLMModel:
        return self.model  # Provides access to delegate
```

**Benefits:**
- Client doesn't need to know provider details
- Model encapsulates provider-specific configuration
- Single source of truth for model information
- Clear separation of concerns

#### B. Facade Delegates to Factory

**LLMClientFacade** delegates to:
- **LLMModelFacade**: For model creation and management
- **LLMClientFactory**: For client creation
- **PropertiesConfigurator**: For configuration

```python
class LLMClientFacade:
    def __init__(self, config_path):
        self.config = PropertiesConfigurator()  # DELEGATES config
        self.model_facade = LLMModelFacade(config_path)  # DELEGATES models
        self.client_factory = LLMClientFactory()  # DELEGATES clients
    
    def get_client(self, provider, model_name):
        model = self.model_facade.get_model(provider, model_name)  # DELEGATES
        return self.client_factory.create_client(model, config)  # DELEGATES
```

**Benefits:**
- Each component has single responsibility
- Clear ownership of functionality
- Easy to test individual components
- Maintainable and extensible

#### C. Facade Delegates to Client

**LLMClientFacade** delegates actual LLM operations to the appropriate client:

```python
class LLMClientFacade:
    def generate(self, prompt: str, provider: str, model_name: str, **kwargs):
        client = self.get_client(provider, model_name)  # Get delegate
        return client.generate(prompt, **kwargs)  # DELEGATE to client
    
    def chat(self, messages: List, provider: str, model_name: str, **kwargs):
        client = self.get_client(provider, model_name)  # Get delegate
        return client.chat(messages, **kwargs)  # DELEGATE to client
```

**Benefits:**
- Facade doesn't need to implement LLM logic
- Clients handle provider-specific details
- Easy to add new operations

### Benefits of Delegation Pattern
✅ Promotes code reuse  
✅ Enhances modularity  
✅ Reduces coupling  
✅ Simplifies testing  
✅ Enables composition over inheritance  

## 4. Abstract Base Classes (ABC)

### Purpose
Define interfaces that concrete implementations must follow.

### Implementation

#### A. BaseLLMModel (Abstract)

```python
class BaseLLMModel(ABC):
    @abstractmethod
    def initialize(self) -> None: pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]: pass
    
    @abstractmethod
    def validate_config(self) -> bool: pass
    
    @abstractmethod
    def supports_streaming(self) -> bool: pass
    
    @abstractmethod
    def get_max_context_length(self) -> int: pass
```

**Concrete Implementations:**
- BedrockModel
- TogetherModel
- HuggingfaceModel
- OpenaiModel
- AnthropicModel
- CohereModel
- GoogleModel
- MockModel

#### B. BaseLLMClient (Abstract)

```python
class BaseLLMClient(ABC):
    @abstractmethod
    def initialize(self) -> None: pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str: pass
    
    @abstractmethod
    def generate_with_metadata(self, prompt: str, **kwargs) -> Dict: pass
    
    @abstractmethod
    def chat(self, messages: List, **kwargs) -> str: pass
    
    @abstractmethod
    def stream_generate(self, prompt: str, **kwargs) -> AsyncIterator: pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int: pass
    
    @abstractmethod
    def get_client_info(self) -> Dict[str, Any]: pass
```

**Concrete Implementations:**
- BedrockClient
- TogetherClient
- HuggingfaceClient
- OpenaiClient
- AnthropicClient
- CohereClient
- GoogleClient
- MockClient

### Benefits of ABC Pattern
✅ Enforces consistent interface across implementations  
✅ Enables polymorphism  
✅ Catches missing implementations at instantiation  
✅ Self-documenting code  
✅ Type safety  

## Pattern Interaction Diagram

```
Client Code
    ↓
LLMClientFacade (Facade)
    ↓
    ├→ LLMModelFacade (Facade)
    │       ↓
    │   LLMModelFactory (Factory)
    │       ↓
    │   BaseLLMModel (Abstract)
    │       ↓
    │   [BedrockModel, TogetherModel, etc.] (Concrete)
    │
    └→ LLMClientFactory (Factory)
            ↓
        BaseLLMClient (Abstract)
            ↓
        [BedrockClient, TogetherClient, etc.] (Concrete)
            ↓ (Delegates to)
        BaseLLMModel
```

## Complete Example: Pattern Collaboration

```python
# 1. CLIENT CODE (Simple interface thanks to Facade)
facade = LLMClientFacade('config.properties')
response = facade.generate("What is AI?", provider="bedrock", model_name="claude-3-sonnet")

# BEHIND THE SCENES:

# 2. FACADE receives request and delegates
class LLMClientFacade:
    def generate(self, prompt, provider, model_name):
        # 3. FACADE asks ModelFacade for model (delegation)
        model = self.model_facade.get_model(provider, model_name)
        
        # 4. ModelFacade asks ModelFactory to create (delegation)
        # ModelFactory uses FACTORY PATTERN to instantiate
        # Returns BedrockModel (concrete implementation of BaseLLMModel)
        
        # 5. FACADE asks ClientFactory for client (delegation)
        client = self.client_factory.create_client(model, config)
        
        # 6. ClientFactory uses FACTORY PATTERN to instantiate
        # Returns BedrockClient (concrete implementation of BaseLLMClient)
        
        # 7. Client DELEGATES to Model for configuration
        # client.get_provider() → model.get_provider()
        
        # 8. FACADE delegates actual generation to client
        return client.generate(prompt)

# RESULT: Client code is simple, but benefits from all patterns working together
```

## Summary

### Design Patterns Used

1. **Factory Pattern** (2 implementations)
   - LLMModelFactory
   - LLMClientFactory

2. **Facade Pattern** (2 implementations)
   - LLMModelFacade
   - LLMClientFacade

3. **Delegation Pattern** (Multiple levels)
   - Client → Model (for configuration)
   - Facade → Factory (for creation)
   - Facade → Client (for operations)

4. **Abstract Base Class Pattern** (2 implementations)
   - BaseLLMModel
   - BaseLLMClient

### Benefits Achieved

✅ **Loose Coupling**: Components are independent  
✅ **High Cohesion**: Each class has single responsibility  
✅ **Extensibility**: Easy to add new providers  
✅ **Maintainability**: Clear structure and separation  
✅ **Testability**: Each component can be tested independently  
✅ **Usability**: Simple interface for complex system  
✅ **Flexibility**: Runtime provider switching  
✅ **Configuration-Driven**: No code changes needed  

### Client Benefits

The client using this system benefits from:
- **Simplicity**: Single facade for all operations
- **Transparency**: Unaware of provider complexity
- **Flexibility**: Can override provider at runtime
- **Consistency**: Same interface for all providers
- **Reliability**: Tested, production-ready code

---

**© 2025-2030 All Rights Reserved | Ashutosh Sinha | ajsinha@gmail.com**
