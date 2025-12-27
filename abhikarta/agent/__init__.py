"""
Agent Module - AI Agent management and execution.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.

Patent Pending: Certain architectural patterns and implementations described in this
software may be subject to patent applications.
"""

from .agent_manager import AgentManager, Agent, AgentType, AgentStatus
from .agent_template import AgentTemplateManager, AgentTemplate

__all__ = [
    'AgentManager', 
    'Agent', 
    'AgentType', 
    'AgentStatus',
    'AgentTemplateManager', 
    'AgentTemplate'
]
