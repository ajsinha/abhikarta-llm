"""
Pre-built Tools Package - Ready-to-use tools for common operations.

This package provides:
- Common utility tools (date, math, text, validation)
- Banking industry tools (KYC, credit, loan, compliance)
- Integration tools (API, notifications, data transformation)
- General-purpose tools (web search, document handling, file operations)

Usage:
    from abhikarta.tools.prebuilt import get_all_prebuilt_tools, register_all_prebuilt_tools
    
    # Get all tools
    tools = get_all_prebuilt_tools()
    
    # Register with registry
    from abhikarta.tools import get_tools_registry
    registry = get_tools_registry()
    register_all_prebuilt_tools(registry)

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

from .common_tools import (
    get_common_tools,
    register_common_tools,
    # Date/Time
    get_current_datetime,
    parse_date,
    calculate_date_difference,
    add_days_to_date,
    get_business_days,
    # Math
    calculate_expression,
    calculate_percentage,
    calculate_compound_interest,
    calculate_loan_emi,
    convert_currency,
    # Text
    extract_text_patterns,
    clean_text,
    extract_entities,
    generate_summary_stats,
    mask_sensitive_data,
    # Validation
    validate_email,
    validate_phone,
    validate_credit_card,
    validate_iban,
    validate_ssn,
    # Conversion
    json_to_csv,
    csv_to_json,
    base64_encode,
    base64_decode,
    generate_hash,
    # ID Generation
    generate_uuid,
    generate_reference_number,
    generate_account_number,
)

from .banking_tools import (
    get_banking_tools,
    register_banking_tools,
    # KYC
    verify_identity_document,
    calculate_kyc_risk_score,
    verify_address,
    # Credit
    calculate_credit_score,
    assess_debt_to_income,
    # Loan
    calculate_loan_eligibility,
    generate_amortization_schedule,
    # Transaction
    analyze_transaction,
    detect_transaction_patterns,
    calculate_transaction_limits,
    # Compliance
    check_sanctions_list,
    generate_aml_report,
    validate_regulatory_compliance,
)

from .integration_tools import (
    get_integration_tools,
    register_integration_tools,
    # HTTP/API
    make_http_request,
    build_query_string,
    parse_json_response,
    validate_api_response,
    # Notifications
    format_email_template,
    create_notification,
    format_sms_message,
    # Data transformation
    map_fields,
    flatten_nested_dict,
    unflatten_dict,
    merge_dicts,
    filter_dict_keys,
    # List/Array
    filter_list,
    sort_list,
    group_by,
    aggregate_list,
    paginate_list,
    # Workflow helpers
    create_workflow_context,
    update_workflow_context,
    evaluate_condition,
)

from .general_tools import (
    get_general_tools,
    register_general_tools,
    # Web/Search
    web_search,
    web_fetch,
    intranet_search,
    news_search,
    # Document handling
    read_document,
    write_document,
    convert_document,
    extract_document_metadata,
    # File operations
    list_files,
    copy_file,
    move_file,
    delete_file,
    # System utilities
    get_system_info,
    execute_shell_command,
    get_environment_variable,
    set_environment_variable,
    # Network tools
    check_url_status,
    ping_host,
    dns_lookup,
    parse_url,
    # Encoding
    url_encode,
    url_decode,
    html_encode,
    html_decode,
)


def get_all_prebuilt_tools():
    """Get all pre-built tools."""
    return (get_common_tools() + get_banking_tools() + 
            get_integration_tools() + get_general_tools())


def register_all_prebuilt_tools(registry) -> int:
    """
    Register all pre-built tools with the registry.
    
    Args:
        registry: ToolsRegistry instance
        
    Returns:
        Total number of tools registered
    """
    count = register_common_tools(registry)
    count += register_banking_tools(registry)
    count += register_integration_tools(registry)
    count += register_general_tools(registry)
    return count


__all__ = [
    # Main functions
    'get_all_prebuilt_tools',
    'register_all_prebuilt_tools',
    'get_common_tools',
    'get_banking_tools',
    'get_integration_tools',
    'get_general_tools',
    'register_common_tools',
    'register_banking_tools',
    'register_integration_tools',
    'register_general_tools',
    
    # Common tools
    'get_current_datetime',
    'parse_date',
    'calculate_date_difference',
    'add_days_to_date',
    'get_business_days',
    'calculate_expression',
    'calculate_percentage',
    'calculate_compound_interest',
    'calculate_loan_emi',
    'convert_currency',
    'extract_text_patterns',
    'clean_text',
    'extract_entities',
    'generate_summary_stats',
    'mask_sensitive_data',
    'validate_email',
    'validate_phone',
    'validate_credit_card',
    'validate_iban',
    'validate_ssn',
    'json_to_csv',
    'csv_to_json',
    'base64_encode',
    'base64_decode',
    'generate_hash',
    'generate_uuid',
    'generate_reference_number',
    'generate_account_number',
    
    # Banking tools
    'verify_identity_document',
    'calculate_kyc_risk_score',
    'verify_address',
    'calculate_credit_score',
    'assess_debt_to_income',
    'calculate_loan_eligibility',
    'generate_amortization_schedule',
    'analyze_transaction',
    'detect_transaction_patterns',
    'calculate_transaction_limits',
    'check_sanctions_list',
    'generate_aml_report',
    'validate_regulatory_compliance',
    
    # Integration tools
    'make_http_request',
    'build_query_string',
    'parse_json_response',
    'validate_api_response',
    'format_email_template',
    'create_notification',
    'format_sms_message',
    'map_fields',
    'flatten_nested_dict',
    'unflatten_dict',
    'merge_dicts',
    'filter_dict_keys',
    'filter_list',
    'sort_list',
    'group_by',
    'aggregate_list',
    'paginate_list',
    'create_workflow_context',
    'update_workflow_context',
    'evaluate_condition',
    
    # General tools
    'web_search',
    'web_fetch',
    'intranet_search',
    'news_search',
    'read_document',
    'write_document',
    'convert_document',
    'extract_document_metadata',
    'list_files',
    'copy_file',
    'move_file',
    'delete_file',
    'get_system_info',
    'execute_shell_command',
    'get_environment_variable',
    'set_environment_variable',
    'check_url_status',
    'ping_host',
    'dns_lookup',
    'parse_url',
    'url_encode',
    'url_decode',
    'html_encode',
    'html_decode',
]
