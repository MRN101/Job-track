"""User profile model for personal use."""

from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class UserProfile(Base):
    """Personal profile for skill gap analysis."""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True, default="India")
    preferred_locations = Column(Text, nullable=True)  # JSON string of locations
    target_roles = Column(Text, nullable=True)  # JSON string of roles
    experience_level = Column(String(50), nullable=True, default="0-2 years")
    skills = Column(Text, nullable=True)  # JSON string of skill names

    def __repr__(self):
        return f"<UserProfile(id={self.id}, name='{self.name}')>"
