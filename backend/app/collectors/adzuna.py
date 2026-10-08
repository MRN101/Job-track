"""Adzuna Job Data Collector."""

import logging
from typing import List, Optional
from datetime import datetime
import httpx
from dateutil import parser as date_parser

from app.collectors.base import BaseCollector, CollectedJob
from app.config import get_settings

logger = logging.getLogger(__name__)

# Map common country names to Adzuna country codes
COUNTRY_CODES = {
    "india": "in",
    "united states": "us",
    "usa": "us",
    "united kingdom": "gb",
    "uk": "gb",
    "canada": "ca",
    "australia": "au",
    "germany": "de",
    "france": "fr",
    "singapore": "sg",
}


class AdzunaCollector(BaseCollector):
    """Collector for Adzuna job search API."""

    def __init__(self, app_id: Optional[str] = None, api_key: Optional[str] = None):
        settings = get_settings()
        self.app_id = app_id or settings.adzuna_app_id
        self.api_key = api_key or settings.adzuna_api_key
        self.base_url = "https://api.adzuna.com/v1/api/jobs"

    @property
    def source_name(self) -> str:
        return "adzuna"

    def is_configured(self) -> bool:
        return bool(self.app_id and self.api_key)

    def _get_country_code(self, country: str) -> str:
        c = (country or "india").strip().lower()
        return COUNTRY_CODES.get(c, "in")

    def collect(
        self,
        country: str = "India",
        role: str = "Software Engineer",
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
        max_results: int = 50,
    ) -> List[CollectedJob]:
        """Fetch jobs from Adzuna API."""
        if not self.is_configured():
            logger.warning("Adzuna API credentials not configured.")
            return []

        country_code = self._get_country_code(country)
        jobs: List[CollectedJob] = []
        page = 1
        results_per_page = min(max_results, 50)

        # Adzuna endpoint format: /v1/api/jobs/{country}/search/{page}
        url = f"{self.base_url}/{country_code}/search/{page}"

        params = {
            "app_id": self.app_id,
            "app_key": self.api_key,
            "results_per_page": results_per_page,
            "what": role,
            "content-type": "application/json",
        }
        if location and location.lower() != "all locations":
            params["where"] = location

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, params=params)
                if response.status_code != 200:
                    logger.error(f"Adzuna API failed: {response.status_code} - {response.text}")
                    return []

                data = response.json()
                items = data.get("results", [])

                for item in items:
                    posted_at = None
                    created_str = item.get("created")
                    if created_str:
                        try:
                            posted_at = date_parser.parse(created_str)
                        except Exception:
                            posted_at = datetime.utcnow()

                    company_info = item.get("company", {})
                    company_name = company_info.get("display_name") if isinstance(company_info, dict) else str(company_info)

                    location_info = item.get("location", {})
                    loc_name = location_info.get("display_name") if isinstance(location_info, dict) else str(location_info)

                    job = CollectedJob(
                        source=self.source_name,
                        external_id=str(item.get("id", "")),
                        title=item.get("title", ""),
                        company_name=company_name,
                        location=loc_name,
                        country=country,
                        description=item.get("description", ""),
                        salary_min=item.get("salary_min"),
                        salary_max=item.get("salary_max"),
                        salary_currency="INR" if country_code == "in" else ("GBP" if country_code == "gb" else "USD"),
                        employment_type=item.get("contract_time"),
                        experience_level=experience_level,
                        posted_at=posted_at,
                        url=item.get("redirect_url"),
                    )
                    jobs.append(job)

        except Exception as e:
            logger.error(f"Error fetching jobs from Adzuna: {e}")

        return jobs
