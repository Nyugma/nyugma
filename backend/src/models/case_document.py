"""
Case document data model for legal case repository management.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
import numpy as np


@dataclass
class CaseDocument:
    """
    Represents a legal case document in the repository.
    
    Attributes:
        case_id: Unique identifier for the case
        title: Case title or name
        date: Case date
        file_path: Path to the original PDF file
        text_content: Extracted text content from the PDF
        vector: Pre-computed TF-IDF vector (optional, loaded separately)
        metadata: Additional metadata dictionary
    """
    case_id: str
    title: str
    date: datetime
    file_path: str
    text_content: str
    vector: Optional[np.ndarray] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert case document to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation (excluding vector and text_content)
        """
        return {
            'case_id': self.case_id,
            'title': self.title,
            'date': self.date.isoformat(),
            'file_path': self.file_path,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], text_content: str = "") -> 'CaseDocument':
        """
        Create CaseDocument from dictionary.
        
        Args:
            data: Dictionary with case metadata
            text_content: Text content (loaded separately)
            
        Returns:
            CaseDocument instance
        """
        return cls(
            case_id=data['case_id'],
            title=data['title'],
            date=datetime.fromisoformat(data['date']),
            file_path=data['file_path'],
            text_content=text_content,
            metadata=data.get('metadata', {})
        )
    
    def get_snippet(self, max_length: int = 200) -> str:
        """
        Get a text snippet from the document.
        
        Args:
            max_length: Maximum length of the snippet
            
        Returns:
            Text snippet
        """
        if len(self.text_content) <= max_length:
            return self.text_content
        return self.text_content[:max_length] + "..."