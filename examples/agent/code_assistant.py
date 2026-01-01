#!/usr/bin/env python3
"""
Code Assistant Agent Example

A sophisticated coding assistant agent that can:
1. Generate code in multiple languages
2. Review and improve existing code
3. Debug issues and explain errors
4. Explain complex code and algorithms

Usage:
    python code_assistant.py "Write a function to..."
    python code_assistant.py --interactive
    python code_assistant.py --review path/to/code.py

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


class TaskType(Enum):
    """Types of coding tasks."""
    GENERATE = "generate"
    REVIEW = "review"
    DEBUG = "debug"
    EXPLAIN = "explain"
    OPTIMIZE = "optimize"
    TEST = "test"


@dataclass
class CodeContext:
    """Context for code-related conversations."""
    language: str = ""
    code_snippets: List[Dict[str, str]] = field(default_factory=list)
    current_task: Optional[TaskType] = None
    conversation_history: List[Dict[str, str]] = field(default_factory=list)


class CodeAssistant:
    """Code Assistant Agent implementation."""
    
    SYSTEM_PROMPT = """You are an expert Code Assistant with mastery across programming languages and paradigms.

CORE CAPABILITIES:

1. CODE GENERATION
   - Write clean, efficient, production-ready code
   - Follow language-specific best practices (PEP 8, ESLint, etc.)
   - Include comprehensive error handling
   - Add clear comments and documentation
   - Consider edge cases and input validation

2. CODE REVIEW
   - Identify bugs, issues, and vulnerabilities
   - Suggest improvements and optimizations
   - Check for code smells and anti-patterns
   - Evaluate maintainability and readability
   - Provide actionable feedback

3. DEBUGGING
   - Analyze error messages and stack traces
   - Identify root causes systematically
   - Provide clear fixes with explanations
   - Suggest preventive measures
   - Help reproduce and isolate issues

4. CODE EXPLANATION
   - Break down complex code step-by-step
   - Explain algorithms and data structures
   - Clarify language-specific features
   - Use analogies and examples
   - Provide complexity analysis

SUPPORTED LANGUAGES:
- Python, JavaScript/TypeScript, Java, C/C++, Go, Rust
- SQL, GraphQL, HTML/CSS, Shell (Bash/PowerShell)
- Configuration: YAML, JSON, TOML, Dockerfile

CODE OUTPUT FORMAT:
```language
# Brief description
# Usage: example of how to use

[well-structured, commented code]
```

ALWAYS PROVIDE:
1. Complete, runnable code (not just snippets)
2. Proper error handling
3. Type hints/annotations where applicable
4. Usage examples
5. Time/space complexity when relevant
6. Potential improvements or alternatives"""

    TASK_PROMPTS = {
        TaskType.GENERATE: "Generate code for the following requirement:",
        TaskType.REVIEW: "Review the following code and provide detailed feedback:",
        TaskType.DEBUG: "Debug the following code and error:",
        TaskType.EXPLAIN: "Explain the following code in detail:",
        TaskType.OPTIMIZE: "Optimize the following code for better performance:",
        TaskType.TEST: "Write comprehensive tests for the following code:"
    }

    def __init__(self, llm_config: Dict[str, Any] = None):
        """Initialize the code assistant."""
        self.llm_config = llm_config or {
            "provider": "ollama",
            "model": "llama3.2:3b",
            "base_url": os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
            "temperature": 0.3  # Lower temperature for code
        }
        self.llm = None
        self.context = CodeContext()
    
    def _create_llm(self):
        """Create LLM instance."""
        if self.llm is not None:
            return self.llm
        
        try:
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(
                model=self.llm_config.get("model", "llama3.2:3b"),
                base_url=self.llm_config.get("base_url", "http://localhost:11434"),
                temperature=self.llm_config.get("temperature", 0.3)
            )
            logger.info(f"LLM initialized: {self.llm_config['model']}")
            return self.llm
        except ImportError:
            raise ImportError("langchain-ollama required")
    
    def _invoke_llm(self, prompt: str) -> str:
        """Invoke the LLM."""
        llm = self._create_llm()
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def _detect_task_type(self, query: str) -> TaskType:
        """Detect the type of coding task from the query."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['write', 'create', 'implement', 'generate', 'make', 'build']):
            return TaskType.GENERATE
        elif any(word in query_lower for word in ['review', 'check', 'analyze', 'audit', 'evaluate']):
            return TaskType.REVIEW
        elif any(word in query_lower for word in ['debug', 'fix', 'error', 'bug', 'issue', 'problem']):
            return TaskType.DEBUG
        elif any(word in query_lower for word in ['explain', 'what does', 'how does', 'understand', 'clarify']):
            return TaskType.EXPLAIN
        elif any(word in query_lower for word in ['optimize', 'improve', 'faster', 'efficient', 'performance']):
            return TaskType.OPTIMIZE
        elif any(word in query_lower for word in ['test', 'unit test', 'pytest', 'testing']):
            return TaskType.TEST
        
        return TaskType.GENERATE  # Default
    
    def _detect_language(self, code_or_query: str) -> str:
        """Detect programming language from code or query."""
        indicators = {
            'python': ['def ', 'import ', 'from ', 'print(', 'elif', '__init__', '.py'],
            'javascript': ['const ', 'let ', 'function ', 'console.log', '=>', '.js', 'async ', 'await '],
            'typescript': [': string', ': number', 'interface ', ': boolean', '.ts'],
            'java': ['public class', 'public static', 'System.out', '.java', 'void '],
            'cpp': ['#include', 'std::', 'cout', 'int main', '.cpp', '.hpp'],
            'go': ['func ', 'package ', 'fmt.', '.go', 'import ('],
            'rust': ['fn ', 'let mut', 'impl ', '.rs', 'println!'],
            'sql': ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE TABLE', 'FROM ']
        }
        
        text = code_or_query.lower()
        for lang, patterns in indicators.items():
            if any(p.lower() in text for p in patterns):
                return lang
        
        return 'python'  # Default
    
    def _build_context_history(self) -> str:
        """Build context from conversation history."""
        if not self.context.conversation_history:
            return ""
        
        recent = self.context.conversation_history[-6:]  # Last 3 exchanges
        parts = ["PREVIOUS CONVERSATION:"]
        for entry in recent:
            role = "User" if entry['role'] == 'user' else "Assistant"
            content = entry['content'][:500] + "..." if len(entry['content']) > 500 else entry['content']
            parts.append(f"{role}: {content}")
        
        return "\n".join(parts)
    
    def generate_code(self, requirement: str, language: str = None) -> str:
        """Generate code based on requirements.
        
        Args:
            requirement: Description of what the code should do
            language: Target programming language (auto-detected if not specified)
        """
        lang = language or self._detect_language(requirement)
        self.context.language = lang
        self.context.current_task = TaskType.GENERATE
        
        context_history = self._build_context_history()
        
        prompt = f"""{self.SYSTEM_PROMPT}

{context_history}

TASK: Generate {lang.upper()} code

REQUIREMENT:
{requirement}

Provide complete, production-ready code with:
1. Proper error handling
2. Type hints (if applicable)
3. Clear comments
4. Usage example
5. Any necessary imports"""
        
        logger.info(f"Generating {lang} code...")
        response = self._invoke_llm(prompt)
        
        # Update context
        self.context.conversation_history.append({"role": "user", "content": requirement})
        self.context.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def review_code(self, code: str, focus_areas: List[str] = None) -> str:
        """Review code and provide feedback.
        
        Args:
            code: Code to review
            focus_areas: Specific areas to focus on (optional)
        """
        lang = self._detect_language(code)
        self.context.language = lang
        self.context.current_task = TaskType.REVIEW
        
        focus = ""
        if focus_areas:
            focus = f"\n\nFOCUS AREAS: {', '.join(focus_areas)}"
        
        prompt = f"""{self.SYSTEM_PROMPT}

TASK: Code Review ({lang.upper()})

CODE TO REVIEW:
```{lang}
{code}
```
{focus}

Provide a comprehensive code review including:
1. 🐛 BUGS/ISSUES: Potential bugs or errors
2. 🔒 SECURITY: Security vulnerabilities
3. ⚡ PERFORMANCE: Performance concerns
4. 📖 READABILITY: Code clarity and maintainability
5. 🎯 BEST PRACTICES: Adherence to conventions
6. 💡 SUGGESTIONS: Specific improvements

End with an overall assessment and improved code if needed."""
        
        logger.info(f"Reviewing {lang} code...")
        response = self._invoke_llm(prompt)
        
        self.context.conversation_history.append({"role": "user", "content": f"Review:\n{code}"})
        self.context.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def debug_code(self, code: str, error_message: str = None) -> str:
        """Debug code and fix issues.
        
        Args:
            code: Code with issues
            error_message: Error message or description of the problem
        """
        lang = self._detect_language(code)
        self.context.language = lang
        self.context.current_task = TaskType.DEBUG
        
        error_section = ""
        if error_message:
            error_section = f"\n\nERROR MESSAGE:\n{error_message}"
        
        prompt = f"""{self.SYSTEM_PROMPT}

TASK: Debug Code ({lang.upper()})

PROBLEMATIC CODE:
```{lang}
{code}
```
{error_section}

Debug this code by:
1. 🔍 ANALYSIS: Identify the root cause
2. 📝 EXPLANATION: Explain why the error occurs
3. ✅ FIX: Provide the corrected code
4. 🛡️ PREVENTION: Suggest how to prevent similar issues
5. 🧪 TESTING: Provide test cases to verify the fix"""
        
        logger.info(f"Debugging {lang} code...")
        response = self._invoke_llm(prompt)
        
        self.context.conversation_history.append({"role": "user", "content": f"Debug:\n{code}\nError: {error_message}"})
        self.context.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def explain_code(self, code: str, detail_level: str = "medium") -> str:
        """Explain code in detail.
        
        Args:
            code: Code to explain
            detail_level: 'brief', 'medium', or 'detailed'
        """
        lang = self._detect_language(code)
        self.context.language = lang
        self.context.current_task = TaskType.EXPLAIN
        
        detail_instruction = {
            'brief': "Provide a concise summary of what the code does.",
            'medium': "Explain the code with moderate detail, covering key concepts.",
            'detailed': "Provide an in-depth explanation, line by line if needed."
        }.get(detail_level, "Explain the code with moderate detail.")
        
        prompt = f"""{self.SYSTEM_PROMPT}

TASK: Explain Code ({lang.upper()})

CODE:
```{lang}
{code}
```

{detail_instruction}

Include:
1. 📋 OVERVIEW: What the code accomplishes
2. 🔄 FLOW: Step-by-step execution flow
3. 📚 CONCEPTS: Key concepts and patterns used
4. ⏱️ COMPLEXITY: Time and space complexity
5. 🎓 LEARNING: Related topics to explore"""
        
        logger.info(f"Explaining {lang} code...")
        response = self._invoke_llm(prompt)
        
        self.context.conversation_history.append({"role": "user", "content": f"Explain:\n{code}"})
        self.context.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def chat(self, message: str) -> str:
        """General chat interface that auto-detects task type."""
        task_type = self._detect_task_type(message)
        
        # Check if message contains code
        has_code = '```' in message or 'def ' in message or 'function ' in message
        
        if has_code:
            # Extract code from message
            if '```' in message:
                parts = message.split('```')
                if len(parts) >= 3:
                    code = parts[1].strip()
                    if code.startswith(('python', 'javascript', 'java', 'cpp', 'go')):
                        code = '\n'.join(code.split('\n')[1:])
                else:
                    code = parts[1] if len(parts) > 1 else message
            else:
                code = message
            
            if task_type == TaskType.REVIEW:
                return self.review_code(code)
            elif task_type == TaskType.DEBUG:
                return self.debug_code(code)
            elif task_type == TaskType.EXPLAIN:
                return self.explain_code(code)
            elif task_type == TaskType.TEST:
                return self.generate_code(f"Write tests for:\n{code}")
        
        # Default to generate
        return self.generate_code(message)
    
    def clear_context(self):
        """Clear conversation context."""
        self.context = CodeContext()
        logger.info("Context cleared")


def run_interactive(assistant: CodeAssistant):
    """Run interactive coding session."""
    print("\n" + "=" * 60)
    print("💻 CODE ASSISTANT - Interactive Mode")
    print("=" * 60)
    print("\nCommands:")
    print("  /generate [lang] <desc> - Generate code")
    print("  /review                 - Review code (paste after)")
    print("  /debug                  - Debug code (paste after)")
    print("  /explain                - Explain code (paste after)")
    print("  /clear                  - Clear context")
    print("  /quit                   - Exit")
    print("\nOr just describe what you need!\n")
    
    while True:
        try:
            user_input = input("💻 > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in ['/quit', '/exit', '/q']:
            print("Goodbye!")
            break
        elif user_input.lower() == '/clear':
            assistant.clear_context()
            print("Context cleared")
            continue
        elif user_input.lower().startswith('/review'):
            print("Paste code to review (end with empty line):")
            code_lines = []
            while True:
                line = input()
                if not line:
                    break
                code_lines.append(line)
            code = '\n'.join(code_lines)
            response = assistant.review_code(code)
        elif user_input.lower().startswith('/debug'):
            print("Paste code to debug (end with empty line):")
            code_lines = []
            while True:
                line = input()
                if not line:
                    break
                code_lines.append(line)
            code = '\n'.join(code_lines)
            error = input("Error message (optional): ").strip()
            response = assistant.debug_code(code, error if error else None)
        elif user_input.lower().startswith('/explain'):
            print("Paste code to explain (end with empty line):")
            code_lines = []
            while True:
                line = input()
                if not line:
                    break
                code_lines.append(line)
            code = '\n'.join(code_lines)
            response = assistant.explain_code(code)
        else:
            response = assistant.chat(user_input)
        
        print("\n" + "-" * 40)
        print(response)
        print("-" * 40 + "\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Code Assistant Agent')
    parser.add_argument('query', nargs='?', help='Coding request')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--review', '-r', help='Review code file')
    parser.add_argument('--debug', '-d', help='Debug code file')
    parser.add_argument('--explain', '-e', help='Explain code file')
    parser.add_argument('--model', default='llama3.2:3b', help='Ollama model')
    parser.add_argument('--base-url', default='http://localhost:11434', help='Ollama URL')
    
    args = parser.parse_args()
    
    llm_config = {
        "provider": "ollama",
        "model": args.model,
        "base_url": args.base_url,
        "temperature": 0.3
    }
    
    assistant = CodeAssistant(llm_config)
    
    if args.interactive:
        run_interactive(assistant)
    elif args.review:
        with open(args.review, 'r') as f:
            code = f.read()
        print(assistant.review_code(code))
    elif args.debug:
        with open(args.debug, 'r') as f:
            code = f.read()
        print(assistant.debug_code(code))
    elif args.explain:
        with open(args.explain, 'r') as f:
            code = f.read()
        print(assistant.explain_code(code))
    elif args.query:
        print(assistant.chat(args.query))
    else:
        run_interactive(assistant)


if __name__ == "__main__":
    main()
