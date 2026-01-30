"""
Inquiry Data Model
Represents a legal inquiry submitted by a user
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class InquiryCreate(BaseModel):
    """Model for creating a new inquiry"""
    case_id: Optional[str] = Field(None, description="Reference case ID if applicable")
    case_type: str = Field(..., description="Type of legal case")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name of the client")
    phone_number: str = Field(..., description="Contact phone number")
    email: Optional[str] = Field(None, description="Email address")
    city: str = Field(..., description="City of residence")
    state: str = Field(..., description="State of residence")
    case_description: str = Field(..., min_length=10, description="Brief description of the case")
    requirements: str = Field(..., min_length=10, description="Client requirements")
    expectations: str = Field(..., min_length=10, description="Client expectations")
    urgency: str = Field(..., description="Urgency level")
    preferred_date: Optional[str] = Field(None, description="Preferred consultation date")
    previous_lawyer: str = Field(default="no", description="Whether consulted a lawyer before")
    budget_range: str = Field(..., description="Budget range for legal services")
    additional_notes: Optional[str] = Field(None, description="Additional notes")
    submitted_at: Optional[str] = Field(None, description="Submission timestamp")

    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format"""
        # Remove spaces and special characters
        cleaned = ''.join(filter(str.isdigit, v))
        if len(cleaned) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return v

    @validator('email')
    def validate_email(cls, v):
        """Validate email format if provided"""
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v

    class Config:
        schema_extra = {
            "example": {
                "case_id": "case_001",
                "case_type": "civil",
                "full_name": "Rajesh Kumar",
                "phone_number": "+91 98765 43210",
                "email": "rajesh.kumar@example.com",
                "city": "Mumbai",
                "state": "Maharashtra",
                "case_description": "Property dispute with neighbor regarding boundary wall",
                "requirements": "Legal consultation and representation in civil court",
                "expectations": "Peaceful resolution through mediation or court order",
                "urgency": "medium",
                "preferred_date": "2026-02-01",
                "previous_lawyer": "no",
                "budget_range": "50k-1l",
                "additional_notes": "Available for consultation on weekdays after 5 PM"
            }
        }


class InquiryResponse(BaseModel):
    """Model for inquiry response"""
    inquiry_id: str
    case_id: Optional[str]
    case_type: str
    full_name: str
    phone_number: str
    email: Optional[str]
    city: str
    state: str
    case_description: str
    requirements: str
    expectations: str
    urgency: str
    preferred_date: Optional[str]
    previous_lawyer: str
    budget_range: str
    additional_notes: Optional[str]
    status: str = "pending"
    submitted_at: str
    created_at: str

    class Config:
        schema_extra = {
            "example": {
                "inquiry_id": "INQ-20260123-001",
                "case_id": "case_001",
                "case_type": "civil",
                "full_name": "Rajesh Kumar",
                "phone_number": "+91 98765 43210",
                "email": "rajesh.kumar@example.com",
                "city": "Mumbai",
                "state": "Maharashtra",
                "case_description": "Property dispute with neighbor",
                "requirements": "Legal consultation and representation",
                "expectations": "Peaceful resolution",
                "urgency": "medium",
                "preferred_date": "2026-02-01",
                "previous_lawyer": "no",
                "budget_range": "50k-1l",
                "additional_notes": "Available on weekdays after 5 PM",
                "status": "pending",
                "submitted_at": "2026-01-23T10:30:00Z",
                "created_at": "2026-01-23T10:30:00Z"
            }
        }


class InquiryListResponse(BaseModel):
    """Model for listing inquiries"""
    total: int
    inquiries: list[InquiryResponse]
    
    class Config:
        schema_extra = {
            "example": {
                "total": 10,
                "inquiries": []
            }
        }
