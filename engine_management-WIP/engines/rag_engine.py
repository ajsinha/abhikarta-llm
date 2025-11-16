"""
Abhikarta LLM Platform - rag_engine.py
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

Legal Notice:
This module and the associated software architecture are proprietary and confidential.
"""

from .base_engine import BaseExecutionEngine
from typing import Dict, Any, List
import json
import uuid

class RAGEngine(BaseExecutionEngine):
    """Retrieval-Augmented Generation execution"""
    
    def get_mode_name(self) -> str:
        return "rag"
    
    async def execute(
        self,
        query: str,
        collection_id: str,
        top_k: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute RAG query"""
        self.create_session_record()
        self.update_session_status("running")
        
        try:
            # Retrieve relevant documents
            retrieval_id = str(uuid.uuid4())
            
            documents = await self.vector_store.similarity_search(
                query=query,
                k=top_k,
                **kwargs
            )
            
            # Save retrieval
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO rag_retrievals (
                        retrieval_id, session_id, collection_id,
                        query_text, top_k, retrieved_documents
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    retrieval_id,
                    self.session_id,
                    collection_id,
                    query,
                    top_k,
                    json.dumps([{
                        "content": doc[0].get("content", ""),
                        "metadata": doc[0].get("metadata", {}),
                        "score": doc[1]
                    } for doc in documents])
                ))
                conn.commit()
            
            # Build context from retrieved documents
            context = "\n\n".join([
                f"Document {i+1}:\n{doc[0].get('content', '')}"
                for i, doc in enumerate(documents)
            ])
            
            # Build augmented prompt
            augmented_prompt = f"""
Context:
{context}

Question: {query}

Answer based on the provided context:
"""
            
            # Generate answer
            response = await self.llm_facade.chat_completion_async(
                messages=[{"role": "user", "content": augmented_prompt}],
                **self.config.get("llm_params", {})
            )
            
            # Save interaction
            self.save_interaction("user", query)
            self.save_interaction("assistant", response["content"])
            
            self.update_session_status("completed")
            
            return {
                "success": True,
                "answer": response["content"],
                "retrieved_documents": len(documents),
                "session_id": self.session_id
            }
            
        except Exception as e:
            self.update_session_status("failed", str(e))
            return {
                "success": False,
                "error": str(e),
                "session_id": self.session_id
            }
