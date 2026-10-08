"""Company model."""

from sqlalchemy import Column, Integer, String, Index

from app.database import Base


class Company(Base):
    """Represents a company found in job listings."""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    normalized_name = Column(String(255), nullable=True, unique=True, index=True)
    location = Column(String(255), nullable=True)
    industry = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}')>"
