from typing import Any, Dict, List, Optional, Union, Iterator, AsyncIterator, Tuple
from huggingface_hub import InferenceClient
from PIL.Image import Image
import io
import json
import time

# Reuse type aliases from previous context
Messages = List[Dict[str, str]]
TextStream = Union[Iterator[str], AsyncIterator[str]]
ToolDefinition = Dict[str, Any]
ToolCall = Dict[str, Any]
Document = Dict[str, Any]
RetrievalResult = List[Tuple[Document, float]]

# Import base class
from llm_model_facade_base import LLMModelBase  # Assuming saved from prior


class HuggingFaceLLMModel(LLMModelBase):
    """
    Concrete implementation of LLMFacadeBase using Hugging Face Inference API.
    Supports hosted models via InferenceClient and local TGI servers.
    """

    def __init__(
        self,
        model: str,
        token: Optional[str] = None,
        provider: Optional[str] = None,
        timeout: float = 60.0,
        **kwargs,
    ):
        """
        Initialize with model ID and optional provider override.
        """
        self.model = model
        self.client = InferenceClient(model=model, token=token, provider=provider, timeout=timeout, **kwargs)
        self._model_info = None

    # =====================================================================
    # Core Text Generation
    # =====================================================================

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
        start_time = time.time()
        try:
            response = self.client.text_generation(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                stop_sequences=stop_sequences,
                repetition_penalty=repetition_penalty,
                stream=stream,
                **kwargs,
            )
            latency_ms = (time.time() - start_time) * 1000
            self.log_request("text_generation", prompt, response, latency_ms)
            return response
        except Exception as e:
            self.log_request("text_generation", prompt, str(e), (time.time() - start_time) * 1000, error=True)
            raise

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
        start_time = time.time()
        try:
            response = self.client.chat_completion(
                messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                stop_sequences=stop_sequences,
                stream=stream,
                tools=tools,
                tool_choice=tool_choice,
                **kwargs,
            )
            latency_ms = (time.time() - start_time) * 1000
            self.log_request("chat_completion", messages, response, latency_ms)
            return response
        except Exception as e:
            self.log_request("chat_completion", messages, str(e), (time.time() - start_time) * 1000, error=True)
            raise

    # =====================================================================
    # Streaming Wrappers
    # =====================================================================

    def stream_text_generation(self, **kwargs) -> TextStream:
        kwargs["stream"] = True
        return self.text_generation(**kwargs)

    def stream_chat_completion(self, **kwargs) -> TextStream:
        kwargs["stream"] = True
        return self.chat_completion(**kwargs)

    # =====================================================================
    # Async Variants
    # =====================================================================

    async def atext_generation(self, **kwargs) -> Union[str, AsyncIterator[str]]:
        return await self.client.atext_generation(**kwargs)

    async def achat_completion(self, **kwargs) -> Union[Dict, AsyncIterator[Dict]]:
        return await self.client.achat_completion(**kwargs)

    # =====================================================================
    # Specialized NLP Tasks
    # =====================================================================

    def summarization(self, text: str, *, max_length: Optional[int] = None, min_length: Optional[int] = None, **kwargs) -> str:
        return self.client.summarization(text, max_length=max_length, min_length=min_length, **kwargs)

    def translation(self, text: str, source_lang: Optional[str] = None, target_lang: str = "en", **kwargs) -> str:
        return self.client.translation(text, source_lang=source_lang, target_lang=target_lang, **kwargs)

    def zero_shot_classification(self, text: str, candidate_labels: List[str], *, multi_label: bool = False, **kwargs) -> List[Dict[str, float]]:
        return self.client.zero_shot_classification(text, candidate_labels, multi_label=multi_label, **kwargs)

    def question_answering(self, question: str, context: str, **kwargs) -> str:
        return self.client.question_answering(question=question, context=context, **kwargs)

    def sentiment_analysis(self, text: str, **kwargs) -> Dict[str, float]:
        return self.client.sentiment_analysis(text, **kwargs)

    def named_entity_recognition(self, text: str, *, aggregation_strategy: str = "simple", **kwargs) -> List[Dict[str, Any]]:
        return self.client.token_classification(text, aggregation_strategy=aggregation_strategy, **kwargs)

    def paraphrasing(self, text: str, *, style: Optional[str] = None, **kwargs) -> str:
        prompt = f"Paraphrase: {text}"
        if style:
            prompt = f"Paraphrase in {style} style: {text}"
        return self.text_generation(prompt, **kwargs)

    def text_correction(self, text: str, **kwargs) -> str:
        prompt = f"Correct grammar and spelling: {text}"
        return self.text_generation(prompt, **kwargs)

    # =====================================================================
    # Multimodal
    # =====================================================================

    def text_to_speech(self, text: str, *, voice: Optional[str] = None, speed: Optional[float] = None, format: str = "mp3", **kwargs) -> Union[bytes, io.BytesIO]:
        return self.client.text_to_speech(text, voice=voice, speed=speed, format=format, **kwargs)

    def visual_question_answering(self, image: Union[Image, bytes, str], question: str, **kwargs) -> str:
        return self.client.visual_question_answering(image=image, question=question, **kwargs)

    def image_captioning(self, image: Union[Image, bytes, str], **kwargs) -> str:
        return self.client.image_captioning(image=image, **kwargs)

    def image_generation(self, prompt: str, *, size: str = "1024x1024", quality: str = "standard", **kwargs) -> Union[Image, bytes]:
        return self.client.image_generation(prompt, size=size, quality=quality, **kwargs)

    # =====================================================================
    # Embeddings
    # =====================================================================

    def embed_text(self, texts: Union[str, List[str]], *, normalize: bool = True, **kwargs) -> List[List[float]]:
        return self.client.feature_extraction(texts, normalize=normalize, **kwargs)

    def embed_image(self, images: Union[Image, bytes, str, List[Union[Image, bytes, str]]], **kwargs) -> List[List[float]]:
        return self.client.image_to_text(images, **kwargs)  # Placeholder; use vision encoder if available

    # =====================================================================
    # Tool Calling
    # =====================================================================

    def call_tool(self, tool_call: ToolCall, available_tools: Dict[str, callable]) -> Any:
        name = tool_call.get("name")
        args = tool_call.get("arguments", {})
        if name not in available_tools:
            raise ValueError(f"Tool {name} not found")
        return available_tools[name](**args)

    # =====================================================================
    # Conversation Management
    # =====================================================================

    def start_conversation(self) -> List[Dict[str, str]]:
        return []

    def continue_conversation(self, conversation: List[Dict[str, str]], user_message: str) -> str:
        conversation.append({"role": "user", "content": user_message})
        response = self.chat_completion(conversation)
        assistant_msg = response.choices[0].message.content
        conversation.append({"role": "assistant", "content": assistant_msg})
        return assistant_msg

    # =====================================================================
    # Token & Model Utilities
    # =====================================================================

    def count_tokens(self, text: str) -> int:
        return len(self.client.tokenizer.encode(text))

    def truncate_to_max_tokens(self, text: str, max_tokens: int) -> str:
        tokens = self.client.tokenizer.encode(text)
        if len(tokens) <= max_tokens:
            return text
        return self.client.tokenizer.decode(tokens[:max_tokens])

    def get_model_info(self) -> Dict[str, Any]:
        if self._model_info is None:
            try:
                info = self.client.model_info()
                self._model_info = {
                    "model_id": info.id,
                    "context_length": getattr(info, "max_model_len", None),
                    "modalities": ["text"],
                    "provider": "huggingface",
                }
            except:
                self._model_info = {"model_id": self.model, "provider": "huggingface"}
        return self._model_info

    # =====================================================================
    # RAG Methods (requires external VectorStore)
    # =====================================================================

    def retrieve_documents(self, query: str, *, top_k: int = 5, filter: Optional[Dict[str, Any]] = None, vector_store: Optional[Any] = None, **kwargs) -> RetrievalResult:
        if vector_store is None:
            raise ValueError("vector_store is required for RAG")
        embedding = self.embed_text(query)[0]
        return vector_store.similarity_search(embedding, k=top_k, filter=filter)

    def rag_chat(
        self,
        messages: Messages,
        *,
        retrieval_top_k: int = 5,
        context_template: str = "Context:\n{context}\n\nQuestion: {question}",
        include_sources: bool = True,
        vector_store: Optional[Any] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        if vector_store is None:
            raise ValueError("vector_store required")
        query = messages[-1]["content"]
        docs = self.retrieve_documents(query, top_k=retrieval_top_k, vector_store=vector_store)
        context = "\n\n".join([d[0]["content"] for d in docs])
        augmented = context_template.format(context=context, question=query)
        messages[-1]["content"] = augmented
        response = self.chat_completion(messages, **kwargs)
        if include_sources:
            response["retrieved_sources"] = [d[0].get("metadata", {}) for d in docs]
        return response

    def rag_generate(self, query: str, *, retrieval_top_k: int = 5, context_template: str = "Use this context:\n{context}\n\nAnswer: {query}", vector_store: Optional[Any] = None, **kwargs) -> str:
        if vector_store is None:
            raise ValueError("vector_store required")
        docs = self.retrieve_documents(query, top_k=retrieval_top_k, vector_store=vector_store)
        context = "\n\n".join([d[0]["content"] for d in docs])
        prompt = context_template.format(context=context, query=query)
        return self.text_generation(prompt, **kwargs)

    def hybrid_search(self, query: str, *, k: int = 5, alpha: float = 0.5, vector_store: Optional[Any] = None, **kwargs) -> RetrievalResult:
        if vector_store is None or not hasattr(vector_store, "hybrid_search"):
            raise NotImplementedError("Hybrid search not supported")
        return vector_store.hybrid_search(query, k=k, alpha=alpha, **kwargs)

    def rerank_documents(self, query: str, documents: RetrievalResult, *, top_k: Optional[int] = None, **kwargs) -> RetrievalResult:
        # Simple heuristic reranking using LLM
        prompt = "Rank these passages by relevance to: '{}'\n\n".format(query)
        for i, (doc, _) in enumerate(documents):
            prompt += f"{i+1}. {doc['content'][:500]}\n\n"
        prompt += "Return ranked indices (1-based) as JSON list:"
        response = self.text_generation(prompt, **kwargs)
        try:
            indices = json.loads(response)
            reranked = [documents[i-1] for i in indices if 1 <= i <= len(documents)]
            return reranked[:top_k] if top_k else reranked
        except:
            return documents[:top_k] if top_k else documents

    def compress_context(self, documents: RetrievalResult, *, max_tokens: int = 3000, **kwargs) -> str:
        texts = [d[0]["content"] for d in documents]
        combined = "\n\n".join(texts)
        if self.count_tokens(combined) <= max_tokens:
            return combined
        return self.summarization(combined, max_length=max_tokens//4, **kwargs)

    def add_documents(self, documents: List[Union[str, Document]], *, vector_store: Optional[Any] = None, **kwargs) -> List[str]:
        if vector_store is None:
            raise ValueError("vector_store required")
        docs = [{"content": d if isinstance(d, str) else d["content"], "metadata": d.get("metadata", {}) if isinstance(d, dict) else {}} for d in documents]
        return vector_store.add_documents(docs, **kwargs)

    def delete_documents(self, doc_ids: List[str], *, vector_store: Optional[Any] = None, **kwargs) -> bool:
        if vector_store is None:
            raise ValueError("vector_store required")
        return vector_store.delete_documents(doc_ids, **kwargs)

    def query_vector_store(self, query: str, *, mode: str = "similarity", vector_store: Optional[Any] = None, **kwargs) -> RetrievalResult:
        if vector_store is None:
            raise ValueError("vector_store required")
        if mode == "mmr":
            return vector_store.max_marginal_relevance_search(query, **kwargs)
        return vector_store.similarity_search(query, **kwargs)

    def evaluate_retrieval(self, query: str, ground_truth: List[str], *, metrics: List[str] = None, vector_store: Optional[Any] = None, **kwargs) -> Dict[str, float]:
        # Simplified evaluation
        results = self.retrieve_documents(query, top_k=10, vector_store=vector_store)
        retrieved = [d[0]["id"] for d in results]
        metrics = metrics or ["recall@5", "mrr"]
        eval_result = {}
        if "recall@5" in metrics:
            top5 = set(retrieved[:5])
            eval_result["recall@5"] = len(top5.intersection(ground_truth)) / len(ground_truth)
        if "mrr" in metrics:
            for i, doc_id in enumerate(retrieved):
                if doc_id in ground_truth:
                    eval_result["mrr"] = 1.0 / (i + 1)
                    break
            else:
                eval_result["mrr"] = 0.0
        return eval_result

    def log_rag_interaction(self, query: str, retrieved_docs: RetrievalResult, response: str, **kwargs) -> None:
        print(f"[RAG LOG] Query: {query[:50]}... | Docs: {len(retrieved_docs)} | Response: {response[:50]}...")

    # =====================================================================
    # Observability & Utilities
    # =====================================================================

    def log_request(self, method: str, input_data: Any, response: Any, latency_ms: float, **metadata) -> None:
        print(f"[HF LOG] {method} | Latency: {latency_ms:.2f}ms | Input: {str(input_data)[:100]}...")

    def format_messages(self, messages: Messages) -> str:
        return "\n".join([f"{m['role'].title()}: {m['content']}" for m in messages])

    def parse_tool_calls(self, response: Dict) -> List[ToolCall]:
        return response.get("tool_calls", []) if isinstance(response, dict) else []

    def health_check(self) -> bool:
        try:
            self.client.model_info()
            return True
        except:
            return False

if __name__ == '__main__':
    # Setup
    from vector_store.faiss_vector_store import FAISSVectorStore  # From previous

    llm = HuggingFaceLLMModel(model="meta-llama/Meta-Llama-3.1-8B-Instruct", token="hf_...")
    vector_store = FAISSVectorStore(embedding_dim=384)

    # Index docs
    docs = [{"content": "Paris is the capital of France.", "metadata": {"source": "wiki"}}]
    vector_store.add_documents(docs, embeddings=llm.embed_text([d["content"] for d in docs]))

    # RAG Query
    response = llm.rag_chat(
        messages=[{"role": "user", "content": "What is the capital of France?"}],
        vector_store=vector_store
    )
    print(response.choices[0].message.content)