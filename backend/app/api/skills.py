"""Skills API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.schemas.skill import SkillResponse

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("", response_model=List[SkillResponse])
def list_skills(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all canonical skills, optionally filtered."""
    from app.models.skill import Skill

    query = db.query(Skill)

    if category:
        query = query.filter(Skill.category == category)
    if search:
        query = query.filter(Skill.canonical_name.ilike(f"%{search}%"))

    skills = query.order_by(Skill.canonical_name).all()

    return [
        SkillResponse(
            id=s.id,
            name=s.name,
            canonical_name=s.canonical_name,
            category=s.category,
            description=s.description,
        )
        for s in skills
    ]


@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    """Get a single skill by ID."""
    from app.models.skill import Skill
    from fastapi import HTTPException

    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    return SkillResponse(
        id=skill.id,
        name=skill.name,
        canonical_name=skill.canonical_name,
        category=skill.category,
        description=skill.description,
    )
