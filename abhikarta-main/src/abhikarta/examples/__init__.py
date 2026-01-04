"""
Abhikarta-LLM Examples Module
=============================

Runnable examples for workflows, agents, swarms, and AI organizations.

Usage:
    # From command line:
    python -m abhikarta.examples.workflow.simple_sequential
    python -m abhikarta.examples.agent.react_agent
    python -m abhikarta.examples.swarm.basic_swarm
    python -m abhikarta.examples.aiorg.hierarchical_org

    # From PyCharm:
    Right-click on any example file and select "Run"

Configuration:
    All examples use Ollama with llama3.2:3b by default.
    Set OLLAMA_HOST environment variable to change the Ollama server address.
    Default: http://192.168.2.36:11434
"""

__version__ = "1.4.8"
__all__ = ["workflow", "agent", "swarm", "aiorg"]
