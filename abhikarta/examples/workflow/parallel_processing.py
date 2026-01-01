#!/usr/bin/env python3
"""
Parallel Processing Workflow Example
=====================================

This example demonstrates parallel execution with split and join:
Input -> Split -> [Branch A, Branch B, Branch C] -> Join -> Output

Requirements:
    - Ollama running with llama3.2:3b model
    - pip install langchain-ollama langgraph

Usage:
    python -m abhikarta.examples.workflow.parallel_processing
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, TypedDict, Annotated, List
from operator import add
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://192.168.2.36:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")


# Workflow Definition JSON
WORKFLOW_DEFINITION = {
    "name": "Parallel Processing Pipeline",
    "description": "Demonstrates parallel execution with split and join operations",
    "nodes": [
        {
            "node_id": "input",
            "node_type": "input",
            "name": "Query Input",
            "position": {"x": 100, "y": 300},
            "config": {}
        },
        {
            "node_id": "split",
            "node_type": "split",
            "name": "Split Query",
            "position": {"x": 300, "y": 300},
            "config": {"split_type": "parallel", "branches": 3}
        },
        {
            "node_id": "branch_facts",
            "node_type": "llm",
            "name": "Get Facts",
            "position": {"x": 500, "y": 100},
            "config": {
                "provider": "ollama",
                "model": "llama3.2:3b",
                "system_prompt": "You are a fact expert. Provide 3 key facts about the topic."
            }
        },
        {
            "node_id": "branch_history",
            "node_type": "llm",
            "name": "Get History",
            "position": {"x": 500, "y": 300},
            "config": {
                "provider": "ollama",
                "model": "llama3.2:3b",
                "system_prompt": "You are a history expert. Provide brief historical context about the topic."
            }
        },
        {
            "node_id": "branch_future",
            "node_type": "llm",
            "name": "Get Future Outlook",
            "position": {"x": 500, "y": 500},
            "config": {
                "provider": "ollama",
                "model": "llama3.2:3b",
                "system_prompt": "You are a futurist. Provide future predictions about the topic."
            }
        },
        {
            "node_id": "join",
            "node_type": "aggregate",
            "name": "Aggregate Results",
            "position": {"x": 700, "y": 300},
            "config": {"strategy": "concat"}
        },
        {
            "node_id": "summarize",
            "node_type": "llm",
            "name": "Summarize",
            "position": {"x": 900, "y": 300},
            "config": {
                "provider": "ollama",
                "model": "llama3.2:3b",
                "system_prompt": "Synthesize the facts, history, and future outlook into a cohesive summary."
            }
        },
        {
            "node_id": "output",
            "node_type": "output",
            "name": "Final Report",
            "position": {"x": 1100, "y": 300},
            "config": {}
        }
    ],
    "edges": [
        {"source": "input", "target": "split"},
        {"source": "split", "target": "branch_facts"},
        {"source": "split", "target": "branch_history"},
        {"source": "split", "target": "branch_future"},
        {"source": "branch_facts", "target": "join"},
        {"source": "branch_history", "target": "join"},
        {"source": "branch_future", "target": "join"},
        {"source": "join", "target": "summarize"},
        {"source": "summarize", "target": "output"}
    ]
}


class WorkflowState(TypedDict):
    """State passed between workflow nodes."""
    input: str
    output: str
    branch_results: Dict[str, str]
    aggregated: str
    messages: Annotated[list, add]
    current_node: str


def run_parallel_workflow():
    """Run the parallel workflow."""
    try:
        from langchain_ollama import ChatOllama
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Install with: pip install langchain-ollama")
        return
    
    logger.info(f"Using Ollama at {OLLAMA_HOST} with model {OLLAMA_MODEL}")
    
    # Initialize LLM
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_HOST,
        temperature=0.7
    )
    
    # Test input
    test_input = "Artificial Intelligence"
    
    print(f"\n{'='*60}")
    print(f"PARALLEL WORKFLOW: Analyzing '{test_input}'")
    print(f"{'='*60}")
    
    # Define branch prompts
    branches = {
        "facts": "You are a fact expert. Provide 3 key facts about the following topic. Be concise.\n\nTopic: ",
        "history": "You are a history expert. Provide brief historical context (2-3 sentences) about the following topic.\n\nTopic: ",
        "future": "You are a futurist. Provide 2-3 future predictions about the following topic.\n\nTopic: "
    }
    
    # Run branches in parallel
    branch_results = {}
    
    def run_branch(name: str, prompt: str) -> tuple:
        logger.info(f"Running branch: {name}")
        try:
            response = llm.invoke(prompt + test_input)
            return (name, response.content)
        except Exception as e:
            logger.error(f"Error in branch {name}: {e}")
            return (name, f"Error: {str(e)}")
    
    # Use ThreadPoolExecutor for parallel execution
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(run_branch, name, prompt) for name, prompt in branches.items()]
        for future in futures:
            name, result = future.result()
            branch_results[name] = result
            print(f"\n--- {name.upper()} ---")
            print(result)
    
    # Aggregate results
    aggregated = "\n\n".join([
        f"## Facts\n{branch_results.get('facts', 'N/A')}",
        f"## History\n{branch_results.get('history', 'N/A')}",
        f"## Future\n{branch_results.get('future', 'N/A')}"
    ])
    
    # Final summarization
    logger.info("Running summarization...")
    summary_prompt = f"""Synthesize the following information about {test_input} into a cohesive 2-3 paragraph summary:

{aggregated}

Provide a well-structured summary that integrates all perspectives."""
    
    summary = llm.invoke(summary_prompt)
    
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    print(summary.content)
    print(f"{'='*60}")
    
    return {
        "input": test_input,
        "branch_results": branch_results,
        "aggregated": aggregated,
        "output": summary.content
    }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Parallel Processing Workflow Example")
    parser.add_argument("--json", action="store_true", help="Print workflow JSON definition")
    parser.add_argument("--host", default=OLLAMA_HOST, help="Ollama host URL")
    parser.add_argument("--model", default=OLLAMA_MODEL, help="Ollama model name")
    
    args = parser.parse_args()
    
    if args.json:
        print(json.dumps(WORKFLOW_DEFINITION, indent=2))
        return
    
    os.environ["OLLAMA_HOST"] = args.host
    os.environ["OLLAMA_MODEL"] = args.model
    
    run_parallel_workflow()


if __name__ == "__main__":
    main()
