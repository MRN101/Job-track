"""Collectors package."""

from typing import Dict, List, Optional
from app.collectors.base import BaseCollector, CollectedJob, CollectionResult
from app.collectors.adzuna import AdzunaCollector
from app.collectors.sample import SampleCollector


def get_collector(source_name: str) -> Optional[BaseCollector]:
    """Factory to retrieve collector by name."""
    name = (source_name or "").lower().strip()
    if name == "adzuna":
        return AdzunaCollector()
    elif name in ("sample", "mock", "demo"):
        return SampleCollector()
    return None


def get_available_collectors() -> List[Dict[str, str]]:
    """List available collectors and their config status."""
    adzuna = AdzunaCollector()
    sample = SampleCollector()
    return [
        {
            "name": "adzuna",
            "title": "Adzuna Job API",
            "configured": adzuna.is_configured(),
            "description": "Live search from millions of listings worldwide via Adzuna API",
        },
        {
            "name": "sample",
            "title": "Curated Tech Jobs (Sample)",
            "configured": True,
            "description": "Curated realistic tech jobs across India and global remote",
        },
    ]


__all__ = [
    "BaseCollector",
    "CollectedJob",
    "CollectionResult",
    "AdzunaCollector",
    "SampleCollector",
    "get_collector",
    "get_available_collectors",
]
