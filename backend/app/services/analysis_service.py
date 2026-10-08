"""Analysis service for skill demand trends, skill gap analysis, and role comparisons."""

import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from app.models.job import Job
from app.models.skill import Skill, JobSkill
from app.models.analysis import AnalysisRun, SkillDemand
from app.analyzers.skill_extractor import normalize_skill_name
from app.services.query_service import get_jobs_query, parse_time_period

logger = logging.getLogger(__name__)


def run_analysis_snapshot(
    db: Session,
    country: Optional[str] = None,
    role: Optional[str] = None,
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    source: Optional[str] = None,
    time_period: Optional[str] = "30d",
    data_type: str = "real",
    include_demo: bool = False,
) -> AnalysisRun:
    """Create a persistent AnalysisRun snapshot and save skill demand percentages.
    Zero artificial variance: all numbers are calculated from actual jobs in the database.
    """
    now = datetime.now(timezone.utc)
    delta = parse_time_period(time_period)
    start_date = now - delta if delta else None
    end_date = now

    query = get_jobs_query(
        db=db,
        country=country,
        role=role,
        location=location,
        experience_level=experience_level,
        source=source,
        time_period=time_period,
        data_type=data_type,
        include_demo=include_demo,
    )

    total_jobs = query.count()
    job_ids = [j.id for j in query.with_entities(Job.id).all()]

    analysis_run = AnalysisRun(
        source=source or "all",
        data_type=data_type,
        country=country or "Worldwide",
        role=role or "All Roles",
        location=location or "All Locations",
        experience_level=experience_level or "All",
        time_period_start=start_date,
        time_period_end=end_date,
        start_date=start_date,
        end_date=end_date,
        jobs_analyzed=total_jobs,
        created_at=now,
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


def calculate_trends(
    db: Session,
    country: Optional[str] = None,
    role: Optional[str] = None,
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    source: Optional[str] = None,
    period: str = "30d",
    data_type: str = "real",
    include_demo: bool = False,
    min_jobs_threshold: int = 5,
) -> Dict[str, Any]:
    """Calculate skill demand trends by comparing two equivalent real time periods.
    Example: Last 30 days vs Previous 30 days.
    Strictly reports 'insufficient data' when historical comparisons lack sufficient records.
    """
    now = datetime.now(timezone.utc)
    delta = parse_time_period(period) or timedelta(days=30)

    # Current window: [now - delta, now]
    cur_start = now - delta
    cur_end = now

    # Previous equivalent window: [now - 2*delta, now - delta]
    prev_start = now - (2 * delta)
    prev_end = now - delta

    # Query jobs in current period
    cur_query = get_jobs_query(
        db=db,
        country=country,
        role=role,
        location=location,
        experience_level=experience_level,
        source=source,
        data_type=data_type,
        include_demo=include_demo,
        date_range=(cur_start, cur_end),
    )
    cur_total = cur_query.count()
    cur_job_ids = [j.id for j in cur_query.with_entities(Job.id).all()]

    # Query jobs in previous equivalent period
    prev_query = get_jobs_query(
        db=db,
        country=country,
        role=role,
        location=location,
        experience_level=experience_level,
        source=source,
        data_type=data_type,
        include_demo=include_demo,
        date_range=(prev_start, prev_end),
    )
    prev_total = prev_query.count()
    prev_job_ids = [j.id for j in prev_query.with_entities(Job.id).all()]

    period_days = delta.days
    cur_label = f"Last {period_days} days"
    prev_label = f"Previous {period_days} days ({period_days*2}d to {period_days}d ago)"

    # Rule: If either period lacks sufficient data, DO NOT fabricate trends
    if cur_total < 2 or prev_total < 2:
        return {
            "emerging": [],
            "declining": [],
            "period": period,
            "has_sufficient_data": False,
            "current_period_label": cur_label,
            "previous_period_label": prev_label,
            "current_jobs_count": cur_total,
            "previous_jobs_count": prev_total,
            "message": (
                f"Not enough historical data to compare {cur_label} ({cur_total} jobs) "
                f"against {prev_label} ({prev_total} jobs). At least 2 jobs in both periods are required."
            ),
        }

    # Skill occurrences in current period
    cur_demands: Dict[int, Dict[str, Any]] = {}
    if cur_job_ids:
        rows = (
            db.query(
                Skill.id,
                Skill.canonical_name,
                Skill.category,
                func.count(distinct(JobSkill.job_id)).label("count"),
            )
            .join(JobSkill, JobSkill.skill_id == Skill.id)
            .filter(JobSkill.job_id.in_(cur_job_ids))
            .group_by(Skill.id, Skill.canonical_name, Skill.category)
            .all()
        )
        for r in rows:
            cur_demands[r.id] = {
                "name": r.canonical_name,
                "category": r.category,
                "count": r.count,
                "percentage": round((r.count / cur_total) * 100, 1),
            }

    # Skill occurrences in previous period
    prev_demands: Dict[int, Dict[str, Any]] = {}
    if prev_job_ids:
        rows = (
            db.query(
                Skill.id,
                Skill.canonical_name,
                Skill.category,
                func.count(distinct(JobSkill.job_id)).label("count"),
            )
            .join(JobSkill, JobSkill.skill_id == Skill.id)
            .filter(JobSkill.job_id.in_(prev_job_ids))
            .group_by(Skill.id, Skill.canonical_name, Skill.category)
            .all()
        )
        for r in rows:
            prev_demands[r.id] = {
                "name": r.canonical_name,
                "category": r.category,
                "count": r.count,
                "percentage": round((r.count / prev_total) * 100, 1),
            }

    all_skill_ids = set(cur_demands.keys()) | set(prev_demands.keys())
    changes = []

    for sid in all_skill_ids:
        cur_item = cur_demands.get(sid, {})
        prev_item = prev_demands.get(sid, {})

        cur_pct = cur_item.get("percentage", 0.0)
        prev_pct = prev_item.get("percentage", 0.0)
        cur_count = cur_item.get("count", 0)
        prev_count = prev_item.get("count", 0)
        name = cur_item.get("name") or prev_item.get("name")
        cat = cur_item.get("category") or prev_item.get("category")

        change_pp = round(cur_pct - prev_pct, 1)

        changes.append({
            "skill_id": sid,
            "skill_name": name,
            "category": cat,
            "current_percentage": cur_pct,
            "previous_percentage": prev_pct,
            "change_pp": change_pp,
            "current_job_count": cur_count,
            "previous_job_count": prev_count,
            "trend_direction": "up" if change_pp > 0 else ("down" if change_pp < 0 else "stable"),
        })

    # Emerging: change_pp > 0 and meets minimum job count threshold in current period
    emerging = sorted(
        [c for c in changes if c["change_pp"] > 0 and c["current_job_count"] >= min_jobs_threshold],
        key=lambda x: x["change_pp"],
        reverse=True,
    )[:10]

    # Declining: change_pp < 0 and had meaningful presence in previous period
    declining = sorted(
        [c for c in changes if c["change_pp"] < 0 and c["previous_job_count"] >= min_jobs_threshold],
        key=lambda x: x["change_pp"],
    )[:10]

    return {
        "emerging": emerging,
        "declining": declining,
        "period": period,
        "has_sufficient_data": True,
        "current_period_label": cur_label,
        "previous_period_label": prev_label,
        "current_jobs_count": cur_total,
        "previous_jobs_count": prev_total,
        "message": f"Comparing {cur_label} ({cur_total} jobs) vs {prev_label} ({prev_total} jobs).",
    }


def calculate_skill_gap(
    db: Session,
    user_skills: List[str],
    target_role: Optional[str] = "Software Engineer",
    country: Optional[str] = None,
    time_period: Optional[str] = "30d",
    data_type: str = "real",
    include_demo: bool = False,
) -> Dict[str, Any]:
    """Compare user's current skills with market demand for target role.
    Uses canonical skill matching (no substring leaks) and transparent ranking.
    """
    # Normalize user skills to canonical names
    normalized_user_skills = set()
    for s in user_skills:
        if s and s.strip():
            canon = normalize_skill_name(s.strip())
            normalized_user_skills.add(canon.lower())

    # Query jobs matching target role
    query = get_jobs_query(
        db=db,
        country=country,
        role=target_role,
        time_period=time_period,
        data_type=data_type,
        include_demo=include_demo,
    )

    total_jobs = query.count()
    job_ids = [j.id for j in query.with_entities(Job.id).all()]

    if total_jobs == 0:
        return {
            "target_role": target_role,
            "jobs_analyzed": 0,
            "market_coverage_percentage": 0.0,
            "match_score": 0.0,
            "matched_skills": [],
            "missing_high_demand": [],
            "missing_nice_to_have": [],
            "recommendations": [
                f"No job data available for role '{target_role}'. Collect jobs first to evaluate skill coverage."
            ],
            "formula_description": (
                "Market Skill Coverage = (sum of demand weights for skills you possess) / "
                "(sum of all market demand weights) * 100."
            ),
        }

    # Aggregate demanded skills in target jobs
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
    user_covered_weight = 0.0

    top_5_skill_names = set(d.canonical_name.lower() for d in demands[:5])

    for d in demands:
        pct = round((d.job_count / total_jobs) * 100, 1)
        canonical = d.canonical_name
        is_covered = canonical.lower() in normalized_user_skills

        # Transparent priority formula:
        # priority_score = demand_percentage * role_relevance * trend_factor
        role_relevance = 1.2 if canonical.lower() in top_5_skill_names else 1.0
        trend_factor = 1.0
        priority_score = round(pct * role_relevance * trend_factor, 1)

        item = {
            "skill_id": d.id,
            "name": canonical,
            "category": d.category or "General",
            "demand_percentage": pct,
            "job_count": d.job_count,
            "priority_score": priority_score,
        }

        total_market_weight += pct
        if is_covered:
            user_covered_weight += pct
            matched_skills.append(item)
        else:
            if pct >= 25.0:
                missing_high_demand.append(item)
            else:
                missing_nice_to_have.append(item)

    # Sort missing skills strictly by priority_score descending
    missing_high_demand.sort(key=lambda x: x["priority_score"], reverse=True)
    missing_nice_to_have.sort(key=lambda x: x["priority_score"], reverse=True)

    coverage_score = (
        round((user_covered_weight / total_market_weight) * 100, 1)
        if total_market_weight > 0
        else 0.0
    )

    # Recommendations
    recommendations = []
    if missing_high_demand:
        top_missing = [s["name"] for s in missing_high_demand[:3]]
        recommendations.append(
            f"High Priority: {', '.join(top_missing)} are demanded in >25% of {target_role} listings."
        )
    if coverage_score >= 80:
        recommendations.append("High market skill coverage: You possess the predominant skills demanded for this role.")
    elif coverage_score >= 50:
        recommendations.append("Moderate skill coverage: Acquiring 2-3 top missing technologies will substantially improve match depth.")
    else:
        recommendations.append("Low coverage for this role: Consider targeted upskilling in the top missing skills before applying.")

    return {
        "target_role": target_role,
        "jobs_analyzed": total_jobs,
        "market_coverage_percentage": min(coverage_score, 100.0),
        "match_score": min(coverage_score, 100.0),  # Alias for backward compatibility
        "matched_skills": matched_skills,
        "missing_high_demand": missing_high_demand[:10],
        "missing_nice_to_have": missing_nice_to_have[:10],
        "recommendations": recommendations,
        "formula_description": (
            "Market Skill Coverage = (sum of demand weights for skills you possess) / "
            "(sum of all market demand weights) * 100. "
            "Missing skills priority = demand_percentage * role_relevance."
        ),
    }


def compare_roles(
    db: Session,
    roles: Optional[List[str]] = None,
    data_type: str = "real",
    include_demo: bool = False,
    time_period: Optional[str] = "30d",
) -> List[Dict[str, Any]]:
    """Compare skill demands across different standard roles using real jobs."""
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
        job_query = get_jobs_query(
            db=db,
            role=role_name,
            data_type=data_type,
            include_demo=include_demo,
            time_period=time_period,
        )
        total = job_query.count()
        if total == 0:
            continue

        job_ids = [j.id for j in job_query.with_entities(Job.id).all()]
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
