"""
Quick verification script for the suffix removal fix

Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""

# Test the suffix removal
def test_suffix_removal():
    suffix = ":abhikartamcp"
    print(f"Suffix: '{suffix}'")
    print(f"Suffix length: {len(suffix)} characters")
    print()
    
    # Test cases
    test_cases = [
        "yahoo_search_symbols:abhikartamcp",
        "yahoo_get_quote:abhikartamcp",
        "yahoo_get_history:abhikartamcp",
        "duckdb_list_files:abhikartamcp",
        "duckdb_describe_table:abhikartamcp",
        "duckdb_get_stats:abhikartamcp",
        "duckdb_aggregate:abhikartamcp",
    ]
    
    print("Testing suffix removal:")
    print("-" * 70)
    
    for tool_name in test_cases:
        if tool_name.endswith(suffix):
            # Correct way (using length 13)
            original_correct = tool_name[:-13]
            
            # Wrong way (using length 14)
            original_wrong = tool_name[:-14]
            
            print(f"Full name:  {tool_name}")
            print(f"  Correct:  {original_correct}")
            print(f"  Wrong:    {original_wrong} ❌")
            print()

if __name__ == "__main__":
    test_suffix_removal()
