"""
Example Python Script Workflow - Document Analysis Pipeline

This script demonstrates how to define a workflow using Abhikarta-LLM's 
Python Script Mode. Workflows orchestrate multiple processing steps
in a directed acyclic graph (DAG) pattern.

Features demonstrated:
- Multi-node workflow definition
- Parallel execution
- Conditional branching
- Error handling
- Output aggregation

Version: 1.4.8
Copyright © 2025-2030, All Rights Reserved
"""

# ==============================================================================
# Node Definitions
# ==============================================================================

# Node 1: Input handling
input_node = {
    "node_id": "input",
    "name": "Document Input",
    "node_type": "input",
    "description": "Receives document for analysis",
    "config": {
        "accepted_types": ["pdf", "docx", "txt", "html"],
        "max_size_mb": 50
    }
}

# Node 2: Text extraction
extract_node = {
    "node_id": "extract",
    "name": "Text Extraction",
    "node_type": "code",
    "description": "Extract text content from document",
    "config": {
        "extract_tables": True,
        "extract_images": False,
        "preserve_formatting": True
    }
}

# Node 3a: Entity extraction (parallel)
entity_node = {
    "node_id": "entities",
    "name": "Entity Extraction",
    "node_type": "llm",
    "description": "Extract named entities from text",
    "config": {
        "provider": "ollama",
        "model": "mistral",
        "prompt_template": "Extract all named entities (people, organizations, locations, dates) from the following text:\n\n{text}"
    }
}

# Node 3b: Sentiment analysis (parallel)
sentiment_node = {
    "node_id": "sentiment",
    "name": "Sentiment Analysis",
    "node_type": "llm",
    "description": "Analyze sentiment of the text",
    "config": {
        "provider": "ollama",
        "model": "mistral",
        "prompt_template": "Analyze the overall sentiment of this text. Rate from -1 (very negative) to +1 (very positive) and explain why:\n\n{text}"
    }
}

# Node 3c: Key points extraction (parallel)
keypoints_node = {
    "node_id": "keypoints",
    "name": "Key Points",
    "node_type": "llm",
    "description": "Extract key points and main ideas",
    "config": {
        "provider": "ollama",
        "model": "mistral",
        "prompt_template": "Extract the 5-10 most important key points from this text:\n\n{text}"
    }
}

# Node 4: Aggregation
aggregate_node = {
    "node_id": "aggregate",
    "name": "Aggregate Results",
    "node_type": "code",
    "description": "Combine all analysis results",
    "config": {
        "merge_strategy": "combine",
        "format": "structured"
    }
}

# Node 5: Summary generation
summary_node = {
    "node_id": "summary",
    "name": "Generate Summary",
    "node_type": "llm",
    "description": "Generate executive summary",
    "config": {
        "provider": "ollama",
        "model": "mistral",
        "prompt_template": """Based on the following analysis results, generate an executive summary:

Entities: {entities}
Sentiment: {sentiment}
Key Points: {keypoints}

Generate a concise executive summary (max 200 words)."""
    }
}

# Node 6: Output
output_node = {
    "node_id": "output",
    "name": "Analysis Output",
    "node_type": "output",
    "description": "Final analysis results",
    "config": {
        "format": "json",
        "include_metadata": True
    }
}

# ==============================================================================
# Edge Definitions (DAG connections)
# ==============================================================================

edges = [
    # Input to extraction
    {"source": "input", "target": "extract"},
    
    # Extraction to parallel analysis nodes
    {"source": "extract", "target": "entities"},
    {"source": "extract", "target": "sentiment"},
    {"source": "extract", "target": "keypoints"},
    
    # Parallel nodes to aggregation
    {"source": "entities", "target": "aggregate"},
    {"source": "sentiment", "target": "aggregate"},
    {"source": "keypoints", "target": "aggregate"},
    
    # Aggregation to summary
    {"source": "aggregate", "target": "summary"},
    
    # Summary to output
    {"source": "summary", "target": "output"}
]

# ==============================================================================
# Workflow Definition (Required)
# ==============================================================================

workflow = {
    "name": "Document Analysis Pipeline",
    "description": "Comprehensive document analysis with parallel processing",
    "version": "1.0.0",
    "workflow_type": "dag",
    
    # All nodes in the workflow
    "nodes": [
        input_node,
        extract_node,
        entity_node,
        sentiment_node,
        keypoints_node,
        aggregate_node,
        summary_node,
        output_node
    ],
    
    # Node connections
    "edges": edges,
    
    # Input/output schemas
    "input_schema": {
        "type": "object",
        "properties": {
            "document": {"type": "string", "description": "Document content or path"},
            "options": {"type": "object", "description": "Processing options"}
        },
        "required": ["document"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "entities": {"type": "array"},
            "sentiment": {"type": "object"},
            "key_points": {"type": "array"}
        }
    },
    
    # Execution settings
    "environment": {
        "timeout_seconds": 600,
        "max_parallel": 3,
        "retry_failed_nodes": True,
        "max_retries": 2
    },
    
    # Metadata
    "tags": ["document", "analysis", "nlp", "python-script"],
    "category": "data-processing"
}

# ==============================================================================
# Export (Required)
# ==============================================================================

__export__ = workflow


# ==============================================================================
# Optional: Custom Node Functions
# ==============================================================================

def extract_text(input_data: dict) -> dict:
    """Custom text extraction logic."""
    document = input_data.get('document', '')
    return {
        "text": document,  # In real implementation, would parse documents
        "metadata": {
            "length": len(document),
            "type": "text"
        }
    }


def aggregate_results(entities: dict, sentiment: dict, keypoints: dict) -> dict:
    """Aggregate parallel processing results."""
    return {
        "entities": entities.get('entities', []),
        "sentiment": sentiment.get('sentiment', {}),
        "key_points": keypoints.get('points', []),
        "analysis_complete": True
    }


def execute(input_data: dict) -> dict:
    """
    Custom execution function for the workflow.
    
    Args:
        input_data: Dictionary with document content
        
    Returns:
        Analysis results
    """
    document = input_data.get('document', '')
    
    # Simulated execution
    return {
        "summary": "Executive summary of the document...",
        "entities": ["Entity1", "Entity2"],
        "sentiment": {"score": 0.5, "label": "neutral"},
        "key_points": ["Point 1", "Point 2", "Point 3"]
    }
