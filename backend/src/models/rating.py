"""
Rating model for user ratings and feedback.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.config.database import Base


class Rating(Base):
    """
    Rating model representing ratings between users.
    """
    __tablename__ = "ratings"
    
    # Primary identification
    rating_id = Column(String(50), primary_key=True, index=True)
    
    # Connection reference
    connection_id = Column(String(50), ForeignKey('connections.connection_id'), nullable=False, index=True)
    
    # User references
    rater_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    rated_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    
    # Rating details
    rating = Column(Integer, nullable=False)  # 1-5 stars
    feedback = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert rating to dictionary."""
        return {
            'rating_id': self.rating_id,
            'connection_id': self.connection_id,
            'rater_id': self.rater_id,
            'rated_id': self.rated_id,
            'rating': self.rating,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<Rating {self.rating_id} ({self.rater_id} -> {self.rated_id}: {self.rating}/5)>"
