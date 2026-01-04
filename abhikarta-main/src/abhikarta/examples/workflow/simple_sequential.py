#!/usr/bin/env python3
"""
Simple Sequential Workflow Example
===================================

This example demonstrates a basic sequential workflow:
Input -> Validate -> Transform -> LLM Process -> Output

Requirements:
    - Ollama running with llama3.2:3b model
    - pip install langchain-ollama langgraph

Usage:
    python -m abhikarta.examples.workflow.simple_sequential
    
    Or directly:
    python simple_sequential.py
"""

import os
import json
import logging
from typing import Dict, Any, TypedDict, Annotated
from operator import add

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://192.168.2.36:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")


# Workflow Definition JSON
WORKFLOW_DEFINITION = {
    "name": "Simple Sequential Pipeline",
    "description": "Basic sequential workflow demonstrating input -> process -> output pattern",
    "nodes": [
        {
            "node_id": "input",
            "node_type": "input",
            "name": "Data Input",
            "position": {"x": 100, "y": 200},
            "config": {}
        },
        {
            "node_id": "validate",
            "node_type": "python",
            "name": "Validate Data",
            "position": {"x": 300, "y": 200},
            "config": {
                "code": """
# Validate input data
if not input_data:
    raise ValueError('No input provided')
output = {'valid': True, 'data': input_data}
"""
            }
        },
        {
            "node_id": "transform",
            "node_type": "transform",
            "name": "Transform Data",
            "position": {"x": 500, "y": 200},
            "config": {
                "transform_type": "passthrough"
            }
        },
        {
            "node_id": "process",
            "node_type": "llm",
            "name": "LLM Process",
            "position": {"x": 700, "y": 200},
            "config": {
                "provider": "ollama",
                "model": "llama3.2:3b",
                "system_prompt": "You are a helpful assistant. Process the input and provide a thoughtful response."
            }
        },
        {
            "node_id": "output",
            "node_type": "output",
            "name": "Result",
            "position": {"x": 900, "y": 200},
            "config": {}
        }
    ],
    "edges": [
        {"source": "input", "target": "validate"},
        {"source": "validate", "target": "transform"},
        {"source": "transform", "target": "process"},
        {"source": "process", "target": "output"}
    ]
}


# State definition for LangGraph
class WorkflowState(TypedDict):
    """State passed between workflow nodes."""
    input: str
    output: str
    node_outputs: Dict[str, Any]
    messages: Annotated[list, add]
    current_node: str
    error: str


def run_with_langgraph():
    """Run the workflow using LangGraph."""
    try:
        from langgraph.graph import StateGraph, END
        from langchain_ollama import ChatOllama
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Install with: pip install langgraph langchain-ollama")
        return
    
    logger.info(f"Using Ollama at {OLLAMA_HOST} with model {OLLAMA_MODEL}")
    
    # Initialize LLM
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_HOST,
        temperature=0.7
    )
    
    # Define node functions
    def validate_node(state: WorkflowState) -> Dict:
        """Validate input data."""
        logger.info("Running validate node")
        input_data = state.get("input", "")
        
        if not input_data:
            return {
                "error": "No input provided",
                "current_node": "validate"
            }
        
        return {
            "node_outputs": {**state.get("node_outputs", {}), "validate": {"valid": True, "data": input_data}},
            "current_node": "validate",
            "messages": [f"Validated input: {input_data[:50]}..."]
        }
    
    def transform_node(state: WorkflowState) -> Dict:
        """Transform data (passthrough in this example)."""
        logger.info("Running transform node")
        validated = state.get("node_outputs", {}).get("validate", {})
        data = validated.get("data", state.get("input", ""))
        
        return {
            "node_outputs": {**state.get("node_outputs", {}), "transform": {"transformed": data}},
            "current_node": "transform",
            "messages": ["Data transformed"]
        }
    
    def llm_process_node(state: WorkflowState) -> Dict:
        """Process with LLM."""
        logger.info("Running LLM process node")
        transformed = state.get("node_outputs", {}).get("transform", {})
        data = transformed.get("transformed", state.get("input", ""))
        
        try:
            response = llm.invoke(f"Please process this input and provide a helpful response:\n\n{data}")
            result = response.content
        except Exception as e:
            logger.error(f"LLM error: {e}")
            result = f"Error processing with LLM: {str(e)}"
        
        return {
            "output": result,
            "node_outputs": {**state.get("node_outputs", {}), "process": {"result": result}},
            "current_node": "process",
            "messages": ["LLM processing complete"]
        }
    
    # Build the graph
    graph = StateGraph(WorkflowState)
    
    # Add nodes (skip input/output - they're handled by entry/exit)
    graph.add_node("validate", validate_node)
    graph.add_node("transform", transform_node)
    graph.add_node("process", llm_process_node)
    
    # Add edges
    graph.set_entry_point("validate")
    graph.add_edge("validate", "transform")
    graph.add_edge("transform", "process")
    graph.add_edge("process", END)
    
    # Compile
    workflow = graph.compile()
    
    # Run with test input
    test_input = "What are three interesting facts about artificial intelligence?"
    
    logger.info(f"Running workflow with input: {test_input}")
    
    initial_state = {
        "input": test_input,
        "output": "",
        "node_outputs": {},
        "messages": [],
        "current_node": "input",
        "error": ""
    }
    
    result = workflow.invoke(initial_state)
    
    print("\n" + "="*60)
    print("WORKFLOW RESULT")
    print("="*60)
    print(f"Input: {test_input}")
    print(f"\nOutput:\n{result.get('output', 'No output')}")
    print(f"\nMessages: {result.get('messages', [])}")
    print("="*60)
    
    return result


def run_simple():
    """Run a simple version without LangGraph (direct Ollama call)."""
    try:
        from langchain_ollama import ChatOllama
    except ImportError:
        logger.error("langchain-ollama not installed. Install with: pip install langchain-ollama")
        return
    
    logger.info(f"Running simple workflow with Ollama at {OLLAMA_HOST}")
    
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_HOST,
        temperature=0.7
    )
    
    test_input = "What are three interesting facts about artificial intelligence?"
    
    # Step 1: Validate
    logger.info("Step 1: Validating input...")
    if not test_input:
        raise ValueError("No input provided")
    logger.info("Input validated")
    
    # Step 2: Transform (passthrough)
    logger.info("Step 2: Transforming data...")
    transformed = test_input
    logger.info("Data transformed")
    
    # Step 3: LLM Process
    logger.info("Step 3: Processing with LLM...")
    response = llm.invoke(f"Please process this input and provide a helpful response:\n\n{transformed}")
    
    print("\n" + "="*60)
    print("SIMPLE WORKFLOW RESULT")
    print("="*60)
    print(f"Input: {test_input}")
    print(f"\nOutput:\n{response.content}")
    print("="*60)
    
    return response.content


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Sequential Workflow Example")
    parser.add_argument("--simple", action="store_true", help="Run simple version without LangGraph")
    parser.add_argument("--json", action="store_true", help="Print workflow JSON definition")
    parser.add_argument("--host", default=OLLAMA_HOST, help="Ollama host URL")
    parser.add_argument("--model", default=OLLAMA_MODEL, help="Ollama model name")
    
    args = parser.parse_args()
    
    if args.json:
        print(json.dumps(WORKFLOW_DEFINITION, indent=2))
        return
    
    # Update configuration from args
    os.environ["OLLAMA_HOST"] = args.host
    os.environ["OLLAMA_MODEL"] = args.model
    
    if args.simple:
        run_simple()
    else:
        run_with_langgraph()


if __name__ == "__main__":
    main()
