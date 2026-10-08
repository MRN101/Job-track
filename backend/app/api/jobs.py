"""Jobs API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.job import JobResponse, JobListResponse

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("", response_model=JobListResponse)
def list_jobs(
    country: Optional[str] = None,
    role: Optional[str] = None,
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    company: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("newest", regex="^(newest|salary|relevance)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List jobs with optional filters and pagination."""
    from app.models.job import Job

    query = db.query(Job)

    # Apply filters
    if country:
        query = query.filter(Job.country.ilike(f"%{country}%"))
    if role:
        query = query.filter(Job.title.ilike(f"%{role}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if experience_level:
        query = query.filter(Job.experience_level == experience_level)
    if company:
        query = query.filter(Job.company_name.ilike(f"%{company}%"))
    if search:
        query = query.filter(
            Job.title.ilike(f"%{search}%") | Job.description.ilike(f"%{search}%")
        )

    # Sorting
    if sort_by == "newest":
        query = query.order_by(Job.posted_at.desc().nullslast(), Job.collected_at.desc())
    elif sort_by == "salary":
        query = query.order_by(Job.salary_max.desc().nullslast())

    # Count total before pagination
    total = query.count()

    # Paginate
    offset = (page - 1) * page_size
    jobs = query.offset(offset).limit(page_size).all()

    # Build response
    job_responses = []
    for job in jobs:
        skills = [
            {
                "id": js.skill.id,
                "name": js.skill.name or js.skill.canonical_name,
                "category": js.skill.category,
                "confidence": js.confidence,
            }
            for js in job.job_skills
            if js.skill
        ]
        job_responses.append(
            JobResponse(
                id=job.id,
                source=job.source,
                external_id=job.external_id,
                title=job.title,
                company_name=job.company_name,
                location=job.location,
                country=job.country,
                description=job.description,
                salary_min=job.salary_min,
                salary_max=job.salary_max,
                salary_currency=job.salary_currency,
                employment_type=job.employment_type,
                experience_level=job.experience_level,
                posted_at=job.posted_at,
                url=job.url,
                collected_at=job.collected_at,
                skills=skills,
            )
        )

    return JobListResponse(
        jobs=job_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a single job by ID."""
    from app.models.job import Job
    from fastapi import HTTPException

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    skills = [
        {
            "id": js.skill.id,
            "name": js.skill.name or js.skill.canonical_name,
            "category": js.skill.category,
            "confidence": js.confidence,
        }
        for js in job.job_skills
        if js.skill
    ]

    return JobResponse(
        id=job.id,
        source=job.source,
        external_id=job.external_id,
        title=job.title,
        company_name=job.company_name,
        location=job.location,
        country=job.country,
        description=job.description,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        employment_type=job.employment_type,
        experience_level=job.experience_level,
        posted_at=job.posted_at,
        url=job.url,
        collected_at=job.collected_at,
        skills=skills,
    )
