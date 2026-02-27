"""
User model for authentication and profile management.
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, Float, DateTime, Text
from sqlalchemy.orm import relationship
from src.config.database import Base


class User(Base):
    """
    User model representing both new litigants and helpers.
    """
    __tablename__ = "users"
    
    # Primary identification
    user_id = Column(String(50), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile information
    full_name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    profile_picture = Column(String(500), nullable=True)
    
    # User type and status
    user_type = Column(String(20), nullable=False)  # 'new_litigant' or 'helper'
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Reputation and statistics
    reputation_score = Column(Float, default=0.0)
    cases_helped = Column(Float, default=0)
    total_ratings = Column(Float, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships (will be defined when other models are created)
    # connections_sent = relationship("Connection", foreign_keys="Connection.requester_id", back_populates="requester")
    # connections_received = relationship("Connection", foreign_keys="Connection.helper_id", back_populates="helper")
    # messages_sent = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    # messages_received = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")
    # ratings_given = relationship("Rating", foreign_keys="Rating.rater_id", back_populates="rater")
    # ratings_received = relationship("Rating", foreign_keys="Rating.rated_id", back_populates="rated")
    
    def to_dict(self, include_sensitive=False):
        """
        Convert user to dictionary.
        
        Args:
            include_sensitive: Whether to include sensitive fields like password_hash
            
        Returns:
            Dictionary representation of user
        """
        data = {
            'user_id': self.user_id,
            'email': self.email,
            'phone': self.phone,
            'full_name': self.full_name,
            'city': self.city,
            'state': self.state,
            'bio': self.bio,
            'profile_picture': self.profile_picture,
            'user_type': self.user_type,
            'is_verified': self.is_verified,
            'is_active': self.is_active,
            'reputation_score': self.reputation_score,
            'cases_helped': self.cases_helped,
            'total_ratings': self.total_ratings,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
            
        return data
    
    def __repr__(self):
        return f"<User {self.user_id} ({self.email})>"
