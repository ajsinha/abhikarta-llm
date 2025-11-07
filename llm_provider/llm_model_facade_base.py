from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Iterator, AsyncIterator, Tuple
from PIL.Image import Image
import io

# Type aliases
Messages = List[Dict[str, str]]  # [{"role": "user"|"assistant"|"system", "content": str}]
TextStream = Union[Iterator[str], AsyncIterator[str]]
ToolDefinition = Dict[str, Any]
ToolCall = Dict[str, Any]
Document = Dict[str, Any]  # { "content": str, "metadata": dict, ... }
RetrievalResult = List[Document]


class LLMModelBase(ABC):
    """
    Abstract base class defining a unified, provider-agnostic interface for LLM operations.
    Acts as a **facade** over different LLM backends (e.g., Hugging Face, OpenAI, Anthropic, Groq, local TGI).
    Concrete subclasses implement these methods for specific models while maintaining identical call signatures.
    """

    # =====================================================================
    # Core Text Generation
    # =====================================================================

    @abstractmethod
    def text_generation(
        self,
        prompt: str,
        *,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        repetition_penalty: Optional[float] = None,
        stream: bool = False,
        **kwargs,
    ) -> Union[str, TextStream]:
        """
        Generate continuation text from a raw prompt (non-chat completion).

        Args:
            prompt (str): The input text to complete.
            max_new_tokens (int, optional): Maximum number of tokens to generate. If None, uses model default.
            temperature (float, optional): Sampling temperature. Higher = more random (0.0–2.0 typical).
            top_p (float, optional): Nucleus sampling threshold. Filters tokens with cumulative prob < top_p.
            top_k (int, optional): Limits sampling to top K most likely tokens.
            stop_sequences (List[str], optional): List of strings that halt generation if generated.
            repetition_penalty (float, optional): Penalizes token repetition (>1.0 discourages, <1.0 encourages).
            stream (bool): If True, returns an iterator yielding chunks as they are generated.
            **kwargs: Provider-specific parameters (e.g., presence_penalty, logprobs).

        Returns:
            str | TextStream: Full generated text if stream=False; else iterator of incremental chunks.
        """
        pass

    @abstractmethod
    def chat_completion(
        self,
        messages: Messages,
        *,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        stream: bool = False,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[Union[str, Dict]] = None,
        **kwargs,
    ) -> Union[Dict[str, Any], TextStream]:
        """
        Perform structured multi-turn chat with role-based messages and optional tool calling.

        Args:
            messages (Messages): List of message dicts with 'role' ('user', 'assistant', 'system') and 'content'.
            max_tokens (int, optional): Max tokens in response (excludes input tokens).
            temperature (float, optional): Controls randomness in sampling.
            top_p (float, optional): Nucleus sampling parameter.
            top_k (int, optional): Top-K sampling limit.
            stop_sequences (List[str], optional): Tokens/phrases that stop generation.
            stream (bool): Return streaming iterator of partial responses.
            tools (List[ToolDefinition], optional): List of JSON schemas defining available functions.
            tool_choice (str | dict, optional): "auto", "none", or {"type": "function", "function": {"name": "..."}} to force tool use.
            **kwargs: Additional provider-specific options (e.g., presence_penalty, response_format).

        Returns:
            dict | TextStream: Full response object (with content, usage, tool_calls) or stream of partial dicts.
        """
        pass

    # =====================================================================
    # Streaming Convenience Wrappers
    # =====================================================================

    @abstractmethod
    def stream_text_generation(self, **kwargs) -> TextStream:
        """
        Convenience method: calls text_generation(..., stream=True).

        Args:
            **kwargs: Same as text_generation, but stream is forced to True.

        Returns:
            TextStream: Iterator yielding generated text chunks in real-time.
        """
        pass

    @abstractmethod
    def stream_chat_completion(self, **kwargs) -> TextStream:
        """
        Convenience method: calls chat_completion(..., stream=True).

        Args:
            **kwargs: Same as chat_completion, but stream is forced to True.

        Returns:
            TextStream: Iterator of partial response dicts (with delta content).
        """
        pass

    # =====================================================================
    # Async Variants
    # =====================================================================

    @abstractmethod
    async def atext_generation(self, **kwargs) -> Union[str, AsyncIterator[str]]:
        """
        Asynchronous version of text_generation.

        Args:
            **kwargs: Same as text_generation (including stream).

        Returns:
            str | AsyncIterator[str]: Full text or async stream of chunks.
        """
        pass

    @abstractmethod
    async def achat_completion(self, **kwargs) -> Union[Dict, AsyncIterator[Dict]]:
        """
        Asynchronous version of chat_completion.

        Args:
            **kwargs: Same as chat_completion.

        Returns:
            dict | AsyncIterator[dict]: Full response or stream of partial responses.
        """
        pass
    # =====================================================================
    # RAG: Retrieval & Augmentation Methods
    # =====================================================================

    @abstractmethod
    def retrieve_documents(
        self,
        query: str,
        *,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None,
        vector_store: Optional[Any] = None,
        **kwargs,
    ) -> RetrievalResult:
        """
        Retrieve relevant documents from the vector store.

        Args:
            query (str): Natural language or embedding query.
            top_k (int): Number of documents to return.
            filter (dict, optional): Metadata filter (e.g., {"source": "pdf"}).
            score_threshold (float, optional): Minimum similarity score.
            vector_store (Any, optional): Explicit vector store instance (if not injected).
            **kwargs: Embedding model, reranker, hybrid search params.

        Returns:
            List[Document]: Retrieved docs with content, metadata, and score.
        """
        pass

    @abstractmethod
    def rag_chat(
        self,
        messages: Messages,
        *,
        retrieval_top_k: int = 5,
        retrieval_filter: Optional[Dict] = None,
        context_template: str = "Context:\n{context}\n\nQuestion: {question}",
        include_sources: bool = True,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
        vector_store: Optional[Any] = None,
        **kwargs,
    ) -> Union[Dict[str, Any], TextStream]:
        """
        Perform RAG-augmented chat: retrieve → augment prompt → generate.

        Args:
            messages (Messages): Conversation history (last message = current query).
            retrieval_top_k (int): Number of docs to retrieve.
            retrieval_filter (dict, optional): Metadata filtering.
            context_template (str): Template to format retrieved context.
            include_sources (bool): Append source citations to response.
            max_tokens, temperature, stream: Generation controls.
            vector_store (Any, optional): Override default vector store.
            **kwargs: Reranking, compression, custom retrieval logic.

        Returns:
            dict | TextStream: Response with content + optional 'retrieved_docs' and 'sources'.
        """
        pass

    @abstractmethod
    def rag_generate(
        self,
        query: str,
        *,
        system_prompt: Optional[str] = None,
        retrieval_top_k: int = 5,
        context_template: str = "Use this context:\n{context}\n\nAnswer: {query}",
        include_sources: bool = True,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
        vector_store: Optional[Any] = None,
        **kwargs,
    ) -> Union[str, TextStream]:
        """
        RAG for single-turn generation (non-chat).

        Args:
            query (str): User question or prompt.
            system_prompt (str, optional): System instruction for generation.
            retrieval_top_k, context_template, include_sources: As in rag_chat.
            max_new_tokens, temperature, stream: Generation params.
            vector_store (Any, optional): Explicit store.
            **kwargs: Custom augmentation, citation format.

        Returns:
            str | TextStream: Generated answer with optional sources.
        """
        pass

    @abstractmethod
    def hybrid_search(
        self,
        query: str,
        *,
        keyword_weight: float = 0.5,
        semantic_weight: float = 0.5,
        top_k: int = 5,
        vector_store: Optional[Any] = None,
        **kwargs,
    ) -> RetrievalResult:
        """
        Combine keyword (BM25) and semantic search.

        Args:
            query (str): Search query.
            keyword_weight (float): Weight for sparse retrieval.
            semantic_weight (float): Weight for dense retrieval.
            top_k (int): Final results after fusion.
            vector_store (Any, optional): Store with hybrid support.
            **kwargs: Min score, boost fields.

        Returns:
            List[Document]: Fused results with hybrid scores.
        """
        pass

    @abstractmethod
    def rerank_documents(
        self,
        query: str,
        documents: RetrievalResult,
        *,
        top_k: Optional[int] = None,
        model: Optional[str] = None,
        **kwargs,
    ) -> RetrievalResult:
        """
        Rerank retrieved documents using a cross-encoder or LLM.

        Args:
            query (str): Original query.
            documents (List[Document]): Initial retrieval results.
            top_k (int, optional): Return only top N after reranking.
            model (str, optional): Reranker model ID.
            **kwargs: Batch size, normalization.

        Returns:
            List[Document]: Reranked with updated scores.
        """
        pass

    @abstractmethod
    def compress_context(
        self,
        documents: RetrievalResult,
        *,
        max_tokens: int = 3000,
        strategy: str = "summarize",  # "summarize" | "extract" | "truncate"
        **kwargs,
    ) -> str:
        """
        Compress retrieved documents to fit context window.

        Args:
            documents (List[Document]): Retrieved docs.
            max_tokens (int): Target token budget.
            strategy (str): Compression method.
            **kwargs: LLM for summarization, importance scoring.

        Returns:
            str: Compressed context string.
        """
        pass

    @abstractmethod
    def add_documents(
        self,
        documents: List[Union[str, Document]],
        *,
        metadata: Optional[List[Dict]] = None,
        vector_store: Optional[Any] = None,
        **kwargs,
    ) -> List[str]:
        """
        Index new documents into the vector store.

        Args:
            documents (List[str|Document]): Text or structured docs.
            metadata (List[dict], optional): Per-doc metadata.
            vector_store (Any, optional): Target store.
            **kwargs: Chunking strategy, embedding batch size.

        Returns:
            List[str]: Document IDs.
        """
        pass

    @abstractmethod
    def delete_documents(
        self,
        doc_ids: List[str],
        *,
        vector_store: Optional[Any] = None,
        **kwargs,
    ) -> bool:
        """
        Remove documents from the index.

        Args:
            doc_ids (List[str]): IDs to delete.
            vector_store (Any, optional): Target store.
            **kwargs: Namespace, filter.

        Returns:
            bool: Success.
        """
        pass

    @abstractmethod
    def query_vector_store(
        self,
        query: str,
        *,
        mode: str = "similarity",  # "similarity" | "mmr" | "metadata"
        vector_store: Optional[Any] = None,
        **kwargs,
    ) -> RetrievalResult:
        """
        Low-level vector store query with advanced modes.

        Args:
            query (str): Query text.
            mode (str): Retrieval strategy.
            vector_store (Any, optional): Store instance.
            **kwargs: Diversity (MMR), lambda, filters.

        Returns:
            List[Document]: Results.
        """
        pass

    # =====================================================================
    # RAG Evaluation & Feedback
    # =====================================================================

    @abstractmethod
    def evaluate_retrieval(
        self,
        query: str,
        ground_truth: List[str],
        *,
        metrics: List[str] = None,  # e.g., ["recall", "precision", "mrr"]
        vector_store: Optional[Any] = None,
        **kwargs,
    ) -> Dict[str, float]:
        """
        Evaluate retrieval quality against ground truth.

        Args:
            query (str): Test query.
            ground_truth (List[str]): Relevant doc IDs or content.
            metrics (List[str], optional): Metrics to compute.
            vector_store (Any, optional): Store to test.
            **kwargs: Top-k per metric.

        Returns:
            dict: {metric: score}
        """
        pass

    @abstractmethod
    def log_rag_interaction(
        self,
        query: str,
        retrieved_docs: RetrievalResult,
        response: str,
        *,
        user_feedback: Optional[float] = None,  # e.g., thumbs up/down
        session_id: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Log full RAG flow for analytics and improvement.

        Args:
            query, retrieved_docs, response: RAG components.
            user_feedback (float, optional): Explicit rating.
            session_id (str, optional): Trace interaction.
            **kwargs: Latency, cost, citations_used.
        """
        pass
    # =====================================================================
    # Specialized NLP Tasks
    # =====================================================================

    @abstractmethod
    def summarization(
        self,
        text: str,
        *,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None,
        length_penalty: Optional[float] = None,
        **kwargs,
    ) -> str:
        """
        Generate a concise summary of the input text.

        Args:
            text (str): Input document or passage to summarize.
            max_length (int, optional): Maximum length of summary in tokens/words.
            min_length (int, optional): Minimum length of summary.
            length_penalty (float, optional): >1.0 favors longer, <1.0 favors shorter summaries.
            **kwargs: Additional controls (e.g., summary style: "bullet", "paragraph").

        Returns:
            str: Summary text.
        """
        pass

    @abstractmethod
    def translation(
        self,
        text: str,
        source_lang: Optional[str] = None,
        target_lang: str = "en",
        **kwargs,
    ) -> str:
        """
        Translate text from source to target language.

        Args:
            text (str): Text to translate.
            source_lang (str, optional): ISO 639-1 code (e.g., "fr"). If None, auto-detect.
            target_lang (str): Target language code (default: "en").
            **kwargs: Style preferences (e.g., formal/informal).

        Returns:
            str: Translated text.
        """
        pass

    @abstractmethod
    def zero_shot_classification(
        self,
        text: str,
        candidate_labels: List[str],
        *,
        multi_label: bool = False,
        **kwargs,
    ) -> List[Dict[str, float]]:
        """
        Classify text into arbitrary labels without prior training.

        Args:
            text (str): Input to classify.
            candidate_labels (List[str]): Possible labels (e.g., ["positive", "negative"]).
            multi_label (bool): If True, allows multiple labels per input.
            **kwargs: Hypothesis template (e.g., "This example is {}").

        Returns:
            List[Dict]: [{'label': str, 'score': float}], sorted by score.
        """
        pass

    @abstractmethod
    def question_answering(
        self,
        question: str,
        context: str,
        **kwargs,
    ) -> str:
        """
        Answer a question given a context passage (extractive or generative).

        Args:
            question (str): The question to answer.
            context (str): Passage containing relevant information.
            **kwargs: Options like top_k, doc_stride.

        Returns:
            str: Answer text.
        """
        pass

    @abstractmethod
    def sentiment_analysis(
        self,
        text: str,
        **kwargs,
    ) -> Dict[str, float]:
        """
        Analyze emotional tone of text.

        Args:
            text (str): Input text.
            **kwargs: Granularity (sentence-level vs document).

        Returns:
            dict: {'positive': float, 'negative': float, 'neutral': float}
        """
        pass

    @abstractmethod
    def named_entity_recognition(
        self,
        text: str,
        *,
        aggregation_strategy: str = "simple",
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Identify named entities in text.

        Args:
            text (str): Input text.
            aggregation_strategy (str): "simple", "first", "average", "max" for subword tokens.
            **kwargs: Entity groups to return.

        Returns:
            List[Dict]: [{'entity': 'PERSON', 'score': 0.99, 'word': 'John', 'start': 0, 'end': 4}, ...]
        """
        pass

    @abstractmethod
    def paraphrasing(
        self,
        text: str,
        *,
        style: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Rephrase text while preserving meaning.

        Args:
            text (str): Original text.
            style (str, optional): Target style ("formal", "casual", "shakespearean").
            **kwargs: Diversity level, length control.

        Returns:
            str: Paraphrased text.
        """
        pass

    @abstractmethod
    def text_correction(
        self,
        text: str,
         **kwargs,
    ) -> str:
        """
        Correct grammar, spelling, punctuation, and style.

        Args:
            text (str): Input with potential errors.
            **kwargs: Language variant ("en-US", "en-GB"), formality level.

        Returns:
            str: Corrected and polished text.
        """
        pass

    # =====================================================================
    # Multimodal Methods
    # =====================================================================

    @abstractmethod
    def text_to_speech(
        self,
        text: str,
        *,
        voice: Optional[str] = None,
        speed: Optional[float] = None,
        format: str = "mp3",
        **kwargs,
    ) -> Union[bytes, io.BytesIO]:
        """
        Synthesize speech from text.

        Args:
            text (str): Text to speak.
            voice (str, optional): Voice ID or name (e.g., "en_us_001").
            speed (float, optional): Playback speed (0.5 = slow, 2.0 = fast).
            format (str): Audio format ("mp3", "wav", "ogg").
            **kwargs: Emotion, pitch, SSML support.

        Returns:
            bytes | BytesIO: Raw audio data.
        """
        pass

    @abstractmethod
    def visual_question_answering(
        self,
        image: Union[Image, bytes, str],
        question: str,
        **kwargs,
    ) -> str:
        """
        Answer natural language question about an image.

        Args:
            image (PIL.Image | bytes | str): Image as PIL, bytes, file path, or URL.
            question (str): Question about the image.
            **kwargs: Model-specific options.

        Returns:
            str: Answer text.
        """
        pass

    @abstractmethod
    def image_captioning(
        self,
        image: Union[Image, bytes, str],
        **kwargs,
    ) -> str:
        """
        Generate descriptive caption for an image.

        Args:
            image (PIL.Image | bytes | str): Input image.
            **kwargs: Caption length, style.

        Returns:
            str: Natural language description.
        """
        pass

    @abstractmethod
    def image_generation(
        self,
        prompt: str,
        *,
        size: str = "1024x1024",
        quality: str = "standard",
        **kwargs,
    ) -> Union[Image, bytes]:
        """
        Generate image from text prompt (if supported by provider).

        Args:
            prompt (str): Text description of desired image.
            size (str): Resolution (e.g., "512x512", "1024x768").
            quality (str): "standard", "hd".
            **kwargs: Style, negative_prompt, steps.

        Returns:
            PIL.Image | bytes: Generated image.
        """
        pass

    # =====================================================================
    # Embeddings
    # =====================================================================

    @abstractmethod
    def embed_text(
        self,
        texts: Union[str, List[str]],
        *,
        normalize: bool = True,
        **kwargs,
    ) -> List[List[float]]:
        """
        Generate dense vector embeddings for text.

        Args:
            texts (str | List[str]): Single string or batch.
            normalize (bool): L2-normalize vectors.
            **kwargs: Embedding type, truncation.

        Returns:
            List[List[float]]: List of embedding vectors.
        """
        pass

    @abstractmethod
    def embed_image(
        self,
        images: Union[Image, bytes, str, List[Union[Image, bytes, str]]],
        **kwargs,
    ) -> List[List[float]]:
        """
        Generate embeddings for images.

        Args:
            images: Single or batch of images (PIL, bytes, path, URL).
            **kwargs: Resize, normalization.

        Returns:
            List[List[float]]: Image embedding vectors.
        """
        pass

    # =====================================================================
    # Tool Execution
    # =====================================================================

    @abstractmethod
    def call_tool(
        self,
        tool_call: ToolCall,
        available_tools: Dict[str, callable],
    ) -> Any:
        """
        Execute a function/tool requested by the LLM.

        Args:
            tool_call (dict): {"name": str, "arguments": dict} from LLM output.
            available_tools (Dict[str, callable]): Mapping of tool names to Python functions.

        Returns:
            Any: Result of the tool execution.
        """
        pass

    # =====================================================================
    # Conversation Management
    # =====================================================================

    @abstractmethod
    def start_conversation(self) -> Any:
        """
        Initialize a new conversation session.

        Returns:
            Any: Conversation object or ID for state tracking.
        """
        pass

    @abstractmethod
    def continue_conversation(self, conversation: Any, user_message: str) -> str:
        """
        Append user message and get assistant response in ongoing conversation.

        Args:
            conversation (Any): Object returned by start_conversation().
            user_message (str): New user input.

        Returns:
            str: Assistant's reply.
        """
        pass

    # =====================================================================
    # Token & Model Utilities
    # =====================================================================

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using the model's tokenizer.

        Args:
            text (str): Input text.

        Returns:
            int: Number of tokens.
        """
        pass

    @abstractmethod
    def truncate_to_max_tokens(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to fit within token limit.

        Args:
            text (str): Input.
            max_tokens (int): Maximum allowed tokens.

        Returns:
            str: Truncated text.
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retrieve metadata about the current model.

        Returns:
            dict: Keys like 'context_length', 'modalities', 'provider', 'pricing'.
        """
        pass

    # =====================================================================
    # Observability
    # =====================================================================

    @abstractmethod
    def log_request(
        self,
        method: str,
        input_data: Any,
        response: Any,
        latency_ms: float,
        **metadata,
    ) -> None:
        """
        Log inference call for monitoring, debugging, or analytics.

        Args:
            method (str): Name of called method.
            input_data (Any): Input prompt/messages.
            response (Any): Output from LLM.
            latency_ms (float): Request duration.
            **metadata: user_id, session_id, cost, etc.
        """
        pass

    # =====================================================================
    # Utilities
    # =====================================================================

    @abstractmethod
    def format_messages(self, messages: Messages) -> str:
        """
        Convert structured messages to single prompt string (for non-chat models).

        Args:
            messages (Messages): Role-based message list.

        Returns:
            str: Formatted prompt.
        """
        pass

    @abstractmethod
    def parse_tool_calls(self, response: Dict) -> List[ToolCall]:
        """
        Extract structured tool calls from raw LLM response.

        Args:
            response (dict): Full LLM output.

        Returns:
            List[ToolCall]: Parsed tool requests.
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Verify LLM service is reachable and responsive.

        Returns:
            bool: True if healthy.
        """
        pass