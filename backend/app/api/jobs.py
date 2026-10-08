"""Jobs API endpoints."""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobResponse, JobListResponse, SkillInJob
from app.services.query_service import get_jobs_query

from app.analyzers.role_classifier import ROLE_TAXONOMY, get_all_role_families, get_roles_for_family

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/taxonomy")
def get_taxonomy():
    """Return available role families and canonical roles."""
    return {
        "families": [
            {
                "name": fam,
                "roles": [r["name"] for r in data["roles"]],
            }
            for fam, data in ROLE_TAXONOMY.items()
        ]
    }


@router.get("", response_model=JobListResponse)
def list_jobs(
    country: Optional[str] = None,
    role: Optional[str] = None,
    role_family: Optional[str] = None,
    normalized_role: Optional[str] = None,
    location: Optional[str] = None,
    normalized_city: Optional[str] = None,
    experience_level: Optional[str] = None,
    company: Optional[str] = None,
    source: Optional[str] = None,
    time_period: Optional[str] = None,
    include_demo: bool = Query(False, description="Set to True to inspect demo jobs"),
    search: Optional[str] = None,
    sort_by: str = Query("newest", regex="^(newest|salary|relevance)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List jobs with optional filters, search, and pagination.
    Defaults to real jobs only unless include_demo=True.
    """
    query = get_jobs_query(
        db=db,
        country=country,
        role=role,
        role_family=role_family,
        normalized_role=normalized_role,
        location=location,
        normalized_city=normalized_city,
        experience_level=experience_level,
        source=source,
        time_period=time_period,
        include_demo=include_demo,
        data_type="demo" if include_demo else "real",
    )

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

    # Total before pagination
    total = query.count()

    # Paginate
    offset = (page - 1) * page_size
    jobs = query.offset(offset).limit(page_size).all()

    # Build response
    job_responses = []
    for job in jobs:
        skills = [
            SkillInJob(
                id=js.skill.id,
                name=js.skill.canonical_name or js.skill.name,
                category=js.skill.category,
                confidence=js.confidence,
            )
            for js in job.job_skills
            if js.skill
        ]
        job_responses.append(
            JobResponse(
                id=job.id,
                source=job.source,
                data_type=job.data_type,
                external_id=job.external_id,
                title=job.title,
                role_family=job.role_family,
                normalized_role=job.normalized_role,
                company_name=job.company_name,
                location=job.location,
                normalized_city=job.normalized_city,
                state=job.state,
                is_remote=job.is_remote,
                country=job.country,
                description=job.description,
                salary_min=job.salary_min,
                salary_max=job.salary_max,
                salary_currency=job.salary_currency,
                salary_period=job.salary_period,
                salary_normalized=job.salary_normalized,
                employment_type=job.employment_type,
                experience_level=job.experience_level,
                posted_at=job.posted_at,
                url=job.url,
                collected_at=job.collected_at,
                first_seen_at=job.first_seen_at,
                last_seen_at=job.last_seen_at,
                skills=skills,
            )
        )

    return JobListResponse(
        jobs=job_responses,
        total=total,
        page=page,
        page_size=page_size,
        data_type="demo" if include_demo else "real",
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a single job by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    skills = [
        SkillInJob(
            id=js.skill.id,
            name=js.skill.canonical_name or js.skill.name,
            category=js.skill.category,
            confidence=js.confidence,
        )
        for js in job.job_skills
        if js.skill
    ]

    return JobResponse(
        id=job.id,
        source=job.source,
        data_type=job.data_type,
        external_id=job.external_id,
        title=job.title,
        role_family=job.role_family,
        normalized_role=job.normalized_role,
        company_name=job.company_name,
        location=job.location,
        normalized_city=job.normalized_city,
        state=job.state,
        is_remote=job.is_remote,
        country=job.country,
        description=job.description,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        salary_period=job.salary_period,
        salary_normalized=job.salary_normalized,
        employment_type=job.employment_type,
        experience_level=job.experience_level,
        posted_at=job.posted_at,
        url=job.url,
        collected_at=job.collected_at,
        first_seen_at=job.first_seen_at,
        last_seen_at=job.last_seen_at,
        skills=skills,
    )
