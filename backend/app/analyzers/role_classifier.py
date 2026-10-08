"""Role taxonomy and deterministic role classification engine."""

import re
from typing import Dict, List, Tuple, Optional, Any

ROLE_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "Software Engineering": {
        "roles": [
            {
                "name": "Backend Engineer",
                "patterns": [
                    r"\bbackend\b",
                    r"\bback-end\b",
                    r"\bserver-side\b",
                    r"\bjava\s+developer\b",
                    r"\bpython\s+developer\b",
                    r"\bnode(?:\.js)?\s+developer\b",
                    r"\bgolang\s+developer\b",
                    r"\b\.net\s+developer\b",
                    r"\bc#\s+developer\b",
                    r"\bruby\s+developer\b",
                    r"\bphp\s+developer\b",
                    r"\bapi\s+developer\b",
                    r"\bmicroservices\s+engineer\b",
                ],
            },
            {
                "name": "Full Stack Engineer",
                "patterns": [
                    r"\bfull\s*stack\b",
                    r"\bfullstack\b",
                    r"\bmearn\s+developer\b",
                    r"\bmean\s+developer\b",
                ],
            },
            {
                "name": "Frontend Engineer",
                "patterns": [
                    r"\bfrontend\b",
                    r"\bfront-end\b",
                    r"\bclient-side\b",
                    r"\breact(?:\.js)?\s+developer\b",
                    r"\bangular\s+developer\b",
                    r"\bvue(?:\.js)?\s+developer\b",
                    r"\bui\s+developer\b",
                    r"\bweb\s+developer\b",
                    r"\bjavascript\s+developer\b",
                    r"\btypescript\s+developer\b",
                ],
            },
            {
                "name": "Mobile Engineer",
                "patterns": [
                    r"\bmobile\s+(?:app\s+)?(?:engineer|developer)\b",
                    r"\bios\s+developer\b",
                    r"\bandroid\s+developer\b",
                    r"\bflutter\s+developer\b",
                    r"\breact\s+native\s+developer\b",
                    r"\bswift\s+developer\b",
                ],
            },
            {
                "name": "Embedded Engineer",
                "patterns": [
                    r"\bembedded\s+(?:systems\s+)?(?:engineer|developer|software)\b",
                    r"\bfirmware\s+engineer\b",
                    r"\biot\s+engineer\b",
                ],
            },
            {
                "name": "Software Engineer",
                "patterns": [
                    r"\bsde(?:\s*[-_]?\s*(?:i|ii|iii|1|2|3|senior|lead))?\b",
                    r"\bsoftware\s+development\s+engineer\b",
                    r"\bsoftware\s+engineer\b",
                    r"\bsoftware\s+developer\b",
                    r"\bapplication\s+developer\b",
                    r"\bprogrammer\b",
                    r"\bcoding\s+engineer\b",
                ],
            },
        ],
    },
    "Data & Analytics": {
        "roles": [
            {
                "name": "Data Engineer",
                "patterns": [
                    r"\bdata\s+engineer\b",
                    r"\bdata\s+pipeline\s+engineer\b",
                    r"\bbig\s+data\s+engineer\b",
                    r"\betl\s+developer\b",
                    r"\bspark\s+developer\b",
                ],
            },
            {
                "name": "Data Analyst",
                "patterns": [
                    r"\bdata\s+analyst\b",
                    r"\bbi\s+analyst\b",
                    r"\bbusiness\s+intelligence\s+analyst\b",
                    r"\banalytics\s+engineer\b",
                    r"\btableau\s+developer\b",
                    r"\bpower\s*bi\s+developer\b",
                ],
            },
            {
                "name": "Database Administrator",
                "patterns": [
                    r"\bdba\b",
                    r"\bdatabase\s+administrator\b",
                    r"\bsql\s+developer\b",
                ],
            },
        ],
    },
    "AI & Machine Learning": {
        "roles": [
            {
                "name": "Machine Learning Engineer",
                "patterns": [
                    r"\bmachine\s+learning\s+engineer\b",
                    r"\bml\s+engineer\b",
                    r"\bmleps\s+engineer\b",
                ],
            },
            {
                "name": "AI Engineer",
                "patterns": [
                    r"\bai\s+engineer\b",
                    r"\bartificial\s+intelligence\s+engineer\b",
                    r"\bgenai\s+engineer\b",
                    r"\bgenerative\s+ai\s+engineer\b",
                    r"\bllm\s+engineer\b",
                ],
            },
            {
                "name": "Data Scientist",
                "patterns": [
                    r"\bdata\s+scientist\b",
                    r"\bapplied\s+scientist\b",
                    r"\bresearch\s+scientist\b",
                ],
            },
            {
                "name": "NLP / Vision Engineer",
                "patterns": [
                    r"\bnlp\s+engineer\b",
                    r"\bcomputer\s+vision\s+engineer\b",
                    r"\bdeep\s+learning\s+engineer\b",
                ],
            },
        ],
    },
    "Cloud & DevOps": {
        "roles": [
            {
                "name": "DevOps Engineer",
                "patterns": [
                    r"\bdevops\s+engineer\b",
                    r"\bci\/cd\s+engineer\b",
                    r"\bbuild\s+(?:and\s+release\s+)?engineer\b",
                ],
            },
            {
                "name": "Site Reliability Engineer (SRE)",
                "patterns": [
                    r"\bsre\b",
                    r"\bsite\s+reliability\s+engineer\b",
                    r"\binfrastructure\s+engineer\b",
                ],
            },
            {
                "name": "Cloud Architect",
                "patterns": [
                    r"\bcloud\s+engineer\b",
                    r"\bcloud\s+architect\b",
                    r"\baws\s+architect\b",
                    r"\bazure\s+architect\b",
                ],
            },
        ],
    },
    "QA & Testing": {
        "roles": [
            {
                "name": "SDET",
                "patterns": [
                    r"\bsdet\b",
                    r"\bsoftware\s+development\s+engineer\s+in\s+test\b",
                ],
            },
            {
                "name": "QA Automation Engineer",
                "patterns": [
                    r"\bqa\s+automation\b",
                    r"\bautomation\s+test(?:er|ing)?\b",
                    r"\btest\s+automation\s+engineer\b",
                    r"\bqa\s+engineer\b",
                    r"\bquality\s+assurance\b",
                ],
            },
        ],
    },
    "Product & Security": {
        "roles": [
            {
                "name": "Security Engineer",
                "patterns": [
                    r"\bsecurity\s+engineer\b",
                    r"\bcybersecurity\b",
                    r"\binfosec\b",
                    r"\bdevsecops\b",
                ],
            },
            {
                "name": "Product Manager",
                "patterns": [
                    r"\bproduct\s+manager\b",
                    r"\btechnical\s+product\s+manager\b",
                ],
            },
            {
                "name": "UI/UX Designer",
                "patterns": [
                    r"\bui\/ux\b",
                    r"\bproduct\s+designer\b",
                    r"\bux\s+designer\b",
                ],
            },
        ],
    },
}

# Precompile patterns for fast matching
_COMPILED_ROLE_PATTERNS: List[Tuple[str, str, re.Pattern]] = []
for family, data in ROLE_TAXONOMY.items():
    for role_item in data["roles"]:
        r_name = role_item["name"]
        for p in role_item["patterns"]:
            _COMPILED_ROLE_PATTERNS.append(
                (family, r_name, re.compile(p, re.IGNORECASE))
            )


def classify_role(title: Optional[str]) -> Tuple[str, str]:
    """Deterministically classify a raw job title into (role_family, normalized_role).

    Examples:
        'Senior Backend Engineer (Python)' -> ('Software Engineering', 'Backend Engineer')
        'SDE 2' -> ('Software Engineering', 'Software Engineer')
        'Full Stack Developer' -> ('Software Engineering', 'Full Stack Engineer')
        'Lead Data Scientist' -> ('AI & Machine Learning', 'Data Scientist')
        'DevOps / SRE' -> ('Cloud & DevOps', 'DevOps Engineer')
    """
    if not title:
        return ("Software Engineering", "Software Engineer")

    cleaned = title.strip()

    # Search precompiled patterns in order of specificity
    for family, normalized_role, pattern in _COMPILED_ROLE_PATTERNS:
        if pattern.search(cleaned):
            return (family, normalized_role)

    # General fallbacks
    lower_t = cleaned.lower()
    if "engineer" in lower_t or "developer" in lower_t or "programmer" in lower_t:
        return ("Software Engineering", "Software Engineer")
    if "data" in lower_t or "analytics" in lower_t:
        return ("Data & Analytics", "Data Analyst")
    if "cloud" in lower_t:
        return ("Cloud & DevOps", "Cloud Architect")

    return ("Other", "Specialized Tech Role")


def get_all_role_families() -> List[str]:
    """Return all canonical role families."""
    return list(ROLE_TAXONOMY.keys())


def get_roles_for_family(family: str) -> List[str]:
    """Return all canonical roles within a given role family."""
    data = ROLE_TAXONOMY.get(family)
    if not data:
        return []
    return [r["name"] for r in data["roles"]]
