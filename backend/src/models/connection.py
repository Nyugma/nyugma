"""
Connection model for managing connections between users.
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.config.database import Base


class Connection(Base):
    """
    Connection model representing a connection request between users.
    """
    __tablename__ = "connections"
    
    # Primary identification
    connection_id = Column(String(50), primary_key=True, index=True)
    
    # User references
    requester_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    helper_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    
    # Case references
    requester_case_id = Column(String(100), nullable=True)
    helper_case_id = Column(String(100), nullable=True)
    
    # Connection details
    similarity_score = Column(Float, nullable=True)
    status = Column(String(20), nullable=False, default='pending')  # pending, accepted, declined, completed
    message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        """Convert connection to dictionary."""
        return {
            'connection_id': self.connection_id,
            'requester_id': self.requester_id,
            'helper_id': self.helper_id,
            'requester_case_id': self.requester_case_id,
            'helper_case_id': self.helper_case_id,
            'similarity_score': self.similarity_score,
            'status': self.status,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self):
        return f"<Connection {self.connection_id} ({self.requester_id} -> {self.helper_id})>"
