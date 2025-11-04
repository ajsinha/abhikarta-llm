"""
RAG (Retrieval Augmented Generation)

System for answering questions using retrieved context from knowledge bases.

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re


@dataclass
class Document:
    """Represents a document in the knowledge base"""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'content': self.content,
            'metadata': self.metadata,
            'source': self.source,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class RetrievalResult:
    """Result from document retrieval"""
    document: Document
    score: float
    rank: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'document': self.document.to_dict(),
            'score': self.score,
            'rank': self.rank
        }


@dataclass
class RAGResponse:
    """Response from RAG system"""
    answer: str
    sources: List[RetrievalResult]
    query: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def format_with_citations(self) -> str:
        """Format answer with citations"""
        answer = self.answer
        
        # Add citations at the end
        citations = "\n\nSources:\n"
        for result in self.sources:
            doc = result.document
            source_name = doc.source or doc.id
            citations += f"[{result.rank}] {source_name} (relevance: {result.score:.2f})\n"
        
        return answer + citations


class RAGClient:
    """
    RAG client for question answering with retrieved context.
    
    Combines vector search with LLM generation for grounded responses.
    """
    
    def __init__(
        self,
        llm_client: Any,
        vector_store: Any,
        top_k: int = 3,
        relevance_threshold: float = 0.7
    ):
        """
        Initialize RAG client.
        
        Args:
            llm_client: LLM client for generation
            vector_store: Vector store for retrieval
            top_k: Number of documents to retrieve
            relevance_threshold: Minimum relevance score
        """
        self.llm_client = llm_client
        self.vector_store = vector_store
        self.top_k = top_k
        self.relevance_threshold = relevance_threshold
        self.query_history: List[Dict[str, Any]] = []
    
    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        include_citations: bool = True,
        **llm_kwargs
    ) -> RAGResponse:
        """
        Answer question using RAG.
        
        Args:
            question: User question
            top_k: Number of documents to retrieve (uses default if None)
            include_citations: Whether to include citations in answer
            **llm_kwargs: Additional arguments for LLM
            
        Returns:
            RAGResponse with answer and sources
        """
        k = top_k or self.top_k
        
        # Retrieve relevant documents
        results = self.vector_store.search(
            question,
            top_k=k,
            threshold=self.relevance_threshold
        )
        
        # Convert to RetrievalResult objects
        retrieval_results = []
        for i, result in enumerate(results):
            doc = Document(
                id=result['metadata'].get('doc_id', f'doc_{i}'),
                content=result['text'],
                metadata=result['metadata'],
                source=result['metadata'].get('source')
            )
            retrieval_results.append(RetrievalResult(
                document=doc,
                score=result['similarity'],
                rank=i + 1
            ))
        
        # Build context from retrieved documents
        context = self._build_context(retrieval_results, include_citations)
        
        # Generate answer
        prompt = self._build_prompt(question, context, include_citations)
        
        # Get LLM response
        if hasattr(self.llm_client, 'complete'):
            answer = self.llm_client.complete(prompt, **llm_kwargs)
        else:
            # Assume it's a facade
            response = self.llm_client.complete(prompt, **llm_kwargs)
            answer = response.text if hasattr(response, 'text') else str(response)
        
        # Create response
        rag_response = RAGResponse(
            answer=answer,
            sources=retrieval_results,
            query=question,
            metadata={
                'context_length': len(context),
                'num_sources': len(retrieval_results)
            }
        )
        
        # Log query
        self.query_history.append({
            'question': question,
            'answer': answer,
            'num_sources': len(retrieval_results),
            'timestamp': datetime.now()
        })
        
        return rag_response
    
    def _build_context(
        self,
        results: List[RetrievalResult],
        include_citations: bool
    ) -> str:
        """Build context string from retrieval results"""
        context_parts = []
        
        for result in results:
            doc = result.document
            
            if include_citations:
                source_id = f"[{result.rank}]"
                context_parts.append(f"{source_id} {doc.content}")
            else:
                context_parts.append(doc.content)
        
        return "\n\n".join(context_parts)
    
    def _build_prompt(
        self,
        question: str,
        context: str,
        include_citations: bool
    ) -> str:
        """Build prompt for LLM"""
        if include_citations:
            prompt = f"""Answer the following question based on the provided context. Include citations using [1], [2], etc. when referencing specific information.

Context:
{context}

Question: {question}

Answer (with citations):"""
        else:
            prompt = f"""Answer the following question based on the provided context.

Context:
{context}

Question: {question}

Answer:"""
        
        return prompt
    
    def query_with_streaming(
        self,
        question: str,
        top_k: Optional[int] = None,
        **llm_kwargs
    ):
        """
        Answer question with streaming response.
        
        Args:
            question: User question
            top_k: Number of documents to retrieve
            **llm_kwargs: Additional arguments for LLM
            
        Yields:
            Response tokens
        """
        k = top_k or self.top_k
        
        # Retrieve documents
        results = self.vector_store.search(question, top_k=k)
        
        # Build context
        retrieval_results = []
        for i, result in enumerate(results):
            doc = Document(
                id=result['metadata'].get('doc_id', f'doc_{i}'),
                content=result['text'],
                metadata=result['metadata']
            )
            retrieval_results.append(RetrievalResult(
                document=doc,
                score=result['similarity'],
                rank=i + 1
            ))
        
        context = self._build_context(retrieval_results, include_citations=True)
        prompt = self._build_prompt(question, context, include_citations=True)
        
        # Stream response
        if hasattr(self.llm_client, 'stream_complete'):
            for token in self.llm_client.stream_complete(prompt, **llm_kwargs):
                yield token
        else:
            # Fallback to non-streaming
            response = self.llm_client.complete(prompt, **llm_kwargs)
            yield response
    
    def get_query_history(self) -> List[Dict[str, Any]]:
        """Get query history"""
        return self.query_history.copy()
    
    def clear_history(self) -> None:
        """Clear query history"""
        self.query_history.clear()


class ConversationalRAG:
    """RAG with conversation history"""
    
    def __init__(
        self,
        llm_client: Any,
        vector_store: Any,
        top_k: int = 3
    ):
        self.rag_client = RAGClient(llm_client, vector_store, top_k)
        self.conversation_history: List[Dict[str, str]] = []
    
    def query(
        self,
        question: str,
        **kwargs
    ) -> RAGResponse:
        """Query with conversation context"""
        # Build context-aware question
        if self.conversation_history:
            context_question = self._build_contextual_question(question)
        else:
            context_question = question
        
        # Get RAG response
        response = self.rag_client.query(context_question, **kwargs)
        
        # Update conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': question
        })
        self.conversation_history.append({
            'role': 'assistant',
            'content': response.answer
        })
        
        return response
    
    def _build_contextual_question(self, question: str) -> str:
        """Build question with conversation context"""
        recent_history = self.conversation_history[-4:]  # Last 2 turns
        
        context = "Previous conversation:\n"
        for msg in recent_history:
            role = msg['role'].title()
            context += f"{role}: {msg['content']}\n"
        
        return f"{context}\nCurrent question: {question}"
    
    def reset_conversation(self) -> None:
        """Reset conversation history"""
        self.conversation_history.clear()


class DocumentChunker:
    """Split documents into chunks for embedding"""
    
    @staticmethod
    def chunk_by_tokens(
        text: str,
        chunk_size: int = 512,
        overlap: int = 50
    ) -> List[str]:
        """
        Chunk text by token count.
        
        Args:
            text: Input text
            chunk_size: Target chunk size in tokens (approx)
            overlap: Number of overlapping tokens
            
        Returns:
            List of text chunks
        """
        # Approximate: 1 token ≈ 4 characters
        char_chunk_size = chunk_size * 4
        char_overlap = overlap * 4
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + char_chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > char_chunk_size // 2:
                    chunk = chunk[:last_period + 1]
                    end = start + last_period + 1
            
            chunks.append(chunk.strip())
            start = end - char_overlap
        
        return [c for c in chunks if c]  # Remove empty chunks
    
    @staticmethod
    def chunk_by_sentences(
        text: str,
        sentences_per_chunk: int = 5
    ) -> List[str]:
        """Chunk text by sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        for i in range(0, len(sentences), sentences_per_chunk):
            chunk = ' '.join(sentences[i:i + sentences_per_chunk])
            chunks.append(chunk)
        
        return chunks
    
    @staticmethod
    def chunk_by_paragraphs(text: str) -> List[str]:
        """Chunk text by paragraphs"""
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]


def build_knowledge_base(
    documents: List[str],
    embedding_client: Any,
    chunk_size: int = 512,
    metadatas: Optional[List[Dict[str, Any]]] = None
) -> Any:
    """
    Build a knowledge base from documents.
    
    Args:
        documents: List of document texts
        embedding_client: Embedding client
        chunk_size: Chunk size for splitting
        metadatas: Optional metadata for each document
        
    Returns:
        VectorStore with indexed documents
    """
    from ..embeddings import VectorStore
    
    vector_store = VectorStore(embedding_client)
    chunker = DocumentChunker()
    
    all_chunks = []
    all_metadatas = []
    
    for i, doc in enumerate(documents):
        chunks = chunker.chunk_by_tokens(doc, chunk_size=chunk_size)
        
        for j, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            
            chunk_metadata = {
                'doc_id': i,
                'chunk_id': j,
                'source': f'doc_{i}'
            }
            
            if metadatas and i < len(metadatas):
                chunk_metadata.update(metadatas[i])
            
            all_metadatas.append(chunk_metadata)
    
    # Add all chunks to vector store
    vector_store.add_batch(all_chunks, all_metadatas)
    
    return vector_store
