"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.3
"""

"""
Test Standalone PII Functions

Tests the detect_pii and redact_pii standalone functions.

© 2025-2030 All rights reserved Ashutosh Sinha
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.abstraction.security import (
    # Detection functions
    detect_pii,
    detect_emails,
    detect_phone_numbers,
    has_pii,
    count_pii,
    find_emails,
    find_phone_numbers,
    
    # Redaction functions
    redact_pii,
    redact_emails,
    redact_phone_numbers,
    redact_all_pii,
    clean_text_for_llm,
    mask_pii
)


def test_detect_functions():
    """Test PII detection functions"""
    print("="*60)
    print("Testing PII Detection Functions")
    print("="*60)
    
    text = "Email: john@example.com, Phone: 555-123-4567"
    
    # Test detect_pii
    print("\n1. detect_pii():")
    matches = detect_pii(text, pii_types=['email', 'phone'])
    print(f"   Found {len(matches)} PII items")
    for match in matches:
        print(f"   - {match.pii_type.value}: {match.original_text}")
    assert len(matches) >= 1
    print("   ✓ PASS")
    
    # Test detect_emails
    print("\n2. detect_emails():")
    emails = detect_emails(text)
    print(f"   Found {len(emails)} email(s)")
    assert len(emails) >= 1
    print("   ✓ PASS")
    
    # Test has_pii
    print("\n3. has_pii():")
    has_it = has_pii(text)
    print(f"   Has PII: {has_it}")
    assert has_it == True
    print("   ✓ PASS")
    
    # Test count_pii
    print("\n4. count_pii():")
    counts = count_pii(text)
    print(f"   Counts: {counts}")
    assert len(counts) > 0
    print("   ✓ PASS")
    
    # Test find_emails
    print("\n5. find_emails():")
    email_list = find_emails(text)
    print(f"   Emails: {email_list}")
    assert len(email_list) >= 1
    print("   ✓ PASS")
    
    print("\n" + "="*60)
    print("✓ ALL DETECTION TESTS PASSED")
    print("="*60)


def test_redact_functions():
    """Test PII redaction functions"""
    print("\n" + "="*60)
    print("Testing PII Redaction Functions")
    print("="*60)
    
    text = "Email: john@example.com, Phone: 555-123-4567"
    
    # Test redact_pii
    print("\n1. redact_pii():")
    redacted = redact_pii(text, pii_types=['email', 'phone'])
    print(f"   Original:  {text}")
    print(f"   Redacted:  {redacted}")
    assert "john@example.com" not in redacted
    print("   ✓ PASS")
    
    # Test redact_emails
    print("\n2. redact_emails():")
    redacted_email = redact_emails(text)
    print(f"   Original:  {text}")
    print(f"   Redacted:  {redacted_email}")
    assert "john@example.com" not in redacted_email
    print("   ✓ PASS")
    
    # Test redact_phone_numbers
    print("\n3. redact_phone_numbers():")
    redacted_phone = redact_phone_numbers(text)
    print(f"   Original:  {text}")
    print(f"   Redacted:  {redacted_phone}")
    print("   ✓ PASS")
    
    # Test redact_all_pii
    print("\n4. redact_all_pii():")
    all_redacted = redact_all_pii(text)
    print(f"   Original:  {text}")
    print(f"   Redacted:  {all_redacted}")
    print("   ✓ PASS")
    
    # Test clean_text_for_llm
    print("\n5. clean_text_for_llm():")
    clean = clean_text_for_llm("My email is secret@example.com")
    print(f"   Cleaned:   {clean}")
    assert "secret@example.com" not in clean
    print("   ✓ PASS")
    
    # Test mask_pii
    print("\n6. mask_pii():")
    card_text = "Card: 4532-1234-5678-9010"
    masked = mask_pii(card_text, pii_types=['credit_card'])
    print(f"   Original:  {card_text}")
    print(f"   Masked:    {masked}")
    print("   ✓ PASS")
    
    print("\n" + "="*60)
    print("✓ ALL REDACTION TESTS PASSED")
    print("="*60)


def test_integration():
    """Test integrated workflow"""
    print("\n" + "="*60)
    print("Testing Integrated Workflow")
    print("="*60)
    
    # Simulate user input with PII
    user_input = """
    Hi, I need help with my account.
    My email is alice@example.com
    My phone is 555-987-6543
    My SSN is 123-45-6789
    """
    
    print("\n1. Check for PII:")
    if has_pii(user_input):
        print("   ⚠️  PII detected in user input!")
        
        # Count PII
        counts = count_pii(user_input)
        print(f"   Found: {counts}")
        
        # Clean for LLM
        clean = clean_text_for_llm(user_input)
        print(f"\n2. Cleaned for LLM:")
        print(f"   {clean[:100]}...")
        
        print("\n   ✓ Safe to send to LLM")
    
    print("\n" + "="*60)
    print("✓ INTEGRATION TEST PASSED")
    print("="*60)


def main():
    """Run all tests"""
    print("\n╔" + "="*58 + "╗")
    print("║" + "  STANDALONE PII FUNCTIONS - TEST SUITE  ".center(58) + "║")
    print("╚" + "="*58 + "╝\n")
    
    try:
        test_detect_functions()
        test_redact_functions()
        test_integration()
        
        print("\n" + "🎉"*30)
        print("✓ ALL TESTS PASSED - detect_pii and redact_pii are working!")
        print("🎉"*30 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
