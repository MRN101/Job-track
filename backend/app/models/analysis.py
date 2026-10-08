"""Analysis models for tracking runs and skill demand over time."""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class AnalysisRun(Base):
    """Represents a single analysis run with specific parameters."""

    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=True, default="all")  # all, adzuna, remotive, sample
    data_type = Column(String(20), nullable=False, default="real", index=True)  # real, demo
    country = Column(String(100), nullable=True)
    role = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    experience_level = Column(String(50), nullable=True)
    time_period_start = Column(DateTime, nullable=True)
    time_period_end = Column(DateTime, nullable=True)
    start_date = Column(DateTime, nullable=True)  # Kept for backward compatibility
    end_date = Column(DateTime, nullable=True)    # Kept for backward compatibility
    jobs_analyzed = Column(Integer, nullable=False, default=0)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationships
    skill_demands = relationship("SkillDemand", back_populates="analysis_run", cascade="all, delete-orphan")

    def __repr__(self):
        return (
            f"<AnalysisRun(id={self.id}, role='{self.role}', "
            f"type='{self.data_type}', jobs_analyzed={self.jobs_analyzed})>"
        )


class SkillDemand(Base):
    """Skill demand data for a specific analysis run."""

    __tablename__ = "skill_demands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_run_id = Column(
        Integer,
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id = Column(
        Integer,
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_count = Column(Integer, nullable=False, default=0)
    percentage = Column(Float, nullable=False, default=0.0)

    # Relationships
    analysis_run = relationship("AnalysisRun", back_populates="skill_demands")
    skill = relationship("Skill", back_populates="skill_demands")

    __table_args__ = (
        Index("ix_skill_demands_run_skill", "analysis_run_id", "skill_id", unique=True),
    )

    def __repr__(self):
        return (
            f"<SkillDemand(run_id={self.analysis_run_id}, "
            f"skill_id={self.skill_id}, percentage={self.percentage})>"
        )
