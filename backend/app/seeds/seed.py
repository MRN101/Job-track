"""Database seeding utilities for canonical skills and default data."""

import logging
from sqlalchemy.orm import Session
from app.models.skill import Skill
from app.models.profile import UserProfile
from app.seeds.taxonomy import CANONICAL_SKILLS

logger = logging.getLogger(__name__)


def seed_skills(db: Session) -> int:
    """Seed canonical skills if they do not exist. Returns number of newly added skills."""
    existing_skills = {s.name.lower(): s for s in db.query(Skill).all()}
    added = 0

    for item in CANONICAL_SKILLS:
        if item["name"].lower() not in existing_skills:
            skill = Skill(
                name=item["name"],
                canonical_name=item["canonical_name"],
                category=item["category"],
                description=item.get("description", ""),
            )
            db.add(skill)
            added += 1

    if added > 0:
        db.commit()
        logger.info(f"Seeded {added} new canonical skills.")
    return added


def seed_default_profile(db: Session) -> UserProfile:
    """Ensure a default user profile exists."""
    profile = db.query(UserProfile).first()
    if not profile:
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
        logger.info("Initialized default user profile.")
    return profile


def run_all_seeds(db: Session):
    """Run all database seeders."""
    seed_skills(db)
    seed_default_profile(db)
