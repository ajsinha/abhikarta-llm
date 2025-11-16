# Abhikarta Model Facades - Comprehensive Examples

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha | ajsinha@gmail.com**

---

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Provider-Specific Examples](#provider-specific-examples)
3. [Advanced Features](#advanced-features)
4. [Production Patterns](#production-patterns)
5. [Multi-Provider Examples](#multi-provider-examples)
6. [Error Handling Examples](#error-handling-examples)
7. [Cost Optimization Examples](#cost-optimization-examples)
8. [Real-World Applications](#real-world-applications)

---

## Basic Examples

### Example 1: Simple Chat Completion

```python
import register_facades
from facade_factory import FacadeFactory

def simple_chat():
    """Most basic usage - single chat completion."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    response = facade.chat_completion(
        messages=[
            {"role": "user", "content": "What is Python?"}
        ],
        max_tokens=500
    )
    
    print(response["content"])
    print(f"\nTokens used: {response['usage'].total_tokens}")
    print(f"Cost: ${facade.estimate_cost(response['usage'].prompt_tokens, response['usage'].completion_tokens):.6f}")

if __name__ == "__main__":
    simple_chat()
```

### Example 2: Multi-Turn Conversation

```python
import register_facades
from facade_factory import FacadeFactory

def conversation():
    """Multi-turn conversation with context."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("openai", "gpt-4-turbo-preview")
    
    messages = []
    
    # First turn
    messages.append({"role": "user", "content": "I'm learning Python. Where should I start?"})
    response = facade.chat_completion(messages)
    messages.append({"role": "assistant", "content": response["content"]})
    print(f"Assistant: {response['content']}\n")
    
    # Second turn
    messages.append({"role": "user", "content": "What about data structures?"})
    response = facade.chat_completion(messages)
    messages.append({"role": "assistant", "content": response["content"]})
    print(f"Assistant: {response['content']}\n")
    
    # Third turn
    messages.append({"role": "user", "content": "Can you show me a list example?"})
    response = facade.chat_completion(messages)
    print(f"Assistant: {response['content']}\n")
    
    # Total tokens used across conversation
    total_tokens = sum(msg.get('usage', {}).get('total_tokens', 0) for msg in [response])
    print(f"Conversation used ~{total_tokens} tokens")

if __name__ == "__main__":
    conversation()
```

### Example 3: Streaming Response

```python
import register_facades
from facade_factory import FacadeFactory

def streaming_chat():
    """Stream response chunks in real-time."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    messages = [
        {"role": "user", "content": "Write a short story about a robot learning to paint."}
    ]
    
    print("Response: ", end="", flush=True)
    
    for chunk in facade.stream_chat_completion(messages, max_tokens=500):
        print(chunk, end="", flush=True)
    
    print("\n")

if __name__ == "__main__":
    streaming_chat()
```

### Example 4: Async Chat Completion

```python
import asyncio
import register_facades
from facade_factory import FacadeFactory

async def async_chat():
    """Async chat completion for concurrent operations."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("openai", "gpt-4-turbo-preview")
    
    messages = [
        {"role": "user", "content": "Explain async programming in Python"}
    ]
    
    response = await facade.achat_completion(messages, max_tokens=300)
    print(response["content"])

async def multiple_async_requests():
    """Run multiple requests concurrently."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    questions = [
        "What is machine learning?",
        "What is deep learning?",
        "What is neural network?"
    ]
    
    tasks = [
        facade.achat_completion(
            [{"role": "user", "content": q}],
            max_tokens=100
        )
        for q in questions
    ]
    
    responses = await asyncio.gather(*tasks)
    
    for i, response in enumerate(responses):
        print(f"\nQ{i+1}: {questions[i]}")
        print(f"A{i+1}: {response['content'][:100]}...")

if __name__ == "__main__":
    # Run single async request
    asyncio.run(async_chat())
    
    # Run multiple concurrent requests
    asyncio.run(multiple_async_requests())
```

### Example 5: System Prompts

```python
import register_facades
from facade_factory import FacadeFactory

def with_system_prompt():
    """Using system prompts to set behavior."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    # Anthropic uses system parameter
    response = facade.chat_completion(
        messages=[
            {"role": "user", "content": "Explain recursion"}
        ],
        system="You are a computer science professor who explains concepts using simple analogies.",
        max_tokens=300
    )
    
    print(response["content"])

if __name__ == "__main__":
    with_system_prompt()
```

---

## Provider-Specific Examples

### Example 6: Anthropic - Vision with Images

```python
import register_facades
from facade_factory import FacadeFactory
from PIL import Image

def anthropic_vision():
    """Use Claude's vision capabilities."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    # Load image
    image = Image.open("chart.png")
    
    response = facade.chat_completion_with_vision(
        messages=[
            {"role": "user", "content": "What trends do you see in this chart?"}
        ],
        images=[image],
        max_tokens=500
    )
    
    print(response["content"])

if __name__ == "__main__":
    anthropic_vision()
```

### Example 7: OpenAI - Function Calling

```python
import register_facades
from facade_factory import FacadeFactory
import json

def openai_function_calling():
    """Use OpenAI's function calling."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("openai", "gpt-4-turbo-preview")
    
    # Define functions
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The temperature unit"
                        }
                    },
                    "required": ["location"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_time",
                "description": "Get the current time in a timezone",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": "IANA timezone name, e.g. America/New_York"
                        }
                    },
                    "required": ["timezone"]
                }
            }
        }
    ]
    
    messages = [
        {"role": "user", "content": "What's the weather like in San Francisco and what time is it there?"}
    ]
    
    response = facade.chat_completion(messages, tools=tools)
    
    # Check for tool calls
    if response["tool_calls"]:
        print("Tool calls requested:")
        for tool_call in response["tool_calls"]:
            func_name = tool_call["function"]["name"]
            func_args = json.loads(tool_call["function"]["arguments"])
            print(f"  - {func_name}({func_args})")
            
            # In real app, execute the functions and send results back
            # For demo, we'll simulate responses
            if func_name == "get_weather":
                result = {"temperature": 65, "condition": "sunny"}
            elif func_name == "get_time":
                result = {"time": "2:30 PM", "date": "2025-11-16"}
            
            print(f"    Result: {result}")
    else:
        print(response["content"])

if __name__ == "__main__":
    openai_function_calling()
```

### Example 8: OpenAI - Embeddings

```python
import register_facades
from facade_factory import FacadeFactory
import numpy as np

def openai_embeddings():
    """Generate and compare embeddings."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("openai", "text-embedding-3-large")
    
    texts = [
        "The cat sat on the mat",
        "A feline rested on the rug",
        "The weather is sunny today"
    ]
    
    # Generate embeddings
    embeddings = facade.generate_embeddings(texts)
    
    print(f"Generated {len(embeddings)} embeddings")
    print(f"Embedding dimensions: {len(embeddings[0])}")
    
    # Calculate similarity between first two (similar meaning)
    emb1 = np.array(embeddings[0])
    emb2 = np.array(embeddings[1])
    emb3 = np.array(embeddings[2])
    
    similarity_1_2 = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    similarity_1_3 = np.dot(emb1, emb3) / (np.linalg.norm(emb1) * np.linalg.norm(emb3))
    
    print(f"\nSimilarity between similar sentences: {similarity_1_2:.4f}")
    print(f"Similarity between different sentences: {similarity_1_3:.4f}")

if __name__ == "__main__":
    openai_embeddings()
```

### Example 9: OpenAI - DALL-E Image Generation

```python
import register_facades
from facade_factory import FacadeFactory

def openai_image_generation():
    """Generate images with DALL-E."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("openai", "dall-e-3")
    
    prompt = "A serene landscape with mountains at sunset, oil painting style"
    
    image_url = facade.generate_image(
        prompt=prompt,
        size="1024x1024",
        quality="hd"
    )
    
    print(f"Image generated: {image_url}")
    print(f"Prompt: {prompt}")
    
    # In real app, you would download and save the image
    # import requests
    # from PIL import Image
    # import io
    # 
    # response = requests.get(image_url)
    # image = Image.open(io.BytesIO(response.content))
    # image.save("generated_image.png")

if __name__ == "__main__":
    openai_image_generation()
```

### Example 10: Google Gemini - Multimodal Input

```python
import register_facades
from facade_factory import FacadeFactory
from PIL import Image

def google_multimodal():
    """Use Gemini's multimodal capabilities."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("google", "gemini-2.0-flash-exp")
    
    # Load multiple images
    images = [
        Image.open("slide1.png"),
        Image.open("slide2.png"),
        Image.open("slide3.png")
    ]
    
    response = facade.chat_completion_with_vision(
        messages=[
            {"role": "user", "content": "Summarize the key points from these presentation slides"}
        ],
        images=images,
        max_tokens=500
    )
    
    print(response["content"])

if __name__ == "__main__":
    google_multimodal()
```

### Example 11: Groq - Ultra-Fast Inference

```python
import register_facades
from facade_factory import FacadeFactory
import time

def groq_speed_test():
    """Demonstrate Groq's speed advantage."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("groq", "llama-3.1-70b-versatile")
    
    messages = [
        {"role": "user", "content": "Write a haiku about coding"}
    ]
    
    start = time.time()
    response = facade.chat_completion(messages, max_tokens=100)
    end = time.time()
    
    print(response["content"])
    print(f"\nLatency: {(end - start) * 1000:.2f}ms")
    print(f"Tokens: {response['usage'].completion_tokens}")
    print(f"Speed: {response['usage'].completion_tokens / (end - start):.0f} tokens/second")

if __name__ == "__main__":
    groq_speed_test()
```

### Example 12: Ollama - Local Model

```python
import register_facades
from facade_factory import FacadeFactory

def ollama_local():
    """Use local models with Ollama."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    
    # Assumes you have llama3.1 pulled: ollama pull llama3.1
    facade = factory.create_facade("ollama", "llama3.1")
    
    response = facade.chat_completion(
        messages=[
            {"role": "user", "content": "Explain the benefits of running LLMs locally"}
        ],
        max_tokens=300
    )
    
    print(response["content"])
    print("\n✓ No API key required")
    print("✓ Complete privacy")
    print("✓ No usage costs")

if __name__ == "__main__":
    ollama_local()
```

### Example 13: Mock Provider - Testing

```python
import register_facades
from facade_factory import FacadeFactory

def test_with_mock():
    """Test your application with mock provider."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("mock", "mock-advanced")
    
    # Test basic chat
    response = facade.chat_completion(
        messages=[{"role": "user", "content": "Test message"}],
        max_tokens=50
    )
    print(f"Response: {response['content']}")
    
    # Test streaming
    print("\nStreaming test:")
    for chunk in facade.stream_chat_completion(
        messages=[{"role": "user", "content": "Stream test"}]
    ):
        print(chunk, end="", flush=True)
    print()
    
    # Test vision
    print("\nVision test:")
    response = facade.chat_completion_with_vision(
        messages=[{"role": "user", "content": "Describe this"}],
        images=["fake_image.jpg"]
    )
    print(f"Response: {response['content']}")
    
    # Get usage stats
    stats = facade.get_usage_stats()
    print(f"\nMock stats: {stats}")

if __name__ == "__main__":
    test_with_mock()
```

---

## Advanced Features

### Example 14: Temperature and Sampling Control

```python
import register_facades
from facade_factory import FacadeFactory

def sampling_control():
    """Control response creativity with temperature."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    prompt = [{"role": "user", "content": "Write a creative opening line for a sci-fi novel"}]
    
    print("Low temperature (0.2) - More deterministic:")
    response = facade.chat_completion(prompt, temperature=0.2, max_tokens=100)
    print(response["content"])
    
    print("\nMedium temperature (0.7) - Balanced:")
    response = facade.chat_completion(prompt, temperature=0.7, max_tokens=100)
    print(response["content"])
    
    print("\nHigh temperature (1.5) - More creative:")
    response = facade.chat_completion(prompt, temperature=1.5, max_tokens=100)
    print(response["content"])

if __name__ == "__main__":
    sampling_control()
```

### Example 15: Dynamic Model Selection

```python
import register_facades
from facade_factory import FacadeFactory

def dynamic_model_selection():
    """Select model based on task complexity."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    
    def process_request(complexity: str, message: str):
        """Route to appropriate model based on complexity."""
        if complexity == "simple":
            # Use fast, cheap model
            facade = factory.create_facade("anthropic", "claude-3-haiku-20240307")
        elif complexity == "medium":
            # Use balanced model
            facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
        else:  # complex
            # Use most capable model
            facade = factory.create_facade("anthropic", "claude-3-opus-20240229")
        
        response = facade.chat_completion(
            messages=[{"role": "user", "content": message}],
            max_tokens=200
        )
        
        return response["content"], facade.model_name
    
    # Simple task
    content, model = process_request("simple", "What's 2+2?")
    print(f"Simple task used: {model}")
    print(f"Response: {content}\n")
    
    # Medium task
    content, model = process_request("medium", "Explain quantum entanglement")
    print(f"Medium task used: {model}")
    print(f"Response: {content[:100]}...\n")
    
    # Complex task
    content, model = process_request("complex", "Design a distributed system architecture for a global e-commerce platform")
    print(f"Complex task used: {model}")
    print(f"Response: {content[:100]}...\n")

if __name__ == "__main__":
    dynamic_model_selection()
```

### Example 16: Batch Processing

```python
import register_facades
from facade_factory import FacadeFactory
import asyncio

async def batch_processing():
    """Process multiple requests efficiently."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("openai", "gpt-4-turbo-preview")
    
    # Batch of customer reviews to analyze
    reviews = [
        "Great product! Love it!",
        "Terrible quality, broke after one day",
        "Decent for the price",
        "Outstanding service and fast shipping",
        "Not what I expected, disappointed"
    ]
    
    async def analyze_review(review: str) -> dict:
        """Analyze sentiment of a single review."""
        response = await facade.achat_completion(
            messages=[
                {"role": "system", "content": "Analyze the sentiment as positive, negative, or neutral. Respond with JSON."},
                {"role": "user", "content": review}
            ],
            max_tokens=50
        )
        return {
            "review": review,
            "sentiment": response["content"]
        }
    
    # Process all reviews concurrently
    tasks = [analyze_review(review) for review in reviews]
    results = await asyncio.gather(*tasks)
    
    print("Batch Processing Results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['review']}")
        print(f"   Sentiment: {result['sentiment']}")

if __name__ == "__main__":
    asyncio.run(batch_processing())
```

### Example 17: Conversation Memory with Context Management

```python
import register_facades
from facade_factory import FacadeFactory

class ConversationManager:
    """Manage conversation history with context window limits."""
    
    def __init__(self, facade, max_context_tokens=4000):
        self.facade = facade
        self.max_context_tokens = max_context_tokens
        self.messages = []
    
    def add_message(self, role: str, content: str):
        """Add message to history."""
        self.messages.append({"role": role, "content": content})
        self._trim_context()
    
    def _trim_context(self):
        """Keep context within token limit."""
        # Rough approximation: 1 token ≈ 4 characters
        total_chars = sum(len(m["content"]) for m in self.messages)
        estimated_tokens = total_chars // 4
        
        while estimated_tokens > self.max_context_tokens and len(self.messages) > 2:
            # Remove oldest messages (keep system message if present)
            if self.messages[0]["role"] == "system":
                self.messages.pop(1)
            else:
                self.messages.pop(0)
            
            total_chars = sum(len(m["content"]) for m in self.messages)
            estimated_tokens = total_chars // 4
    
    def chat(self, user_message: str) -> str:
        """Send message and get response."""
        self.add_message("user", user_message)
        
        response = self.facade.chat_completion(self.messages, max_tokens=500)
        assistant_message = response["content"]
        
        self.add_message("assistant", assistant_message)
        
        return assistant_message
    
    def get_message_count(self) -> int:
        """Get number of messages in context."""
        return len(self.messages)

def conversation_with_memory():
    """Extended conversation with automatic context management."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    manager = ConversationManager(facade, max_context_tokens=2000)
    
    # Add system message
    manager.add_message("system", "You are a helpful Python programming tutor.")
    
    # Multiple turns
    questions = [
        "What are Python decorators?",
        "Can you show me an example?",
        "How do they differ from class methods?",
        "When should I use them?",
        "What are some common use cases?"
    ]
    
    for question in questions:
        print(f"\nUser: {question}")
        response = manager.chat(question)
        print(f"Assistant: {response[:200]}...")
        print(f"(Context: {manager.get_message_count()} messages)")

if __name__ == "__main__":
    conversation_with_memory()
```

### Example 18: Retry Logic with Exponential Backoff

```python
import register_facades
from facade_factory import FacadeFactory
from llm_facade import RateLimitException, NetworkException
import time

def chat_with_retry(facade, messages, max_retries=5):
    """Chat with automatic retry on rate limits."""
    retry_delay = 1  # Start with 1 second
    
    for attempt in range(max_retries):
        try:
            response = facade.chat_completion(messages, max_tokens=300)
            return response
        
        except RateLimitException as e:
            if attempt == max_retries - 1:
                raise
            
            wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
            print(f"Rate limited. Retrying in {wait_time}s...")
            time.sleep(wait_time)
        
        except NetworkException as e:
            if attempt == max_retries - 1:
                raise
            
            print(f"Network error. Retrying...")
            time.sleep(retry_delay)
    
    raise Exception("Max retries exceeded")

def resilient_chat():
    """Chat with resilience to transient errors."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    messages = [
        {"role": "user", "content": "Explain error handling in Python"}
    ]
    
    try:
        response = chat_with_retry(facade, messages)
        print(response["content"])
    except Exception as e:
        print(f"Failed after retries: {e}")

if __name__ == "__main__":
    resilient_chat()
```

---

## Cost Optimization Examples

### Example 19: Automatic Cheapest Model Selection

```python
import register_facades
from facade_factory import FacadeFactory

def cost_optimized_chat():
    """Automatically use cheapest model for task."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    
    # Estimate token usage
    input_text = "What is machine learning?" * 10  # ~100 tokens
    estimated_input = len(input_text) // 4
    estimated_output = 500
    
    # Get cheapest model
    facade, cost = factory.create_cheapest_facade(
        capability="chat",
        input_tokens=estimated_input,
        output_tokens=estimated_output
    )
    
    print(f"Selected: {facade.provider_name}/{facade.model_name}")
    print(f"Estimated cost: ${cost:.6f}\n")
    
    response = facade.chat_completion(
        messages=[{"role": "user", "content": input_text}],
        max_tokens=estimated_output
    )
    
    # Calculate actual cost
    actual_cost = facade.estimate_cost(
        response['usage'].prompt_tokens,
        response['usage'].completion_tokens
    )
    
    print(f"Actual cost: ${actual_cost:.6f}")
    print(f"Tokens used: {response['usage'].total_tokens}")

if __name__ == "__main__":
    cost_optimized_chat()
```

### Example 20: Cost Comparison Across Providers

```python
import register_facades
from facade_factory import FacadeFactory

def compare_provider_costs():
    """Compare costs across different providers."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    
    providers_models = [
        ("anthropic", "claude-3-haiku-20240307"),
        ("openai", "gpt-3.5-turbo"),
        ("google", "gemini-1.5-flash"),
        ("groq", "llama-3.1-8b-instant"),
    ]
    
    input_tokens = 1000
    output_tokens = 500
    
    print("Cost Comparison (1K input + 500 output tokens):\n")
    
    costs = []
    for provider, model in providers_models:
        try:
            facade = factory.create_facade(provider, model)
            cost = facade.estimate_cost(input_tokens, output_tokens)
            costs.append((provider, model, cost))
            print(f"{provider:15} {model:40} ${cost:.6f}")
        except Exception as e:
            print(f"{provider:15} {model:40} Error: {e}")
    
    # Find cheapest
    if costs:
        costs.sort(key=lambda x: x[2])
        cheapest = costs[0]
        print(f"\n✓ Cheapest: {cheapest[0]}/{cheapest[1]} at ${cheapest[2]:.6f}")

if __name__ == "__main__":
    compare_provider_costs()
```

### Example 21: Budget-Aware Processing

```python
import register_facades
from facade_factory import FacadeFactory

class BudgetManager:
    """Manage API usage within budget."""
    
    def __init__(self, daily_budget: float):
        self.daily_budget = daily_budget
        self.spent_today = 0.0
        self.requests = []
    
    def can_afford(self, estimated_cost: float) -> bool:
        """Check if request is within budget."""
        return (self.spent_today + estimated_cost) <= self.daily_budget
    
    def record_request(self, cost: float, provider: str, model: str):
        """Record request cost."""
        self.spent_today += cost
        self.requests.append({
            "cost": cost,
            "provider": provider,
            "model": model
        })
    
    def get_remaining_budget(self) -> float:
        """Get remaining budget."""
        return self.daily_budget - self.spent_today
    
    def get_stats(self) -> dict:
        """Get spending statistics."""
        return {
            "budget": self.daily_budget,
            "spent": self.spent_today,
            "remaining": self.get_remaining_budget(),
            "requests": len(self.requests)
        }

def budget_aware_processing():
    """Process requests within budget."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    budget = BudgetManager(daily_budget=1.00)  # $1 daily budget
    
    requests = [
        "Explain Python classes",
        "What are Python decorators?",
        "Describe async/await in Python",
        "What is a Python generator?",
        "Explain Python context managers"
    ]
    
    for i, request in enumerate(requests, 1):
        # Estimate cost
        facade, estimated_cost = factory.create_cheapest_facade(
            capability="chat",
            input_tokens=len(request) // 4,
            output_tokens=200
        )
        
        if budget.can_afford(estimated_cost):
            print(f"\n{i}. Processing: {request[:50]}...")
            
            response = facade.chat_completion(
                messages=[{"role": "user", "content": request}],
                max_tokens=200
            )
            
            actual_cost = facade.estimate_cost(
                response['usage'].prompt_tokens,
                response['usage'].completion_tokens
            )
            
            budget.record_request(actual_cost, facade.provider_name, facade.model_name)
            print(f"   Model: {facade.provider_name}/{facade.model_name}")
            print(f"   Cost: ${actual_cost:.6f}")
            print(f"   Response: {response['content'][:100]}...")
        else:
            print(f"\n{i}. Skipped (budget exceeded): {request[:50]}...")
            break
    
    # Print summary
    stats = budget.get_stats()
    print(f"\n{'='*60}")
    print(f"Budget Summary:")
    print(f"  Daily Budget: ${stats['budget']:.6f}")
    print(f"  Spent: ${stats['spent']:.6f}")
    print(f"  Remaining: ${stats['remaining']:.6f}")
    print(f"  Requests: {stats['requests']}")

if __name__ == "__main__":
    budget_aware_processing()
```

---

## Multi-Provider Examples

### Example 22: Provider Fallback Chain

```python
import register_facades
from facade_factory import FacadeFactory
from llm_facade import LLMFacadeException

def chat_with_fallback(factory, messages, provider_chain):
    """Try providers in sequence until one succeeds."""
    last_error = None
    
    for provider, model in provider_chain:
        try:
            print(f"Trying {provider}/{model}...")
            facade = factory.create_facade(provider, model)
            response = facade.chat_completion(messages, max_tokens=300)
            print(f"✓ Success with {provider}/{model}")
            return response
        except Exception as e:
            print(f"✗ Failed with {provider}/{model}: {str(e)[:50]}")
            last_error = e
            continue
    
    raise last_error or Exception("All providers failed")

def resilient_multi_provider():
    """Use multiple providers for resilience."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    
    # Define fallback chain (primary -> backup -> last resort)
    provider_chain = [
        ("anthropic", "claude-3-5-sonnet-20241022"),  # Primary
        ("openai", "gpt-4-turbo-preview"),             # Backup
        ("groq", "llama-3.1-70b-versatile"),          # Fast fallback
        ("ollama", "llama3.1")                        # Local fallback
    ]
    
    messages = [
        {"role": "user", "content": "Explain microservices architecture"}
    ]
    
    try:
        response = chat_with_fallback(factory, messages, provider_chain)
        print(f"\nResponse: {response['content'][:200]}...")
    except Exception as e:
        print(f"\nAll providers failed: {e}")

if __name__ == "__main__":
    resilient_multi_provider()
```

### Example 23: Multi-Provider Comparison

```python
import register_facades
from facade_factory import FacadeFactory
import asyncio

async def compare_providers():
    """Compare responses from multiple providers."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    
    providers = [
        ("anthropic", "claude-3-5-sonnet-20241022"),
        ("openai", "gpt-4-turbo-preview"),
        ("google", "gemini-1.5-pro")
    ]
    
    question = "What are the key differences between SQL and NoSQL databases?"
    messages = [{"role": "user", "content": question}]
    
    async def get_response(provider, model):
        """Get response from a provider."""
        try:
            facade = factory.create_facade(provider, model)
            response = await facade.achat_completion(messages, max_tokens=200)
            return {
                "provider": provider,
                "model": model,
                "content": response["content"],
                "tokens": response["usage"].total_tokens,
                "cost": facade.estimate_cost(
                    response["usage"].prompt_tokens,
                    response["usage"].completion_tokens
                )
            }
        except Exception as e:
            return {
                "provider": provider,
                "model": model,
                "error": str(e)
            }
    
    # Get all responses concurrently
    tasks = [get_response(p, m) for p, m in providers]
    results = await asyncio.gather(*tasks)
    
    print(f"Question: {question}\n")
    print("="*80)
    
    for result in results:
        if "error" in result:
            print(f"\n{result['provider']}/{result['model']}")
            print(f"Error: {result['error']}")
        else:
            print(f"\n{result['provider']}/{result['model']}")
            print(f"Cost: ${result['cost']:.6f} | Tokens: {result['tokens']}")
            print(f"Response: {result['content'][:150]}...")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(compare_providers())
```

### Example 24: Provider Routing by Task Type

```python
import register_facades
from facade_factory import FacadeFactory

class SmartRouter:
    """Route requests to optimal provider based on task."""
    
    def __init__(self, factory):
        self.factory = factory
    
    def route(self, task_type: str, content: str):
        """Select best provider for task type."""
        routes = {
            "code": ("anthropic", "claude-3-5-sonnet-20241022"),  # Best for code
            "creative": ("openai", "gpt-4-turbo-preview"),        # Best for creative
            "fast": ("groq", "llama-3.1-70b-versatile"),         # Fastest
            "cheap": ("anthropic", "claude-3-haiku-20240307"),    # Cheapest
            "multimodal": ("google", "gemini-2.0-flash-exp"),    # Best multimodal
            "local": ("ollama", "llama3.1")                      # Privacy/offline
        }
        
        provider, model = routes.get(task_type, routes["fast"])
        facade = self.factory.create_facade(provider, model)
        
        response = facade.chat_completion(
            messages=[{"role": "user", "content": content}],
            max_tokens=300
        )
        
        return {
            "provider": provider,
            "model": model,
            "response": response["content"],
            "cost": facade.estimate_cost(
                response["usage"].prompt_tokens,
                response["usage"].completion_tokens
            )
        }

def smart_routing_example():
    """Use smart routing for different task types."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    router = SmartRouter(factory)
    
    tasks = [
        ("code", "Write a Python function to calculate fibonacci numbers"),
        ("creative", "Write a haiku about artificial intelligence"),
        ("fast", "What is 25 * 17?"),
        ("cheap", "Define machine learning in one sentence")
    ]
    
    for task_type, content in tasks:
        print(f"\nTask type: {task_type}")
        print(f"Request: {content}")
        
        result = router.route(task_type, content)
        
        print(f"Routed to: {result['provider']}/{result['model']}")
        print(f"Cost: ${result['cost']:.6f}")
        print(f"Response: {result['response'][:150]}...")

if __name__ == "__main__":
    smart_routing_example()
```

---

## Error Handling Examples

### Example 25: Comprehensive Error Handling

```python
import register_facades
from facade_factory import FacadeFactory
from llm_facade import (
    AuthenticationException,
    RateLimitException,
    ContextLengthExceededException,
    CapabilityNotSupportedException,
    InvalidResponseException,
    NetworkException
)

def robust_chat():
    """Handle all possible errors gracefully."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    
    try:
        facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
        
        messages = [
            {"role": "user", "content": "Explain quantum computing"}
        ]
        
        response = facade.chat_completion(messages, max_tokens=500)
        print(response["content"])
    
    except AuthenticationException as e:
        print(f"❌ Authentication failed: {e}")
        print("   → Check your API key in environment variables")
    
    except RateLimitException as e:
        print(f"❌ Rate limit exceeded: {e}")
        if e.retry_after:
            print(f"   → Retry after {e.retry_after} seconds")
        else:
            print("   → Wait a few minutes before retrying")
    
    except ContextLengthExceededException as e:
        print(f"❌ Context too long: {e.provided} tokens (max: {e.maximum})")
        print("   → Reduce input length or use a model with larger context")
    
    except CapabilityNotSupportedException as e:
        print(f"❌ Capability not supported: {e.capability}")
        print(f"   → Model '{e.model}' doesn't support this feature")
    
    except InvalidResponseException as e:
        print(f"❌ Invalid response from API: {e}")
        print("   → Try again or use a different model")
    
    except NetworkException as e:
        print(f"❌ Network error: {e}")
        print("   → Check internet connection and try again")
    
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("   → Check provider/model names and configuration")
    
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        print("   → Please report this issue")

if __name__ == "__main__":
    robust_chat()
```

### Example 26: Input Validation

```python
import register_facades
from facade_factory import FacadeFactory
from llm_facade import ContextLengthExceededException

def validate_and_process(facade, messages, max_tokens):
    """Validate input before processing."""
    # Check context window
    context_limit = facade.get_context_window_size()
    max_output = facade.get_max_output_tokens()
    
    # Estimate input tokens
    total_input_chars = sum(len(str(m.get("content", ""))) for m in messages)
    estimated_input_tokens = total_input_chars // 4
    
    # Validate
    errors = []
    
    if estimated_input_tokens + max_tokens > context_limit:
        errors.append(
            f"Total tokens ({estimated_input_tokens + max_tokens}) "
            f"exceeds context limit ({context_limit})"
        )
    
    if max_tokens > max_output:
        errors.append(
            f"max_tokens ({max_tokens}) exceeds model limit ({max_output})"
        )
    
    if errors:
        raise ValueError("Validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    
    # Process if valid
    return facade.chat_completion(messages, max_tokens=max_tokens)

def validated_processing():
    """Process with input validation."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("anthropic", "claude-3-haiku-20240307")
    
    # Get model limits
    print(f"Model: {facade.model_name}")
    print(f"Context window: {facade.get_context_window_size():,} tokens")
    print(f"Max output: {facade.get_max_output_tokens():,} tokens\n")
    
    messages = [
        {"role": "user", "content": "Explain machine learning"}
    ]
    
    try:
        response = validate_and_process(facade, messages, max_tokens=500)
        print(f"✓ Success: {response['content'][:100]}...")
    except ValueError as e:
        print(f"✗ Validation failed:\n{e}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    validated_processing()
```

---

## Real-World Applications

### Example 27: Customer Support Chatbot

```python
import register_facades
from facade_factory import FacadeFactory

class SupportBot:
    """Customer support chatbot with context."""
    
    def __init__(self, factory):
        self.factory = factory
        self.facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
        self.conversation_history = []
        
        # System prompt for support bot
        self.system_prompt = """You are a helpful customer support agent for TechCorp. 
Be friendly, professional, and solution-oriented. If you don't know something, 
offer to escalate to a human agent. Our business hours are 9 AM - 5 PM EST."""
    
    def start_conversation(self):
        """Initialize conversation."""
        self.conversation_history = []
        return "Hello! I'm the TechCorp support bot. How can I help you today?"
    
    def respond(self, user_message: str) -> str:
        """Generate response to user message."""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Get response
        response = self.facade.chat_completion(
            messages=self.conversation_history,
            system=self.system_prompt,
            max_tokens=300
        )
        
        assistant_message = response["content"]
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    
    def get_conversation_summary(self) -> str:
        """Generate conversation summary."""
        if not self.conversation_history:
            return "No conversation yet"
        
        # Create summary request
        summary_request = [{
            "role": "user",
            "content": f"""Summarize this customer support conversation:

{self._format_conversation()}

Provide:
1. Customer's main issue
2. Resolution status
3. Any follow-up needed"""
        }]
        
        response = self.facade.chat_completion(summary_request, max_tokens=200)
        return response["content"]
    
    def _format_conversation(self) -> str:
        """Format conversation for summary."""
        lines = []
        for msg in self.conversation_history:
            role = "Customer" if msg["role"] == "user" else "Agent"
            lines.append(f"{role}: {msg['content']}")
        return "\n\n".join(lines)

def customer_support_demo():
    """Demo customer support bot."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    bot = SupportBot(factory)
    
    # Start conversation
    print("Bot:", bot.start_conversation())
    
    # Simulate conversation
    conversation = [
        "Hi, I can't log into my account",
        "I tried resetting my password but didn't get the email",
        "My email is customer@example.com",
        "Yes, I checked spam folder",
        "Okay, thank you for your help!"
    ]
    
    for message in conversation:
        print(f"\nCustomer: {message}")
        response = bot.respond(message)
        print(f"Bot: {response}")
    
    # Get summary
    print("\n" + "="*60)
    print("Conversation Summary:")
    print(bot.get_conversation_summary())

if __name__ == "__main__":
    customer_support_demo()
```

### Example 28: Document Analysis and Summarization

```python
import register_facades
from facade_factory import FacadeFactory

def analyze_document(facade, document_text: str) -> dict:
    """Analyze a document for key information."""
    
    analyses = {}
    
    # 1. Generate summary
    print("Generating summary...")
    response = facade.chat_completion(
        messages=[{
            "role": "user",
            "content": f"Provide a concise summary of this document:\n\n{document_text}"
        }],
        max_tokens=200
    )
    analyses["summary"] = response["content"]
    
    # 2. Extract key points
    print("Extracting key points...")
    response = facade.chat_completion(
        messages=[{
            "role": "user",
            "content": f"List the 5 most important points from this document:\n\n{document_text}"
        }],
        max_tokens=300
    )
    analyses["key_points"] = response["content"]
    
    # 3. Identify action items
    print("Identifying action items...")
    response = facade.chat_completion(
        messages=[{
            "role": "user",
            "content": f"Identify any action items or tasks mentioned in this document:\n\n{document_text}"
        }],
        max_tokens=200
    )
    analyses["action_items"] = response["content"]
    
    # 4. Sentiment analysis
    print("Analyzing sentiment...")
    response = facade.chat_completion(
        messages=[{
            "role": "user",
            "content": f"Analyze the overall sentiment/tone of this document (positive/negative/neutral):\n\n{document_text}"
        }],
        max_tokens=100
    )
    analyses["sentiment"] = response["content"]
    
    return analyses

def document_analysis_demo():
    """Demo document analysis."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    # Sample document
    document = """
    Project Status Update - Q4 2025
    
    The development team has made significant progress on the new mobile app. 
    We've completed 75% of the planned features and are on track for a January 2026 release.
    
    Key Accomplishments:
    - User authentication system implemented and tested
    - Payment integration completed with Stripe
    - Push notifications working across iOS and Android
    - Initial user testing showed 90% satisfaction rate
    
    Challenges:
    - Backend scaling issues need to be addressed before launch
    - iOS App Store review may take 2-3 weeks
    - Need to hire 2 more QA engineers
    
    Next Steps:
    - Complete remaining 25% of features by December 15
    - Begin beta testing with 100 users
    - Finalize marketing materials
    - Schedule team training for customer support
    
    Budget: Currently at 85% of allocated budget with good runway for completion.
    """
    
    print("Analyzing document...\n")
    results = analyze_document(facade, document)
    
    print("\n" + "="*60)
    print("DOCUMENT ANALYSIS RESULTS")
    print("="*60)
    
    print("\n📝 SUMMARY:")
    print(results["summary"])
    
    print("\n🎯 KEY POINTS:")
    print(results["key_points"])
    
    print("\n✅ ACTION ITEMS:")
    print(results["action_items"])
    
    print("\n💭 SENTIMENT:")
    print(results["sentiment"])

if __name__ == "__main__":
    document_analysis_demo()
```

### Example 29: Code Review Assistant

```python
import register_facades
from facade_factory import FacadeFactory

def review_code(facade, code: str, language: str) -> dict:
    """AI-powered code review."""
    
    reviews = {}
    
    # 1. General assessment
    response = facade.chat_completion(
        messages=[{
            "role": "user",
            "content": f"""Review this {language} code and provide:
1. Overall code quality (1-10)
2. Brief assessment

Code:
```{language}
{code}
```"""
        }],
        max_tokens=200
    )
    reviews["assessment"] = response["content"]
    
    # 2. Identify issues
    response = facade.chat_completion(
        messages=[{
            "role": "user",
            "content": f"""Identify potential bugs, security issues, or problems in this {language} code:

```{language}
{code}
```

List each issue with line numbers if applicable."""
        }],
        max_tokens=400
    )
    reviews["issues"] = response["content"]
    
    # 3. Suggest improvements
    response = facade.chat_completion(
        messages=[{
            "role": "user",
            "content": f"""Suggest specific improvements for this {language} code (performance, readability, best practices):

```{language}
{code}
```"""
        }],
        max_tokens=400
    )
    reviews["improvements"] = response["content"]
    
    return reviews

def code_review_demo():
    """Demo AI code review."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    # Sample code with issues
    code = """
def calculate_average(numbers):
    total = 0
    for i in range(len(numbers)):
        total = total + numbers[i]
    return total / len(numbers)

def process_data(data):
    result = []
    for item in data:
        if item != None:
            result.append(item * 2)
    return result

# Main
data = [1, 2, None, 4, 5]
avg = calculate_average([1, 2, 3, 4, 5])
processed = process_data(data)
print("Average:", avg)
print("Processed:", processed)
"""
    
    print("Reviewing code...\n")
    results = review_code(facade, code, "python")
    
    print("="*60)
    print("CODE REVIEW RESULTS")
    print("="*60)
    
    print("\n📊 ASSESSMENT:")
    print(results["assessment"])
    
    print("\n🐛 ISSUES FOUND:")
    print(results["issues"])
    
    print("\n💡 IMPROVEMENTS:")
    print(results["improvements"])

if __name__ == "__main__":
    code_review_demo()
```

### Example 30: Content Generation Pipeline

```python
import register_facades
from facade_factory import FacadeFactory
import asyncio

class ContentPipeline:
    """Generate various content types in a pipeline."""
    
    def __init__(self, factory):
        self.factory = factory
    
    async def generate_blog_post(self, topic: str) -> dict:
        """Generate complete blog post with all components."""
        
        # Use different models for different tasks
        creative_facade = self.factory.create_facade("openai", "gpt-4-turbo-preview")
        fast_facade = self.factory.create_facade("groq", "llama-3.1-70b-versatile")
        
        print(f"Generating content for: {topic}\n")
        
        # 1. Generate title (fast)
        print("📝 Generating title...")
        title_task = fast_facade.achat_completion(
            messages=[{
                "role": "user",
                "content": f"Generate a catchy blog post title about: {topic}"
            }],
            max_tokens=50
        )
        
        # 2. Generate outline (fast)
        print("📋 Creating outline...")
        outline_task = fast_facade.achat_completion(
            messages=[{
                "role": "user",
                "content": f"Create a blog post outline with 5 main sections about: {topic}"
            }],
            max_tokens=200
        )
        
        # Wait for title and outline
        title_response, outline_response = await asyncio.gather(title_task, outline_task)
        title = title_response["content"]
        outline = outline_response["content"]
        
        print(f"✓ Title: {title[:60]}...")
        print(f"✓ Outline ready\n")
        
        # 3. Generate main content (creative)
        print("✍️  Writing main content...")
        content_response = await creative_facade.achat_completion(
            messages=[{
                "role": "user",
                "content": f"""Write a blog post about: {topic}

Title: {title}

Outline:
{outline}

Write engaging, informative content (500-700 words)."""
            }],
            max_tokens=1000
        )
        content = content_response["content"]
        print("✓ Content written\n")
        
        # 4. Generate meta description (fast)
        print("🏷️  Creating meta description...")
        meta_response = await fast_facade.achat_completion(
            messages=[{
                "role": "user",
                "content": f"Write a 150-character SEO meta description for:\n\n{content[:500]}"
            }],
            max_tokens=50
        )
        meta_description = meta_response["content"]
        print("✓ Meta description ready\n")
        
        # 5. Generate tags (fast)
        print("🏷️  Generating tags...")
        tags_response = await fast_facade.achat_completion(
            messages=[{
                "role": "user",
                "content": f"Generate 5 relevant tags/keywords for this blog post:\n\n{content[:300]}"
            }],
            max_tokens=50
        )
        tags = tags_response["content"]
        print("✓ Tags generated\n")
        
        return {
            "title": title,
            "outline": outline,
            "content": content,
            "meta_description": meta_description,
            "tags": tags
        }

async def content_generation_demo():
    """Demo content generation pipeline."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    pipeline = ContentPipeline(factory)
    
    # Generate blog post
    result = await pipeline.generate_blog_post(
        "The Future of Artificial Intelligence in Healthcare"
    )
    
    print("="*60)
    print("GENERATED BLOG POST")
    print("="*60)
    
    print(f"\n📰 TITLE:")
    print(result["title"])
    
    print(f"\n📋 OUTLINE:")
    print(result["outline"])
    
    print(f"\n📄 CONTENT:")
    print(result["content"][:500] + "...")
    
    print(f"\n🏷️  META DESCRIPTION:")
    print(result["meta_description"])
    
    print(f"\n🏷️  TAGS:")
    print(result["tags"])

if __name__ == "__main__":
    asyncio.run(content_generation_demo())
```

---

## Additional Practical Examples

### Example 31: Data Extraction from Text

```python
import register_facades
from facade_factory import FacadeFactory
import json

def extract_structured_data(facade, text: str) -> dict:
    """Extract structured data from unstructured text."""
    
    response = facade.chat_completion(
        messages=[{
            "role": "system",
            "content": "Extract information and respond with valid JSON only."
        }, {
            "role": "user",
            "content": f"""Extract the following information from this text:
- Names (people)
- Companies/Organizations
- Dates
- Locations
- Key facts/numbers

Text: {text}

Respond with JSON in this format:
{{
  "names": ["name1", "name2"],
  "companies": ["company1"],
  "dates": ["date1"],
  "locations": ["location1"],
  "facts": ["fact1"]
}}"""
        }],
        max_tokens=400
    )
    
    # Parse JSON response
    try:
        data = json.loads(response["content"])
        return data
    except json.JSONDecodeError:
        # Extract JSON from response if wrapped in markdown
        content = response["content"]
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        return json.loads(content.strip())

def data_extraction_demo():
    """Demo structured data extraction."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("openai", "gpt-4-turbo-preview")
    
    text = """
    TechCorp announced today that CEO Jane Smith will step down effective December 31, 2025.
    The company, based in San Francisco, reported revenue of $2.3 billion for Q3.
    John Doe, currently serving as COO, will take over as CEO starting January 1, 2026.
    The transition follows TechCorp's acquisition of DataSystems Inc. in September 2025.
    """
    
    print("Extracting data from text...\n")
    data = extract_structured_data(facade, text)
    
    print("EXTRACTED DATA:")
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    data_extraction_demo()
```

### Example 32: Translation Service

```python
import register_facades
from facade_factory import FacadeFactory

def translate_text(facade, text: str, target_language: str) -> str:
    """Translate text to target language."""
    response = facade.chat_completion(
        messages=[{
            "role": "user",
            "content": f"Translate the following text to {target_language}. Respond with only the translation:\n\n{text}"
        }],
        max_tokens=len(text) * 2  # Allow for language expansion
    )
    return response["content"]

def multi_language_demo():
    """Demo translation across multiple languages."""
    factory = FacadeFactory(config_source="json", config_path="./config")
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    original = "Artificial intelligence is transforming how we live and work."
    languages = ["Spanish", "French", "German", "Japanese", "Arabic"]
    
    print(f"Original (English): {original}\n")
    
    for language in languages:
        translated = translate_text(facade, original, language)
        print(f"{language}: {translated}")

if __name__ == "__main__":
    multi_language_demo()
```

---

## Summary

This examples document contains **30+ comprehensive examples** covering:

1. ✅ **Basic Operations** (5 examples) - Simple chat, conversations, streaming, async
2. ✅ **Provider-Specific** (8 examples) - Vision, functions, embeddings, images
3. ✅ **Advanced Features** (6 examples) - Sampling, routing, batch processing, memory
4. ✅ **Cost Optimization** (3 examples) - Cheapest selection, comparison, budgeting
5. ✅ **Multi-Provider** (3 examples) - Fallbacks, comparisons, smart routing
6. ✅ **Error Handling** (2 examples) - Comprehensive handling, validation
7. ✅ **Real-World Apps** (5+ examples) - Support bot, document analysis, code review, content generation

All examples are:
- ✅ Production-ready
- ✅ Fully commented
- ✅ Complete and runnable
- ✅ Cover real use cases
- ✅ Include error handling
- ✅ Show best practices

---

**Copyright © 2025-2030 | Ashutosh Sinha | ajsinha@gmail.com**
