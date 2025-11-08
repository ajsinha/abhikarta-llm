"""
Example Usage of Abhikarta LLM Model Capability Enum

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

from model_management import ModelCapability, ProviderType
from typing import List, Set, Dict, Any


# ==================================================================================
# EXAMPLE 1: Basic Capability Checking
# ==================================================================================

def example_basic_usage():
    """Demonstrate basic usage of ModelCapability enum."""

    print("=== Example 1: Basic Capability Checking ===\n")

    # Simulate model capabilities (from JSON config)
    model_capabilities = {
        "chat": True,
        "streaming": True,
        "vision": True,
        "function_calling": True,
        "prompt_caching": True
    }

    # Check for specific capabilities using enum
    if ModelCapability.VISION.value in model_capabilities:
        print("✓ Model supports vision")

    if ModelCapability.FUNCTION_CALLING.value in model_capabilities:
        print("✓ Model supports function calling")

    if ModelCapability.EXTENDED_THINKING.value in model_capabilities:
        print("✓ Model supports extended thinking")
    else:
        print("✗ Model does not support extended thinking")

    print()


# ==================================================================================
# EXAMPLE 2: Filtering Models by Capabilities
# ==================================================================================

def filter_models_by_capabilities(
        models: List[Dict[str, Any]],
        required_capabilities: List[ModelCapability]
) -> List[Dict[str, Any]]:
    """
    Filter models that have all required capabilities.

    Args:
        models: List of model configurations
        required_capabilities: List of required ModelCapability enums

    Returns:
        Filtered list of models with all required capabilities
    """
    matching_models = []

    for model in models:
        capabilities = model.get("capabilities", {})

        # Check if all required capabilities are present and True
        has_all = all(
            capabilities.get(cap.value, False)
            for cap in required_capabilities
        )

        if has_all:
            matching_models.append(model)

    return matching_models


def example_filter_models():
    """Demonstrate filtering models by capabilities."""

    print("=== Example 2: Filtering Models by Capabilities ===\n")

    # Simulate model database
    models = [
        {
            "name": "claude-3-7-sonnet",
            "provider": "anthropic",
            "capabilities": {
                "chat": True,
                "vision": True,
                "function_calling": True,
                "extended_thinking": True,
                "prompt_caching": True
            }
        },
        {
            "name": "gpt-4o",
            "provider": "openai",
            "capabilities": {
                "chat": True,
                "vision": True,
                "audio_input": True,
                "audio_output": True,
                "function_calling": True
            }
        },
        {
            "name": "llama-3.1-8b",
            "provider": "groq",
            "capabilities": {
                "chat": True,
                "streaming": True,
                "function_calling": True
            }
        }
    ]

    # Find models with vision AND function calling
    required = [ModelCapability.VISION, ModelCapability.FUNCTION_CALLING]
    vision_models = filter_models_by_capabilities(models, required)

    print(f"Models with {[c.value for c in required]}:")
    for model in vision_models:
        print(f"  • {model['name']} ({model['provider']})")

    print()

    # Find models with extended thinking
    thinking_models = filter_models_by_capabilities(
        models,
        [ModelCapability.EXTENDED_THINKING]
    )

    print(f"Models with extended thinking:")
    for model in thinking_models:
        print(f"  • {model['name']} ({model['provider']})")

    print()


# ==================================================================================
# EXAMPLE 3: Using Capability Groups
# ==================================================================================

def example_capability_groups():
    """Demonstrate using predefined capability groups."""

    print("=== Example 3: Capability Groups ===\n")

    # Get all multimodal capabilities
    multimodal_caps = ModelCapability.get_multimodal_capabilities()
    print("Multimodal Capabilities:")
    for cap in multimodal_caps:
        print(f"  • {cap.value}")

    print()

    # Get all audio capabilities
    audio_caps = ModelCapability.get_audio_capabilities()
    print("Audio Capabilities:")
    for cap in audio_caps:
        print(f"  • {cap.value}")

    print()

    # Get all optimization capabilities
    optimization_caps = ModelCapability.get_optimization_capabilities()
    print("Optimization Capabilities:")
    for cap in optimization_caps:
        print(f"  • {cap.value}")

    print()


# ==================================================================================
# EXAMPLE 4: Capability Comparison Across Providers
# ==================================================================================

def compare_provider_capabilities(
        models: List[Dict[str, Any]],
        capability: ModelCapability
) -> Dict[str, List[str]]:
    """
    Compare which models from each provider support a capability.

    Args:
        models: List of model configurations
        capability: The capability to check

    Returns:
        Dictionary mapping provider to list of model names
    """
    provider_models = {}

    for model in models:
        capabilities = model.get("capabilities", {})

        if capabilities.get(capability.value, False):
            provider = model.get("provider", "unknown")
            if provider not in provider_models:
                provider_models[provider] = []
            provider_models[provider].append(model["name"])

    return provider_models


def example_provider_comparison():
    """Demonstrate comparing capabilities across providers."""

    print("=== Example 4: Provider Capability Comparison ===\n")

    models = [
        {"name": "claude-3-7-sonnet", "provider": "anthropic",
         "capabilities": {"vision": True, "extended_thinking": True}},
        {"name": "claude-3-5-haiku", "provider": "anthropic",
         "capabilities": {"vision": True}},
        {"name": "gpt-4o", "provider": "openai",
         "capabilities": {"vision": True, "audio_input": True}},
        {"name": "gpt-4o-mini", "provider": "openai",
         "capabilities": {"vision": True}},
        {"name": "gemini-1.5-pro", "provider": "google",
         "capabilities": {"vision": True, "video_input": True}},
        {"name": "llama-3.2-90b-vision", "provider": "groq",
         "capabilities": {"vision": True}},
    ]

    # Compare vision support
    vision_by_provider = compare_provider_capabilities(models, ModelCapability.VISION)

    print("Vision Support by Provider:")
    for provider, model_names in vision_by_provider.items():
        print(f"\n  {provider.upper()}:")
        for name in model_names:
            print(f"    • {name}")

    print()


# ==================================================================================
# EXAMPLE 5: Metadata Field Detection
# ==================================================================================

def example_metadata_detection():
    """Demonstrate detecting metadata vs boolean capabilities."""

    print("=== Example 5: Metadata Field Detection ===\n")

    # Test various capabilities
    test_capabilities = [
        ModelCapability.VISION,
        ModelCapability.DIMENSIONS,
        ModelCapability.LANGUAGES,
        ModelCapability.FUNCTION_CALLING,
        ModelCapability.EMBEDDING_TYPES
    ]

    print("Capability Type Detection:")
    for cap in test_capabilities:
        is_metadata = ModelCapability.is_metadata_field(cap)
        cap_type = "Metadata" if is_metadata else "Boolean"
        print(f"  • {cap.value:25s} → {cap_type}")

    print()


# ==================================================================================
# EXAMPLE 6: Building Capability Requirements
# ==================================================================================

class ModelRequirements:
    """Helper class to build and check model requirements."""

    def __init__(self):
        self.required: Set[ModelCapability] = set()
        self.optional: Set[ModelCapability] = set()
        self.excluded: Set[ModelCapability] = set()

    def require(self, *capabilities: ModelCapability) -> 'ModelRequirements':
        """Add required capabilities."""
        self.required.update(capabilities)
        return self

    def prefer(self, *capabilities: ModelCapability) -> 'ModelRequirements':
        """Add optional/preferred capabilities."""
        self.optional.update(capabilities)
        return self

    def exclude(self, *capabilities: ModelCapability) -> 'ModelRequirements':
        """Add capabilities to exclude."""
        self.excluded.update(capabilities)
        return self

    def matches(self, model_capabilities: Dict[str, Any]) -> bool:
        """Check if model capabilities match requirements."""
        # Check all required capabilities are present
        for cap in self.required:
            if not model_capabilities.get(cap.value, False):
                return False

        # Check no excluded capabilities are present
        for cap in self.excluded:
            if model_capabilities.get(cap.value, False):
                return False

        return True

    def score(self, model_capabilities: Dict[str, Any]) -> float:
        """
        Score how well model matches requirements.

        Returns:
            Score from 0.0 to 1.0, where 1.0 is perfect match
        """
        if not self.matches(model_capabilities):
            return 0.0

        # Start with base score for matching required capabilities
        score = 0.5

        # Add score for each optional capability present
        if self.optional:
            optional_matches = sum(
                1 for cap in self.optional
                if model_capabilities.get(cap.value, False)
            )
            score += 0.5 * (optional_matches / len(self.optional))

        return score


def example_requirements_builder():
    """Demonstrate building and using model requirements."""

    print("=== Example 6: Building Model Requirements ===\n")

    # Build requirements for a multimodal RAG application
    requirements = ModelRequirements() \
        .require(ModelCapability.CHAT, ModelCapability.STREAMING) \
        .require(ModelCapability.FUNCTION_CALLING) \
        .prefer(ModelCapability.VISION, ModelCapability.PROMPT_CACHING) \
        .exclude(ModelCapability.DEPRECATED)

    # Test models
    models = [
        {
            "name": "claude-3-7-sonnet",
            "capabilities": {
                "chat": True,
                "streaming": True,
                "function_calling": True,
                "vision": True,
                "prompt_caching": True
            }
        },
        {
            "name": "gpt-4o-mini",
            "capabilities": {
                "chat": True,
                "streaming": True,
                "function_calling": True,
                "vision": True
            }
        },
        {
            "name": "llama-3.1-8b",
            "capabilities": {
                "chat": True,
                "streaming": True,
                "function_calling": True
            }
        }
    ]

    print("Scoring models against requirements:")
    print("Required: chat, streaming, function_calling")
    print("Preferred: vision, prompt_caching")
    print()

    for model in models:
        score = requirements.score(model["capabilities"])
        matches = requirements.matches(model["capabilities"])
        status = "✓" if matches else "✗"
        print(f"{status} {model['name']:25s} Score: {score:.2f}")

    print()


# ==================================================================================
# EXAMPLE 7: Dynamic Capability Discovery
# ==================================================================================

def discover_capabilities(model_config: Dict[str, Any]) -> List[ModelCapability]:
    """
    Discover all capabilities that a model has.

    Args:
        model_config: Model configuration dictionary

    Returns:
        List of ModelCapability enums that the model supports
    """
    capabilities_dict = model_config.get("capabilities", {})
    discovered = []

    for capability_name, value in capabilities_dict.items():
        # Try to match with enum
        try:
            cap_enum = ModelCapability(capability_name)
            # Only include if it's boolean True or metadata field
            if value is True or ModelCapability.is_metadata_field(cap_enum):
                discovered.append(cap_enum)
        except ValueError:
            # Unknown capability, skip it
            pass

    return discovered


def example_capability_discovery():
    """Demonstrate dynamic capability discovery."""

    print("=== Example 7: Dynamic Capability Discovery ===\n")

    model = {
        "name": "gpt-4o",
        "capabilities": {
            "chat": True,
            "streaming": True,
            "vision": True,
            "audio_input": True,
            "audio_output": True,
            "function_calling": True,
            "json_mode": True
        }
    }

    capabilities = discover_capabilities(model)

    print(f"Discovered capabilities for {model['name']}:")

    # Group by category
    core = [c for c in capabilities if c in ModelCapability.get_core_capabilities()]
    multimodal = [c for c in capabilities if c in ModelCapability.get_multimodal_capabilities()]
    tools = [c for c in capabilities if c in ModelCapability.get_tool_capabilities()]
    other = [c for c in capabilities if c not in core + multimodal + tools]

    if core:
        print("\n  Core:")
        for cap in core:
            print(f"    • {cap.value}")

    if multimodal:
        print("\n  Multimodal:")
        for cap in multimodal:
            print(f"    • {cap.value}")

    if tools:
        print("\n  Tools:")
        for cap in tools:
            print(f"    • {cap.value}")

    if other:
        print("\n  Other:")
        for cap in other:
            print(f"    • {cap.value}")

    print()


# ==================================================================================
# MAIN EXECUTION
# ==================================================================================

def main():
    """Run all examples."""

    print("\n" + "=" * 70)
    print("Abhikarta LLM Model Capability Enum - Usage Examples")
    print("=" * 70 + "\n")

    example_basic_usage()
    example_filter_models()
    example_capability_groups()
    example_provider_comparison()
    example_metadata_detection()
    example_requirements_builder()
    example_capability_discovery()

    print("=" * 70)
    print("All examples completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()