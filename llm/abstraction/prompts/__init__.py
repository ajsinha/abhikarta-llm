"""
Prompt Templates and Management

System for managing, versioning, and reusing prompt templates.

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import re
import json


@dataclass
class PromptTemplate:
    """A reusable prompt template"""
    
    name: str
    template: str
    description: str = ""
    version: str = "1.0"
    variables: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Extract variables from template"""
        if not self.variables:
            self.variables = self._extract_variables()
    
    def _extract_variables(self) -> Set[str]:
        """Extract variable names from template using {variable} syntax"""
        pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}'
        matches = re.findall(pattern, self.template)
        return set(matches)
    
    def render(self, **kwargs) -> str:
        """
        Render template with provided variables.
        
        Args:
            **kwargs: Variable values
            
        Returns:
            Rendered prompt string
            
        Raises:
            ValueError: If required variables are missing
        """
        # Check for missing required variables
        missing = self.variables - set(kwargs.keys())
        if missing:
            raise ValueError(f"Missing required variables: {missing}")
        
        # Render template
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Template rendering failed: {e}")
    
    def validate(self, **kwargs) -> bool:
        """Validate that all required variables are provided"""
        return self.variables.issubset(set(kwargs.keys()))
    
    def get_example(self) -> str:
        """Get an example rendering with placeholder values"""
        example_values = {var: f"<{var}>" for var in self.variables}
        return self.render(**example_values)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'template': self.template,
            'description': self.description,
            'version': self.version,
            'variables': list(self.variables),
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """Create from dictionary"""
        return cls(
            name=data['name'],
            template=data['template'],
            description=data.get('description', ''),
            version=data.get('version', '1.0'),
            variables=set(data.get('variables', [])),
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now()
        )


class PromptRegistry:
    """Registry for managing prompt templates"""
    
    def __init__(self):
        self.templates: Dict[str, Dict[str, PromptTemplate]] = {}  # name -> {version -> template}
        self.usage_stats: Dict[str, int] = {}  # template name -> usage count
    
    def register(self, template: PromptTemplate) -> None:
        """
        Register a prompt template.
        
        Args:
            template: PromptTemplate to register
            
        Raises:
            ValueError: If template with same name and version exists
        """
        if template.name not in self.templates:
            self.templates[template.name] = {}
        
        if template.version in self.templates[template.name]:
            raise ValueError(
                f"Template '{template.name}' version '{template.version}' already exists"
            )
        
        self.templates[template.name][template.version] = template
        self.usage_stats[template.name] = 0
    
    def get(
        self,
        name: str,
        version: Optional[str] = None
    ) -> Optional[PromptTemplate]:
        """
        Get a prompt template.
        
        Args:
            name: Template name
            version: Specific version (uses latest if None)
            
        Returns:
            PromptTemplate or None if not found
        """
        if name not in self.templates:
            return None
        
        versions = self.templates[name]
        
        if version:
            return versions.get(version)
        
        # Get latest version
        latest_version = max(versions.keys())
        return versions[latest_version]
    
    def render(
        self,
        name: str,
        version: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Render a template by name.
        
        Args:
            name: Template name
            version: Specific version
            **kwargs: Variable values
            
        Returns:
            Rendered prompt
            
        Raises:
            ValueError: If template not found or rendering fails
        """
        template = self.get(name, version)
        if not template:
            raise ValueError(f"Template '{name}' not found")
        
        # Track usage
        self.usage_stats[name] += 1
        
        return template.render(**kwargs)
    
    def list_templates(self) -> List[str]:
        """List all registered template names"""
        return list(self.templates.keys())
    
    def list_versions(self, name: str) -> List[str]:
        """List all versions of a template"""
        if name not in self.templates:
            return []
        return list(self.templates[name].keys())
    
    def delete(self, name: str, version: Optional[str] = None) -> None:
        """
        Delete a template or specific version.
        
        Args:
            name: Template name
            version: Specific version (deletes all if None)
        """
        if name not in self.templates:
            return
        
        if version:
            if version in self.templates[name]:
                del self.templates[name][version]
            
            # Remove entry if no versions left
            if not self.templates[name]:
                del self.templates[name]
                del self.usage_stats[name]
        else:
            del self.templates[name]
            del self.usage_stats[name]
    
    def get_usage_stats(self) -> Dict[str, int]:
        """Get usage statistics for all templates"""
        return self.usage_stats.copy()
    
    def save(self, filepath: str) -> None:
        """Save registry to JSON file"""
        data = {
            'templates': {
                name: {
                    version: template.to_dict()
                    for version, template in versions.items()
                }
                for name, versions in self.templates.items()
            },
            'usage_stats': self.usage_stats
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath: str) -> None:
        """Load registry from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.templates.clear()
        self.usage_stats.clear()
        
        for name, versions in data.get('templates', {}).items():
            self.templates[name] = {}
            for version, template_data in versions.items():
                template = PromptTemplate.from_dict(template_data)
                self.templates[name][version] = template
        
        self.usage_stats = data.get('usage_stats', {})


class PromptChain:
    """Chain multiple prompts together"""
    
    def __init__(self, registry: PromptRegistry):
        self.registry = registry
        self.steps: List[Dict[str, Any]] = []
    
    def add_step(
        self,
        template_name: str,
        output_key: Optional[str] = None,
        **variables
    ) -> 'PromptChain':
        """
        Add a step to the chain.
        
        Args:
            template_name: Name of template to use
            output_key: Key to store output (uses template name if None)
            **variables: Variables for template
            
        Returns:
            Self for chaining
        """
        self.steps.append({
            'template': template_name,
            'output_key': output_key or template_name,
            'variables': variables
        })
        return self
    
    def execute(self, llm_client: Any, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the prompt chain.
        
        Args:
            llm_client: LLM client to use
            initial_context: Initial context variables
            
        Returns:
            Dictionary with all outputs
        """
        context = initial_context or {}
        outputs = {}
        
        for step in self.steps:
            # Merge context with step variables
            variables = {**context, **step['variables']}
            
            # Render prompt
            prompt = self.registry.render(step['template'], **variables)
            
            # Call LLM (simplified - actual implementation would use proper client)
            response = llm_client.complete(prompt)
            
            # Store output
            output_key = step['output_key']
            outputs[output_key] = response
            context[output_key] = response
        
        return outputs


# Built-in templates

def create_default_templates() -> PromptRegistry:
    """Create registry with common default templates"""
    registry = PromptRegistry()
    
    # Summarization
    registry.register(PromptTemplate(
        name="summarize",
        template="Summarize the following text in {num_sentences} sentences:\n\n{text}",
        description="Summarize text to specified number of sentences",
        version="1.0"
    ))
    
    # Translation
    registry.register(PromptTemplate(
        name="translate",
        template="Translate the following {source_lang} text to {target_lang}:\n\n{text}",
        description="Translate text between languages",
        version="1.0"
    ))
    
    # Question answering
    registry.register(PromptTemplate(
        name="qa",
        template="Answer the following question based on the context:\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:",
        description="Answer questions based on context",
        version="1.0"
    ))
    
    # Code generation
    registry.register(PromptTemplate(
        name="code_gen",
        template="Write {language} code to {task}. Include comments and handle errors.",
        description="Generate code for a specific task",
        version="1.0"
    ))
    
    # Code explanation
    registry.register(PromptTemplate(
        name="code_explain",
        template="Explain the following {language} code:\n\n```{language}\n{code}\n```\n\nProvide a clear explanation:",
        description="Explain code functionality",
        version="1.0"
    ))
    
    # Creative writing
    registry.register(PromptTemplate(
        name="story",
        template="Write a {length} story about {topic}. Style: {style}",
        description="Generate creative stories",
        version="1.0"
    ))
    
    # Email generation
    registry.register(PromptTemplate(
        name="email",
        template="Write a {tone} email to {recipient} about {subject}. Key points to include:\n{points}",
        description="Generate professional emails",
        version="1.0"
    ))
    
    # Analysis
    registry.register(PromptTemplate(
        name="analyze",
        template="Analyze the following {data_type} and provide insights:\n\n{data}\n\nFocus on: {focus_areas}",
        description="Analyze data and provide insights",
        version="1.0"
    ))
    
    return registry


# Prompt optimization utilities

def optimize_prompt_length(prompt: str, max_tokens: int = 4000) -> str:
    """Optimize prompt to fit within token limit"""
    # Simple approximation: 1 token ≈ 4 characters
    max_chars = max_tokens * 4
    
    if len(prompt) <= max_chars:
        return prompt
    
    # Truncate from middle, keep beginning and end
    keep_start = max_chars // 2
    keep_end = max_chars // 2
    
    return f"{prompt[:keep_start]}\n\n[... truncated ...]\n\n{prompt[-keep_end:]}"


def add_few_shot_examples(
    template: str,
    examples: List[Dict[str, str]],
    max_examples: int = 3
) -> str:
    """Add few-shot examples to a prompt template"""
    examples_text = "\n\n".join([
        f"Example {i+1}:\nInput: {ex['input']}\nOutput: {ex['output']}"
        for i, ex in enumerate(examples[:max_examples])
    ])
    
    return f"{examples_text}\n\n{template}"
