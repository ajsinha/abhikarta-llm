"""
Model Registry Test and Demonstration Script

This script demonstrates all features of the ModelRegistry including:
- Singleton pattern
- Loading providers from JSON files
- Accessing models by various criteria
- Finding cheapest models
- Auto-reload functionality
- Thread safety
"""

import time
import threading

from model_management.model_registry_json import ModelRegistryJSON
from model_registry import ModelRegistry
from exceptions import (
    ProviderNotFoundException,
    ProviderDisabledException,
    ModelNotFoundException,
    ModelDisabledException,
    NoModelsAvailableException
)


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def test_singleton_pattern():
    """Test that ModelRegistry follows singleton pattern."""
    print_section("Testing Singleton Pattern")

    # First initialization
    registry1 = ModelRegistryJSON.get_instance("/home/claude/config", auto_reload_interval_minutes=10)
    print(f"First instance: {registry1}")

    # Second call should return same instance
    registry2 = ModelRegistryJSON.get_instance()
    print(f"Second instance: {registry2}")

    print(f"Same instance? {registry1 is registry2}")
    assert registry1 is registry2, "Singleton pattern violated!"
    print("✓ Singleton pattern working correctly")


def test_get_all_providers(registry: ModelRegistry):
    """Test retrieving all providers."""
    print_section("Getting All Providers")

    providers = registry.get_all_providers()
    print(f"Found {len(providers)} enabled providers:")

    for name, provider in providers.items():
        print(f"\n  {name}:")
        print(f"    API Version: {provider.api_version}")
        print(f"    Base URL: {provider.base_url}")
        print(f"    Models: {provider.get_model_count()}")
        print(f"    Enabled: {provider.enabled}")


def test_get_provider_by_name(registry: ModelRegistry):
    """Test retrieving a specific provider."""
    print_section("Getting Provider by Name")

    try:
        provider = registry.get_provider_by_name("anthropic")
        print(f"✓ Found provider: {provider}")
        print(f"  Models: {provider.get_model_count()}")
    except ProviderNotFoundException as e:
        print(f"✗ {e}")

    # Test with non-existent provider
    try:
        provider = registry.get_provider_by_name("nonexistent")
        print(f"✗ Should have raised ProviderNotFoundException")
    except ProviderNotFoundException as e:
        print(f"✓ Correctly raised: {e}")


def test_get_model_from_provider(registry: ModelRegistry):
    """Test retrieving a specific model from a provider."""
    print_section("Getting Model from Provider by Name")

    # Test with existing model
    try:
        model = registry.get_model_from_provider_by_name("google", "gemini-1.5-pro")
        print(f"✓ Found model: {model.name}")
        print(f"  Description: {model.description}")
        print(f"  Context window: {model.context_window:,}")
        print(f"  Max output: {model.max_output:,}")
        print(f"  Version: {model.version}")
    except (ModelNotFoundException, ProviderNotFoundException) as e:
        print(f"✗ {e}")

    # Test with non-existent model
    try:
        model = registry.get_model_from_provider_by_name("anthropic", "nonexistent-model")
        print(f"✗ Should have raised ModelNotFoundException")
    except ModelNotFoundException as e:
        print(f"✓ Correctly raised: {e}")


def test_get_model_with_capability(registry: ModelRegistry):
    """Test retrieving a model by name and capability."""
    print_section("Getting Model by Name and Capability")

    # Test with model that has the capability
    try:
        model = registry.get_model_from_provider_by_name_capability(
            "google",
            "gemini-1.5-pro",
            "vision"
        )
        print(f"✓ Found vision-capable model: {model.name}")
        print(f"  Has vision: {model.has_capability('vision')}")
        print(f"  Has streaming: {model.has_capability('streaming')}")
    except (ModelNotFoundException, ProviderNotFoundException) as e:
        print(f"✗ {e}")

    # Test with model that doesn't have the capability
    try:
        model = registry.get_model_from_provider_by_name_capability(
            "cohere",
            "command-r-plus",
            "vision"
        )
        print(f"✗ Should have raised ModelNotFoundException")
    except ModelNotFoundException as e:
        print(f"✓ Correctly raised: {e}")


def test_get_cheapest_model_for_capability(registry: ModelRegistry):
    """Test finding the cheapest model for a capability across all providers."""
    print_section("Finding Cheapest Model for Capability")

    capabilities = ["chat", "vision", "function_calling"]

    for capability in capabilities:
        try:
            provider_name, model, cost = registry.get_cheapest_model_for_capability(
                capability,
                input_tokens=1_000_000,
                output_tokens=10_000
            )
            print(f"\n✓ Cheapest model for '{capability}':")
            print(f"  Provider: {provider_name}")
            print(f"  Model: {model.name}")
            print(f"  Cost for 1M input + 10K output: ${cost:.4f}")
        except NoModelsAvailableException as e:
            print(f"\n✗ {e}")


def test_get_cheapest_model_for_provider_and_capability(registry: ModelRegistry):
    """Test finding the cheapest model for a capability within a specific provider."""
    print_section("Finding Cheapest Model for Provider and Capability")

    test_cases = [
        ("google", "chat"),
        ("anthropic", "vision"),
        ("mistral", "function_calling"),
    ]

    for provider_name, capability in test_cases:
        try:
            model, cost = registry.get_cheapest_model_for_provider_and_capability(
                provider_name,
                capability,
                input_tokens=500_000,
                output_tokens=5_000
            )
            print(f"\n✓ Cheapest {provider_name} model for '{capability}':")
            print(f"  Model: {model.name}")
            print(f"  Cost for 500K input + 5K output: ${cost:.4f}")
        except (ProviderNotFoundException, NoModelsAvailableException) as e:
            print(f"\n✗ {e}")


def test_registry_summary(registry: ModelRegistry):
    """Test getting registry summary."""
    print_section("Registry Summary")

    summary = registry.get_registry_summary()

    print(f"Configuration Directory: {summary['config_directory']}")
    print(f"Enabled Providers: {summary['provider_count']}")
    print(f"Total Providers: {summary['total_provider_count']}")
    print(f"Total Models: {summary['total_model_count']}")
    print(f"Auto-reload Enabled: {summary['auto_reload_enabled']}")
    print(f"Auto-reload Interval: {summary['auto_reload_interval']} seconds")

    print("\nProvider Details:")
    for provider in summary['providers']:
        status = "✓" if provider['enabled'] else "✗"
        print(f"  {status} {provider['name']}: {provider['model_count']} models (API v{provider['api_version']})")


def test_auto_reload(registry: ModelRegistry):
    """Test auto-reload functionality."""
    print_section("Testing Auto-Reload Functionality")

    # Start auto-reload with short interval for testing
    print("Starting auto-reload with 5-second interval...")
    registry.start_auto_reload(interval_minutes=5)

    print("Waiting 12 seconds to see auto-reload in action...")
    print("(Check console for reload messages)")
    time.sleep(12)

    print("Stopping auto-reload...")
    registry.stop_auto_reload()
    print("✓ Auto-reload test completed")


def test_thread_safety(registry: ModelRegistry):
    """Test thread safety by accessing registry from multiple threads."""
    print_section("Testing Thread Safety")

    results = []
    errors = []

    def worker(thread_id: int):
        """Worker function that performs various registry operations."""
        try:
            # Get all providers
            providers = registry.get_all_providers()

            # Get cheapest model
            provider_name, model, cost = registry.get_cheapest_model_for_capability("chat")

            # Get specific model
            model = registry.get_model_from_provider_by_name("google", "gemini-1.5-pro")

            results.append(f"Thread {thread_id}: Success")
        except Exception as e:
            errors.append(f"Thread {thread_id}: {e}")

    # Create and start multiple threads
    threads = []
    num_threads = 10

    print(f"Starting {num_threads} concurrent threads...")
    for i in range(num_threads):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print(f"✓ All {len(results)} threads completed successfully")
    if errors:
        print(f"✗ {len(errors)} threads encountered errors:")
        for error in errors:
            print(f"  {error}")
    else:
        print("✓ No errors encountered in concurrent access")


def test_all_models_for_capability(registry: ModelRegistry):
    """Test getting all models across providers for a capability."""
    print_section("Getting All Models for Capability")

    capability = "vision"
    print(f"Finding all models with '{capability}' capability...")

    models = registry.get_all_models_for_capability(capability)
    print(f"\nFound {len(models)} vision-capable models:")

    for provider_name, model in models[:10]:  # Show first 10
        cost = model.calculate_cost(100000, 1000)
        print(f"  {provider_name}/{model.name}")
        print(f"    Context: {model.context_window:,} | Cost (100K in, 1K out): ${cost:.4f}")

    if len(models) > 10:
        print(f"  ... and {len(models) - 10} more models")


def run_all_tests():
    """Run all test functions."""
    print("\n" + "=" * 80)
    print(" MODEL REGISTRY - COMPREHENSIVE TEST SUITE")
    print("=" * 80)

    # Test singleton and get instance
    test_singleton_pattern()
    registry = ModelRegistryJSON.get_instance()

    # Run all tests
    test_get_all_providers(registry)
    test_get_provider_by_name(registry)
    test_get_model_from_provider(registry)
    test_get_model_with_capability(registry)
    test_all_models_for_capability(registry)
    test_get_cheapest_model_for_capability(registry)
    test_get_cheapest_model_for_provider_and_capability(registry)
    test_registry_summary(registry)
    test_thread_safety(registry)

    # Auto-reload test (optional, takes time)
    # test_auto_reload(registry)

    print("\n" + "=" * 80)
    print(" ALL TESTS COMPLETED")
    print("=" * 80)
    print(f"\nFinal Registry State: {registry}")


if __name__ == "__main__":
    run_all_tests()