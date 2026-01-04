"""
Communication Tools Library - Tools for notifications and messaging.

This module provides tools for:
- Email formatting
- SMS formatting
- Notification templates
- Message generation

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

from ..base_tool import ToolCategory
from ..function_tool import FunctionTool

logger = logging.getLogger(__name__)


# =============================================================================
# EMAIL TOOLS
# =============================================================================

def format_email(to: str, subject: str, body: str, 
                from_email: str = None,
                cc: List[str] = None,
                bcc: List[str] = None,
                reply_to: str = None,
                is_html: bool = False) -> Dict[str, Any]:
    """
    Format an email message.
    
    Args:
        to: Recipient email
        subject: Email subject
        body: Email body
        from_email: Sender email
        cc: CC recipients
        bcc: BCC recipients
        reply_to: Reply-to address
        is_html: Body is HTML
        
    Returns:
        Formatted email object
    """
    email = {
        "to": to,
        "subject": subject,
        "body": body,
        "content_type": "text/html" if is_html else "text/plain",
        "created_at": datetime.utcnow().isoformat()
    }
    
    if from_email:
        email["from"] = from_email
    if cc:
        email["cc"] = cc
    if bcc:
        email["bcc"] = bcc
    if reply_to:
        email["reply_to"] = reply_to
    
    return email


def generate_email_from_template(template_name: str, 
                                 variables: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate email from predefined template.
    
    Args:
        template_name: Name of template
        variables: Variables to substitute
        
    Returns:
        Generated email content
    """
    templates = {
        "welcome": {
            "subject": "Welcome to {company_name}!",
            "body": """Dear {customer_name},

Welcome to {company_name}! We're thrilled to have you as a new customer.

Your account has been successfully created. Here's what you can do next:

1. Log in to your account at {login_url}
2. Complete your profile
3. Explore our services

If you have any questions, please don't hesitate to contact our support team.

Best regards,
The {company_name} Team"""
        },
        "password_reset": {
            "subject": "Password Reset Request - {company_name}",
            "body": """Dear {customer_name},

We received a request to reset your password. Click the link below to create a new password:

{reset_link}

This link will expire in {expiry_hours} hours.

If you didn't request this, please ignore this email or contact support.

Best regards,
The {company_name} Team"""
        },
        "transaction_alert": {
            "subject": "Transaction Alert - {transaction_type}",
            "body": """Dear {customer_name},

A {transaction_type} of {currency} {amount} has been made from your account.

Transaction Details:
- Date: {transaction_date}
- Reference: {reference_number}
- Description: {description}
- Balance: {currency} {balance}

If you did not authorize this transaction, please contact us immediately.

Best regards,
{company_name}"""
        },
        "loan_approved": {
            "subject": "Congratulations! Your Loan Application is Approved",
            "body": """Dear {customer_name},

Great news! Your loan application has been approved.

Loan Details:
- Loan Amount: {currency} {loan_amount}
- Interest Rate: {interest_rate}% per annum
- Term: {term_months} months
- Monthly Payment: {currency} {monthly_payment}
- First Payment Date: {first_payment_date}

Next Steps:
1. Review and sign the loan agreement
2. Provide any remaining documents
3. Funds will be disbursed within {disbursement_days} business days

Best regards,
{company_name}"""
        },
        "loan_declined": {
            "subject": "Update on Your Loan Application",
            "body": """Dear {customer_name},

Thank you for your loan application with {company_name}.

After careful review, we regret to inform you that we are unable to approve your application at this time.

Primary Reasons:
{decline_reasons}

What You Can Do:
1. Review your credit report for errors
2. Work on improving your credit score
3. Consider a co-applicant or collateral
4. Reapply after {reapply_months} months

If you have questions, please contact us.

Best regards,
{company_name}"""
        },
        "account_statement": {
            "subject": "Your {month} Account Statement",
            "body": """Dear {customer_name},

Your account statement for {month} is now available.

Account Summary:
- Account Number: {account_number}
- Opening Balance: {currency} {opening_balance}
- Total Credits: {currency} {total_credits}
- Total Debits: {currency} {total_debits}
- Closing Balance: {currency} {closing_balance}

View your detailed statement by logging into your account.

Best regards,
{company_name}"""
        },
        "kyc_reminder": {
            "subject": "Action Required: Complete Your KYC Verification",
            "body": """Dear {customer_name},

Your KYC verification is pending. Please complete it to enjoy full access to our services.

Required Documents:
{required_documents}

Deadline: {deadline}

Complete your verification here: {verification_url}

Best regards,
{company_name}"""
        },
        "payment_reminder": {
            "subject": "Payment Reminder - {payment_type} Due",
            "body": """Dear {customer_name},

This is a friendly reminder that your {payment_type} payment is due.

Payment Details:
- Amount Due: {currency} {amount_due}
- Due Date: {due_date}
- Account: {account_reference}

Pay now to avoid late fees: {payment_url}

Best regards,
{company_name}"""
        }
    }
    
    template = templates.get(template_name)
    if not template:
        return {"error": f"Template '{template_name}' not found",
                "available_templates": list(templates.keys())}
    
    # Substitute variables
    subject = template["subject"]
    body = template["body"]
    
    for key, value in variables.items():
        placeholder = "{" + key + "}"
        subject = subject.replace(placeholder, str(value))
        body = body.replace(placeholder, str(value))
    
    return {
        "subject": subject,
        "body": body,
        "template_used": template_name,
        "variables_provided": list(variables.keys())
    }


def validate_email_content(email: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate email content for common issues.
    
    Args:
        email: Email object
        
    Returns:
        Validation result
    """
    issues = []
    warnings = []
    
    # Required fields
    if not email.get("to"):
        issues.append("Missing recipient (to)")
    if not email.get("subject"):
        issues.append("Missing subject")
    if not email.get("body"):
        issues.append("Missing body")
    
    # Email format validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if email.get("to") and not re.match(email_pattern, email["to"]):
        issues.append("Invalid recipient email format")
    
    if email.get("from") and not re.match(email_pattern, email["from"]):
        issues.append("Invalid sender email format")
    
    # Subject length
    subject = email.get("subject", "")
    if len(subject) > 200:
        warnings.append("Subject exceeds 200 characters")
    
    # Body checks
    body = email.get("body", "")
    if len(body) < 10:
        warnings.append("Body seems too short")
    
    # Check for unfilled placeholders
    placeholders = re.findall(r'\{[a-z_]+\}', body + subject)
    if placeholders:
        warnings.append(f"Unfilled placeholders found: {placeholders}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings
    }


# =============================================================================
# SMS TOOLS
# =============================================================================

def format_sms(to: str, message: str, sender_id: str = None) -> Dict[str, Any]:
    """
    Format an SMS message.
    
    Args:
        to: Recipient phone number
        message: SMS content
        sender_id: Sender ID
        
    Returns:
        Formatted SMS object
    """
    # Calculate SMS segments (160 chars for GSM-7, 70 for Unicode)
    is_unicode = any(ord(c) > 127 for c in message)
    chars_per_segment = 70 if is_unicode else 160
    
    if len(message) <= chars_per_segment:
        segments = 1
    else:
        # Concatenated SMS use 6-7 bytes for header
        chars_per_concat = 67 if is_unicode else 153
        segments = (len(message) + chars_per_concat - 1) // chars_per_concat
    
    return {
        "to": to,
        "message": message,
        "sender_id": sender_id,
        "character_count": len(message),
        "segments": segments,
        "is_unicode": is_unicode,
        "created_at": datetime.utcnow().isoformat()
    }


def generate_otp_message(otp: str, purpose: str = "verification",
                        expiry_minutes: int = 5) -> str:
    """
    Generate OTP message.
    
    Args:
        otp: One-time password
        purpose: Purpose of OTP
        expiry_minutes: Expiry time in minutes
        
    Returns:
        Formatted OTP message
    """
    templates = {
        "verification": f"Your verification code is {otp}. Valid for {expiry_minutes} minutes. Do not share this code.",
        "login": f"Your login OTP is {otp}. Expires in {expiry_minutes} min. Never share this code with anyone.",
        "transaction": f"Your transaction OTP is {otp}. Valid for {expiry_minutes} minutes. Do not share.",
        "password_reset": f"Your password reset code is {otp}. Valid for {expiry_minutes} minutes.",
        "registration": f"Welcome! Your registration code is {otp}. Valid for {expiry_minutes} minutes."
    }
    
    return templates.get(purpose, templates["verification"])


def generate_alert_sms(alert_type: str, variables: Dict[str, Any]) -> str:
    """
    Generate alert SMS from template.
    
    Args:
        alert_type: Type of alert
        variables: Template variables
        
    Returns:
        Alert message
    """
    templates = {
        "transaction": "Alert: {type} of {currency}{amount} on {date}. Bal: {currency}{balance}. Ref: {ref}",
        "login": "Login detected from {device} at {location} on {date}. Not you? Call {helpline}",
        "low_balance": "Alert: Your balance is {currency}{balance}. Maintain min balance to avoid charges.",
        "payment_due": "Reminder: {payment_type} of {currency}{amount} due on {due_date}. Pay to avoid late fees.",
        "card_blocked": "Your card ending {last4} has been blocked. Contact {helpline} immediately.",
        "fraud_alert": "Suspicious activity detected on your account. If not you, call {helpline} now."
    }
    
    template = templates.get(alert_type, "Alert: {message}")
    
    for key, value in variables.items():
        placeholder = "{" + key + "}"
        template = template.replace(placeholder, str(value))
    
    return template


# =============================================================================
# NOTIFICATION TOOLS
# =============================================================================

def create_push_notification(title: str, body: str,
                            data: Dict[str, Any] = None,
                            channel: str = "default",
                            priority: str = "normal") -> Dict[str, Any]:
    """
    Create push notification payload.
    
    Args:
        title: Notification title
        body: Notification body
        data: Additional data payload
        channel: Notification channel
        priority: Priority (normal, high)
        
    Returns:
        Push notification object
    """
    notification = {
        "notification": {
            "title": title,
            "body": body
        },
        "data": data or {},
        "android": {
            "notification": {
                "channel_id": channel
            },
            "priority": priority
        },
        "apns": {
            "payload": {
                "aps": {
                    "alert": {
                        "title": title,
                        "body": body
                    },
                    "sound": "default"
                }
            }
        },
        "created_at": datetime.utcnow().isoformat()
    }
    
    return notification


def create_in_app_notification(type: str, title: str, message: str,
                              action_url: str = None,
                              metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create in-app notification.
    
    Args:
        type: Notification type (info, success, warning, error)
        title: Notification title
        message: Notification message
        action_url: URL for action button
        metadata: Additional metadata
        
    Returns:
        In-app notification object
    """
    return {
        "type": type,
        "title": title,
        "message": message,
        "action_url": action_url,
        "metadata": metadata or {},
        "read": False,
        "created_at": datetime.utcnow().isoformat()
    }


def batch_notifications(notifications: List[Dict[str, Any]], 
                       channel: str = "all") -> Dict[str, Any]:
    """
    Prepare batch notifications.
    
    Args:
        notifications: List of notification objects
        channel: Delivery channel (email, sms, push, all)
        
    Returns:
        Batch notification payload
    """
    batch = {
        "batch_id": f"BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "channel": channel,
        "notification_count": len(notifications),
        "notifications": notifications,
        "created_at": datetime.utcnow().isoformat()
    }
    
    return batch


# =============================================================================
# MESSAGE FORMATTING TOOLS
# =============================================================================

def format_currency_message(amount: float, currency: str = "USD",
                           locale: str = "en_US") -> str:
    """
    Format currency for messages.
    
    Args:
        amount: Numeric amount
        currency: Currency code
        locale: Locale for formatting
        
    Returns:
        Formatted currency string
    """
    symbols = {
        "USD": "$", "EUR": "€", "GBP": "£", "INR": "₹",
        "JPY": "¥", "CNY": "¥", "AUD": "A$", "CAD": "C$"
    }
    
    symbol = symbols.get(currency, currency + " ")
    
    # Format with thousand separators
    if locale.startswith("en"):
        formatted = f"{symbol}{amount:,.2f}"
    else:
        formatted = f"{amount:,.2f} {currency}"
    
    return formatted


def format_date_message(date_str: str, format_type: str = "full",
                       input_format: str = "%Y-%m-%d") -> str:
    """
    Format date for messages.
    
    Args:
        date_str: Date string
        format_type: full, short, relative
        input_format: Input date format
        
    Returns:
        Formatted date string
    """
    try:
        dt = datetime.strptime(date_str, input_format)
        
        if format_type == "full":
            return dt.strftime("%B %d, %Y")
        elif format_type == "short":
            return dt.strftime("%b %d, %Y")
        elif format_type == "relative":
            now = datetime.now()
            diff = now - dt
            
            if diff.days == 0:
                return "Today"
            elif diff.days == 1:
                return "Yesterday"
            elif diff.days == -1:
                return "Tomorrow"
            elif diff.days < 7:
                return f"{abs(diff.days)} days {'ago' if diff.days > 0 else 'from now'}"
            else:
                return dt.strftime("%b %d, %Y")
        else:
            return dt.strftime("%Y-%m-%d")
    except ValueError:
        return date_str


def truncate_message(message: str, max_length: int = 160,
                    ellipsis: str = "...") -> str:
    """
    Truncate message to maximum length.
    
    Args:
        message: Original message
        max_length: Maximum length
        ellipsis: Ellipsis string
        
    Returns:
        Truncated message
    """
    if len(message) <= max_length:
        return message
    
    return message[:max_length - len(ellipsis)] + ellipsis


# =============================================================================
# REGISTER COMMUNICATION TOOLS
# =============================================================================

def get_communication_tools() -> List[FunctionTool]:
    """Get all communication tools."""
    tools = []
    
    # Email tools
    tools.append(FunctionTool.from_function(
        format_email, name="format_email",
        description="Format an email message",
        category=ToolCategory.COMMUNICATION
    ))
    tools.append(FunctionTool.from_function(
        generate_email_from_template, name="generate_email_from_template",
        description="Generate email from predefined template",
        category=ToolCategory.COMMUNICATION
    ))
    tools.append(FunctionTool.from_function(
        validate_email_content, name="validate_email_content",
        description="Validate email content for issues",
        category=ToolCategory.COMMUNICATION
    ))
    
    # SMS tools
    tools.append(FunctionTool.from_function(
        format_sms, name="format_sms",
        description="Format SMS message with segment calculation",
        category=ToolCategory.COMMUNICATION
    ))
    tools.append(FunctionTool.from_function(
        generate_otp_message, name="generate_otp_message",
        description="Generate OTP message for various purposes",
        category=ToolCategory.COMMUNICATION
    ))
    tools.append(FunctionTool.from_function(
        generate_alert_sms, name="generate_alert_sms",
        description="Generate alert SMS from template",
        category=ToolCategory.COMMUNICATION
    ))
    
    # Notification tools
    tools.append(FunctionTool.from_function(
        create_push_notification, name="create_push_notification",
        description="Create push notification payload",
        category=ToolCategory.COMMUNICATION
    ))
    tools.append(FunctionTool.from_function(
        create_in_app_notification, name="create_in_app_notification",
        description="Create in-app notification",
        category=ToolCategory.COMMUNICATION
    ))
    tools.append(FunctionTool.from_function(
        batch_notifications, name="batch_notifications",
        description="Prepare batch notifications",
        category=ToolCategory.COMMUNICATION
    ))
    
    # Formatting tools
    tools.append(FunctionTool.from_function(
        format_currency_message, name="format_currency_message",
        description="Format currency for messages",
        category=ToolCategory.COMMUNICATION
    ))
    tools.append(FunctionTool.from_function(
        format_date_message, name="format_date_message",
        description="Format date for messages",
        category=ToolCategory.COMMUNICATION
    ))
    tools.append(FunctionTool.from_function(
        truncate_message, name="truncate_message",
        description="Truncate message to maximum length",
        category=ToolCategory.COMMUNICATION
    ))
    
    return tools


def register_communication_tools(registry) -> int:
    """Register all communication tools."""
    tools = get_communication_tools()
    count = 0
    for tool in tools:
        if registry.register(tool):
            count += 1
    logger.info(f"Registered {count} communication tools")
    return count
