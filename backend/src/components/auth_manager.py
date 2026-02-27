"""
Authentication manager for user authentication and JWT token handling.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


class AuthManager:
    """
    Handles authentication operations including password hashing and JWT tokens.
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and verify a JWT access token.
        
        Args:
            token: JWT token to decode
            
        Returns:
            Decoded token data if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except InvalidTokenError:
            return None
    
    @staticmethod
    def generate_user_id(email: str) -> str:
        """
        Generate a unique user ID from email.
        
        Args:
            email: User's email address
            
        Returns:
            Generated user ID
        """
        # Use first part of email + timestamp + random string
        email_prefix = email.split('@')[0][:8]
        timestamp = datetime.now().strftime('%Y%m%d')
        random_suffix = secrets.token_hex(4)
        
        return f"user_{email_prefix}_{timestamp}_{random_suffix}"
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """
        Validate email format.
        
        Args:
            email: Email to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        import re
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_regex, email):
            return False, "Invalid email format"
        
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> tuple[bool, str]:
        """
        Validate Indian phone number format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        import re
        
        # Remove spaces and special characters
        phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check for Indian phone number format
        # Accepts: +91XXXXXXXXXX, 91XXXXXXXXXX, XXXXXXXXXX
        phone_regex = r'^(\+91|91)?[6-9]\d{9}$'
        
        if not re.match(phone_regex, phone_clean):
            return False, "Invalid phone number format. Use Indian mobile number (10 digits starting with 6-9)"
        
        return True, ""


# Create singleton instance
auth_manager = AuthManager()
