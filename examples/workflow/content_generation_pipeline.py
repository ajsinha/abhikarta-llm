#!/usr/bin/env python3
"""
Content Generation Pipeline Example

A comprehensive content generation workflow that creates high-quality content through:
1. Brief parsing and understanding
2. Research gathering
3. Ideation and brainstorming
4. Outline creation
5. Draft writing
6. Review and revision
7. Style polishing
8. Final assembly

Usage:
    python content_generation_pipeline.py "Write a blog post about..."
    python content_generation_pipeline.py --interactive
    python content_generation_pipeline.py --brief brief.txt

Copyright © 2025-2030 Abhikarta. All Rights Reserved.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ContentBrief:
    """Content brief specification."""
    content_type: str = "article"
    target_audience: str = ""
    tone: str = "professional"
    word_count: int = 1000
    key_topics: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)


@dataclass
class ContentStage:
    """Represents a stage in the content pipeline."""
    name: str
    output: str = ""
    duration_ms: int = 0
    quality_score: float = 0.0


class ContentGenerationPipeline:
    """Content generation pipeline implementation."""
    
    def __init__(self, llm_config: Dict[str, Any] = None):
        """Initialize the content generation pipeline."""
        self.llm_config = llm_config or {
            "provider": "ollama",
            "model": "llama3.2:3b",
            "base_url": os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
            "temperature": 0.7
        }
        self.llm = None
        self.stages: Dict[str, ContentStage] = {}
        self.brief: Optional[ContentBrief] = None
        
    def _create_llm(self):
        """Create LLM instance."""
        if self.llm is not None:
            return self.llm
        try:
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(
                model=self.llm_config.get("model", "llama3.2:3b"),
                base_url=self.llm_config.get("base_url", "http://localhost:11434"),
                temperature=self.llm_config.get("temperature", 0.7)
            )
            return self.llm
        except ImportError:
            raise ImportError("langchain-ollama required")
    
    def _invoke(self, prompt: str) -> str:
        """Invoke the LLM."""
        import time
        start = time.time()
        llm = self._create_llm()
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def _run_stage(self, stage_name: str, prompt: str) -> str:
        """Run a pipeline stage."""
        import time
        logger.info(f"Running stage: {stage_name}")
        start = time.time()
        
        result = self._invoke(prompt)
        
        duration = int((time.time() - start) * 1000)
        self.stages[stage_name] = ContentStage(
            name=stage_name,
            output=result,
            duration_ms=duration
        )
        
        logger.info(f"Stage {stage_name} completed in {duration}ms")
        return result
    
    def parse_brief(self, input_text: str) -> str:
        """Parse the content brief."""
        prompt = f"""Parse this content request:

{input_text}

Extract and format as:
CONTENT_TYPE: [article/blog/report/etc.]
TARGET_AUDIENCE: [description]
TONE: [formal/casual/professional/etc.]
WORD_COUNT: [number]
KEY_TOPICS: [comma-separated list]
GOALS: [what the content should achieve]
CONSTRAINTS: [any limitations]"""
        
        return self._run_stage("brief_parsing", prompt)
    
    def gather_research(self, brief: str) -> str:
        """Gather research for the content."""
        prompt = f"""Gather research for this content:

BRIEF:
{brief}

Provide comprehensive research:

KEY FACTS:
- [Important information to include]

STATISTICS:
- [Relevant data points with sources]

EXAMPLES:
- [Illustrative cases and scenarios]

EXPERT PERSPECTIVES:
- [Notable viewpoints on the topic]

COUNTERPOINTS:
- [Alternative views to consider]

SUPPORTING RESOURCES:
- [Reference materials]"""
        
        return self._run_stage("research_gathering", prompt)
    
    def generate_ideas(self, brief: str, research: str) -> str:
        """Generate content ideas."""
        prompt = f"""Generate content ideas:

BRIEF:
{brief}

RESEARCH:
{research}

Brainstorm creative approaches:

ANGLES (5 different approaches):
1. 
2. 
3. 
4. 
5. 

HOOKS (5 attention-grabbing openers):
1. 
2. 
3. 
4. 
5. 

UNIQUE INSIGHTS:
- What fresh perspective can we offer?

STORY ELEMENTS:
- Narrative ideas to make it engaging"""
        
        return self._run_stage("ideation", prompt)
    
    def create_outline(self, brief: str, research: str, ideas: str) -> str:
        """Create content outline."""
        prompt = f"""Create a detailed content outline:

BRIEF:
{brief}

RESEARCH:
{research}

IDEAS:
{ideas}

Create comprehensive outline:

# [COMPELLING TITLE]

## Introduction (~100 words)
- Hook: [specific attention grabber]
- Context: [background setup]
- Thesis: [main argument/promise]

## Section 1: [Title] (~200 words)
- Main Point
  - Supporting detail
  - Evidence/example
- Secondary Point
  - Supporting detail

## Section 2: [Title] (~200 words)
- Main Point
  - Supporting detail
  - Evidence/example

## Section 3: [Title] (~200 words)
- Main Point
  - Supporting detail
  - Evidence/example

## Conclusion (~100 words)
- Summary of key points
- Call to action
- Memorable closing thought

Total target: [X words]"""
        
        return self._run_stage("outline_creation", prompt)
    
    def write_draft(self, brief: str, research: str, outline: str) -> str:
        """Write the first draft."""
        prompt = f"""Write a complete first draft:

BRIEF:
{brief}

RESEARCH:
{research}

OUTLINE:
{outline}

Write the complete first draft following the outline exactly.

Guidelines:
- Follow the outline structure
- Incorporate research naturally
- Match the specified tone
- Meet word count targets
- Focus on completeness over perfection
- Use clear transitions between sections
- Include specific examples

Write the full draft now:"""
        
        return self._run_stage("draft_writing", prompt)
    
    def review_content(self, brief: str, draft: str) -> str:
        """Review the draft."""
        prompt = f"""Review this draft thoroughly:

BRIEF:
{brief}

DRAFT:
{draft}

Evaluate on these criteria:

ACCURACY (1-10):
- Score: 
- Issues found:

COMPLETENESS (1-10):
- Score:
- Missing elements:

STRUCTURE (1-10):
- Score:
- Flow issues:

ENGAGEMENT (1-10):
- Score:
- Where attention might drop:

CLARITY (1-10):
- Score:
- Confusing sections:

TONE (1-10):
- Score:
- Tone mismatches:

SPECIFIC IMPROVEMENTS:
1. [Location]: [Problem] -> [Suggestion]
2. [Location]: [Problem] -> [Suggestion]
3. [Location]: [Problem] -> [Suggestion]

OVERALL SCORE: X/10
MAJOR REVISION NEEDED: Yes/No"""
        
        return self._run_stage("review", prompt)
    
    def revise_draft(self, draft: str, review: str, brief: str) -> str:
        """Revise based on review."""
        prompt = f"""Revise the draft based on review feedback:

ORIGINAL DRAFT:
{draft}

REVIEW FEEDBACK:
{review}

BRIEF:
{brief}

Create a revised draft that:
1. Addresses ALL review feedback
2. Maintains original strengths
3. Improves weak sections
4. Enhances overall quality

Provide the complete revised draft:"""
        
        return self._run_stage("revision", prompt)
    
    def polish_style(self, draft: str, brief: str) -> str:
        """Polish the writing style."""
        prompt = f"""Polish this content for style and readability:

DRAFT:
{draft}

TARGET TONE: {brief}

Polish for:

WORD CHOICE:
- Replace weak verbs with strong ones
- Eliminate unnecessary adverbs
- Use specific nouns over vague ones

SENTENCE VARIETY:
- Mix short punchy sentences with longer flowing ones
- Vary sentence openings
- Create rhythm

TRANSITIONS:
- Ensure smooth connections between paragraphs
- Use transitional phrases appropriately

IMPACT:
- Strengthen the opening hook
- Punch up the conclusion
- Add memorable phrases

Provide the fully polished version:"""
        
        return self._run_stage("style_polish", prompt)
    
    def assemble_final(self, polished_draft: str, brief: str) -> str:
        """Assemble final content with metadata."""
        prompt = f"""Assemble the final content:

POLISHED CONTENT:
{polished_draft}

BRIEF:
{brief}

Create the final deliverable:

---
[OPTIMIZED TITLE]

[Full polished content]

---

CONTENT METADATA:
- Word Count: [actual count]
- Reading Time: [X minutes]
- Content Type: [type]
- Target Audience: [audience]
- Tone: [tone achieved]

SUMMARY:
[2-3 sentence summary of the content]

KEYWORDS:
[5-7 relevant keywords]
---"""
        
        return self._run_stage("final_assembly", prompt)
    
    def generate(self, content_request: str) -> Dict[str, Any]:
        """Run the full content generation pipeline."""
        logger.info("=" * 60)
        logger.info("CONTENT GENERATION PIPELINE")
        logger.info("=" * 60)
        
        start_time = datetime.now(timezone.utc)
        
        # Stage 1: Parse brief
        logger.info("\n[1/7] Parsing content brief...")
        brief = self.parse_brief(content_request)
        
        # Stage 2: Gather research
        logger.info("\n[2/7] Gathering research...")
        research = self.gather_research(brief)
        
        # Stage 3: Generate ideas
        logger.info("\n[3/7] Generating ideas...")
        ideas = self.generate_ideas(brief, research)
        
        # Stage 4: Create outline
        logger.info("\n[4/7] Creating outline...")
        outline = self.create_outline(brief, research, ideas)
        
        # Stage 5: Write draft
        logger.info("\n[5/7] Writing first draft...")
        draft = self.write_draft(brief, research, outline)
        
        # Stage 6: Review and revise
        logger.info("\n[6/7] Reviewing and revising...")
        review = self.review_content(brief, draft)
        revised = self.revise_draft(draft, review, brief)
        
        # Stage 7: Polish and assemble
        logger.info("\n[7/7] Polishing and assembling...")
        polished = self.polish_style(revised, brief)
        final = self.assemble_final(polished, brief)
        
        end_time = datetime.now(timezone.utc)
        total_duration = (end_time - start_time).total_seconds()
        
        # Compile results
        results = {
            "content_request": content_request,
            "final_content": final,
            "stages": {
                name: {
                    "output_preview": stage.output[:500] + "..." if len(stage.output) > 500 else stage.output,
                    "duration_ms": stage.duration_ms
                }
                for name, stage in self.stages.items()
            },
            "metadata": {
                "total_duration_seconds": total_duration,
                "stages_completed": len(self.stages),
                "completed_at": end_time.isoformat()
            }
        }
        
        logger.info("\n" + "=" * 60)
        logger.info("CONTENT GENERATION COMPLETE")
        logger.info(f"Total time: {total_duration:.2f}s")
        logger.info("=" * 60)
        
        return results


def run_interactive(pipeline: ContentGenerationPipeline):
    """Run interactive content generation."""
    print("\n" + "=" * 60)
    print("📝 CONTENT GENERATION PIPELINE")
    print("=" * 60)
    print("\nDescribe the content you want to create.")
    print("Include: type, audience, tone, length, topics")
    print("\nType 'quit' to exit.\n")
    
    while True:
        print("-" * 40)
        request = input("📋 Content Request: ").strip()
        
        if request.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not request:
            continue
        
        result = pipeline.generate(request)
        
        print("\n" + "=" * 60)
        print("📄 GENERATED CONTENT")
        print("=" * 60)
        print(result['final_content'])
        print("\n" + "=" * 60)
        
        # Ask if user wants to save
        save = input("\nSave to file? (y/n): ").strip().lower()
        if save == 'y':
            filename = f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, 'w') as f:
                f.write(result['final_content'])
            print(f"Saved to: {filename}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Content Generation Pipeline')
    parser.add_argument('request', nargs='?', help='Content request')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--brief', '-b', help='Read brief from file')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--model', default='llama3.2:3b', help='Ollama model')
    parser.add_argument('--base-url', default='http://localhost:11434', help='Ollama URL')
    
    args = parser.parse_args()
    
    llm_config = {
        "provider": "ollama",
        "model": args.model,
        "base_url": args.base_url,
        "temperature": 0.7
    }
    
    pipeline = ContentGenerationPipeline(llm_config)
    
    if args.interactive:
        run_interactive(pipeline)
    elif args.brief:
        with open(args.brief, 'r') as f:
            request = f.read()
        result = pipeline.generate(request)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result['final_content'])
        else:
            print(result['final_content'])
    elif args.request:
        result = pipeline.generate(args.request)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result['final_content'])
        else:
            print(result['final_content'])
    else:
        run_interactive(pipeline)


if __name__ == "__main__":
    main()
