"""Location normalizer for job locations."""

import re
from typing import Dict, Optional, Tuple, Any

# Map of lowercased tokens / phrases to (normalized_city, state, country)
CITY_MAP: Dict[str, Tuple[str, Optional[str], str]] = {
    # India
    "bangalore": ("Bengaluru", "Karnataka", "India"),
    "bengaluru": ("Bengaluru", "Karnataka", "India"),
    "bombay": ("Mumbai", "Maharashtra", "India"),
    "mumbai": ("Mumbai", "Maharashtra", "India"),
    "navi mumbai": ("Mumbai", "Maharashtra", "India"),
    "thane": ("Mumbai", "Maharashtra", "India"),
    "calcutta": ("Kolkata", "West Bengal", "India"),
    "kolkata": ("Kolkata", "West Bengal", "India"),
    "madras": ("Chennai", "Tamil Nadu", "India"),
    "chennai": ("Chennai", "Tamil Nadu", "India"),
    "hyderabad": ("Hyderabad", "Telangana", "India"),
    "secunderabad": ("Hyderabad", "Telangana", "India"),
    "cyberabad": ("Hyderabad", "Telangana", "India"),
    "pune": ("Pune", "Maharashtra", "India"),
    "gurgaon": ("Gurugram", "Haryana", "India"),
    "gurugram": ("Gurugram", "Haryana", "India"),
    "noida": ("Noida", "Uttar Pradesh", "India"),
    "greater noida": ("Noida", "Uttar Pradesh", "India"),
    "delhi": ("New Delhi", "Delhi", "India"),
    "new delhi": ("New Delhi", "Delhi", "India"),
    "delhi ncr": ("New Delhi", "Delhi", "India"),
    "ahmedabad": ("Ahmedabad", "Gujarat", "India"),
    "jaipur": ("Jaipur", "Rajasthan", "India"),
    "kochi": ("Kochi", "Kerala", "India"),
    "cochin": ("Kochi", "Kerala", "India"),
    "thiruvananthapuram": ("Thiruvananthapuram", "Kerala", "India"),
    "trivandrum": ("Thiruvananthapuram", "Kerala", "India"),
    "chandigarh": ("Chandigarh", "Punjab", "India"),
    "mohali": ("Chandigarh", "Punjab", "India"),
    "indore": ("Indore", "Madhya Pradesh", "India"),
    "bhopal": ("Bhopal", "Madhya Pradesh", "India"),
    "coimbatore": ("Coimbatore", "Tamil Nadu", "India"),
    
    # Global Tech Hubs
    "san francisco": ("San Francisco", "California", "United States"),
    "bay area": ("San Francisco", "California", "United States"),
    "new york": ("New York", "New York", "United States"),
    "new york city": ("New York", "New York", "United States"),
    "nyc": ("New York", "New York", "United States"),
    "seattle": ("Seattle", "Washington", "United States"),
    "austin": ("Austin", "Texas", "United States"),
    "boston": ("Boston", "Massachusetts", "United States"),
    "chicago": ("Chicago", "Illinois", "United States"),
    "london": ("London", "England", "United Kingdom"),
    "berlin": ("Berlin", "Berlin", "Germany"),
    "amsterdam": ("Amsterdam", "North Holland", "Netherlands"),
    "singapore": ("Singapore", "Singapore", "Singapore"),
    "toronto": ("Toronto", "Ontario", "Canada"),
    "vancouver": ("Vancouver", "British Columbia", "Canada"),
    "sydney": ("Sydney", "New South Wales", "Australia"),
    "dubai": ("Dubai", "Dubai", "United Arab Emirates"),
}

REMOTE_PATTERNS = [
    re.compile(r"\bremote\b", re.IGNORECASE),
    re.compile(r"\bwork\s+from\s+home\b", re.IGNORECASE),
    re.compile(r"\bwfh\b", re.IGNORECASE),
    re.compile(r"\btelecommute\b", re.IGNORECASE),
    re.compile(r"\banywhere\b", re.IGNORECASE),
    re.compile(r"\bvirtual\b", re.IGNORECASE),
]


def normalize_location(raw_location: Optional[str], default_country: Optional[str] = "India") -> Dict[str, Any]:
    """Parse and normalize a raw location string into structured components.
    
    Returns:
        {
            "original_location": str,
            "normalized_city": Optional[str],
            "state": Optional[str],
            "country": Optional[str],
            "is_remote": bool
        }
    """
    if not raw_location:
        return {
            "original_location": "",
            "normalized_city": None,
            "state": None,
            "country": default_country,
            "is_remote": False,
        }

    raw = raw_location.strip()
    is_remote = any(p.search(raw) for p in REMOTE_PATTERNS)

    # Clean tokens
    cleaned = re.sub(r"[^\w\s,/-]", "", raw.lower())
    parts = [p.strip() for p in re.split(r"[,/|-]", cleaned) if p.strip()]

    matched_city = None
    matched_state = None
    matched_country = None

    # Check exact matching on parts first (multi-word matches like 'navi mumbai')
    for part in parts:
        if part in CITY_MAP:
            matched_city, matched_state, matched_country = CITY_MAP[part]
            break

    # If not found by parts, search substring / whole word tokens in cleaned text
    if not matched_city:
        for key, (city, state, country) in sorted(CITY_MAP.items(), key=lambda x: -len(x[0])):
            pattern = rf"\b{re.escape(key)}\b"
            if re.search(pattern, cleaned):
                matched_city = city
                matched_state = state
                matched_country = country
                break

    # Country fallback
    if not matched_country:
        if "india" in cleaned:
            matched_country = "India"
        elif "usa" in cleaned or "united states" in cleaned or "us" in parts:
            matched_country = "United States"
        elif "uk" in parts or "united kingdom" in cleaned:
            matched_country = "United Kingdom"
        elif "germany" in cleaned:
            matched_country = "Germany"
        elif "canada" in cleaned:
            matched_country = "Canada"
        elif "australia" in cleaned:
            matched_country = "Australia"
        elif default_country:
            matched_country = default_country

    # If purely remote without specific city
    if not matched_city and is_remote:
        matched_city = "Remote"

    return {
        "original_location": raw,
        "normalized_city": matched_city,
        "state": matched_state,
        "country": matched_country or default_country,
        "is_remote": is_remote,
    }
