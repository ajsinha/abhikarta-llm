#!/usr/bin/env python3
"""
Automated Facade Fixer - Converts Dataclasses to Dicts

Fixes the bug in all LLM facades where TokenUsage and CompletionMetadata
are returned as dataclass objects instead of plain dicts.

Usage:
    python fix_facades_auto.py path/to/llm_provider/

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | Email: ajsinha@gmail.com
"""

import re
import sys
import os
from pathlib import Path


def fix_token_usage(content: str) -> str:
    """Convert TokenUsage(...) to plain dict."""
    # Pattern 1: TokenUsage with 3 parameters
    pattern = r'TokenUsage\(\s*prompt_tokens=([^,]+),\s*completion_tokens=([^,]+),\s*total_tokens=([^)]+)\s*\)'
    replacement = r'{\n                "prompt_tokens": \1,\n                "completion_tokens": \2,\n                "total_tokens": \3\n            }'
    content = re.sub(pattern, replacement, content)

    # Pattern 2: Variable assignment of TokenUsage
    pattern2 = r'(\w+)\s*=\s*TokenUsage\(\s*prompt_tokens=([^,]+),\s*completion_tokens=([^,]+),\s*total_tokens=([^)]+)\s*\)'
    replacement2 = r'\1 = {\n        "prompt_tokens": \2,\n        "completion_tokens": \3,\n        "total_tokens": \4\n    }'
    content = re.sub(pattern2, replacement2, content)

    return content


def fix_completion_metadata(content: str) -> str:
    """Convert CompletionMetadata(...) to plain dict."""
    # Pattern 1: CompletionMetadata(model=X)
    pattern1 = r'CompletionMetadata\(\s*model=([^,)]+)\s*\)'
    replacement1 = r'{\n                "model": \1\n            }'
    content = re.sub(pattern1, replacement1, content)

    # Pattern 2: CompletionMetadata(model=X, finish_reason=Y)
    pattern2 = r'CompletionMetadata\(\s*model=([^,]+),\s*finish_reason=([^,)]+)\s*\)'
    replacement2 = r'{\n                "model": \1,\n                "finish_reason": \2\n            }'
    content = re.sub(pattern2, replacement2, content)

    # Pattern 3: CompletionMetadata(model=X, usage=Y) - Remove usage parameter
    pattern3 = r'CompletionMetadata\(\s*model=([^,]+),\s*usage=[^)]+\s*\)'
    replacement3 = r'{\n                "model": \1\n            }'
    content = re.sub(pattern3, replacement3, content)

    # Pattern 4: CompletionMetadata(model=X, finish_reason=Y, usage=Z) - Remove usage
    pattern4 = r'CompletionMetadata\(\s*model=([^,]+),\s*finish_reason=([^,]+),\s*usage=[^)]+\s*\)'
    replacement4 = r'{\n                "model": \1,\n                "finish_reason": \2\n            }'
    content = re.sub(pattern4, replacement4, content)

    return content


def fix_facade_file(filepath: Path) -> tuple[bool, str, int]:
    """
    Fix a single facade file.

    Returns:
        (success, message, changes_made)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()

        content = original_content

        # Count occurrences before fixing
        token_usage_count = len(re.findall(r'TokenUsage\(', content))
        metadata_count = len(re.findall(r'CompletionMetadata\(', content))
        total_before = token_usage_count + metadata_count

        if total_before == 0:
            return (True, f"✅ {filepath.name}: No issues found", 0)

        # Apply fixes
        content = fix_token_usage(content)
        content = fix_completion_metadata(content)

        # Count after fixing
        token_usage_after = len(re.findall(r'TokenUsage\(', content))
        metadata_after = len(re.findall(r'CompletionMetadata\(', content))
        changes_made = (token_usage_count - token_usage_after) + (metadata_count - metadata_after)

        if content == original_content:
            return (True, f"⚠️  {filepath.name}: No changes made (unexpected)", 0)

        # Backup original
        backup_path = filepath.with_suffix('.py.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)

        # Write fixed version
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return (True, f"✅ {filepath.name}: Fixed {changes_made} occurrences (backup created)", changes_made)

    except Exception as e:
        return (False, f"❌ {filepath.name}: Error - {e}", 0)


def main():
    """Main function."""


    provider_dir = Path('/home/ashutosh/PycharmProjects/abhikarta-llm/llm_provider/facade_impl')

    if not provider_dir.exists():
        print(f"❌ Directory not found: {provider_dir}")
        sys.exit(1)

    if not provider_dir.is_dir():
        print(f"❌ Not a directory: {provider_dir}")
        sys.exit(1)

    print("=" * 80)
    print("LLM Facade Fixer - Converting Dataclasses to Dicts")
    print("=" * 80)
    print()
    print(f"Scanning directory: {provider_dir}")
    print()

    # Find all facade files
    facade_files = list(provider_dir.glob("*_facade.py"))

    if not facade_files:
        print(f"⚠️  No facade files (*_facade.py) found in {provider_dir}")
        sys.exit(1)

    print(f"Found {len(facade_files)} facade files:")
    for f in facade_files:
        print(f"  - {f.name}")
    print()

    # Process each file
    results = []
    total_changes = 0

    for filepath in facade_files:
        success, message, changes = fix_facade_file(filepath)
        results.append((success, message))
        total_changes += changes
        print(message)

    # Summary
    print()
    print("=" * 80)
    successful = sum(1 for s, _ in results if s)
    print(f"Summary: {successful}/{len(results)} files processed successfully")
    print(f"Total changes: {total_changes} dataclass instances converted to dicts")
    print()
    print("Backup files created with .backup extension")
    print("=" * 80)

    if successful < len(results):
        sys.exit(1)

    print()
    print("✅ All facades fixed! Restart your Flask app to use the corrected facades.")


if __name__ == '__main__':
    main()