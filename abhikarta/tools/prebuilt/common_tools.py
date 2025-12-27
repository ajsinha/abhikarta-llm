"""
Pre-built Tools Library - Common utility tools ready for use.

This module provides a comprehensive set of commonly used tools
that can be registered with the ToolsRegistry and used in agents/workflows.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
import json
import re
import hashlib
import base64
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import math

from ..base_tool import (
    BaseTool, ToolMetadata, ToolSchema, ToolParameter,
    ToolResult, ToolType, ToolCategory
)
from ..function_tool import FunctionTool

logger = logging.getLogger(__name__)


# =============================================================================
# DATE/TIME TOOLS
# =============================================================================

def get_current_datetime(format: str = "%Y-%m-%d %H:%M:%S", timezone: str = "UTC") -> str:
    """Get current date and time in specified format."""
    from datetime import datetime
    now = datetime.utcnow()
    return now.strftime(format)

def parse_date(date_string: str, input_format: str = "%Y-%m-%d") -> Dict[str, Any]:
    """Parse a date string and return components."""
    try:
        dt = datetime.strptime(date_string, input_format)
        return {
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
            "weekday": dt.strftime("%A"),
            "iso_format": dt.isoformat(),
            "timestamp": dt.timestamp()
        }
    except ValueError as e:
        return {"error": str(e)}

def calculate_date_difference(date1: str, date2: str, format: str = "%Y-%m-%d") -> Dict[str, Any]:
    """Calculate difference between two dates."""
    try:
        dt1 = datetime.strptime(date1, format)
        dt2 = datetime.strptime(date2, format)
        diff = abs(dt2 - dt1)
        return {
            "days": diff.days,
            "weeks": diff.days // 7,
            "months": diff.days // 30,
            "years": diff.days // 365
        }
    except ValueError as e:
        return {"error": str(e)}

def add_days_to_date(date_string: str, days: int, format: str = "%Y-%m-%d") -> str:
    """Add or subtract days from a date."""
    try:
        dt = datetime.strptime(date_string, format)
        result = dt + timedelta(days=days)
        return result.strftime(format)
    except ValueError as e:
        return f"Error: {e}"

def get_business_days(start_date: str, end_date: str, format: str = "%Y-%m-%d") -> int:
    """Calculate business days between two dates (excluding weekends)."""
    try:
        dt1 = datetime.strptime(start_date, format)
        dt2 = datetime.strptime(end_date, format)
        business_days = 0
        current = dt1
        while current <= dt2:
            if current.weekday() < 5:  # Monday = 0, Friday = 4
                business_days += 1
            current += timedelta(days=1)
        return business_days
    except ValueError:
        return -1


# =============================================================================
# MATH/CALCULATOR TOOLS
# =============================================================================

def calculate_expression(expression: str) -> Dict[str, Any]:
    """Safely evaluate a mathematical expression."""
    allowed_names = {
        'abs': abs, 'round': round, 'min': min, 'max': max,
        'sum': sum, 'pow': pow, 'sqrt': math.sqrt,
        'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
        'log': math.log, 'log10': math.log10, 'exp': math.exp,
        'pi': math.pi, 'e': math.e
    }
    try:
        # Remove potentially dangerous characters
        if any(c in expression for c in ['import', 'exec', 'eval', '__']):
            return {"error": "Invalid expression"}
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return {"result": result, "expression": expression}
    except Exception as e:
        return {"error": str(e)}

def calculate_percentage(value: float, percentage: float) -> Dict[str, float]:
    """Calculate percentage of a value."""
    result = value * (percentage / 100)
    return {
        "original_value": value,
        "percentage": percentage,
        "result": result,
        "remaining": value - result
    }

def calculate_compound_interest(principal: float, rate: float, 
                                time_years: float, compounds_per_year: int = 12) -> Dict[str, float]:
    """Calculate compound interest."""
    amount = principal * (1 + rate / (100 * compounds_per_year)) ** (compounds_per_year * time_years)
    interest = amount - principal
    return {
        "principal": principal,
        "rate": rate,
        "time_years": time_years,
        "final_amount": round(amount, 2),
        "interest_earned": round(interest, 2)
    }

def calculate_loan_emi(principal: float, annual_rate: float, tenure_months: int) -> Dict[str, float]:
    """Calculate EMI for a loan."""
    monthly_rate = annual_rate / (12 * 100)
    if monthly_rate == 0:
        emi = principal / tenure_months
    else:
        emi = principal * monthly_rate * (1 + monthly_rate) ** tenure_months / \
              ((1 + monthly_rate) ** tenure_months - 1)
    total_payment = emi * tenure_months
    total_interest = total_payment - principal
    return {
        "principal": principal,
        "annual_rate": annual_rate,
        "tenure_months": tenure_months,
        "emi": round(emi, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2)
    }

def convert_currency(amount: float, from_currency: str, to_currency: str, 
                    exchange_rate: float) -> Dict[str, Any]:
    """Convert currency using provided exchange rate."""
    converted = amount * exchange_rate
    return {
        "original_amount": amount,
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "exchange_rate": exchange_rate,
        "converted_amount": round(converted, 2)
    }


# =============================================================================
# TEXT PROCESSING TOOLS
# =============================================================================

def extract_text_patterns(text: str, pattern: str) -> Dict[str, Any]:
    """Extract patterns from text using regex."""
    try:
        matches = re.findall(pattern, text)
        return {
            "pattern": pattern,
            "matches": matches,
            "count": len(matches)
        }
    except re.error as e:
        return {"error": str(e)}

def clean_text(text: str, remove_html: bool = True, remove_extra_spaces: bool = True,
              lowercase: bool = False) -> str:
    """Clean and normalize text."""
    result = text
    if remove_html:
        result = re.sub(r'<[^>]+>', '', result)
    if remove_extra_spaces:
        result = ' '.join(result.split())
    if lowercase:
        result = result.lower()
    return result

def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract common entities from text (emails, phones, URLs, etc.)."""
    entities = {
        "emails": re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
        "phones": re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text),
        "urls": re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text),
        "dates": re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text),
        "amounts": re.findall(r'\$[\d,]+\.?\d*', text),
        "percentages": re.findall(r'\d+\.?\d*%', text)
    }
    return entities

def generate_summary_stats(text: str) -> Dict[str, Any]:
    """Generate statistics about text."""
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    return {
        "character_count": len(text),
        "word_count": len(words),
        "sentence_count": len([s for s in sentences if s.strip()]),
        "average_word_length": round(sum(len(w) for w in words) / max(len(words), 1), 2),
        "unique_words": len(set(w.lower() for w in words))
    }

def mask_sensitive_data(text: str, mask_emails: bool = True, mask_phones: bool = True,
                       mask_ssn: bool = True, mask_cards: bool = True) -> str:
    """Mask sensitive data in text."""
    result = text
    if mask_emails:
        result = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                       '[EMAIL MASKED]', result)
    if mask_phones:
        result = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE MASKED]', result)
    if mask_ssn:
        result = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN MASKED]', result)
    if mask_cards:
        result = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 
                       '[CARD MASKED]', result)
    return result


# =============================================================================
# DATA VALIDATION TOOLS
# =============================================================================

def validate_email(email: str) -> Dict[str, Any]:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = bool(re.match(pattern, email))
    return {
        "email": email,
        "is_valid": is_valid,
        "domain": email.split('@')[1] if '@' in email else None
    }

def validate_phone(phone: str, country_code: str = "US") -> Dict[str, Any]:
    """Validate phone number format."""
    # Remove common separators
    cleaned = re.sub(r'[\s\-\.\(\)]', '', phone)
    patterns = {
        "US": r'^(\+1)?[2-9]\d{9}$',
        "UK": r'^(\+44)?[1-9]\d{9,10}$',
        "IN": r'^(\+91)?[6-9]\d{9}$'
    }
    pattern = patterns.get(country_code, patterns["US"])
    is_valid = bool(re.match(pattern, cleaned))
    return {
        "phone": phone,
        "cleaned": cleaned,
        "country_code": country_code,
        "is_valid": is_valid
    }

def validate_credit_card(card_number: str) -> Dict[str, Any]:
    """Validate credit card using Luhn algorithm."""
    # Remove spaces and dashes
    cleaned = re.sub(r'[\s\-]', '', card_number)
    
    if not cleaned.isdigit() or len(cleaned) < 13 or len(cleaned) > 19:
        return {"card_number": card_number, "is_valid": False, "card_type": None}
    
    # Luhn algorithm
    def luhn_check(num):
        digits = [int(d) for d in num]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(divmod(d * 2, 10))
        return checksum % 10 == 0
    
    # Determine card type
    card_type = None
    if cleaned.startswith('4'):
        card_type = 'Visa'
    elif cleaned.startswith(('51', '52', '53', '54', '55')):
        card_type = 'Mastercard'
    elif cleaned.startswith(('34', '37')):
        card_type = 'American Express'
    elif cleaned.startswith('6011'):
        card_type = 'Discover'
    
    return {
        "card_number": f"****{cleaned[-4:]}",
        "is_valid": luhn_check(cleaned),
        "card_type": card_type
    }

def validate_iban(iban: str) -> Dict[str, Any]:
    """Validate IBAN (International Bank Account Number)."""
    cleaned = iban.replace(' ', '').upper()
    
    if len(cleaned) < 15 or len(cleaned) > 34:
        return {"iban": iban, "is_valid": False, "country": None}
    
    country_code = cleaned[:2]
    
    # Move first 4 chars to end
    rearranged = cleaned[4:] + cleaned[:4]
    
    # Convert letters to numbers (A=10, B=11, etc.)
    numeric = ''
    for char in rearranged:
        if char.isdigit():
            numeric += char
        else:
            numeric += str(ord(char) - 55)
    
    is_valid = int(numeric) % 97 == 1
    
    return {
        "iban": cleaned,
        "is_valid": is_valid,
        "country": country_code,
        "check_digits": cleaned[2:4]
    }

def validate_ssn(ssn: str) -> Dict[str, Any]:
    """Validate US Social Security Number format."""
    cleaned = re.sub(r'[\s\-]', '', ssn)
    
    if not re.match(r'^\d{9}$', cleaned):
        return {"ssn": "***-**-" + ssn[-4:] if len(ssn) >= 4 else "invalid",
                "is_valid": False}
    
    # Check for invalid patterns
    area = int(cleaned[:3])
    group = int(cleaned[3:5])
    serial = int(cleaned[5:])
    
    is_valid = (
        area not in (0, 666) and
        area < 900 and
        group != 0 and
        serial != 0
    )
    
    return {
        "ssn": f"***-**-{cleaned[-4:]}",
        "is_valid": is_valid
    }


# =============================================================================
# FORMAT CONVERSION TOOLS
# =============================================================================

def json_to_csv(json_data: str, delimiter: str = ",") -> str:
    """Convert JSON array to CSV format."""
    try:
        data = json.loads(json_data) if isinstance(json_data, str) else json_data
        if not isinstance(data, list) or not data:
            return "Error: Input must be a non-empty JSON array"
        
        headers = list(data[0].keys())
        csv_lines = [delimiter.join(headers)]
        
        for row in data:
            values = [str(row.get(h, '')) for h in headers]
            csv_lines.append(delimiter.join(values))
        
        return '\n'.join(csv_lines)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON - {e}"

def csv_to_json(csv_data: str, delimiter: str = ",") -> str:
    """Convert CSV to JSON array."""
    try:
        lines = csv_data.strip().split('\n')
        if len(lines) < 2:
            return "Error: CSV must have header and at least one data row"
        
        headers = [h.strip() for h in lines[0].split(delimiter)]
        result = []
        
        for line in lines[1:]:
            values = [v.strip() for v in line.split(delimiter)]
            row = dict(zip(headers, values))
            result.append(row)
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {e}"

def xml_to_json(xml_data: str) -> str:
    """Convert simple XML to JSON (basic implementation)."""
    try:
        import xml.etree.ElementTree as ET
        
        def element_to_dict(element):
            result = {}
            for child in element:
                if len(child) == 0:
                    result[child.tag] = child.text
                else:
                    result[child.tag] = element_to_dict(child)
            return result
        
        root = ET.fromstring(xml_data)
        return json.dumps({root.tag: element_to_dict(root)}, indent=2)
    except Exception as e:
        return f"Error: {e}"

def base64_encode(text: str) -> str:
    """Encode text to base64."""
    return base64.b64encode(text.encode()).decode()

def base64_decode(encoded: str) -> str:
    """Decode base64 to text."""
    try:
        return base64.b64decode(encoded).decode()
    except Exception as e:
        return f"Error: {e}"

def generate_hash(text: str, algorithm: str = "sha256") -> Dict[str, str]:
    """Generate hash of text."""
    algorithms = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512
    }
    
    if algorithm not in algorithms:
        return {"error": f"Unknown algorithm. Use: {list(algorithms.keys())}"}
    
    hash_obj = algorithms[algorithm](text.encode())
    return {
        "algorithm": algorithm,
        "hash": hash_obj.hexdigest(),
        "input_length": len(text)
    }


# =============================================================================
# ID GENERATION TOOLS
# =============================================================================

def generate_uuid(version: int = 4) -> str:
    """Generate a UUID."""
    if version == 1:
        return str(uuid.uuid1())
    elif version == 4:
        return str(uuid.uuid4())
    else:
        return str(uuid.uuid4())

def generate_reference_number(prefix: str = "REF", length: int = 12) -> str:
    """Generate a reference number."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = uuid.uuid4().hex[:length - len(timestamp) - len(prefix) - 1]
    return f"{prefix}-{timestamp}{random_part}".upper()

def generate_account_number(bank_code: str = "BANK", length: int = 12) -> str:
    """Generate a bank account number format."""
    random_digits = ''.join([str(uuid.uuid4().int % 10) for _ in range(length)])
    return f"{bank_code}{random_digits}"


# =============================================================================
# REGISTER ALL TOOLS
# =============================================================================

def get_common_tools() -> List[FunctionTool]:
    """
    Get all pre-built common tools.
    
    Returns:
        List of FunctionTool instances
    """
    tools = []
    
    # Date/Time tools
    tools.append(FunctionTool.from_function(
        get_current_datetime, 
        name="get_current_datetime",
        description="Get current date and time in specified format",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        parse_date,
        name="parse_date",
        description="Parse a date string and return its components",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        calculate_date_difference,
        name="calculate_date_difference", 
        description="Calculate the difference between two dates",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        add_days_to_date,
        name="add_days_to_date",
        description="Add or subtract days from a date",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        get_business_days,
        name="get_business_days",
        description="Calculate business days between two dates",
        category=ToolCategory.UTILITY
    ))
    
    # Math tools
    tools.append(FunctionTool.from_function(
        calculate_expression,
        name="calculate_expression",
        description="Safely evaluate a mathematical expression",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        calculate_percentage,
        name="calculate_percentage",
        description="Calculate percentage of a value",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        calculate_compound_interest,
        name="calculate_compound_interest",
        description="Calculate compound interest",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        calculate_loan_emi,
        name="calculate_loan_emi",
        description="Calculate EMI (Equated Monthly Installment) for a loan",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        convert_currency,
        name="convert_currency",
        description="Convert currency using exchange rate",
        category=ToolCategory.UTILITY
    ))
    
    # Text processing tools
    tools.append(FunctionTool.from_function(
        extract_text_patterns,
        name="extract_text_patterns",
        description="Extract patterns from text using regex",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        clean_text,
        name="clean_text",
        description="Clean and normalize text",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        extract_entities,
        name="extract_entities",
        description="Extract entities like emails, phones, URLs from text",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        generate_summary_stats,
        name="generate_summary_stats",
        description="Generate statistics about text",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        mask_sensitive_data,
        name="mask_sensitive_data",
        description="Mask sensitive data in text",
        category=ToolCategory.UTILITY
    ))
    
    # Validation tools
    tools.append(FunctionTool.from_function(
        validate_email,
        name="validate_email",
        description="Validate email format",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        validate_phone,
        name="validate_phone",
        description="Validate phone number format",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        validate_credit_card,
        name="validate_credit_card",
        description="Validate credit card number using Luhn algorithm",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        validate_iban,
        name="validate_iban",
        description="Validate IBAN (International Bank Account Number)",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        validate_ssn,
        name="validate_ssn",
        description="Validate US Social Security Number format",
        category=ToolCategory.UTILITY
    ))
    
    # Format conversion tools
    tools.append(FunctionTool.from_function(
        json_to_csv,
        name="json_to_csv",
        description="Convert JSON array to CSV format",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        csv_to_json,
        name="csv_to_json",
        description="Convert CSV to JSON array",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        base64_encode,
        name="base64_encode",
        description="Encode text to base64",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        base64_decode,
        name="base64_decode",
        description="Decode base64 to text",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        generate_hash,
        name="generate_hash",
        description="Generate hash of text (MD5, SHA1, SHA256, SHA512)",
        category=ToolCategory.UTILITY
    ))
    
    # ID generation tools
    tools.append(FunctionTool.from_function(
        generate_uuid,
        name="generate_uuid",
        description="Generate a UUID",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        generate_reference_number,
        name="generate_reference_number",
        description="Generate a reference number",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        generate_account_number,
        name="generate_account_number",
        description="Generate a bank account number format",
        category=ToolCategory.UTILITY
    ))
    
    return tools


def register_common_tools(registry) -> int:
    """
    Register all common tools with the registry.
    
    Args:
        registry: ToolsRegistry instance
        
    Returns:
        Number of tools registered
    """
    tools = get_common_tools()
    count = 0
    for tool in tools:
        if registry.register(tool):
            count += 1
    logger.info(f"Registered {count} common tools")
    return count
