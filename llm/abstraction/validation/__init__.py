"""
Response Validation & Schema Enforcement

Ensure LLM responses match expected format/schema with automatic retry.

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from typing import Type, TypeVar, Optional, Callable, Any, Dict, List
from pydantic import BaseModel, ValidationError as PydanticValidationError
from dataclasses import dataclass
import json
import re


T = TypeVar('T', bound=BaseModel)


class ValidationError(Exception):
    """Custom validation error"""
    pass


@dataclass
class ValidationResult:
    """Result of validation"""
    valid: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    attempt: int = 1


class ResponseValidator:
    """Validate and parse LLM responses"""
    
    def __init__(self, max_retries: int = 3):
        """
        Initialize validator.
        
        Args:
            max_retries: Maximum number of retry attempts
        """
        self.max_retries = max_retries
        self.validation_history: List[ValidationResult] = []
    
    def validate(
        self,
        response: str,
        schema: Type[T],
        extract_json: bool = True
    ) -> T:
        """
        Validate response against schema.
        
        Args:
            response: LLM response text
            schema: Pydantic model schema
            extract_json: Try to extract JSON from response
            
        Returns:
            Parsed and validated data
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Extract JSON if needed
            if extract_json:
                json_str = self._extract_json(response)
            else:
                json_str = response
            
            # Parse JSON
            data = json.loads(json_str)
            
            # Validate against schema
            validated = schema(**data)
            
            self.validation_history.append(ValidationResult(
                valid=True,
                data=validated
            ))
            
            return validated
            
        except (json.JSONDecodeError, PydanticValidationError) as e:
            error_msg = f"Validation failed: {str(e)}"
            
            self.validation_history.append(ValidationResult(
                valid=False,
                error=error_msg
            ))
            
            raise ValidationError(error_msg)
    
    def validate_with_retry(
        self,
        llm_client: Any,
        prompt: str,
        schema: Type[T],
        extract_json: bool = True,
        **llm_kwargs
    ) -> T:
        """
        Call LLM with validation and retry on failure.
        
        Args:
            llm_client: LLM client
            prompt: Initial prompt
            schema: Pydantic model schema
            extract_json: Try to extract JSON
            **llm_kwargs: Additional LLM arguments
            
        Returns:
            Validated response
            
        Raises:
            ValidationError: If all retries fail
        """
        current_prompt = self._build_initial_prompt(prompt, schema)
        
        for attempt in range(self.max_retries):
            # Get LLM response
            if hasattr(llm_client, 'complete'):
                response = llm_client.complete(current_prompt, **llm_kwargs)
            else:
                # Assume it's a facade
                llm_response = llm_client.complete(current_prompt, **llm_kwargs)
                response = llm_response.text if hasattr(llm_response, 'text') else str(llm_response)
            
            # Try to validate
            try:
                result = self.validate(response, schema, extract_json)
                
                # Log successful attempt
                self.validation_history[-1].attempt = attempt + 1
                
                return result
                
            except ValidationError as e:
                if attempt < self.max_retries - 1:
                    # Build retry prompt with error feedback
                    current_prompt = self._build_retry_prompt(
                        prompt,
                        response,
                        str(e),
                        schema
                    )
                else:
                    # Final attempt failed
                    raise ValidationError(
                        f"Validation failed after {self.max_retries} attempts. "
                        f"Last error: {str(e)}"
                    )
        
        raise ValidationError("Unexpected error in validation loop")
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from text"""
        # Try to find JSON block
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',  # ```json { ... } ```
            r'```\s*(\{.*?\})\s*```',       # ``` { ... } ```
            r'(\{[^{]*?"[^"]+"\s*:[^}]*\})',  # Bare { ... }
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1)
        
        # Try to extract anything between first { and last }
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1 and start < end:
            return text[start:end + 1]
        
        # Return as-is and let JSON parser fail
        return text
    
    def _build_initial_prompt(self, prompt: str, schema: Type[BaseModel]) -> str:
        """Build initial prompt with schema instructions"""
        schema_json = schema.model_json_schema()
        
        return f"""{prompt}

Please respond with valid JSON matching this schema:

{json.dumps(schema_json, indent=2)}

Return only the JSON object, no additional text."""
    
    def _build_retry_prompt(
        self,
        original_prompt: str,
        failed_response: str,
        error: str,
        schema: Type[BaseModel]
    ) -> str:
        """Build retry prompt with error feedback"""
        schema_json = schema.model_json_schema()
        
        return f"""{original_prompt}

Your previous response had an error:
{error}

Previous response:
{failed_response}

Please fix the error and return valid JSON matching this schema:

{json.dumps(schema_json, indent=2)}

Return only the corrected JSON object."""
    
    def get_validation_history(self) -> List[ValidationResult]:
        """Get validation history"""
        return self.validation_history.copy()
    
    def clear_history(self) -> None:
        """Clear validation history"""
        self.validation_history.clear()


class StructuredOutputValidator(ResponseValidator):
    """Validator for structured outputs with custom formats"""
    
    def validate_list(
        self,
        response: str,
        item_schema: Type[T],
        min_items: Optional[int] = None,
        max_items: Optional[int] = None
    ) -> List[T]:
        """
        Validate response as list of items.
        
        Args:
            response: LLM response
            item_schema: Schema for list items
            min_items: Minimum number of items
            max_items: Maximum number of items
            
        Returns:
            List of validated items
        """
        json_str = self._extract_json(response)
        data = json.loads(json_str)
        
        if not isinstance(data, list):
            raise ValidationError("Response is not a list")
        
        if min_items and len(data) < min_items:
            raise ValidationError(f"List has fewer than {min_items} items")
        
        if max_items and len(data) > max_items:
            raise ValidationError(f"List has more than {max_items} items")
        
        validated_items = []
        for item in data:
            validated_items.append(item_schema(**item))
        
        return validated_items
    
    def validate_choice(
        self,
        response: str,
        choices: List[str],
        case_sensitive: bool = False
    ) -> str:
        """
        Validate response is one of allowed choices.
        
        Args:
            response: LLM response
            choices: Allowed choices
            case_sensitive: Whether matching is case-sensitive
            
        Returns:
            Validated choice
        """
        response = response.strip()
        
        if not case_sensitive:
            response_lower = response.lower()
            choices_lower = [c.lower() for c in choices]
            
            if response_lower in choices_lower:
                idx = choices_lower.index(response_lower)
                return choices[idx]
        else:
            if response in choices:
                return response
        
        raise ValidationError(
            f"Response '{response}' not in allowed choices: {choices}"
        )
    
    def validate_range(
        self,
        response: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> float:
        """Validate response is a number in range"""
        try:
            value = float(response.strip())
        except ValueError:
            raise ValidationError(f"Response '{response}' is not a number")
        
        if min_value is not None and value < min_value:
            raise ValidationError(f"Value {value} is less than minimum {min_value}")
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"Value {value} is greater than maximum {max_value}")
        
        return value


def validate_json_response(
    response: str,
    required_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Simple JSON validation without schema.
    
    Args:
        response: LLM response
        required_keys: Required keys in JSON
        
    Returns:
        Parsed JSON data
    """
    try:
        # Try to extract JSON
        start = response.find('{')
        end = response.rfind('}')
        
        if start != -1 and end != -1:
            json_str = response[start:end + 1]
        else:
            json_str = response
        
        data = json.loads(json_str)
        
        if required_keys:
            missing = [k for k in required_keys if k not in data]
            if missing:
                raise ValidationError(f"Missing required keys: {missing}")
        
        return data
        
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON: {e}")


def create_retry_wrapper(
    validator: ResponseValidator,
    schema: Type[T]
) -> Callable:
    """
    Create a decorator for automatic validation and retry.
    
    Args:
        validator: ResponseValidator instance
        schema: Pydantic model schema
        
    Returns:
        Decorator function
    """
    def decorator(llm_func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> T:
            prompt = args[0] if args else kwargs.get('prompt', '')
            llm_client = kwargs.get('llm_client')
            
            if not llm_client:
                raise ValueError("llm_client must be provided")
            
            return validator.validate_with_retry(
                llm_client,
                prompt,
                schema,
                **kwargs
            )
        
        return wrapper
    
    return decorator
