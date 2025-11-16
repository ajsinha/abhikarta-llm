"""
Abhikarta LLM Platform
DAG Workflow Examples
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""

import asyncio
import sys
sys.path.insert(0, '..')

from engine_management.api import AbhikartaExecutionAPI
from engine_management.database.db_manager import DatabaseManager
import json
import uuid

async def example_sequential_dag():
    """Example: Simple sequential workflow"""
    
    print("="*60)
    print("SEQUENTIAL DAG WORKFLOW")
    print("="*60)
    
    # Initialize
    db_manager = DatabaseManager("examples.db")
    api = AbhikartaExecutionAPI(db_path="examples.db")
    
    # Define sequential DAG
    dag_definition = {
        "nodes": {
            "extract_data": {
                "type": "tool",
                "tool": "data_extractor",
                "description": "Extract data from source",
                "inputs": {"source": "{data_source}"},
                "next": ["transform_data"]
            },
            "transform_data": {
                "type": "tool",
                "tool": "data_transformer",
                "description": "Transform extracted data",
                "inputs": {"data": "{extract_data.result}"},
                "next": ["analyze_data"]
            },
            "analyze_data": {
                "type": "llm",
                "description": "Analyze transformed data",
                "prompt": "Analyze this data and provide insights: {transform_data.result}",
                "next": ["generate_report"]
            },
            "generate_report": {
                "type": "llm",
                "description": "Generate final report",
                "prompt": "Create a report based on: {analyze_data.result}",
                "next": []
            }
        }
    }
    
    # Save DAG
    dag_id = str(uuid.uuid4())
    
    with api.db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dag_definitions (
                dag_id, name, description, graph_definition, entry_point
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            dag_id,
            "Data Pipeline DAG",
            "Sequential data processing pipeline",
            json.dumps(dag_definition),
            "extract_data"
        ))
        conn.commit()
    
    print(f"\n✓ DAG created: {dag_id}")
    print("\nWorkflow Steps:")
    for node_name, node_def in dag_definition["nodes"].items():
        print(f"  {node_name}: {node_def['description']}")
    
    # Execute (requires actual implementation)
    print("\n🚀 DAG ready for execution")
    print("   Use: api.execute_dag(user_id='user', dag_id='{dag_id}')")

async def example_conditional_dag():
    """Example: DAG with conditional branching"""
    
    print("\n" + "="*60)
    print("CONDITIONAL DAG WORKFLOW")
    print("="*60)
    
    # Define conditional DAG
    dag_definition = {
        "nodes": {
            "check_sentiment": {
                "type": "tool",
                "tool": "sentiment_analyzer",
                "description": "Analyze sentiment of input",
                "inputs": {"text": "{user_message}"},
                "next": ["route_by_sentiment"]
            },
            "route_by_sentiment": {
                "type": "condition",
                "description": "Route based on sentiment",
                "condition": "sentiment == 'positive'",
                "true_branch": "positive_handler",
                "false_branch": "negative_handler"
            },
            "positive_handler": {
                "type": "llm",
                "description": "Handle positive sentiment",
                "prompt": "Generate enthusiastic response to: {user_message}",
                "next": ["finalize"]
            },
            "negative_handler": {
                "type": "llm",
                "description": "Handle negative sentiment",
                "prompt": "Generate empathetic response to: {user_message}",
                "next": ["finalize"]
            },
            "finalize": {
                "type": "tool",
                "tool": "response_formatter",
                "description": "Format final response",
                "inputs": {"response": "{previous.result}"},
                "next": []
            }
        }
    }
    
    print("\nConditional Workflow:")
    print("  1. Check sentiment")
    print("  2. Route to positive or negative handler")
    print("  3. Generate appropriate response")
    print("  4. Format and return")
    
    print("\n✓ Conditional DAG structure defined")

async def example_parallel_dag():
    """Example: Parallel execution DAG"""
    
    print("\n" + "="*60)
    print("PARALLEL DAG WORKFLOW")
    print("="*60)
    
    dag_definition = {
        "nodes": {
            "start": {
                "type": "split",
                "description": "Split into parallel branches",
                "next": ["search_news", "search_papers", "search_social"]
            },
            "search_news": {
                "type": "tool",
                "tool": "news_searcher",
                "description": "Search news sources",
                "inputs": {"query": "{topic}"},
                "next": ["merge_results"]
            },
            "search_papers": {
                "type": "tool",
                "tool": "paper_searcher",
                "description": "Search academic papers",
                "inputs": {"query": "{topic}"},
                "next": ["merge_results"]
            },
            "search_social": {
                "type": "tool",
                "tool": "social_searcher",
                "description": "Search social media",
                "inputs": {"query": "{topic}"},
                "next": ["merge_results"]
            },
            "merge_results": {
                "type": "llm",
                "description": "Synthesize all findings",
                "prompt": """
                Synthesize these findings:
                News: {search_news.result}
                Papers: {search_papers.result}
                Social: {search_social.result}
                """,
                "next": []
            }
        }
    }
    
    print("\nParallel Workflow:")
    print("  ┌─ Search News ────┐")
    print("  ├─ Search Papers ──┤")
    print("  └─ Search Social ──┘")
    print("         ↓")
    print("    Merge Results")
    
    print("\n✓ Parallel DAG enables concurrent execution")

async def example_complex_dag():
    """Example: Complex DAG with multiple patterns"""
    
    print("\n" + "="*60)
    print("COMPLEX DAG WORKFLOW")
    print("="*60)
    
    # E-commerce order processing DAG
    dag_definition = {
        "nodes": {
            "validate_order": {
                "type": "tool",
                "tool": "order_validator",
                "next": ["check_inventory"]
            },
            "check_inventory": {
                "type": "condition",
                "condition": "in_stock == true",
                "true_branch": "process_payment",
                "false_branch": "notify_out_of_stock"
            },
            "process_payment": {
                "type": "tool",
                "tool": "payment_processor",
                "next": ["parallel_split"]
            },
            "parallel_split": {
                "type": "split",
                "next": ["send_confirmation", "update_inventory", "create_shipment"]
            },
            "send_confirmation": {
                "type": "llm",
                "prompt": "Generate order confirmation email",
                "next": ["complete"]
            },
            "update_inventory": {
                "type": "tool",
                "tool": "inventory_updater",
                "next": ["complete"]
            },
            "create_shipment": {
                "type": "tool",
                "tool": "shipment_creator",
                "next": ["complete"]
            },
            "notify_out_of_stock": {
                "type": "llm",
                "prompt": "Generate out-of-stock notification",
                "next": []
            },
            "complete": {
                "type": "merge",
                "description": "Wait for all parallel tasks",
                "next": []
            }
        }
    }
    
    print("\nE-commerce Order Processing DAG:")
    print("  Validate → Check Inventory")
    print("               ├─ In Stock → Process Payment")
    print("               │              ├─ Send Email")
    print("               │              ├─ Update Inventory")
    print("               │              └─ Create Shipment")
    print("               └─ Out of Stock → Notify")
    
    print("\n✓ Complex DAG combines conditional and parallel patterns")

if __name__ == "__main__":
    print("ABHIKARTA DAG WORKFLOW EXAMPLES\n")
    
    asyncio.run(example_sequential_dag())
    asyncio.run(example_conditional_dag())
    asyncio.run(example_parallel_dag())
    asyncio.run(example_complex_dag())
    
    print("\n" + "="*60)
    print("✅ All DAG examples completed!")
    print("="*60)
