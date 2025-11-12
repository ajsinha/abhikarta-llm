# URGENT BUG FIX - Tool Name Extraction

**Date:** 2025-11-12  
**Severity:** High  
**Status:** Fixed  

---

## Issue

**Error reported:**
```
MCP Error -32602: Tool not found: yahoo_search_symbol
```

The tool name was being sent to the MCP server with one character missing from the end.

---

## Root Cause

**Off-by-one error in `abhikarta_base_tool.py`:**

The suffix `:abhikartamcp` is **13 characters**, not 14.

**Incorrect code:**
```python
self.original_tool_name = name[:-14]  # WRONG - cuts off 14 chars
```

**Result:**
- `yahoo_search_symbols:abhikartamcp` → `yahoo_search_symbol` ❌
- `duckdb_list_files:abhikartamcp` → `duckdb_list_file` ❌

---

## Fix

**Corrected code:**
```python
self.original_tool_name = name[:-13]  # CORRECT - cuts off 13 chars
```

**Result:**
- `yahoo_search_symbols:abhikartamcp` → `yahoo_search_symbols` ✓
- `duckdb_list_files:abhikartamcp` → `duckdb_list_files` ✓

---

## Verification

Run the test to verify:
```bash
python tests/test_suffix_fix.py
```

Expected output:
```
Suffix: ':abhikartamcp'
Suffix length: 13 characters

Testing suffix removal:
----------------------------------------------------------------------
Full name:  yahoo_search_symbols:abhikartamcp
  Correct:  yahoo_search_symbols
  Wrong:    yahoo_search_symbol ❌
```

---

## Files Changed

1. `abhikartamcp/abhikarta_base_tool.py` - Line ~64
   - Changed `name[:-14]` to `name[:-13]`

2. `tests/test_suffix_fix.py` - New verification test

---

## Impact

**Before fix:**
- All tool names sent to MCP server were missing the last character
- Tools could not be found/executed
- All examples would fail

**After fix:**
- Tool names are sent correctly
- All tools work as expected
- Examples run successfully

---

## Action Required

**If you downloaded the package before this fix:**

1. Re-download the updated archive
2. Or manually apply the fix:
   ```bash
   cd abhikarta_mcp_integration/abhikartamcp
   
   # Edit abhikarta_base_tool.py
   # Find line ~64:
   #   self.original_tool_name = name[:-14]
   # Change to:
   #   self.original_tool_name = name[:-13]
   ```

3. Verify the fix:
   ```bash
   python tests/test_suffix_fix.py
   ```

---

## Updated Version

**Version:** 1.0.1 (patch)  
**Release Date:** 2025-11-12  
**Status:** Fixed and tested

---

## Apology

We apologize for this critical bug in the initial release. Thank you for reporting it!

The issue has been fixed and thoroughly tested. All tools now work correctly.

---

**Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)**
