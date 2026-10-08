"""Base collector interface for job data sources."""

from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CollectedJob:
    """Standardized job data from any source."""
    source: str
    external_id: Optional[str] = None
    title: str = ""
    company_name: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    posted_at: Optional[datetime] = None
    url: Optional[str] = None


@dataclass
class CollectionResult:
    """Result of a collection operation."""
    source: str
    retrieved: int = 0
    new_jobs: int = 0
    duplicates: int = 0
    errors: int = 0
    error_messages: List[str] = field(default_factory=list)


class BaseCollector(ABC):
    """Abstract base class for job data collectors."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the name of this data source."""
        pass

    @abstractmethod
    def collect(
        self,
        country: str = "India",
        role: str = "Software Engineer",
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
        max_results: int = 100,
    ) -> List[CollectedJob]:
        """Collect jobs from the source.

        Args:
            country: Country to search in.
            role: Job role/title to search for.
            location: Specific location within the country.
            experience_level: Experience level filter.
            max_results: Maximum number of results to return.

        Returns:
            List of CollectedJob objects.
        """
        pass

    def is_configured(self) -> bool:
        """Check if this collector has the required configuration."""
        return True
