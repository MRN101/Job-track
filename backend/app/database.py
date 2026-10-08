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

    # Create all tables
    Base.metadata.create_all(bind=_engine)

    # Seed initial data (canonical skills, default profile)
    from app.seeds.seed import run_all_seeds
    with _session_factory() as session:
        run_all_seeds(session)



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
