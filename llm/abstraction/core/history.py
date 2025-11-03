"""
Interaction History Management

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import deque
import json


@dataclass
class Interaction:
    """Represents a single LLM interaction"""
    prompt: str
    response: str
    model: str
    provider: str
    timestamp: datetime = field(default_factory=datetime.now)
    tokens_used: int = 0
    cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Interaction':
        """Create from dictionary"""
        if isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class InteractionHistory:
    """
    Manages interaction history with configurable size limit.
    
    Uses a deque for efficient FIFO operations when history limit is reached.
    """
    
    def __init__(self, max_size: int = 50):
        """
        Initialize history manager.
        
        Args:
            max_size: Maximum number of interactions to store
        """
        self.max_size = max_size
        self._history: deque[Interaction] = deque(maxlen=max_size)
        self._total_tokens: int = 0
        self._total_cost: float = 0.0
    
    def add(self, interaction: Interaction) -> None:
        """
        Add an interaction to history.
        
        Args:
            interaction: Interaction to add
        """
        # If we're at max size and adding a new item, we'll lose the oldest
        if len(self._history) == self.max_size and self.max_size > 0:
            oldest = self._history[0]
            self._total_tokens -= oldest.tokens_used
            self._total_cost -= oldest.cost
        
        self._history.append(interaction)
        self._total_tokens += interaction.tokens_used
        self._total_cost += interaction.cost
    
    def get_all(self) -> List[Interaction]:
        """
        Get all interactions.
        
        Returns:
            List of interactions in chronological order
        """
        return list(self._history)
    
    def get_recent(self, n: int) -> List[Interaction]:
        """
        Get the n most recent interactions.
        
        Args:
            n: Number of interactions to retrieve
            
        Returns:
            List of most recent interactions
        """
        if n <= 0:
            return []
        return list(self._history)[-n:]
    
    def get_by_model(self, model: str) -> List[Interaction]:
        """
        Get all interactions for a specific model.
        
        Args:
            model: Model name to filter by
            
        Returns:
            List of interactions using the specified model
        """
        return [i for i in self._history if i.model == model]
    
    def get_by_provider(self, provider: str) -> List[Interaction]:
        """
        Get all interactions for a specific provider.
        
        Args:
            provider: Provider name to filter by
            
        Returns:
            List of interactions using the specified provider
        """
        return [i for i in self._history if i.provider == provider]
    
    def search(self, query: str, case_sensitive: bool = False) -> List[Interaction]:
        """
        Search interactions by content.
        
        Args:
            query: Search query
            case_sensitive: Whether search is case-sensitive
            
        Returns:
            List of matching interactions
        """
        if not case_sensitive:
            query = query.lower()
            
        results = []
        for interaction in self._history:
            prompt = interaction.prompt if case_sensitive else interaction.prompt.lower()
            response = interaction.response if case_sensitive else interaction.response.lower()
            
            if query in prompt or query in response:
                results.append(interaction)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the history.
        
        Returns:
            Dictionary containing statistics
        """
        if not self._history:
            return {
                'total_interactions': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'average_tokens': 0,
                'average_cost': 0.0,
                'providers': {},
                'models': {}
            }
        
        providers: Dict[str, int] = {}
        models: Dict[str, int] = {}
        
        for interaction in self._history:
            providers[interaction.provider] = providers.get(interaction.provider, 0) + 1
            models[interaction.model] = models.get(interaction.model, 0) + 1
        
        total = len(self._history)
        
        return {
            'total_interactions': total,
            'total_tokens': self._total_tokens,
            'total_cost': round(self._total_cost, 4),
            'average_tokens': self._total_tokens // total if total > 0 else 0,
            'average_cost': round(self._total_cost / total, 4) if total > 0 else 0.0,
            'providers': providers,
            'models': models
        }
    
    def clear(self) -> None:
        """Clear all history"""
        self._history.clear()
        self._total_tokens = 0
        self._total_cost = 0.0
    
    def export_to_json(self, filepath: str) -> None:
        """
        Export history to JSON file.
        
        Args:
            filepath: Path to output file
        """
        data = {
            'max_size': self.max_size,
            'statistics': self.get_statistics(),
            'interactions': [i.to_dict() for i in self._history]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def import_from_json(self, filepath: str) -> None:
        """
        Import history from JSON file.
        
        Args:
            filepath: Path to input file
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.clear()
        
        for interaction_data in data.get('interactions', []):
            interaction = Interaction.from_dict(interaction_data)
            self.add(interaction)
    
    def __len__(self) -> int:
        """Get number of interactions in history"""
        return len(self._history)
    
    def __iter__(self):
        """Iterate over interactions"""
        return iter(self._history)
