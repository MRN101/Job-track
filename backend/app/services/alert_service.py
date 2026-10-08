"""Personal alerts service for job market changes and emerging technologies."""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.skill import CandidateSkill
from app.services.analysis_service import calculate_trends


def evaluate_alerts(
    db: Session,
    growth_threshold_pp: float = 3.0,
    candidate_threshold_jobs: int = 5,
    market_threshold_pct: float = 30.0,
    role: Optional[str] = "Software Engineer",
    country: Optional[str] = "Worldwide",
) -> List[Dict[str, Any]]:
    """Generate dynamic personal alerts based on current job market conditions:
    1. Skill growth: skill demand increased by >= X percentage points
    2. Emerging candidates: unapproved candidate skill appears in >= X jobs
    3. Market saturation/core requirement: skill appears in > X% of active listings
    """
    alerts = []
    now = datetime.now(timezone.utc)

    # 1. Emerging Candidates
    high_freq_candidates = (
        db.query(CandidateSkill)
        .filter(
            CandidateSkill.status == "candidate",
            CandidateSkill.job_count >= candidate_threshold_jobs,
        )
        .order_by(CandidateSkill.job_count.desc())
        .limit(5)
        .all()
    )

    for cand in high_freq_candidates:
        alerts.append({
            "type": "new_candidate",
            "title": f"Emerging Tech Candidate: {cand.name}",
            "message": f"'{cand.name}' detected in {cand.job_count} active job listings across the market.",
            "severity": "info",
            "timestamp": cand.last_seen_at or now,
            "data": {
                "skill_name": cand.name,
                "job_count": cand.job_count,
                "confidence": cand.confidence,
                "candidate_id": cand.id,
            },
        })

    # 2. Skill Growth & High Demand (via trends comparison)
    trends = calculate_trends(
        db=db,
        role=role,
        country=country,
        period="30d",
        data_type="real",
    )

    has_data = trends.get("has_sufficient_data") if isinstance(trends, dict) else getattr(trends, "has_sufficient_data", False)
    emerging_list = trends.get("emerging", []) if isinstance(trends, dict) else getattr(trends, "emerging", [])

    if has_data and emerging_list:
        # Check rising skills
        for item in emerging_list:
            s_name = item.get("skill_name") if isinstance(item, dict) else item.skill_name
            chg = item.get("change_pp") if isinstance(item, dict) else item.change_pp
            cur_pct = item.get("current_percentage") if isinstance(item, dict) else item.current_percentage
            prev_pct = item.get("previous_percentage") if isinstance(item, dict) else item.previous_percentage

            if chg and chg >= growth_threshold_pp:
                alerts.append({
                    "type": "skill_growth",
                    "title": f"Rapid Demand Surge: {s_name}",
                    "message": f"{s_name} demand grew by +{chg:.1f} pp (now at {cur_pct:.1f}%).",
                    "severity": "success",
                    "timestamp": now,
                    "data": {
                        "skill_name": s_name,
                        "change_pp": chg,
                        "current_pct": cur_pct,
                        "previous_pct": prev_pct,
                    },
                })

            if cur_pct and cur_pct >= market_threshold_pct:
                alerts.append({
                    "type": "threshold",
                    "title": f"Core Market Standard: {s_name}",
                    "message": f"{s_name} is required in {cur_pct:.1f}% of current '{role}' listings.",
                    "severity": "info",
                    "timestamp": now,
                    "data": {
                        "skill_name": s_name,
                        "current_pct": cur_pct,
                    },
                })

    return alerts
