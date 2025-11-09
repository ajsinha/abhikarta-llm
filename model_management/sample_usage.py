"""
Abhikarta LLM Model Management - Sample Usage Script

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

This script demonstrates how to use the Abhikarta LLM Model Management System
with both Database and JSON implementations, including the new auto-reload API.
"""

import os
import time
from model_registry_db import ModelRegistryDB
from model_registry_json import ModelRegistryJSON
from model_management import ModelCapability
from exceptions import (
    ProviderNotFoundException,
    ModelNotFoundException,
    NoModelsAvailableException
)


def demo_database_implementation(db_path: str, json_dir: str = None):
    """
    Demonstrate the Database implementation (ModelRegistryDB).
    
    Args:
        db_path: Path to SQLite database
        json_dir: Optional directory containing JSON config files
    """
    print("\n" + "=" * 70)
    print("DATABASE IMPLEMENTATION DEMO (ModelRegistryDB)")
    print("=" * 70)
    
    # 1. Initialize registry
    print(f"\n1. Initializing database at: {db_path}")
    registry = ModelRegistryDB.get_instance(db_connection_pool_name=db_path)
    print("   ✓ Database initialized")
    
    # 2. Import JSON files if directory provided
    if json_dir and os.path.exists(json_dir):
        print(f"\n2. Importing JSON configurations from: {json_dir}")
        loaded_providers = registry.load_json_directory(json_dir)
        print(f"   ✓ Loaded {len(loaded_providers)} providers: {', '.join(loaded_providers)}")
    else:
        print("\n2. No JSON directory provided, skipping import")
    
    # 3. Show summary
    print("\n3. Database Summary:")
    summary = registry.get_registry_summary()
    print(f"   - Total providers: {summary['total_provider_count']}")
    print(f"   - Enabled providers: {summary['provider_count']}")
    print(f"   - Total models: {summary['total_model_count']}")
    
    # 4. Demonstrate auto-reload API (no-op for database)
    print("\n4. Testing auto-reload API:")
    print("   (Note: Auto-reload is not needed for database implementation)")
    print("   (Database changes are reflected immediately on next query)")
    registry.start_auto_reload(interval_minutes=5)
    registry.stop_auto_reload()
    print("   ✓ Auto-reload API methods are available for compatibility")
    
    # 5. Query examples
    print("\n5. Query Examples:")
    try:
        # Get all providers
        providers = registry.get_all_providers()
        print(f"   - Found {len(providers)} enabled providers")
        
        if providers:
            # Get first provider
            provider_name = list(providers.keys())[0]
            provider = providers[provider_name]
            print(f"   - Provider: {provider.provider}")
            print(f"   - Models: {provider.get_model_count()}")
            
            # Get models for capability
            chat_models = registry.get_all_models_for_capability(ModelCapability.CHAT.value)
            if chat_models:
                print(f"   - Chat models found: {len(chat_models)}")
                provider_name, model = chat_models[0]
                print(f"   - Example: {provider_name}/{model.name}")
                
                # Calculate cost
                cost = model.calculate_cost(100000, 1000)
                print(f"   - Cost for 100k input + 1k output: ${cost:.4f}")
                
                # Demonstrate new method: get_model_from_provider_by_name_capability
                try:
                    print(f"\n   - Testing get_model_from_provider_by_name_capability:")
                    model_with_cap = registry.get_model_from_provider_by_name_capability(
                        provider_name,
                        model.name,
                        ModelCapability.CHAT.value
                    )
                    print(f"     ✓ Verified: {model_with_cap.name} has 'chat' capability")
                except NoModelsAvailableException as e:
                    print(f"     ✗ Model doesn't have required capability: {e}")
    except Exception as e:
        print(f"   ! Query example skipped: {e}")
    
    return registry


def demo_json_implementation(json_dir: str):
    """
    Demonstrate the JSON implementation (ModelRegistryJSON).
    
    Args:
        json_dir: Directory containing JSON config files
    """
    print("\n" + "=" * 70)
    print("JSON IMPLEMENTATION DEMO (ModelRegistryJSON)")
    print("=" * 70)
    
    # 1. Initialize registry
    print(f"\n1. Initializing from directory: {json_dir}")
    if not os.path.exists(json_dir):
        print(f"   ! Directory not found: {json_dir}")
        print("   Skipping JSON implementation demo")
        return None
    
    # Reset instance to demonstrate fresh initialization
    ModelRegistryJSON.reset_instance()
    registry = ModelRegistryJSON.get_instance(json_dir)
    print("   ✓ Registry initialized from JSON files")
    
    # 2. Show summary
    print("\n2. Registry Summary:")
    summary = registry.get_registry_summary()
    print(f"   - Providers: {summary['provider_count']}")
    print(f"   - Total models: {summary['total_model_count']}")
    print(f"   - Config directory: {summary['config_directory']}")
    print(f"   - Auto-reload: {summary['auto_reload_enabled']}")
    
    # 3. Start auto-reload with default interval
    print("\n3. Starting auto-reload with default interval (10 minutes):")
    registry.start_auto_reload()  # Uses default 10 minutes
    
    summary = registry.get_registry_summary()
    print(f"   - Auto-reload enabled: {summary['auto_reload_enabled']}")
    print(f"   - Interval: {summary['auto_reload_interval_minutes']} minutes")
    print(f"   - Interval (seconds): {summary['auto_reload_interval_seconds']} seconds")
    print("   ✓ Background thread started (checking for file changes)")
    
    # 4. Query examples
    print("\n4. Query Examples:")
    try:
        providers = registry.get_all_providers()
        if providers:
            print(f"   - Found {len(providers)} providers")
            
            for name, provider in list(providers.items())[:3]:  # Show first 3
                print(f"   - {name}: {provider.get_model_count()} models")
        else:
            print("   - No providers loaded")
    except Exception as e:
        print(f"   ! Query example skipped: {e}")
    
    # 5. Manual reload
    print("\n5. Manual reload test:")
    registry.reload_from_storage()
    print("   ✓ Successfully reloaded from JSON files")
    
    # 6. Stop auto-reload
    print("\n6. Stopping auto-reload:")
    registry.stop_auto_reload()
    summary = registry.get_registry_summary()
    print(f"   - Auto-reload enabled: {summary['auto_reload_enabled']}")
    print("   ✓ Background thread stopped cleanly")
    
    return registry


def demo_auto_reload_with_custom_interval():
    """
    Demonstrate auto-reload with custom intervals.
    """
    print("\n" + "=" * 70)
    print("AUTO-RELOAD WITH CUSTOM INTERVALS")
    print("=" * 70)
    
    json_dir = "./json_configs"
    if not os.path.exists(json_dir):
        print(f"   ! Directory not found: {json_dir}")
        print("   Skipping custom interval demo")
        return
    
    print("\n1. Initialize registry:")
    ModelRegistryJSON.reset_instance()
    registry = ModelRegistryJSON.get_instance(json_dir)
    print("   ✓ Registry initialized (auto-reload not started yet)")
    
    # 2. Start with custom interval
    print("\n2. Start auto-reload with 2-minute interval:")
    registry.start_auto_reload(interval_minutes=2)
    
    summary = registry.get_registry_summary()
    print(f"   - Interval: {summary['auto_reload_interval_minutes']} minutes")
    print(f"   - Seconds: {summary['auto_reload_interval_seconds']} seconds")
    print("   ✓ Checking for changes every 2 minutes")
    
    # 3. Try to start again (should show already running)
    print("\n3. Attempt to start again:")
    registry.start_auto_reload(interval_minutes=5)
    print("   (Message above shows it's already running)")
    
    # 4. Wait a few seconds
    print("\n4. Simulating runtime...")
    for i in range(3, 0, -1):
        print(f"   Waiting {i} seconds...", end='\r')
        time.sleep(1)
    print("   ✓ Background thread is actively monitoring files")
    
    # 5. Stop
    print("\n5. Clean shutdown:")
    registry.stop_auto_reload()
    print("   ✓ Auto-reload stopped")


def demo_api_consistency():
    """
    Demonstrate that both implementations share the same API.
    """
    print("\n" + "=" * 70)
    print("API CONSISTENCY DEMO")
    print("=" * 70)
    
    print("\n1. Both implementations support auto-reload API:")
    print("   - start_auto_reload(interval_minutes=10)")
    print("   - stop_auto_reload()")
    print("   - reload_from_storage()")
    
    print("\n2. Database Implementation:")
    print("   - Auto-reload methods are no-ops (not needed)")
    print("   - Database changes are immediately visible")
    print("   - Provided for API compatibility")
    
    print("\n3. JSON Implementation:")
    print("   - Auto-reload actively monitors file changes")
    print("   - Detects new/modified/deleted files")
    print("   - Uses MD5 hashing for change detection")
    
    print("\n4. Switching implementations is easy:")
    print("   # Just change the import!")
    print("   from model_registry_db import ModelRegistryDB as Registry")
    print("   # OR")
    print("   from model_registry_json import ModelRegistryJSON as Registry")
    print("")
    print("   # Same API works for both")
    print("   registry = Registry.get_instance(...)")
    print("   registry.start_auto_reload(interval_minutes=5)")
    print("   registry.stop_auto_reload()")


def demo_capability_validation():
    """
    Demonstrate the new get_model_from_provider_by_name_capability method.
    """
    print("\n" + "=" * 70)
    print("CAPABILITY VALIDATION DEMO")
    print("=" * 70)
    
    print("\nThe new get_model_from_provider_by_name_capability() method")
    print("combines model retrieval with capability validation.")
    
    json_dir = "./json_configs"
    if not os.path.exists(json_dir):
        print(f"\n   ! Directory not found: {json_dir}")
        print("   Skipping capability validation demo")
        return
    
    try:
        # Use database for this demo
        ModelRegistryDB.reset_instance()
        registry = ModelRegistryDB.get_instance(db_connection_pool_name=":memory:")
        
        # Try to load configs
        if os.path.exists(json_dir):
            registry.load_json_directory(json_dir)
        
        providers = registry.get_all_providers()
        if not providers:
            print("\n   ! No providers loaded")
            print("   Skipping capability validation demo")
            return
        
        print("\n1. Successful Validation:")
        print("   Finding a vision-capable model...")
        
        # Find a vision model
        vision_models = registry.get_all_models_for_capability("vision")
        if vision_models:
            provider_name, model = vision_models[0]
            
            try:
                validated_model = registry.get_model_from_provider_by_name_capability(
                    provider_name,
                    model.name,
                    "vision"
                )
                print(f"   ✓ Success: {provider_name}/{validated_model.name}")
                print(f"     Model has 'vision' capability")
                print(f"     Context: {validated_model.context_window:,} tokens")
            except NoModelsAvailableException as e:
                print(f"   ✗ Unexpected: {e}")
        else:
            print("   ! No vision models found")
        
        print("\n2. Failed Validation:")
        print("   Attempting to get a model with wrong capability...")
        
        # Try to get a model that doesn't have a specific capability
        chat_models = registry.get_all_models_for_capability("chat")
        if chat_models:
            provider_name, model = chat_models[0]
            
            # Check if it has vision
            if not model.has_capability("vision"):
                try:
                    registry.get_model_from_provider_by_name_capability(
                        provider_name,
                        model.name,
                        "vision"  # This will fail
                    )
                    print(f"   ✗ Unexpected: Should have failed")
                except NoModelsAvailableException as e:
                    print(f"   ✓ Expected failure:")
                    print(f"     Model: {provider_name}/{model.name}")
                    print(f"     Missing: 'vision' capability")
                    print(f"     Error: {str(e)[:60]}...")
            else:
                print("   ! All chat models also have vision")
        
        print("\n3. Practical Use Cases:")
        print("   a) Ensure model supports multimodal input:")
        print("      model = registry.get_model_from_provider_by_name_capability(")
        print("          'google', 'gemini-1.5-pro', 'vision'")
        print("      )")
        print("")
        print("   b) Verify function calling support:")
        print("      model = registry.get_model_from_provider_by_name_capability(")
        print("          'anthropic', 'claude-opus-4', 'function_calling'")
        print("      )")
        print("")
        print("   c) Validate streaming capability:")
        print("      model = registry.get_model_from_provider_by_name_capability(")
        print("          'openai', 'gpt-4o', 'streaming'")
        print("      )")
        
        print("\n4. Benefits:")
        print("   ✓ Single method call for retrieval + validation")
        print("   ✓ Clear error message if capability missing")
        print("   ✓ Prevents runtime errors from using wrong model")
        print("   ✓ Safer than checking capability separately")
        
    except Exception as e:
        print(f"\n   Error during demo: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point for the demonstration script."""
    print("\n" + "=" * 70)
    print("ABHIKARTA LLM MODEL MANAGEMENT SYSTEM")
    print("Comprehensive Demonstration")
    print("=" * 70)
    
    # Configuration
    DB_PATH = "./demo_models.db_management"
    JSON_DIR = "./json_configs"
    
    print("\nConfiguration:")
    print(f"   Database: {DB_PATH}")
    print(f"   JSON Directory: {JSON_DIR}")
    
    try:
        # Demo 1: Database Implementation
        print("\n" + "#" * 70)
        print("# PART 1: Database Implementation")
        print("#" * 70)
        db_registry = demo_database_implementation(DB_PATH, JSON_DIR)
        
        # Demo 2: JSON Implementation
        print("\n" + "#" * 70)
        print("# PART 2: JSON Implementation")
        print("#" * 70)
        json_registry = demo_json_implementation(JSON_DIR)
        
        # Demo 3: Custom Intervals
        if json_registry:
            print("\n" + "#" * 70)
            print("# PART 3: Custom Auto-Reload Intervals")
            print("#" * 70)
            demo_auto_reload_with_custom_interval()
        
        # Demo 4: API Consistency
        print("\n" + "#" * 70)
        print("# PART 4: API Consistency")
        print("#" * 70)
        demo_api_consistency()
        
        # Demo 5: Capability Validation (NEW!)
        print("\n" + "#" * 70)
        print("# PART 5: Capability Validation (NEW!)")
        print("#" * 70)
        demo_capability_validation()
        
        # Summary
        print("\n" + "=" * 70)
        print("DEMONSTRATION COMPLETE!")
        print("=" * 70)
        
        print("\nKey Features Demonstrated:")
        print("  ✓ Database implementation (ModelRegistryDB)")
        print("  ✓ JSON implementation (ModelRegistryJSON)")
        print("  ✓ Auto-reload API (abstract base class)")
        print("  ✓ Default interval: 10 minutes")
        print("  ✓ Custom intervals supported")
        print("  ✓ Same API for both implementations")
        print("  ✓ NEW: Capability validation method")
        
        print("\nAuto-Reload Summary:")
        print("  • Abstract method in ModelRegistry base class")
        print("  • Default interval: 10 minutes")
        print("  • Parameter: interval_minutes (int)")
        print("  • Database: No-op (not needed)")
        print("  • JSON: Active file watching")
        
        print("\nNew Method Summary:")
        print("  • get_model_from_provider_by_name_capability()")
        print("  • Combines retrieval + validation")
        print("  • Ensures model has required capability")
        print("  • Raises NoModelsAvailableException if not")
        
        print("\nUsage Examples:")
        print("  # Auto-reload (default 10 minutes)")
        print("  registry.start_auto_reload()")
        print("")
        print("  # Auto-reload (custom 5 minutes)")
        print("  registry.start_auto_reload(interval_minutes=5)")
        print("")
        print("  # Stop auto-reload")
        print("  registry.stop_auto_reload()")
        print("")
        print("  # Get model with capability validation (NEW!)")
        print("  model = registry.get_model_from_provider_by_name_capability(")
        print("      'google', 'gemini-1.5-pro', 'vision'")
        print("  )")
        
        print("\nNext Steps:")
        print("  1. Choose your implementation:")
        print("     - Production: ModelRegistryDB (database-backed)")
        print("     - Development: ModelRegistryJSON (auto-reload)")
        print("  2. Load your provider configurations")
        print("  3. Start auto-reload if using JSON")
        print("  4. Use the registry API to find optimal models")
        
        print("\nDocumentation:")
        print("  - Architecture: Model Registry System - Architecture.md")
        print("  - Quick Reference: Model Registry System - Quick Reference Guide.md")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("Copyright © 2025-2030 Ashutosh Sinha - All Rights Reserved")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
