"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.4

Document Processor - High-level document processing
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from .loaders import auto_load, get_file_info


class DocumentProcessor:
    """
    High-level document processor with LLM integration.
    
    Example:
        processor = DocumentProcessor()
        text = processor.load("document.pdf")
        summary = processor.process_with_llm(text, facade, "Summarize this")
    """
    
    def __init__(self):
        self.loaded_documents = {}
    
    def load(self, filepath: str, **kwargs) -> str:
        """
        Load document and return text content.
        
        Args:
            filepath: Path to document
            **kwargs: Additional arguments for loader
        
        Returns:
            Document text content
        """
        content = auto_load(filepath, **kwargs)
        
        # Convert to string if needed
        if isinstance(content, (dict, list)):
            import json
            content = json.dumps(content, indent=2)
        
        # Store for later reference
        self.loaded_documents[filepath] = content
        
        return content
    
    def load_multiple(self, filepaths: List[str]) -> Dict[str, str]:
        """
        Load multiple documents.
        
        Args:
            filepaths: List of file paths
        
        Returns:
            Dictionary mapping filepath to content
        """
        results = {}
        for filepath in filepaths:
            try:
                results[filepath] = self.load(filepath)
            except Exception as e:
                results[filepath] = f"Error: {e}"
        
        return results
    
    def process_with_llm(
        self,
        content: str,
        llm_facade,
        instruction: str,
        **llm_kwargs
    ) -> str:
        """
        Process document content with LLM.
        
        Args:
            content: Document content
            llm_facade: UnifiedLLMFacade instance
            instruction: Instruction for the LLM
            **llm_kwargs: Additional arguments for LLM
        
        Returns:
            LLM response
        
        Example:
            processor = DocumentProcessor()
            text = processor.load("doc.pdf")
            summary = processor.process_with_llm(
                text, 
                facade,
                "Summarize this document in 3 bullet points"
            )
        """
        prompt = f"{instruction}\n\nDocument content:\n{content}"
        response = llm_facade.complete(prompt, **llm_kwargs)
        return response.text
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        overlap: int = 100
    ) -> List[str]:
        """
        Split text into chunks for processing.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks
        
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def summarize_long_document(
        self,
        filepath: str,
        llm_facade,
        chunk_size: int = 2000,
        **llm_kwargs
    ) -> str:
        """
        Summarize a long document by chunking.
        
        Args:
            filepath: Path to document
            llm_facade: UnifiedLLMFacade instance
            chunk_size: Size of chunks
            **llm_kwargs: Additional LLM arguments
        
        Returns:
            Combined summary
        """
        # Load document
        text = self.load(filepath)
        
        # If short enough, process directly
        if len(text) < chunk_size:
            return self.process_with_llm(
                text,
                llm_facade,
                "Summarize this document",
                **llm_kwargs
            )
        
        # Chunk and summarize each
        chunks = self.chunk_text(text, chunk_size=chunk_size)
        summaries = []
        
        for i, chunk in enumerate(chunks):
            summary = self.process_with_llm(
                chunk,
                llm_facade,
                f"Summarize this section (part {i+1}/{len(chunks)})",
                **llm_kwargs
            )
            summaries.append(summary)
        
        # Combine summaries
        combined = "\n\n".join(summaries)
        
        # Final summary
        final_summary = self.process_with_llm(
            combined,
            llm_facade,
            "Create a final summary from these section summaries",
            **llm_kwargs
        )
        
        return final_summary
    
    def extract_key_points(
        self,
        filepath: str,
        llm_facade,
        num_points: int = 5,
        **llm_kwargs
    ) -> List[str]:
        """
        Extract key points from document.
        
        Args:
            filepath: Path to document
            llm_facade: UnifiedLLMFacade instance
            num_points: Number of key points to extract
            **llm_kwargs: Additional LLM arguments
        
        Returns:
            List of key points
        """
        text = self.load(filepath)
        
        response = self.process_with_llm(
            text,
            llm_facade,
            f"Extract the {num_points} most important key points from this document. "
            f"Return as a numbered list.",
            **llm_kwargs
        )
        
        # Parse response into list
        lines = response.strip().split('\n')
        points = [line.strip() for line in lines if line.strip()]
        
        return points[:num_points]
    
    def get_info(self, filepath: str) -> Dict[str, Any]:
        """Get information about a document."""
        return get_file_info(filepath)


__all__ = ['DocumentProcessor']


"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.4
"""
