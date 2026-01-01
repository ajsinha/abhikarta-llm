#!/usr/bin/env python3
"""
Hierarchical AI Organization Example
=====================================

This example demonstrates a hierarchical AI organization with:
- CEO: Sets strategy and makes final decisions
- Product Manager: Defines requirements and priorities
- Tech Lead: Makes technical decisions
- Developer: Implements solutions
- QA: Reviews and validates output

Requirements:
    - Ollama running with llama3.2:3b model
    - pip install langchain-ollama

Usage:
    python -m abhikarta.examples.aiorg.hierarchical_org
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://192.168.2.36:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")


# AI Organization Definition JSON
AIORG_DEFINITION = {
    "org_id": "software_dev_org",
    "name": "AI Software Development Organization",
    "description": "Hierarchical organization for software development tasks",
    "structure_type": "hierarchical",
    "levels": [
        {
            "level": 0,
            "name": "Executive",
            "agents": [
                {
                    "agent_id": "ceo",
                    "name": "CEO",
                    "role": "executive",
                    "responsibilities": ["strategy", "final_approval"],
                    "system_prompt": "You are the CEO. Set strategic direction and make final decisions. Be concise and decisive."
                }
            ]
        },
        {
            "level": 1,
            "name": "Management",
            "agents": [
                {
                    "agent_id": "product_manager",
                    "name": "Product Manager",
                    "role": "manager",
                    "reports_to": "ceo",
                    "responsibilities": ["requirements", "prioritization"],
                    "system_prompt": "You are a Product Manager. Define clear requirements and prioritize features. Focus on user value."
                },
                {
                    "agent_id": "tech_lead",
                    "name": "Tech Lead",
                    "role": "manager",
                    "reports_to": "ceo",
                    "responsibilities": ["architecture", "technical_decisions"],
                    "system_prompt": "You are a Tech Lead. Make sound technical decisions and guide implementation. Consider scalability and maintainability."
                }
            ]
        },
        {
            "level": 2,
            "name": "Individual Contributors",
            "agents": [
                {
                    "agent_id": "developer",
                    "name": "Developer",
                    "role": "worker",
                    "reports_to": "tech_lead",
                    "responsibilities": ["implementation", "coding"],
                    "system_prompt": "You are a Developer. Write clean, efficient code and implement features. Follow best practices."
                },
                {
                    "agent_id": "qa",
                    "name": "QA Engineer",
                    "role": "worker",
                    "reports_to": "product_manager",
                    "responsibilities": ["testing", "quality"],
                    "system_prompt": "You are a QA Engineer. Review work for quality and identify issues. Be thorough but constructive."
                }
            ]
        }
    ],
    "workflows": [
        {
            "name": "feature_development",
            "steps": [
                {"agent": "ceo", "action": "approve_initiative"},
                {"agent": "product_manager", "action": "define_requirements"},
                {"agent": "tech_lead", "action": "design_solution"},
                {"agent": "developer", "action": "implement"},
                {"agent": "qa", "action": "review"},
                {"agent": "ceo", "action": "final_approval"}
            ]
        }
    ],
    "llm_config": {
        "provider": "ollama",
        "model": "llama3.2:3b",
        "temperature": 0.7
    }
}


class OrgLevel(Enum):
    EXECUTIVE = 0
    MANAGEMENT = 1
    WORKER = 2


@dataclass
class OrgAgent:
    """Agent in the organization."""
    agent_id: str
    name: str
    role: str
    level: int
    system_prompt: str
    reports_to: Optional[str] = None
    direct_reports: List[str] = field(default_factory=list)


class AIOrganization:
    """Hierarchical AI organization."""
    
    def __init__(self, llm):
        self.llm = llm
        self.agents: Dict[str, OrgAgent] = {}
        self.communication_log: List[Dict[str, Any]] = []
    
    def add_agent(self, agent_id: str, name: str, role: str, level: int,
                  system_prompt: str, reports_to: Optional[str] = None):
        """Add an agent to the organization."""
        agent = OrgAgent(
            agent_id=agent_id,
            name=name,
            role=role,
            level=level,
            system_prompt=system_prompt,
            reports_to=reports_to
        )
        self.agents[agent_id] = agent
        
        # Update reporting structure
        if reports_to and reports_to in self.agents:
            self.agents[reports_to].direct_reports.append(agent_id)
        
        logger.info(f"Added agent: {name} (Level {level}, reports to: {reports_to})")
    
    def communicate(self, from_agent: str, to_agent: str, message: str, context: str = "") -> str:
        """Send a message from one agent to another and get response."""
        sender = self.agents.get(from_agent)
        receiver = self.agents.get(to_agent)
        
        if not sender or not receiver:
            return "Agent not found"
        
        prompt = f"""{receiver.system_prompt}

You are receiving a message from {sender.name} ({sender.role}):

{message}

Context:
{context}

Please provide your response:"""
        
        logger.info(f"Communication: {sender.name} -> {receiver.name}")
        response = self.llm.invoke(prompt)
        
        self.communication_log.append({
            "from": from_agent,
            "to": to_agent,
            "message": message,
            "response": response.content
        })
        
        return response.content
    
    def cascade_down(self, agent_id: str, directive: str, context: str = "") -> Dict[str, str]:
        """Cascade a directive from a manager to their reports."""
        agent = self.agents.get(agent_id)
        if not agent:
            return {}
        
        results = {}
        for report_id in agent.direct_reports:
            result = self.communicate(agent_id, report_id, directive, context)
            results[report_id] = result
        
        return results
    
    def report_up(self, agent_id: str, report: str, context: str = "") -> str:
        """Send a report up to the manager."""
        agent = self.agents.get(agent_id)
        if not agent or not agent.reports_to:
            return "No manager to report to"
        
        return self.communicate(agent_id, agent.reports_to, report, context)
    
    def run_workflow(self, workflow_name: str, task: str) -> Dict[str, Any]:
        """Run a predefined workflow."""
        # For this example, we'll run the feature_development workflow
        results = {}
        context = f"Task: {task}"
        
        print(f"\n{'='*60}")
        print(f"WORKFLOW: {workflow_name}")
        print(f"Task: {task}")
        print(f"{'='*60}")
        
        # Step 1: CEO approves initiative
        print("\n--- Step 1: CEO Initiative Approval ---")
        ceo_response = self.communicate(
            "ceo", "ceo",
            f"Should we proceed with this initiative: {task}? Provide a brief yes/no with reasoning.",
            context
        )
        results["ceo_approval"] = ceo_response
        print(f"CEO: {ceo_response}")
        context += f"\n\nCEO Approval: {ceo_response}"
        
        # Step 2: Product Manager defines requirements
        print("\n--- Step 2: Product Manager Requirements ---")
        pm_response = self.communicate(
            "ceo", "product_manager",
            f"Define 3 key requirements for: {task}",
            context
        )
        results["requirements"] = pm_response
        print(f"PM: {pm_response}")
        context += f"\n\nRequirements: {pm_response}"
        
        # Step 3: Tech Lead designs solution
        print("\n--- Step 3: Tech Lead Design ---")
        tl_response = self.communicate(
            "product_manager", "tech_lead",
            f"Design a technical approach for implementing these requirements.",
            context
        )
        results["design"] = tl_response
        print(f"Tech Lead: {tl_response}")
        context += f"\n\nTechnical Design: {tl_response}"
        
        # Step 4: Developer implements
        print("\n--- Step 4: Developer Implementation ---")
        dev_response = self.communicate(
            "tech_lead", "developer",
            "Describe how you would implement this. Provide a brief code outline or pseudocode.",
            context
        )
        results["implementation"] = dev_response
        print(f"Developer: {dev_response}")
        context += f"\n\nImplementation: {dev_response}"
        
        # Step 5: QA reviews
        print("\n--- Step 5: QA Review ---")
        qa_response = self.communicate(
            "product_manager", "qa",
            "Review the implementation plan. What test cases would you create? Any concerns?",
            context
        )
        results["qa_review"] = qa_response
        print(f"QA: {qa_response}")
        context += f"\n\nQA Review: {qa_response}"
        
        # Step 6: CEO final approval
        print("\n--- Step 6: CEO Final Approval ---")
        final_response = self.communicate(
            "qa", "ceo",
            "Based on all the work done, provide final approval or feedback.",
            context
        )
        results["final_approval"] = final_response
        print(f"CEO Final: {final_response}")
        
        return results


def run_hierarchical_org():
    """Run the hierarchical organization example."""
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
    
    # Create organization
    org = AIOrganization(llm)
    
    # Add agents from definition
    for level_def in AIORG_DEFINITION["levels"]:
        level = level_def["level"]
        for agent_def in level_def["agents"]:
            org.add_agent(
                agent_id=agent_def["agent_id"],
                name=agent_def["name"],
                role=agent_def["role"],
                level=level,
                system_prompt=agent_def["system_prompt"],
                reports_to=agent_def.get("reports_to")
            )
    
    # Run a workflow
    task = "Build a REST API endpoint for user authentication"
    results = org.run_workflow("feature_development", task)
    
    print("\n" + "="*60)
    print("WORKFLOW COMPLETE")
    print("="*60)
    print(f"Total communications: {len(org.communication_log)}")
    print("="*60)
    
    return results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hierarchical AI Organization Example")
    parser.add_argument("--json", action="store_true", help="Print organization JSON definition")
    parser.add_argument("--host", default=OLLAMA_HOST, help="Ollama host URL")
    parser.add_argument("--model", default=OLLAMA_MODEL, help="Ollama model name")
    
    args = parser.parse_args()
    
    if args.json:
        print(json.dumps(AIORG_DEFINITION, indent=2))
        return
    
    os.environ["OLLAMA_HOST"] = args.host
    os.environ["OLLAMA_MODEL"] = args.model
    
    run_hierarchical_org()


if __name__ == "__main__":
    main()
