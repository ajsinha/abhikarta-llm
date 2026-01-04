"""
Abhikarta SDK Client - Connect to Abhikarta-LLM Server
======================================================

A lightweight Python SDK for connecting to a running Abhikarta-LLM server.
Use this when you have Abhikarta-LLM deployed and want to interact with it
programmatically.

Quick Start:
    >>> from abhikarta_client import AbhikartaClient
    >>> 
    >>> # Connect to server
    >>> client = AbhikartaClient("http://localhost:5000")
    >>> 
    >>> # List agents
    >>> agents = client.agents.list()
    >>> 
    >>> # Execute an agent
    >>> result = client.agents.execute("agent-id", prompt="Hello!")
    >>> 
    >>> # Create new agent
    >>> agent = client.agents.create(
    ...     name="My Agent",
    ...     agent_type="react",
    ...     model="llama3.2:3b"
    ... )

For standalone usage without a server, use `abhikarta-sdk-embedded` instead.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.4.8
"""

__version__ = "1.4.8"
__author__ = "Ashutosh Sinha"
__email__ = "ajsinha@gmail.com"

from .client import (
    AbhikartaClient,
    ClientConfig,
)
from .agents import (
    AgentsClient,
    RemoteAgent,
)
from .workflows import (
    WorkflowsClient,
    RemoteWorkflow,
)
from .swarms import (
    SwarmsClient,
    RemoteSwarm,
)
from .organizations import (
    OrganizationsClient,
    RemoteOrganization,
)
from .scripts import (
    ScriptsClient,
)

__all__ = [
    # Version
    "__version__",
    "__author__",
    # Main client
    "AbhikartaClient",
    "ClientConfig",
    # Agents
    "AgentsClient",
    "RemoteAgent",
    # Workflows
    "WorkflowsClient",
    "RemoteWorkflow",
    # Swarms
    "SwarmsClient",
    "RemoteSwarm",
    # Organizations
    "OrganizationsClient",
    "RemoteOrganization",
    # Scripts
    "ScriptsClient",
]
