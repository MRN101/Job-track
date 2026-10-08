"""Pydantic schemas for Analytics and Trends."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AnalysisRunResponse(BaseModel):
    """Response for an analysis run."""
    id: int
    country: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    jobs_analyzed: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TrendDataPoint(BaseModel):
    """A single point in a trend timeline."""
    date: datetime
    percentage: float
    job_count: int


class SkillTrendResponse(BaseModel):
    """Trend data for a single skill."""
    skill_id: int
    skill_name: str
    category: Optional[str] = None
    current_percentage: float
    previous_percentage: Optional[float] = None
    change_pp: Optional[float] = None  # Change in percentage points
    trend_direction: Optional[str] = None  # "up", "down", "stable"
    data_points: List[TrendDataPoint] = []


class TrendsResponse(BaseModel):
    """Full trends response."""
    emerging: List[SkillTrendResponse]
    declining: List[SkillTrendResponse]
    period: str  # "7d", "30d", "90d", "6m"
    has_sufficient_data: bool


class DashboardMetrics(BaseModel):
    """Dashboard summary metrics."""
    jobs_analyzed: int = 0
    companies: int = 0
    unique_skills: int = 0
    median_salary: Optional[float] = None
    salary_currency: Optional[str] = None
    last_collection: Optional[datetime] = None
    last_analysis: Optional[datetime] = None


class DashboardFilters(BaseModel):
    """Current dashboard filter state."""
    country: str = "India"
    role: str = "Software Engineer"
    experience_level: str = "0-2 years"
    location: str = "All locations"
    time_period: str = "30d"


class CollectionRequest(BaseModel):
    """Request to start a job collection."""
    country: str = "India"
    role: str = "Software Engineer"
    location: Optional[str] = None
    experience_level: Optional[str] = None
    keywords: Optional[List[str]] = None
    max_results: int = 100


class CollectionStatus(BaseModel):
    """Status of a job collection."""
    status: str  # "running", "completed", "error"
    source: str
    retrieved: int = 0
    new_jobs: int = 0
    duplicates: int = 0
    errors: int = 0
    message: Optional[str] = None
