"""
Enhanced case model for helper users (experienced litigants).
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
import numpy as np


@dataclass
class HelperCase:
    """
    Represents a case submitted by an experienced litigant (helper).
    
    Attributes:
        case_id: Unique identifier for the case
        user_id: ID of the helper who submitted this case
        title: Case title or name
        case_type: Type of case (civil, criminal, property, etc.)
        description: Brief description of the case
        outcome: Case outcome (won, lost, settled, ongoing)
        duration_months: How long the case took (in months)
        total_cost: Total cost incurred (in INR)
        court_name: Name of the court
        state: State where case was filed
        city: City where case was filed
        lawyer_name: Name of the lawyer (optional)
        lawyer_contact: Lawyer's contact (optional)
        key_learnings: Important lessons learned
        advice_for_others: Advice for people in similar situations
        file_path: Path to the original PDF file
        text_content: Extracted text content from the PDF
        vector: Pre-computed TF-IDF vector
        is_public: Whether this case is visible to others
        willing_to_help: Whether user is willing to be contacted
        created_at: When this case was added
        updated_at: When this case was last updated
    """
    case_id: str
    user_id: str
    title: str
    case_type: str
    description: str
    outcome: str
    duration_months: int
    total_cost: float
    court_name: str
    state: str
    city: str
    file_path: str
    text_content: str
    is_public: bool = True
    willing_to_help: bool = True
    lawyer_name: Optional[str] = None
    lawyer_contact: Optional[str] = None
    key_learnings: Optional[str] = None
    advice_for_others: Optional[str] = None
    vector: Optional[np.ndarray] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert case to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation (excluding vector and text_content)
        """
        return {
            'case_id': self.case_id,
            'user_id': self.user_id,
            'title': self.title,
            'case_type': self.case_type,
            'description': self.description,
            'outcome': self.outcome,
            'duration_months': self.duration_months,
            'total_cost': self.total_cost,
            'court_name': self.court_name,
            'state': self.state,
            'city': self.city,
            'lawyer_name': self.lawyer_name,
            'lawyer_contact': self.lawyer_contact,
            'key_learnings': self.key_learnings,
            'advice_for_others': self.advice_for_others,
            'file_path': self.file_path,
            'is_public': self.is_public,
            'willing_to_help': self.willing_to_help,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], text_content: str = "") -> 'HelperCase':
        """
        Create HelperCase from dictionary.
        
        Args:
            data: Dictionary with case metadata
            text_content: Text content (loaded separately)
            
        Returns:
            HelperCase instance
        """
        return cls(
            case_id=data['case_id'],
            user_id=data['user_id'],
            title=data['title'],
            case_type=data['case_type'],
            description=data['description'],
            outcome=data['outcome'],
            duration_months=data['duration_months'],
            total_cost=data['total_cost'],
            court_name=data['court_name'],
            state=data['state'],
            city=data['city'],
            file_path=data['file_path'],
            text_content=text_content,
            lawyer_name=data.get('lawyer_name'),
            lawyer_contact=data.get('lawyer_contact'),
            key_learnings=data.get('key_learnings'),
            advice_for_others=data.get('advice_for_others'),
            is_public=data.get('is_public', True),
            willing_to_help=data.get('willing_to_help', True),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
