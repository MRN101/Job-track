"""Pydantic schemas for Skills."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SkillBase(BaseModel):
    """Base skill schema."""
    name: str
    canonical_name: str
    category: Optional[str] = None
    description: Optional[str] = None


class SkillCreate(SkillBase):
    """Schema for creating a skill."""
    pass


class SkillResponse(SkillBase):
    """Schema for returning a skill."""
    id: int
    job_count: Optional[int] = None
    demand_percentage: Optional[float] = None

    model_config = {"from_attributes": True}


class SkillDemandResponse(BaseModel):
    """Skill demand data for analytics."""
    skill_id: int
    skill_name: str
    category: Optional[str] = None
    job_count: int
    percentage: float
    trend: Optional[float] = None  # Change in percentage points

    model_config = {"from_attributes": True}


class TopSkillsResponse(BaseModel):
    """Response for top skills endpoint."""
    skills: List[SkillDemandResponse]
    total_jobs: int
    analysis_run_id: Optional[int] = None


class SkillCategoryResponse(BaseModel):
    """Skills grouped by category."""
    category: str
    skills: List[SkillDemandResponse]
