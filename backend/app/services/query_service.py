"""Centralized query builder for consistent date filtering, data separation, and freshness."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session, Query
from sqlalchemy import func

from app.models.job import Job


def parse_time_period(time_period: Optional[str]) -> Optional[timedelta]:
    """Parse supported time periods into a timedelta.
    Supported periods:
        '7d': 7 days
        '30d': 30 days
        '90d': 90 days
        '6m': 180 days (~6 months)
        '1y': 365 days (1 year)
        'all': None (all time)
    """
    if not time_period or time_period.lower() == "all":
        return None

    period_map = {
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "90d": timedelta(days=90),
        "6m": timedelta(days=180),
        "1y": timedelta(days=365),
    }
    return period_map.get(time_period.lower(), timedelta(days=30))


def get_job_freshness_expr():
    """SQLAlchemy expression for job freshness: posted_at if reliable, else collected_at."""
    return func.coalesce(Job.posted_at, Job.collected_at)


def get_jobs_query(
    db: Session,
    country: Optional[str] = None,
    role: Optional[str] = None,
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    source: Optional[str] = None,
    time_period: Optional[str] = "30d",
    data_type: Optional[str] = "real",
    include_demo: bool = False,
    date_range: Optional[Tuple[datetime, datetime]] = None,
) -> Query:
    """Build a filtered Job query adhering to rigorous data separation and date filtering.

    Rule:
    - Real data is the default (Job.data_type == 'real').
    - Demo data is NEVER mixed into real analytics unless include_demo=True or data_type='demo'.
    - Time filter strictly uses coalesce(Job.posted_at, Job.collected_at).
    """
    query = db.query(Job)

    # 1. Real vs Demo separation
    if data_type == "demo":
        query = query.filter(Job.data_type == "demo")
    elif not include_demo:
        query = query.filter(Job.data_type == "real")
    # If include_demo=True and data_type is not demo, all data types are allowed

    # 2. Source filter
    if source and source.lower() not in ("all", "all sources"):
        query = query.filter(Job.source == source.lower().strip())

    # 3. Country filter
    if country and country.lower() not in ("all", "all countries", "worldwide"):
        query = query.filter(Job.country.ilike(f"%{country.strip()}%"))

    # 4. Role filter
    if role and role.lower() not in ("all", "all roles"):
        query = query.filter(Job.title.ilike(f"%{role.strip()}%"))

    # 5. Location filter
    if location and location.lower() not in ("all", "all locations"):
        query = query.filter(Job.location.ilike(f"%{location.strip()}%"))

    # 6. Experience level filter
    if experience_level and experience_level.lower() not in ("all", "any"):
        query = query.filter(Job.experience_level == experience_level.strip())

    # 7. Time period / Date range filter
    freshness_date = get_job_freshness_expr()

    if date_range:
        start_date, end_date = date_range
        if start_date:
            query = query.filter(freshness_date >= start_date)
        if end_date:
            query = query.filter(freshness_date <= end_date)
    elif time_period:
        delta = parse_time_period(time_period)
        if delta is not None:
            cutoff = datetime.now(timezone.utc) - delta
            query = query.filter(freshness_date >= cutoff)

    return query
