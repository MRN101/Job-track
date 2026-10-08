"""Analytics API endpoints."""

from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import json

from app.database import get_db
from app.schemas.analytics import (
    DashboardMetrics,
    CollectionRequest,
    CollectionStatus,
)
from app.services.job_service import collect_and_ingest, ensure_skills_taxonomy
from app.services.analysis_service import (
    run_analysis_snapshot,
    calculate_skill_gap,
    compare_roles,
)
from app.collectors import get_available_collectors

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardMetrics)
def get_dashboard_metrics(
    country: Optional[str] = None,
    role: Optional[str] = None,
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    time_period: str = "30d",
    db: Session = Depends(get_db),
):
    """Get dashboard summary metrics."""
    from app.models.job import Job
    from app.models.skill import JobSkill
    from sqlalchemy import func, distinct
    from datetime import datetime, timedelta, timezone

    # Parse time period
    now = datetime.now(timezone.utc)
    period_map = {
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "90d": timedelta(days=90),
        "6m": timedelta(days=180),
        "all": None,
    }
    delta = period_map.get(time_period, timedelta(days=30))

    query = db.query(Job)
    if delta is not None:
        start_date = now - delta
        query = query.filter(Job.collected_at >= start_date)

    if country and country.lower() != "all countries":
        query = query.filter(Job.country.ilike(f"%{country}%"))
    if role and role.lower() != "all roles":
        query = query.filter(Job.title.ilike(f"%{role}%"))
    if location and location.lower() != "all locations":
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if experience_level and experience_level.lower() != "all":
        query = query.filter(Job.experience_level == experience_level)

    # Count jobs
    jobs_analyzed = query.count()

    # If 0 jobs found with time filter but database has jobs, fallback to all jobs to prevent blank dashboard
    if jobs_analyzed == 0 and delta is not None:
        fallback_query = db.query(Job)
        if country and country.lower() != "all countries":
            fallback_query = fallback_query.filter(Job.country.ilike(f"%{country}%"))
        if role and role.lower() != "all roles":
            fallback_query = fallback_query.filter(Job.title.ilike(f"%{role}%"))
        total_fallback = fallback_query.count()
        if total_fallback > 0:
            query = fallback_query
            jobs_analyzed = total_fallback

    # Count unique companies
    companies = query.with_entities(
        func.count(distinct(Job.company_name))
    ).scalar() or 0

    # Count unique skills from those jobs
    job_ids = [j.id for j in query.with_entities(Job.id).all()]
    unique_skills = 0
    if job_ids:
        unique_skills = db.query(func.count(distinct(JobSkill.skill_id))).filter(
            JobSkill.job_id.in_(job_ids)
        ).scalar() or 0

    # Median salary
    median_salary = None
    salary_currency = None
    salary_jobs = query.filter(
        Job.salary_max.isnot(None), Job.salary_max > 0
    ).all()
    if len(salary_jobs) >= 1:
        salaries = sorted([j.salary_max for j in salary_jobs])
        mid = len(salaries) // 2
        median_salary = salaries[mid]
        salary_currency = salary_jobs[0].salary_currency

    # Last collection time
    last_job = db.query(Job).order_by(Job.collected_at.desc()).first()
    last_collection = last_job.collected_at if last_job else None

    return DashboardMetrics(
        jobs_analyzed=jobs_analyzed,
        companies=companies,
        unique_skills=unique_skills,
        median_salary=median_salary,
        salary_currency=salary_currency,
        last_collection=last_collection,
    )


@router.get("/top-skills")
def get_top_skills(
    country: Optional[str] = None,
    role: Optional[str] = None,
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    time_period: str = "30d",
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get the most frequently requested skills."""
    from app.models.job import Job
    from app.models.skill import Skill, JobSkill
    from sqlalchemy import func, distinct

    # Get matching jobs
    job_query = db.query(Job.id)
    if country and country.lower() != "all countries":
        job_query = job_query.filter(Job.country.ilike(f"%{country}%"))
    if role and role.lower() != "all roles":
        job_query = job_query.filter(Job.title.ilike(f"%{role}%"))
    if location and location.lower() != "all locations":
        job_query = job_query.filter(Job.location.ilike(f"%{location}%"))

    total_jobs = job_query.count()

    if total_jobs == 0:
        return {"skills": [], "total_jobs": 0}

    job_ids_subquery = job_query.subquery()

    # Count skill occurrences
    skill_counts = (
        db.query(
            Skill.id,
            Skill.name,
            Skill.canonical_name,
            Skill.category,
            func.count(distinct(JobSkill.job_id)).label("job_count"),
        )
        .join(JobSkill, JobSkill.skill_id == Skill.id)
        .filter(JobSkill.job_id.in_(db.query(job_ids_subquery.c.id)))
        .group_by(Skill.id, Skill.name, Skill.canonical_name, Skill.category)
        .order_by(func.count(distinct(JobSkill.job_id)).desc())
        .limit(limit)
        .all()
    )

    skills = [
        {
            "skill_id": s.id,
            "skill_name": s.name or s.canonical_name,
            "category": s.category,
            "job_count": s.job_count,
            "percentage": round((s.job_count / total_jobs) * 100, 1),
        }
        for s in skill_counts
    ]

    return {"skills": skills, "total_jobs": total_jobs}


@router.get("/trends")
def get_trends(
    country: Optional[str] = None,
    role: Optional[str] = None,
    period: str = "30d",
    db: Session = Depends(get_db),
):
    """Get skill trend data (emerging and declining)."""
    from app.models.analysis import AnalysisRun, SkillDemand
    from app.models.skill import Skill

    query = db.query(AnalysisRun).order_by(AnalysisRun.created_at.desc())
    if country and country.lower() != "all countries":
        query = query.filter(AnalysisRun.country == country)
    if role and role.lower() != "all roles":
        query = query.filter(AnalysisRun.role.ilike(f"%{role}%"))

    runs = query.limit(10).all()

    if len(runs) < 2:
        return {
            "emerging": [],
            "declining": [],
            "period": period,
            "has_sufficient_data": False,
        }

    current_run = runs[0]
    previous_run = runs[1]

    current_demands = {
        sd.skill_id: sd.percentage
        for sd in db.query(SkillDemand).filter(
            SkillDemand.analysis_run_id == current_run.id
        ).all()
    }

    previous_demands = {
        sd.skill_id: sd.percentage
        for sd in db.query(SkillDemand).filter(
            SkillDemand.analysis_run_id == previous_run.id
        ).all()
    }

    all_skill_ids = set(current_demands.keys()) | set(previous_demands.keys())
    changes = []
    for skill_id in all_skill_ids:
        current = current_demands.get(skill_id, 0.0)
        previous = previous_demands.get(skill_id, 0.0)
        change = round(current - previous, 1)

        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if skill:
            changes.append({
                "skill_id": skill_id,
                "skill_name": skill.name or skill.canonical_name,
                "category": skill.category,
                "current_percentage": current,
                "previous_percentage": previous,
                "change_pp": change,
                "trend_direction": "up" if change > 0 else ("down" if change < 0 else "stable"),
            })

    emerging = sorted(
        [c for c in changes if c["change_pp"] > 0],
        key=lambda x: x["change_pp"],
        reverse=True,
    )[:10]

    declining = sorted(
        [c for c in changes if c["change_pp"] < 0],
        key=lambda x: x["change_pp"],
    )[:10]

    return {
        "emerging": emerging,
        "declining": declining,
        "period": period,
        "has_sufficient_data": True,
    }


@router.get("/collectors")
def list_collectors():
    """List available job data sources and their status."""
    return get_available_collectors()


@router.post("/collect", response_model=CollectionStatus)
def trigger_collection(
    request: CollectionRequest,
    source: str = Query("sample", description="Collector source: sample or adzuna"),
    db: Session = Depends(get_db),
):
    """Trigger job collection from a specified source."""
    result = collect_and_ingest(
        source=source,
        country=request.country,
        role=request.role,
        location=request.location,
        experience_level=request.experience_level,
        max_results=request.max_results,
        db=db,
    )

    return CollectionStatus(
        status="completed" if result.errors == 0 else "error",
        source=result.source,
        retrieved=result.retrieved,
        new_jobs=result.new_jobs,
        duplicates=result.duplicates,
        errors=result.errors,
        message=result.error_messages[0] if result.error_messages else "Collection completed successfully.",
    )


@router.post("/seed-sample")
def seed_sample_data(db: Session = Depends(get_db)):
    """Seed comprehensive sample jobs and create baseline analysis snapshots."""
    # 1. Ensure canonical skills taxonomy
    skills_count = ensure_skills_taxonomy(db)

    # 2. Collect and ingest sample jobs
    result = collect_and_ingest(
        source="sample",
        country="India",
        role="Software Engineer",
        max_results=50,
        db=db,
    )

    # 3. Create two consecutive analysis snapshots (baseline and current) for trend analysis
    # First baseline run
    run1 = run_analysis_snapshot(db, country="India", role="Software Engineer")

    # Second run with slight variance for realistic historical comparison
    run2 = run_analysis_snapshot(db, country="India", role="Software Engineer")

    return {
        "status": "success",
        "taxonomy_skills_seeded": skills_count,
        "jobs_ingested": result.new_jobs,
        "duplicates": result.duplicates,
        "analysis_runs_created": 2,
    }


@router.post("/run-snapshot")
def trigger_analysis_snapshot(
    country: Optional[str] = "India",
    role: Optional[str] = "Software Engineer",
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Create a persistent snapshot of skill demands."""
    run = run_analysis_snapshot(
        db=db,
        country=country,
        role=role,
        location=location,
        experience_level=experience_level,
    )
    return {
        "status": "success",
        "analysis_run_id": run.id,
        "jobs_analyzed": run.jobs_analyzed,
        "created_at": run.created_at,
    }


@router.get("/skill-gap")
def get_skill_gap(
    target_role: Optional[str] = Query("Software Engineer"),
    country: Optional[str] = Query("India"),
    skills: Optional[str] = Query(None, description="Comma-separated user skills override"),
    db: Session = Depends(get_db),
):
    """Calculate skill gap against market demand."""
    from app.models.profile import UserProfile

    user_skills_list = []
    if skills:
        user_skills_list = [s.strip() for s in skills.split(",") if s.strip()]
    else:
        profile = db.query(UserProfile).first()
        if profile and profile.skills:
            try:
                user_skills_list = json.loads(profile.skills)
            except Exception:
                user_skills_list = []

    return calculate_skill_gap(
        db=db,
        user_skills=user_skills_list,
        target_role=target_role,
        country=country,
    )


@router.get("/role-comparison")
def get_role_comparison(
    roles: Optional[str] = Query(None, description="Comma-separated list of roles"),
    db: Session = Depends(get_db),
):
    """Compare skill demands across key tech roles."""
    roles_list = None
    if roles:
        roles_list = [r.strip() for r in roles.split(",") if r.strip()]
    return compare_roles(db=db, roles=roles_list)
