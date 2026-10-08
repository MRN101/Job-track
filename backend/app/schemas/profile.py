"""Pydantic schemas for User Profile."""

from pydantic import BaseModel
from typing import Optional, List


class ProfileBase(BaseModel):
    """Base profile schema."""
    name: Optional[str] = None
    country: str = "India"
    preferred_locations: List[str] = []
    target_roles: List[str] = ["Software Engineer"]
    experience_level: str = "0-2 years"
    skills: List[str] = []


class ProfileUpdate(ProfileBase):
    """Schema for updating the profile."""
    pass


class ProfileResponse(ProfileBase):
    """Schema for returning the profile."""
    id: int

    model_config = {"from_attributes": True}
