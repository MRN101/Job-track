"""Remotive API Collector for live developer and tech jobs."""

import re
import html
import logging
from typing import List, Optional
from datetime import datetime, timezone
import httpx

from app.collectors.base import BaseCollector, CollectedJob
from app.services.salary_service import parse_and_normalize_salary

logger = logging.getLogger(__name__)


def clean_html(text: Optional[str]) -> str:
    """Strip HTML tags and unescape entities."""
    if not text:
        return ""
    # Strip HTML tags
    cleaned = re.sub(r"<[^>]+>", " ", text)
    # Unescape HTML entities
    cleaned = html.unescape(cleaned)
    # Collapse whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


class RemotiveCollector(BaseCollector):
    """Collector for Remotive public jobs feed (real, live data source)."""

    API_URL = "https://remotive.com/api/remote-jobs"

    @property
    def source_name(self) -> str:
        return "remotive"

    def is_configured(self) -> bool:
        """Remotive public API requires no key and is always available."""
        return True

    def collect(
        self,
        country: str = "Worldwide",
        role: str = "Software Engineer",
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
        max_results: int = 50,
    ) -> List[CollectedJob]:
        """Collect live developer jobs from Remotive."""
        params = {"category": "software-dev"}
        if role and role.strip() and role.lower() not in ("all", "all roles"):
            params["search"] = role.strip()
        if max_results:
            params["limit"] = min(max_results, 100)

        logger.info(f"Querying Remotive API with search='{role}'...")
        jobs: List[CollectedJob] = []

        try:
            with httpx.Client(timeout=20.0, follow_redirects=True) as client:
                resp = client.get(self.API_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
                items = data.get("jobs", [])

                for item in items[:max_results]:
                    ext_id = str(item.get("id"))
                    title = item.get("title", "Untitled Job")
                    company = item.get("company_name", "")
                    job_loc = item.get("candidate_required_location") or "Remote"
                    raw_desc = item.get("description", "")
                    desc_text = clean_html(raw_desc)
                    raw_salary = item.get("salary")
                    job_type = item.get("job_type")

                    # Parse and normalize salary
                    sal_min, sal_max, sal_curr, sal_period, sal_norm = parse_and_normalize_salary(
                        raw_text=raw_salary
                    )

                    # Parse publication date
                    posted_at = None
                    pub_str = item.get("publication_date")
                    if pub_str:
                        try:
                            posted_at = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
                        except Exception:
                            posted_at = datetime.now(timezone.utc)

                    jobs.append(
                        CollectedJob(
                            source=self.source_name,
                            data_type="real",
                            external_id=ext_id,
                            title=title,
                            company_name=company,
                            location=job_loc,
                            country=country if country and country.lower() not in ("worldwide", "all") else "Remote",
                            description=desc_text,
                            salary_min=sal_min,
                            salary_max=sal_max,
                            salary_currency=sal_curr,
                            salary_period=sal_period,
                            salary_normalized=sal_norm,
                            employment_type=job_type,
                            experience_level=experience_level,
                            posted_at=posted_at,
                            url=item.get("url"),
                        )
                    )

            logger.info(f"Collected {len(jobs)} live jobs from Remotive.")
        except Exception as e:
            logger.error(f"Error collecting from Remotive: {e}")
            raise

        return jobs
