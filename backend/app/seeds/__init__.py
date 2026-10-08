"""Seeds package for initial database taxonomy and fixtures."""

from app.seeds.taxonomy import CANONICAL_SKILLS
from app.seeds.seed import seed_skills, seed_default_profile, run_all_seeds

__all__ = ["CANONICAL_SKILLS", "seed_skills", "seed_default_profile", "run_all_seeds"]
