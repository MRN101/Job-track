"""Database connection and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator
import os

from app.config import get_settings

# Create the declarative base for models
Base = declarative_base()


def get_engine():
    """Create and return the SQLAlchemy engine."""
    settings = get_settings()
    db_url = settings.database_url

    # SQLite-specific settings
    if db_url.startswith("sqlite"):
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=False,
        )
    else:
        # PostgreSQL or other databases
        engine = create_engine(db_url, echo=False, pool_pre_ping=True)

    return engine


def get_session_factory():
    """Create and return a session factory."""
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Lazy-initialized globals
_engine = None
_session_factory = None


def init_db():
    """Initialize the database engine and session factory."""
    global _engine, _session_factory
    _engine = get_engine()
    _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    # Ensure data directory exists for SQLite
    settings = get_settings()
    if settings.database_url.startswith("sqlite"):
        db_path = settings.database_url.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    # Import all models so Base.metadata is aware of them
    import app.models.job  # noqa: F401
    import app.models.skill  # noqa: F401
    import app.models.company  # noqa: F401
    import app.models.analysis  # noqa: F401
    import app.models.profile  # noqa: F401
    import app.models.collection  # noqa: F401

    # Create all tables
    Base.metadata.create_all(bind=_engine)

    # Auto-migrate missing columns for existing SQLite databases
    _auto_migrate(_engine)

    # Backfill role & location normalization for any unnormalized jobs
    _backfill_normalizations(_session_factory)

    # Seed initial data (canonical skills, default profile)
    from app.seeds.seed import run_all_seeds
    with _session_factory() as session:
        run_all_seeds(session)


def _auto_migrate(engine):
    """Safely add new columns to existing tables if they don't exist yet."""
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.connect() as conn:
        # 1. Migrate 'jobs' table
        if "jobs" in existing_tables:
            job_cols = {c["name"] for c in inspector.get_columns("jobs")}
            if "data_type" not in job_cols:
                conn.execute(text("ALTER TABLE jobs ADD COLUMN data_type VARCHAR(20) DEFAULT 'real'"))
            if "role_family" not in job_cols:
                conn.execute(text("ALTER TABLE jobs ADD COLUMN role_family VARCHAR(100)"))
            if "normalized_role" not in job_cols:
                conn.execute(text("ALTER TABLE jobs ADD COLUMN normalized_role VARCHAR(100)"))
            if "normalized_city" not in job_cols:
                conn.execute(text("ALTER TABLE jobs ADD COLUMN normalized_city VARCHAR(100)"))
            if "state" not in job_cols:
                conn.execute(text("ALTER TABLE jobs ADD COLUMN state VARCHAR(100)"))
            if "is_remote" not in job_cols:
                conn.execute(text("ALTER TABLE jobs ADD COLUMN is_remote INTEGER DEFAULT 0"))
            if "salary_period" not in job_cols:
                conn.execute(text("ALTER TABLE jobs ADD COLUMN salary_period VARCHAR(20)"))
            if "salary_normalized" not in job_cols:
                conn.execute(text("ALTER TABLE jobs ADD COLUMN salary_normalized FLOAT"))
            if "first_seen_at" not in job_cols:
                conn.execute(text("ALTER TABLE jobs ADD COLUMN first_seen_at TIMESTAMP"))
            if "last_seen_at" not in job_cols:
                conn.execute(text("ALTER TABLE jobs ADD COLUMN last_seen_at TIMESTAMP"))
            if "content_hash" not in job_cols:
                conn.execute(text("ALTER TABLE jobs ADD COLUMN content_hash VARCHAR(64)"))
            # Ensure existing sample jobs are marked as demo
            conn.execute(text("UPDATE jobs SET data_type = 'demo' WHERE source = 'sample' OR source = 'demo'"))
            conn.execute(text("UPDATE jobs SET first_seen_at = collected_at WHERE first_seen_at IS NULL"))
            conn.execute(text("UPDATE jobs SET last_seen_at = collected_at WHERE last_seen_at IS NULL"))

        # 2. Migrate 'analysis_runs' table
        if "analysis_runs" in existing_tables:
            run_cols = {c["name"] for c in inspector.get_columns("analysis_runs")}
            if "source" not in run_cols:
                conn.execute(text("ALTER TABLE analysis_runs ADD COLUMN source VARCHAR(50) DEFAULT 'all'"))
            if "data_type" not in run_cols:
                conn.execute(text("ALTER TABLE analysis_runs ADD COLUMN data_type VARCHAR(20) DEFAULT 'real'"))
            if "time_period_start" not in run_cols:
                conn.execute(text("ALTER TABLE analysis_runs ADD COLUMN time_period_start TIMESTAMP"))
            if "time_period_end" not in run_cols:
                conn.execute(text("ALTER TABLE analysis_runs ADD COLUMN time_period_end TIMESTAMP"))

        # 3. Migrate 'candidate_skills' table
        if "candidate_skills" in existing_tables:
            cand_cols = {c["name"] for c in inspector.get_columns("candidate_skills")}
            if "confidence" not in cand_cols:
                conn.execute(text("ALTER TABLE candidate_skills ADD COLUMN confidence FLOAT DEFAULT 0.8"))
            if "normalized_name" not in cand_cols:
                conn.execute(text("ALTER TABLE candidate_skills ADD COLUMN normalized_name VARCHAR(255)"))
            if "job_count" not in cand_cols:
                conn.execute(text("ALTER TABLE candidate_skills ADD COLUMN job_count INTEGER DEFAULT 1"))
            if "status" not in cand_cols:
                conn.execute(text("ALTER TABLE candidate_skills ADD COLUMN status VARCHAR(20) DEFAULT 'candidate'"))
            if "first_seen" not in cand_cols:
                conn.execute(text("ALTER TABLE candidate_skills ADD COLUMN first_seen TIMESTAMP"))
            if "last_seen" not in cand_cols:
                conn.execute(text("ALTER TABLE candidate_skills ADD COLUMN last_seen TIMESTAMP"))
            if "first_seen_at" not in cand_cols:
                conn.execute(text("ALTER TABLE candidate_skills ADD COLUMN first_seen_at TIMESTAMP"))
            if "last_seen_at" not in cand_cols:
                conn.execute(text("ALTER TABLE candidate_skills ADD COLUMN last_seen_at TIMESTAMP"))

        conn.commit()


def _backfill_normalizations(session_factory):
    """Backfill role_family, normalized_role, and normalized location on existing jobs if missing."""
    from app.models.job import Job
    from app.analyzers.role_classifier import classify_role
    from app.analyzers.location_normalizer import normalize_location

    with session_factory() as session:
        unnormalized_jobs = session.query(Job).filter(
            (Job.role_family.is_(None)) | (Job.normalized_city.is_(None))
        ).limit(1000).all()

        if unnormalized_jobs:
            for j in unnormalized_jobs:
                if not j.role_family or not j.normalized_role:
                    fam, norm_role = classify_role(j.title)
                    j.role_family = fam
                    j.normalized_role = norm_role
                if not j.normalized_city:
                    loc_data = normalize_location(j.location, j.country)
                    j.normalized_city = loc_data["normalized_city"]
                    j.state = loc_data["state"]
                    j.country = loc_data["country"]
                    j.is_remote = 1 if loc_data["is_remote"] else 0
            session.commit()



def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session."""
    global _session_factory
    if _session_factory is None:
        init_db()
    db = _session_factory()
    try:
        yield db
    finally:
        db.close()
