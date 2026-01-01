#!/usr/bin/env python3
"""
Document Processing Pipeline Example

This example demonstrates a comprehensive document processing workflow that:
1. Ingests documents in various formats
2. Classifies document type and content
3. Extracts structure, entities, and key points
4. Generates multi-level summaries
5. Produces insights and recommendations
6. Formats final output

Usage:
    python document_processing_pipeline.py [document_path]
    
    Or run with sample data:
    python document_processing_pipeline.py --sample

Copyright © 2025-2030 Abhikarta. All Rights Reserved.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from abhikarta.langchain.agents import AgentExecutor, create_conversational_agent
from abhikarta.database.db_facade import DBFacade

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Document processing pipeline implementation."""
    
    def __init__(self, llm_config: Dict[str, Any] = None):
        """Initialize the document processor.
        
        Args:
            llm_config: LLM configuration dictionary
        """
        self.llm_config = llm_config or {
            "provider": "ollama",
            "model": "llama3.2:3b",
            "base_url": os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
            "temperature": 0.5
        }
        self.llm = None
        self.results = {}
        
    def _create_llm(self):
        """Create LLM instance."""
        if self.llm is not None:
            return self.llm
            
        try:
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(
                model=self.llm_config.get("model", "llama3.2:3b"),
                base_url=self.llm_config.get("base_url", "http://localhost:11434"),
                temperature=self.llm_config.get("temperature", 0.5)
            )
            logger.info(f"LLM created: {self.llm_config['model']}")
            return self.llm
        except ImportError:
            raise ImportError("langchain-ollama is required. Install with: pip install langchain-ollama")
    
    def _invoke_llm(self, prompt: str) -> str:
        """Invoke LLM with a prompt."""
        llm = self._create_llm()
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def extract_content(self, document_path: str = None, content: str = None) -> str:
        """Extract content from document or use provided content.
        
        Args:
            document_path: Path to document file
            content: Raw content string
            
        Returns:
            Extracted text content
        """
        if content:
            self.results['raw_content'] = content
            return content
            
        if document_path:
            path = Path(document_path)
            if not path.exists():
                raise FileNotFoundError(f"Document not found: {document_path}")
                
            # Simple text extraction (extend for PDF, DOCX, etc.)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.results['raw_content'] = content
            return content
            
        raise ValueError("Either document_path or content must be provided")
    
    def classify_content(self) -> Dict[str, Any]:
        """Classify the document content."""
        logger.info("Step 1: Classifying content...")
        
        prompt = f"""Analyze this document and classify it:

{self.results['raw_content'][:3000]}

Provide a JSON response with:
{{
    "document_type": "report/article/email/contract/memo/other",
    "primary_topic": "main topic",
    "key_entities": ["entity1", "entity2"],
    "sentiment": "positive/neutral/negative",
    "complexity": "simple/moderate/complex",
    "recommended_processing": "description of how to process"
}}"""
        
        response = self._invoke_llm(prompt)
        self.results['classification'] = response
        logger.info("Classification complete")
        return {"classification": response}
    
    def extract_structure(self) -> Dict[str, Any]:
        """Extract document structure."""
        logger.info("Step 2: Extracting structure...")
        
        prompt = f"""Extract the document structure:

{self.results['raw_content'][:3000]}

Identify:
1. Sections and subsections
2. Headers and titles
3. Lists and tables
4. Key paragraphs
5. References or citations

Provide a hierarchical structure map."""
        
        response = self._invoke_llm(prompt)
        self.results['document_structure'] = response
        logger.info("Structure extraction complete")
        return {"document_structure": response}
    
    def extract_entities(self) -> Dict[str, Any]:
        """Extract named entities."""
        logger.info("Step 3: Extracting entities...")
        
        prompt = f"""Extract all named entities from:

{self.results['raw_content'][:3000]}

Categories:
- PERSON: Names of people
- ORG: Organizations
- DATE: Dates and times
- LOCATION: Places
- MONEY: Monetary values
- PRODUCT: Products or services

List each entity with its category."""
        
        response = self._invoke_llm(prompt)
        self.results['entities'] = response
        logger.info("Entity extraction complete")
        return {"entities": response}
    
    def extract_key_points(self) -> Dict[str, Any]:
        """Extract key points from document."""
        logger.info("Step 4: Extracting key points...")
        
        prompt = f"""Extract the key points from this document:

{self.results['raw_content'][:3000]}

Classification: {self.results.get('classification', 'Not available')}

Provide:
1. Main thesis/purpose
2. Top 5-10 key points
3. Supporting evidence for each
4. Conclusions drawn
5. Action items (if any)"""
        
        response = self._invoke_llm(prompt)
        self.results['key_points'] = response
        logger.info("Key points extraction complete")
        return {"key_points": response}
    
    def generate_summaries(self) -> Dict[str, Any]:
        """Generate multi-level summaries."""
        logger.info("Step 5: Generating summaries...")
        
        prompt = f"""Generate summaries at multiple levels:

Document excerpt: {self.results['raw_content'][:2000]}
Key Points: {self.results.get('key_points', 'Not available')[:1000]}

Provide:
1. ONE-LINER: Single sentence summary
2. BRIEF (50 words): Key takeaway
3. STANDARD (150 words): Main points covered
4. DETAILED (300 words): Comprehensive summary"""
        
        response = self._invoke_llm(prompt)
        self.results['summaries'] = response
        logger.info("Summary generation complete")
        return {"summaries": response}
    
    def generate_insights(self) -> Dict[str, Any]:
        """Generate insights from analysis."""
        logger.info("Step 6: Generating insights...")
        
        prompt = f"""Generate insights from this document analysis:

Classification: {self.results.get('classification', 'N/A')[:500]}
Structure: {self.results.get('document_structure', 'N/A')[:500]}
Entities: {self.results.get('entities', 'N/A')[:500]}
Key Points: {self.results.get('key_points', 'N/A')[:500]}

Provide:
1. Key Insights (non-obvious observations)
2. Patterns Identified
3. Gaps or Missing Information
4. Questions Raised
5. Recommendations"""
        
        response = self._invoke_llm(prompt)
        self.results['insights'] = response
        logger.info("Insight generation complete")
        return {"insights": response}
    
    def format_output(self) -> Dict[str, Any]:
        """Format final output report."""
        logger.info("Step 7: Formatting final output...")
        
        prompt = f"""Create a comprehensive document analysis report:

CLASSIFICATION:
{self.results.get('classification', 'N/A')}

DOCUMENT STRUCTURE:
{self.results.get('document_structure', 'N/A')}

ENTITIES FOUND:
{self.results.get('entities', 'N/A')}

KEY POINTS:
{self.results.get('key_points', 'N/A')}

SUMMARIES:
{self.results.get('summaries', 'N/A')}

INSIGHTS:
{self.results.get('insights', 'N/A')}

Format this as a professional document analysis report with clear sections and actionable takeaways."""
        
        response = self._invoke_llm(prompt)
        self.results['final_report'] = response
        logger.info("Output formatting complete")
        return {"final_report": response}
    
    def process(self, document_path: str = None, content: str = None) -> Dict[str, Any]:
        """Run the complete document processing pipeline.
        
        Args:
            document_path: Path to document file
            content: Raw content string
            
        Returns:
            Complete processing results
        """
        start_time = datetime.now(timezone.utc)
        logger.info("=" * 60)
        logger.info("Starting Document Processing Pipeline")
        logger.info("=" * 60)
        
        try:
            # Step 1: Extract content
            self.extract_content(document_path, content)
            
            # Step 2-4: Parallel analysis (run sequentially for simplicity)
            self.classify_content()
            self.extract_structure()
            self.extract_entities()
            self.extract_key_points()
            
            # Step 5-6: Generate outputs
            self.generate_summaries()
            self.generate_insights()
            
            # Step 7: Format final output
            self.format_output()
            
            # Add metadata
            end_time = datetime.now(timezone.utc)
            self.results['metadata'] = {
                'processing_time_seconds': (end_time - start_time).total_seconds(),
                'word_count': len(self.results.get('raw_content', '').split()),
                'processed_at': end_time.isoformat(),
                'status': 'completed'
            }
            
            logger.info("=" * 60)
            logger.info("Document Processing Complete")
            logger.info(f"Total time: {self.results['metadata']['processing_time_seconds']:.2f}s")
            logger.info("=" * 60)
            
            return self.results
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self.results['error'] = str(e)
            self.results['status'] = 'failed'
            return self.results


def get_sample_document() -> str:
    """Return a sample document for testing."""
    return """Annual Performance Report 2024

Executive Summary:
This report presents the annual performance metrics for fiscal year 2024. Overall, the organization 
achieved 15% growth compared to the previous year, exceeding targets by 3%. Key strategic 
initiatives including digital transformation and market expansion contributed significantly to 
these results.

Key Achievements:
1. Revenue Growth: Revenue increased from $10M to $11.5M, representing a 15% year-over-year growth
2. Customer Satisfaction: Net Promoter Score improved from 85% to 92%, indicating strong customer loyalty
3. Product Innovation: Successfully launched 5 new products, capturing 8% additional market share
4. Geographic Expansion: Extended operations into 3 new regions: Southeast Asia, Eastern Europe, and South America
5. Operational Efficiency: Reduced operational costs by 12% through process automation

Challenges Faced:
- Supply chain disruptions in Q2 due to global logistics issues impacted delivery timelines
- Increased competition from new market entrants required accelerated innovation cycles
- Talent acquisition difficulties, particularly in technical roles, affected some project timelines
- Rising material costs impacted profit margins in certain product lines

Financial Highlights:
- Gross Revenue: $11.5M (up 15%)
- Net Profit: $2.3M (up 18%)
- Operating Margin: 20% (improved from 18.5%)
- R&D Investment: $1.8M (15.6% of revenue)

Strategic Recommendations:
1. Supply Chain Resilience: Invest in diversified supplier networks and local manufacturing capabilities
2. Digital Transformation: Accelerate adoption of AI and automation across all business functions
3. Talent Strategy: Enhance employee value proposition with competitive benefits and growth opportunities
4. Market Defense: Strengthen competitive moat through continuous innovation and customer engagement

Conclusion:
Fiscal Year 2024 was a successful year that demonstrated the organization's resilience and 
adaptability. Despite facing significant external challenges, the team delivered strong results 
across all key metrics. Looking ahead, continued focus on innovation, operational excellence, 
and customer-centricity will drive sustained growth.

Prepared by: Strategic Planning Division
Date: January 15, 2025
Classification: Internal Use Only"""


def main():
    """Main function to run the document processing pipeline."""
    parser = argparse.ArgumentParser(description='Document Processing Pipeline')
    parser.add_argument('document', nargs='?', help='Path to document file')
    parser.add_argument('--sample', action='store_true', help='Use sample document')
    parser.add_argument('--output', '-o', help='Output file path for results')
    parser.add_argument('--model', default='llama3.2:3b', help='Ollama model to use')
    parser.add_argument('--base-url', default='http://localhost:11434', help='Ollama base URL')
    
    args = parser.parse_args()
    
    # Configure LLM
    llm_config = {
        "provider": "ollama",
        "model": args.model,
        "base_url": args.base_url,
        "temperature": 0.5
    }
    
    # Create processor
    processor = DocumentProcessor(llm_config)
    
    # Process document
    if args.sample or not args.document:
        logger.info("Using sample document")
        results = processor.process(content=get_sample_document())
    else:
        logger.info(f"Processing document: {args.document}")
        results = processor.process(document_path=args.document)
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved to: {args.output}")
    else:
        print("\n" + "=" * 60)
        print("FINAL REPORT")
        print("=" * 60)
        print(results.get('final_report', 'No report generated'))
        print("\n" + "=" * 60)
        print("METADATA")
        print("=" * 60)
        print(json.dumps(results.get('metadata', {}), indent=2))


if __name__ == "__main__":
    main()
