"""
Workflow Template Manager - Template library for workflow DAGs.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.

Version: 1.3.0
"""

import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class WorkflowTemplate:
    """Workflow template definition."""
    template_id: str
    name: str
    description: str
    category: str
    icon: str = "bi-diagram-3"
    difficulty: str = "intermediate"
    dag_definition: Dict[str, Any] = field(default_factory=dict)
    python_modules: List[str] = field(default_factory=list)
    sample_inputs: List[Dict[str, Any]] = field(default_factory=list)
    expected_outputs: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    is_system: bool = True
    created_by: str = "system"
    created_at: str = ""
    use_count: int = 0
    prerequisites: List[str] = field(default_factory=list)
    estimated_duration: str = "< 1 minute"
    industry: str = "General"
    uses_code_fragments: bool = False
    code_fragments: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WorkflowTemplateManager:
    """Manages workflow templates including built-in and custom templates."""
    
    def __init__(self, db_facade=None):
        """Initialize with optional database facade."""
        self.db_facade = db_facade
        self._templates: Dict[str, WorkflowTemplate] = {}
        self._init_builtin_templates()
        logger.info("WorkflowTemplateManager initialized")
    
    def _init_builtin_templates(self):
        """Initialize built-in workflow templates."""
        builtin = self._get_document_workflows() + \
                  self._get_data_workflows() + \
                  self._get_automation_workflows() + \
                  self._get_financial_workflows() + \
                  self._get_healthcare_workflows() + \
                  self._get_hr_workflows() + \
                  self._get_legal_workflows() + \
                  self._get_sales_workflows() + \
                  self._get_technology_workflows() + \
                  self._get_customer_service_workflows() + \
                  self._get_supply_chain_workflows()
        
        for template in builtin:
            from abhikarta.utils.helpers import get_timestamp
            template.created_at = get_timestamp()
            self._templates[template.template_id] = template
    
    def _get_document_workflows(self) -> List[WorkflowTemplate]:
        """Document processing workflows."""
        return [
            WorkflowTemplate(
                template_id="wf_tpl_document_summarizer",
                name="Document Summarizer",
                description="Extracts and summarizes key information from documents with customizable summary length and format.",
                category="Document Processing",
                icon="bi-file-earmark-text",
                difficulty="beginner",
                industry="General",
                estimated_duration="30 seconds",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Document Input"},
                        {"node_id": "extract", "node_type": "transform", "name": "Extract Text"},
                        {"node_id": "analyze", "node_type": "llm", "name": "Analyze Content"},
                        {"node_id": "summarize", "node_type": "llm", "name": "Generate Summary"},
                        {"node_id": "output", "node_type": "output", "name": "Summary Output"}
                    ],
                    "edges": [
                        {"source": "input", "target": "extract"},
                        {"source": "extract", "target": "analyze"},
                        {"source": "analyze", "target": "summarize"},
                        {"source": "summarize", "target": "output"}
                    ]
                },
                sample_inputs=[{"document": "sample_report.pdf", "summary_length": "short"}],
                expected_outputs=["Summary text", "Key points list", "Word count"],
                tags=["document", "summarization", "nlp", "beginner"],
                prerequisites=["LLM provider configured"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_pdf_data_extraction",
                name="PDF Data Extraction Pipeline",
                description="Extracts structured data from PDF documents using OCR and NLP. Supports tables, forms, and unstructured text.",
                category="Document Processing",
                icon="bi-file-earmark-pdf",
                difficulty="intermediate",
                industry="General",
                estimated_duration="1-2 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/pdf_table_extractor",
                    "s3://abhikarta-fragments/ocr_processor.py"
                ],
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "PDF Upload"},
                        {"node_id": "ocr", "node_type": "code_fragment", "name": "OCR Processing",
                         "config": {"fragment_uri": "s3://abhikarta-fragments/ocr_processor.py"}},
                        {"node_id": "table_extract", "node_type": "code_fragment", "name": "Table Extraction",
                         "config": {"fragment_uri": "db://code_fragments/pdf_table_extractor"}},
                        {"node_id": "structure", "node_type": "llm", "name": "Structure Data"},
                        {"node_id": "validate", "node_type": "transform", "name": "Validate Output"},
                        {"node_id": "output", "node_type": "output", "name": "Structured Data"}
                    ],
                    "edges": [
                        {"source": "input", "target": "ocr"},
                        {"source": "ocr", "target": "table_extract"},
                        {"source": "table_extract", "target": "structure"},
                        {"source": "structure", "target": "validate"},
                        {"source": "validate", "target": "output"}
                    ]
                },
                sample_inputs=[{"pdf_path": "invoice.pdf", "extract_tables": True}],
                expected_outputs=["Extracted text", "Table data as JSON", "Form fields"],
                tags=["pdf", "ocr", "extraction", "code-fragment"],
                prerequisites=["OCR library installed", "Code fragments configured in Admin > Code Fragments"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_invoice_processor",
                name="Invoice Processing Workflow",
                description="Automated invoice data extraction, validation, and entry into accounting systems.",
                category="Document Processing",
                icon="bi-receipt",
                difficulty="intermediate",
                industry="Finance",
                estimated_duration="1-3 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/invoice_parser",
                    "s3://abhikarta-fragments/accounting_api_client.py"
                ],
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Invoice Upload"},
                        {"node_id": "parse", "node_type": "code_fragment", "name": "Parse Invoice",
                         "config": {"fragment_uri": "db://code_fragments/invoice_parser"}},
                        {"node_id": "extract", "node_type": "llm", "name": "Extract Line Items"},
                        {"node_id": "validate", "node_type": "condition", "name": "Validate Amounts"},
                        {"node_id": "hitl", "node_type": "hitl", "name": "Review if Mismatch"},
                        {"node_id": "post", "node_type": "code_fragment", "name": "Post to Accounting",
                         "config": {"fragment_uri": "s3://abhikarta-fragments/accounting_api_client.py"}},
                        {"node_id": "output", "node_type": "output", "name": "Processing Result"}
                    ],
                    "edges": [
                        {"source": "input", "target": "parse"},
                        {"source": "parse", "target": "extract"},
                        {"source": "extract", "target": "validate"},
                        {"source": "validate", "target": "post", "condition": "valid"},
                        {"source": "validate", "target": "hitl", "condition": "needs_review"},
                        {"source": "hitl", "target": "post"},
                        {"source": "post", "target": "output"}
                    ]
                },
                sample_inputs=[{"invoice_file": "invoice_001.pdf", "vendor": "Acme Corp"}],
                expected_outputs=["Invoice ID", "Line items", "Total amount", "Posting status"],
                tags=["invoice", "finance", "automation", "code-fragment"],
                prerequisites=["Accounting system API access", "Code fragments configured in Admin > Code Fragments"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_document_classification",
                name="Document Classification",
                description="Automatically classifies documents by type, department, and priority.",
                category="Document Processing",
                icon="bi-folder2-open",
                difficulty="beginner",
                industry="General",
                estimated_duration="< 30 seconds",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Document"},
                        {"node_id": "extract", "node_type": "transform", "name": "Extract Features"},
                        {"node_id": "classify", "node_type": "llm", "name": "Classify Type"},
                        {"node_id": "route", "node_type": "condition", "name": "Route"},
                        {"node_id": "output", "node_type": "output", "name": "Classification"}
                    ],
                    "edges": [
                        {"source": "input", "target": "extract"},
                        {"source": "extract", "target": "classify"},
                        {"source": "classify", "target": "route"},
                        {"source": "route", "target": "output"}
                    ]
                },
                sample_inputs=[{"document": "file.pdf"}],
                expected_outputs=["Document type", "Department", "Priority"],
                tags=["classification", "document", "beginner"]
            )
        ]
    
    def _get_data_workflows(self) -> List[WorkflowTemplate]:
        """Data processing workflows."""
        return [
            WorkflowTemplate(
                template_id="wf_tpl_etl_pipeline",
                name="Data ETL Pipeline",
                description="Extract, Transform, Load pipeline for data processing with support for multiple data sources.",
                category="Data Processing",
                icon="bi-arrow-left-right",
                difficulty="intermediate",
                industry="General",
                estimated_duration="2-5 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/data_extractor",
                    "s3://abhikarta-fragments/data_transformer.py",
                    "db://code_fragments/data_loader"
                ],
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Data Source Config"},
                        {"node_id": "extract", "node_type": "code_fragment", "name": "Extract Data",
                         "config": {"fragment_uri": "db://code_fragments/data_extractor"}},
                        {"node_id": "validate", "node_type": "transform", "name": "Validate Schema"},
                        {"node_id": "transform", "node_type": "code_fragment", "name": "Transform Data",
                         "config": {"fragment_uri": "s3://abhikarta-fragments/data_transformer.py"}},
                        {"node_id": "load", "node_type": "code_fragment", "name": "Load to Target",
                         "config": {"fragment_uri": "db://code_fragments/data_loader"}},
                        {"node_id": "output", "node_type": "output", "name": "ETL Result"}
                    ],
                    "edges": [
                        {"source": "input", "target": "extract"},
                        {"source": "extract", "target": "validate"},
                        {"source": "validate", "target": "transform"},
                        {"source": "transform", "target": "load"},
                        {"source": "load", "target": "output"}
                    ]
                },
                sample_inputs=[{"source": "postgres://db/sales", "target": "snowflake://warehouse/analytics"}],
                expected_outputs=["Records processed", "Transformation log", "Load status"],
                tags=["etl", "data", "pipeline", "code-fragment"],
                prerequisites=["Database connections configured", "Code fragments configured in Admin > Code Fragments"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_csv_analyzer",
                name="CSV Data Analyzer",
                description="Analyzes CSV data files, generates statistics, identifies patterns, and creates visualizations.",
                category="Data Processing",
                icon="bi-file-earmark-spreadsheet",
                difficulty="beginner",
                industry="General",
                estimated_duration="30 seconds",
                uses_code_fragments=True,
                code_fragments=["db://code_fragments/pandas_analyzer"],
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "CSV Upload"},
                        {"node_id": "parse", "node_type": "code_fragment", "name": "Parse CSV",
                         "config": {"fragment_uri": "db://code_fragments/pandas_analyzer"}},
                        {"node_id": "stats", "node_type": "transform", "name": "Generate Statistics"},
                        {"node_id": "analyze", "node_type": "llm", "name": "Interpret Patterns"},
                        {"node_id": "output", "node_type": "output", "name": "Analysis Report"}
                    ],
                    "edges": [
                        {"source": "input", "target": "parse"},
                        {"source": "parse", "target": "stats"},
                        {"source": "stats", "target": "analyze"},
                        {"source": "analyze", "target": "output"}
                    ]
                },
                sample_inputs=[{"csv_file": "sales_data.csv", "analysis_type": "full"}],
                expected_outputs=["Summary statistics", "Column analysis", "Pattern insights"],
                tags=["csv", "analysis", "pandas", "code-fragment", "beginner"],
                prerequisites=["Pandas code fragment configured in Admin > Code Fragments"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_data_quality_check",
                name="Data Quality Checker",
                description="Comprehensive data quality assessment including completeness, accuracy, and consistency checks.",
                category="Data Processing",
                icon="bi-check2-all",
                difficulty="intermediate",
                industry="General",
                estimated_duration="1-3 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/data_quality_rules",
                    "s3://abhikarta-fragments/quality_reporter.py"
                ],
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Data Input"},
                        {"node_id": "profile", "node_type": "code_fragment", "name": "Data Profiling",
                         "config": {"fragment_uri": "db://code_fragments/data_quality_rules"}},
                        {"node_id": "completeness", "node_type": "transform", "name": "Check Completeness"},
                        {"node_id": "accuracy", "node_type": "transform", "name": "Check Accuracy"},
                        {"node_id": "consistency", "node_type": "transform", "name": "Check Consistency"},
                        {"node_id": "report", "node_type": "code_fragment", "name": "Generate Report",
                         "config": {"fragment_uri": "s3://abhikarta-fragments/quality_reporter.py"}},
                        {"node_id": "output", "node_type": "output", "name": "Quality Report"}
                    ],
                    "edges": [
                        {"source": "input", "target": "profile"},
                        {"source": "profile", "target": "completeness"},
                        {"source": "completeness", "target": "accuracy"},
                        {"source": "accuracy", "target": "consistency"},
                        {"source": "consistency", "target": "report"},
                        {"source": "report", "target": "output"}
                    ]
                },
                sample_inputs=[{"dataset": "customer_data", "rules": ["not_null", "unique_id"]}],
                expected_outputs=["Quality score", "Issue breakdown", "Recommendations"],
                tags=["quality", "validation", "data-governance", "code-fragment"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_json_transformer",
                name="JSON Data Transformer",
                description="Transforms JSON data between different schemas with validation and mapping rules.",
                category="Data Processing",
                icon="bi-braces",
                difficulty="beginner",
                industry="General",
                estimated_duration="< 30 seconds",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "JSON Input"},
                        {"node_id": "validate", "node_type": "transform", "name": "Validate Schema"},
                        {"node_id": "map", "node_type": "transform", "name": "Apply Mapping"},
                        {"node_id": "transform", "node_type": "llm", "name": "Enrich Data"},
                        {"node_id": "output", "node_type": "output", "name": "Transformed JSON"}
                    ],
                    "edges": [
                        {"source": "input", "target": "validate"},
                        {"source": "validate", "target": "map"},
                        {"source": "map", "target": "transform"},
                        {"source": "transform", "target": "output"}
                    ]
                },
                sample_inputs=[{"json_data": {"old_format": "data"}, "target_schema": "v2"}],
                expected_outputs=["Transformed JSON", "Validation report"],
                tags=["json", "transformation", "schema", "beginner"]
            )
        ]
    
    def _get_automation_workflows(self) -> List[WorkflowTemplate]:
        """Automation workflows."""
        return [
            WorkflowTemplate(
                template_id="wf_tpl_email_classifier",
                name="Email Classification & Routing",
                description="Classifies incoming emails by intent and routes them to appropriate handlers or departments.",
                category="Automation",
                icon="bi-envelope-open",
                difficulty="beginner",
                industry="General",
                estimated_duration="< 30 seconds",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Email Input"},
                        {"node_id": "extract", "node_type": "transform", "name": "Extract Content"},
                        {"node_id": "classify", "node_type": "llm", "name": "Classify Intent"},
                        {"node_id": "route", "node_type": "condition", "name": "Route Decision"},
                        {"node_id": "support", "node_type": "tool", "name": "Support Queue"},
                        {"node_id": "sales", "node_type": "tool", "name": "Sales Queue"},
                        {"node_id": "general", "node_type": "tool", "name": "General Queue"},
                        {"node_id": "output", "node_type": "output", "name": "Routing Result"}
                    ],
                    "edges": [
                        {"source": "input", "target": "extract"},
                        {"source": "extract", "target": "classify"},
                        {"source": "classify", "target": "route"},
                        {"source": "route", "target": "support", "condition": "support"},
                        {"source": "route", "target": "sales", "condition": "sales"},
                        {"source": "route", "target": "general", "condition": "default"},
                        {"source": "support", "target": "output"},
                        {"source": "sales", "target": "output"},
                        {"source": "general", "target": "output"}
                    ]
                },
                sample_inputs=[{"email_subject": "Need help with order", "email_body": "..."}],
                expected_outputs=["Classification label", "Confidence score", "Routed queue"],
                tags=["email", "classification", "routing", "automation", "beginner"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_report_generator",
                name="Automated Report Generator",
                description="Generates comprehensive reports from data sources with charts and insights.",
                category="Automation",
                icon="bi-file-earmark-bar-graph",
                difficulty="intermediate",
                industry="General",
                estimated_duration="2-5 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/chart_generator",
                    "s3://abhikarta-fragments/report_formatter.py"
                ],
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Report Config"},
                        {"node_id": "fetch", "node_type": "tool", "name": "Fetch Data"},
                        {"node_id": "analyze", "node_type": "llm", "name": "Analyze Trends"},
                        {"node_id": "charts", "node_type": "code_fragment", "name": "Generate Charts",
                         "config": {"fragment_uri": "db://code_fragments/chart_generator"}},
                        {"node_id": "format", "node_type": "code_fragment", "name": "Format Report",
                         "config": {"fragment_uri": "s3://abhikarta-fragments/report_formatter.py"}},
                        {"node_id": "output", "node_type": "output", "name": "Report Output"}
                    ],
                    "edges": [
                        {"source": "input", "target": "fetch"},
                        {"source": "fetch", "target": "analyze"},
                        {"source": "analyze", "target": "charts"},
                        {"source": "charts", "target": "format"},
                        {"source": "format", "target": "output"}
                    ]
                },
                sample_inputs=[{"report_type": "monthly_sales", "date_range": "2024-01"}],
                expected_outputs=["PDF report", "Executive summary", "Charts"],
                tags=["reporting", "analytics", "charts", "code-fragment"],
                prerequisites=["Data sources configured", "Code fragments configured in Admin > Code Fragments"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_web_scraper",
                name="Intelligent Web Scraper",
                description="Scrapes web content with intelligent parsing and data extraction using LLM.",
                category="Automation",
                icon="bi-globe",
                difficulty="intermediate",
                industry="General",
                estimated_duration="1-5 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/web_scraper",
                    "file:///opt/abhikarta/fragments/html_parser.py"
                ],
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "URL Input"},
                        {"node_id": "fetch", "node_type": "code_fragment", "name": "Fetch Page",
                         "config": {"fragment_uri": "db://code_fragments/web_scraper"}},
                        {"node_id": "parse", "node_type": "code_fragment", "name": "Parse HTML",
                         "config": {"fragment_uri": "file:///opt/abhikarta/fragments/html_parser.py"}},
                        {"node_id": "extract", "node_type": "llm", "name": "Extract Data"},
                        {"node_id": "structure", "node_type": "transform", "name": "Structure Output"},
                        {"node_id": "output", "node_type": "output", "name": "Scraped Data"}
                    ],
                    "edges": [
                        {"source": "input", "target": "fetch"},
                        {"source": "fetch", "target": "parse"},
                        {"source": "parse", "target": "extract"},
                        {"source": "extract", "target": "structure"},
                        {"source": "structure", "target": "output"}
                    ]
                },
                sample_inputs=[{"url": "https://example.com/products", "extract_fields": ["name", "price"]}],
                expected_outputs=["Structured data", "Raw text", "Metadata"],
                tags=["scraping", "web", "extraction", "code-fragment"],
                prerequisites=["Code fragments configured in Admin > Code Fragments"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_content_moderation",
                name="Content Moderation Pipeline",
                description="Automated content moderation for user-generated content with multi-stage review process.",
                category="Automation",
                icon="bi-shield-check",
                difficulty="intermediate",
                industry="General",
                estimated_duration="< 30 seconds",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Content Input"},
                        {"node_id": "prefilter", "node_type": "transform", "name": "Keyword Filter"},
                        {"node_id": "analyze", "node_type": "llm", "name": "AI Analysis"},
                        {"node_id": "score", "node_type": "transform", "name": "Risk Scoring"},
                        {"node_id": "decide", "node_type": "condition", "name": "Moderation Decision"},
                        {"node_id": "approve", "node_type": "output", "name": "Auto Approve"},
                        {"node_id": "review", "node_type": "hitl", "name": "Human Review"},
                        {"node_id": "reject", "node_type": "output", "name": "Auto Reject"}
                    ],
                    "edges": [
                        {"source": "input", "target": "prefilter"},
                        {"source": "prefilter", "target": "analyze"},
                        {"source": "analyze", "target": "score"},
                        {"source": "score", "target": "decide"},
                        {"source": "decide", "target": "approve", "condition": "safe"},
                        {"source": "decide", "target": "review", "condition": "uncertain"},
                        {"source": "decide", "target": "reject", "condition": "unsafe"}
                    ]
                },
                sample_inputs=[{"content": "User comment text", "content_type": "comment"}],
                expected_outputs=["Moderation status", "Risk score", "Flagged categories"],
                tags=["moderation", "safety", "content", "hitl"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_notification_dispatcher",
                name="Multi-Channel Notification Dispatcher",
                description="Sends notifications across multiple channels (email, SMS, push, Slack) based on rules.",
                category="Automation",
                icon="bi-bell",
                difficulty="beginner",
                industry="General",
                estimated_duration="< 30 seconds",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Notification Request"},
                        {"node_id": "template", "node_type": "llm", "name": "Generate Message"},
                        {"node_id": "channels", "node_type": "condition", "name": "Select Channels"},
                        {"node_id": "email", "node_type": "tool", "name": "Send Email"},
                        {"node_id": "sms", "node_type": "tool", "name": "Send SMS"},
                        {"node_id": "slack", "node_type": "tool", "name": "Send Slack"},
                        {"node_id": "output", "node_type": "output", "name": "Delivery Status"}
                    ],
                    "edges": [
                        {"source": "input", "target": "template"},
                        {"source": "template", "target": "channels"},
                        {"source": "channels", "target": "email", "condition": "email"},
                        {"source": "channels", "target": "sms", "condition": "sms"},
                        {"source": "channels", "target": "slack", "condition": "slack"},
                        {"source": "email", "target": "output"},
                        {"source": "sms", "target": "output"},
                        {"source": "slack", "target": "output"}
                    ]
                },
                sample_inputs=[{"event": "order_shipped", "user_id": "12345", "channels": ["email", "sms"]}],
                expected_outputs=["Delivery confirmations", "Failure reasons if any"],
                tags=["notifications", "messaging", "multi-channel", "beginner"]
            )
        ]
    
    def _get_financial_workflows(self) -> List[WorkflowTemplate]:
        """Financial processing workflows."""
        return [
            WorkflowTemplate(
                template_id="wf_tpl_loan_application",
                name="Loan Application Processing",
                description="End-to-end loan application processing with credit checks, risk assessment, and approval workflow.",
                category="Financial Processing",
                icon="bi-bank",
                difficulty="advanced",
                industry="Banking",
                estimated_duration="5-10 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "s3://banking-fragments/credit_score_api.py",
                    "db://code_fragments/risk_calculator"
                ],
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Application Data"},
                        {"node_id": "validate", "node_type": "transform", "name": "Validate Application"},
                        {"node_id": "credit", "node_type": "code_fragment", "name": "Credit Check",
                         "config": {"fragment_uri": "s3://banking-fragments/credit_score_api.py"}},
                        {"node_id": "income", "node_type": "tool", "name": "Verify Income"},
                        {"node_id": "risk", "node_type": "code_fragment", "name": "Risk Assessment",
                         "config": {"fragment_uri": "db://code_fragments/risk_calculator"}},
                        {"node_id": "decision", "node_type": "llm", "name": "Initial Decision"},
                        {"node_id": "review", "node_type": "condition", "name": "Review Needed?"},
                        {"node_id": "hitl", "node_type": "hitl", "name": "Underwriter Review"},
                        {"node_id": "approval", "node_type": "output", "name": "Approval Decision"}
                    ],
                    "edges": [
                        {"source": "input", "target": "validate"},
                        {"source": "validate", "target": "credit"},
                        {"source": "credit", "target": "income"},
                        {"source": "income", "target": "risk"},
                        {"source": "risk", "target": "decision"},
                        {"source": "decision", "target": "review"},
                        {"source": "review", "target": "approval", "condition": "auto_approve"},
                        {"source": "review", "target": "hitl", "condition": "needs_review"},
                        {"source": "hitl", "target": "approval"}
                    ]
                },
                sample_inputs=[{"applicant_id": "A123", "loan_amount": 50000, "loan_type": "personal"}],
                expected_outputs=["Approval status", "Interest rate", "Terms", "Risk score"],
                tags=["lending", "banking", "credit", "hitl", "code-fragment"],
                prerequisites=["Credit bureau API access", "Code fragments configured in Admin > Code Fragments"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_fraud_detection",
                name="Real-Time Fraud Detection",
                description="Real-time transaction fraud detection using ML models and rule-based checks.",
                category="Financial Processing",
                icon="bi-shield-exclamation",
                difficulty="advanced",
                industry="Banking",
                estimated_duration="< 5 seconds",
                uses_code_fragments=True,
                code_fragments=[
                    "s3://ml-models/fraud_ml_model.py",
                    "db://code_fragments/velocity_checker"
                ],
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Transaction"},
                        {"node_id": "enrich", "node_type": "transform", "name": "Enrich Data"},
                        {"node_id": "rules", "node_type": "code_fragment", "name": "Rule Engine",
                         "config": {"fragment_uri": "db://code_fragments/velocity_checker"}},
                        {"node_id": "ml", "node_type": "code_fragment", "name": "ML Scoring",
                         "config": {"fragment_uri": "s3://ml-models/fraud_ml_model.py"}},
                        {"node_id": "combine", "node_type": "transform", "name": "Combine Scores"},
                        {"node_id": "decide", "node_type": "condition", "name": "Decision"},
                        {"node_id": "approve", "node_type": "output", "name": "Approve"},
                        {"node_id": "review", "node_type": "hitl", "name": "Manual Review"},
                        {"node_id": "block", "node_type": "output", "name": "Block"}
                    ],
                    "edges": [
                        {"source": "input", "target": "enrich"},
                        {"source": "enrich", "target": "rules"},
                        {"source": "enrich", "target": "ml"},
                        {"source": "rules", "target": "combine"},
                        {"source": "ml", "target": "combine"},
                        {"source": "combine", "target": "decide"},
                        {"source": "decide", "target": "approve", "condition": "low_risk"},
                        {"source": "decide", "target": "review", "condition": "medium_risk"},
                        {"source": "decide", "target": "block", "condition": "high_risk"}
                    ]
                },
                sample_inputs=[{"transaction_id": "T123", "amount": 5000, "merchant": "Online Store"}],
                expected_outputs=["Decision", "Fraud score", "Triggered rules"],
                tags=["fraud", "ml", "real-time", "banking", "code-fragment"],
                prerequisites=["ML model deployed", "Code fragments configured in Admin > Code Fragments"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_kyc_verification",
                name="KYC/AML Verification",
                description="Know Your Customer and Anti-Money Laundering verification workflow.",
                category="Financial Processing",
                icon="bi-person-check",
                difficulty="advanced",
                industry="Banking",
                estimated_duration="5-15 minutes",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Customer Data"},
                        {"node_id": "id_verify", "node_type": "tool", "name": "ID Verification"},
                        {"node_id": "address_verify", "node_type": "tool", "name": "Address Verification"},
                        {"node_id": "sanctions", "node_type": "tool", "name": "Sanctions Check"},
                        {"node_id": "pep", "node_type": "tool", "name": "PEP Screening"},
                        {"node_id": "risk_score", "node_type": "llm", "name": "Risk Assessment"},
                        {"node_id": "decision", "node_type": "condition", "name": "KYC Decision"},
                        {"node_id": "approve", "node_type": "output", "name": "Approved"},
                        {"node_id": "review", "node_type": "hitl", "name": "Compliance Review"},
                        {"node_id": "reject", "node_type": "output", "name": "Rejected"}
                    ],
                    "edges": [
                        {"source": "input", "target": "id_verify"},
                        {"source": "id_verify", "target": "address_verify"},
                        {"source": "address_verify", "target": "sanctions"},
                        {"source": "sanctions", "target": "pep"},
                        {"source": "pep", "target": "risk_score"},
                        {"source": "risk_score", "target": "decision"},
                        {"source": "decision", "target": "approve", "condition": "pass"},
                        {"source": "decision", "target": "review", "condition": "review"},
                        {"source": "decision", "target": "reject", "condition": "fail"}
                    ]
                },
                sample_inputs=[{"customer_id": "C123", "id_document": "passport.jpg"}],
                expected_outputs=["KYC status", "Risk level", "Verification details"],
                tags=["kyc", "aml", "compliance", "banking", "hitl"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_payment_processing",
                name="Payment Processing Pipeline",
                description="End-to-end payment processing with validation, routing, and settlement.",
                category="Financial Processing",
                icon="bi-credit-card",
                difficulty="intermediate",
                industry="Banking",
                estimated_duration="< 30 seconds",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Payment Request"},
                        {"node_id": "validate", "node_type": "transform", "name": "Validate Payment"},
                        {"node_id": "balance", "node_type": "tool", "name": "Check Balance"},
                        {"node_id": "route", "node_type": "condition", "name": "Route Payment"},
                        {"node_id": "domestic", "node_type": "tool", "name": "Domestic Transfer"},
                        {"node_id": "international", "node_type": "tool", "name": "SWIFT Transfer"},
                        {"node_id": "settle", "node_type": "transform", "name": "Settlement"},
                        {"node_id": "output", "node_type": "output", "name": "Payment Status"}
                    ],
                    "edges": [
                        {"source": "input", "target": "validate"},
                        {"source": "validate", "target": "balance"},
                        {"source": "balance", "target": "route"},
                        {"source": "route", "target": "domestic", "condition": "domestic"},
                        {"source": "route", "target": "international", "condition": "international"},
                        {"source": "domestic", "target": "settle"},
                        {"source": "international", "target": "settle"},
                        {"source": "settle", "target": "output"}
                    ]
                },
                sample_inputs=[{"from_account": "1234", "to_account": "5678", "amount": 1000}],
                expected_outputs=["Transaction ID", "Status", "Settlement time"],
                tags=["payments", "transfers", "banking"]
            )
        ]
    
    def _get_healthcare_workflows(self) -> List[WorkflowTemplate]:
        """Healthcare workflows."""
        return [
            WorkflowTemplate(
                template_id="wf_tpl_patient_intake",
                name="Patient Intake Processing",
                description="Digital patient intake with form processing, insurance verification, and appointment scheduling.",
                category="Healthcare",
                icon="bi-hospital",
                difficulty="intermediate",
                industry="Healthcare",
                estimated_duration="5-10 minutes",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Patient Forms"},
                        {"node_id": "extract", "node_type": "llm", "name": "Extract Information"},
                        {"node_id": "verify_insurance", "node_type": "tool", "name": "Verify Insurance"},
                        {"node_id": "medical_history", "node_type": "transform", "name": "Process History"},
                        {"node_id": "risk_assess", "node_type": "llm", "name": "Risk Assessment"},
                        {"node_id": "schedule", "node_type": "tool", "name": "Schedule Appointment"},
                        {"node_id": "output", "node_type": "output", "name": "Intake Complete"}
                    ],
                    "edges": [
                        {"source": "input", "target": "extract"},
                        {"source": "extract", "target": "verify_insurance"},
                        {"source": "verify_insurance", "target": "medical_history"},
                        {"source": "medical_history", "target": "risk_assess"},
                        {"source": "risk_assess", "target": "schedule"},
                        {"source": "schedule", "target": "output"}
                    ]
                },
                sample_inputs=[{"patient_name": "John Doe", "insurance_id": "INS123"}],
                expected_outputs=["Patient record", "Insurance status", "Appointment confirmation"],
                tags=["healthcare", "patient", "intake"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_claims_processing",
                name="Insurance Claims Processing",
                description="Automated insurance claims processing with validation, adjudication, and payment.",
                category="Healthcare",
                icon="bi-file-medical",
                difficulty="advanced",
                industry="Healthcare",
                estimated_duration="10-30 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/claims_adjudicator",
                    "s3://healthcare-fragments/payment_calculator.py"
                ],
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Claim Submission"},
                        {"node_id": "validate", "node_type": "transform", "name": "Validate Claim"},
                        {"node_id": "eligibility", "node_type": "tool", "name": "Check Eligibility"},
                        {"node_id": "coding", "node_type": "llm", "name": "Verify Coding"},
                        {"node_id": "adjudicate", "node_type": "code_fragment", "name": "Adjudicate",
                         "config": {"fragment_uri": "db://code_fragments/claims_adjudicator"}},
                        {"node_id": "calculate", "node_type": "code_fragment", "name": "Calculate Payment",
                         "config": {"fragment_uri": "s3://healthcare-fragments/payment_calculator.py"}},
                        {"node_id": "review", "node_type": "condition", "name": "Review Needed?"},
                        {"node_id": "hitl", "node_type": "hitl", "name": "Manual Review"},
                        {"node_id": "payment", "node_type": "tool", "name": "Process Payment"},
                        {"node_id": "output", "node_type": "output", "name": "Claim Result"}
                    ],
                    "edges": [
                        {"source": "input", "target": "validate"},
                        {"source": "validate", "target": "eligibility"},
                        {"source": "eligibility", "target": "coding"},
                        {"source": "coding", "target": "adjudicate"},
                        {"source": "adjudicate", "target": "calculate"},
                        {"source": "calculate", "target": "review"},
                        {"source": "review", "target": "payment", "condition": "auto"},
                        {"source": "review", "target": "hitl", "condition": "manual"},
                        {"source": "hitl", "target": "payment"},
                        {"source": "payment", "target": "output"}
                    ]
                },
                sample_inputs=[{"claim_id": "CLM123", "procedure_code": "99213"}],
                expected_outputs=["Claim status", "Payment amount", "Denial reason if any"],
                tags=["claims", "insurance", "healthcare", "hitl", "code-fragment"],
                prerequisites=["Code fragments configured in Admin > Code Fragments"]
            )
        ]
    
    def _get_hr_workflows(self) -> List[WorkflowTemplate]:
        """HR workflows."""
        return [
            WorkflowTemplate(
                template_id="wf_tpl_resume_screening",
                name="AI Resume Screening",
                description="Automated resume screening with skill matching and candidate ranking.",
                category="Human Resources",
                icon="bi-file-person",
                difficulty="intermediate",
                industry="HR",
                estimated_duration="1-2 minutes per resume",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/resume_parser",
                    "s3://hr-fragments/skill_matcher.py"
                ],
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Resume Upload"},
                        {"node_id": "parse", "node_type": "code_fragment", "name": "Parse Resume",
                         "config": {"fragment_uri": "db://code_fragments/resume_parser"}},
                        {"node_id": "extract", "node_type": "llm", "name": "Extract Skills"},
                        {"node_id": "match", "node_type": "code_fragment", "name": "Match Requirements",
                         "config": {"fragment_uri": "s3://hr-fragments/skill_matcher.py"}},
                        {"node_id": "score", "node_type": "transform", "name": "Calculate Score"},
                        {"node_id": "rank", "node_type": "llm", "name": "Rank Candidate"},
                        {"node_id": "output", "node_type": "output", "name": "Screening Result"}
                    ],
                    "edges": [
                        {"source": "input", "target": "parse"},
                        {"source": "parse", "target": "extract"},
                        {"source": "extract", "target": "match"},
                        {"source": "match", "target": "score"},
                        {"source": "score", "target": "rank"},
                        {"source": "rank", "target": "output"}
                    ]
                },
                sample_inputs=[{"resume_file": "candidate.pdf", "job_id": "JOB123"}],
                expected_outputs=["Match score", "Skill gaps", "Recommendation"],
                tags=["recruiting", "resume", "hr", "code-fragment"],
                prerequisites=["Code fragments configured in Admin > Code Fragments"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_onboarding",
                name="Employee Onboarding Workflow",
                description="Comprehensive employee onboarding with task management and compliance tracking.",
                category="Human Resources",
                icon="bi-person-plus",
                difficulty="beginner",
                industry="HR",
                estimated_duration="Spans multiple days",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "New Hire Data"},
                        {"node_id": "accounts", "node_type": "tool", "name": "Create Accounts"},
                        {"node_id": "equipment", "node_type": "tool", "name": "Order Equipment"},
                        {"node_id": "docs", "node_type": "llm", "name": "Generate Documents"},
                        {"node_id": "training", "node_type": "tool", "name": "Assign Training"},
                        {"node_id": "notify", "node_type": "tool", "name": "Notify Stakeholders"},
                        {"node_id": "output", "node_type": "output", "name": "Onboarding Status"}
                    ],
                    "edges": [
                        {"source": "input", "target": "accounts"},
                        {"source": "input", "target": "equipment"},
                        {"source": "input", "target": "docs"},
                        {"source": "accounts", "target": "training"},
                        {"source": "equipment", "target": "notify"},
                        {"source": "docs", "target": "notify"},
                        {"source": "training", "target": "output"},
                        {"source": "notify", "target": "output"}
                    ]
                },
                sample_inputs=[{"employee_name": "Jane Smith", "start_date": "2024-02-01", "department": "Engineering"}],
                expected_outputs=["Account credentials", "Equipment order", "Training schedule"],
                tags=["onboarding", "hr", "employee", "beginner"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_expense_approval",
                name="Expense Approval Workflow",
                description="Multi-level expense approval workflow with policy checks and budget validation.",
                category="Human Resources",
                icon="bi-receipt-cutoff",
                difficulty="beginner",
                industry="HR",
                estimated_duration="1-5 minutes",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Expense Claim"},
                        {"node_id": "validate", "node_type": "transform", "name": "Validate Receipts"},
                        {"node_id": "policy", "node_type": "llm", "name": "Check Policy"},
                        {"node_id": "budget", "node_type": "tool", "name": "Check Budget"},
                        {"node_id": "route", "node_type": "condition", "name": "Approval Route"},
                        {"node_id": "auto_approve", "node_type": "output", "name": "Auto Approve"},
                        {"node_id": "manager", "node_type": "hitl", "name": "Manager Approval"},
                        {"node_id": "finance", "node_type": "hitl", "name": "Finance Approval"},
                        {"node_id": "output", "node_type": "output", "name": "Approval Status"}
                    ],
                    "edges": [
                        {"source": "input", "target": "validate"},
                        {"source": "validate", "target": "policy"},
                        {"source": "policy", "target": "budget"},
                        {"source": "budget", "target": "route"},
                        {"source": "route", "target": "auto_approve", "condition": "under_limit"},
                        {"source": "route", "target": "manager", "condition": "manager_approval"},
                        {"source": "route", "target": "finance", "condition": "finance_approval"},
                        {"source": "manager", "target": "output"},
                        {"source": "finance", "target": "output"}
                    ]
                },
                sample_inputs=[{"employee_id": "E123", "amount": 500, "category": "travel"}],
                expected_outputs=["Approval status", "Approver", "Reimbursement date"],
                tags=["expenses", "approval", "hr", "hitl", "beginner"]
            )
        ]
    
    def _get_legal_workflows(self) -> List[WorkflowTemplate]:
        """Legal workflows."""
        return [
            WorkflowTemplate(
                template_id="wf_tpl_contract_review",
                name="Contract Review Pipeline",
                description="AI-assisted contract review with clause extraction, risk identification, and redlining.",
                category="Legal",
                icon="bi-file-earmark-ruled",
                difficulty="advanced",
                industry="Legal",
                estimated_duration="10-30 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/contract_parser",
                    "s3://legal-fragments/clause_extractor.py"
                ],
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Contract Document"},
                        {"node_id": "parse", "node_type": "code_fragment", "name": "Parse Contract",
                         "config": {"fragment_uri": "db://code_fragments/contract_parser"}},
                        {"node_id": "extract", "node_type": "code_fragment", "name": "Extract Clauses",
                         "config": {"fragment_uri": "s3://legal-fragments/clause_extractor.py"}},
                        {"node_id": "analyze", "node_type": "llm", "name": "Analyze Terms"},
                        {"node_id": "risk", "node_type": "llm", "name": "Identify Risks"},
                        {"node_id": "compare", "node_type": "tool", "name": "Compare Playbook"},
                        {"node_id": "redline", "node_type": "llm", "name": "Generate Redlines"},
                        {"node_id": "review", "node_type": "hitl", "name": "Attorney Review"},
                        {"node_id": "output", "node_type": "output", "name": "Review Report"}
                    ],
                    "edges": [
                        {"source": "input", "target": "parse"},
                        {"source": "parse", "target": "extract"},
                        {"source": "extract", "target": "analyze"},
                        {"source": "analyze", "target": "risk"},
                        {"source": "risk", "target": "compare"},
                        {"source": "compare", "target": "redline"},
                        {"source": "redline", "target": "review"},
                        {"source": "review", "target": "output"}
                    ]
                },
                sample_inputs=[{"contract_file": "nda.pdf", "contract_type": "NDA"}],
                expected_outputs=["Clause summary", "Risk assessment", "Suggested redlines"],
                tags=["contracts", "legal", "review", "hitl", "code-fragment"],
                prerequisites=["Code fragments configured in Admin > Code Fragments"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_compliance_check",
                name="Regulatory Compliance Checker",
                description="Automated compliance checking against regulatory requirements with gap analysis.",
                category="Legal",
                icon="bi-clipboard-check",
                difficulty="intermediate",
                industry="Legal",
                estimated_duration="5-10 minutes",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Policy Document"},
                        {"node_id": "extract", "node_type": "llm", "name": "Extract Requirements"},
                        {"node_id": "map", "node_type": "tool", "name": "Map to Regulations"},
                        {"node_id": "analyze", "node_type": "llm", "name": "Gap Analysis"},
                        {"node_id": "recommend", "node_type": "llm", "name": "Recommendations"},
                        {"node_id": "review", "node_type": "hitl", "name": "Compliance Review"},
                        {"node_id": "output", "node_type": "output", "name": "Compliance Report"}
                    ],
                    "edges": [
                        {"source": "input", "target": "extract"},
                        {"source": "extract", "target": "map"},
                        {"source": "map", "target": "analyze"},
                        {"source": "analyze", "target": "recommend"},
                        {"source": "recommend", "target": "review"},
                        {"source": "review", "target": "output"}
                    ]
                },
                sample_inputs=[{"document": "privacy_policy.pdf", "regulations": ["GDPR", "CCPA"]}],
                expected_outputs=["Compliance score", "Gap list", "Remediation steps"],
                tags=["compliance", "regulatory", "legal", "hitl"]
            )
        ]
    
    def _get_sales_workflows(self) -> List[WorkflowTemplate]:
        """Sales & Marketing workflows."""
        return [
            WorkflowTemplate(
                template_id="wf_tpl_lead_scoring",
                name="Lead Scoring & Routing",
                description="AI-powered lead scoring with automatic routing to appropriate sales reps.",
                category="Sales & Marketing",
                icon="bi-funnel",
                difficulty="intermediate",
                industry="Sales",
                estimated_duration="< 30 seconds",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/lead_scorer",
                    "s3://sales-fragments/crm_updater.py"
                ],
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Lead Data"},
                        {"node_id": "enrich", "node_type": "tool", "name": "Enrich Lead"},
                        {"node_id": "score", "node_type": "code_fragment", "name": "Score Lead",
                         "config": {"fragment_uri": "db://code_fragments/lead_scorer"}},
                        {"node_id": "segment", "node_type": "llm", "name": "Segment Lead"},
                        {"node_id": "route", "node_type": "condition", "name": "Route Lead"},
                        {"node_id": "hot", "node_type": "tool", "name": "Hot Lead Queue"},
                        {"node_id": "warm", "node_type": "tool", "name": "Warm Lead Queue"},
                        {"node_id": "nurture", "node_type": "tool", "name": "Nurture Campaign"},
                        {"node_id": "update", "node_type": "code_fragment", "name": "Update CRM",
                         "config": {"fragment_uri": "s3://sales-fragments/crm_updater.py"}},
                        {"node_id": "output", "node_type": "output", "name": "Routing Result"}
                    ],
                    "edges": [
                        {"source": "input", "target": "enrich"},
                        {"source": "enrich", "target": "score"},
                        {"source": "score", "target": "segment"},
                        {"source": "segment", "target": "route"},
                        {"source": "route", "target": "hot", "condition": "hot"},
                        {"source": "route", "target": "warm", "condition": "warm"},
                        {"source": "route", "target": "nurture", "condition": "cold"},
                        {"source": "hot", "target": "update"},
                        {"source": "warm", "target": "update"},
                        {"source": "nurture", "target": "update"},
                        {"source": "update", "target": "output"}
                    ]
                },
                sample_inputs=[{"email": "lead@company.com", "company": "Acme Inc", "source": "webinar"}],
                expected_outputs=["Lead score", "Segment", "Assigned rep", "Next action"],
                tags=["leads", "scoring", "sales", "code-fragment"],
                prerequisites=["Code fragments configured in Admin > Code Fragments"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_campaign_automation",
                name="Marketing Campaign Automation",
                description="End-to-end marketing campaign automation with personalization and performance tracking.",
                category="Sales & Marketing",
                icon="bi-megaphone",
                difficulty="intermediate",
                industry="Marketing",
                estimated_duration="Ongoing",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Campaign Config"},
                        {"node_id": "segment", "node_type": "tool", "name": "Segment Audience"},
                        {"node_id": "personalize", "node_type": "llm", "name": "Personalize Content"},
                        {"node_id": "schedule", "node_type": "transform", "name": "Schedule Sends"},
                        {"node_id": "email", "node_type": "tool", "name": "Send Emails"},
                        {"node_id": "social", "node_type": "tool", "name": "Post Social"},
                        {"node_id": "track", "node_type": "tool", "name": "Track Performance"},
                        {"node_id": "analyze", "node_type": "llm", "name": "Analyze Results"},
                        {"node_id": "output", "node_type": "output", "name": "Campaign Report"}
                    ],
                    "edges": [
                        {"source": "input", "target": "segment"},
                        {"source": "segment", "target": "personalize"},
                        {"source": "personalize", "target": "schedule"},
                        {"source": "schedule", "target": "email"},
                        {"source": "schedule", "target": "social"},
                        {"source": "email", "target": "track"},
                        {"source": "social", "target": "track"},
                        {"source": "track", "target": "analyze"},
                        {"source": "analyze", "target": "output"}
                    ]
                },
                sample_inputs=[{"campaign_name": "Product Launch", "budget": 10000}],
                expected_outputs=["Campaign metrics", "Engagement rates", "ROI analysis"],
                tags=["marketing", "campaigns", "automation"]
            )
        ]
    
    def _get_technology_workflows(self) -> List[WorkflowTemplate]:
        """Technology workflows."""
        return [
            WorkflowTemplate(
                template_id="wf_tpl_code_review",
                name="Automated Code Review",
                description="AI-powered code review with security scanning, best practices, and suggestions.",
                category="Technology",
                icon="bi-code-slash",
                difficulty="intermediate",
                industry="Technology",
                estimated_duration="1-5 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/code_analyzer",
                    "s3://devops-fragments/security_scanner.py"
                ],
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Code Diff"},
                        {"node_id": "parse", "node_type": "code_fragment", "name": "Parse Code",
                         "config": {"fragment_uri": "db://code_fragments/code_analyzer"}},
                        {"node_id": "security", "node_type": "code_fragment", "name": "Security Scan",
                         "config": {"fragment_uri": "s3://devops-fragments/security_scanner.py"}},
                        {"node_id": "style", "node_type": "llm", "name": "Style Check"},
                        {"node_id": "logic", "node_type": "llm", "name": "Logic Review"},
                        {"node_id": "suggest", "node_type": "llm", "name": "Suggestions"},
                        {"node_id": "output", "node_type": "output", "name": "Review Report"}
                    ],
                    "edges": [
                        {"source": "input", "target": "parse"},
                        {"source": "parse", "target": "security"},
                        {"source": "parse", "target": "style"},
                        {"source": "parse", "target": "logic"},
                        {"source": "security", "target": "suggest"},
                        {"source": "style", "target": "suggest"},
                        {"source": "logic", "target": "suggest"},
                        {"source": "suggest", "target": "output"}
                    ]
                },
                sample_inputs=[{"repo": "myapp", "pr_number": 123}],
                expected_outputs=["Security issues", "Style violations", "Improvement suggestions"],
                tags=["code", "review", "security", "code-fragment"],
                prerequisites=["Code fragments configured in Admin > Code Fragments"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_incident_response",
                name="Incident Response Workflow",
                description="Automated incident response with alerting, diagnosis, and remediation steps.",
                category="Technology",
                icon="bi-exclamation-octagon",
                difficulty="advanced",
                industry="Technology",
                estimated_duration="Variable",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Alert Trigger"},
                        {"node_id": "classify", "node_type": "llm", "name": "Classify Severity"},
                        {"node_id": "diagnose", "node_type": "tool", "name": "Run Diagnostics"},
                        {"node_id": "analyze", "node_type": "llm", "name": "Analyze Root Cause"},
                        {"node_id": "route", "node_type": "condition", "name": "Escalation Path"},
                        {"node_id": "auto_fix", "node_type": "tool", "name": "Auto Remediation"},
                        {"node_id": "page", "node_type": "tool", "name": "Page On-Call"},
                        {"node_id": "critical", "node_type": "hitl", "name": "War Room"},
                        {"node_id": "output", "node_type": "output", "name": "Incident Status"}
                    ],
                    "edges": [
                        {"source": "input", "target": "classify"},
                        {"source": "classify", "target": "diagnose"},
                        {"source": "diagnose", "target": "analyze"},
                        {"source": "analyze", "target": "route"},
                        {"source": "route", "target": "auto_fix", "condition": "low"},
                        {"source": "route", "target": "page", "condition": "medium"},
                        {"source": "route", "target": "critical", "condition": "critical"},
                        {"source": "auto_fix", "target": "output"},
                        {"source": "page", "target": "output"},
                        {"source": "critical", "target": "output"}
                    ]
                },
                sample_inputs=[{"alert_id": "ALT123", "service": "api-gateway"}],
                expected_outputs=["Severity", "Root cause", "Resolution steps", "Timeline"],
                tags=["incident", "devops", "sre", "hitl"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_api_testing",
                name="API Testing Pipeline",
                description="Automated API testing with request generation, validation, and reporting.",
                category="Technology",
                icon="bi-plug",
                difficulty="intermediate",
                industry="Technology",
                estimated_duration="2-10 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/api_tester",
                    "s3://devops-fragments/test_reporter.py"
                ],
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "API Spec"},
                        {"node_id": "generate", "node_type": "llm", "name": "Generate Test Cases"},
                        {"node_id": "execute", "node_type": "code_fragment", "name": "Execute Tests",
                         "config": {"fragment_uri": "db://code_fragments/api_tester"}},
                        {"node_id": "validate", "node_type": "transform", "name": "Validate Responses"},
                        {"node_id": "analyze", "node_type": "llm", "name": "Analyze Failures"},
                        {"node_id": "report", "node_type": "code_fragment", "name": "Generate Report",
                         "config": {"fragment_uri": "s3://devops-fragments/test_reporter.py"}},
                        {"node_id": "output", "node_type": "output", "name": "Test Report"}
                    ],
                    "edges": [
                        {"source": "input", "target": "generate"},
                        {"source": "generate", "target": "execute"},
                        {"source": "execute", "target": "validate"},
                        {"source": "validate", "target": "analyze"},
                        {"source": "analyze", "target": "report"},
                        {"source": "report", "target": "output"}
                    ]
                },
                sample_inputs=[{"openapi_spec": "api.yaml", "environment": "staging"}],
                expected_outputs=["Test results", "Pass/fail rate", "Failure analysis"],
                tags=["api", "testing", "automation", "code-fragment"],
                prerequisites=["Code fragments configured in Admin > Code Fragments"]
            )
        ]
    
    def _get_customer_service_workflows(self) -> List[WorkflowTemplate]:
        """Customer service workflows."""
        return [
            WorkflowTemplate(
                template_id="wf_tpl_ticket_triage",
                name="Support Ticket Triage",
                description="Automated support ticket classification, prioritization, and routing.",
                category="Customer Service",
                icon="bi-ticket-detailed",
                difficulty="beginner",
                industry="General",
                estimated_duration="< 30 seconds",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "New Ticket"},
                        {"node_id": "classify", "node_type": "llm", "name": "Classify Issue"},
                        {"node_id": "priority", "node_type": "llm", "name": "Assess Priority"},
                        {"node_id": "route", "node_type": "condition", "name": "Routing Decision"},
                        {"node_id": "l1", "node_type": "output", "name": "L1 Support"},
                        {"node_id": "l2", "node_type": "output", "name": "L2 Support"},
                        {"node_id": "escalate", "node_type": "hitl", "name": "Escalate"}
                    ],
                    "edges": [
                        {"source": "input", "target": "classify"},
                        {"source": "classify", "target": "priority"},
                        {"source": "priority", "target": "route"},
                        {"source": "route", "target": "l1", "condition": "low"},
                        {"source": "route", "target": "l2", "condition": "medium"},
                        {"source": "route", "target": "escalate", "condition": "high"}
                    ]
                },
                sample_inputs=[{"ticket_subject": "Can't login", "ticket_body": "Getting error 401"}],
                expected_outputs=["Category", "Priority", "Assigned queue", "Suggested response"],
                tags=["support", "tickets", "triage", "beginner"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_chatbot_fallback",
                name="Chatbot Fallback Handler",
                description="Handles chatbot fallbacks with context preservation and human handoff.",
                category="Customer Service",
                icon="bi-chat-dots",
                difficulty="intermediate",
                industry="General",
                estimated_duration="< 1 minute",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Failed Query"},
                        {"node_id": "analyze", "node_type": "llm", "name": "Analyze Intent"},
                        {"node_id": "search", "node_type": "tool", "name": "Search KB"},
                        {"node_id": "decision", "node_type": "condition", "name": "Resolution Path"},
                        {"node_id": "respond", "node_type": "llm", "name": "Generate Response"},
                        {"node_id": "handoff", "node_type": "hitl", "name": "Human Handoff"},
                        {"node_id": "output", "node_type": "output", "name": "Resolution"}
                    ],
                    "edges": [
                        {"source": "input", "target": "analyze"},
                        {"source": "analyze", "target": "search"},
                        {"source": "search", "target": "decision"},
                        {"source": "decision", "target": "respond", "condition": "found"},
                        {"source": "decision", "target": "handoff", "condition": "not_found"},
                        {"source": "respond", "target": "output"},
                        {"source": "handoff", "target": "output"}
                    ]
                },
                sample_inputs=[{"query": "How do I cancel?", "context": {"user_id": "123"}}],
                expected_outputs=["Response", "Confidence", "Handoff status"],
                tags=["chatbot", "fallback", "support", "hitl"]
            )
        ]
    
    def _get_supply_chain_workflows(self) -> List[WorkflowTemplate]:
        """Supply chain workflows."""
        return [
            WorkflowTemplate(
                template_id="wf_tpl_inventory_reorder",
                name="Inventory Reorder Automation",
                description="Automated inventory monitoring and reorder processing based on thresholds.",
                category="Supply Chain",
                icon="bi-box-seam",
                difficulty="intermediate",
                industry="Retail",
                estimated_duration="1-5 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/inventory_checker",
                    "s3://supply-chain-fragments/po_generator.py"
                ],
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Inventory Alert"},
                        {"node_id": "check", "node_type": "code_fragment", "name": "Check Levels",
                         "config": {"fragment_uri": "db://code_fragments/inventory_checker"}},
                        {"node_id": "forecast", "node_type": "llm", "name": "Demand Forecast"},
                        {"node_id": "calculate", "node_type": "transform", "name": "Calculate Order"},
                        {"node_id": "approve", "node_type": "condition", "name": "Auto Approve?"},
                        {"node_id": "generate", "node_type": "code_fragment", "name": "Generate PO",
                         "config": {"fragment_uri": "s3://supply-chain-fragments/po_generator.py"}},
                        {"node_id": "review", "node_type": "hitl", "name": "Manual Review"},
                        {"node_id": "output", "node_type": "output", "name": "Order Status"}
                    ],
                    "edges": [
                        {"source": "input", "target": "check"},
                        {"source": "check", "target": "forecast"},
                        {"source": "forecast", "target": "calculate"},
                        {"source": "calculate", "target": "approve"},
                        {"source": "approve", "target": "generate", "condition": "auto"},
                        {"source": "approve", "target": "review", "condition": "manual"},
                        {"source": "review", "target": "generate"},
                        {"source": "generate", "target": "output"}
                    ]
                },
                sample_inputs=[{"sku": "PROD123", "current_level": 50, "threshold": 100}],
                expected_outputs=["Order quantity", "Supplier", "Expected delivery", "PO number"],
                tags=["inventory", "supply-chain", "automation", "code-fragment"]
            ),
            WorkflowTemplate(
                template_id="wf_tpl_shipment_tracking",
                name="Shipment Tracking & Alerts",
                description="Real-time shipment tracking with delay detection and customer notifications.",
                category="Supply Chain",
                icon="bi-truck",
                difficulty="beginner",
                industry="Logistics",
                estimated_duration="Continuous",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Tracking Update"},
                        {"node_id": "parse", "node_type": "transform", "name": "Parse Event"},
                        {"node_id": "check", "node_type": "condition", "name": "Check Status"},
                        {"node_id": "on_track", "node_type": "transform", "name": "Update Status"},
                        {"node_id": "delayed", "node_type": "llm", "name": "Analyze Delay"},
                        {"node_id": "notify", "node_type": "tool", "name": "Send Alert"},
                        {"node_id": "output", "node_type": "output", "name": "Tracking Status"}
                    ],
                    "edges": [
                        {"source": "input", "target": "parse"},
                        {"source": "parse", "target": "check"},
                        {"source": "check", "target": "on_track", "condition": "on_time"},
                        {"source": "check", "target": "delayed", "condition": "delayed"},
                        {"source": "delayed", "target": "notify"},
                        {"source": "on_track", "target": "output"},
                        {"source": "notify", "target": "output"}
                    ]
                },
                sample_inputs=[{"tracking_number": "1Z999999", "carrier": "UPS"}],
                expected_outputs=["Current location", "ETA", "Delay reason if any"],
                tags=["shipping", "tracking", "logistics", "beginner"]
            )
        ]
    
    # Manager methods
    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get a template by ID."""
        return self._templates.get(template_id)
    
    def list_templates(self, category: str = None, 
                       difficulty: str = None,
                       industry: str = None,
                       uses_code_fragments: bool = None) -> List[WorkflowTemplate]:
        """List templates with optional filters."""
        templates = list(self._templates.values())
        
        if category:
            templates = [t for t in templates if t.category.lower() == category.lower()]
        if difficulty:
            templates = [t for t in templates if t.difficulty == difficulty]
        if industry:
            templates = [t for t in templates if t.industry.lower() == industry.lower()]
        if uses_code_fragments is not None:
            templates = [t for t in templates if t.uses_code_fragments == uses_code_fragments]
        
        return sorted(templates, key=lambda t: t.name)
    
    def get_categories(self) -> List[str]:
        """Get list of unique categories."""
        categories = set(t.category for t in self._templates.values())
        return sorted(categories)
    
    def get_industries(self) -> List[str]:
        """Get list of unique industries."""
        industries = set(t.industry for t in self._templates.values())
        return sorted(industries)
    
    def get_code_fragment_templates(self) -> List[WorkflowTemplate]:
        """Get templates that use code fragments."""
        return [t for t in self._templates.values() if t.uses_code_fragments]
