"""
AI Org Prompts - LLM prompts for task analysis, delegation, and aggregation.

Version: 1.4.6
Copyright © 2025-2030, All Rights Reserved
"""

from typing import Dict, Any, List
from .models import AINode, AITask, NodeType


class AIORGPrompts:
    """Prompt templates for AI Org operations."""
    
    SYSTEM_PROMPT = """You are an AI assistant operating as part of an AI-powered organizational structure.
You represent a specific role in the organization and must act professionally and effectively.
Your responses should be structured, actionable, and appropriate for your role level.
Always respond in valid JSON format when requested."""
    
    def get_role_system_prompt(self, node: AINode) -> str:
        """Get role-specific system prompt."""
        role_descriptions = {
            NodeType.EXECUTIVE: "a senior executive responsible for strategic decisions and overall coordination",
            NodeType.MANAGER: "a middle manager responsible for coordinating teams and synthesizing work",
            NodeType.ANALYST: "an analyst responsible for detailed research, analysis, and producing findings",
            NodeType.COORDINATOR: "a coordinator responsible for cross-functional collaboration"
        }
        
        role_desc = role_descriptions.get(node.role_type, "a professional team member")
        
        return f"""You are {node.role_name}, {role_desc} in an AI-powered organization.
{node.description if node.description else ''}

Your responsibilities include:
- Analyzing tasks assigned to you
- Producing high-quality, actionable outputs
- Communicating clearly and professionally
- Following organizational protocols

Always structure your responses as JSON when requested."""
    
    def get_analysis_prompt(
        self,
        task: AITask,
        node: AINode,
        subordinates: List[AINode]
    ) -> str:
        """Get prompt for task analysis and delegation decision."""
        
        subordinate_info = ""
        if subordinates:
            sub_list = []
            for sub in subordinates:
                sub_list.append(f"  - {sub.role_name} ({sub.role_type.value}): {sub.description or 'Available for tasks'}")
            subordinate_info = f"""
Your direct reports:
{chr(10).join(sub_list)}
"""
        else:
            subordinate_info = "You have no direct reports - you must complete tasks yourself."
        
        return f"""Analyze the following task and determine how to proceed.

**Task Information:**
Title: {task.title}
Description: {task.description}
Priority: {task.priority.value}
Context: {task.context}

**Input Data:**
{task.input_data}

{subordinate_info}

**Your Decision:**
Analyze this task and decide:
1. Can you complete this task yourself, or should you delegate to your direct reports?
2. If delegating, how should the work be divided?

Respond in JSON format:
```json
{{
    "needs_delegation": true/false,
    "reasoning": "Your analysis of why delegation is or isn't needed",
    "delegation_plan": {{
        "strategy": "parallel" or "sequential",
        "subtasks": [
            {{
                "title": "Subtask title",
                "description": "What this subordinate should do",
                "assigned_to": "node_id of subordinate",
                "priority": "high/medium/low",
                "instructions": "Specific instructions"
            }}
        ],
        "summary_instructions": "How to synthesize the results"
    }},
    "direct_response": {{
        // Only if needs_delegation is false
        "findings": "Your analysis",
        "recommendations": ["List of recommendations"],
        "summary": "Executive summary"
    }}
}}
```
"""
    
    def get_execution_prompt(self, task: AITask, node: AINode) -> str:
        """Get prompt for direct task execution."""
        return f"""Execute the following task and provide your analysis.

**Your Role:** {node.role_name}
**Role Description:** {node.description or 'Team member'}

**Task:**
Title: {task.title}
Description: {task.description}
Priority: {task.priority.value}

**Context from Manager:**
{task.context}

**Input Data:**
{task.input_data}

**Instructions:**
Analyze this task thoroughly and provide your professional findings.
Be comprehensive, accurate, and actionable.

Respond in JSON format:
```json
{{
    "findings": {{
        "summary": "Brief summary of your findings",
        "details": ["Detailed finding 1", "Detailed finding 2"],
        "data_points": ["Relevant data or facts discovered"],
        "issues_identified": ["Any problems or concerns found"]
    }},
    "analysis": {{
        "methodology": "How you approached this task",
        "assumptions": ["Any assumptions made"],
        "limitations": ["Limitations of your analysis"]
    }},
    "recommendations": [
        {{
            "recommendation": "What you recommend",
            "rationale": "Why this is recommended",
            "priority": "high/medium/low"
        }}
    ],
    "summary": "Executive summary for your manager",
    "confidence_level": "high/medium/low",
    "additional_notes": "Any other relevant information"
}}
```
"""
    
    def get_aggregation_prompt(
        self,
        task: AITask,
        node: AINode,
        subordinate_responses: List[Dict[str, Any]]
    ) -> str:
        """Get prompt for aggregating subordinate responses."""
        
        responses_text = ""
        for i, resp in enumerate(subordinate_responses, 1):
            responses_text += f"""
**Response {i} - {resp.get('subtask_title', 'Subtask')}:**
Summary: {resp.get('summary', 'No summary')}
Content: {resp.get('response', {})}
---
"""
        
        return f"""Synthesize the following responses from your team into a comprehensive report.

**Original Task:**
Title: {task.title}
Description: {task.description}

**Your Role:** {node.role_name}

**Team Responses:**
{responses_text}

**Instructions:**
1. Review all subordinate responses
2. Identify key findings and themes
3. Note any conflicts or gaps
4. Synthesize into a coherent summary
5. Provide actionable conclusions

Respond in JSON format:
```json
{{
    "executive_summary": "High-level summary for leadership",
    "key_findings": [
        {{
            "finding": "Key finding",
            "source": "Which subordinate(s) contributed",
            "importance": "high/medium/low"
        }}
    ],
    "synthesis": {{
        "themes": ["Common themes identified"],
        "agreements": ["Points where subordinates agreed"],
        "conflicts": ["Any conflicting information"],
        "gaps": ["Information gaps or areas needing more research"]
    }},
    "consolidated_recommendations": [
        {{
            "recommendation": "Action item",
            "rationale": "Why this is recommended",
            "priority": "high/medium/low",
            "supporting_inputs": ["Which subordinate responses support this"]
        }}
    ],
    "risk_assessment": {{
        "identified_risks": ["Risk 1", "Risk 2"],
        "mitigation_suggestions": ["How to address risks"]
    }},
    "next_steps": ["Recommended next steps"],
    "confidence_level": "high/medium/low",
    "summary": "Final summary paragraph for the report"
}}
```
"""
    
    def get_hitl_review_prompt(
        self,
        task: AITask,
        node: AINode,
        ai_response: Dict[str, Any],
        review_type: str
    ) -> str:
        """Get prompt explaining what's being reviewed for HITL."""
        return f"""**HITL Review Required**

**Review Type:** {review_type}
**Role:** {node.role_name}
**Task:** {task.title}

**AI-Generated Content:**
{ai_response}

**What needs review:**
{'- Review the delegation plan before tasks are assigned to subordinates' if review_type == 'delegation_review' else ''}
{'- Review the response before it is sent to your manager' if review_type == 'response_approval' else ''}
{'- Review the incoming task before processing begins' if review_type == 'task_received' else ''}

**Actions available:**
- Approve: Accept the AI content as-is
- Override: Replace with your own content
- Reject: Cancel this action
- Message: Add a note without changing the flow
"""
