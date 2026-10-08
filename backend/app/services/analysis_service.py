"""Analysis service for skill demand trends, skill gap analysis, and role comparisons."""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from app.models.job import Job
from app.models.skill import Skill, JobSkill
from app.models.analysis import AnalysisRun, SkillDemand

logger = logging.getLogger(__name__)


def run_analysis_snapshot(
    db: Session,
    country: Optional[str] = None,
    role: Optional[str] = None,
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
) -> AnalysisRun:
    """Create a new AnalysisRun snapshot and save skill demand percentages."""
    query = db.query(Job)
    if country:
        query = query.filter(Job.country.ilike(f"%{country}%"))
    if role and role.lower() != "all roles":
        query = query.filter(Job.title.ilike(f"%{role}%"))
    if location and location.lower() != "all locations":
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if experience_level and experience_level.lower() != "all":
        query = query.filter(Job.experience_level == experience_level)

    total_jobs = query.count()
    job_ids = [j.id for j in query.with_entities(Job.id).all()]

    analysis_run = AnalysisRun(
        country=country or "India",
        role=role or "Software Engineer",
        location=location or "All locations",
        experience_level=experience_level or "All",
        jobs_analyzed=total_jobs,
        created_at=datetime.now(timezone.utc),
    )
    db.add(analysis_run)
    db.flush()

    if total_jobs > 0 and job_ids:
        skill_counts = (
            db.query(
                Skill.id.label("skill_id"),
                func.count(distinct(JobSkill.job_id)).label("count"),
            )
            .join(JobSkill, JobSkill.skill_id == Skill.id)
            .filter(JobSkill.job_id.in_(job_ids))
            .group_by(Skill.id)
            .all()
        )

        for sc in skill_counts:
            pct = round((sc.count / total_jobs) * 100, 1)
            sd = SkillDemand(
                analysis_run_id=analysis_run.id,
                skill_id=sc.skill_id,
                job_count=sc.count,
                percentage=pct,
            )
            db.add(sd)

    db.commit()
    db.refresh(analysis_run)
    return analysis_run


def calculate_skill_gap(
    db: Session,
    user_skills: List[str],
    target_role: Optional[str] = "Software Engineer",
    country: Optional[str] = "India",
) -> Dict[str, Any]:
    """Compare user's current skills with market demand for the target role."""
    # Normalize user skills
    normalized_user = set(s.strip().lower() for s in user_skills if s.strip())

    # Find jobs matching target role
    query = db.query(Job)
    if country:
        query = query.filter(Job.country.ilike(f"%{country}%"))
    if target_role and target_role.lower() != "all":
        query = query.filter(Job.title.ilike(f"%{target_role}%"))

    total_jobs = query.count()
    if total_jobs == 0:
        # Fallback to all jobs if specific role has no jobs
        total_jobs = db.query(Job).count()
        job_ids = [j.id for j in db.query(Job.id).all()]
    else:
        job_ids = [j.id for j in query.with_entities(Job.id).all()]

    if total_jobs == 0:
        return {
            "target_role": target_role,
            "jobs_analyzed": 0,
            "match_score": 0,
            "matched_skills": [],
            "missing_high_demand": [],
            "missing_nice_to_have": [],
            "recommendations": ["No job data available. Collect jobs first."],
        }

    # Aggregate skill demand for these jobs
    demands = (
        db.query(
            Skill.id,
            Skill.canonical_name,
            Skill.category,
            func.count(distinct(JobSkill.job_id)).label("job_count"),
        )
        .join(JobSkill, JobSkill.skill_id == Skill.id)
        .filter(JobSkill.job_id.in_(job_ids))
        .group_by(Skill.id, Skill.canonical_name, Skill.category)
        .order_by(func.count(distinct(JobSkill.job_id)).desc())
        .all()
    )

    matched_skills = []
    missing_high_demand = []
    missing_nice_to_have = []

    total_market_weight = 0.0
    user_matched_weight = 0.0

    for d in demands:
        pct = round((d.job_count / total_jobs) * 100, 1)
        skill_name = d.canonical_name
        is_user_has = skill_name.lower() in normalized_user or any(
            u in skill_name.lower() or skill_name.lower() in u for u in normalized_user
        )

        item = {
            "skill_id": d.id,
            "name": skill_name,
            "category": d.category or "General",
            "demand_percentage": pct,
            "job_count": d.job_count,
        }

        # Weight higher-demand skills more in match score
        weight = pct
        total_market_weight += weight

        if is_user_has:
            user_matched_weight += weight
            matched_skills.append(item)
        else:
            if pct >= 25.0:
                missing_high_demand.append(item)
            else:
                missing_nice_to_have.append(item)

    match_score = (
        round((user_matched_weight / total_market_weight) * 100, 1)
        if total_market_weight > 0
        else 0
    )

    # Generate tailored recommendations
    recommendations = []
    if missing_high_demand:
        top_missing = [s["name"] for s in missing_high_demand[:3]]
        recommendations.append(
            f"Prioritize mastering {', '.join(top_missing)}: required in >25% of {target_role} listings."
        )
    if match_score >= 80:
        recommendations.append("Outstanding match! You meet most key requirements for this role.")
    elif match_score >= 50:
        recommendations.append("Solid foundation. Bridging 2-3 top missing skills will significantly increase interview callbacks.")
    else:
        recommendations.append("Skill gap identified. Focus on core requirements before applying.")

    return {
        "target_role": target_role,
        "jobs_analyzed": total_jobs,
        "match_score": min(match_score, 100.0),
        "matched_skills": matched_skills,
        "missing_high_demand": missing_high_demand[:10],
        "missing_nice_to_have": missing_nice_to_have[:10],
        "recommendations": recommendations,
    }


def compare_roles(db: Session, roles: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Compare skill demands across different standard roles."""
    if not roles:
        roles = [
            "Frontend",
            "Backend",
            "Full Stack",
            "DevOps",
            "Data",
        ]

    comparison_results = []

    for role_name in roles:
        job_query = db.query(Job.id).filter(Job.title.ilike(f"%{role_name}%"))
        total = job_query.count()
        if total == 0:
            continue

        job_ids = [j.id for j in job_query.all()]
        top_skills = (
            db.query(
                Skill.canonical_name,
                func.count(distinct(JobSkill.job_id)).label("count"),
            )
            .join(JobSkill, JobSkill.skill_id == Skill.id)
            .filter(JobSkill.job_id.in_(job_ids))
            .group_by(Skill.canonical_name)
            .order_by(func.count(distinct(JobSkill.job_id)).desc())
            .limit(8)
            .all()
        )

        comparison_results.append({
            "role": role_name,
            "job_count": total,
            "skills": [
                {
                    "name": ts.canonical_name,
                    "count": ts.count,
                    "percentage": round((ts.count / total) * 100, 1),
                }
                for ts in top_skills
            ],
        })

    return comparison_results
