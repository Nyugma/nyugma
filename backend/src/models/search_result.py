"""
Search result data model for legal case similarity search.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchResult:
    """
    Represents a search result from similarity search.
    
    Attributes:
        case_id: Unique identifier for the case
        title: Case title or name
        date: Case date as string
        similarity_score: Cosine similarity score (0-1)
        snippet: Brief text excerpt from the case
        file_path: Path to the original case file
    """
    case_id: str
    title: str
    date: str
    similarity_score: float
    snippet: str
    file_path: str
    
    def __post_init__(self):
        """Validate similarity score is within valid range."""
        # Clamp similarity score to [0, 1] range to handle floating point precision issues
        self.similarity_score = max(0.0, min(1.0, self.similarity_score))
        
        if not 0.0 <= self.similarity_score <= 1.0:
            raise ValueError(f"Similarity score must be between 0 and 1, got {self.similarity_score}")