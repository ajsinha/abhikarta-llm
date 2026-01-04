#!/usr/bin/env python3
"""
Basic Swarm Example
===================

This example demonstrates a multi-agent swarm where agents collaborate
to analyze a topic from different perspectives.

Swarm Structure:
- Coordinator Agent: Routes tasks and synthesizes results
- Researcher Agent: Gathers facts and information
- Analyst Agent: Analyzes data and provides insights
- Writer Agent: Creates final report

Requirements:
    - Ollama running with llama3.2:3b model
    - pip install langchain-ollama

Usage:
    python -m abhikarta.examples.swarm.basic_swarm
"""

import os
import json
import logging
from typing import Dict, Any, List
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://192.168.2.36:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")


# Swarm Definition JSON
SWARM_DEFINITION = {
    "swarm_id": "basic_research_swarm",
    "name": "Research Analysis Swarm",
    "description": "Multi-agent swarm for collaborative research and analysis",
    "swarm_type": "collaborative",
    "coordination_strategy": "round_robin",
    "agents": [
        {
            "agent_id": "coordinator",
            "name": "Coordinator",
            "role": "coordinator",
            "system_prompt": "You are a coordinator. Route tasks to appropriate agents and synthesize their outputs.",
            "llm_config": {"provider": "ollama", "model": "llama3.2:3b"}
        },
        {
            "agent_id": "researcher",
            "name": "Researcher",
            "role": "worker",
            "system_prompt": "You are a researcher. Find and present factual information about topics.",
            "llm_config": {"provider": "ollama", "model": "llama3.2:3b"}
        },
        {
            "agent_id": "analyst",
            "name": "Analyst",
            "role": "worker",
            "system_prompt": "You are an analyst. Analyze information and provide insights and implications.",
            "llm_config": {"provider": "ollama", "model": "llama3.2:3b"}
        },
        {
            "agent_id": "writer",
            "name": "Writer",
            "role": "worker",
            "system_prompt": "You are a writer. Create clear, well-structured reports from provided information.",
            "llm_config": {"provider": "ollama", "model": "llama3.2:3b"}
        }
    ],
    "communication_channels": [
        {"from": "coordinator", "to": "researcher"},
        {"from": "coordinator", "to": "analyst"},
        {"from": "coordinator", "to": "writer"},
        {"from": "researcher", "to": "coordinator"},
        {"from": "analyst", "to": "coordinator"},
        {"from": "writer", "to": "coordinator"}
    ]
}


@dataclass
class Agent:
    """Simple agent class."""
    agent_id: str
    name: str
    role: str
    system_prompt: str
    llm: Any = None


class Swarm:
    """Simple swarm implementation."""
    
    def __init__(self, llm):
        self.llm = llm
        self.agents: Dict[str, Agent] = {}
        self.messages: List[Dict[str, Any]] = []
    
    def add_agent(self, agent_id: str, name: str, role: str, system_prompt: str):
        """Add an agent to the swarm."""
        self.agents[agent_id] = Agent(
            agent_id=agent_id,
            name=name,
            role=role,
            system_prompt=system_prompt,
            llm=self.llm
        )
        logger.info(f"Added agent: {name} ({role})")
    
    def run_agent(self, agent_id: str, task: str, context: str = "") -> str:
        """Run a specific agent with a task."""
        agent = self.agents.get(agent_id)
        if not agent:
            return f"Agent {agent_id} not found"
        
        prompt = f"""{agent.system_prompt}

Context:
{context}

Task: {task}

Please provide your response:"""
        
        logger.info(f"Running agent: {agent.name}")
        response = self.llm.invoke(prompt)
        
        self.messages.append({
            "agent": agent_id,
            "task": task,
            "response": response.content
        })
        
        return response.content
    
    def run_parallel(self, tasks: Dict[str, str], context: str = "") -> Dict[str, str]:
        """Run multiple agents in parallel."""
        results = {}
        
        def run_task(agent_id: str, task: str) -> tuple:
            result = self.run_agent(agent_id, task, context)
            return (agent_id, result)
        
        with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            futures = [executor.submit(run_task, aid, task) for aid, task in tasks.items()]
            for future in futures:
                agent_id, result = future.result()
                results[agent_id] = result
        
        return results


def run_basic_swarm():
    """Run the basic swarm example."""
    try:
        from langchain_ollama import ChatOllama
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Install with: pip install langchain-ollama")
        return
    
    logger.info(f"Using Ollama at {OLLAMA_HOST} with model {OLLAMA_MODEL}")
    
    # Initialize LLM
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_HOST,
        temperature=0.7
    )
    
    # Create swarm
    swarm = Swarm(llm)
    
    # Add agents from definition
    for agent_def in SWARM_DEFINITION["agents"]:
        swarm.add_agent(
            agent_id=agent_def["agent_id"],
            name=agent_def["name"],
            role=agent_def["role"],
            system_prompt=agent_def["system_prompt"]
        )
    
    # Topic to research
    topic = "The impact of large language models on software development"
    
    print("="*60)
    print(f"SWARM ANALYSIS: {topic}")
    print("="*60)
    
    # Step 1: Coordinator creates research plan
    print("\n--- Step 1: Coordinator Planning ---")
    plan = swarm.run_agent(
        "coordinator",
        f"Create a brief research plan for analyzing: {topic}. List 3 key areas to investigate."
    )
    print(f"Plan:\n{plan}")
    
    # Step 2: Researcher and Analyst work in parallel
    print("\n--- Step 2: Research & Analysis (Parallel) ---")
    parallel_results = swarm.run_parallel({
        "researcher": f"Research key facts about: {topic}. Provide 3-4 important points.",
        "analyst": f"Analyze the implications of: {topic}. What are the pros and cons?"
    }, context=f"Research plan: {plan}")
    
    print(f"\nResearcher Output:\n{parallel_results['researcher']}")
    print(f"\nAnalyst Output:\n{parallel_results['analyst']}")
    
    # Step 3: Writer creates final report
    print("\n--- Step 3: Writer Creates Report ---")
    context = f"""
Research findings:
{parallel_results['researcher']}

Analysis:
{parallel_results['analyst']}
"""
    
    report = swarm.run_agent(
        "writer",
        "Create a concise 2-paragraph summary report based on the research and analysis provided.",
        context=context
    )
    print(f"\nFinal Report:\n{report}")
    
    # Step 4: Coordinator provides final synthesis
    print("\n--- Step 4: Coordinator Synthesis ---")
    synthesis = swarm.run_agent(
        "coordinator",
        "Provide a 2-3 sentence executive summary of the swarm's findings.",
        context=f"Full report:\n{report}"
    )
    
    print("="*60)
    print("EXECUTIVE SUMMARY")
    print("="*60)
    print(synthesis)
    print("="*60)
    
    return {
        "topic": topic,
        "plan": plan,
        "research": parallel_results["researcher"],
        "analysis": parallel_results["analyst"],
        "report": report,
        "summary": synthesis
    }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Basic Swarm Example")
    parser.add_argument("--json", action="store_true", help="Print swarm JSON definition")
    parser.add_argument("--host", default=OLLAMA_HOST, help="Ollama host URL")
    parser.add_argument("--model", default=OLLAMA_MODEL, help="Ollama model name")
    
    args = parser.parse_args()
    
    if args.json:
        print(json.dumps(SWARM_DEFINITION, indent=2))
        return
    
    os.environ["OLLAMA_HOST"] = args.host
    os.environ["OLLAMA_MODEL"] = args.model
    
    run_basic_swarm()


if __name__ == "__main__":
    main()
