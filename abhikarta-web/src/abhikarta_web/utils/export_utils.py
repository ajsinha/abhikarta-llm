"""
Export Utilities for Abhikarta-LLM entities.

Provides code generation for JSON and Python SDK exports for:
- Agents
- Workflows  
- Swarms
- AI Organizations

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import json
from typing import Any, Dict


# Valid status transitions for approval workflow
STATUS_TRANSITIONS = {
    'draft': ['testing', 'archived'],
    'testing': ['draft', 'pending_review', 'archived'],
    'pending_review': ['testing', 'approved', 'draft'],
    'approved': ['published', 'draft'],
    'published': ['deprecated', 'draft'],
    'deprecated': ['published', 'archived'],
    'archived': ['draft'],
}


def is_valid_transition(current_status: str, new_status: str) -> bool:
    """Check if a status transition is valid."""
    allowed = STATUS_TRANSITIONS.get(current_status, [])
    return new_status in allowed


def get_allowed_transitions(current_status: str) -> list:
    """Get list of allowed status transitions from current status."""
    return STATUS_TRANSITIONS.get(current_status, [])


def generate_workflow_python_code(workflow) -> str:
    """Generate Python SDK code for a workflow configuration."""
    
    # Handle both dict and object
    if hasattr(workflow, 'to_dict'):
        wf_dict = workflow.to_dict()
    elif isinstance(workflow, dict):
        wf_dict = workflow
    else:
        wf_dict = dict(workflow)
    
    name = wf_dict.get('name', 'Unknown')
    workflow_id = wf_dict.get('workflow_id', '')
    description = wf_dict.get('description', '')
    
    code_lines = [
        '"""',
        f'Workflow: {name}',
        f'Description: {description}',
        f'Generated from Abhikarta-LLM',
        '"""',
        '',
        'from abhikarta_client import AbhikartaClient',
        'from abhikarta_embedded import Workflow, WorkflowNode',
        '',
        '# Initialize client',
        'client = AbhikartaClient(',
        '    base_url="http://localhost:5000",',
        '    api_key="your_api_key_here"',
        ')',
        '',
        '# Workflow configuration',
        f'WORKFLOW_ID = "{workflow_id}"',
        f'WORKFLOW_NAME = "{name}"',
        '',
        '# DAG Definition',
        'dag_definition = ' + json.dumps(wf_dict.get('dag_definition', {}), indent=4, default=str),
        '',
        '# Input/Output Schemas',
        'input_schema = ' + json.dumps(wf_dict.get('input_schema', {}), indent=4),
        'output_schema = ' + json.dumps(wf_dict.get('output_schema', {}), indent=4),
        '',
        '# Full Configuration',
        'workflow_config = ' + json.dumps(wf_dict, indent=4, default=str),
        '',
        '',
        '# ============================================',
        '# Option 1: Execute existing workflow via API',
        '# ============================================',
        '',
        'def execute_workflow(inputs: dict):',
        '    """Execute the workflow via API."""',
        '    result = client.workflows.execute(',
        f'        workflow_id="{workflow_id}",',
        '        inputs=inputs',
        '    )',
        '    return result',
        '',
        '',
        '# ============================================',
        '# Option 2: Create workflow programmatically',
        '# ============================================',
        '',
        'def create_workflow_from_dag():',
        '    """Create workflow using SDK."""',
        '    workflow = Workflow(',
        f'        name="{name}",',
        f'        description="{description}",',
        '        dag_definition=dag_definition',
        '    )',
        '    return workflow',
        '',
        '',
        '# ============================================',
        '# Option 3: Local embedded execution',
        '# ============================================',
        '',
        'def run_local(inputs: dict):',
        '    """Run workflow locally using embedded SDK."""',
        '    from abhikarta_embedded import create_workflow',
        '    ',
        '    workflow = create_workflow(config=workflow_config)',
        '    result = workflow.execute(inputs)',
        '    return result',
        '',
        '',
        'if __name__ == "__main__":',
        '    print(f"Workflow: {WORKFLOW_NAME}")',
        '    print(f"ID: {WORKFLOW_ID}")',
        '    ',
        '    # Example execution',
        '    # result = execute_workflow({"input": "value"})',
        '    # print(result)',
        '',
    ]
    
    return '\n'.join(code_lines)


def generate_swarm_python_code(swarm) -> str:
    """Generate Python SDK code for a swarm configuration."""
    
    # Handle both dict and object
    if hasattr(swarm, 'to_dict'):
        swarm_dict = swarm.to_dict()
    elif isinstance(swarm, dict):
        swarm_dict = swarm
    else:
        swarm_dict = dict(swarm)
    
    name = swarm_dict.get('name', 'Unknown')
    swarm_id = swarm_dict.get('swarm_id', '')
    description = swarm_dict.get('description', '')
    
    code_lines = [
        '"""',
        f'Swarm: {name}',
        f'Description: {description}',
        f'Generated from Abhikarta-LLM',
        '"""',
        '',
        'from abhikarta_client import AbhikartaClient',
        'from abhikarta_embedded import Swarm, SwarmAgent',
        '',
        '# Initialize client',
        'client = AbhikartaClient(',
        '    base_url="http://localhost:5000",',
        '    api_key="your_api_key_here"',
        ')',
        '',
        '# Swarm configuration',
        f'SWARM_ID = "{swarm_id}"',
        f'SWARM_NAME = "{name}"',
        '',
        '# Swarm Definition',
        'definition = ' + json.dumps(swarm_dict.get('definition_json', {}), indent=4, default=str),
        '',
        '# Swarm Configuration',
        'config = ' + json.dumps(swarm_dict.get('config_json', {}), indent=4, default=str),
        '',
        '# Full Swarm Data',
        'swarm_data = ' + json.dumps(swarm_dict, indent=4, default=str),
        '',
        '',
        '# ============================================',
        '# Option 1: Control existing swarm via API',
        '# ============================================',
        '',
        'def start_swarm():',
        '    """Start the swarm via API."""',
        f'    return client.swarms.start("{swarm_id}")',
        '',
        'def stop_swarm():',
        '    """Stop the swarm via API."""',
        f'    return client.swarms.stop("{swarm_id}")',
        '',
        'def get_swarm_status():',
        '    """Get swarm status."""',
        f'    return client.swarms.get("{swarm_id}")',
        '',
        '',
        '# ============================================',
        '# Option 2: Create swarm programmatically',
        '# ============================================',
        '',
        'def create_swarm():',
        '    """Create swarm using SDK."""',
        '    swarm = Swarm(',
        f'        name="{name}",',
        f'        description="{description}",',
        '        definition=definition,',
        '        config=config',
        '    )',
        '    return swarm',
        '',
        '',
        '# ============================================',
        '# Option 3: Local embedded execution',
        '# ============================================',
        '',
        'def run_local():',
        '    """Run swarm locally using embedded SDK."""',
        '    from abhikarta_embedded import create_swarm',
        '    ',
        '    swarm = create_swarm(config=swarm_data)',
        '    swarm.start()',
        '    return swarm',
        '',
        '',
        'if __name__ == "__main__":',
        '    print(f"Swarm: {SWARM_NAME}")',
        '    print(f"ID: {SWARM_ID}")',
        '    ',
        '    # Start/Stop via API',
        '    # start_swarm()',
        '    # stop_swarm()',
        '',
    ]
    
    return '\n'.join(code_lines)


def generate_aiorg_python_code(org) -> str:
    """Generate Python SDK code for an AI organization configuration."""
    
    # Handle both dict and object
    if hasattr(org, 'to_dict'):
        org_dict = org.to_dict()
    elif isinstance(org, dict):
        org_dict = org
    else:
        org_dict = dict(org)
    
    name = org_dict.get('name', 'Unknown')
    org_id = org_dict.get('org_id', '')
    description = org_dict.get('description', '')
    
    code_lines = [
        '"""',
        f'AI Organization: {name}',
        f'Description: {description}',
        f'Generated from Abhikarta-LLM',
        '"""',
        '',
        'from abhikarta_client import AbhikartaClient',
        'from abhikarta_embedded import AIOrganization, AINode',
        '',
        '# Initialize client',
        'client = AbhikartaClient(',
        '    base_url="http://localhost:5000",',
        '    api_key="your_api_key_here"',
        ')',
        '',
        '# Organization configuration',
        f'ORG_ID = "{org_id}"',
        f'ORG_NAME = "{name}"',
        '',
        '# Organization Config',
        'org_config = ' + json.dumps(org_dict.get('config', {}), indent=4, default=str),
        '',
        '# Full Organization Data',
        'org_data = ' + json.dumps(org_dict, indent=4, default=str),
        '',
        '',
        '# ============================================',
        '# Option 1: Interact with organization via API',
        '# ============================================',
        '',
        'def get_organization():',
        '    """Get organization details."""',
        f'    return client.aiorg.get("{org_id}")',
        '',
        'def list_nodes():',
        '    """List all nodes in the organization."""',
        f'    return client.aiorg.list_nodes("{org_id}")',
        '',
        'def submit_task(task_data: dict):',
        '    """Submit a task to the organization."""',
        f'    return client.aiorg.submit_task("{org_id}", task_data)',
        '',
        '',
        '# ============================================',
        '# Option 2: Create organization programmatically',
        '# ============================================',
        '',
        'def create_organization():',
        '    """Create AI organization using SDK."""',
        '    org = AIOrganization(',
        f'        name="{name}",',
        f'        description="{description}",',
        '        config=org_config',
        '    )',
        '    return org',
        '',
        '',
        '# ============================================',
        '# Option 3: Local embedded execution',
        '# ============================================',
        '',
        'def run_local():',
        '    """Run organization locally using embedded SDK."""',
        '    from abhikarta_embedded import create_ai_organization',
        '    ',
        '    org = create_ai_organization(config=org_data)',
        '    org.activate()',
        '    return org',
        '',
        '',
        'if __name__ == "__main__":',
        '    print(f"AI Organization: {ORG_NAME}")',
        '    print(f"ID: {ORG_ID}")',
        '    ',
        '    # Get info via API',
        '    # info = get_organization()',
        '    # print(info)',
        '',
    ]
    
    return '\n'.join(code_lines)
