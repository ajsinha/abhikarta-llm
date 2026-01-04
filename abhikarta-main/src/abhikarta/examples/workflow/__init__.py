"""
Workflow Examples
=================

Examples demonstrating different workflow patterns.

Available Examples:
- simple_sequential: Basic sequential workflow (input -> process -> output)
- parallel_processing: Parallel execution with split and join
- conditional_workflow: Workflow with branching logic
- code_injection: Workflow using Python code nodes
- hitl_workflow: Human-in-the-loop approval workflow

Usage:
    python -m abhikarta.examples.workflow.simple_sequential
"""

__all__ = [
    "simple_sequential",
    "parallel_processing", 
    "conditional_workflow",
    "code_injection",
    "hitl_workflow"
]
