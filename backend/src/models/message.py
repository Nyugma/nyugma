"""
Message model for user-to-user messaging.
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.config.database import Base


class Message(Base):
    """
    Message model representing messages between users.
    """
    __tablename__ = "messages"
    
    # Primary identification
    message_id = Column(String(50), primary_key=True, index=True)
    
    # Connection reference
    connection_id = Column(String(50), ForeignKey('connections.connection_id'), nullable=False, index=True)
    
    # User references
    sender_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    receiver_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    
    # Message content
    content = Column(Text, nullable=False)
    
    # Status
    is_read = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        """Convert message to dictionary."""
        return {
            'message_id': self.message_id,
            'connection_id': self.connection_id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }
    
    def __repr__(self):
        return f"<Message {self.message_id} ({self.sender_id} -> {self.receiver_id})>"
