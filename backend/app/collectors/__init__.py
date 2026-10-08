"""Collectors package with full registry of all supported sources."""

from typing import Dict, List, Optional, Any
from app.collectors.base import BaseCollector, CollectedJob, CollectionResult
from app.collectors.adzuna import AdzunaCollector
from app.collectors.remotive import RemotiveCollector
from app.collectors.sample import SampleCollector


def get_collector(source_name: str) -> Optional[BaseCollector]:
    """Factory to retrieve collector by name."""
    name = (source_name or "").lower().strip()
    if name == "adzuna":
        return AdzunaCollector()
    elif name == "remotive":
        return RemotiveCollector()
    elif name in ("sample", "demo", "mock"):
        return SampleCollector()
    return None


def get_available_collectors() -> List[Dict[str, Any]]:
    """List available collectors and their live status."""
    adzuna = AdzunaCollector()
    remotive = RemotiveCollector()
    sample = SampleCollector()

    return [
        {
            "name": "remotive",
            "title": "Remotive Remote Developer Jobs",
            "type": "real",
            "configured": remotive.is_configured(),
            "description": "Live real developer jobs from worldwide remote companies (No API key needed).",
        },
        {
            "name": "adzuna",
            "title": "Adzuna Job API",
            "type": "real",
            "configured": adzuna.is_configured(),
            "description": "Global job search API across multiple countries (Requires App ID & API Key).",
        },
        {
            "name": "sample",
            "title": "Curated Tech Jobs (Demo Dataset)",
            "type": "demo",
            "configured": True,
            "description": "Curated developer listings for development, offline testing, and demonstration.",
        },
    ]


__all__ = [
    "BaseCollector",
    "CollectedJob",
    "CollectionResult",
    "AdzunaCollector",
    "RemotiveCollector",
    "SampleCollector",
    "get_collector",
    "get_available_collectors",
]
