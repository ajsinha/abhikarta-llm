"""
Workflow Management Module

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | Email: ajsinha@gmail.com

Legal Notice: This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without explicit 
written permission from the copyright holder.

Patent Pending: Certain architectural patterns and implementations described in this module 
may be subject to patent applications.
"""

__version__ = "1.0.0"
__author__ = "Ashutosh Sinha"
__email__ = "ajsinha@gmail.com"

# Optional imports - only available when integrated with full Abhikarta system
__all__ = []

try:
    from workflow_management.workflow_db_handler import WorkflowDBHandler
    __all__.append('WorkflowDBHandler')
except ImportError:
    WorkflowDBHandler = None

try:
    from workflow_management.workflow_execution_engine import WorkflowExecutionEngine
    __all__.append('WorkflowExecutionEngine')
except ImportError:
    WorkflowExecutionEngine = None

try:
    from workflow_management.workflow_routes import WorkflowRoutes
    __all__.append('WorkflowRoutes')
except ImportError:
    WorkflowRoutes = None

# Always available - standalone components
try:
    from workflow_management.example_tools import get_tool, list_available_tools, EXAMPLE_TOOLS
    __all__.extend(['get_tool', 'list_available_tools', 'EXAMPLE_TOOLS'])
except ImportError:
    pass

try:
    from workflow_management.workflow_builders import (
        WorkflowBuilder, WorkflowNode, WorkflowEdge,
        create_sequential_workflow, create_parallel_workflow,
        create_hitl_workflow, create_complex_workflow
    )
    __all__.extend([
        'WorkflowBuilder', 'WorkflowNode', 'WorkflowEdge',
        'create_sequential_workflow', 'create_parallel_workflow',
        'create_hitl_workflow', 'create_complex_workflow'
    ])
except ImportError:
    pass
