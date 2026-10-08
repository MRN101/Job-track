"""Analytics API endpoints."""

from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import Optional, List, Dict, Any
import json
from datetime import datetime, timezone

from app.database import get_db
from app.schemas.analytics import (
    DashboardMetrics,
    DataQualityMetrics,
    CollectionRequest,
    CollectionStatus,
    TrendsResponse,
    CollectionRunItem,
    CandidateSkillItem,
    AlertItem,
)
from app.models.job import Job
from app.models.skill import Skill, JobSkill, CandidateSkill
from app.models.company import Company
from app.models.collection import CollectionRun
from app.services.job_service import collect_and_ingest, ensure_skills_taxonomy
from app.services.analysis_service import (
    run_analysis_snapshot,
    calculate_trends,
    calculate_skill_gap,
    compare_roles,
)
from app.services.salary_service import calculate_salary_statistics
from app.services.query_service import get_jobs_query, parse_time_period
from app.collectors import get_available_collectors

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardMetrics)
def get_dashboard_metrics(
    country: Optional[str] = None,
    role: Optional[str] = None,
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    source: Optional[str] = None,
    time_period: str = "30d",
    include_demo: bool = Query(False, description="Set to True only to explicitly inspect demo data"),
    db: Session = Depends(get_db),
):
    """Get dashboard summary metrics.
    By default, uses REAL DATA ONLY. Does not fallback to demo jobs when real jobs are 0.
    """
    # Build query with strict separation
    query = get_jobs_query(
        db=db,
        country=country,
        role=role,
        location=location,
        experience_level=experience_level,
        source=source,
        time_period=time_period,
        include_demo=include_demo,
        data_type="demo" if include_demo else "real",
    )

    jobs_analyzed = query.count()
    job_ids = [j.id for j in query.with_entities(Job.id).all()]

    companies = 0
    unique_skills = 0
    salary_stats = calculate_salary_statistics([], "INR")

    if jobs_analyzed > 0 and job_ids:
        # Unique companies in filtered set
        companies = (
            query.with_entities(func.count(distinct(Job.company_name))).scalar() or 0
        )

        # Unique skills detected in filtered set
        unique_skills = (
            db.query(func.count(distinct(JobSkill.skill_id)))
            .filter(JobSkill.job_id.in_(job_ids))
            .scalar() or 0
        )

        # Salary statistics (using normalized annual salaries if available, else salary_max)
        salary_rows = (
            query.filter(
                (Job.salary_normalized.isnot(None) & (Job.salary_normalized > 0)) |
                (Job.salary_max.isnot(None) & (Job.salary_max > 0))
            )
            .all()
        )
        salaries = [
            (j.salary_normalized if (j.salary_normalized and j.salary_normalized > 0) else j.salary_max)
            for j in salary_rows
        ]
        curr = salary_rows[0].salary_currency if salary_rows else "INR"
        salary_stats = calculate_salary_statistics(salaries, curr)

    # Last collection date for this data scope
    last_job = query.order_by(Job.collected_at.desc()).first()
    last_collection = last_job.collected_at if last_job else None

    # Source breakdown counts
    source_counts = (
        query.with_entities(Job.source, func.count(Job.id))
        .group_by(Job.source)
        .all()
    )
    sources_breakdown = {s: c for s, c in source_counts}

    return DashboardMetrics(
        jobs_analyzed=jobs_analyzed,
        companies=companies,
        unique_skills=unique_skills,
        median_salary=salary_stats["median"],
        salary_min=salary_stats["min"],
        salary_max=salary_stats["max"],
        salary_p25=salary_stats["p25"],
        salary_p75=salary_stats["p75"],
        salary_currency=salary_stats["currency"],
        jobs_with_salary=salary_stats["jobs_with_salary"],
        last_collection=last_collection,
        data_type="demo" if include_demo else "real",
        is_demo=include_demo,
        sources_breakdown=sources_breakdown,
    )


@router.get("/top-skills")
def get_top_skills(
    country: Optional[str] = None,
    role: Optional[str] = None,
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    source: Optional[str] = None,
    time_period: str = "30d",
    include_demo: bool = Query(False, description="Set to True only to explicitly inspect demo data"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get the most frequently requested skills.
    Consistent filtering: numerator and denominator use the EXACT same filtered jobs query.
    """
    job_query = get_jobs_query(
        db=db,
        country=country,
        role=role,
        location=location,
        experience_level=experience_level,
        source=source,
        time_period=time_period,
        include_demo=include_demo,
        data_type="demo" if include_demo else "real",
    )

    total_jobs = job_query.count()
    if total_jobs == 0:
        return {"skills": [], "total_jobs": 0}

    job_ids = [j.id for j in job_query.with_entities(Job.id).all()]

    skill_counts = (
        db.query(
            Skill.id,
            Skill.name,
            Skill.canonical_name,
            Skill.category,
            func.count(distinct(JobSkill.job_id)).label("job_count"),
        )
        .join(JobSkill, JobSkill.skill_id == Skill.id)
        .filter(JobSkill.job_id.in_(job_ids))
        .group_by(Skill.id, Skill.name, Skill.canonical_name, Skill.category)
        .order_by(func.count(distinct(JobSkill.job_id)).desc())
        .limit(limit)
        .all()
    )

    skills = [
        {
            "skill_id": s.id,
            "skill_name": s.canonical_name or s.name,
            "category": s.category,
            "job_count": s.job_count,
            "percentage": round((s.job_count / total_jobs) * 100, 1),
        }
        for s in skill_counts
    ]

    return {"skills": skills, "total_jobs": total_jobs}


@router.get("/trends", response_model=TrendsResponse)
def get_trends(
    country: Optional[str] = None,
    role: Optional[str] = None,
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    source: Optional[str] = None,
    period: str = "30d",
    include_demo: bool = Query(False, description="Set to True to inspect demo trends"),
    db: Session = Depends(get_db),
):
    """Get emerging and declining skill trends by comparing equivalent real time windows.
    Zero fake numbers: reports insufficient data if two real windows cannot be compared.
    """
    trends = calculate_trends(
        db=db,
        country=country,
        role=role,
        location=location,
        experience_level=experience_level,
        source=source,
        period=period,
        data_type="demo" if include_demo else "real",
        include_demo=include_demo,
    )
    return trends


@router.get("/skill-gap")
def get_skill_gap(
    target_role: Optional[str] = Query("Software Engineer"),
    country: Optional[str] = None,
    time_period: str = "30d",
    skills: Optional[str] = Query(None, description="Comma-separated user skills override"),
    include_demo: bool = Query(False, description="Set to True to inspect demo data"),
    db: Session = Depends(get_db),
):
    """Calculate skill gap and Market Skill Coverage against market demand for target role."""
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
        time_period=time_period,
        data_type="demo" if include_demo else "real",
        include_demo=include_demo,
    )


@router.get("/role-comparison")
def get_role_comparison(
    roles: Optional[str] = Query(None, description="Comma-separated list of roles"),
    time_period: str = "30d",
    include_demo: bool = Query(False),
    db: Session = Depends(get_db),
):
    """Compare skill demands across key tech roles using real jobs."""
    roles_list = None
    if roles:
        roles_list = [r.strip() for r in roles.split(",") if r.strip()]
    return compare_roles(
        db=db,
        roles=roles_list,
        data_type="demo" if include_demo else "real",
        include_demo=include_demo,
        time_period=time_period,
    )


@router.get("/data-quality", response_model=DataQualityMetrics)
def get_data_quality(db: Session = Depends(get_db)):
    """Data quality and integrity metrics across all collected listings."""
    total_jobs = db.query(Job).count()
    real_jobs = db.query(Job).filter(Job.data_type == "real").count()
    demo_jobs = db.query(Job).filter(Job.data_type == "demo").count()

    jobs_with_description = (
        db.query(Job).filter(Job.description.isnot(None), Job.description != "").count()
    )
    jobs_with_salary = (
        db.query(Job)
        .filter(
            (Job.salary_min.isnot(None) & (Job.salary_min > 0)) |
            (Job.salary_max.isnot(None) & (Job.salary_max > 0))
        )
        .count()
    )
    jobs_with_skills = (
        db.query(func.count(distinct(JobSkill.job_id))).scalar() or 0
    )
    roles_normalized = (
        db.query(Job).filter(Job.normalized_role.isnot(None)).count()
    )
    locations_normalized = (
        db.query(Job).filter(Job.normalized_city.isnot(None)).count()
    )

    duplicate_records_prevented = (
        db.query(func.coalesce(func.sum(CollectionRun.duplicates), 0)).scalar() or 0
    )

    # Source breakdown
    source_counts = (
        db.query(Job.source, func.count(Job.id))
        .group_by(Job.source)
        .all()
    )
    sources_breakdown = {s: c for s, c in source_counts}

    # Last collection time per source
    last_collection_per_source = {}
    for s, _ in source_counts:
        last_job = db.query(Job).filter(Job.source == s).order_by(Job.collected_at.desc()).first()
        last_collection_per_source[s] = last_job.collected_at if last_job else None

    return DataQualityMetrics(
        total_jobs=total_jobs,
        real_jobs=real_jobs,
        demo_jobs=demo_jobs,
        jobs_with_description=jobs_with_description,
        jobs_with_salary=jobs_with_salary,
        jobs_with_skills=jobs_with_skills,
        roles_normalized=roles_normalized,
        locations_normalized=locations_normalized,
        duplicate_records_prevented=duplicate_records_prevented,
        sources_breakdown=sources_breakdown,
        last_collection_per_source=last_collection_per_source,
    )


@router.get("/collections/history", response_model=List[CollectionRunItem])
def get_collection_history(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List historical collection runs with status and metrics."""
    runs = (
        db.query(CollectionRun)
        .order_by(CollectionRun.started_at.desc())
        .limit(limit)
        .all()
    )
    return runs


@router.get("/scheduler/status")
def get_scheduler_status_endpoint():
    """Get status of background scheduler."""
    from app.services.scheduler import get_scheduler_status
    return get_scheduler_status()


@router.post("/scheduler/trigger")
def trigger_scheduled_collection():
    """Trigger the scheduled collection pipeline immediately in background."""
    from app.services.scheduler import trigger_immediate_collection
    return trigger_immediate_collection()


@router.post("/scheduler/interval")
def set_scheduler_interval_endpoint(frequency: str = Query("daily", regex="^(daily|weekly|manual)$")):
    """Update background collection frequency."""
    from app.services.scheduler import set_scheduler_interval
    set_scheduler_interval(frequency)
    return {"status": "success", "frequency": frequency}


@router.get("/candidate-skills", response_model=List[CandidateSkillItem])
def get_candidate_skills(
    status: Optional[str] = Query("candidate", description="candidate, approved, or rejected"),
    min_jobs: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List discovered candidate skills for emerging tech radar."""
    query = db.query(CandidateSkill)
    if status and status.lower() != "all":
        query = query.filter(CandidateSkill.status == status)
    query = query.filter(CandidateSkill.job_count >= min_jobs)
    return query.order_by(CandidateSkill.job_count.desc()).limit(limit).all()


@router.post("/candidate-skills/{cand_id}/approve")
def approve_candidate_skill(cand_id: int, db: Session = Depends(get_db)):
    """Approve a candidate skill and integrate it into the canonical taxonomy."""
    cand = db.query(CandidateSkill).filter(CandidateSkill.id == cand_id).first()
    if not cand:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Candidate skill not found")

    cand.status = "approved"
    cand.approved = 1

    # Check if already in canonical Skill table
    existing_skill = db.query(Skill).filter(
        (Skill.name.ilike(cand.name)) | (Skill.canonical_name.ilike(cand.name))
    ).first()

    if not existing_skill:
        new_skill = Skill(
            name=cand.name,
            canonical_name=cand.name,
            category="Emerging Technologies",
            description=f"Approved emerging skill: {cand.name}",
        )
        db.add(new_skill)

    db.commit()
    return {"status": "success", "message": f"Skill '{cand.name}' approved into canonical taxonomy."}


@router.post("/candidate-skills/{cand_id}/reject")
def reject_candidate_skill(cand_id: int, db: Session = Depends(get_db)):
    """Reject a candidate skill to prevent it from cluttering recommendations."""
    cand = db.query(CandidateSkill).filter(CandidateSkill.id == cand_id).first()
    if not cand:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Candidate skill not found")

    cand.status = "rejected"
    cand.approved = -1
    db.commit()
    return {"status": "success", "message": f"Candidate skill '{cand.name}' rejected."}


@router.get("/alerts", response_model=List[AlertItem])
def get_alerts(
    role: Optional[str] = "Software Engineer",
    country: Optional[str] = "Worldwide",
    growth_threshold: float = Query(3.0, description="Minimum percentage point increase"),
    db: Session = Depends(get_db),
):
    """Personal alerts for significant skill surges and emerging technologies."""
    from app.services.alert_service import evaluate_alerts
    return evaluate_alerts(
        db=db,
        growth_threshold_pp=growth_threshold,
        role=role,
        country=country,
    )


@router.get("/collectors")
def list_collectors():
    """List available job data sources and their status."""
    return get_available_collectors()


@router.post("/collect", response_model=CollectionStatus)
def trigger_collection(
    request: CollectionRequest,
    source: str = Query("remotive", description="Collector source: remotive, adzuna, or all"),
    db: Session = Depends(get_db),
):
    """Trigger real job collection from live source(s) with partial-failure resilience."""
    result = collect_and_ingest(
        source=source,
        country=request.country,
        role=request.role,
        location=request.location,
        experience_level=request.experience_level,
        max_results=request.max_results,
        db=db,
    )

    status_str = "completed"
    if result.errors > 0 and result.new_jobs > 0:
        status_str = "partial"
    elif result.errors > 0 and result.new_jobs == 0:
        status_str = "error"

    msg = (
        f"Collection {status_str}: {result.new_jobs} new jobs ingested, "
        f"{result.duplicates} duplicates updated, {result.errors} errors."
    )
    if result.error_messages:
        msg += f" Note: {result.error_messages[0]}"

    return CollectionStatus(
        status=status_str,
        source=result.source,
        retrieved=result.retrieved,
        new_jobs=result.new_jobs,
        duplicates=result.duplicates,
        errors=result.errors,
        message=msg,
        details=result.details,
    )


@router.post("/seed-sample")
def seed_sample_data(db: Session = Depends(get_db)):
    """Seed sample demo dataset explicitly marked as demo data.
    Does NOT create artificial variance or pretend historical trends.
    """
    skills_count = ensure_skills_taxonomy(db)

    result = collect_and_ingest(
        source="sample",
        country="India",
        role="Software Engineer",
        max_results=50,
        db=db,
    )

    # Create one single baseline analysis snapshot for the sample dataset
    run = run_analysis_snapshot(
        db,
        country="India",
        role="Software Engineer",
        data_type="demo",
        include_demo=True,
    )

    return {
        "status": "success",
        "message": "Demo sample dataset loaded. Analytics are clearly tagged as demo data.",
        "taxonomy_skills_seeded": skills_count,
        "jobs_ingested": result.new_jobs,
        "duplicates": result.duplicates,
        "analysis_run_id": run.id,
    }


@router.post("/run-snapshot")
def trigger_analysis_snapshot(
    country: Optional[str] = "Worldwide",
    role: Optional[str] = "Software Engineer",
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    source: Optional[str] = None,
    time_period: str = "30d",
    include_demo: bool = Query(False),
    db: Session = Depends(get_db),
):
    """Create a persistent snapshot of real skill demands."""
    run = run_analysis_snapshot(
        db=db,
        country=country,
        role=role,
        location=location,
        experience_level=experience_level,
        source=source,
        time_period=time_period,
        data_type="demo" if include_demo else "real",
        include_demo=include_demo,
    )
    return {
        "status": "success",
        "analysis_run_id": run.id,
        "jobs_analyzed": run.jobs_analyzed,
        "data_type": run.data_type,
        "created_at": run.created_at,
    }
