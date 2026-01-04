"""
Tool Documentation Module - Sample inputs, outputs, and detailed descriptions.

This module provides comprehensive documentation for all tools including:
- Detailed human-readable descriptions
- Sample input parameters (JSON)
- Sample output (JSON)
- Use cases and best practices
- Common pitfalls

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

from typing import Dict, Any, Optional
import json


class ToolDocumentation:
    """Container for tool documentation including examples."""
    
    def __init__(
        self,
        tool_name: str,
        detailed_description: str,
        sample_input: Dict[str, Any],
        sample_output: Any,
        use_cases: list = None,
        tips: list = None,
        related_tools: list = None
    ):
        self.tool_name = tool_name
        self.detailed_description = detailed_description
        self.sample_input = sample_input
        self.sample_output = sample_output
        self.use_cases = use_cases or []
        self.tips = tips or []
        self.related_tools = related_tools or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "detailed_description": self.detailed_description,
            "sample_input": self.sample_input,
            "sample_output": self.sample_output,
            "use_cases": self.use_cases,
            "tips": self.tips,
            "related_tools": self.related_tools
        }


# =============================================================================
# TOOL DOCUMENTATION REGISTRY
# =============================================================================

TOOL_DOCS: Dict[str, ToolDocumentation] = {}


def register_tool_doc(doc: ToolDocumentation):
    """Register documentation for a tool."""
    TOOL_DOCS[doc.tool_name] = doc


def get_tool_doc(tool_name: str) -> Optional[ToolDocumentation]:
    """Get documentation for a tool by name."""
    return TOOL_DOCS.get(tool_name)


def get_all_tool_docs() -> Dict[str, ToolDocumentation]:
    """Get all registered tool documentation."""
    return TOOL_DOCS.copy()


# =============================================================================
# DATE/TIME TOOLS DOCUMENTATION
# =============================================================================

register_tool_doc(ToolDocumentation(
    tool_name="get_current_datetime",
    detailed_description="""
Returns the current date and time formatted according to the specified format string.
This tool uses UTC time by default and supports Python's strftime format codes.

Common format codes:
- %Y: 4-digit year (e.g., 2025)
- %m: 2-digit month (01-12)
- %d: 2-digit day (01-31)
- %H: 24-hour hour (00-23)
- %M: Minutes (00-59)
- %S: Seconds (00-59)
- %A: Full weekday name (e.g., Monday)
- %B: Full month name (e.g., January)
""".strip(),
    sample_input={
        "format": "%Y-%m-%d %H:%M:%S",
        "timezone": "UTC"
    },
    sample_output="2025-01-15 14:30:45",
    use_cases=[
        "Adding timestamps to logs or reports",
        "Generating date-based file names",
        "Recording when actions were taken",
        "Creating audit trails"
    ],
    tips=[
        "Use ISO 8601 format (%Y-%m-%dT%H:%M:%SZ) for API compatibility",
        "For human-readable output, use formats like '%B %d, %Y'",
        "Always specify timezone for distributed systems"
    ],
    related_tools=["parse_date", "calculate_date_difference", "add_days_to_date"]
))


register_tool_doc(ToolDocumentation(
    tool_name="parse_date",
    detailed_description="""
Parses a date string according to the specified format and returns a structured
breakdown of the date components. This is useful for extracting individual parts
of a date (year, month, day, weekday) or converting between formats.

The tool returns:
- Individual components (year, month, day)
- Day of week name
- ISO 8601 formatted string
- Unix timestamp
""".strip(),
    sample_input={
        "date_string": "2025-03-15",
        "input_format": "%Y-%m-%d"
    },
    sample_output={
        "year": 2025,
        "month": 3,
        "day": 15,
        "weekday": "Saturday",
        "iso_format": "2025-03-15T00:00:00",
        "timestamp": 1742169600.0
    },
    use_cases=[
        "Extracting year/month for filtering data",
        "Converting date formats between systems",
        "Determining day of week for scheduling",
        "Calculating Unix timestamps for APIs"
    ],
    tips=[
        "Ensure input_format exactly matches your date string",
        "Use this before calculate_date_difference for validation",
        "The timestamp is useful for database storage"
    ],
    related_tools=["get_current_datetime", "calculate_date_difference", "add_days_to_date"]
))


register_tool_doc(ToolDocumentation(
    tool_name="calculate_date_difference",
    detailed_description="""
Calculates the absolute difference between two dates. Returns the difference
expressed in multiple units: days, weeks, months (approximated as 30 days),
and years (approximated as 365 days).

The calculation always returns absolute values (positive), regardless of
which date comes first.
""".strip(),
    sample_input={
        "date1": "2025-01-01",
        "date2": "2025-12-31",
        "format": "%Y-%m-%d"
    },
    sample_output={
        "days": 364,
        "weeks": 52,
        "months": 12,
        "years": 0
    },
    use_cases=[
        "Calculating age or tenure",
        "Determining subscription duration",
        "SLA compliance checking",
        "Project timeline analysis"
    ],
    tips=[
        "For precise business days, use get_business_days instead",
        "Months and years are approximations - use days for precision",
        "Order of dates doesn't matter (result is always positive)"
    ],
    related_tools=["parse_date", "add_days_to_date", "get_business_days"]
))


register_tool_doc(ToolDocumentation(
    tool_name="add_days_to_date",
    detailed_description="""
Adds (or subtracts) a specified number of days to a date. Use positive numbers
to add days into the future, or negative numbers to go back in time.

This is useful for calculating due dates, expiration dates, or finding dates
a certain number of days before/after a reference date.
""".strip(),
    sample_input={
        "date_string": "2025-01-15",
        "days": 30,
        "format": "%Y-%m-%d"
    },
    sample_output="2025-02-14",
    use_cases=[
        "Calculating due dates",
        "Setting expiration dates",
        "Finding dates N days in the future/past",
        "Scheduling follow-ups"
    ],
    tips=[
        "Use negative numbers to subtract days",
        "For business days only, combine with get_business_days",
        "Consider holidays if business context requires it"
    ],
    related_tools=["parse_date", "calculate_date_difference", "get_business_days"]
))


register_tool_doc(ToolDocumentation(
    tool_name="get_business_days",
    detailed_description="""
Calculates the number of business days (weekdays: Monday-Friday) between
two dates, inclusive of both start and end dates. This excludes weekends
but does NOT account for public holidays.

Use this for business-oriented date calculations like delivery estimates,
SLA tracking, or project planning.
""".strip(),
    sample_input={
        "start_date": "2025-01-06",
        "end_date": "2025-01-17",
        "format": "%Y-%m-%d"
    },
    sample_output=10,
    use_cases=[
        "Calculating delivery timeframes",
        "SLA compliance monitoring",
        "Project timeline estimation",
        "Payment term calculations"
    ],
    tips=[
        "Does not account for public holidays",
        "Both start and end dates are counted if they're weekdays",
        "For holiday-aware calculations, combine with a holiday list"
    ],
    related_tools=["calculate_date_difference", "add_days_to_date"]
))


# =============================================================================
# MATH/CALCULATOR TOOLS DOCUMENTATION
# =============================================================================

register_tool_doc(ToolDocumentation(
    tool_name="calculate_expression",
    detailed_description="""
Safely evaluates mathematical expressions provided as strings. Supports basic
arithmetic operations (+, -, *, /, **, %), parentheses for grouping, and
common mathematical functions.

Available functions: abs, round, min, max, sum, pow, sqrt, sin, cos, tan,
log, log10, exp, plus constants pi and e.

Security: The tool blocks potentially dangerous operations like imports
or code execution attempts.
""".strip(),
    sample_input={
        "expression": "sqrt(16) + pow(2, 3) * pi"
    },
    sample_output={
        "result": 29.132741228718345,
        "expression": "sqrt(16) + pow(2, 3) * pi"
    },
    use_cases=[
        "Performing calculations in workflows",
        "Processing user-provided formulas",
        "Financial calculations",
        "Scientific computations"
    ],
    tips=[
        "Use parentheses to ensure correct order of operations",
        "For division, be aware of integer vs float results",
        "Dangerous keywords (import, exec, eval) are blocked"
    ],
    related_tools=["calculate_percentage", "calculate_compound_interest", "calculate_loan_emi"]
))


register_tool_doc(ToolDocumentation(
    tool_name="calculate_percentage",
    detailed_description="""
Calculates a percentage of a given value. Returns both the calculated
percentage amount and the remaining value after that percentage is taken.

This is useful for discount calculations, tax computations, tip calculations,
or any scenario where you need to find what portion of a value corresponds
to a given percentage.
""".strip(),
    sample_input={
        "value": 150.00,
        "percentage": 20
    },
    sample_output={
        "original_value": 150.0,
        "percentage": 20,
        "result": 30.0,
        "remaining": 120.0
    },
    use_cases=[
        "Calculating discounts",
        "Computing tax amounts",
        "Tip calculations",
        "Commission calculations"
    ],
    tips=[
        "The 'remaining' field gives you value minus the percentage",
        "For adding percentage (like tax), add result to original_value",
        "Chain multiple calls for compound percentages"
    ],
    related_tools=["calculate_expression", "calculate_compound_interest"]
))


register_tool_doc(ToolDocumentation(
    tool_name="calculate_compound_interest",
    detailed_description="""
Calculates compound interest on a principal amount. Compound interest means
interest is calculated on both the initial principal and the accumulated
interest from previous periods.

Parameters:
- principal: Initial investment amount
- rate: Annual interest rate as a percentage (e.g., 5 for 5%)
- time_years: Investment duration in years
- compounds_per_year: How often interest compounds (12=monthly, 4=quarterly, 1=annually)

Formula: A = P(1 + r/n)^(nt)
""".strip(),
    sample_input={
        "principal": 10000,
        "rate": 7.5,
        "time_years": 5,
        "compounds_per_year": 12
    },
    sample_output={
        "principal": 10000,
        "rate": 7.5,
        "time_years": 5,
        "final_amount": 14536.99,
        "interest_earned": 4536.99
    },
    use_cases=[
        "Investment projections",
        "Savings growth calculations",
        "Loan cost analysis",
        "Retirement planning"
    ],
    tips=[
        "Monthly compounding (12) is most common for savings",
        "Higher compounds_per_year means more interest earned",
        "Rate is entered as percentage (7.5 for 7.5%), not decimal"
    ],
    related_tools=["calculate_loan_emi", "calculate_percentage"]
))


register_tool_doc(ToolDocumentation(
    tool_name="calculate_loan_emi",
    detailed_description="""
Calculates the Equated Monthly Installment (EMI) for a loan. EMI is the
fixed monthly payment that includes both principal and interest, designed
to pay off the loan completely over the tenure.

Also returns total payment over the loan term and total interest paid.

Formula: EMI = P × r × (1+r)^n / ((1+r)^n - 1)
where P=principal, r=monthly rate, n=number of months
""".strip(),
    sample_input={
        "principal": 500000,
        "annual_rate": 8.5,
        "tenure_months": 60
    },
    sample_output={
        "principal": 500000,
        "annual_rate": 8.5,
        "tenure_months": 60,
        "emi": 10242.02,
        "total_payment": 614521.2,
        "total_interest": 114521.2
    },
    use_cases=[
        "Loan affordability analysis",
        "Mortgage planning",
        "Auto loan calculations",
        "Personal loan comparison"
    ],
    tips=[
        "Use total_interest to compare different loan options",
        "Shorter tenure = higher EMI but less total interest",
        "annual_rate is the APR as percentage (8.5 for 8.5%)"
    ],
    related_tools=["calculate_compound_interest", "calculate_percentage"]
))


register_tool_doc(ToolDocumentation(
    tool_name="convert_currency",
    detailed_description="""
Converts an amount from one currency to another using a provided exchange rate.
Note: This tool requires you to provide the exchange rate - it does not fetch
live rates. For live rates, use an API integration tool.

The exchange rate should be: 1 unit of from_currency = X units of to_currency
""".strip(),
    sample_input={
        "amount": 1000,
        "from_currency": "USD",
        "to_currency": "EUR",
        "exchange_rate": 0.92
    },
    sample_output={
        "original_amount": 1000,
        "from_currency": "USD",
        "to_currency": "EUR",
        "exchange_rate": 0.92,
        "converted_amount": 920.0
    },
    use_cases=[
        "Converting prices for international customers",
        "Financial report conversions",
        "Travel expense calculations",
        "Multi-currency accounting"
    ],
    tips=[
        "Exchange rates must be provided - not fetched automatically",
        "For live rates, combine with an API call tool",
        "Currency codes are automatically uppercased"
    ],
    related_tools=["calculate_expression", "calculate_percentage"]
))


# =============================================================================
# TEXT PROCESSING TOOLS DOCUMENTATION
# =============================================================================

register_tool_doc(ToolDocumentation(
    tool_name="extract_text_patterns",
    detailed_description="""
Extracts all occurrences of a regex pattern from text. Returns all matches
found along with a count. Useful for finding specific data patterns like
dates, codes, identifiers, or any structured text.

Supports full Python regex syntax including:
- Character classes: [a-z], \\d, \\w, \\s
- Quantifiers: *, +, ?, {n,m}
- Groups: (pattern), (?:pattern)
- Anchors: ^, $, \\b
""".strip(),
    sample_input={
        "text": "Contact us at support@example.com or sales@example.com for help.",
        "pattern": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    },
    sample_output={
        "pattern": "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}",
        "matches": ["support@example.com", "sales@example.com"],
        "count": 2
    },
    use_cases=[
        "Extracting email addresses from text",
        "Finding phone numbers in documents",
        "Parsing structured codes or IDs",
        "Data extraction from unstructured text"
    ],
    tips=[
        "Use extract_entities for common patterns without writing regex",
        "Test regex patterns before using in production",
        "Use raw strings (r'...') for patterns with backslashes"
    ],
    related_tools=["extract_entities", "clean_text", "mask_sensitive_data"]
))


register_tool_doc(ToolDocumentation(
    tool_name="clean_text",
    detailed_description="""
Cleans and normalizes text by optionally:
- Removing HTML tags
- Collapsing multiple whitespace to single spaces
- Converting to lowercase

This is useful for preprocessing text before analysis, search indexing,
or comparison operations.
""".strip(),
    sample_input={
        "text": "<p>Hello   World!</p>  <br> How are  you?",
        "remove_html": True,
        "remove_extra_spaces": True,
        "lowercase": False
    },
    sample_output="Hello World! How are you?",
    use_cases=[
        "Preprocessing text for NLP",
        "Cleaning scraped web content",
        "Normalizing user input",
        "Preparing text for comparison"
    ],
    tips=[
        "Apply before text comparison to avoid whitespace mismatches",
        "Use lowercase=True for case-insensitive matching",
        "HTML removal is basic - for complex HTML use a proper parser"
    ],
    related_tools=["extract_text_patterns", "extract_entities", "generate_summary_stats"]
))


register_tool_doc(ToolDocumentation(
    tool_name="extract_entities",
    detailed_description="""
Automatically extracts common entity types from text without requiring regex
knowledge. Identifies:
- Email addresses
- Phone numbers (US format)
- URLs
- Dates (common formats)
- Currency amounts ($)
- Percentages

This is a convenience tool that combines multiple pattern extractions.
""".strip(),
    sample_input={
        "text": "Contact john@example.com or call 555-123-4567. Visit https://example.com for 20% off! Offer ends 12/31/2025. Total: $99.99"
    },
    sample_output={
        "emails": ["john@example.com"],
        "phones": ["555-123-4567"],
        "urls": ["https://example.com"],
        "dates": ["12/31/2025"],
        "amounts": ["$99.99"],
        "percentages": ["20%"]
    },
    use_cases=[
        "Contact information extraction",
        "Document metadata extraction",
        "Lead generation from text",
        "Data entry automation"
    ],
    tips=[
        "For custom patterns, use extract_text_patterns",
        "Phone patterns are US-centric - customize for other regions",
        "Combine with mask_sensitive_data for privacy compliance"
    ],
    related_tools=["extract_text_patterns", "mask_sensitive_data", "clean_text"]
))


register_tool_doc(ToolDocumentation(
    tool_name="generate_summary_stats",
    detailed_description="""
Generates statistical metrics about a piece of text including:
- Character count (total length)
- Word count
- Sentence count
- Average word length
- Count of unique words

Useful for content analysis, readability assessment, or quality checks.
""".strip(),
    sample_input={
        "text": "The quick brown fox jumps over the lazy dog. The dog was not amused."
    },
    sample_output={
        "character_count": 68,
        "word_count": 14,
        "sentence_count": 2,
        "average_word_length": 3.79,
        "unique_words": 12
    },
    use_cases=[
        "Content length validation",
        "Readability analysis",
        "Plagiarism detection preprocessing",
        "Writing quality assessment"
    ],
    tips=[
        "Average word length indicates complexity (higher = more complex)",
        "Unique words / total words = vocabulary diversity",
        "Sentence detection is basic (splits on .!?)"
    ],
    related_tools=["clean_text", "extract_text_patterns"]
))


register_tool_doc(ToolDocumentation(
    tool_name="mask_sensitive_data",
    detailed_description="""
Replaces sensitive data patterns in text with masked placeholders.
Supports masking:
- Email addresses → [EMAIL MASKED]
- Phone numbers → [PHONE MASKED]
- Social Security Numbers → [SSN MASKED]
- Credit card numbers → [CARD MASKED]

Essential for data privacy compliance (GDPR, PII protection).
""".strip(),
    sample_input={
        "text": "Customer email: john@example.com, phone: 555-123-4567, SSN: 123-45-6789",
        "mask_emails": True,
        "mask_phones": True,
        "mask_ssn": True,
        "mask_cards": True
    },
    sample_output="Customer email: [EMAIL MASKED], phone: [PHONE MASKED], SSN: [SSN MASKED]",
    use_cases=[
        "Log sanitization",
        "GDPR compliance",
        "Preparing data for ML training",
        "Secure data sharing"
    ],
    tips=[
        "Always mask before logging sensitive data",
        "Enable only the masking types you need",
        "For redaction instead of masking, modify the replacement text"
    ],
    related_tools=["extract_entities", "clean_text"]
))


# =============================================================================
# VALIDATION TOOLS DOCUMENTATION
# =============================================================================

register_tool_doc(ToolDocumentation(
    tool_name="validate_email",
    detailed_description="""
Validates whether a string is a properly formatted email address.
Checks for:
- Presence of @ symbol
- Valid local part (before @)
- Valid domain part (after @)
- Valid TLD (top-level domain)

Note: This validates format only - it does not verify the email exists.
""".strip(),
    sample_input={
        "email": "user.name@example.com"
    },
    sample_output={
        "valid": True,
        "email": "user.name@example.com"
    },
    use_cases=[
        "Form input validation",
        "Data quality checks",
        "User registration validation",
        "Contact list cleaning"
    ],
    tips=[
        "Format validation ≠ deliverability verification",
        "Some valid emails may fail (very long TLDs, etc.)",
        "Consider also checking MX records for critical cases"
    ],
    related_tools=["validate_phone", "extract_entities"]
))


register_tool_doc(ToolDocumentation(
    tool_name="validate_phone",
    detailed_description="""
Validates US phone number formats. Accepts various common formats:
- 555-123-4567
- 555.123.4567
- 5551234567
- (555) 123-4567

Returns the validated phone number and whether it's valid.
""".strip(),
    sample_input={
        "phone": "555-123-4567"
    },
    sample_output={
        "valid": True,
        "phone": "555-123-4567"
    },
    use_cases=[
        "Contact form validation",
        "CRM data cleaning",
        "User profile validation",
        "Data import validation"
    ],
    tips=[
        "US formats only - customize for international numbers",
        "Does not validate if number is actually in service",
        "Consider normalizing to a standard format after validation"
    ],
    related_tools=["validate_email", "extract_entities"]
))


register_tool_doc(ToolDocumentation(
    tool_name="validate_credit_card",
    detailed_description="""
Validates credit card numbers using the Luhn algorithm (modulus 10).
This is a checksum validation that catches typos and obvious errors.

Also attempts to identify the card type based on the number prefix:
- Visa: Starts with 4
- MasterCard: Starts with 51-55 or 2221-2720
- Amex: Starts with 34 or 37
- Discover: Starts with 6011, 644-649, or 65

Note: Passes validation ≠ card can be charged
""".strip(),
    sample_input={
        "card_number": "4532015112830366"
    },
    sample_output={
        "valid": True,
        "card_number": "4532015112830366",
        "card_type": "visa"
    },
    use_cases=[
        "Payment form validation",
        "Checkout flow pre-validation",
        "Data entry error detection",
        "Fraud prevention (first step)"
    ],
    tips=[
        "This is format validation only - not authorization",
        "Always use with your payment processor's validation",
        "Remove spaces/dashes before validation"
    ],
    related_tools=["validate_iban", "mask_sensitive_data"]
))


register_tool_doc(ToolDocumentation(
    tool_name="validate_iban",
    detailed_description="""
Validates International Bank Account Numbers (IBAN). IBANs are used for
international money transfers and contain:
- Country code (2 letters)
- Check digits (2 numbers)
- Basic Bank Account Number (BBAN)

Validation includes:
- Length check per country
- Check digit verification (ISO 7064 Mod 97-10)
""".strip(),
    sample_input={
        "iban": "DE89370400440532013000"
    },
    sample_output={
        "valid": True,
        "iban": "DE89370400440532013000",
        "country": "DE"
    },
    use_cases=[
        "International payment validation",
        "Bank transfer forms",
        "Financial data import",
        "Wire transfer setup"
    ],
    tips=[
        "IBANs should have spaces removed before validation",
        "Country determines expected length",
        "Valid format ≠ active account"
    ],
    related_tools=["validate_credit_card", "generate_account_number"]
))


register_tool_doc(ToolDocumentation(
    tool_name="validate_ssn",
    detailed_description="""
Validates US Social Security Number format. Valid formats:
- 123-45-6789 (with dashes)
- 123456789 (without dashes)

Checks for:
- Correct number of digits (9)
- Valid area number (first 3 digits)
- Not using known invalid patterns (000, 666, 900-999 area)

Note: Does not verify SSN is actually assigned.
""".strip(),
    sample_input={
        "ssn": "123-45-6789"
    },
    sample_output={
        "valid": True,
        "ssn": "123-45-6789"
    },
    use_cases=[
        "Employment form validation",
        "Financial application processing",
        "Identity verification forms",
        "Tax document processing"
    ],
    tips=[
        "Handle SSN data with extreme care (PII)",
        "Always mask when logging or displaying",
        "Format validation only - not SSA verification"
    ],
    related_tools=["mask_sensitive_data", "validate_email"]
))


# =============================================================================
# DATA TRANSFORMATION TOOLS DOCUMENTATION  
# =============================================================================

register_tool_doc(ToolDocumentation(
    tool_name="json_to_csv",
    detailed_description="""
Converts a JSON array of objects to CSV (Comma-Separated Values) format.
Each object in the array becomes a row, and object keys become column headers.

The first object's keys determine the columns. If subsequent objects have
different keys, those columns may be empty.
""".strip(),
    sample_input={
        "data": [
            {"name": "Alice", "age": 30, "city": "NYC"},
            {"name": "Bob", "age": 25, "city": "LA"}
        ]
    },
    sample_output="name,age,city\nAlice,30,NYC\nBob,25,LA",
    use_cases=[
        "Exporting data to spreadsheets",
        "Data interchange between systems",
        "Report generation",
        "Database exports"
    ],
    tips=[
        "Ensure consistent keys across all objects",
        "Nested objects will be stringified",
        "Use for flat data structures"
    ],
    related_tools=["csv_to_json", "flatten_json"]
))


register_tool_doc(ToolDocumentation(
    tool_name="csv_to_json",
    detailed_description="""
Converts CSV text to a JSON array of objects. Each row becomes an object
with column headers as keys.

Handles:
- Comma-separated values
- Header row for keys
- Quoted strings
""".strip(),
    sample_input={
        "csv_data": "name,age,city\nAlice,30,NYC\nBob,25,LA"
    },
    sample_output=[
        {"name": "Alice", "age": "30", "city": "NYC"},
        {"name": "Bob", "age": "25", "city": "LA"}
    ],
    use_cases=[
        "Importing spreadsheet data",
        "Processing CSV uploads",
        "Data migration",
        "API input preparation"
    ],
    tips=[
        "All values are returned as strings - cast as needed",
        "First row must be headers",
        "Handle encoding issues before processing"
    ],
    related_tools=["json_to_csv", "unflatten_json"]
))


register_tool_doc(ToolDocumentation(
    tool_name="base64_encode",
    detailed_description="""
Encodes text to Base64 format. Base64 is used to represent binary data
as ASCII text, commonly used for:
- Embedding data in JSON/XML
- URL parameters
- Email attachments
- Basic authentication headers

The encoding is reversible with base64_decode.
""".strip(),
    sample_input={
        "text": "Hello, World!"
    },
    sample_output="SGVsbG8sIFdvcmxkIQ==",
    use_cases=[
        "Encoding data for API transmission",
        "Creating authentication headers",
        "Embedding binary data in text formats",
        "URL-safe data encoding"
    ],
    tips=[
        "Base64 increases size by ~33%",
        "Not encryption - easily decoded",
        "For binary files, encode bytes not text"
    ],
    related_tools=["base64_decode", "generate_hash"]
))


register_tool_doc(ToolDocumentation(
    tool_name="base64_decode",
    detailed_description="""
Decodes Base64-encoded text back to its original form.
Reverses the encoding done by base64_encode.

Returns an error if the input is not valid Base64.
""".strip(),
    sample_input={
        "encoded": "SGVsbG8sIFdvcmxkIQ=="
    },
    sample_output="Hello, World!",
    use_cases=[
        "Decoding API responses",
        "Processing authentication headers",
        "Reading encoded configurations",
        "Extracting embedded data"
    ],
    tips=[
        "Invalid Base64 returns an error",
        "Handles standard Base64 encoding",
        "For binary data, result may need further processing"
    ],
    related_tools=["base64_encode", "generate_hash"]
))


register_tool_doc(ToolDocumentation(
    tool_name="generate_hash",
    detailed_description="""
Generates a cryptographic hash of text. Supports multiple algorithms:
- MD5: 128-bit (fast but less secure)
- SHA1: 160-bit (deprecated for security)
- SHA256: 256-bit (recommended for most uses)
- SHA512: 512-bit (maximum security)

Hashes are one-way - original text cannot be recovered from the hash.
""".strip(),
    sample_input={
        "text": "Hello, World!",
        "algorithm": "sha256"
    },
    sample_output={
        "algorithm": "sha256",
        "hash": "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
    },
    use_cases=[
        "Password storage (with salt)",
        "Data integrity verification",
        "File deduplication",
        "Digital signatures"
    ],
    tips=[
        "Use SHA256 or SHA512 for security-sensitive applications",
        "MD5/SHA1 are suitable for non-security uses (checksums)",
        "For passwords, use bcrypt/argon2 instead"
    ],
    related_tools=["base64_encode", "generate_uuid"]
))


# =============================================================================
# ID GENERATION TOOLS DOCUMENTATION
# =============================================================================

register_tool_doc(ToolDocumentation(
    tool_name="generate_uuid",
    detailed_description="""
Generates a Universally Unique Identifier (UUID). Supports different versions:
- UUID4: Random-based (default, most common)
- UUID1: Time-based with MAC address

UUIDs are 128-bit identifiers formatted as 32 hexadecimal digits in 5 groups:
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
""".strip(),
    sample_input={
        "version": 4
    },
    sample_output="550e8400-e29b-41d4-a716-446655440000",
    use_cases=[
        "Database primary keys",
        "Transaction identifiers",
        "Session tokens",
        "File naming"
    ],
    tips=[
        "UUID4 (random) is best for most uses",
        "UUID1 includes timestamp and MAC (less random)",
        "Virtually zero chance of collision"
    ],
    related_tools=["generate_reference_number", "generate_account_number"]
))


register_tool_doc(ToolDocumentation(
    tool_name="generate_reference_number",
    detailed_description="""
Generates a formatted reference number with a prefix, timestamp, and
random component. Format: PREFIX-YYYYMMDDHHMMSSxxx

Useful for:
- Order numbers
- Invoice references
- Support ticket IDs
- Transaction references

The timestamp component makes numbers roughly sortable by creation time.
""".strip(),
    sample_input={
        "prefix": "ORD",
        "length": 12
    },
    sample_output="ORD-20250115143045A7",
    use_cases=[
        "Order management systems",
        "Invoice generation",
        "Support ticket systems",
        "Shipment tracking"
    ],
    tips=[
        "Prefix helps identify reference type at a glance",
        "Length includes all characters",
        "Timestamp makes references chronologically sortable"
    ],
    related_tools=["generate_uuid", "generate_account_number"]
))


register_tool_doc(ToolDocumentation(
    tool_name="generate_account_number",
    detailed_description="""
Generates a formatted account number with a bank code prefix followed
by random digits. Format: BANKCODEnnnnnnnnnnnn

This is for demo/testing purposes. Real account numbers follow specific
formats per institution and should be generated by banking systems.
""".strip(),
    sample_input={
        "bank_code": "HDFC",
        "length": 12
    },
    sample_output="HDFC123456789012",
    use_cases=[
        "Test data generation",
        "Demo environments",
        "Sample data for development",
        "Mock banking scenarios"
    ],
    tips=[
        "FOR TEST/DEMO ONLY - not real account numbers",
        "Real account numbers need proper banking validation",
        "Combine with validate_iban for realistic testing"
    ],
    related_tools=["generate_reference_number", "validate_iban"]
))


# =============================================================================
# DATA PROCESSING TOOLS DOCUMENTATION
# =============================================================================

register_tool_doc(ToolDocumentation(
    tool_name="flatten_json",
    detailed_description="""
Flattens a nested JSON structure into a single-level dictionary using
dot notation for keys. Useful for:
- Converting nested data for flat storage (databases)
- Easier iteration over all values
- Comparison of complex structures
- Search indexing

Example: {"a": {"b": 1}} becomes {"a.b": 1}
Arrays are flattened with numeric indices: {"items": [1,2]} becomes {"items.0": 1, "items.1": 2}
""".strip(),
    sample_input={
        "data": {
            "user": {
                "name": "Alice",
                "address": {
                    "city": "NYC",
                    "zip": "10001"
                }
            },
            "items": ["book", "pen"]
        },
        "separator": "."
    },
    sample_output={
        "user.name": "Alice",
        "user.address.city": "NYC",
        "user.address.zip": "10001",
        "items.0": "book",
        "items.1": "pen"
    },
    use_cases=[
        "Database storage of JSON",
        "Search indexing",
        "Configuration management",
        "Data comparison"
    ],
    tips=[
        "Use unflatten_json to reverse the operation",
        "Custom separator can avoid conflicts with keys containing dots",
        "Deep nesting creates very long key names"
    ],
    related_tools=["unflatten_json", "merge_json"]
))


register_tool_doc(ToolDocumentation(
    tool_name="unflatten_json",
    detailed_description="""
Reverses flatten_json by converting dot-notation keys back into a nested
structure. Keys with numeric parts become array indices.

Example: {"a.b": 1} becomes {"a": {"b": 1}}
Numeric keys: {"items.0": "a", "items.1": "b"} becomes {"items": ["a", "b"]}
""".strip(),
    sample_input={
        "data": {
            "user.name": "Alice",
            "user.address.city": "NYC",
            "user.address.zip": "10001"
        },
        "separator": "."
    },
    sample_output={
        "user": {
            "name": "Alice",
            "address": {
                "city": "NYC",
                "zip": "10001"
            }
        }
    },
    use_cases=[
        "Reconstructing nested structures from flat storage",
        "Form data to JSON conversion",
        "API request building",
        "Configuration reconstruction"
    ],
    tips=[
        "Numeric keys in path become array indices",
        "Use same separator as was used in flatten_json",
        "Mixed objects and arrays can be tricky"
    ],
    related_tools=["flatten_json", "merge_json"]
))


register_tool_doc(ToolDocumentation(
    tool_name="merge_json",
    detailed_description="""
Merges two JSON objects with the second object taking priority for
conflicting keys. Supports deep merge where nested objects are merged
recursively rather than being completely replaced.

Shallow merge: {"a": {"x": 1}} + {"a": {"y": 2}} = {"a": {"y": 2}}
Deep merge: {"a": {"x": 1}} + {"a": {"y": 2}} = {"a": {"x": 1, "y": 2}}
""".strip(),
    sample_input={
        "base": {
            "name": "Widget",
            "config": {
                "color": "red",
                "size": "large"
            }
        },
        "override": {
            "config": {
                "color": "blue"
            },
            "price": 99.99
        },
        "deep": True
    },
    sample_output={
        "name": "Widget",
        "config": {
            "color": "blue",
            "size": "large"
        },
        "price": 99.99
    },
    use_cases=[
        "Configuration layering (defaults + overrides)",
        "Patching API objects",
        "Template customization",
        "State management"
    ],
    tips=[
        "Use deep=True to preserve nested structure",
        "Arrays are replaced, not merged",
        "Override values completely replace base values"
    ],
    related_tools=["flatten_json", "unflatten_json"]
))


register_tool_doc(ToolDocumentation(
    tool_name="aggregate_list",
    detailed_description="""
Performs aggregation operations on a list of objects by extracting values from a
specified field and applying an operation.

Supported operations:
- **sum**: Total of all values in the field
- **avg**: Average (mean) of values
- **min**: Smallest value
- **max**: Largest value  
- **count**: Number of items with the field

This is useful for quick calculations on lists of data objects, similar to
SQL aggregate functions but operating on in-memory data.
""".strip(),
    sample_input={
        "items": [
            {"name": "Alice", "sales": 1500},
            {"name": "Bob", "sales": 2200},
            {"name": "Charlie", "sales": 1800},
            {"name": "Diana", "sales": 2500}
        ],
        "field": "sales",
        "operation": "sum"
    },
    sample_output={
        "result": 8000,
        "count": 4,
        "operation": "sum",
        "field": "sales"
    },
    use_cases=[
        "Calculating total sales from order list",
        "Finding average scores in survey data",
        "Getting min/max prices from product catalog",
        "Counting records with specific field"
    ],
    tips=[
        "Items missing the field are skipped in calculation",
        "Use 'avg' for averages, not 'average' or 'mean'",
        "Float results are rounded to 2 decimal places",
        "For grouped aggregation, use group_and_aggregate"
    ],
    related_tools=["group_and_aggregate", "filter_list", "sort_list"]
))


register_tool_doc(ToolDocumentation(
    tool_name="group_and_aggregate",
    detailed_description="""
Groups data by a specified key and performs aggregation on a numeric field.
Similar to SQL's GROUP BY with aggregate functions.

For each unique value of the group_by field:
- Count: Number of records
- Sum: Total of the aggregate field
- Average: Mean of the aggregate field
- Min/Max: Extremes of the aggregate field
""".strip(),
    sample_input={
        "data": [
            {"category": "A", "value": 100},
            {"category": "A", "value": 150},
            {"category": "B", "value": 200},
            {"category": "B", "value": 250},
            {"category": "B", "value": 300}
        ],
        "group_by": "category",
        "aggregate_field": "value"
    },
    sample_output={
        "A": {"count": 2, "sum": 250, "average": 125.0, "min": 100, "max": 150},
        "B": {"count": 3, "sum": 750, "average": 250.0, "min": 200, "max": 300}
    },
    use_cases=[
        "Sales by category",
        "Performance by team",
        "Expenses by department",
        "Orders by status"
    ],
    tips=[
        "Group key must exist in all records",
        "Missing aggregate fields are skipped",
        "For multiple aggregations, call multiple times"
    ],
    related_tools=["aggregate_list", "filter_list"]
))


register_tool_doc(ToolDocumentation(
    tool_name="filter_list",
    detailed_description="""
Filters a list of dictionaries based on a field condition. Supports operators:
- **eq**: Equal to
- **ne**: Not equal to
- **gt**: Greater than
- **lt**: Less than
- **gte**: Greater than or equal
- **lte**: Less than or equal
- **contains**: String contains (in string representation)
- **in**: Value is in a list of options

Returns items that match the condition. Items missing the field are treated as
having a None value.
""".strip(),
    sample_input={
        "items": [
            {"name": "Alice", "age": 30, "department": "Sales"},
            {"name": "Bob", "age": 25, "department": "Engineering"},
            {"name": "Charlie", "age": 35, "department": "Sales"},
            {"name": "Diana", "age": 28, "department": "Marketing"}
        ],
        "field": "age",
        "operator": "gte",
        "value": 30
    },
    sample_output=[
        {"name": "Alice", "age": 30, "department": "Sales"},
        {"name": "Charlie", "age": 35, "department": "Sales"}
    ],
    use_cases=[
        "Filtering records by status or category",
        "Finding items above/below a threshold",
        "Searching for records containing text",
        "Narrowing down query results"
    ],
    tips=[
        "Use 'in' operator with a list for multiple matching values",
        "Combine multiple filter calls for AND conditions",
        "Missing fields are treated as None (only 'ne' will match)",
        "For complex filters, chain multiple filter_list calls"
    ],
    related_tools=["sort_list", "group_by", "aggregate_list"]
))


register_tool_doc(ToolDocumentation(
    tool_name="sort_list",
    detailed_description="""
Sorts a list of dictionaries by a specified key field. Supports:
- Ascending order (default)
- Descending order (set descending=true)

Items missing the sort key are treated as having a value of 0.
Handles both numeric and string sorting based on the key values.
""".strip(),
    sample_input={
        "items": [
            {"name": "Charlie", "score": 85},
            {"name": "Alice", "score": 92},
            {"name": "Bob", "score": 78}
        ],
        "sort_key": "score",
        "descending": True
    },
    sample_output=[
        {"name": "Alice", "score": 92},
        {"name": "Charlie", "score": 85},
        {"name": "Bob", "score": 78}
    ],
    use_cases=[
        "Ranking results by score",
        "Sorting products by price",
        "Ordering records by date",
        "Creating leaderboards"
    ],
    tips=[
        "Set descending=true for highest-first ordering",
        "Missing sort_key fields are treated as 0",
        "For multiple sort keys, call sort_list multiple times",
        "Stable sort maintains relative order of equal elements"
    ],
    related_tools=["filter_list", "group_by", "aggregate_list"]
))


register_tool_doc(ToolDocumentation(
    tool_name="group_by",
    detailed_description="""
Groups a list of dictionaries by a specified key field. Each unique value of the
key becomes a group, and all items with that value are collected in that group.

This is similar to SQL's GROUP BY but returns the full items rather than
aggregated values. For aggregation, combine with aggregate_list.

Items missing the group key are placed in an "unknown" group.
""".strip(),
    sample_input={
        "items": [
            {"name": "Alice", "department": "Sales", "sales": 1500},
            {"name": "Bob", "department": "Engineering", "sales": 0},
            {"name": "Charlie", "department": "Sales", "sales": 2200},
            {"name": "Diana", "department": "Marketing", "sales": 800}
        ],
        "group_key": "department"
    },
    sample_output={
        "Sales": [
            {"name": "Alice", "department": "Sales", "sales": 1500},
            {"name": "Charlie", "department": "Sales", "sales": 2200}
        ],
        "Engineering": [
            {"name": "Bob", "department": "Engineering", "sales": 0}
        ],
        "Marketing": [
            {"name": "Diana", "department": "Marketing", "sales": 800}
        ]
    },
    use_cases=[
        "Grouping employees by department",
        "Categorizing products by type",
        "Organizing events by date",
        "Clustering data for batch processing"
    ],
    tips=[
        "Group keys are converted to strings",
        "Combine with aggregate_list for group statistics",
        "Missing group_key values go to 'unknown' group",
        "Order within groups is preserved"
    ],
    related_tools=["aggregate_list", "filter_list", "sort_list"]
))


register_tool_doc(ToolDocumentation(
    tool_name="paginate_list",
    detailed_description="""
Paginates a list into pages of a specified size. Returns a single page along
with pagination metadata.

This is useful for:
- Implementing paged APIs
- Displaying large datasets in chunks
- Lazy loading data
- Building paginated UIs

Page numbers are 1-indexed (first page is 1, not 0).
""".strip(),
    sample_input={
        "items": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"},
            {"id": 4, "name": "Item 4"},
            {"id": 5, "name": "Item 5"}
        ],
        "page": 1,
        "page_size": 2
    },
    sample_output={
        "items": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"}
        ],
        "page": 1,
        "page_size": 2,
        "total_items": 5,
        "total_pages": 3,
        "has_next": True,
        "has_prev": False
    },
    use_cases=[
        "Building paginated API responses",
        "Implementing infinite scroll",
        "Batch processing large datasets",
        "Creating paged reports"
    ],
    tips=[
        "Page numbers start at 1, not 0",
        "Use has_next/has_prev for navigation logic",
        "Last page may have fewer items than page_size",
        "Empty list returns page 1 with empty items"
    ],
    related_tools=["filter_list", "sort_list"]
))


register_tool_doc(ToolDocumentation(
    tool_name="map_fields",
    detailed_description="""
Maps fields from a source dictionary to a target structure using a field mapping.
This is useful for transforming data between different schemas or APIs.

The mapping specifies which source fields map to which target fields.
Fields not in the mapping are ignored.
""".strip(),
    sample_input={
        "source": {
            "firstName": "John",
            "lastName": "Doe",
            "emailAddress": "john@example.com",
            "phoneNumber": "555-1234"
        },
        "mapping": {
            "firstName": "first_name",
            "lastName": "last_name",
            "emailAddress": "email"
        }
    },
    sample_output={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
    },
    use_cases=[
        "API data transformation",
        "Database field mapping",
        "Integration between systems",
        "Data normalization"
    ],
    tips=[
        "Unmapped source fields are dropped",
        "Target fields get None if source field missing",
        "Use for schema conversion between APIs",
        "Chain with filter_dict_keys for complex transforms"
    ],
    related_tools=["flatten_nested_dict", "merge_dicts", "filter_dict_keys"]
))


# =============================================================================
# MCP TOOL DOCUMENTATION (Template for dynamic MCP tools)
# =============================================================================

def generate_mcp_tool_doc(
    tool_name: str,
    description: str,
    input_schema: Dict[str, Any],
    server_name: str
) -> ToolDocumentation:
    """
    Generate documentation for an MCP tool based on its schema.
    Creates sample input from the schema and provides generic guidance.
    """
    # Generate sample input from schema
    sample_input = {}
    properties = input_schema.get("properties", {})
    required = input_schema.get("required", [])
    
    for prop_name, prop_def in properties.items():
        prop_type = prop_def.get("type", "string")
        prop_desc = prop_def.get("description", "")
        
        # Generate sample value based on type
        if prop_type == "string":
            if "email" in prop_name.lower():
                sample_input[prop_name] = "example@email.com"
            elif "url" in prop_name.lower():
                sample_input[prop_name] = "https://example.com"
            elif "date" in prop_name.lower():
                sample_input[prop_name] = "2025-01-15"
            elif "id" in prop_name.lower():
                sample_input[prop_name] = "abc123"
            else:
                sample_input[prop_name] = f"sample_{prop_name}"
        elif prop_type == "number" or prop_type == "integer":
            sample_input[prop_name] = 100
        elif prop_type == "boolean":
            sample_input[prop_name] = True
        elif prop_type == "array":
            item_type = prop_def.get("items", {}).get("type", "string")
            if item_type == "string":
                sample_input[prop_name] = ["item1", "item2"]
            else:
                sample_input[prop_name] = [1, 2, 3]
        elif prop_type == "object":
            sample_input[prop_name] = {"key": "value"}
    
    detailed_desc = f"""
{description}

This tool is provided by the MCP server: {server_name}

**Parameters:**
"""
    for prop_name, prop_def in properties.items():
        prop_type = prop_def.get("type", "string")
        prop_desc = prop_def.get("description", "No description")
        req_marker = " (required)" if prop_name in required else " (optional)"
        detailed_desc += f"\n- **{prop_name}** ({prop_type}){req_marker}: {prop_desc}"
    
    return ToolDocumentation(
        tool_name=tool_name,
        detailed_description=detailed_desc.strip(),
        sample_input=sample_input,
        sample_output={"status": "success", "message": "Tool executed successfully", "data": {}},
        use_cases=[
            f"Integrate with {server_name} server capabilities",
            "Automate external service interactions",
            "Extend agent capabilities with external tools"
        ],
        tips=[
            f"This tool requires the {server_name} MCP server to be running",
            "Check MCP server logs for detailed error messages",
            "Ensure all required parameters are provided"
        ],
        related_tools=[]
    )


def get_tool_documentation(tool_name: str, tool=None) -> Optional[Dict[str, Any]]:
    """
    Get documentation for a tool. First checks the static registry,
    then generates dynamic documentation for MCP tools.
    
    Args:
        tool_name: Name of the tool
        tool: Optional tool object (for MCP tools)
        
    Returns:
        Documentation dict or None
    """
    # Check static documentation first
    doc = get_tool_doc(tool_name)
    if doc:
        return doc.to_dict()
    
    # For MCP tools, generate documentation from schema
    if tool and hasattr(tool, 'metadata') and tool.metadata:
        source = tool.metadata.source if tool.metadata.source else ''
        if source.startswith('mcp:'):
            server_name = source.replace('mcp:', '')
            schema = tool.get_schema() if hasattr(tool, 'get_schema') else None
            if schema:
                input_schema = schema.to_json_schema() if hasattr(schema, 'to_json_schema') else {}
                mcp_doc = generate_mcp_tool_doc(
                    tool_name=tool_name,
                    description=tool.description or "MCP tool",
                    input_schema=input_schema.get("properties", {}),
                    server_name=server_name
                )
                return mcp_doc.to_dict()
    
    # Return generic documentation if nothing found
    return {
        "tool_name": tool_name,
        "detailed_description": tool.description if tool else "No detailed documentation available for this tool.",
        "sample_input": {},
        "sample_output": {},
        "use_cases": [],
        "tips": [],
        "related_tools": []
    }
