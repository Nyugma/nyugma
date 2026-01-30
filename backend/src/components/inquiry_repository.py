"""
Inquiry Repository
Handles storage and retrieval of legal inquiries
"""

import json
import os
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path


class InquiryRepository:
    """Repository for managing legal inquiries"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the inquiry repository
        
        Args:
            data_dir: Directory to store inquiry data
        """
        self.data_dir = Path(data_dir)
        self.inquiries_dir = self.data_dir / "inquiries"
        self.inquiries_file = self.data_dir / "inquiries.json"
        
        # Create directories if they don't exist
        self.inquiries_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize inquiries file if it doesn't exist
        if not self.inquiries_file.exists():
            self._save_inquiries([])
    
    def _generate_inquiry_id(self) -> str:
        """Generate a unique inquiry ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        inquiries = self._load_inquiries()
        
        # Count inquiries from today
        today_count = sum(1 for inq in inquiries if inq.get('inquiry_id', '').startswith(f"INQ-{timestamp}"))
        
        return f"INQ-{timestamp}-{today_count + 1:03d}"
    
    def _load_inquiries(self) -> List[Dict]:
        """Load all inquiries from file"""
        try:
            with open(self.inquiries_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_inquiries(self, inquiries: List[Dict]) -> None:
        """Save inquiries to file"""
        with open(self.inquiries_file, 'w', encoding='utf-8') as f:
            json.dump(inquiries, f, indent=2, ensure_ascii=False)
    
    def create_inquiry(self, inquiry_data: Dict) -> Dict:
        """
        Create a new inquiry
        
        Args:
            inquiry_data: Dictionary containing inquiry information
            
        Returns:
            Created inquiry with generated ID and timestamps
        """
        # Generate inquiry ID
        inquiry_id = self._generate_inquiry_id()
        
        # Add metadata
        created_at = datetime.now().isoformat()
        
        inquiry = {
            "inquiry_id": inquiry_id,
            **inquiry_data,
            "status": "pending",
            "created_at": created_at
        }
        
        # Ensure submitted_at is set
        if not inquiry.get('submitted_at'):
            inquiry['submitted_at'] = created_at
        
        # Load existing inquiries
        inquiries = self._load_inquiries()
        
        # Add new inquiry
        inquiries.append(inquiry)
        
        # Save to file
        self._save_inquiries(inquiries)
        
        # Also save individual inquiry file for easy access
        self._save_individual_inquiry(inquiry)
        
        return inquiry
    
    def _save_individual_inquiry(self, inquiry: Dict) -> None:
        """Save individual inquiry to separate file"""
        inquiry_file = self.inquiries_dir / f"{inquiry['inquiry_id']}.json"
        with open(inquiry_file, 'w', encoding='utf-8') as f:
            json.dump(inquiry, f, indent=2, ensure_ascii=False)
    
    def get_inquiry(self, inquiry_id: str) -> Optional[Dict]:
        """
        Get a specific inquiry by ID
        
        Args:
            inquiry_id: The inquiry ID
            
        Returns:
            Inquiry data or None if not found
        """
        inquiries = self._load_inquiries()
        
        for inquiry in inquiries:
            if inquiry.get('inquiry_id') == inquiry_id:
                return inquiry
        
        return None
    
    def get_all_inquiries(self, 
                         status: Optional[str] = None,
                         limit: Optional[int] = None,
                         offset: int = 0) -> List[Dict]:
        """
        Get all inquiries with optional filtering
        
        Args:
            status: Filter by status (pending, reviewed, contacted, closed)
            limit: Maximum number of inquiries to return
            offset: Number of inquiries to skip
            
        Returns:
            List of inquiries
        """
        inquiries = self._load_inquiries()
        
        # Filter by status if provided
        if status:
            inquiries = [inq for inq in inquiries if inq.get('status') == status]
        
        # Sort by created_at (newest first)
        inquiries.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Apply pagination
        if limit:
            inquiries = inquiries[offset:offset + limit]
        else:
            inquiries = inquiries[offset:]
        
        return inquiries
    
    def update_inquiry_status(self, inquiry_id: str, status: str) -> Optional[Dict]:
        """
        Update inquiry status
        
        Args:
            inquiry_id: The inquiry ID
            status: New status (pending, reviewed, contacted, closed)
            
        Returns:
            Updated inquiry or None if not found
        """
        inquiries = self._load_inquiries()
        
        for i, inquiry in enumerate(inquiries):
            if inquiry.get('inquiry_id') == inquiry_id:
                inquiry['status'] = status
                inquiry['updated_at'] = datetime.now().isoformat()
                inquiries[i] = inquiry
                
                # Save updated inquiries
                self._save_inquiries(inquiries)
                self._save_individual_inquiry(inquiry)
                
                return inquiry
        
        return None
    
    def delete_inquiry(self, inquiry_id: str) -> bool:
        """
        Delete an inquiry
        
        Args:
            inquiry_id: The inquiry ID
            
        Returns:
            True if deleted, False if not found
        """
        inquiries = self._load_inquiries()
        
        # Find and remove inquiry
        original_length = len(inquiries)
        inquiries = [inq for inq in inquiries if inq.get('inquiry_id') != inquiry_id]
        
        if len(inquiries) < original_length:
            # Save updated list
            self._save_inquiries(inquiries)
            
            # Delete individual file
            inquiry_file = self.inquiries_dir / f"{inquiry_id}.json"
            if inquiry_file.exists():
                inquiry_file.unlink()
            
            return True
        
        return False
    
    def get_statistics(self) -> Dict:
        """
        Get inquiry statistics
        
        Returns:
            Dictionary with statistics
        """
        inquiries = self._load_inquiries()
        
        total = len(inquiries)
        pending = sum(1 for inq in inquiries if inq.get('status') == 'pending')
        reviewed = sum(1 for inq in inquiries if inq.get('status') == 'reviewed')
        contacted = sum(1 for inq in inquiries if inq.get('status') == 'contacted')
        closed = sum(1 for inq in inquiries if inq.get('status') == 'closed')
        
        # Count by urgency
        urgent = sum(1 for inq in inquiries if inq.get('urgency') == 'urgent')
        high = sum(1 for inq in inquiries if inq.get('urgency') == 'high')
        
        # Count by case type
        case_types = {}
        for inq in inquiries:
            case_type = inq.get('case_type', 'unknown')
            case_types[case_type] = case_types.get(case_type, 0) + 1
        
        return {
            "total_inquiries": total,
            "by_status": {
                "pending": pending,
                "reviewed": reviewed,
                "contacted": contacted,
                "closed": closed
            },
            "by_urgency": {
                "urgent": urgent,
                "high": high
            },
            "by_case_type": case_types
        }
