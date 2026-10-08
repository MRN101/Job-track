"""Comprehensive automated tests for JobPulse analytics, filtering, normalization, and deduplication."""

import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.job import Job
from app.models.skill import Skill, JobSkill
from app.models.company import Company
from app.analyzers.skill_extractor import SkillExtractor, normalize_skill_name, get_skill_extractor
from app.services.salary_service import (
    calculate_salary_statistics,
    parse_and_normalize_salary,
    convert_currency,
)
from app.services.query_service import get_jobs_query, parse_time_period
from app.services.analysis_service import calculate_trends, calculate_skill_gap
from app.services.job_service import ingest_jobs, ensure_skills_taxonomy
from app.collectors.base import CollectedJob


# ==========================================
# 1. Skill Normalization Tests
# ==========================================

def test_skill_normalization():
    """Verify centralized skill normalization maps variants to canonical names."""
    assert normalize_skill_name("React.js") == "React"
    assert normalize_skill_name("reactjs") == "React"
    assert normalize_skill_name("React JS") == "React"
    assert normalize_skill_name("Postgres") == "PostgreSQL"
    assert normalize_skill_name("postgresql") == "PostgreSQL"
    assert normalize_skill_name("Amazon Web Services") == "AWS"
    assert normalize_skill_name("aws") == "AWS"
    assert normalize_skill_name("Golang") == "Go"
    assert normalize_skill_name(".net") == ".NET Core"
    assert normalize_skill_name("k8s") == "Kubernetes"
    assert normalize_skill_name("nodejs") == "Node.js"


# ==========================================
# 2. False Positive Avoidance Tests
# ==========================================

def test_false_positive_skill_matching():
    """Verify strict word boundary matching prevents false positives for short/ambiguous terms."""
    extractor = SkillExtractor()

    # 'C' should NOT match 'vitamin C' or 'Class C'
    text_false = "Must have category C driving license and drink vitamin C."
    detected_false = [s["canonical_name"] for s in extractor.extract_skills(description=text_false)]
    assert "C" not in detected_false

    # 'C' SHOULD match in explicit technical context
    text_true_c = "Requirements: C/C++ programming and embedded C experience."
    detected_true_c = [s["canonical_name"] for s in extractor.extract_skills(description=text_true_c)]
    assert "C" in detected_true_c
    assert "C++" in detected_true_c

    # 'Go' should NOT match ordinary verb 'go'
    text_go_false = "We go to market fast and want candidates ready to go."
    detected_go_false = [s["canonical_name"] for s in extractor.extract_skills(description=text_go_false)]
    assert "Go" not in detected_go_false

    # 'Go' SHOULD match Golang or Go language
    text_go_true = "Senior Golang engineer with 3+ years Go language experience."
    detected_go_true = [s["canonical_name"] for s in extractor.extract_skills(description=text_go_true)]
    assert "Go" in detected_go_true


# ==========================================
# 3. Salary Statistical Calculations & Percentiles
# ==========================================

def test_salary_statistics_odd_and_even():
    """Verify median, Q1 (25th percentile), Q3 (75th percentile), min, and max."""
    # Odd count: 5 elements
    salaries_odd = [100000.0, 200000.0, 300000.0, 400000.0, 500000.0]
    stats_odd = calculate_salary_statistics(salaries_odd, "INR")
    assert stats_odd["min"] == 100000.0
    assert stats_odd["max"] == 500000.0
    assert stats_odd["median"] == 300000.0
    assert stats_odd["p25"] == 200000.0
    assert stats_odd["p75"] == 400000.0

    # Even count: 4 elements
    salaries_even = [100000.0, 200000.0, 300000.0, 400000.0]
    stats_even = calculate_salary_statistics(salaries_even, "INR")
    assert stats_even["min"] == 100000.0
    assert stats_even["max"] == 400000.0
    assert stats_even["median"] == 250000.0  # (200k + 300k) / 2
    assert stats_even["p25"] == 175000.0
    assert stats_even["p75"] == 325000.0

    # Empty list
    stats_empty = calculate_salary_statistics([], "INR")
    assert stats_empty["median"] is None
    assert stats_empty["jobs_with_salary"] == 0


def test_salary_normalization_and_lpa():
    """Verify LPA to annual conversion and hourly/monthly normalization."""
    # LPA format
    s_min, s_max, curr, period, norm = parse_and_normalize_salary(raw_text="Compensation: ₹6-12 LPA")
    assert s_min == 600000.0
    assert s_max == 1200000.0
    assert curr == "INR"
    assert period == "year"
    assert norm == 1200000.0

    # Hourly format ($50/hour)
    s_min, s_max, curr, period, norm = parse_and_normalize_salary(
        raw_min=50, raw_max=50, raw_currency="USD", raw_period="hour"
    )
    assert norm == 50 * 2080.0  # 104,000 USD/year

    # Unclear salary: do not guess!
    s_min, s_max, curr, period, norm = parse_and_normalize_salary(
        raw_min=500, raw_max=500, raw_currency="EUR", raw_period=None, raw_text="Equity only"
    )
    # When period cannot be determined confidently
    assert norm is None or period is not None


def test_currency_conversion():
    """Verify currency conversion service across INR, USD, EUR, GBP."""
    assert convert_currency(100.0, "USD", "USD") == 100.0
    inr_from_usd = convert_currency(10.0, "USD", "INR")
    assert inr_from_usd == 865.0  # 10 * 86.5
    usd_from_inr = convert_currency(865.0, "INR", "USD")
    assert usd_from_inr == 10.0


# ==========================================
# 4. In-Memory Database Fixture
# ==========================================

@pytest.fixture
def db_session():
    """Provide a fresh isolated SQLite in-memory database session."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()

    # Seed canonical taxonomy
    ensure_skills_taxonomy(session)

    yield session

    session.close()


# ==========================================
# 5. Date Filtering Tests
# ==========================================

def test_date_filtering(db_session):
    """Verify 7d, 30d, 90d filtering strictly scopes jobs by freshness date."""
    now = datetime.now(timezone.utc)

    # Job 1: posted 3 days ago (Real)
    j1 = Job(
        source="remotive",
        data_type="real",
        title="Software Engineer",
        posted_at=now - timedelta(days=3),
        collected_at=now,
    )
    # Job 2: posted 15 days ago (Real)
    j2 = Job(
        source="remotive",
        data_type="real",
        title="Software Engineer",
        posted_at=now - timedelta(days=15),
        collected_at=now,
    )
    # Job 3: posted 60 days ago (Real)
    j3 = Job(
        source="remotive",
        data_type="real",
        title="Software Engineer",
        posted_at=now - timedelta(days=60),
        collected_at=now,
    )

    db_session.add_all([j1, j2, j3])
    db_session.commit()

    # 7 days filter: only j1
    q_7d = get_jobs_query(db_session, time_period="7d")
    assert q_7d.count() == 1

    # 30 days filter: j1 and j2
    q_30d = get_jobs_query(db_session, time_period="30d")
    assert q_30d.count() == 2

    # 90 days filter: j1, j2, and j3
    q_90d = get_jobs_query(db_session, time_period="90d")
    assert q_90d.count() == 3


# ==========================================
# 6. Real vs Demo Separation Tests
# ==========================================

def test_real_vs_demo_separation(db_session):
    """Verify demo data is never mixed into default analytics queries."""
    now = datetime.now(timezone.utc)

    # 1 Real job
    j_real = Job(
        source="remotive",
        data_type="real",
        title="Real Engineer",
        posted_at=now,
        collected_at=now,
    )
    # 2 Demo jobs
    j_demo1 = Job(
        source="sample",
        data_type="demo",
        title="Demo Engineer 1",
        posted_at=now,
        collected_at=now,
    )
    j_demo2 = Job(
        source="sample",
        data_type="demo",
        title="Demo Engineer 2",
        posted_at=now,
        collected_at=now,
    )

    db_session.add_all([j_real, j_demo1, j_demo2])
    db_session.commit()

    # Default query (real data only)
    q_default = get_jobs_query(db_session)
    assert q_default.count() == 1
    assert q_default.first().title == "Real Engineer"

    # Explicit demo query
    q_demo = get_jobs_query(db_session, include_demo=True, data_type="demo")
    assert q_demo.count() == 2


# ==========================================
# 7. Trends & Insufficient Historical Data Tests
# ==========================================

def test_insufficient_historical_data_trend(db_session):
    """Verify system returns 'insufficient data' rather than fabricating trends."""
    now = datetime.now(timezone.utc)

    # Only 1 job in current period, 0 in previous period
    j = Job(
        source="remotive",
        data_type="real",
        title="Python Dev",
        posted_at=now - timedelta(days=5),
        collected_at=now,
    )
    db_session.add(j)
    db_session.commit()

    trends = calculate_trends(db_session, period="30d")
    assert trends["has_sufficient_data"] is False
    assert len(trends["emerging"]) == 0
    assert len(trends["declining"]) == 0
    assert "Not enough historical data" in trends["message"]


def test_trend_calculation_percentage_points(db_session):
    """Verify trend compares real periods and reports percentage points correctly."""
    now = datetime.now(timezone.utc)
    py_skill = db_session.query(Skill).filter(Skill.canonical_name == "Python").first()

    # Previous 30d window: [now - 60d, now - 30d] -> 10 jobs, 5 have Python (50.0%)
    for i in range(10):
        job = Job(
            source="remotive",
            data_type="real",
            title=f"Engineer Prev {i}",
            posted_at=now - timedelta(days=45),
            collected_at=now,
        )
        db_session.add(job)
        db_session.flush()
        if i < 5:
            db_session.add(JobSkill(job_id=job.id, skill_id=py_skill.id, confidence=1.0))

    # Current 30d window: [now - 30d, now] -> 10 jobs, 8 have Python (80.0%)
    for i in range(10):
        job = Job(
            source="remotive",
            data_type="real",
            title=f"Engineer Cur {i}",
            posted_at=now - timedelta(days=10),
            collected_at=now,
        )
        db_session.add(job)
        db_session.flush()
        if i < 8:
            db_session.add(JobSkill(job_id=job.id, skill_id=py_skill.id, confidence=1.0))

    db_session.commit()

    trends = calculate_trends(db_session, period="30d", min_jobs_threshold=2)
    assert trends["has_sufficient_data"] is True
    assert len(trends["emerging"]) > 0

    py_trend = next((s for s in trends["emerging"] if s["skill_name"] == "Python"), None)
    assert py_trend is not None
    assert py_trend["current_percentage"] == 80.0
    assert py_trend["previous_percentage"] == 50.0
    assert py_trend["change_pp"] == 30.0  # +30.0 percentage points


# ==========================================
# 8. Duplicate Job Detection Tests
# ==========================================

def test_duplicate_job_detection(db_session):
    """Verify duplicate external IDs or title/company do not create duplicate records."""
    jobs = [
        CollectedJob(
            source="remotive",
            external_id="ext_1001",
            title="Full Stack Developer",
            company_name="Acme Corp",
            location="Remote",
            description="Working with React and Node.js",
        ),
        # Identical external_id
        CollectedJob(
            source="remotive",
            external_id="ext_1001",
            title="Full Stack Developer",
            company_name="Acme Corp",
            location="Remote",
            description="Working with React and Node.js",
        ),
    ]

    res = ingest_jobs(jobs, db_session)
    assert res.retrieved == 2
    assert res.new_jobs == 1
    assert res.duplicates == 1

    total_in_db = db_session.query(Job).count()
    assert total_in_db == 1
