"""Job data ingestion, deduplication, and collection service."""

import hashlib
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.job import Job
from app.models.company import Company
from app.models.skill import Skill, JobSkill, CandidateSkill
from app.models.collection import CollectionRun
from app.analyzers.taxonomy import TAXONOMY
from app.analyzers.skill_extractor import get_skill_extractor, normalize_skill_name
from app.analyzers.role_classifier import classify_role
from app.analyzers.location_normalizer import normalize_location
from app.collectors.base import CollectedJob, CollectionResult

logger = logging.getLogger(__name__)


def compute_job_content_hash(company_name: Optional[str], title: str, location: Optional[str]) -> str:
    """Compute deterministic SHA-256 hash for deduplication fallback."""
    c = (company_name or "").strip().lower()
    t = (title or "").strip().lower()
    l = (location or "").strip().lower()
    raw = f"{c}|{t}|{l}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


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
    """Process and save collected jobs with robust deduplication, role/location normalization, and skill extraction."""
    if not collected_jobs:
        return CollectionResult(source="none", retrieved=0)

    # Ensure canonical taxonomy is loaded
    ensure_skills_taxonomy(db)

    # Cache canonical skills by name and canonical_name
    skills_map = {}
    for s in db.query(Skill).all():
        skills_map[s.name.lower()] = s
        skills_map[s.canonical_name.lower()] = s

    extractor = get_skill_extractor()
    now_utc = datetime.now(timezone.utc)

    result = CollectionResult(
        source=collected_jobs[0].source if collected_jobs else "unknown",
        retrieved=len(collected_jobs),
    )

    for item in collected_jobs:
        try:
            content_hash = compute_job_content_hash(item.company_name, item.title, item.location)

            # 1. Deduplication check: by (source, external_id)
            existing = None
            if item.external_id:
                existing = db.query(Job).filter(
                    Job.source == item.source,
                    Job.external_id == item.external_id,
                ).first()

            # 2. Fallback deduplication: by content hash or title + company
            if not existing and content_hash:
                existing = db.query(Job).filter(
                    Job.content_hash == content_hash
                ).first()

            if not existing and item.title and item.company_name:
                existing = db.query(Job).filter(
                    Job.title.ilike(item.title.strip()),
                    Job.company_name.ilike(item.company_name.strip()),
                ).first()

            # If job already exists, increment deduplication count and update last_seen_at
            if existing:
                existing.last_seen_at = now_utc
                result.duplicates += 1
                continue

            # Find or create company
            company_id = None
            if item.company_name:
                comp_norm = item.company_name.lower().strip()
                comp = db.query(Company).filter(Company.normalized_name == comp_norm).first()
                if not comp:
                    comp = Company(
                        name=item.company_name.strip(),
                        normalized_name=comp_norm,
                        location=item.location,
                    )
                    db.add(comp)
                    db.flush()
                company_id = comp.id

            # Classify role taxonomy
            role_family, normalized_role = classify_role(item.title)

            # Normalize location
            loc_data = normalize_location(item.location, item.country or "India")

            # Create new job record
            new_job = Job(
                source=item.source,
                data_type=item.data_type or "real",
                external_id=item.external_id,
                title=item.title.strip(),
                company_name=item.company_name.strip() if item.company_name else None,
                company_id=company_id,
                location=item.location.strip() if item.location else None,
                country=loc_data["country"] or item.country or "India",
                role_family=role_family,
                normalized_role=normalized_role,
                normalized_city=loc_data["normalized_city"],
                state=loc_data["state"],
                is_remote=1 if loc_data["is_remote"] else 0,
                description=item.description,
                salary_min=item.salary_min,
                salary_max=item.salary_max,
                salary_currency=item.salary_currency or "INR",
                salary_period=item.salary_period,
                salary_normalized=item.salary_normalized,
                employment_type=item.employment_type or "full_time",
                experience_level=item.experience_level,
                posted_at=item.posted_at or now_utc,
                url=item.url,
                collected_at=now_utc,
                first_seen_at=now_utc,
                last_seen_at=now_utc,
                content_hash=content_hash,
            )
            db.add(new_job)
            db.flush()

            # Extract skills using strict extractor
            extracted = extractor.extract_skills(
                title=item.title or "",
                description=item.description or "",
            )

            linked_skill_ids = set()
            for sk in extracted:
                canonical = sk["canonical_name"].lower()
                skill_obj = skills_map.get(canonical)
                if skill_obj and skill_obj.id not in linked_skill_ids:
                    linked_skill_ids.add(skill_obj.id)
                    job_skill = JobSkill(
                        job_id=new_job.id,
                        skill_id=skill_obj.id,
                        confidence=sk.get("confidence", 1.0),
                        extraction_method="dictionary",
                    )
                    db.add(job_skill)

            # Discover and track candidate skills for emerging tech radar
            from app.analyzers.candidate_extractor import extract_candidate_skills
            full_text = f"{item.title or ''} {item.description or ''}"
            cand_list = extract_candidate_skills(full_text, set(skills_map.keys()))
            for cand in cand_list:
                c_norm = cand["normalized_name"]
                c_db = db.query(CandidateSkill).filter(
                    (CandidateSkill.name.ilike(cand["name"])) | (CandidateSkill.normalized_name == c_norm)
                ).first()
                if c_db:
                    c_db.job_count = (c_db.job_count or 0) + 1
                    c_db.occurrences = (c_db.occurrences or 0) + 1
                    c_db.last_seen_at = now_utc
                    c_db.last_seen = now_utc
                else:
                    new_cand = CandidateSkill(
                        name=cand["name"],
                        normalized_name=c_norm,
                        job_count=1,
                        occurrences=1,
                        confidence=cand["confidence"],
                        status="candidate",
                        first_seen_at=now_utc,
                        last_seen_at=now_utc,
                        first_seen=now_utc,
                        last_seen=now_utc,
                        source_method="heuristic",
                    )
                    db.add(new_cand)

            result.new_jobs += 1

        except Exception as e:
            result.errors += 1
            result.error_messages.append(f"Error ingesting '{item.title}': {str(e)}")
            logger.error(f"Error ingesting job '{item.title}': {e}")

    db.commit()
    return result


def collect_and_ingest(
    source: str = "remotive",
    country: str = "Worldwide",
    role: str = "Software Engineer",
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    max_results: int = 50,
    db: Optional[Session] = None,
) -> CollectionResult:
    """Collect jobs using specified source or 'all' sources, and ingest into database.
    Catches source errors gracefully without crashing the overall collection process.
    """
    sources_to_run = []
    if source in ("all", "all_real"):
        sources_to_run = ["remotive", "adzuna"]
    else:
        sources_to_run = [source]

    combined_result = CollectionResult(source=source)
    details: Dict[str, Any] = {}

    from app.collectors import get_collector

    for src_name in sources_to_run:
        collector = get_collector(src_name)
        if not collector:
            combined_result.errors += 1
            msg = f"Collector '{src_name}' not found or unsupported."
            combined_result.error_messages.append(msg)
            details[src_name] = {"status": "error", "message": msg}
            continue

        run_record = None
        start_time = datetime.now(timezone.utc)
        if db:
            try:
                run_record = CollectionRun(
                    source=src_name,
                    status="running",
                    started_at=start_time,
                )
                db.add(run_record)
                db.commit()
            except Exception as e:
                logger.warning(f"Could not persist initial CollectionRun for {src_name}: {e}")

        if not collector.is_configured():
            msg = f"{collector.source_name}: Not configured (API credentials missing)."
            combined_result.error_messages.append(msg)
            details[src_name] = {"status": "not_configured", "message": msg}
            if db and run_record:
                run_record.status = "failed"
                run_record.completed_at = datetime.now(timezone.utc)
                run_record.error_message = msg
                db.commit()
            continue

        try:
            logger.info(f"Running collector '{src_name}'...")
            collected_jobs = collector.collect(
                country=country,
                role=role,
                location=location,
                experience_level=experience_level,
                max_results=max_results,
            )

            if not collected_jobs:
                details[src_name] = {
                    "status": "completed",
                    "retrieved": 0,
                    "new_jobs": 0,
                    "duplicates": 0,
                    "message": "0 jobs returned from API query.",
                }
                if db and run_record:
                    run_record.status = "completed"
                    run_record.completed_at = datetime.now(timezone.utc)
                    run_record.jobs_retrieved = 0
                    db.commit()
                continue

            # Ingest jobs into database
            res = ingest_jobs(collected_jobs, db)
            combined_result.retrieved += res.retrieved
            combined_result.new_jobs += res.new_jobs
            combined_result.duplicates += res.duplicates
            combined_result.errors += res.errors
            combined_result.error_messages.extend(res.error_messages)

            run_status = "completed" if res.errors == 0 else "partial"
            details[src_name] = {
                "status": run_status,
                "retrieved": res.retrieved,
                "new_jobs": res.new_jobs,
                "duplicates": res.duplicates,
                "errors": res.errors,
            }

            if db and run_record:
                run_record.status = run_status
                run_record.completed_at = datetime.now(timezone.utc)
                run_record.jobs_retrieved = res.retrieved
                run_record.new_jobs = res.new_jobs
                run_record.duplicates = res.duplicates
                run_record.failed_jobs = res.errors
                if res.error_messages:
                    run_record.error_message = "; ".join(res.error_messages[:3])
                db.commit()

        except Exception as e:
            combined_result.errors += 1
            err_msg = f"{src_name}: Failed — {str(e)}"
            combined_result.error_messages.append(err_msg)
            details[src_name] = {"status": "failed", "error": str(e)}
            logger.error(f"Collector '{src_name}' failed: {e}")

            if db and run_record:
                run_record.status = "failed"
                run_record.completed_at = datetime.now(timezone.utc)
                run_record.error_message = str(e)
                db.commit()

    combined_result.details = details
    return combined_result
