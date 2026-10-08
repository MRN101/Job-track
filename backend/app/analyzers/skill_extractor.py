"""Skill extraction and normalization engine."""

import re
import logging
from typing import List, Dict, Tuple, Optional
from app.analyzers.taxonomy import TAXONOMY

logger = logging.getLogger(__name__)

# Build global normalization dictionary
_NORMALIZATION_MAP: Dict[str, str] = {}
for _item in TAXONOMY:
    _canonical = _item["canonical_name"]
    _NORMALIZATION_MAP[_canonical.lower()] = _canonical
    _NORMALIZATION_MAP[_item["name"].lower()] = _canonical
    for _alias in _item.get("aliases", []):
        _NORMALIZATION_MAP[_alias.strip().lower()] = _canonical

# Special common aliases and variations
_SPECIAL_NORMALIZATIONS = {
    "react.js": "React",
    "reactjs": "React",
    "react js": "React",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "postgre": "PostgreSQL",
    "psql": "PostgreSQL",
    "aws": "AWS",
    "amazon web services": "AWS",
    "golang": "Go",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    ".net": ".NET Core",
    ".net core": ".NET Core",
    "dotnet": ".NET Core",
    "k8s": "Kubernetes",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
}
for _k, _v in _SPECIAL_NORMALIZATIONS.items():
    _NORMALIZATION_MAP[_k.lower()] = _v


def normalize_skill_name(name: str) -> str:
    """Centralized skill normalization.
    Maps aliases and variations to canonical skill names.
    Examples:
        'React.js' -> 'React'
        'Postgres' -> 'PostgreSQL'
        'Amazon Web Services' -> 'AWS'
    """
    if not name:
        return ""
    cleaned = name.strip()
    lookup = cleaned.lower()
    if lookup in _NORMALIZATION_MAP:
        return _NORMALIZATION_MAP[lookup]

    # Normalize punctuation and check again
    simplified = re.sub(r"[\._\-\s]+", "", lookup)
    for k, v in _NORMALIZATION_MAP.items():
        if re.sub(r"[\._\-\s]+", "", k) == simplified:
            return v

    return cleaned


class SkillExtractor:
    """Extracts canonical and candidate skills from job texts with strict false-positive prevention."""

    def __init__(self):
        self.taxonomy = TAXONOMY
        self._compiled_patterns: List[Tuple[Dict, List[re.Pattern]]] = []
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for taxonomy items with strict boundaries."""
        for item in self.taxonomy:
            patterns = []

            # Check if item defines strict contextual patterns (e.g. for C, Go)
            strict_patterns = item.get("strict_patterns")
            if strict_patterns:
                for sp in strict_patterns:
                    try:
                        compiled = re.compile(sp, re.IGNORECASE)
                        patterns.append(compiled)
                    except re.error as e:
                        logger.warning(f"Failed to compile strict pattern {sp}: {e}")
                # For items with strict patterns, only compile unambiguous aliases longer than 3 chars
                aliases = item.get("aliases", [])
                unique_aliases = set(a.strip().lower() for a in aliases if len(a.strip()) > 3)
            else:
                # For regular aliases, compile with boundary checks
                aliases = item.get("aliases", []) + [item["name"], item["canonical_name"]]
                unique_aliases = set(a.strip().lower() for a in aliases if len(a.strip()) > 1)

            for alias in unique_aliases:
                escaped = re.escape(alias)
                # Word boundaries that respect +, #, etc.
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
        Returns list of dicts with canonical_name, category, confidence, and in_title.
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
        """Optionally use LLM to detect candidate skills not in taxonomy."""
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
            logger.error(f"LLM candidate extraction error: {e}")

        return []


# Global singleton instance
_extractor: Optional[SkillExtractor] = None


def get_skill_extractor() -> SkillExtractor:
    """Get the skill extractor singleton."""
    global _extractor
    if _extractor is None:
        _extractor = SkillExtractor()
    return _extractor
