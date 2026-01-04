#!/usr/bin/env python3
"""
Interactive Tutor Agent Example

An intelligent tutoring agent that:
1. Assesses learner's current understanding
2. Uses Socratic method to guide discovery
3. Adapts to learning style and pace
4. Tracks progress across sessions
5. Provides personalized explanations

Usage:
    python interactive_tutor.py --topic "recursion"
    python interactive_tutor.py --interactive
    python interactive_tutor.py --assess "What do you know about machine learning?"

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
from enum import Enum

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LearnerLevel(Enum):
    """Learner proficiency levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class InteractionMode(Enum):
    """Tutor interaction modes."""
    ASSESSING = "assessing"
    EXPLAINING = "explaining"
    QUESTIONING = "questioning"
    CHALLENGING = "challenging"
    REVIEWING = "reviewing"


@dataclass
class LearnerProfile:
    """Tracks learner progress and preferences."""
    learner_id: str
    current_topic: str = ""
    level: LearnerLevel = LearnerLevel.BEGINNER
    concepts_understood: List[str] = field(default_factory=list)
    concepts_struggling: List[str] = field(default_factory=list)
    questions_asked: int = 0
    correct_responses: int = 0
    session_start: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    interaction_history: List[Dict] = field(default_factory=list)


@dataclass
class TutoringSession:
    """Represents a tutoring session."""
    session_id: str
    topic: str
    learner: LearnerProfile
    exchanges: List[Dict[str, str]] = field(default_factory=list)
    mode: InteractionMode = InteractionMode.ASSESSING
    insights: List[str] = field(default_factory=list)


class InteractiveTutor:
    """Interactive tutoring agent implementation."""
    
    SYSTEM_PROMPT = """You are an Intelligent Tutor specialized in personalized learning.

CORE TEACHING PRINCIPLES:

1. SOCRATIC METHOD
   - Guide through questions rather than direct answers
   - Let learners discover understanding themselves
   - Build on what they already know
   - Only provide direct explanation when truly stuck

2. ADAPTIVE TEACHING
   - Assess understanding before teaching
   - Adjust complexity to learner level
   - Use multiple explanations and analogies
   - Connect to real-world applications

3. SCAFFOLDING
   - Break complex topics into smaller parts
   - Provide support, then gradually remove it
   - Celebrate insights and progress
   - Address misconceptions gently

4. ENGAGEMENT
   - Be encouraging and patient
   - Make learning enjoyable
   - Use thought experiments
   - Ask follow-up questions

INTERACTION PATTERNS:

When ASSESSING:
- "Before we begin, what do you already know about [topic]?"
- "What specifically interests you about this?"
- "Have you encountered this concept before?"

When QUESTIONING (Socratic):
- "What do you think would happen if...?"
- "Why do you think that works that way?"
- "Can you think of an example?"
- "What's the relationship between X and Y?"

When GUIDING:
- "That's a good observation. Now consider..."
- "You're close. What if we also think about...?"
- "Let's break this down further..."

When ENCOURAGING:
- "Excellent insight!"
- "You've made a key connection there."
- "That's exactly the right question to ask."

When CHALLENGING:
- "But what about this scenario...?"
- "How would you explain this exception...?"
- "Someone might argue... How would you respond?"

IMPORTANT RULES:
1. Never simply give the answer unless absolutely necessary
2. Always follow up insights with deeper questions
3. Acknowledge effort even when wrong
4. Track what concepts are understood vs. struggling
5. Periodically summarize progress"""

    def __init__(self, llm_config: Dict[str, Any] = None):
        """Initialize the tutor."""
        self.llm_config = llm_config or {
            "provider": "ollama",
            "model": "llama3.2:3b",
            "base_url": os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
            "temperature": 0.7
        }
        self.llm = None
        self.session: Optional[TutoringSession] = None
        self.learner: Optional[LearnerProfile] = None
        
    def _create_llm(self):
        """Create LLM instance."""
        if self.llm is not None:
            return self.llm
        try:
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(
                model=self.llm_config.get("model", "llama3.2:3b"),
                base_url=self.llm_config.get("base_url", "http://localhost:11434"),
                temperature=self.llm_config.get("temperature", 0.7)
            )
            return self.llm
        except ImportError:
            raise ImportError("langchain-ollama required")
    
    def _invoke(self, prompt: str) -> str:
        """Invoke the LLM."""
        llm = self._create_llm()
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def _build_context(self) -> str:
        """Build context from session history."""
        if not self.session or not self.session.exchanges:
            return ""
        
        # Get recent exchanges
        recent = self.session.exchanges[-10:]
        
        context_parts = ["RECENT CONVERSATION:"]
        for exchange in recent:
            context_parts.append(f"Learner: {exchange.get('user', '')}")
            context_parts.append(f"Tutor: {exchange.get('tutor', '')}")
        
        # Add learner state
        if self.learner:
            context_parts.append(f"\nLEARNER PROFILE:")
            context_parts.append(f"- Level: {self.learner.level.value}")
            context_parts.append(f"- Concepts understood: {', '.join(self.learner.concepts_understood) or 'None yet'}")
            context_parts.append(f"- Struggling with: {', '.join(self.learner.concepts_struggling) or 'None identified'}")
        
        return "\n".join(context_parts)
    
    def start_session(self, topic: str, learner_id: str = None) -> str:
        """Start a new tutoring session."""
        learner_id = learner_id or f"learner_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.learner = LearnerProfile(
            learner_id=learner_id,
            current_topic=topic
        )
        
        self.session = TutoringSession(
            session_id=f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            topic=topic,
            learner=self.learner,
            mode=InteractionMode.ASSESSING
        )
        
        # Generate opening assessment question
        prompt = f"""{self.SYSTEM_PROMPT}

You are starting a tutoring session on: {topic}

Begin by assessing what the learner already knows. Ask 1-2 friendly questions to gauge their current understanding. Be warm and welcoming.

Provide your opening message:"""
        
        response = self._invoke(prompt)
        
        self.session.exchanges.append({
            "user": f"[Session start: {topic}]",
            "tutor": response
        })
        
        logger.info(f"Started tutoring session on: {topic}")
        return response
    
    def respond(self, learner_input: str) -> str:
        """Generate tutor response to learner input."""
        if not self.session:
            return self.start_session("general learning")
        
        context = self._build_context()
        
        # Update learner stats
        self.learner.questions_asked += 1
        
        prompt = f"""{self.SYSTEM_PROMPT}

TOPIC: {self.session.topic}
CURRENT MODE: {self.session.mode.value}

{context}

LEARNER'S MESSAGE:
{learner_input}

As a Socratic tutor:
1. Acknowledge their response
2. Assess their understanding from what they said
3. Guide them with a question OR provide a small hint if stuck
4. Keep the conversation moving toward deeper understanding

Remember:
- Don't just give answers
- Ask follow-up questions
- Be encouraging
- Note any concepts they seem to understand or struggle with

Your response:"""
        
        response = self._invoke(prompt)
        
        # Record exchange
        self.session.exchanges.append({
            "user": learner_input,
            "tutor": response
        })
        
        # Simple progress tracking (would be more sophisticated in production)
        if any(word in response.lower() for word in ['excellent', 'great insight', 'exactly right', 'you\'ve got it']):
            # Learner seems to understand something
            self.learner.correct_responses += 1
        
        return response
    
    def assess_level(self, learner_input: str) -> LearnerLevel:
        """Assess learner level from their responses."""
        prompt = f"""Based on this learner's responses about {self.session.topic}:

{learner_input}

Assess their level:
- BEGINNER: Little to no prior knowledge
- INTERMEDIATE: Some understanding, needs guidance
- ADVANCED: Good understanding, ready for complex topics
- EXPERT: Deep understanding, can discuss nuances

Respond with just the level: BEGINNER, INTERMEDIATE, ADVANCED, or EXPERT"""
        
        response = self._invoke(prompt)
        
        level_map = {
            'BEGINNER': LearnerLevel.BEGINNER,
            'INTERMEDIATE': LearnerLevel.INTERMEDIATE,
            'ADVANCED': LearnerLevel.ADVANCED,
            'EXPERT': LearnerLevel.EXPERT
        }
        
        for key, value in level_map.items():
            if key in response.upper():
                self.learner.level = value
                return value
        
        return self.learner.level
    
    def summarize_progress(self) -> str:
        """Summarize learning progress."""
        if not self.session:
            return "No active session."
        
        context = self._build_context()
        
        prompt = f"""{self.SYSTEM_PROMPT}

TOPIC: {self.session.topic}
SESSION EXCHANGES: {len(self.session.exchanges)}

{context}

Provide a warm, encouraging summary of the learner's progress:
1. What concepts they seem to understand now
2. What they're still working on
3. Key insights they've had
4. Suggested next steps for continued learning

Keep it positive and constructive:"""
        
        return self._invoke(prompt)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        if not self.session:
            return {"status": "no active session"}
        
        return {
            "session_id": self.session.session_id,
            "topic": self.session.topic,
            "learner_level": self.learner.level.value,
            "total_exchanges": len(self.session.exchanges),
            "questions_asked": self.learner.questions_asked,
            "concepts_understood": self.learner.concepts_understood,
            "concepts_struggling": self.learner.concepts_struggling,
            "session_duration": self.learner.session_start
        }
    
    def end_session(self) -> str:
        """End the session with a summary."""
        summary = self.summarize_progress()
        
        closing = f"""

📚 SESSION COMPLETE

{summary}

Thank you for learning with me today! Keep exploring and asking questions. 🌟
"""
        self.session = None
        self.learner = None
        
        return closing


def run_interactive(tutor: InteractiveTutor):
    """Run interactive tutoring session."""
    print("\n" + "=" * 60)
    print("🎓 INTERACTIVE TUTOR")
    print("=" * 60)
    print("\nCommands:")
    print("  /topic <topic>  - Start new topic")
    print("  /summary        - Get progress summary")
    print("  /stats          - Show session stats")
    print("  /end            - End session")
    print("  /quit           - Exit")
    print("\nWhat would you like to learn about?")
    
    topic = input("\n📖 Topic: ").strip()
    if topic.lower() in ['quit', 'exit']:
        return
    
    opening = tutor.start_session(topic)
    print(f"\n🎓 Tutor: {opening}\n")
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n" + tutor.end_session())
            break
        
        if not user_input:
            continue
        
        # Handle commands
        if user_input.startswith('/'):
            cmd = user_input.lower().split()[0]
            
            if cmd == '/quit' or cmd == '/exit':
                print(tutor.end_session())
                break
            elif cmd == '/topic':
                new_topic = user_input[6:].strip()
                if new_topic:
                    opening = tutor.start_session(new_topic)
                    print(f"\n🎓 Tutor: {opening}\n")
                else:
                    print("Please specify a topic: /topic <topic>")
            elif cmd == '/summary':
                print(f"\n📊 {tutor.summarize_progress()}\n")
            elif cmd == '/stats':
                stats = tutor.get_session_stats()
                print("\n📈 Session Stats:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                print()
            elif cmd == '/end':
                print(tutor.end_session())
                topic = input("\n📖 New topic (or 'quit'): ").strip()
                if topic.lower() in ['quit', 'exit']:
                    break
                opening = tutor.start_session(topic)
                print(f"\n🎓 Tutor: {opening}\n")
            else:
                print(f"Unknown command: {cmd}")
            continue
        
        # Normal conversation
        response = tutor.respond(user_input)
        print(f"\n🎓 Tutor: {response}\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Interactive Tutor Agent')
    parser.add_argument('--topic', '-t', help='Start with specific topic')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--assess', '-a', help='Assess a statement')
    parser.add_argument('--model', default='llama3.2:3b', help='Ollama model')
    parser.add_argument('--base-url', default='http://localhost:11434', help='Ollama URL')
    
    args = parser.parse_args()
    
    llm_config = {
        "provider": "ollama",
        "model": args.model,
        "base_url": args.base_url,
        "temperature": 0.7
    }
    
    tutor = InteractiveTutor(llm_config)
    
    if args.assess:
        tutor.start_session("assessment")
        level = tutor.assess_level(args.assess)
        print(f"Assessed level: {level.value}")
    elif args.topic:
        opening = tutor.start_session(args.topic)
        print(f"\n🎓 Tutor: {opening}")
        run_interactive(tutor)
    else:
        run_interactive(tutor)


if __name__ == "__main__":
    main()
