"""Collection run model for tracking collection executions and statistics."""

from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone

from app.database import Base


class CollectionRun(Base):
    """Represents a scheduled or manual job data collection run."""

    __tablename__ = "collection_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="running", index=True)  # running, completed, partial, failed
    started_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Counts
    jobs_retrieved = Column(Integer, nullable=False, default=0)
    new_jobs = Column(Integer, nullable=False, default=0)
    updated_jobs = Column(Integer, nullable=False, default=0)
    duplicates = Column(Integer, nullable=False, default=0)
    failed_jobs = Column(Integer, nullable=False, default=0)
    skills_extracted = Column(Integer, nullable=False, default=0)

    # Errors & Details
    error_message = Column(Text, nullable=True)

    def __repr__(self):
        return (
            f"<CollectionRun(id={self.id}, source='{self.source}', status='{self.status}', "
            f"new={self.new_jobs}, dupes={self.duplicates})>"
        )
