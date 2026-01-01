#!/usr/bin/env python3
"""
Research Assistant Agent Example

A sophisticated research assistant agent that can:
1. Conduct comprehensive research on any topic
2. Synthesize information from multiple perspectives
3. Maintain conversation context for follow-up questions
4. Produce well-structured research outputs

Usage:
    python research_assistant.py "Your research question"
    python research_assistant.py --interactive
    python research_assistant.py --demo

Copyright © 2025-2030 Abhikarta. All Rights Reserved.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """A single turn in the conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ResearchSession:
    """A research session with history."""
    session_id: str
    topic: str = ""
    history: List[ConversationTurn] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ResearchAssistant:
    """Research Assistant Agent implementation."""
    
    SYSTEM_PROMPT = """You are an expert Research Assistant with deep capabilities in investigation and analysis.

Your Core Competencies:
1. SYSTEMATIC RESEARCH
   - Break down complex topics into researchable components
   - Identify key questions that need answering
   - Map relationships between concepts

2. MULTI-PERSPECTIVE ANALYSIS
   - Consider multiple viewpoints and sources
   - Identify areas of consensus and disagreement
   - Present balanced analysis

3. CRITICAL EVALUATION
   - Assess evidence quality and reliability
   - Identify potential biases and limitations
   - Distinguish facts from opinions

4. KNOWLEDGE SYNTHESIS
   - Combine findings into coherent insights
   - Highlight patterns and connections
   - Draw well-supported conclusions

5. CLEAR COMMUNICATION
   - Present findings in structured format
   - Use appropriate detail level
   - Provide actionable recommendations

Research Methodology:
- Start with understanding the scope and goals
- Break complex topics into manageable parts
- Consider multiple perspectives
- Synthesize findings systematically
- Acknowledge limitations and uncertainties

Output Format Guidelines:
- Use clear section headers
- Include bullet points for key findings
- Provide confidence levels where appropriate
- End with actionable insights or next steps

Remember: Maintain intellectual honesty about what you know vs. don't know."""

    def __init__(self, llm_config: Dict[str, Any] = None):
        """Initialize the research assistant.
        
        Args:
            llm_config: LLM configuration dictionary
        """
        self.llm_config = llm_config or {
            "provider": "ollama",
            "model": "llama3.2:3b",
            "base_url": os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
            "temperature": 0.5
        }
        self.llm = None
        self.session = ResearchSession(
            session_id=f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        )
        self.max_context_turns = 10
    
    def _create_llm(self):
        """Create LLM instance."""
        if self.llm is not None:
            return self.llm
        
        try:
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(
                model=self.llm_config.get("model", "llama3.2:3b"),
                base_url=self.llm_config.get("base_url", "http://localhost:11434"),
                temperature=self.llm_config.get("temperature", 0.5)
            )
            logger.info(f"LLM initialized: {self.llm_config['model']}")
            return self.llm
        except ImportError:
            raise ImportError("langchain-ollama required. Install: pip install langchain-ollama")
    
    def _build_context(self) -> str:
        """Build conversation context from history."""
        if not self.session.history:
            return ""
        
        # Get recent turns for context
        recent_turns = self.session.history[-self.max_context_turns:]
        
        context_parts = ["CONVERSATION HISTORY:"]
        for turn in recent_turns:
            prefix = "User" if turn.role == "user" else "Assistant"
            # Truncate long responses in context
            content = turn.content[:500] + "..." if len(turn.content) > 500 else turn.content
            context_parts.append(f"{prefix}: {content}")
        
        return "\n".join(context_parts)
    
    def _invoke_llm(self, prompt: str) -> str:
        """Invoke the LLM with a prompt."""
        llm = self._create_llm()
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def research(self, query: str) -> str:
        """Conduct research on a query.
        
        Args:
            query: The research question or topic
            
        Returns:
            Research response
        """
        # Update session topic if this is first query
        if not self.session.topic:
            self.session.topic = query[:100]
        
        # Build context from history
        context = self._build_context()
        
        # Create prompt
        prompt = f"""{self.SYSTEM_PROMPT}

{context}

USER QUERY: {query}

Provide a comprehensive research response. If this relates to previous conversation, build upon prior findings. Structure your response clearly with appropriate sections."""
        
        # Get response
        logger.info(f"Researching: {query[:50]}...")
        response = self._invoke_llm(prompt)
        
        # Update history
        self.session.history.append(ConversationTurn(role="user", content=query))
        self.session.history.append(ConversationTurn(role="assistant", content=response))
        
        # Extract key findings (simple extraction)
        if "KEY FINDING" in response.upper() or "FINDING" in response.upper():
            self.session.findings.append(f"Query: {query[:50]}... - Response recorded")
        
        return response
    
    def summarize_session(self) -> str:
        """Summarize the research session."""
        if not self.session.history:
            return "No research conducted in this session."
        
        context = self._build_context()
        
        prompt = f"""{self.SYSTEM_PROMPT}

{context}

Please provide a comprehensive summary of our research session:
1. Main topics explored
2. Key findings across all queries
3. Patterns or connections identified
4. Outstanding questions
5. Recommended next steps"""
        
        return self._invoke_llm(prompt)
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current session."""
        return {
            "session_id": self.session.session_id,
            "topic": self.session.topic,
            "turns": len(self.session.history),
            "queries": len([t for t in self.session.history if t.role == "user"]),
            "created_at": self.session.created_at,
            "findings_count": len(self.session.findings)
        }
    
    def export_session(self, filepath: str = None) -> str:
        """Export session to JSON file.
        
        Args:
            filepath: Optional output path
            
        Returns:
            Path to exported file
        """
        if not filepath:
            filepath = f"research_session_{self.session.session_id}.json"
        
        data = {
            "session_id": self.session.session_id,
            "topic": self.session.topic,
            "created_at": self.session.created_at,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "conversation": [
                {"role": t.role, "content": t.content, "timestamp": t.timestamp}
                for t in self.session.history
            ],
            "findings": self.session.findings,
            "llm_config": {k: v for k, v in self.llm_config.items() if k != "api_key"}
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Session exported to: {filepath}")
        return filepath
    
    def clear_history(self):
        """Clear conversation history."""
        self.session = ResearchSession(
            session_id=f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        )
        logger.info("Session cleared")


def run_demo(assistant: ResearchAssistant):
    """Run a demonstration of the research assistant."""
    print("\n" + "=" * 60)
    print("🔬 RESEARCH ASSISTANT DEMONSTRATION")
    print("=" * 60)
    
    demo_queries = [
        "What are the key principles of effective software architecture?",
        "How do microservices compare to monolithic architectures?",
        "What are the best practices for designing scalable systems?",
        "Summarize what we've learned about software architecture."
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print("-" * 40)
        
        response = assistant.research(query)
        
        # Print truncated response for demo
        if len(response) > 1000:
            print(response[:1000] + "\n... [truncated]")
        else:
            print(response)
        
        print()
    
    print("\n" + "=" * 60)
    print("📊 SESSION SUMMARY")
    print("=" * 60)
    
    summary = assistant.summarize_session()
    print(summary)
    
    print("\n" + "=" * 60)
    print("ℹ️  SESSION INFO")
    print("=" * 60)
    info = assistant.get_session_info()
    for key, value in info.items():
        print(f"  {key}: {value}")


def run_interactive(assistant: ResearchAssistant):
    """Run interactive research session."""
    print("\n" + "=" * 60)
    print("🔬 RESEARCH ASSISTANT - Interactive Mode")
    print("=" * 60)
    print("\nCommands:")
    print("  /summary  - Summarize session")
    print("  /info     - Show session info")
    print("  /export   - Export session")
    print("  /clear    - Clear history")
    print("  /quit     - Exit")
    print("\nEnter your research questions:\n")
    
    while True:
        try:
            query = input("🔍 > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
        
        if not query:
            continue
        
        # Handle commands
        if query.startswith("/"):
            cmd = query.lower()
            if cmd == "/quit" or cmd == "/exit":
                print("Goodbye!")
                break
            elif cmd == "/summary":
                print("\n" + assistant.summarize_session())
            elif cmd == "/info":
                info = assistant.get_session_info()
                print("\nSession Info:")
                for k, v in info.items():
                    print(f"  {k}: {v}")
            elif cmd == "/export":
                path = assistant.export_session()
                print(f"Exported to: {path}")
            elif cmd == "/clear":
                assistant.clear_history()
                print("History cleared")
            else:
                print(f"Unknown command: {query}")
            print()
            continue
        
        # Process research query
        print("\n" + "-" * 40)
        response = assistant.research(query)
        print(response)
        print("-" * 40 + "\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Research Assistant Agent')
    parser.add_argument('query', nargs='?', help='Research query')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--demo', '-d', action='store_true', help='Run demonstration')
    parser.add_argument('--output', '-o', help='Output file for results')
    parser.add_argument('--model', default='llama3.2:3b', help='Ollama model')
    parser.add_argument('--base-url', default='http://localhost:11434', help='Ollama URL')
    
    args = parser.parse_args()
    
    llm_config = {
        "provider": "ollama",
        "model": args.model,
        "base_url": args.base_url,
        "temperature": 0.5
    }
    
    assistant = ResearchAssistant(llm_config)
    
    if args.demo:
        run_demo(assistant)
    elif args.interactive:
        run_interactive(assistant)
    elif args.query:
        response = assistant.research(args.query)
        print("\n" + "=" * 60)
        print("RESEARCH RESULTS")
        print("=" * 60)
        print(response)
        
        if args.output:
            assistant.export_session(args.output)
    else:
        # Default to interactive mode
        run_interactive(assistant)


if __name__ == "__main__":
    main()
