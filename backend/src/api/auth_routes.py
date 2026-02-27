"""
Authentication API routes for user registration, login, and profile management.
"""

import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.models.user import User
from src.components.auth_manager import auth_manager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class RegisterRequest(BaseModel):
    """Request model for user registration."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password")
    full_name: str = Field(..., min_length=2, max_length=255, description="User's full name")
    phone: Optional[str] = Field(None, description="User's phone number")
    city: Optional[str] = Field(None, description="User's city")
    state: Optional[str] = Field(None, description="User's state")
    user_type: str = Field(..., description="User type: 'new_litigant' or 'helper'")


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class AuthResponse(BaseModel):
    """Response model for authentication."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: dict = Field(..., description="User information")


class UserProfileResponse(BaseModel):
    """Response model for user profile."""
    user_id: str
    email: str
    full_name: str
    phone: Optional[str]
    city: Optional[str]
    state: Optional[str]
    bio: Optional[str]
    user_type: str
    is_verified: bool
    reputation_score: float
    cases_helped: int
    total_ratings: int
    created_at: str


class UpdateProfileRequest(BaseModel):
    """Request model for updating user profile."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    bio: Optional[str] = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        authorization: Authorization header with Bearer token
        db: Database session
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    payload = auth_manager.decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account"
)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Args:
        request: Registration request data
        db: Database session
        
    Returns:
        Authentication response with token and user info
        
    Raises:
        HTTPException: If validation fails or user already exists
    """
    try:
        # Validate email
        is_valid, error_msg = auth_manager.validate_email(request.email)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Validate password strength
        is_valid, error_msg = auth_manager.validate_password_strength(request.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Validate phone if provided
        if request.phone:
            is_valid, error_msg = auth_manager.validate_phone(request.phone)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
        
        # Validate user type
        if request.user_type not in ['new_litigant', 'helper']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User type must be 'new_litigant' or 'helper'"
            )
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        
        if request.phone:
            existing_phone = db.query(User).filter(User.phone == request.phone).first()
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this phone number already exists"
                )
        
        # Generate user ID
        user_id = auth_manager.generate_user_id(request.email)
        
        # Hash password
        password_hash = auth_manager.hash_password(request.password)
        
        # Create new user
        new_user = User(
            user_id=user_id,
            email=request.email,
            password_hash=password_hash,
            full_name=request.full_name,
            phone=request.phone,
            city=request.city,
            state=request.state,
            user_type=request.user_type,
            is_verified=False,
            is_active=True,
            reputation_score=0.0,
            cases_helped=0,
            total_ratings=0
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user registered: {user_id} ({request.email})")
        
        # Create access token
        access_token = auth_manager.create_access_token(data={"sub": user_id})
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=new_user.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User login",
    description="Authenticate user and get access token"
)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.
    
    Args:
        request: Login request data
        db: Database session
        
    Returns:
        Authentication response with token and user info
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not auth_manager.verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        logger.info(f"User logged in: {user.user_id} ({user.email})")
        
        # Create access token
        access_token = auth_manager.create_access_token(data={"sub": user.user_id})
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=user.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current user profile",
    description="Get profile information of currently authenticated user"
)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User profile information
    """
    return UserProfileResponse(**current_user.to_dict())


@router.put(
    "/me",
    response_model=UserProfileResponse,
    summary="Update user profile",
    description="Update profile information of currently authenticated user"
)
async def update_user_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.
    
    Args:
        request: Update profile request data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user profile information
    """
    try:
        # Update fields if provided
        if request.full_name is not None:
            current_user.full_name = request.full_name
        
        if request.phone is not None:
            # Validate phone
            is_valid, error_msg = auth_manager.validate_phone(request.phone)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
            
            # Check if phone already exists
            existing_phone = db.query(User).filter(
                User.phone == request.phone,
                User.user_id != current_user.user_id
            ).first()
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Phone number already in use"
                )
            
            current_user.phone = request.phone
        
        if request.city is not None:
            current_user.city = request.city
        
        if request.state is not None:
            current_user.state = request.state
        
        if request.bio is not None:
            current_user.bio = request.bio
        
        current_user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"User profile updated: {current_user.user_id}")
        
        return UserProfileResponse(**current_user.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}"
        )


@router.get(
    "/users/{user_id}",
    response_model=UserProfileResponse,
    summary="Get user profile by ID",
    description="Get public profile information of any user"
)
async def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    """
    Get user profile by user ID.
    
    Args:
        user_id: User ID to retrieve
        db: Database session
        
    Returns:
        User profile information
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserProfileResponse(**user.to_dict())
