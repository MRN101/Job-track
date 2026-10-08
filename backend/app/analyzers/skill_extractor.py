"""Skill extraction engine using dictionary-based regex and optional LLM."""

import re
import logging
from typing import List, Dict, Set, Tuple, Optional
from app.analyzers.taxonomy import TAXONOMY

logger = logging.getLogger(__name__)


class SkillExtractor:
    """Extracts canonical and candidate skills from job texts."""

    def __init__(self):
        self.taxonomy = TAXONOMY
        self._compiled_patterns: List[Tuple[Dict, List[re.Pattern]]] = []
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for taxonomy items handling punctuation properly."""
        for item in self.taxonomy:
            patterns = []
            aliases = item.get("aliases", []) + [item["name"], item["canonical_name"]]
            # Deduplicate lowercase aliases
            unique_aliases = set(a.strip().lower() for a in aliases if a.strip())

            for alias in unique_aliases:
                # Handle special characters (C++, C#, .NET, CI/CD, etc.)
                escaped = re.escape(alias)
                # If alias starts/ends with alphanumeric, enforce word boundary
                start_boundary = r"(?<![a-zA-Z0-9_])"
                end_boundary = r"(?![a-zA-Z0-9_])"
                pattern_str = f"{start_boundary}{escaped}{end_boundary}"
                try:
                    compiled = re.compile(pattern_str, re.IGNORECASE)
                    patterns.append(compiled)
                except re.error as e:
                    logger.warning(f"Failed to compile pattern for {alias}: {e}")

            self._compiled_patterns.append((item, patterns))

    def extract_skills(
        self,
        title: str = "",
        description: str = "",
    ) -> List[Dict]:
        """Extract skills from title and description.

        Returns list of dicts:
        [
            {
                "canonical_name": "Python",
                "category": "Programming Languages",
                "confidence": 1.0,
                "in_title": True
            },
            ...
        ]
        """
        combined_text = f"{title}\n{description}"
        detected: Dict[str, Dict] = {}

        for item, patterns in self._compiled_patterns:
            canonical_name = item["canonical_name"]
            category = item.get("category", "General")

            # Check if present in title
            in_title = any(p.search(title) for p in patterns)
            # Check in full text
            in_text = in_title or any(p.search(combined_text) for p in patterns)

            if in_text:
                confidence = 1.0 if in_title else 0.85
                detected[canonical_name] = {
                    "canonical_name": canonical_name,
                    "name": item["name"],
                    "category": category,
                    "confidence": confidence,
                    "in_title": in_title,
                }

        return list(detected.values())

    async def extract_candidate_skills_llm(
        self,
        description: str,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
    ) -> List[str]:
        """Optionally use OpenAI to detect emerging/candidate skills not in taxonomy."""
        if not api_key or not description:
            return []

        try:
            import httpx
            prompt = (
                "Extract technical skills, tools, and methodologies mentioned in this job listing. "
                "Return only a comma-separated list of short skill names:\n\n"
                f"{description[:2000]}"
            )
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a tech recruiter skill extractor."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
                "max_tokens": 150,
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    skills = [s.strip() for s in content.split(",") if s.strip()]
                    return skills
        except Exception as e:
            logger.error(f"LLM extraction error: {e}")

        return []


# Global singleton instance
_extractor: Optional[SkillExtractor] = None


def get_skill_extractor() -> SkillExtractor:
    """Get the skill extractor singleton."""
    global _extractor
    if _extractor is None:
        _extractor = SkillExtractor()
    return _extractor
