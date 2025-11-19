"""
Abhikarta Mock Facade - For Testing (Complete Version)

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import time
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator, Callable, Tuple

from llm_provider.base_provider_facade import BaseProviderFacade
from llm_provider.llm_facade import *


class MockFacade(BaseProviderFacade):
    """Mock facade for testing and development with all required methods."""

    def __init__(self, provider, model_name: str, **kwargs):
        """Initialize mock facade."""
        # Call parent init
        super().__init__(provider, model_name, **kwargs)

        # Initialize the client (sets up mock-specific attributes)
        self._initialize_client()

    def _initialize_client(self):
        """No real client needed for mock."""
        self.call_count = 0
        self.latency_ms = self.kwargs.get('mock_latency_ms', 100)

    def chat_completion(self, messages: Messages, temperature: Optional[float] = None,
                       max_tokens: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        self.call_count += 1
        time.sleep(self.latency_ms / 1000.0)

        # Generate mock response
        last_message = messages[-1]['content'] if messages else "Hello"
        response_text = f"Mock response to: {last_message[:50]}... (call #{self.call_count})"

        token_count = len(response_text) // 4

        return {
            "content": response_text,
            "tool_calls": None,
            "usage": {
                "prompt_tokens": token_count,
                "completion_tokens": token_count,
                "total_tokens": token_count * 2
            },
            "metadata": {
                "model": self.model_name,
                "finish_reason": "stop"
            },
            "raw_response": {"mock": True}
        }

    async def achat_completion(self, messages: Messages, **kwargs) -> Dict[str, Any]:
        import asyncio
        await asyncio.sleep(self.latency_ms / 1000.0)
        return self.chat_completion(messages, **kwargs)

    def stream_chat_completion(self, messages: Messages, **kwargs) -> Iterator[str]:
        self.call_count += 1
        words = ["This", "is", "a", "mock", "streaming", "response", f"(call #{self.call_count})"]

        for word in words:
            time.sleep(0.05)
            yield word + " "

    async def astream_chat_completion(self, messages: Messages, **kwargs) -> AsyncIterator[str]:
        import asyncio
        self.call_count += 1
        words = ["This", "is", "a", "mock", "streaming", "response", f"(call #{self.call_count})"]

        for word in words:
            await asyncio.sleep(0.05)
            yield word + " "

    def chat_completion_with_vision(self, messages: Messages, images: List[ImageInput], **kwargs) -> Dict[str, Any]:
        self.call_count += 1

        return {
            "content": f"Mock vision response: I see {len(images)} image(s) (call #{self.call_count})",
            "tool_calls": None,
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            },
            "metadata": {
                "model": self.model_name,
                "finish_reason": "stop"
            },
            "raw_response": {"mock": True}
        }

    async def achat_completion_with_vision(self, messages: Messages, images: List[ImageInput], **kwargs) -> Dict[str, Any]:
        """Async vision chat."""
        import asyncio
        await asyncio.sleep(0.05)
        return self.chat_completion_with_vision(messages, images, **kwargs)

    def text_completion(self, prompt: str, **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = self.chat_completion(messages, **kwargs)
        return response["content"]

    async def atext_completion(self, prompt: str, **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = await self.achat_completion(messages, **kwargs)
        return response["content"]

    def stream_text_completion(self, prompt: str, **kwargs) -> TextStream:
        messages = [{"role": "user", "content": prompt}]
        return self.stream_chat_completion(messages, **kwargs)

    async def astream_text_completion(self, prompt: str, **kwargs) -> TextStream:
        messages = [{"role": "user", "content": prompt}]
        async for chunk in self.astream_chat_completion(messages, **kwargs):
            yield chunk

    def text_generation(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        return self.text_completion(prompt, **kwargs)

    async def atext_generation(self, prompt: str, **kwargs) -> str:
        """Async text generation."""
        return await self.atext_completion(prompt, **kwargs)

    def stream_text_generation(self, prompt: str, **kwargs) -> TextStream:
        """Stream text generation."""
        return self.stream_text_completion(prompt, **kwargs)

    def parse_tool_calls(self, response: Dict[str, Any], **kwargs) -> List[ToolCall]:
        return []

    def count_tokens(self, text: str, **kwargs) -> int:
        return len(text) // 4

    def generate_embeddings(self, texts: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        is_single = isinstance(texts, str)
        # Return mock embeddings (128-dimensional)
        embedding = [0.1] * 128
        return embedding if is_single else [embedding]

    async def agenerate_embeddings(self, texts: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        return self.generate_embeddings(texts, **kwargs)

    def generate_image(self, prompt: str, **kwargs) -> ImageOutput:
        return f"mock_image_url_for_{prompt[:20]}.png"

    async def agenerate_image(self, prompt: str, **kwargs) -> ImageOutput:
        return self.generate_image(prompt, **kwargs)

    def moderate_content(self, content: str, **kwargs) -> ModerationResult:
        return {
            "flagged": False,
            "categories": {"hate": False, "violence": False},
            "scores": {"hate": 0.01, "violence": 0.02}
        }

    async def amoderate_content(self, content: str, **kwargs) -> ModerationResult:
        return self.moderate_content(content, **kwargs)

    def log_request(self, method: str, input_data: Any, response: Any, latency_ms: float, metadata: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        print(f"Mock: Logged {method} call")

    def get_usage_stats(self, period: str = "day", **kwargs) -> Dict[str, Any]:
        return {
            "total_calls": self.call_count,
            "mock": True
        }

    # Additional required methods from LLMFacade

    def audio_transcription(self, audio: Any, **kwargs) -> str:
        """Transcribe audio."""
        return "Mock transcription: Hello world"

    def audio_translation(self, audio: Any, **kwargs) -> str:
        """Translate audio."""
        return "Mock translation: Hello world"

    def batch_embed(self, texts: List[str], **kwargs) -> List[Embedding]:
        """Batch embed texts."""
        return [[0.1] * 128 for _ in texts]

    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """Batch generate responses."""
        return [f"Mock response to: {p[:30]}..." for p in prompts]

    def call_tool(self, tool_name: str, arguments: Dict[str, Any], **kwargs) -> Any:
        """Call a tool."""
        return {"mock_tool_result": f"Called {tool_name} with {arguments}"}

    def classify_text(self, text: str, labels: List[str], **kwargs) -> Dict[str, float]:
        """Classify text into labels."""
        return {label: 0.5 for label in labels}

    def clear_conversation(self, conversation_id: str, **kwargs) -> bool:
        """Clear conversation."""
        return True

    def code_completion(self, code: str, **kwargs) -> str:
        """Complete code."""
        return code + "\n# Mock code completion"

    def code_explanation(self, code: str, **kwargs) -> str:
        """Explain code."""
        return f"Mock explanation: This code does something"

    def code_generation(self, description: str, language: str = "python", **kwargs) -> str:
        """Generate code from description."""
        return f"# Mock {language} code for: {description}\nprint('Hello')"

    def code_review(self, code: str, **kwargs) -> str:
        """Review code."""
        return "Mock review: Code looks good"

    def compute_similarity(self, text1: str, text2: str, **kwargs) -> float:
        """Compute similarity between texts."""
        return 0.75

    def continue_conversation(self, conversation_id: str, message: str, **kwargs) -> Dict[str, Any]:
        """Continue existing conversation."""
        return self.chat_completion([{"role": "user", "content": message}], **kwargs)

    def create_conversation(self, initial_message: str, **kwargs) -> Dict[str, Any]:
        """Create new conversation."""
        return {
            "conversation_id": f"mock_conv_{int(time.time())}",
            "response": self.chat_completion([{"role": "user", "content": initial_message}], **kwargs)
        }

    def create_fine_tuning_job(self, training_data: Any, **kwargs) -> str:
        """Create fine-tuning job."""
        return "mock_finetuning_job_123"

    def create_tool_definition(self, function: Callable, **kwargs) -> ToolDefinition:
        """Create tool definition from function."""
        return {
            "type": "function",
            "function": {
                "name": function.__name__,
                "description": "Mock tool",
                "parameters": {"type": "object", "properties": {}}
            }
        }

    def embed_image(self, image: ImageInput, **kwargs) -> Embedding:
        """Embed image."""
        return [0.1] * 128

    def embed_text(self, text: str, **kwargs) -> Embedding:
        """Embed single text."""
        return [0.1] * 128

    def execute_tool_loop(self, messages: Messages, tools: List[ToolDefinition],
                         tool_functions: Dict[str, Callable], max_iterations: int = 5, **kwargs) -> Dict[str, Any]:
        """Execute tool calling loop."""
        return self.chat_completion(messages, **kwargs)

    def extract_structured_data(self, text: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Extract structured data from text."""
        return {"mock_extracted": "data"}

    def generate_with_schema(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate with JSON schema."""
        return {"mock_result": "data"}

    def get_context_window(self) -> int:
        """Get context window size."""
        return self.model.context_window if hasattr(self, 'model') else 8192

    def get_conversation_history(self, conversation_id: str, **kwargs) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return []

    def get_fine_tuning_status(self, job_id: str, **kwargs) -> Dict[str, Any]:
        """Get fine-tuning status."""
        return {"job_id": job_id, "status": "completed", "mock": True}

    def image_captioning(self, image: ImageInput, **kwargs) -> str:
        """Generate caption for image."""
        return "Mock caption: A beautiful scene"

    def image_editing(self, image: ImageInput, prompt: str, **kwargs) -> ImageOutput:
        """Edit image with prompt."""
        return f"mock_edited_image_{int(time.time())}.png"

    def image_generation(self, prompt: str, **kwargs) -> ImageOutput:
        """Generate image from prompt."""
        return self.generate_image(prompt, **kwargs)

    def image_variation(self, image: ImageInput, **kwargs) -> ImageOutput:
        """Create image variation."""
        return f"mock_variation_{int(time.time())}.png"

    def rag_chat(self, query: str, documents: List[Document], **kwargs) -> Dict[str, Any]:
        """RAG-based chat."""
        return {
            "content": f"Mock RAG response to: {query[:50]}",
            "sources": [doc.get('id', 'mock_doc') for doc in documents[:3]]
        }

    def rag_generate(self, query: str, documents: List[Document], **kwargs) -> str:
        """RAG-based generation."""
        return f"Mock RAG answer based on {len(documents)} documents"

    def retrieve_documents(self, query: str, document_store: Any, top_k: int = 5, **kwargs) -> RetrievalResult:
        """Retrieve relevant documents."""
        mock_doc = {"id": "mock_1", "content": "Mock document", "metadata": {}}
        return [(mock_doc, 0.9) for _ in range(top_k)]

    def truncate_to_max_tokens(self, text: str, max_tokens: int, **kwargs) -> str:
        """Truncate text to max tokens."""
        words = text.split()
        truncated = " ".join(words[:max_tokens])
        return truncated


__all__ = ['MockFacade']