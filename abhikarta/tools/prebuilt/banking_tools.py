"""
Banking Tools Library - Tools specific to banking operations.

This module provides banking industry tools for:
- KYC verification
- Credit scoring
- Loan processing
- Transaction analysis
- Compliance checking
- Fraud detection

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import random
import math

from ..base_tool import (
    BaseTool, ToolMetadata, ToolSchema, ToolParameter,
    ToolResult, ToolType, ToolCategory
)
from ..function_tool import FunctionTool

logger = logging.getLogger(__name__)


# =============================================================================
# KYC VERIFICATION TOOLS
# =============================================================================

def verify_identity_document(document_type: str, document_number: str,
                            issuing_country: str, expiry_date: str = None) -> Dict[str, Any]:
    """
    Verify identity document format and validity.
    
    Args:
        document_type: Type of document (passport, drivers_license, national_id)
        document_number: Document number
        issuing_country: Country code
        expiry_date: Expiry date in YYYY-MM-DD format
        
    Returns:
        Verification result with validity status
    """
    result = {
        "document_type": document_type,
        "document_number": document_number[:4] + "****",
        "issuing_country": issuing_country,
        "format_valid": False,
        "expired": None,
        "checks_passed": []
    }
    
    # Document format validation
    patterns = {
        "passport": {
            "US": r'^[A-Z]\d{8}$',
            "UK": r'^\d{9}$',
            "IN": r'^[A-Z]\d{7}$',
            "DEFAULT": r'^[A-Z0-9]{6,12}$'
        },
        "drivers_license": {
            "US": r'^[A-Z0-9]{7,14}$',
            "UK": r'^[A-Z0-9]{16}$',
            "DEFAULT": r'^[A-Z0-9]{6,16}$'
        },
        "national_id": {
            "DEFAULT": r'^[A-Z0-9]{8,20}$'
        }
    }
    
    doc_patterns = patterns.get(document_type.lower(), {"DEFAULT": r'^[A-Z0-9]{6,20}$'})
    pattern = doc_patterns.get(issuing_country.upper(), doc_patterns.get("DEFAULT"))
    
    if re.match(pattern, document_number.upper()):
        result["format_valid"] = True
        result["checks_passed"].append("format_validation")
    
    # Expiry check
    if expiry_date:
        try:
            exp_date = datetime.strptime(expiry_date, "%Y-%m-%d")
            result["expired"] = exp_date < datetime.now()
            if not result["expired"]:
                result["checks_passed"].append("expiry_check")
        except ValueError:
            result["expired"] = None
    
    result["verification_status"] = "passed" if len(result["checks_passed"]) >= 2 else "review_required"
    return result


def calculate_kyc_risk_score(customer_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate KYC risk score based on customer data.
    
    Args:
        customer_data: Dictionary with customer information
        
    Returns:
        Risk assessment with score and factors
    """
    risk_score = 0
    risk_factors = []
    
    # Country risk
    high_risk_countries = ["AF", "IR", "KP", "SY", "YE"]
    country = customer_data.get("country", "").upper()
    if country in high_risk_countries:
        risk_score += 30
        risk_factors.append({"factor": "high_risk_country", "weight": 30})
    
    # PEP (Politically Exposed Person) check
    if customer_data.get("is_pep", False):
        risk_score += 25
        risk_factors.append({"factor": "politically_exposed_person", "weight": 25})
    
    # Occupation risk
    high_risk_occupations = ["money_service", "gambling", "arms_dealer", "cryptocurrency"]
    occupation = customer_data.get("occupation", "").lower()
    if occupation in high_risk_occupations:
        risk_score += 20
        risk_factors.append({"factor": "high_risk_occupation", "weight": 20})
    
    # Income source
    if customer_data.get("income_source") == "unknown":
        risk_score += 15
        risk_factors.append({"factor": "unknown_income_source", "weight": 15})
    
    # Account purpose
    if customer_data.get("account_purpose") in ["international_transfers", "business"]:
        risk_score += 10
        risk_factors.append({"factor": "high_risk_account_purpose", "weight": 10})
    
    # Determine risk level
    if risk_score >= 50:
        risk_level = "high"
    elif risk_score >= 25:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "enhanced_due_diligence_required": risk_level in ["high", "medium"],
        "recommendation": "approve" if risk_level == "low" else "manual_review"
    }


def verify_address(address_data: Dict[str, str]) -> Dict[str, Any]:
    """
    Verify address format and completeness.
    
    Args:
        address_data: Dictionary with address fields
        
    Returns:
        Address verification result
    """
    required_fields = ["street", "city", "postal_code", "country"]
    missing_fields = [f for f in required_fields if not address_data.get(f)]
    
    result = {
        "is_complete": len(missing_fields) == 0,
        "missing_fields": missing_fields,
        "format_valid": True,
        "standardized_address": None
    }
    
    # Postal code validation
    postal_patterns = {
        "US": r'^\d{5}(-\d{4})?$',
        "UK": r'^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$',
        "IN": r'^\d{6}$',
        "DEFAULT": r'^[A-Z0-9]{3,10}$'
    }
    
    country = address_data.get("country", "").upper()
    pattern = postal_patterns.get(country, postal_patterns["DEFAULT"])
    postal_code = address_data.get("postal_code", "")
    
    if postal_code and not re.match(pattern, postal_code.upper()):
        result["format_valid"] = False
    
    # Standardize address
    if result["is_complete"]:
        result["standardized_address"] = {
            "line1": address_data.get("street", "").title(),
            "line2": address_data.get("apartment", ""),
            "city": address_data.get("city", "").title(),
            "state": address_data.get("state", "").upper(),
            "postal_code": postal_code.upper(),
            "country": country
        }
    
    return result


# =============================================================================
# CREDIT SCORING TOOLS
# =============================================================================

def calculate_credit_score(credit_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate credit score based on credit history data.
    
    Args:
        credit_data: Dictionary with credit history information
        
    Returns:
        Credit score and breakdown
    """
    score = 300  # Base score
    factors = []
    
    # Payment history (35% weight)
    payment_history = credit_data.get("payment_history", {})
    on_time_rate = payment_history.get("on_time_percentage", 100)
    payment_score = int((on_time_rate / 100) * 250 * 0.35)
    score += payment_score
    factors.append({
        "factor": "payment_history",
        "weight": "35%",
        "score": payment_score,
        "detail": f"{on_time_rate}% on-time payments"
    })
    
    # Credit utilization (30% weight)
    utilization = credit_data.get("credit_utilization", 50)
    util_score = int(max(0, (100 - utilization)) / 100 * 250 * 0.30)
    score += util_score
    factors.append({
        "factor": "credit_utilization",
        "weight": "30%",
        "score": util_score,
        "detail": f"{utilization}% utilization"
    })
    
    # Credit history length (15% weight)
    history_years = credit_data.get("credit_history_years", 0)
    history_score = int(min(history_years / 10, 1) * 250 * 0.15)
    score += history_score
    factors.append({
        "factor": "credit_history_length",
        "weight": "15%",
        "score": history_score,
        "detail": f"{history_years} years"
    })
    
    # Credit mix (10% weight)
    credit_types = credit_data.get("credit_types", [])
    mix_score = int(min(len(credit_types) / 4, 1) * 250 * 0.10)
    score += mix_score
    factors.append({
        "factor": "credit_mix",
        "weight": "10%",
        "score": mix_score,
        "detail": f"{len(credit_types)} credit types"
    })
    
    # Recent inquiries (10% weight)
    recent_inquiries = credit_data.get("recent_inquiries", 0)
    inquiry_penalty = min(recent_inquiries * 10, 25)
    inquiry_score = int((250 * 0.10) - inquiry_penalty)
    score += max(0, inquiry_score)
    factors.append({
        "factor": "recent_inquiries",
        "weight": "10%",
        "score": max(0, inquiry_score),
        "detail": f"{recent_inquiries} inquiries"
    })
    
    # Determine rating
    if score >= 750:
        rating = "Excellent"
    elif score >= 700:
        rating = "Good"
    elif score >= 650:
        rating = "Fair"
    elif score >= 600:
        rating = "Poor"
    else:
        rating = "Very Poor"
    
    return {
        "credit_score": min(850, score),
        "rating": rating,
        "score_range": "300-850",
        "factors": factors,
        "recommendations": _get_credit_recommendations(credit_data)
    }


def _get_credit_recommendations(credit_data: Dict[str, Any]) -> List[str]:
    """Generate credit improvement recommendations."""
    recommendations = []
    
    if credit_data.get("credit_utilization", 0) > 30:
        recommendations.append("Reduce credit utilization below 30%")
    
    if credit_data.get("payment_history", {}).get("on_time_percentage", 100) < 100:
        recommendations.append("Set up automatic payments to avoid late payments")
    
    if credit_data.get("credit_history_years", 0) < 5:
        recommendations.append("Keep oldest accounts open to build history")
    
    if credit_data.get("recent_inquiries", 0) > 2:
        recommendations.append("Limit new credit applications")
    
    return recommendations


def assess_debt_to_income(monthly_income: float, monthly_debts: Dict[str, float]) -> Dict[str, Any]:
    """
    Calculate debt-to-income ratio.
    
    Args:
        monthly_income: Monthly gross income
        monthly_debts: Dictionary of monthly debt payments
        
    Returns:
        DTI analysis
    """
    total_debt = sum(monthly_debts.values())
    dti_ratio = (total_debt / monthly_income * 100) if monthly_income > 0 else 100
    
    if dti_ratio <= 28:
        rating = "Excellent"
        loan_eligible = True
    elif dti_ratio <= 36:
        rating = "Good"
        loan_eligible = True
    elif dti_ratio <= 43:
        rating = "Fair"
        loan_eligible = True
    elif dti_ratio <= 50:
        rating = "High"
        loan_eligible = False
    else:
        rating = "Very High"
        loan_eligible = False
    
    return {
        "monthly_income": monthly_income,
        "total_monthly_debt": total_debt,
        "debt_breakdown": monthly_debts,
        "dti_ratio": round(dti_ratio, 2),
        "dti_rating": rating,
        "loan_eligible": loan_eligible,
        "max_additional_debt": max(0, (monthly_income * 0.43) - total_debt)
    }


# =============================================================================
# LOAN PROCESSING TOOLS
# =============================================================================

def calculate_loan_eligibility(applicant_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine loan eligibility based on applicant data.
    
    Args:
        applicant_data: Dictionary with applicant information
        
    Returns:
        Eligibility assessment
    """
    eligibility_score = 100
    issues = []
    
    # Credit score check
    credit_score = applicant_data.get("credit_score", 0)
    if credit_score < 600:
        eligibility_score -= 40
        issues.append("Credit score below minimum requirement (600)")
    elif credit_score < 700:
        eligibility_score -= 20
        issues.append("Credit score below preferred threshold (700)")
    
    # Employment check
    employment_years = applicant_data.get("employment_years", 0)
    if employment_years < 1:
        eligibility_score -= 25
        issues.append("Less than 1 year with current employer")
    elif employment_years < 2:
        eligibility_score -= 10
        issues.append("Less than 2 years with current employer")
    
    # Income verification
    monthly_income = applicant_data.get("monthly_income", 0)
    loan_amount = applicant_data.get("requested_loan_amount", 0)
    
    if loan_amount > monthly_income * 48:
        eligibility_score -= 30
        issues.append("Loan amount exceeds 48x monthly income")
    
    # DTI check
    dti_ratio = applicant_data.get("dti_ratio", 50)
    if dti_ratio > 43:
        eligibility_score -= 25
        issues.append("Debt-to-income ratio exceeds 43%")
    
    # Determine eligibility
    if eligibility_score >= 80:
        status = "approved"
        decision = "Auto-approved"
    elif eligibility_score >= 60:
        status = "conditional"
        decision = "Conditional approval - requires additional documentation"
    elif eligibility_score >= 40:
        status = "review"
        decision = "Requires manual review"
    else:
        status = "declined"
        decision = "Does not meet minimum requirements"
    
    return {
        "eligibility_score": eligibility_score,
        "status": status,
        "decision": decision,
        "issues": issues,
        "max_loan_amount": monthly_income * 48 * (eligibility_score / 100),
        "recommended_terms": _get_recommended_loan_terms(eligibility_score, loan_amount)
    }


def _get_recommended_loan_terms(score: int, amount: float) -> Dict[str, Any]:
    """Get recommended loan terms based on eligibility."""
    if score >= 80:
        rate = 6.5
        term = 60
    elif score >= 60:
        rate = 8.5
        term = 48
    else:
        rate = 12.0
        term = 36
    
    return {
        "interest_rate": rate,
        "term_months": term,
        "monthly_payment": round(
            amount * (rate/100/12) * (1 + rate/100/12)**term / 
            ((1 + rate/100/12)**term - 1), 2
        ) if amount > 0 else 0
    }


def generate_amortization_schedule(principal: float, annual_rate: float,
                                  term_months: int, start_date: str = None) -> Dict[str, Any]:
    """
    Generate loan amortization schedule.
    
    Args:
        principal: Loan principal amount
        annual_rate: Annual interest rate (percentage)
        term_months: Loan term in months
        start_date: First payment date (YYYY-MM-DD)
        
    Returns:
        Amortization schedule
    """
    monthly_rate = annual_rate / 100 / 12
    
    if monthly_rate == 0:
        monthly_payment = principal / term_months
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**term_months) / \
                         ((1 + monthly_rate)**term_months - 1)
    
    if start_date:
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        current_date = datetime.now() + timedelta(days=30)
    
    schedule = []
    balance = principal
    total_interest = 0
    total_principal = 0
    
    for month in range(1, term_months + 1):
        interest_payment = balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        balance -= principal_payment
        
        total_interest += interest_payment
        total_principal += principal_payment
        
        schedule.append({
            "payment_number": month,
            "payment_date": current_date.strftime("%Y-%m-%d"),
            "payment_amount": round(monthly_payment, 2),
            "principal": round(principal_payment, 2),
            "interest": round(interest_payment, 2),
            "balance": round(max(0, balance), 2)
        })
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return {
        "loan_summary": {
            "principal": principal,
            "annual_rate": annual_rate,
            "term_months": term_months,
            "monthly_payment": round(monthly_payment, 2),
            "total_interest": round(total_interest, 2),
            "total_payment": round(principal + total_interest, 2)
        },
        "schedule": schedule[:12],  # Return first 12 months for brevity
        "total_payments": len(schedule)
    }


# =============================================================================
# TRANSACTION ANALYSIS TOOLS
# =============================================================================

def analyze_transaction(transaction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a single transaction for risk and patterns.
    
    Args:
        transaction: Transaction details
        
    Returns:
        Transaction analysis
    """
    risk_score = 0
    risk_flags = []
    
    amount = transaction.get("amount", 0)
    transaction_type = transaction.get("type", "")
    
    # Large transaction check
    if amount > 10000:
        risk_score += 20
        risk_flags.append("large_transaction")
    
    # Round amount check (potential structuring)
    if amount > 1000 and amount % 1000 == 0:
        risk_score += 10
        risk_flags.append("round_amount")
    
    # International transaction
    if transaction.get("is_international", False):
        risk_score += 15
        risk_flags.append("international_transaction")
    
    # High-risk country
    high_risk_countries = ["AF", "IR", "KP", "SY", "YE", "CU"]
    if transaction.get("destination_country", "") in high_risk_countries:
        risk_score += 30
        risk_flags.append("high_risk_country")
    
    # Unusual time
    transaction_time = transaction.get("time", "12:00")
    hour = int(transaction_time.split(":")[0])
    if hour < 6 or hour > 22:
        risk_score += 10
        risk_flags.append("unusual_time")
    
    # Cash transaction
    if transaction_type.lower() == "cash":
        risk_score += 15
        risk_flags.append("cash_transaction")
    
    return {
        "transaction_id": transaction.get("id", "unknown"),
        "risk_score": risk_score,
        "risk_level": "high" if risk_score >= 40 else "medium" if risk_score >= 20 else "low",
        "risk_flags": risk_flags,
        "requires_review": risk_score >= 30,
        "requires_sar": risk_score >= 50  # Suspicious Activity Report
    }


def detect_transaction_patterns(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Detect patterns in a list of transactions.
    
    Args:
        transactions: List of transaction records
        
    Returns:
        Pattern analysis
    """
    if not transactions:
        return {"error": "No transactions provided"}
    
    patterns = {
        "structuring": False,
        "velocity_anomaly": False,
        "round_amounts": False,
        "unusual_recipients": False
    }
    
    alerts = []
    
    # Calculate statistics
    amounts = [t.get("amount", 0) for t in transactions]
    avg_amount = sum(amounts) / len(amounts)
    
    # Structuring detection (multiple transactions just under reporting threshold)
    threshold_transactions = [t for t in transactions 
                             if 8000 <= t.get("amount", 0) < 10000]
    if len(threshold_transactions) >= 3:
        patterns["structuring"] = True
        alerts.append({
            "type": "structuring",
            "severity": "high",
            "description": f"{len(threshold_transactions)} transactions just under $10,000 threshold"
        })
    
    # Velocity check (too many transactions in short period)
    if len(transactions) > 10:
        patterns["velocity_anomaly"] = True
        alerts.append({
            "type": "velocity",
            "severity": "medium",
            "description": "High transaction frequency detected"
        })
    
    # Round amount pattern
    round_amounts = [t for t in transactions if t.get("amount", 0) % 1000 == 0]
    if len(round_amounts) > len(transactions) * 0.5:
        patterns["round_amounts"] = True
        alerts.append({
            "type": "round_amounts",
            "severity": "low",
            "description": "Majority of transactions are round amounts"
        })
    
    return {
        "transaction_count": len(transactions),
        "total_amount": sum(amounts),
        "average_amount": round(avg_amount, 2),
        "patterns_detected": patterns,
        "alerts": alerts,
        "recommendation": "manual_review" if any(patterns.values()) else "normal_processing"
    }


def calculate_transaction_limits(account_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate transaction limits based on account profile.
    
    Args:
        account_data: Account information
        
    Returns:
        Transaction limits
    """
    account_type = account_data.get("account_type", "personal")
    kyc_level = account_data.get("kyc_level", "basic")
    account_age_months = account_data.get("account_age_months", 0)
    
    base_limits = {
        "personal": {
            "daily": 5000,
            "monthly": 25000,
            "single": 2500
        },
        "business": {
            "daily": 50000,
            "monthly": 250000,
            "single": 25000
        },
        "premium": {
            "daily": 25000,
            "monthly": 100000,
            "single": 10000
        }
    }
    
    limits = base_limits.get(account_type, base_limits["personal"]).copy()
    
    # Adjust for KYC level
    kyc_multipliers = {"basic": 1.0, "standard": 1.5, "enhanced": 2.5}
    multiplier = kyc_multipliers.get(kyc_level, 1.0)
    
    # Adjust for account age
    if account_age_months >= 12:
        multiplier *= 1.5
    elif account_age_months >= 6:
        multiplier *= 1.25
    
    return {
        "account_type": account_type,
        "kyc_level": kyc_level,
        "limits": {
            "daily_limit": round(limits["daily"] * multiplier, 2),
            "monthly_limit": round(limits["monthly"] * multiplier, 2),
            "single_transaction_limit": round(limits["single"] * multiplier, 2)
        },
        "remaining_limits": {
            "daily": round(limits["daily"] * multiplier - account_data.get("daily_used", 0), 2),
            "monthly": round(limits["monthly"] * multiplier - account_data.get("monthly_used", 0), 2)
        }
    }


# =============================================================================
# COMPLIANCE TOOLS
# =============================================================================

def check_sanctions_list(entity_name: str, entity_type: str = "individual") -> Dict[str, Any]:
    """
    Check entity against sanctions lists.
    
    Args:
        entity_name: Name to check
        entity_type: Type of entity (individual, organization)
        
    Returns:
        Sanctions check result
    """
    # Simulated sanctions check (in production, would call actual sanctions database)
    name_normalized = entity_name.upper().strip()
    
    # Generate consistent mock result based on name
    hash_val = hash(name_normalized) % 100
    
    result = {
        "entity_name": entity_name,
        "entity_type": entity_type,
        "check_timestamp": datetime.utcnow().isoformat(),
        "lists_checked": [
            "OFAC SDN List",
            "UN Security Council",
            "EU Consolidated List",
            "UK HM Treasury"
        ],
        "matches_found": [],
        "status": "clear"
    }
    
    # For demo purposes, flag names starting with certain letters
    if name_normalized.startswith(("X", "Z")) or hash_val < 5:
        result["status"] = "potential_match"
        result["matches_found"].append({
            "list": "OFAC SDN List",
            "match_score": 85,
            "matched_name": name_normalized,
            "match_type": "fuzzy"
        })
    
    return result


def generate_aml_report(customer_id: str, transactions: List[Dict[str, Any]],
                       reporting_period: str = "monthly") -> Dict[str, Any]:
    """
    Generate Anti-Money Laundering report.
    
    Args:
        customer_id: Customer identifier
        transactions: List of transactions
        reporting_period: Report period type
        
    Returns:
        AML report
    """
    report = {
        "report_id": f"AML-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "customer_id": customer_id,
        "reporting_period": reporting_period,
        "generated_at": datetime.utcnow().isoformat(),
        "transaction_summary": {
            "total_count": len(transactions),
            "total_amount": sum(t.get("amount", 0) for t in transactions),
            "incoming": sum(1 for t in transactions if t.get("direction") == "in"),
            "outgoing": sum(1 for t in transactions if t.get("direction") == "out")
        },
        "risk_indicators": [],
        "alerts": [],
        "recommendation": "normal"
    }
    
    total_amount = report["transaction_summary"]["total_amount"]
    
    # Check for CTR requirement
    cash_total = sum(t.get("amount", 0) for t in transactions 
                    if t.get("type") == "cash")
    if cash_total > 10000:
        report["risk_indicators"].append({
            "indicator": "ctr_required",
            "description": f"Cash transactions exceed $10,000 (${cash_total})"
        })
        report["alerts"].append("Currency Transaction Report Required")
    
    # Check for suspicious patterns
    pattern_result = detect_transaction_patterns(transactions)
    if pattern_result.get("alerts"):
        report["risk_indicators"].extend([
            {"indicator": a["type"], "description": a["description"]}
            for a in pattern_result["alerts"]
        ])
        report["recommendation"] = "review"
    
    # High value check
    if total_amount > 100000:
        report["risk_indicators"].append({
            "indicator": "high_value",
            "description": f"Total transaction value exceeds $100,000"
        })
    
    if len(report["risk_indicators"]) > 2:
        report["recommendation"] = "sar_review"
    
    return report


def validate_regulatory_compliance(account_data: Dict[str, Any],
                                  regulation: str = "all") -> Dict[str, Any]:
    """
    Validate account against regulatory requirements.
    
    Args:
        account_data: Account information
        regulation: Specific regulation or 'all'
        
    Returns:
        Compliance validation result
    """
    compliance_checks = []
    
    # KYC compliance
    kyc_check = {
        "regulation": "KYC",
        "requirement": "Customer identification and verification",
        "status": "compliant" if account_data.get("kyc_verified") else "non_compliant",
        "details": []
    }
    
    if not account_data.get("identity_verified"):
        kyc_check["details"].append("Identity verification pending")
        kyc_check["status"] = "non_compliant"
    if not account_data.get("address_verified"):
        kyc_check["details"].append("Address verification pending")
    
    compliance_checks.append(kyc_check)
    
    # AML compliance
    aml_check = {
        "regulation": "AML",
        "requirement": "Anti-Money Laundering controls",
        "status": "compliant",
        "details": []
    }
    
    if not account_data.get("sanctions_checked"):
        aml_check["details"].append("Sanctions check not completed")
        aml_check["status"] = "non_compliant"
    if not account_data.get("pep_checked"):
        aml_check["details"].append("PEP screening not completed")
    
    compliance_checks.append(aml_check)
    
    # CDD compliance
    cdd_check = {
        "regulation": "CDD",
        "requirement": "Customer Due Diligence",
        "status": "compliant",
        "details": []
    }
    
    if account_data.get("risk_level") == "high" and not account_data.get("edd_completed"):
        cdd_check["details"].append("Enhanced Due Diligence required for high-risk customer")
        cdd_check["status"] = "non_compliant"
    
    compliance_checks.append(cdd_check)
    
    overall_status = "compliant" if all(c["status"] == "compliant" for c in compliance_checks) \
                     else "non_compliant"
    
    return {
        "account_id": account_data.get("account_id"),
        "assessment_date": datetime.utcnow().isoformat(),
        "overall_status": overall_status,
        "compliance_checks": compliance_checks,
        "required_actions": [c["details"] for c in compliance_checks if c["status"] != "compliant"]
    }


# =============================================================================
# REGISTER ALL BANKING TOOLS
# =============================================================================

def get_banking_tools() -> List[FunctionTool]:
    """
    Get all pre-built banking tools.
    
    Returns:
        List of FunctionTool instances
    """
    tools = []
    
    # KYC tools
    tools.append(FunctionTool.from_function(
        verify_identity_document,
        name="verify_identity_document",
        description="Verify identity document format and validity",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        calculate_kyc_risk_score,
        name="calculate_kyc_risk_score",
        description="Calculate KYC risk score based on customer data",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        verify_address,
        name="verify_address",
        description="Verify address format and completeness",
        category=ToolCategory.UTILITY
    ))
    
    # Credit tools
    tools.append(FunctionTool.from_function(
        calculate_credit_score,
        name="calculate_credit_score",
        description="Calculate credit score from credit history data",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        assess_debt_to_income,
        name="assess_debt_to_income",
        description="Calculate and assess debt-to-income ratio",
        category=ToolCategory.UTILITY
    ))
    
    # Loan tools
    tools.append(FunctionTool.from_function(
        calculate_loan_eligibility,
        name="calculate_loan_eligibility",
        description="Determine loan eligibility based on applicant data",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        generate_amortization_schedule,
        name="generate_amortization_schedule",
        description="Generate loan amortization schedule",
        category=ToolCategory.UTILITY
    ))
    
    # Transaction tools
    tools.append(FunctionTool.from_function(
        analyze_transaction,
        name="analyze_transaction",
        description="Analyze a transaction for risk and patterns",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        detect_transaction_patterns,
        name="detect_transaction_patterns",
        description="Detect patterns in transaction history",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        calculate_transaction_limits,
        name="calculate_transaction_limits",
        description="Calculate transaction limits for account",
        category=ToolCategory.UTILITY
    ))
    
    # Compliance tools
    tools.append(FunctionTool.from_function(
        check_sanctions_list,
        name="check_sanctions_list",
        description="Check entity against sanctions lists",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        generate_aml_report,
        name="generate_aml_report",
        description="Generate Anti-Money Laundering report",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        validate_regulatory_compliance,
        name="validate_regulatory_compliance",
        description="Validate account against regulatory requirements",
        category=ToolCategory.UTILITY
    ))
    
    return tools


def register_banking_tools(registry) -> int:
    """
    Register all banking tools with the registry.
    
    Args:
        registry: ToolsRegistry instance
        
    Returns:
        Number of tools registered
    """
    tools = get_banking_tools()
    count = 0
    for tool in tools:
        # Set source metadata to indicate prebuilt
        if tool.metadata:
            tool.metadata.source = f"prebuilt:banking:{tool.name}"
        if registry.register(tool):
            count += 1
    logger.info(f"Registered {count} banking tools")
    return count
