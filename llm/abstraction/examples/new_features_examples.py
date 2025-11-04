"""
Comprehensive Examples for New Features

Demonstrates improvements 4-12:
- Function Calling
- RAG Support
- Prompt Templates
- Response Validation
- Batch Processing
- Conversation Management
- Embeddings
- Connection Pooling
- Semantic Caching

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pydantic import BaseModel, Field
from typing import List


# Example 1: Function Calling / Tool Use
def example_function_calling():
    print("="*70)
    print("EXAMPLE 1: Function Calling / Tool Use")
    print("="*70)
    
    from llm.abstraction.tools import Tool, ToolRegistry, ToolParameter, ToolParameterType
    
    # Create tools
    def get_weather(location: str) -> str:
        """Get weather for a location"""
        return f"Weather in {location}: Sunny, 72°F"
    
    def calculate(expression: str) -> float:
        """Calculate mathematical expression"""
        return eval(expression.replace('^', '**'))
    
    # Create registry
    registry = ToolRegistry()
    
    # Register tools
    registry.register(Tool(
        name="get_weather",
        description="Get current weather for a location",
        function=get_weather,
        parameters=[
            ToolParameter(
                name="location",
                type=ToolParameterType.STRING,
                description="City name",
                required=True
            )
        ]
    ))
    
    registry.register(Tool(
        name="calculate",
        description="Perform calculations",
        function=calculate,
        parameters=[
            ToolParameter(
                name="expression",
                type=ToolParameterType.STRING,
                description="Math expression",
                required=True
            )
        ]
    ))
    
    print("\n✅ Registered tools:")
    for tool_name in registry.list_tools():
        print(f"  - {tool_name}")
    
    # Execute tools
    print("\n🔧 Executing tools:")
    weather = registry.execute("get_weather", location="San Francisco")
    print(f"  Weather: {weather}")
    
    result = registry.execute("calculate", expression="2^8 + 15")
    print(f"  Calculation: {result}")
    
    print("="*70 + "\n")


# Example 2: Prompt Templates
def example_prompt_templates():
    print("="*70)
    print("EXAMPLE 2: Prompt Templates")
    print("="*70)
    
    from llm.abstraction.prompts import PromptTemplate, PromptRegistry, create_default_templates
    
    # Create registry with defaults
    registry = create_default_templates()
    
    print("\n📝 Available templates:")
    for name in registry.list_templates():
        print(f"  - {name}")
    
    # Use templates
    print("\n🎨 Using templates:")
    
    # Summarization
    summary_prompt = registry.render(
        'summarize',
        num_sentences=3,
        text="This is a long text about AI and machine learning..."
    )
    print(f"\nSummarize template:\n{summary_prompt[:100]}...")
    
    # Translation
    translate_prompt = registry.render(
        'translate',
        source_lang='English',
        target_lang='Spanish',
        text='Hello, how are you?'
    )
    print(f"\nTranslate template:\n{translate_prompt}")
    
    # Custom template
    custom = PromptTemplate(
        name="custom_analysis",
        template="Analyze {data_type} and focus on {aspects}",
        description="Custom analysis template"
    )
    registry.register(custom)
    
    analysis_prompt = registry.render(
        'custom_analysis',
        data_type='sales data',
        aspects='trends and patterns'
    )
    print(f"\nCustom template:\n{analysis_prompt}")
    
    print("\n✅ Template usage:", registry.get_usage_stats())
    print("="*70 + "\n")


# Example 3: Embeddings & Semantic Search
def example_embeddings():
    print("="*70)
    print("EXAMPLE 3: Embeddings & Semantic Search")
    print("="*70)
    
    from llm.abstraction.embeddings import EmbeddingClient, VectorStore, SemanticSearch
    
    # Create embedding client (using mock for demo)
    client = EmbeddingClient(provider='mock')
    
    # Create documents
    documents = [
        "Python is a high-level programming language",
        "Machine learning is a subset of artificial intelligence",
        "Neural networks are inspired by biological neurons",
        "Data science involves statistics and programming",
        "Deep learning uses multiple layers of neural networks"
    ]
    
    # Build search index
    search = SemanticSearch(client)
    search.add_documents(documents)
    
    print(f"\n📚 Indexed {len(documents)} documents")
    
    # Search
    print("\n🔍 Searching for 'AI and neural nets':")
    results = search.search("AI and neural nets", top_k=3)
    
    for i, result in enumerate(results, 1):
        print(f"\n  Result {i} (similarity: {result['similarity']:.3f}):")
        print(f"  {result['text']}")
    
    print("="*70 + "\n")


# Example 4: RAG (Retrieval Augmented Generation)
def example_rag():
    print("="*70)
    print("EXAMPLE 4: RAG (Retrieval Augmented Generation)")
    print("="*70)
    
    from llm.abstraction.embeddings import EmbeddingClient, VectorStore
    from llm.abstraction.rag import RAGClient, build_knowledge_base
    from llm.abstraction.providers.mock import MockProvider
    
    # Create knowledge base
    documents = [
        "Our company was founded in 2020 in San Francisco.",
        "We offer 24/7 customer support via email and phone.",
        "Our return policy allows returns within 30 days.",
        "We ship to over 50 countries worldwide.",
        "Annual revenue in 2024 was $10 million."
    ]
    
    embedding_client = EmbeddingClient(provider='mock')
    vector_store = build_knowledge_base(documents, embedding_client)
    
    print(f"\n📚 Knowledge base: {vector_store.size()} chunks")
    
    # Create RAG client (mock LLM)
    mock_provider = MockProvider()
    mock_provider.initialize({})
    facade = mock_provider.create_facade('mock-model')
    
    rag = RAGClient(facade, vector_store, top_k=2)
    
    # Query
    print("\n❓ Question: 'What is your return policy?'")
    response = rag.query("What is your return policy?")
    
    print(f"\n💡 Answer: {response.answer}")
    print(f"\n📖 Sources used: {len(response.sources)}")
    for source in response.sources:
        print(f"  - {source.document.content[:60]}... (score: {source.score:.3f})")
    
    print("="*70 + "\n")


# Example 5: Response Validation
def example_validation():
    print("="*70)
    print("EXAMPLE 5: Response Validation")
    print("="*70)
    
    from llm.abstraction.validation import ResponseValidator
    from pydantic import BaseModel
    
    # Define schema
    class Product(BaseModel):
        name: str = Field(..., description="Product name")
        price: float = Field(..., gt=0, description="Product price")
        categories: List[str] = Field(..., description="Categories")
    
    validator = ResponseValidator()
    
    # Valid response
    print("\n✅ Validating valid JSON:")
    valid_json = '{"name": "Laptop", "price": 999.99, "categories": ["Electronics", "Computers"]}'
    
    try:
        product = validator.validate(valid_json, Product)
        print(f"  Product: {product.name}")
        print(f"  Price: ${product.price}")
        print(f"  Categories: {', '.join(product.categories)}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Invalid response
    print("\n❌ Validating invalid JSON:")
    invalid_json = '{"name": "Laptop", "price": -50}'
    
    try:
        product = validator.validate(invalid_json, Product)
    except Exception as e:
        print(f"  Error caught: {str(e)[:60]}...")
    
    print("="*70 + "\n")


# Example 6: Batch Processing
def example_batch_processing():
    print("="*70)
    print("EXAMPLE 6: Batch Processing")
    print("="*70)
    
    from llm.abstraction.batch import BatchProcessor
    from llm.abstraction.providers.mock import MockProvider
    
    # Create client
    mock_provider = MockProvider()
    mock_provider.initialize({})
    facade = mock_provider.create_facade('mock-model')
    
    # Create batch processor
    processor = BatchProcessor(facade, batch_size=5, max_concurrent=3)
    
    # Batch of prompts
    prompts = [
        "Summarize article 1",
        "Summarize article 2",
        "Summarize article 3",
        "Summarize article 4",
        "Summarize article 5",
        "Summarize article 6",
        "Summarize article 7",
        "Summarize article 8",
    ]
    
    print(f"\n📦 Processing {len(prompts)} prompts in batches...")
    
    result = processor.process_batch_sync(prompts)
    
    print(f"\n✅ Results:")
    print(f"  Total: {result.total}")
    print(f"  Successful: {result.successful}")
    print(f"  Failed: {len(result.failed)}")
    print(f"  Duration: {result.duration_seconds:.2f}s")
    print(f"  Throughput: {result.successful / result.duration_seconds:.1f} requests/sec")
    
    print("="*70 + "\n")


# Example 7: Conversation Management
def example_conversation():
    print("="*70)
    print("EXAMPLE 7: Conversation Management")
    print("="*70)
    
    from llm.abstraction.conversation import ChatClient, Conversation
    from llm.abstraction.providers.mock import MockProvider
    
    # Create client
    mock_provider = MockProvider()
    mock_provider.initialize({})
    facade = mock_provider.create_facade('mock-model')
    
    # Create chat client
    chat = ChatClient(
        facade,
        max_history=10,
        system_message="You are a helpful assistant."
    )
    
    print("\n💬 Starting conversation:")
    
    # Conversation
    print("\n👤 User: Hello! My name is Alice.")
    response1 = chat.chat("Hello! My name is Alice.")
    print(f"🤖 Assistant: {response1[:60]}...")
    
    print("\n👤 User: What's my name?")
    response2 = chat.chat("What's my name?")
    print(f"🤖 Assistant: {response2[:60]}...")
    
    print("\n👤 User: Tell me about Python.")
    response3 = chat.chat("Tell me about Python.")
    print(f"🤖 Assistant: {response3[:60]}...")
    
    print(f"\n📊 Conversation stats:")
    print(f"  Messages: {len(chat.conversation.messages)}")
    print(f"  Context length: {len(chat.conversation.format_history())} chars")
    
    print("="*70 + "\n")


# Example 8: Semantic Caching
def example_semantic_cache():
    print("="*70)
    print("EXAMPLE 8: Semantic Caching")
    print("="*70)
    
    from llm.abstraction.embeddings import EmbeddingClient
    from llm.abstraction.advanced import SemanticCache
    
    # Create cache
    embedding_client = EmbeddingClient(provider='mock')
    cache = SemanticCache(
        embedding_client,
        similarity_threshold=0.90,
        max_size=100
    )
    
    # Cache some responses
    cache.set("What is Python?", "Python is a programming language.")
    cache.set("Tell me about AI", "AI is artificial intelligence.")
    cache.set("How does ML work?", "ML learns from data patterns.")
    
    print("\n✅ Cached 3 responses")
    
    # Try similar queries
    print("\n🔍 Testing semantic cache:")
    
    queries = [
        "What is Python?",  # Exact match
        "Tell me about Python",  # Similar
        "Explain AI to me",  # Similar
        "What is quantum computing?"  # Not cached
    ]
    
    for query in queries:
        result = cache.get(query)
        status = "✅ HIT" if result else "❌ MISS"
        print(f"  {status}: '{query}'")
        if result:
            print(f"    → {result}")
    
    print("="*70 + "\n")


def main():
    """Run all examples"""
    print("\n" + "🚀" * 35)
    print("ABHIKARTA LLM - NEW FEATURES EXAMPLES")
    print("Features 4-12 Demonstration")
    print("🚀" * 35 + "\n")
    
    examples = [
        ("Function Calling", example_function_calling),
        ("Prompt Templates", example_prompt_templates),
        ("Embeddings & Search", example_embeddings),
        ("RAG", example_rag),
        ("Response Validation", example_validation),
        ("Batch Processing", example_batch_processing),
        ("Conversation Management", example_conversation),
        ("Semantic Caching", example_semantic_cache),
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        try:
            func()
        except Exception as e:
            print(f"❌ Example {i} ({name}) failed: {e}\n")
    
    print("=" * 70)
    print("✅ All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
