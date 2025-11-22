"""
Python-based Workflow Builders

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | Email: ajsinha@gmail.com

This module provides Python classes for building workflows programmatically.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json


@dataclass
class WorkflowNode:
    """Represents a node in the workflow"""
    node_id: str
    node_type: str
    name: str
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    input_mappings: Dict[str, str] = field(default_factory=dict)
    output_mappings: Dict[str, str] = field(default_factory=dict)
    timeout: int = 300
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "description": self.description,
            "config": self.config,
            "input_mappings": self.input_mappings,
            "output_mappings": self.output_mappings,
            "timeout": self.timeout,
            "retry_count": self.retry_count
        }


@dataclass
class WorkflowEdge:
    """Represents an edge between nodes"""
    source: str
    target: str
    condition: Optional[str] = None
    priority: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        edge_dict = {
            "source": self.source,
            "target": self.target,
            "priority": self.priority
        }
        if self.condition:
            edge_dict["condition"] = self.condition
        return edge_dict


class WorkflowBuilder:
    """Builder class for creating workflows programmatically"""
    
    def __init__(self, name: str, description: str, version: str = "1.0.0"):
        self.name = name
        self.description = description
        self.version = version
        self.nodes: List[WorkflowNode] = []
        self.edges: List[WorkflowEdge] = []
        self.variables: Dict[str, Any] = {}
    
    def add_node(self, node: WorkflowNode) -> 'WorkflowBuilder':
        """Add a node to the workflow"""
        self.nodes.append(node)
        return self
    
    def add_edge(self, edge: WorkflowEdge) -> 'WorkflowBuilder':
        """Add an edge to the workflow"""
        self.edges.append(edge)
        return self
    
    def set_variable(self, key: str, value: Any) -> 'WorkflowBuilder':
        """Set a workflow variable"""
        self.variables[key] = value
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the complete workflow definition"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "workflow": {
                "nodes": [node.to_dict() for node in self.nodes],
                "edges": [edge.to_dict() for edge in self.edges],
                "variables": self.variables
            }
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert workflow to JSON string"""
        return json.dumps(self.build(), indent=indent)
    
    def save_to_file(self, filename: str):
        """Save workflow to JSON file"""
        with open(filename, 'w') as f:
            f.write(self.to_json())


def create_sequential_workflow() -> WorkflowBuilder:
    """
    Create a sequential workflow example.
    
    Flow: Start -> Text Analysis -> Transform -> Validate -> End
    """
    builder = WorkflowBuilder(
        name="Sequential Text Processing",
        description="Processes text through a sequence of transformations",
        version="1.0.0"
    )
    
    # Add nodes
    builder.add_node(WorkflowNode(
        node_id="start",
        node_type="start",
        name="Start",
        description="Workflow entry point"
    ))
    
    builder.add_node(WorkflowNode(
        node_id="analyze_text",
        node_type="tool",
        name="Analyze Text",
        description="Analyze input text for statistics",
        config={
            "tool_name": "text_analysis",
            "parameters": {
                "text": "{{input_text}}"
            }
        },
        output_mappings={"analysis": "output"}
    ))
    
    builder.add_node(WorkflowNode(
        node_id="transform_text",
        node_type="tool",
        name="Transform to Uppercase",
        description="Convert text to uppercase",
        config={
            "tool_name": "data_transform",
            "parameters": {
                "input_data": "{{input_text}}",
                "operation": "uppercase"
            }
        },
        output_mappings={"transformed": "output"}
    ))
    
    builder.add_node(WorkflowNode(
        node_id="validate_length",
        node_type="tool",
        name="Validate Word Count",
        description="Ensure word count is within acceptable range",
        config={
            "tool_name": "data_validator",
            "parameters": {
                "value": 10,
                "min_threshold": 5,
                "max_threshold": 1000
            }
        },
        output_mappings={"validation": "output"}
    ))
    
    builder.add_node(WorkflowNode(
        node_id="end",
        node_type="end",
        name="End",
        description="Workflow completion"
    ))
    
    # Add edges
    builder.add_edge(WorkflowEdge("start", "analyze_text"))
    builder.add_edge(WorkflowEdge("analyze_text", "transform_text"))
    builder.add_edge(WorkflowEdge("transform_text", "validate_length"))
    builder.add_edge(WorkflowEdge("validate_length", "end"))
    
    # Set variables
    builder.set_variable("input_text", "The quick brown fox jumps over the lazy dog")
    
    return builder


def create_parallel_workflow() -> WorkflowBuilder:
    """
    Create a parallel workflow example.
    
    Flow: Start -> Parallel Split -> [Branch1, Branch2, Branch3] -> Join -> End
    """
    builder = WorkflowBuilder(
        name="Parallel Data Processing",
        description="Processes data in parallel branches",
        version="1.0.0"
    )
    
    # Start node
    builder.add_node(WorkflowNode(
        node_id="start",
        node_type="start",
        name="Start"
    ))
    
    # Parallel split
    builder.add_node(WorkflowNode(
        node_id="parallel_split",
        node_type="parallel",
        name="Split into Parallel Branches",
        config={"strategy": "all", "max_concurrent": 3}
    ))
    
    # Branch 1: Text Analysis
    builder.add_node(WorkflowNode(
        node_id="branch1_analysis",
        node_type="tool",
        name="Text Analysis Branch",
        config={
            "tool_name": "text_analysis",
            "parameters": {"text": "{{input_text}}"}
        }
    ))
    
    # Branch 2: Data Transform
    builder.add_node(WorkflowNode(
        node_id="branch2_transform",
        node_type="tool",
        name="Transform Branch",
        config={
            "tool_name": "data_transform",
            "parameters": {
                "input_data": "{{input_text}}",
                "operation": "title"
            }
        }
    ))
    
    # Branch 3: Random Numbers
    builder.add_node(WorkflowNode(
        node_id="branch3_random",
        node_type="tool",
        name="Random Number Generation",
        config={
            "tool_name": "random_number",
            "parameters": {
                "min_value": 1,
                "max_value": 100,
                "count": 5
            }
        }
    ))
    
    # Parallel join
    builder.add_node(WorkflowNode(
        node_id="parallel_join",
        node_type="parallel",
        name="Join Parallel Results",
        config={"strategy": "all"}
    ))
    
    # Aggregate results
    builder.add_node(WorkflowNode(
        node_id="aggregate",
        node_type="tool",
        name="Aggregate Results",
        config={
            "tool_name": "math_calculator",
            "parameters": {
                "operation": "add",
                "operand1": 100,
                "operand2": 200
            }
        }
    ))
    
    # End node
    builder.add_node(WorkflowNode(
        node_id="end",
        node_type="end",
        name="End"
    ))
    
    # Add edges
    builder.add_edge(WorkflowEdge("start", "parallel_split"))
    builder.add_edge(WorkflowEdge("parallel_split", "branch1_analysis", priority=1))
    builder.add_edge(WorkflowEdge("parallel_split", "branch2_transform", priority=2))
    builder.add_edge(WorkflowEdge("parallel_split", "branch3_random", priority=3))
    builder.add_edge(WorkflowEdge("branch1_analysis", "parallel_join"))
    builder.add_edge(WorkflowEdge("branch2_transform", "parallel_join"))
    builder.add_edge(WorkflowEdge("branch3_random", "parallel_join"))
    builder.add_edge(WorkflowEdge("parallel_join", "aggregate"))
    builder.add_edge(WorkflowEdge("aggregate", "end"))
    
    # Set variables
    builder.set_variable("input_text", "Parallel Processing with Abhikarta Workflows")
    
    return builder


def create_hitl_workflow() -> WorkflowBuilder:
    """
    Create a Human-in-the-Loop workflow example.
    
    Flow: Start -> Generate Data -> Calculate -> Human Approval -> Conditional -> [Approved/Rejected] -> End
    """
    builder = WorkflowBuilder(
        name="Human Approval Workflow",
        description="Requires human review and approval before proceeding",
        version="1.0.0"
    )
    
    # Start
    builder.add_node(WorkflowNode(
        node_id="start",
        node_type="start",
        name="Start"
    ))
    
    # Generate random data
    builder.add_node(WorkflowNode(
        node_id="generate_data",
        node_type="tool",
        name="Generate Random Data",
        config={
            "tool_name": "random_number",
            "parameters": {
                "min_value": 1,
                "max_value": 100,
                "count": 10
            }
        },
        output_mappings={"random_data": "output"}
    ))
    
    # Perform calculation
    builder.add_node(WorkflowNode(
        node_id="calculate_sum",
        node_type="tool",
        name="Calculate Statistics",
        config={
            "tool_name": "math_calculator",
            "parameters": {
                "operation": "add",
                "operand1": 50,
                "operand2": 75
            }
        },
        output_mappings={"calculation": "output"}
    ))
    
    # Human approval node
    builder.add_node(WorkflowNode(
        node_id="human_approval",
        node_type="human",
        name="Request Human Approval",
        description="Requires approval to proceed with workflow",
        config={
            "assigned_to": "admin",
            "task_type": "approval",
            "timeout": 3600,
            "instructions": "Please review the generated data and calculations. Approve to continue or reject to stop."
        }
    ))
    
    # Conditional check
    builder.add_node(WorkflowNode(
        node_id="check_approval",
        node_type="conditional",
        name="Check Approval Status",
        config={
            "condition": "status == 'completed'"
        }
    ))
    
    # Approved path
    builder.add_node(WorkflowNode(
        node_id="approved_action",
        node_type="tool",
        name="Process Approved Data",
        config={
            "tool_name": "data_transform",
            "parameters": {
                "input_data": "Workflow Approved - Proceeding",
                "operation": "uppercase"
            }
        }
    ))
    
    # Rejected path
    builder.add_node(WorkflowNode(
        node_id="rejected_action",
        node_type="tool",
        name="Handle Rejection",
        config={
            "tool_name": "data_transform",
            "parameters": {
                "input_data": "Workflow Rejected - Stopping",
                "operation": "uppercase"
            }
        }
    ))
    
    # End nodes
    builder.add_node(WorkflowNode(
        node_id="end_approved",
        node_type="end",
        name="End (Approved Path)"
    ))
    
    builder.add_node(WorkflowNode(
        node_id="end_rejected",
        node_type="end",
        name="End (Rejected Path)"
    ))
    
    # Add edges
    builder.add_edge(WorkflowEdge("start", "generate_data"))
    builder.add_edge(WorkflowEdge("generate_data", "calculate_sum"))
    builder.add_edge(WorkflowEdge("calculate_sum", "human_approval"))
    builder.add_edge(WorkflowEdge("human_approval", "check_approval"))
    builder.add_edge(WorkflowEdge("check_approval", "approved_action", condition="status == 'completed'"))
    builder.add_edge(WorkflowEdge("check_approval", "rejected_action", condition="status == 'rejected'"))
    builder.add_edge(WorkflowEdge("approved_action", "end_approved"))
    builder.add_edge(WorkflowEdge("rejected_action", "end_rejected"))
    
    return builder


def create_complex_workflow() -> WorkflowBuilder:
    """
    Create a complex workflow combining sequential, parallel, and HITL patterns.
    """
    builder = WorkflowBuilder(
        name="Complex Multi-Pattern Workflow",
        description="Demonstrates all workflow patterns in a single workflow",
        version="1.0.0"
    )
    
    # Sequential start
    builder.add_node(WorkflowNode(
        node_id="start",
        node_type="start",
        name="Start"
    ))
    
    builder.add_node(WorkflowNode(
        node_id="initial_analysis",
        node_type="tool",
        name="Initial Data Analysis",
        config={
            "tool_name": "text_analysis",
            "parameters": {"text": "{{input_data}}"}
        }
    ))
    
    # Parallel processing section
    builder.add_node(WorkflowNode(
        node_id="parallel_start",
        node_type="parallel",
        name="Start Parallel Processing"
    ))
    
    builder.add_node(WorkflowNode(
        node_id="parallel_branch1",
        node_type="tool",
        name="Parallel Branch 1",
        config={
            "tool_name": "data_transform",
            "parameters": {
                "input_data": "{{input_data}}",
                "operation": "uppercase"
            }
        }
    ))
    
    builder.add_node(WorkflowNode(
        node_id="parallel_branch2",
        node_type="tool",
        name="Parallel Branch 2",
        config={
            "tool_name": "random_number",
            "parameters": {
                "min_value": 1,
                "max_value": 50,
                "count": 3
            }
        }
    ))
    
    builder.add_node(WorkflowNode(
        node_id="parallel_end",
        node_type="parallel",
        name="End Parallel Processing"
    ))
    
    # Human review section
    builder.add_node(WorkflowNode(
        node_id="human_review",
        node_type="human",
        name="Quality Review",
        config={
            "assigned_to": "admin",
            "task_type": "review",
            "timeout": 7200
        }
    ))
    
    # Final sequential steps
    builder.add_node(WorkflowNode(
        node_id="final_calculation",
        node_type="tool",
        name="Final Calculation",
        config={
            "tool_name": "math_calculator",
            "parameters": {
                "operation": "multiply",
                "operand1": 42,
                "operand2": 2
            }
        }
    ))
    
    builder.add_node(WorkflowNode(
        node_id="end",
        node_type="end",
        name="End"
    ))
    
    # Add edges
    builder.add_edge(WorkflowEdge("start", "initial_analysis"))
    builder.add_edge(WorkflowEdge("initial_analysis", "parallel_start"))
    builder.add_edge(WorkflowEdge("parallel_start", "parallel_branch1"))
    builder.add_edge(WorkflowEdge("parallel_start", "parallel_branch2"))
    builder.add_edge(WorkflowEdge("parallel_branch1", "parallel_end"))
    builder.add_edge(WorkflowEdge("parallel_branch2", "parallel_end"))
    builder.add_edge(WorkflowEdge("parallel_end", "human_review"))
    builder.add_edge(WorkflowEdge("human_review", "final_calculation"))
    builder.add_edge(WorkflowEdge("final_calculation", "end"))
    
    builder.set_variable("input_data", "Complex Workflow Test Data")
    
    return builder


# Export all builders
__all__ = [
    'WorkflowBuilder',
    'WorkflowNode',
    'WorkflowEdge',
    'create_sequential_workflow',
    'create_parallel_workflow',
    'create_hitl_workflow',
    'create_complex_workflow'
]
