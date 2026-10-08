"""Profile API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app.schemas.profile import ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
def get_profile(db: Session = Depends(get_db)):
    """Get the user profile (creates a default one if none exists)."""
    from app.models.profile import UserProfile

    profile = db.query(UserProfile).first()
    if not profile:
        # Create default profile
        profile = UserProfile(
            name="",
            country="India",
            preferred_locations="[]",
            target_roles='["Software Engineer"]',
            experience_level="0-2 years",
            skills="[]",
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return ProfileResponse(
        id=profile.id,
        name=profile.name or "",
        country=profile.country or "India",
        preferred_locations=json.loads(profile.preferred_locations or "[]"),
        target_roles=json.loads(profile.target_roles or '["Software Engineer"]'),
        experience_level=profile.experience_level or "0-2 years",
        skills=json.loads(profile.skills or "[]"),
    )


@router.put("", response_model=ProfileResponse)
def update_profile(data: ProfileUpdate, db: Session = Depends(get_db)):
    """Update the user profile."""
    from app.models.profile import UserProfile

    profile = db.query(UserProfile).first()
    if not profile:
        profile = UserProfile()
        db.add(profile)

    profile.name = data.name
    profile.country = data.country
    profile.preferred_locations = json.dumps(data.preferred_locations)
    profile.target_roles = json.dumps(data.target_roles)
    profile.experience_level = data.experience_level
    profile.skills = json.dumps(data.skills)

    db.commit()
    db.refresh(profile)

    return ProfileResponse(
        id=profile.id,
        name=profile.name or "",
        country=profile.country or "India",
        preferred_locations=json.loads(profile.preferred_locations or "[]"),
        target_roles=json.loads(profile.target_roles or '["Software Engineer"]'),
        experience_level=profile.experience_level or "0-2 years",
        skills=json.loads(profile.skills or "[]"),
    )
