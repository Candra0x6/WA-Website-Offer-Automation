"""
Business Data Model
Represents a business entity with contact and website information.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Business:
    """Data model for a business entity."""
    
    business_name: str
    phone: str
    description: Optional[str] = None
    website: Optional[str] = None
    google_maps_link: Optional[str] = None
    
    def has_website(self) -> bool:
        """Check if business has a website."""
        return bool(self.website and self.website.strip())
    
    def __str__(self) -> str:
        """String representation of the business."""
        return f"Business(name={self.business_name}, phone={self.phone}, has_website={self.has_website()})"
