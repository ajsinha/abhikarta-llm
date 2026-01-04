#!/usr/bin/env python3
"""
ReAct Agent Example
===================

This example demonstrates a ReAct (Reasoning + Acting) pattern agent
that uses tools to accomplish tasks.

Requirements:
    - Ollama running with llama3.2:3b model
    - pip install langchain-ollama langgraph

Usage:
    python -m abhikarta.examples.agent.react_agent
"""

import os
import json
import logging
from typing import Dict, Any, List, TypedDict, Annotated
from operator import add
import math
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://192.168.2.36:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")


# Agent Definition JSON
AGENT_DEFINITION = {
    "agent_id": "react_agent_example",
    "name": "ReAct Calculator Agent",
    "description": "An agent that uses ReAct pattern with calculator and datetime tools",
    "agent_type": "react",
    "llm_config": {
        "provider": "ollama",
        "model": "llama3.2:3b",
        "temperature": 0.1,
        "max_tokens": 1024
    },
    "tools": [
        {
            "name": "calculator",
            "description": "Perform mathematical calculations. Input should be a mathematical expression.",
            "parameters": {
                "expression": {"type": "string", "description": "Math expression to evaluate"}
            }
        },
        {
            "name": "get_current_time",
            "description": "Get the current date and time",
            "parameters": {}
        },
        {
            "name": "convert_units",
            "description": "Convert between units (e.g., miles to km, fahrenheit to celsius)",
            "parameters": {
                "value": {"type": "number", "description": "Value to convert"},
                "from_unit": {"type": "string", "description": "Source unit"},
                "to_unit": {"type": "string", "description": "Target unit"}
            }
        }
    ],
    "system_prompt": """You are a helpful assistant that uses the ReAct pattern.
For each step:
1. Thought: Think about what you need to do
2. Action: Choose a tool to use
3. Observation: See the result
4. Repeat until you have the answer
5. Final Answer: Provide the complete answer

Available tools: calculator, get_current_time, convert_units"""
}


# Tool implementations
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        # Safe eval with math functions
        allowed_names = {
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "pow": pow, "sqrt": math.sqrt,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "log": math.log, "log10": math.log10, "exp": math.exp,
            "pi": math.pi, "e": math.e
        }
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"


def get_current_time() -> str:
    """Get current date and time."""
    now = datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"


def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between units."""
    conversions = {
        ("miles", "km"): lambda x: x * 1.60934,
        ("km", "miles"): lambda x: x / 1.60934,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
        ("celsius", "fahrenheit"): lambda x: x * 9/5 + 32,
        ("pounds", "kg"): lambda x: x * 0.453592,
        ("kg", "pounds"): lambda x: x / 0.453592,
        ("inches", "cm"): lambda x: x * 2.54,
        ("cm", "inches"): lambda x: x / 2.54,
    }
    
    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        result = conversions[key](value)
        return f"{value} {from_unit} = {result:.4f} {to_unit}"
    else:
        return f"Unknown conversion: {from_unit} to {to_unit}"


TOOLS = {
    "calculator": calculator,
    "get_current_time": get_current_time,
    "convert_units": convert_units
}


class AgentState(TypedDict):
    """Agent state."""
    input: str
    chat_history: List[Dict[str, str]]
    intermediate_steps: List[Dict[str, Any]]
    output: str


def run_react_agent():
    """Run the ReAct agent."""
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
        temperature=0.1
    )
    
    # ReAct prompt template
    react_prompt = """You are a helpful assistant using the ReAct pattern.

Available Tools:
- calculator: Evaluate math expressions (e.g., "2 + 2 * 3")
- get_current_time: Get current date and time
- convert_units: Convert units (value, from_unit, to_unit)

Format your response as:
Thought: [your reasoning]
Action: [tool_name]
Action Input: [input for the tool]

After receiving an observation, continue with another Thought/Action or provide:
Final Answer: [your complete answer]

Question: {question}

{scratchpad}"""

    def parse_action(text: str) -> tuple:
        """Parse action from LLM response."""
        action = None
        action_input = None
        
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('Action:'):
                action = line.replace('Action:', '').strip()
            elif line.startswith('Action Input:'):
                action_input = line.replace('Action Input:', '').strip()
        
        return action, action_input
    
    def run_agent(question: str, max_iterations: int = 5) -> str:
        """Run the agent loop."""
        scratchpad = ""
        
        for i in range(max_iterations):
            # Get LLM response
            prompt = react_prompt.format(question=question, scratchpad=scratchpad)
            response = llm.invoke(prompt)
            response_text = response.content
            
            print(f"\n--- Iteration {i+1} ---")
            print(response_text)
            
            # Check for final answer
            if "Final Answer:" in response_text:
                final = response_text.split("Final Answer:")[-1].strip()
                return final
            
            # Parse and execute action
            action, action_input = parse_action(response_text)
            
            if action and action in TOOLS:
                # Execute tool
                tool_fn = TOOLS[action]
                
                if action == "calculator":
                    observation = tool_fn(action_input)
                elif action == "get_current_time":
                    observation = tool_fn()
                elif action == "convert_units":
                    # Parse action input for convert_units
                    try:
                        parts = action_input.split(',')
                        value = float(parts[0].strip())
                        from_unit = parts[1].strip()
                        to_unit = parts[2].strip()
                        observation = tool_fn(value, from_unit, to_unit)
                    except:
                        observation = f"Error parsing input: {action_input}"
                else:
                    observation = f"Unknown action: {action}"
                
                scratchpad += f"\n{response_text}\nObservation: {observation}\n"
                print(f"Observation: {observation}")
            else:
                scratchpad += f"\n{response_text}\nObservation: Could not parse action or unknown tool.\n"
        
        return "Max iterations reached without final answer."
    
    # Test questions
    test_questions = [
        "What is 15% of 250?",
        "What time is it right now?",
        "Convert 100 miles to kilometers",
        "Calculate the square root of 144 plus 5 squared"
    ]
    
    print("="*60)
    print("REACT AGENT EXAMPLE")
    print("="*60)
    
    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print("="*60)
        
        answer = run_agent(question)
        
        print(f"\n{'='*60}")
        print(f"Final Answer: {answer}")
        print("="*60)
        
        # Add delay between questions
        import time
        time.sleep(1)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ReAct Agent Example")
    parser.add_argument("--json", action="store_true", help="Print agent JSON definition")
    parser.add_argument("--host", default=OLLAMA_HOST, help="Ollama host URL")
    parser.add_argument("--model", default=OLLAMA_MODEL, help="Ollama model name")
    parser.add_argument("--question", "-q", type=str, help="Ask a specific question")
    
    args = parser.parse_args()
    
    if args.json:
        print(json.dumps(AGENT_DEFINITION, indent=2))
        return
    
    os.environ["OLLAMA_HOST"] = args.host
    os.environ["OLLAMA_MODEL"] = args.model
    
    run_react_agent()


if __name__ == "__main__":
    main()
