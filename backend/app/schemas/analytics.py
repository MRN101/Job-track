"""Pydantic schemas for Analytics and Trends."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class AnalysisRunResponse(BaseModel):
    """Response for an analysis run."""
    id: int
    source: Optional[str] = "all"
    data_type: str = "real"
    country: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    time_period_start: Optional[datetime] = None
    time_period_end: Optional[datetime] = None
    jobs_analyzed: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SkillTrendResponse(BaseModel):
    """Trend data for a single skill."""
    skill_id: int
    skill_name: str
    category: Optional[str] = None
    current_percentage: float
    previous_percentage: Optional[float] = None
    change_pp: Optional[float] = None  # Change in percentage points
    current_job_count: int = 0
    previous_job_count: int = 0
    trend_direction: Optional[str] = None  # "up", "down", "stable"


class TrendsResponse(BaseModel):
    """Full trends response."""
    emerging: List[SkillTrendResponse]
    declining: List[SkillTrendResponse]
    period: str  # "7d", "30d", "90d", "6m"
    has_sufficient_data: bool
    current_period_label: Optional[str] = None
    previous_period_label: Optional[str] = None
    current_jobs_count: int = 0
    previous_jobs_count: int = 0
    message: Optional[str] = None


class SalaryStatistics(BaseModel):
    """Detailed statistically valid salary statistics."""
    min: Optional[float] = None
    max: Optional[float] = None
    median: Optional[float] = None
    p25: Optional[float] = None
    p75: Optional[float] = None
    currency: Optional[str] = None
    jobs_with_salary: int = 0


class DashboardMetrics(BaseModel):
    """Dashboard summary metrics."""
    jobs_analyzed: int = 0
    companies: int = 0
    unique_skills: int = 0
    median_salary: Optional[float] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_p25: Optional[float] = None
    salary_p75: Optional[float] = None
    salary_currency: Optional[str] = None
    jobs_with_salary: int = 0
    last_collection: Optional[datetime] = None
    last_analysis: Optional[datetime] = None
    data_type: str = "real"  # "real" or "demo"
    is_demo: bool = False
    sources_breakdown: Dict[str, int] = {}


class DataQualityMetrics(BaseModel):
    """Data quality and integrity metrics."""
    total_jobs: int = 0
    real_jobs: int = 0
    demo_jobs: int = 0
    jobs_with_description: int = 0
    jobs_with_salary: int = 0
    jobs_with_skills: int = 0
    duplicate_records_prevented: int = 0
    sources_breakdown: Dict[str, int] = {}
    last_collection_per_source: Dict[str, Optional[datetime]] = {}


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
    status: str  # "completed", "partial", "error"
    source: str
    retrieved: int = 0
    new_jobs: int = 0
    duplicates: int = 0
    errors: int = 0
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
