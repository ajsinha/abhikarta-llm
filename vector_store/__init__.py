"""
Abhikarta LLM Vector Store Package
Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.
Email: ajsinha@gmail.com
"""

from .vector_store_base import VectorStoreBase, Document, Embedding, Filter, RetrievalResult
from .vector_store_factory import VectorStoreFactory, create_vector_store

__version__ = "1.0.0"
__author__ = "Ashutosh Sinha"
__email__ = "ajsinha@gmail.com"

__all__ = [
    "VectorStoreBase",
    "VectorStoreFactory",
    "create_vector_store",
    "Document",
    "Embedding",
    "Filter",
    "RetrievalResult",
]