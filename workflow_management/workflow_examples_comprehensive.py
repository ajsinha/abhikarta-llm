"""
Workflow Examples - JSON and Python Formats

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | Email: ajsinha@gmail.com

This module provides comprehensive examples of workflows in both JSON and Python
(LangGraph) formats demonstrating sequential, parallel, and human-in-the-loop patterns.
"""

from typing import Dict, Any
import json
from langgraph.graph import StateGraph, END
from datetime import datetime


# =============================================================================
# EXAMPLE 1: SEQUENTIAL WORKFLOW
# =============================================================================

def get_sequential_workflow_json() -> Dict[str, Any]:
    """
    Sequential Workflow - JSON Format

    Flow: Start -> Analyze Text -> Transform -> Calculate -> Validate -> End

    This workflow processes text through a series of sequential operations,
    demonstrating basic linear workflow execution.
    """
    return {
        "name": "Sequential Text Processing",
        "description": "Processes text through sequential transformations",
        "version": "1.0.0",
        "workflow_type": "json",
        "definition": {
            "nodes": [
                {
                    "node_id": "start",
                    "node_type": "start",
                    "name": "Start",
                    "description": "Workflow entry point"
                },
                {
                    "node_id": "analyze_text",
                    "node_type": "tool",
                    "name": "Analyze Input Text",
                    "description": "Analyze text for word count, sentiment, etc.",
                    "config": {
                        "tool_name": "text_analysis",
                        "parameters": {
                            "text": "{{input_text}}"
                        }
                    },
                    "timeout": 30,
                    "retry_count": 2
                },
                {
                    "node_id": "transform_uppercase",
                    "node_type": "tool",
                    "name": "Transform to Uppercase",
                    "description": "Convert text to uppercase",
                    "config": {
                        "tool_name": "data_transform",
                        "parameters": {
                            "input_data": "{{input_text}}",
                            "operation": "uppercase"
                        }
                    },
                    "timeout": 30
                },
                {
                    "node_id": "calculate_stats",
                    "node_type": "tool",
                    "name": "Calculate Statistics",
                    "description": "Perform statistical calculations",
                    "config": {
                        "tool_name": "math_calculator",
                        "parameters": {
                            "operation": "add",
                            "operand1": 100,
                            "operand2": 50
                        }
                    },
                    "timeout": 30
                },
                {
                    "node_id": "validate_result",
                    "node_type": "tool",
                    "name": "Validate Results",
                    "description": "Validate calculation results",
                    "config": {
                        "tool_name": "data_validator",
                        "parameters": {
                            "value": 150,
                            "min_threshold": 100,
                            "max_threshold": 200
                        }
                    },
                    "timeout": 30
                },
                {
                    "node_id": "end",
                    "node_type": "end",
                    "name": "End",
                    "description": "Workflow completion"
                }
            ],
            "edges": [
                {"source": "start", "target": "analyze_text"},
                {"source": "analyze_text", "target": "transform_uppercase"},
                {"source": "transform_uppercase", "target": "calculate_stats"},
                {"source": "calculate_stats", "target": "validate_result"},
                {"source": "validate_result", "target": "end"}
            ],
            "variables": {
                "input_text": "The quick brown fox jumps over the lazy dog. This is a test of sequential workflow processing."
            }
        }
    }


def get_sequential_workflow_python() -> str:
    """
    Sequential Workflow - Python Format

    Returns Python code that creates a LangGraph workflow for sequential processing.
    """
    return '''
# Sequential Workflow - Python/LangGraph Implementation
from langgraph.graph import StateGraph, END
from typing import Dict, Any

# Define the workflow graph
graph = StateGraph(WorkflowState)

# Node 1: Analyze Text
def analyze_text_node(state: WorkflowState) -> WorkflowState:
    """Analyze input text"""
    node_func = _create_node_function(execution_id, {
        'node_id': 'analyze_text',
        'node_type': 'tool',
        'config': {
            'tool_name': 'text_analysis',
            'parameters': {'text': state['variables'].get('input_text', '')}
        }
    })
    return node_func(state)

# Node 2: Transform to Uppercase
def transform_node(state: WorkflowState) -> WorkflowState:
    """Transform text to uppercase"""
    node_func = _create_node_function(execution_id, {
        'node_id': 'transform_uppercase',
        'node_type': 'tool',
        'config': {
            'tool_name': 'data_transform',
            'parameters': {
                'input_data': state['variables'].get('input_text', ''),
                'operation': 'uppercase'
            }
        }
    })
    return node_func(state)

# Node 3: Calculate Statistics
def calculate_node(state: WorkflowState) -> WorkflowState:
    """Perform calculations"""
    node_func = _create_node_function(execution_id, {
        'node_id': 'calculate_stats',
        'node_type': 'tool',
        'config': {
            'tool_name': 'math_calculator',
            'parameters': {
                'operation': 'add',
                'operand1': 100,
                'operand2': 50
            }
        }
    })
    return node_func(state)

# Node 4: Validate Results
def validate_node(state: WorkflowState) -> WorkflowState:
    """Validate results"""
    node_func = _create_node_function(execution_id, {
        'node_id': 'validate_result',
        'node_type': 'tool',
        'config': {
            'tool_name': 'data_validator',
            'parameters': {
                'value': 150,
                'min_threshold': 100,
                'max_threshold': 200
            }
        }
    })
    return node_func(state)

# Add nodes to graph
graph.add_node("start", lambda state: state)
graph.add_node("analyze_text", analyze_text_node)
graph.add_node("transform_uppercase", transform_node)
graph.add_node("calculate_stats", calculate_node)
graph.add_node("validate_result", validate_node)
graph.add_node("end", lambda state: {**state, "status": "completed"})

# Add edges (sequential flow)
graph.set_entry_point("start")
graph.add_edge("start", "analyze_text")
graph.add_edge("analyze_text", "transform_uppercase")
graph.add_edge("transform_uppercase", "calculate_stats")
graph.add_edge("calculate_stats", "validate_result")
graph.add_edge("validate_result", "end")
graph.add_edge("end", END)

# Compile the graph
compiled_graph = graph.compile()

# Initialize state
initial_state = WorkflowState(
    execution_id=execution_id,
    workflow_id="sequential_workflow",
    current_node="start",
    messages=[],
    variables={
        'input_text': 'The quick brown fox jumps over the lazy dog. This is a test of sequential workflow processing.'
    },
    node_outputs={},
    input_parameters=input_parameters,
    status="running",
    error=None,
    metadata={}
)
'''


# =============================================================================
# EXAMPLE 2: PARALLEL WORKFLOW
# =============================================================================

def get_parallel_workflow_json() -> Dict[str, Any]:
    """
    Parallel Workflow - JSON Format

    Flow: Start -> Parallel Split -> [Branch 1, Branch 2, Branch 3] -> Parallel Join -> Aggregate -> End

    This workflow demonstrates parallel execution where multiple branches
    run concurrently and their results are aggregated.
    """
    return {
        "name": "Parallel Data Processing",
        "description": "Processes data through parallel branches and aggregates results",
        "version": "1.0.0",
        "workflow_type": "json",
        "definition": {
            "nodes": [
                {
                    "node_id": "start",
                    "node_type": "start",
                    "name": "Start"
                },
                {
                    "node_id": "parallel_split",
                    "node_type": "parallel",
                    "name": "Split into Parallel Branches",
                    "description": "Split execution into parallel paths",
                    "config": {
                        "strategy": "all",
                        "max_concurrent": 3
                    }
                },
                {
                    "node_id": "branch1_text_analysis",
                    "node_type": "tool",
                    "name": "Branch 1: Text Analysis",
                    "description": "Analyze text in parallel",
                    "config": {
                        "tool_name": "text_analysis",
                        "parameters": {
                            "text": "{{input_text}}"
                        }
                    },
                    "timeout": 60
                },
                {
                    "node_id": "branch2_transform",
                    "node_type": "tool",
                    "name": "Branch 2: Data Transform",
                    "description": "Transform data in parallel",
                    "config": {
                        "tool_name": "data_transform",
                        "parameters": {
                            "input_data": "{{input_text}}",
                            "operation": "title"
                        }
                    },
                    "timeout": 60
                },
                {
                    "node_id": "branch3_random_gen",
                    "node_type": "tool",
                    "name": "Branch 3: Random Generation",
                    "description": "Generate random numbers in parallel",
                    "config": {
                        "tool_name": "random_number",
                        "parameters": {
                            "min_value": 1,
                            "max_value": 100,
                            "count": 10
                        }
                    },
                    "timeout": 60
                },
                {
                    "node_id": "parallel_join",
                    "node_type": "parallel",
                    "name": "Join Parallel Results",
                    "description": "Wait for all parallel branches to complete",
                    "config": {
                        "strategy": "all"
                    }
                },
                {
                    "node_id": "aggregate_results",
                    "node_type": "tool",
                    "name": "Aggregate Results",
                    "description": "Aggregate all parallel results",
                    "config": {
                        "tool_name": "math_calculator",
                        "parameters": {
                            "operation": "multiply",
                            "operand1": 3,
                            "operand2": 100
                        }
                    },
                    "timeout": 30
                },
                {
                    "node_id": "end",
                    "node_type": "end",
                    "name": "End"
                }
            ],
            "edges": [
                {"source": "start", "target": "parallel_split"},
                {"source": "parallel_split", "target": "branch1_text_analysis", "priority": 1},
                {"source": "parallel_split", "target": "branch2_transform", "priority": 2},
                {"source": "parallel_split", "target": "branch3_random_gen", "priority": 3},
                {"source": "branch1_text_analysis", "target": "parallel_join"},
                {"source": "branch2_transform", "target": "parallel_join"},
                {"source": "branch3_random_gen", "target": "parallel_join"},
                {"source": "parallel_join", "target": "aggregate_results"},
                {"source": "aggregate_results", "target": "end"}
            ],
            "variables": {
                "input_text": "Parallel workflow execution with LangGraph and Abhikarta"
            }
        }
    }


def get_parallel_workflow_python() -> str:
    """
    Parallel Workflow - Python Format

    Returns Python code that creates a LangGraph workflow for parallel processing.
    """
    return '''
# Parallel Workflow - Python/LangGraph Implementation
from langgraph.graph import StateGraph, END
from typing import Dict, Any

# Define the workflow graph
graph = StateGraph(WorkflowState)

# Branch 1: Text Analysis
def branch1_analysis(state: WorkflowState) -> WorkflowState:
    """Branch 1: Analyze text"""
    node_func = _create_node_function(execution_id, {
        'node_id': 'branch1_text_analysis',
        'node_type': 'tool',
        'config': {
            'tool_name': 'text_analysis',
            'parameters': {'text': state['variables'].get('input_text', '')}
        }
    })
    return node_func(state)

# Branch 2: Transform Data
def branch2_transform(state: WorkflowState) -> WorkflowState:
    """Branch 2: Transform data"""
    node_func = _create_node_function(execution_id, {
        'node_id': 'branch2_transform',
        'node_type': 'tool',
        'config': {
            'tool_name': 'data_transform',
            'parameters': {
                'input_data': state['variables'].get('input_text', ''),
                'operation': 'title'
            }
        }
    })
    return node_func(state)

# Branch 3: Random Numbers
def branch3_random(state: WorkflowState) -> WorkflowState:
    """Branch 3: Generate random numbers"""
    node_func = _create_node_function(execution_id, {
        'node_id': 'branch3_random_gen',
        'node_type': 'tool',
        'config': {
            'tool_name': 'random_number',
            'parameters': {
                'min_value': 1,
                'max_value': 100,
                'count': 10
            }
        }
    })
    return node_func(state)

# Aggregate Results
def aggregate_results(state: WorkflowState) -> WorkflowState:
    """Aggregate results from all branches"""
    node_func = _create_node_function(execution_id, {
        'node_id': 'aggregate_results',
        'node_type': 'tool',
        'config': {
            'tool_name': 'math_calculator',
            'parameters': {
                'operation': 'multiply',
                'operand1': 3,
                'operand2': 100
            }
        }
    })
    result_state = node_func(state)

    # Aggregate outputs from all branches
    branch_outputs = {
        'branch1': state['node_outputs'].get('branch1_text_analysis', {}),
        'branch2': state['node_outputs'].get('branch2_transform', {}),
        'branch3': state['node_outputs'].get('branch3_random_gen', {})
    }
    result_state['node_outputs']['aggregated'] = branch_outputs

    return result_state

# Add nodes
graph.add_node("start", lambda state: state)
graph.add_node("branch1_analysis", branch1_analysis)
graph.add_node("branch2_transform", branch2_transform)
graph.add_node("branch3_random", branch3_random)
graph.add_node("aggregate", aggregate_results)
graph.add_node("end", lambda state: {**state, "status": "completed"})

# Add edges for parallel execution
# LangGraph will execute branch1, branch2, branch3 in parallel automatically
graph.set_entry_point("start")
graph.add_edge("start", "branch1_analysis")
graph.add_edge("start", "branch2_transform")
graph.add_edge("start", "branch3_random")

# All branches converge to aggregate
graph.add_edge("branch1_analysis", "aggregate")
graph.add_edge("branch2_transform", "aggregate")
graph.add_edge("branch3_random", "aggregate")

graph.add_edge("aggregate", "end")
graph.add_edge("end", END)

# Compile the graph
compiled_graph = graph.compile()

# Initialize state
initial_state = WorkflowState(
    execution_id=execution_id,
    workflow_id="parallel_workflow",
    current_node="start",
    messages=[],
    variables={
        'input_text': 'Parallel workflow execution with LangGraph and Abhikarta'
    },
    node_outputs={},
    input_parameters=input_parameters,
    status="running",
    error=None,
    metadata={}
)
'''


# =============================================================================
# EXAMPLE 3: HUMAN-IN-THE-LOOP WORKFLOW
# =============================================================================

def get_hitl_workflow_json() -> Dict[str, Any]:
    """
    Human-in-the-Loop Workflow - JSON Format

    Flow: Start -> Generate Data -> Analyze -> Human Approval -> Conditional Branch -> [Approved/Rejected] -> End

    This workflow demonstrates human intervention where execution pauses
    for human review and approval before proceeding.
    """
    return {
        "name": "Human Approval Workflow",
        "description": "Requires human review and approval before proceeding",
        "version": "1.0.0",
        "workflow_type": "json",
        "definition": {
            "nodes": [
                {
                    "node_id": "start",
                    "node_type": "start",
                    "name": "Start"
                },
                {
                    "node_id": "generate_data",
                    "node_type": "tool",
                    "name": "Generate Random Data",
                    "description": "Generate sample data for review",
                    "config": {
                        "tool_name": "random_number",
                        "parameters": {
                            "min_value": 1,
                            "max_value": 1000,
                            "count": 20
                        }
                    },
                    "timeout": 30
                },
                {
                    "node_id": "analyze_data",
                    "node_type": "tool",
                    "name": "Analyze Generated Data",
                    "description": "Perform analysis on generated data",
                    "config": {
                        "tool_name": "math_calculator",
                        "parameters": {
                            "operation": "multiply",
                            "operand1": 42,
                            "operand2": 10
                        }
                    },
                    "timeout": 30
                },
                {
                    "node_id": "human_approval",
                    "node_type": "human",
                    "name": "Request Human Approval",
                    "description": "Pause for human review and approval",
                    "config": {
                        "assigned_to": "admin",
                        "task_type": "approval",
                        "timeout": 3600,
                        "instructions": "Please review the generated data and analysis results. Approve to continue processing or reject to stop the workflow.",
                        "required_fields": ["comments", "decision"]
                    }
                },
                {
                    "node_id": "check_approval",
                    "node_type": "conditional",
                    "name": "Check Approval Status",
                    "description": "Determine next steps based on approval",
                    "config": {
                        "condition": "node_outputs['human_approval']['status'] == 'completed'"
                    }
                },
                {
                    "node_id": "approved_processing",
                    "node_type": "tool",
                    "name": "Process Approved Data",
                    "description": "Continue processing after approval",
                    "config": {
                        "tool_name": "data_transform",
                        "parameters": {
                            "input_data": "Workflow Approved - Proceeding with processing",
                            "operation": "uppercase"
                        }
                    },
                    "timeout": 30
                },
                {
                    "node_id": "final_calculation",
                    "node_type": "tool",
                    "name": "Final Calculation",
                    "description": "Perform final calculations",
                    "config": {
                        "tool_name": "math_calculator",
                        "parameters": {
                            "operation": "power",
                            "operand1": 2,
                            "operand2": 10
                        }
                    },
                    "timeout": 30
                },
                {
                    "node_id": "rejected_handling",
                    "node_type": "tool",
                    "name": "Handle Rejection",
                    "description": "Handle workflow rejection",
                    "config": {
                        "tool_name": "data_transform",
                        "parameters": {
                            "input_data": "Workflow Rejected - Stopping execution",
                            "operation": "uppercase"
                        }
                    },
                    "timeout": 30
                },
                {
                    "node_id": "end_approved",
                    "node_type": "end",
                    "name": "End (Approved Path)"
                },
                {
                    "node_id": "end_rejected",
                    "node_type": "end",
                    "name": "End (Rejected Path)"
                }
            ],
            "edges": [
                {"source": "start", "target": "generate_data"},
                {"source": "generate_data", "target": "analyze_data"},
                {"source": "analyze_data", "target": "human_approval"},
                {"source": "human_approval", "target": "check_approval"},
                {
                    "source": "check_approval",
                    "target": "approved_processing",
                    "condition": "node_outputs['human_approval']['status'] == 'completed'"
                },
                {
                    "source": "check_approval",
                    "target": "rejected_handling",
                    "condition": "node_outputs['human_approval']['status'] == 'rejected'"
                },
                {"source": "approved_processing", "target": "final_calculation"},
                {"source": "final_calculation", "target": "end_approved"},
                {"source": "rejected_handling", "target": "end_rejected"}
            ],
            "variables": {
                "approval_required": True,
                "timeout_minutes": 60
            }
        }
    }


def get_hitl_workflow_python() -> str:
    """
    Human-in-the-Loop Workflow - Python Format

    Returns Python code that creates a LangGraph workflow with human approval.
    """
    return '''
# Human-in-the-Loop Workflow - Python/LangGraph Implementation
from langgraph.graph import StateGraph, END
from typing import Dict, Any

# Define the workflow graph
graph = StateGraph(WorkflowState)

# Node 1: Generate Data
def generate_data_node(state: WorkflowState) -> WorkflowState:
    """Generate random data"""
    node_func = _create_node_function(execution_id, {
        'node_id': 'generate_data',
        'node_type': 'tool',
        'config': {
            'tool_name': 'random_number',
            'parameters': {
                'min_value': 1,
                'max_value': 1000,
                'count': 20
            }
        }
    })
    return node_func(state)

# Node 2: Analyze Data
def analyze_data_node(state: WorkflowState) -> WorkflowState:
    """Analyze generated data"""
    node_func = _create_node_function(execution_id, {
        'node_id': 'analyze_data',
        'node_type': 'tool',
        'config': {
            'tool_name': 'math_calculator',
            'parameters': {
                'operation': 'multiply',
                'operand1': 42,
                'operand2': 10
            }
        }
    })
    return node_func(state)

# Node 3: Human Approval (CRITICAL NODE)
def human_approval_node(state: WorkflowState) -> WorkflowState:
    """Request human approval - workflow pauses here"""
    # Create human task in database
    from workflow_management.models.workflow_models import HumanTask, TaskStatus
    from datetime import datetime, timedelta

    task_id = HumanTask.generate_id()
    task = HumanTask(
        task_id=task_id,
        execution_id=execution_id,
        node_execution_id="human_approval_node",
        assigned_to="admin",
        task_type="approval",
        status=TaskStatus.PENDING.value,
        created_at=datetime.now(),
        timeout_at=datetime.now() + timedelta(hours=1)
    )

    db_handler.create_human_task(task)

    _log_audit(
        execution_id, "INFO",
        f"Human approval task created: {task_id}",
        {'assigned_to': 'admin', 'task_type': 'approval'}
    )

    # Update state with task information
    new_state = {**state}
    new_state['node_outputs']['human_approval'] = {
        'task_id': task_id,
        'status': 'waiting_for_human',
        'assigned_to': 'admin'
    }

    # In a real implementation, this would pause execution and wait
    # For demo purposes, we'll simulate approval
    # In production, you would check task status from database

    return new_state

# Node 4: Check Approval (Conditional Router)
def check_approval_router(state: WorkflowState) -> str:
    """Route based on approval status"""
    approval_status = state['node_outputs'].get('human_approval', {}).get('status', 'rejected')

    # Check actual task status from database
    # task = db_handler.get_human_task(task_id)
    # if task.status == 'completed':
    #     return 'approved'
    # else:
    #     return 'rejected'

    # For demo, check state
    if approval_status == 'completed':
        return 'approved'
    else:
        return 'rejected'

# Node 5: Approved Processing
def approved_processing_node(state: WorkflowState) -> WorkflowState:
    """Process approved workflow"""
    node_func = _create_node_function(execution_id, {
        'node_id': 'approved_processing',
        'node_type': 'tool',
        'config': {
            'tool_name': 'data_transform',
            'parameters': {
                'input_data': 'Workflow Approved - Proceeding with processing',
                'operation': 'uppercase'
            }
        }
    })
    return node_func(state)

# Node 6: Final Calculation
def final_calculation_node(state: WorkflowState) -> WorkflowState:
    """Perform final calculations"""
    node_func = _create_node_function(execution_id, {
        'node_id': 'final_calculation',
        'node_type': 'tool',
        'config': {
            'tool_name': 'math_calculator',
            'parameters': {
                'operation': 'power',
                'operand1': 2,
                'operand2': 10
            }
        }
    })
    return node_func(state)

# Node 7: Rejected Handling
def rejected_handling_node(state: WorkflowState) -> WorkflowState:
    """Handle workflow rejection"""
    node_func = _create_node_function(execution_id, {
        'node_id': 'rejected_handling',
        'node_type': 'tool',
        'config': {
            'tool_name': 'data_transform',
            'parameters': {
                'input_data': 'Workflow Rejected - Stopping execution',
                'operation': 'uppercase'
            }
        }
    })
    return node_func(state)

# Build the graph
graph.add_node("start", lambda state: state)
graph.add_node("generate_data", generate_data_node)
graph.add_node("analyze_data", analyze_data_node)
graph.add_node("human_approval", human_approval_node)
graph.add_node("approved_processing", approved_processing_node)
graph.add_node("final_calculation", final_calculation_node)
graph.add_node("rejected_handling", rejected_handling_node)
graph.add_node("end_approved", lambda state: {**state, "status": "completed"})
graph.add_node("end_rejected", lambda state: {**state, "status": "rejected"})

# Add edges
graph.set_entry_point("start")
graph.add_edge("start", "generate_data")
graph.add_edge("generate_data", "analyze_data")
graph.add_edge("analyze_data", "human_approval")

# Conditional routing after human approval
graph.add_conditional_edges(
    "human_approval",
    check_approval_router,
    {
        "approved": "approved_processing",
        "rejected": "rejected_handling"
    }
)

# Approved path
graph.add_edge("approved_processing", "final_calculation")
graph.add_edge("final_calculation", "end_approved")
graph.add_edge("end_approved", END)

# Rejected path
graph.add_edge("rejected_handling", "end_rejected")
graph.add_edge("end_rejected", END)

# Compile the graph
compiled_graph = graph.compile()

# Initialize state
initial_state = WorkflowState(
    execution_id=execution_id,
    workflow_id="hitl_workflow",
    current_node="start",
    messages=[],
    variables={
        'approval_required': True,
        'timeout_minutes': 60
    },
    node_outputs={},
    input_parameters=input_parameters,
    status="running",
    error=None,
    metadata={}
)
'''


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def save_workflow_examples():
    """Save all workflow examples to JSON files"""
    examples = {
        'sequential_json': get_sequential_workflow_json(),
        'parallel_json': get_parallel_workflow_json(),
        'hitl_json': get_hitl_workflow_json()
    }

    for name, workflow in examples.items():
        filename = f"/home/claude/workflow_example_{name}.json"
        with open(filename, 'w') as f:
            json.dump(workflow, f, indent=2)
        print(f"Saved: {filename}")

    # Save Python examples
    python_examples = {
        'sequential_python': get_sequential_workflow_python(),
        'parallel_python': get_parallel_workflow_python(),
        'hitl_python': get_hitl_workflow_python()
    }

    for name, code in python_examples.items():
        filename = f"/home/claude/workflow_example_{name}.py"
        with open(filename, 'w') as f:
            f.write(code)
        print(f"Saved: {filename}")


def get_all_examples() -> Dict[str, Any]:
    """Get all workflow examples in a single dictionary"""
    return {
        'sequential': {
            'json': get_sequential_workflow_json(),
            'python': get_sequential_workflow_python()
        },
        'parallel': {
            'json': get_parallel_workflow_json(),
            'python': get_parallel_workflow_python()
        },
        'human_in_loop': {
            'json': get_hitl_workflow_json(),
            'python': get_hitl_workflow_python()
        }
    }


# Export all example functions
__all__ = [
    'get_sequential_workflow_json',
    'get_sequential_workflow_python',
    'get_parallel_workflow_json',
    'get_parallel_workflow_python',
    'get_hitl_workflow_json',
    'get_hitl_workflow_python',
    'save_workflow_examples',
    'get_all_examples'
]