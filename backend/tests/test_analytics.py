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


# ==========================================
# 9. Strict False Positive Tests (Phase 22)
# ==========================================

def test_false_positives_all_short_skills():
    """Verify strict word boundary matching for C, R, Go, .NET, AI, SQL, AWS."""
    extractor = SkillExtractor()

    # --- C & R ---
    # Negative
    neg_cr = "Looking for candidate with class C driver license and grade R early education."
    detected = [s["canonical_name"] for s in extractor.extract_skills(description=neg_cr)]
    assert "C" not in detected
    assert "R" not in detected

    # Positive
    pos_cr = "Embedded C developer with R programming for statistical data modeling."
    detected_pos = [s["canonical_name"] for s in extractor.extract_skills(description=pos_cr)]
    assert "C" in detected_pos
    assert "R" in detected_pos

    # --- Go ---
    # Negative
    neg_go = "We must go forward and let nothing go wrong in our fast go-to-market."
    detected_go = [s["canonical_name"] for s in extractor.extract_skills(description=neg_go)]
    assert "Go" not in detected_go

    # Positive
    pos_go = "Senior Golang engineer writing Go backend services."
    detected_pos_go = [s["canonical_name"] for s in extractor.extract_skills(description=pos_go)]
    assert "Go" in detected_pos_go

    # --- .NET ---
    # Negative
    neg_dotnet = "Visit our site at company.net or read the net proceeds."
    detected_dotnet = [s["canonical_name"] for s in extractor.extract_skills(description=neg_dotnet)]
    assert ".NET Core" not in detected_dotnet

    # Positive
    pos_dotnet = "C# .NET developer proficient with ASP.NET Core web APIs."
    detected_pos_dotnet = [s["canonical_name"] for s in extractor.extract_skills(description=pos_dotnet)]
    assert ".NET Core" in detected_pos_dotnet

    # --- AI ---
    # Negative
    neg_ai = "We aim to assist and aid our customers with main solutions."
    detected_ai = [s["canonical_name"] for s in extractor.extract_skills(description=neg_ai)]
    assert "AI" not in detected_ai

    # Positive
    pos_ai = "Building modern AI systems and generative AI/ML architectures."
    detected_pos_ai = [s["canonical_name"] for s in extractor.extract_skills(description=pos_ai)]
    assert "AI" in detected_pos_ai

    # --- SQL & AWS ---
    # Positive
    pos_sql_aws = "Strong SQL querying skills and deployment on AWS cloud infrastructure."
    detected_sql_aws = [s["canonical_name"] for s in extractor.extract_skills(description=pos_sql_aws)]
    assert "SQL" in detected_sql_aws
    assert "AWS" in detected_sql_aws


# ==========================================
# 10. Role Taxonomy & Classification Tests
# ==========================================

def test_role_classification():
    """Verify deterministic role taxonomy classifications."""
    from app.analyzers.role_classifier import classify_role

    # Software Engineering
    f1, r1 = classify_role("Senior Backend Engineer (Python)")
    assert f1 == "Software Engineering"
    assert r1 == "Backend Engineer"

    f2, r2 = classify_role("SDE 2")
    assert f2 == "Software Engineering"
    assert r2 == "Software Engineer"

    f3, r3 = classify_role("Full Stack Web Developer")
    assert f3 == "Software Engineering"
    assert r3 == "Full Stack Engineer"

    # AI & Data
    f4, r4 = classify_role("Staff Machine Learning Engineer")
    assert f4 == "AI & Machine Learning"
    assert r4 == "Machine Learning Engineer"

    f5, r5 = classify_role("Lead Data Scientist")
    assert f5 == "AI & Machine Learning"
    assert r5 == "Data Scientist"

    f6, r6 = classify_role("Senior BI / Data Analyst")
    assert f6 == "Data & Analytics"
    assert r6 == "Data Analyst"

    # DevOps
    f7, r7 = classify_role("Site Reliability Engineer (SRE)")
    assert f7 == "Cloud & DevOps"
    assert r7 == "Site Reliability Engineer (SRE)"


# ==========================================
# 11. Location Normalization Tests
# ==========================================

def test_location_normalization():
    """Verify normalization of Indian metros, global tech hubs, and remote flags."""
    from app.analyzers.location_normalizer import normalize_location

    # Bengaluru variants
    loc1 = normalize_location("Bangalore, Karnataka")
    assert loc1["normalized_city"] == "Bengaluru"
    assert loc1["state"] == "Karnataka"
    assert loc1["country"] == "India"

    loc2 = normalize_location("bengaluru")
    assert loc2["normalized_city"] == "Bengaluru"

    # Bombay / Mumbai
    loc3 = normalize_location("Bombay, MH")
    assert loc3["normalized_city"] == "Mumbai"

    # Calcutta / Kolkata
    loc4 = normalize_location("Calcutta")
    assert loc4["normalized_city"] == "Kolkata"

    # Madras / Chennai
    loc5 = normalize_location("Madras, Tamil Nadu")
    assert loc5["normalized_city"] == "Chennai"

    # Remote
    loc6 = normalize_location("Remote - Worldwide")
    assert loc6["is_remote"] is True
    assert loc6["normalized_city"] == "Remote"

    # Global Hub
    loc7 = normalize_location("San Francisco, CA")
    assert loc7["normalized_city"] == "San Francisco"
    assert loc7["country"] == "United States"


# ==========================================
# 12. Candidate Skill Discovery Tests
# ==========================================

def test_candidate_skill_discovery():
    """Verify discovery of new technologies without polluting canonical skills."""
    from app.analyzers.candidate_extractor import extract_candidate_skills

    known = {"Python", "JavaScript", "React", "PostgreSQL", "AWS"}
    text = (
        "Seeking an engineer skilled in Python and React. Experience with MCP protocol, "
        "LangChain orchestration, and WASM compilation is a huge plus."
    )
    candidates = extract_candidate_skills(text, known)
    cand_names = [c["name"].upper() for c in candidates]

    assert "MCP" in cand_names
    assert "WASM" in cand_names
    assert "PYTHON" not in cand_names  # Already in known
    assert "REACT" not in cand_names   # Already in known


# ==========================================
# 13. End-to-End Pipeline Integration Test (Phase 29)
# ==========================================

def test_end_to_end_pipeline(db_session):
    """End-to-end integration: Collector -> DB -> Skills/Roles/Location -> Analysis Snapshot -> Trends."""
    from app.services.analysis_service import run_analysis_snapshot

    now = datetime.now(timezone.utc)

    # 1. Simulate collected jobs
    raw_jobs = [
        CollectedJob(
            source="remotive",
            external_id="e2e_1",
            title="Senior Backend Engineer",
            company_name="TechCorp India",
            location="Bangalore, Karnataka",
            country="India",
            description="We build Python backend systems using FastAPI, PostgreSQL, and AWS.",
            posted_at=now - timedelta(days=5),
        ),
        CollectedJob(
            source="remotive",
            external_id="e2e_2",
            title="Full Stack Developer",
            company_name="Innovate Ltd",
            location="Bombay",
            country="India",
            description="Looking for Python and React developers with SQL and Docker.",
            posted_at=now - timedelta(days=10),
        ),
    ]

    # 2. Ingest
    result = ingest_jobs(raw_jobs, db_session)
    assert result.retrieved == 2
    assert result.new_jobs == 2

    # 3. Verify Database normalization
    stored_jobs = db_session.query(Job).all()
    assert len(stored_jobs) == 2

    j1 = next(j for j in stored_jobs if j.external_id == "e2e_1")
    assert j1.role_family == "Software Engineering"
    assert j1.normalized_role == "Backend Engineer"
    assert j1.normalized_city == "Bengaluru"

    j2 = next(j for j in stored_jobs if j.external_id == "e2e_2")
    assert j2.normalized_city == "Mumbai"

    # 4. Verify Skills Extracted
    j1_skills = [js.skill.canonical_name for js in j1.job_skills]
    assert "Python" in j1_skills
    assert "FastAPI" in j1_skills
    assert "PostgreSQL" in j1_skills
    assert "AWS" in j1_skills

    # 5. Run Snapshot
    snapshot = run_analysis_snapshot(
        db=db_session,
        country="India",
        role="Software Engineering",
        data_type="real",
    )
    assert snapshot.jobs_analyzed == 2

    # 6. Query filtered query service
    q = get_jobs_query(
        db=db_session,
        role_family="Software Engineering",
        normalized_city="Bengaluru",
        data_type="real",
    )
    assert q.count() == 1
    assert q.first().external_id == "e2e_1"

