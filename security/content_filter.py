"""
Content Filtering Module

Filters harmful, inappropriate, or policy-violating content before
sending to LLM providers or displaying to users.

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import re
import logging
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ContentCategory(Enum):
    """Categories of content that can be filtered"""
    HATE_SPEECH = "hate_speech"
    VIOLENCE = "violence"
    SEXUAL_CONTENT = "sexual_content"
    SELF_HARM = "self_harm"
    HARASSMENT = "harassment"
    ILLEGAL_ACTIVITY = "illegal_activity"
    PROFANITY = "profanity"
    SPAM = "spam"
    MISINFORMATION = "misinformation"
    MALWARE = "malware"
    PERSONAL_ATTACKS = "personal_attacks"
    DISCRIMINATION = "discrimination"


class FilterAction(Enum):
    """Actions to take when harmful content is detected"""
    BLOCK = "block"
    WARN = "warn"
    SANITIZE = "sanitize"
    LOG = "log"


@dataclass
class ContentMatch:
    """Represents detected harmful content"""
    category: ContentCategory
    matched_text: str
    confidence: float
    start: int
    end: int
    rule_name: str = ""


@dataclass
class FilterResult:
    """Result of content filtering"""
    original_text: str
    filtered_text: str
    was_blocked: bool = False
    warnings: List[str] = field(default_factory=list)
    matches: List[ContentMatch] = field(default_factory=list)
    category_scores: Dict[ContentCategory, float] = field(default_factory=dict)


@dataclass
class FilterRule:
    """Rule for content filtering"""
    name: str
    category: ContentCategory
    patterns: List[str]
    keywords: List[str] = field(default_factory=list)
    confidence: float = 1.0
    enabled: bool = True


class ContentFilter:
    """
    Filters harmful and inappropriate content.
    
    Example:
        filter = ContentFilter(
            block_categories=['hate_speech', 'violence', 'sexual_content'],
            threshold=0.8,
            action='block'
        )
        
        result = filter.process("Some harmful text here")
        if result.was_blocked:
            print("Content blocked!")
    """
    
    # Built-in filter rules
    BUILT_IN_RULES = {
        ContentCategory.HATE_SPEECH: FilterRule(
            "hate_speech_basic",
            ContentCategory.HATE_SPEECH,
            patterns=[
                r'\b(?:hate|despise|detest)\s+(?:all|every)?\s*\w+s?\b',
            ],
            keywords=[
                'supremacy', 'inferior', 'subhuman', 'deport', 'exterminate'
            ],
            confidence=0.9
        ),
        
        ContentCategory.VIOLENCE: FilterRule(
            "violence_basic",
            ContentCategory.VIOLENCE,
            patterns=[
                r'\b(?:kill|murder|assault|attack|harm|hurt|destroy)\b',
                r'\b(?:bomb|weapon|gun|knife|explosive)\b',
            ],
            keywords=[
                'violence', 'bloodshed', 'massacre', 'torture', 'abuse'
            ],
            confidence=0.85
        ),
        
        ContentCategory.SEXUAL_CONTENT: FilterRule(
            "sexual_basic",
            ContentCategory.SEXUAL_CONTENT,
            patterns=[
                r'\b(?:explicit|nsfw|xxx|porn)\b',
            ],
            keywords=[
                'explicit', 'adult', 'nsfw', 'inappropriate'
            ],
            confidence=0.9
        ),
        
        ContentCategory.SELF_HARM: FilterRule(
            "self_harm_basic",
            ContentCategory.SELF_HARM,
            patterns=[
                r'\b(?:suicide|self.?harm|end\s+(?:my|your)\s+life)\b',
                r'\bhow\s+to\s+(?:kill|hurt)\s+(?:myself|yourself)\b',
            ],
            keywords=[
                'suicide', 'self-harm', 'cutting', 'overdose'
            ],
            confidence=0.95
        ),
        
        ContentCategory.HARASSMENT: FilterRule(
            "harassment_basic",
            ContentCategory.HARASSMENT,
            patterns=[
                r'\b(?:harass|bully|threaten|intimidate|stalk)\b',
            ],
            keywords=[
                'harassment', 'bullying', 'threatening', 'intimidation'
            ],
            confidence=0.8
        ),
        
        ContentCategory.ILLEGAL_ACTIVITY: FilterRule(
            "illegal_basic",
            ContentCategory.ILLEGAL_ACTIVITY,
            patterns=[
                r'\bhow\s+to\s+(?:make|build|create)\s+(?:bomb|explosive|weapon)\b',
                r'\bhow\s+to\s+(?:hack|crack|break\s+into)\b',
            ],
            keywords=[
                'illegal', 'hack', 'crack', 'steal', 'fraud', 'scam'
            ],
            confidence=0.9
        ),
        
        ContentCategory.PROFANITY: FilterRule(
            "profanity_basic",
            ContentCategory.PROFANITY,
            patterns=[],
            keywords=[
                # Common profanity (censored for production)
                'f***', 's***', 'damn', 'hell'
            ],
            confidence=0.95
        ),
        
        ContentCategory.SPAM: FilterRule(
            "spam_basic",
            ContentCategory.SPAM,
            patterns=[
                r'(?:click\s+here|buy\s+now|limited\s+offer){2,}',
                r'(?:\$\$\$|!!!)+'
            ],
            keywords=[
                'free', 'winner', 'congratulations', 'act now'
            ],
            confidence=0.7
        ),
    }
    
    def __init__(
        self,
        block_categories: List[str] = None,
        threshold: float = 0.8,
        action: str = 'block',
        custom_rules: List[FilterRule] = None,
        whitelist: List[str] = None,
        case_sensitive: bool = False
    ):
        """
        Initialize content filter.
        
        Args:
            block_categories: Categories to block
            threshold: Confidence threshold for blocking
            action: Action to take ('block', 'warn', 'sanitize', 'log')
            custom_rules: Custom filter rules
            whitelist: Words/phrases to never filter
            case_sensitive: Whether matching is case-sensitive
        """
        self.block_categories = self._parse_categories(block_categories)
        self.threshold = threshold
        self.action = FilterAction(action)
        self.custom_rules = custom_rules or []
        self.whitelist = set(w.lower() for w in (whitelist or []))
        self.case_sensitive = case_sensitive
        
        # Build active rules
        self.rules = []
        for category in self.block_categories:
            if category in self.BUILT_IN_RULES:
                self.rules.append(self.BUILT_IN_RULES[category])
        self.rules.extend(self.custom_rules)
        
        # Statistics
        self.total_checks = 0
        self.total_blocks = 0
        self.total_warnings = 0
        self.category_counts = {cat: 0 for cat in ContentCategory}
    
    def _parse_categories(self, categories: Optional[List[str]]) -> Set[ContentCategory]:
        """Parse category strings to ContentCategory enums"""
        if categories is None:
            return set(ContentCategory)
        
        result = set()
        for cat in categories:
            try:
                result.add(ContentCategory(cat))
            except ValueError:
                logger.warning(f"Unknown content category: {cat}")
        
        return result
    
    def _is_whitelisted(self, text: str) -> bool:
        """Check if text contains whitelisted content"""
        text_lower = text.lower()
        return any(word in text_lower for word in self.whitelist)
    
    def detect_patterns(self, text: str) -> List[ContentMatch]:
        """
        Detect harmful content using pattern matching.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of ContentMatch objects
        """
        matches = []
        search_text = text if self.case_sensitive else text.lower()
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            # Check regex patterns
            for pattern in rule.patterns:
                flags = 0 if self.case_sensitive else re.IGNORECASE
                for match in re.finditer(pattern, text, flags):
                    matched_text = match.group(0)
                    
                    # Skip if whitelisted
                    if self._is_whitelisted(matched_text):
                        continue
                    
                    matches.append(ContentMatch(
                        category=rule.category,
                        matched_text=matched_text,
                        confidence=rule.confidence,
                        start=match.start(),
                        end=match.end(),
                        rule_name=rule.name
                    ))
            
            # Check keywords
            for keyword in rule.keywords:
                check_keyword = keyword if self.case_sensitive else keyword.lower()
                if check_keyword in search_text:
                    # Skip if whitelisted
                    if self._is_whitelisted(keyword):
                        continue
                    
                    # Find position
                    start = search_text.find(check_keyword)
                    end = start + len(check_keyword)
                    
                    matches.append(ContentMatch(
                        category=rule.category,
                        matched_text=keyword,
                        confidence=rule.confidence,
                        start=start,
                        end=end,
                        rule_name=rule.name
                    ))
        
        return matches
    
    def calculate_category_scores(self, matches: List[ContentMatch]) -> Dict[ContentCategory, float]:
        """
        Calculate confidence scores for each category.
        
        Args:
            matches: List of content matches
            
        Returns:
            Dictionary mapping categories to confidence scores
        """
        scores = {}
        
        for match in matches:
            category = match.category
            if category not in scores:
                scores[category] = 0.0
            
            # Take maximum confidence for each category
            scores[category] = max(scores[category], match.confidence)
        
        return scores
    
    def sanitize(self, text: str, matches: List[ContentMatch]) -> str:
        """
        Sanitize text by removing harmful content.
        
        Args:
            text: Original text
            matches: List of content matches
            
        Returns:
            Sanitized text
        """
        if not matches:
            return text
        
        # Sort matches by position (reverse order for safe removal)
        sorted_matches = sorted(matches, key=lambda m: m.start, reverse=True)
        
        result = text
        for match in sorted_matches:
            # Replace with placeholder
            placeholder = f"[{match.category.value.upper()}_REMOVED]"
            result = result[:match.start] + placeholder + result[match.end:]
        
        return result
    
    def process(self, text: str) -> FilterResult:
        """
        Process text through content filter.
        
        Args:
            text: Text to filter
            
        Returns:
            FilterResult with processed text and metadata
            
        Raises:
            ContentFilterException: If action is 'block' and harmful content found
        """
        self.total_checks += 1
        
        # Detect harmful content
        matches = self.detect_patterns(text)
        category_scores = self.calculate_category_scores(matches)
        
        # Filter matches by threshold
        filtered_matches = [
            m for m in matches
            if m.confidence >= self.threshold
        ]
        
        # Update statistics
        for match in filtered_matches:
            self.category_counts[match.category] += 1
        
        # Take action
        was_blocked = False
        warnings = []
        filtered_text = text
        
        if filtered_matches:
            if self.action == FilterAction.BLOCK:
                self.total_blocks += 1
                was_blocked = True
                categories = set(m.category.value for m in filtered_matches)
                logger.warning(f"Blocked content containing: {', '.join(categories)}")
            
            elif self.action == FilterAction.WARN:
                self.total_warnings += 1
                categories = set(m.category.value for m in filtered_matches)
                warning = f"Content warning: {', '.join(categories)}"
                warnings.append(warning)
                logger.warning(warning)
            
            elif self.action == FilterAction.SANITIZE:
                filtered_text = self.sanitize(text, filtered_matches)
                logger.info(f"Sanitized {len(filtered_matches)} content matches")
            
            elif self.action == FilterAction.LOG:
                categories = set(m.category.value for m in filtered_matches)
                logger.info(f"Detected harmful content: {', '.join(categories)}")
        
        return FilterResult(
            original_text=text,
            filtered_text=filtered_text,
            was_blocked=was_blocked,
            warnings=warnings,
            matches=filtered_matches,
            category_scores=category_scores
        )
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get filtering statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_checks': self.total_checks,
            'total_blocks': self.total_blocks,
            'total_warnings': self.total_warnings,
            'category_counts': {
                cat.value: count
                for cat, count in self.category_counts.items()
                if count > 0
            }
        }
    
    def add_rule(self, rule: FilterRule) -> None:
        """Add a custom filter rule"""
        self.custom_rules.append(rule)
        self.rules.append(rule)
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a custom rule by name"""
        for i, rule in enumerate(self.custom_rules):
            if rule.name == rule_name:
                del self.custom_rules[i]
                self.rules = [r for r in self.rules if r.name != rule_name]
                return True
        return False


class ContentFilterException(Exception):
    """Raised when harmful content is detected and blocked"""
    
    def __init__(self, category: ContentCategory, reason: str = ""):
        self.category = category
        message = f"Content blocked: {category.value}"
        if reason:
            message += f" - {reason}"
        super().__init__(message)
