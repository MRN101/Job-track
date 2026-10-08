"""Job data ingestion and collection service."""

import logging
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.job import Job
from app.models.company import Company
from app.models.skill import Skill, JobSkill, CandidateSkill
from app.analyzers.taxonomy import TAXONOMY
from app.analyzers.skill_extractor import get_skill_extractor
from app.collectors import get_collector, CollectedJob, CollectionResult

logger = logging.getLogger(__name__)


def ensure_skills_taxonomy(db: Session) -> int:
    """Ensure canonical skills from taxonomy are seeded into the database.
    Returns number of newly seeded skills.
    """
    all_db_skills = db.query(Skill).all()
    existing_by_name = {s.name.lower(): s for s in all_db_skills}
    existing_by_canonical = {s.canonical_name.lower(): s for s in all_db_skills}
    new_count = 0

    for item in TAXONOMY:
        name_lower = item["name"].lower()
        c_name_lower = item["canonical_name"].lower()
        if name_lower not in existing_by_name and c_name_lower not in existing_by_canonical:
            skill = Skill(
                name=item["name"],
                canonical_name=item["canonical_name"],
                category=item.get("category"),
                description=f"Standard skill for {item['canonical_name']}",
            )
            db.add(skill)
            existing_by_name[name_lower] = skill
            existing_by_canonical[c_name_lower] = skill
            new_count += 1

    if new_count > 0:
        db.commit()
        logger.info(f"Seeded {new_count} skills into the canonical taxonomy.")

    return new_count


def ingest_jobs(collected_jobs: List[CollectedJob], db: Session) -> CollectionResult:
    """Process and save collected jobs, extracting and linking skills."""
    # Ensure taxonomy is loaded
    ensure_skills_taxonomy(db)

    # Cache canonical skills by name and canonical_name
    skills_map = {}
    for s in db.query(Skill).all():
        skills_map[s.name.lower()] = s
        skills_map[s.canonical_name.lower()] = s
    extractor = get_skill_extractor()

    result = CollectionResult(
        source=collected_jobs[0].source if collected_jobs else "unknown",
        retrieved=len(collected_jobs),
    )

    for item in collected_jobs:
        try:
            # Deduplication check
            existing = None
            if item.external_id:
                existing = db.query(Job).filter(
                    Job.source == item.source,
                    Job.external_id == item.external_id,
                ).first()

            if not existing and item.title and item.company_name:
                existing = db.query(Job).filter(
                    Job.title == item.title,
                    Job.company_name == item.company_name,
                ).first()

            if existing:
                result.duplicates += 1
                continue

            # Find or create company
            company_id = None
            if item.company_name:
                comp = db.query(Company).filter(Company.name == item.company_name).first()
                if not comp:
                    comp = Company(
                        name=item.company_name,
                        normalized_name=item.company_name.lower().strip(),
                        location=item.location,
                    )
                    db.add(comp)
                    db.flush()
                company_id = comp.id

            # Create job record
            new_job = Job(
                source=item.source,
                external_id=item.external_id,
                title=item.title,
                company_name=item.company_name,
                company_id=company_id,
                location=item.location,
                country=item.country or "India",
                description=item.description,
                salary_min=item.salary_min,
                salary_max=item.salary_max,
                salary_currency=item.salary_currency or "INR",
                employment_type=item.employment_type or "full_time",
                experience_level=item.experience_level,
                posted_at=item.posted_at or datetime.now(timezone.utc),
                url=item.url,
                collected_at=datetime.now(timezone.utc),
            )
            db.add(new_job)
            db.flush()

            # Extract skills
            extracted = extractor.extract_skills(
                title=item.title or "",
                description=item.description or "",
            )

            for sk in extracted:
                canonical = sk["canonical_name"].lower()
                skill_obj = skills_map.get(canonical)
                if skill_obj:
                    # Link skill to job
                    job_skill = JobSkill(
                        job_id=new_job.id,
                        skill_id=skill_obj.id,
                        confidence=sk.get("confidence", 1.0),
                        extraction_method="dictionary",
                    )
                    db.add(job_skill)

            result.new_jobs += 1

        except Exception as e:
            result.errors += 1
            result.error_messages.append(str(e))
            logger.error(f"Error ingesting job '{item.title}': {e}")

    db.commit()
    return result


def collect_and_ingest(
    source: str = "sample",
    country: str = "India",
    role: str = "Software Engineer",
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    max_results: int = 50,
    db: Optional[Session] = None,
) -> CollectionResult:
    """Collect jobs using specified source and ingest into database."""
    collector = get_collector(source)
    if not collector:
        res = CollectionResult(source=source)
        res.errors = 1
        res.error_messages.append(f"Collector '{source}' not found or unsupported.")
        return res

    collected_jobs = collector.collect(
        country=country,
        role=role,
        location=location,
        experience_level=experience_level,
        max_results=max_results,
    )

    if not collected_jobs:
        return CollectionResult(
            source=source,
            retrieved=0,
            new_jobs=0,
            duplicates=0,
            errors=0 if collector.is_configured() else 1,
            error_messages=[] if collector.is_configured() else ["Collector not configured with valid API keys."],
        )

    return ingest_jobs(collected_jobs, db)
