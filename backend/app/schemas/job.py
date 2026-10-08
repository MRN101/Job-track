"""Pydantic schemas for Jobs."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobBase(BaseModel):
    """Base job schema."""
    title: str
    company_name: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    url: Optional[str] = None


class JobCreate(JobBase):
    """Schema for creating a job."""
    source: str
    external_id: Optional[str] = None
    description: Optional[str] = None
    posted_at: Optional[datetime] = None


class SkillInJob(BaseModel):
    """Skill info embedded in a job response."""
    id: int
    name: str
    category: Optional[str] = None
    confidence: float = 1.0

    model_config = {"from_attributes": True}


class JobResponse(JobBase):
    """Schema for returning a job."""
    id: int
    source: str
    external_id: Optional[str] = None
    description: Optional[str] = None
    posted_at: Optional[datetime] = None
    collected_at: datetime
    skills: List[SkillInJob] = []

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    """Paginated job list response."""
    jobs: List[JobResponse]
    total: int
    page: int
    page_size: int


class JobFilters(BaseModel):
    """Filters for querying jobs."""
    country: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    company: Optional[str] = None
    skill: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None
    sort_by: Optional[str] = "newest"
    page: int = 1
    page_size: int = 20
