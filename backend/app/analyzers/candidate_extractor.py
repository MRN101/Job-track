"""Lightweight candidate skill extractor for discovering emerging/unseen technologies."""

import re
from typing import List, Dict, Set, Optional, Any

# Non-technical English words, common abbreviations, degrees, and generic words to exclude
EXCLUDE_TERMS: Set[str] = {
    # Generic English & Grammar
    "AND", "THE", "FOR", "WITH", "FROM", "THIS", "THAT", "ABOUT", "AFTER", "BEFORE",
    "HAVE", "HAS", "HAD", "WILL", "WOULD", "COULD", "SHOULD", "MUST", "BEING", "BEEN",
    "WHICH", "WHERE", "WHEN", "WHAT", "WHO", "HOW", "WHY", "EACH", "EVERY", "OTHER",
    "SOME", "SUCH", "ONLY", "OWN", "SAME", "SO", "THAN", "TOO", "VERY", "JUST",
    # Job posting boilerplate
    "JOB", "ROLE", "WORK", "TEAM", "CLIENT", "PROJECT", "BUSINESS", "PRODUCT", "SERVICE",
    "COMPANY", "CANDIDATE", "REQUIRED", "REQUIREMENT", "REQUIREMENTS", "SKILLS", "SKILL",
    "PLUS", "MINIMUM", "MAXIMUM", "APPLY", "APPLICATION", "EXPERIENCE", "YEAR", "YEARS",
    "LOCATION", "SALARY", "OFFICE", "HYBRID", "REMOTE", "FULLTIME", "PARTTIME", "CONTRACT",
    "PERMANENT", "BENEFITS", "JOIN", "OPPORTUNITY", "RESPONSIBILITIES", "QUALIFICATIONS",
    "RESPONSIBILITY", "DUTIES", "OVERVIEW", "DESCRIPTION", "PROFILE", "ABOUT", "SUMMARY",
    # Locations / Currency
    "INDIA", "USA", "UK", "UNITED", "STATES", "CANADA", "GERMANY", "INR", "USD", "EUR", "GBP", "LPA",
    # Degrees / Education
    "BTECH", "BE", "MCA", "BSC", "MSC", "MBA", "PHD", "BACHELORS", "MASTERS", "DEGREE",
    # Generic Tech / Process Words (too vague to be a distinct skill)
    "AGILE", "SCRUM", "SDLC", "OOP", "OOD", "MVC", "REST", "API", "APIS", "HTTP", "HTTPS",
    "URL", "JSON", "XML", "HTML", "CSS", "SQL", "CODE", "CODING", "PROGRAMMING", "SOFTWARE",
    "HARDWARE", "TECH", "TECHNOLOGY", "STACK", "DEV", "DEVELOPMENT", "ENGINEERING",
    "SENIOR", "JUNIOR", "LEAD", "PRINCIPAL", "STAFF", "MANAGER", "DIRECTOR", "HEAD",
}

# Regex for uppercase acronyms (e.g. MCP, WASM, HTMX, RAG, GRPC, CUDA, VLLM)
ACRONYM_REGEX = re.compile(r"\b[A-Z][A-Z0-9]{1,6}\b")

# Regex for CamelCase or tech-formatted words (e.g. LangChain, ChromaDB, Fastify, LlamaIndex, PyTorch, tRPC)
TECH_CAMELCASE_REGEX = re.compile(r"\b(?:[a-z]+[A-Z][a-zA-Z0-9]*|[A-Z][a-z]+[A-Z][a-zA-Z0-9]*)\b")

# Regex for tech terms with dots/dashes (e.g. Bun.js, Next.js, Vue.js, Node.js - usually canonical, but new ones like Deno.js)
TECH_PUNCT_REGEX = re.compile(r"\b[a-zA-Z0-9]+(?:\.[a-zA-Z]{1,4}|-[a-zA-Z]{2,})\b")


def extract_candidate_skills(
    text: str,
    known_skill_names: Set[str],
) -> List[Dict[str, Any]]:
    """Extract candidate technical skills from text that are not present in known_skill_names.
    
    Returns list of dicts:
        [{"name": "MCP", "normalized_name": "mcp", "confidence": 0.85}, ...]
    """
    if not text:
        return []

    candidates: Dict[str, Dict[str, Any]] = {}
    lower_known = {k.lower().strip() for k in known_skill_names}

    # Helper to validate and add
    def consider_candidate(token: str, conf: float):
        raw = token.strip(" ,.-/:;()[]{}*\"'")
        if not raw or len(raw) < 2 or len(raw) > 30:
            return
        
        # Check against exclusions
        upper_val = raw.upper()
        if upper_val in EXCLUDE_TERMS:
            return
            
        lower_val = raw.lower()
        if lower_val in lower_known:
            return

        # Skip pure numbers or single characters
        if raw.isdigit() or len(raw) <= 1:
            return

        # Skip common punctuation artifact
        if not re.search(r"[a-zA-Z]", raw):
            return

        # Record candidate with normalized key
        if lower_val not in candidates:
            candidates[lower_val] = {
                "name": raw,
                "normalized_name": lower_val,
                "confidence": conf,
            }

    # 1. Acronyms (e.g. MCP, RAG, WASM)
    for match in ACRONYM_REGEX.findall(text):
        consider_candidate(match, 0.85)

    # 2. CamelCase Tech terms (e.g. LangChain, LlamaIndex, ChromaDB, Pinecone)
    for match in TECH_CAMELCASE_REGEX.findall(text):
        consider_candidate(match, 0.80)

    # 3. Specific tech punctuation
    for match in TECH_PUNCT_REGEX.findall(text):
        if not match.lower().endswith((".com", ".org", ".net", ".io", ".ai", ".in")):
            consider_candidate(match, 0.75)

    return list(candidates.values())
