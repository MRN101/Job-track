"""Remotive API Collector for developer and tech jobs."""

import re
import html
import logging
from typing import List, Optional
from datetime import datetime, timezone
import httpx

from app.collectors.base import BaseCollector, CollectedJob

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


def parse_salary(salary_str: Optional[str]):
    """Extract salary min, max, currency from salary string if possible."""
    if not salary_str:
        return None, None, None
    s = salary_str.strip()
    currency = "USD"
    if "€" in s or "EUR" in s:
        currency = "EUR"
    elif "£" in s or "GBP" in s:
        currency = "GBP"
    elif "₹" in s or "INR" in s:
        currency = "INR"

    # Find numbers like 120,000 or 120k
    numbers = []
    matches = re.findall(r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(k|kilo)?", s, re.IGNORECASE)
    for num_str, multiplier in matches:
        num = float(num_str.replace(",", ""))
        if multiplier.lower() in ("k", "kilo"):
            num *= 1000
        numbers.append(num)

    if len(numbers) >= 2:
        return min(numbers), max(numbers), currency
    elif len(numbers) == 1:
        return numbers[0], numbers[0], currency
    return None, None, None


class RemotiveCollector(BaseCollector):
    """Collector for Remotive public jobs feed."""

    API_URL = "https://remotive.com/api/remote-jobs"

    @property
    def source_name(self) -> str:
        return "remotive"

    def is_configured(self) -> bool:
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
        if role and role.strip():
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
                    # Extract fields
                    ext_id = str(item.get("id"))
                    title = item.get("title", "Untitled Job")
                    company = item.get("company_name", "")
                    job_loc = item.get("candidate_required_location") or "Remote"
                    raw_desc = item.get("description", "")
                    desc_text = clean_html(raw_desc)
                    sal_min, sal_max, sal_curr = parse_salary(item.get("salary"))
                    job_type = item.get("job_type")

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
                            external_id=ext_id,
                            title=title,
                            company_name=company,
                            location=job_loc,
                            country=country if country and country != "Worldwide" else "Remote",
                            description=desc_text,
                            salary_min=sal_min,
                            salary_max=sal_max,
                            salary_currency=sal_curr,
                            employment_type=job_type,
                            experience_level=experience_level,
                            posted_at=posted_at,
                            url=item.get("url"),
                        )
                    )

            logger.info(f"Collected {len(jobs)} jobs from Remotive.")
        except Exception as e:
            logger.error(f"Error collecting from Remotive: {e}")

        return jobs
