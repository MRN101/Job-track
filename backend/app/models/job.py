"""Job model."""

from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class Job(Base):
    """Represents a job listing collected from a data source."""

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False, index=True)
    external_id = Column(String(255), nullable=True)
    title = Column(String(500), nullable=False, index=True)
    company_name = Column(String(255), nullable=True, index=True)
    company_id = Column(Integer, nullable=True)
    location = Column(String(255), nullable=True, index=True)
    country = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(10), nullable=True)
    employment_type = Column(String(50), nullable=True)
    experience_level = Column(String(50), nullable=True)
    posted_at = Column(DateTime, nullable=True, index=True)
    url = Column(String(1000), nullable=True)
    collected_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    job_skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")

    __table_args__ = (
        # Deduplication: unique on source + external_id when external_id exists
        Index("ix_jobs_source_external_id", "source", "external_id", unique=True),
    )

    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title}', company='{self.company_name}')>"
