"""Skill models."""

from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class Skill(Base):
    """Represents a canonical skill in the taxonomy."""

    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    canonical_name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)

    # Relationships
    job_skills = relationship("JobSkill", back_populates="skill")
    skill_demands = relationship("SkillDemand", back_populates="skill")

    def __repr__(self):
        return f"<Skill(id={self.id}, name='{self.name}', category='{self.category}')>"


class JobSkill(Base):
    """Association between a job and a detected skill."""

    __tablename__ = "job_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    confidence = Column(Float, nullable=False, default=1.0)
    extraction_method = Column(String(50), nullable=False, default="dictionary")

    # Relationships
    job = relationship("Job", back_populates="job_skills")
    skill = relationship("Skill", back_populates="job_skills")

    __table_args__ = (
        Index("ix_job_skills_job_skill", "job_id", "skill_id", unique=True),
    )

    def __repr__(self):
        return f"<JobSkill(job_id={self.job_id}, skill_id={self.skill_id}, confidence={self.confidence})>"


class CandidateSkill(Base):
    """Skills detected by LLM or heuristics that are not yet in the canonical taxonomy."""

    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    occurrences = Column(Integer, nullable=False, default=1)
    confidence = Column(Float, nullable=False, default=0.8)
    source_method = Column(String(50), nullable=False, default="heuristic")
    first_seen = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    approved = Column(Integer, nullable=False, default=0)  # 0=pending, 1=approved, -1=rejected

    def __repr__(self):
        return f"<CandidateSkill(name='{self.name}', occurrences={self.occurrences}, approved={self.approved})>"
