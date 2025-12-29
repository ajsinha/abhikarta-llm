"""
Abhikarta-LLM - AI Agent Design & Orchestration Platform

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.
"""

__version__ = "1.3.0"
__author__ = "Ashutosh Sinha"
__email__ = "ajsinha@gmail.com"

# Actor System exports (v1.3.0)
from abhikarta.actor import (
    Actor,
    TypedActor,
    ActorRef,
    ActorSystem,
    Props,
    PropsBuilder,
    create_actor_system,
    # Message types
    PoisonPill,
    Kill,
    Terminated,
    # Supervision
    OneForOneStrategy,
    AllForOneStrategy,
    Directive,
    # Patterns
    RouterActor,
    EventBus,
    CircuitBreaker,
)
