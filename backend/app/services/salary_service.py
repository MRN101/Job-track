"""Salary normalization, statistical calculation, and currency conversion service."""

import re
import logging
from typing import List, Dict, Optional, Tuple, Any
import numpy as np

logger = logging.getLogger(__name__)

# Currency conversion rates relative to INR as base
# (1 unit of currency = X INR)
CURRENCY_TO_INR = {
    "INR": 1.0,
    "USD": 86.5,
    "EUR": 93.5,
    "GBP": 110.0,
}


def convert_currency(amount: float, from_curr: str, to_curr: str) -> Optional[float]:
    """Convert amount between supported currencies (INR, USD, GBP, EUR)."""
    if amount is None:
        return None
    f = (from_curr or "INR").upper().strip()
    t = (to_curr or "INR").upper().strip()
    if f == t:
        return float(amount)

    rate_from = CURRENCY_TO_INR.get(f)
    rate_to = CURRENCY_TO_INR.get(t)

    if not rate_from or not rate_to:
        logger.warning(f"Unsupported currency conversion: {f} to {t}")
        return None

    # amount in INR = amount * rate_from
    amount_in_inr = amount * rate_from
    converted = amount_in_inr / rate_to
    return round(converted, 2)


def parse_and_normalize_salary(
    raw_min: Optional[float] = None,
    raw_max: Optional[float] = None,
    raw_currency: Optional[str] = None,
    raw_period: Optional[str] = None,
    raw_text: Optional[str] = None,
) -> Tuple[Optional[float], Optional[float], Optional[str], Optional[str], Optional[float]]:
    """Parse and normalize salary into annual equivalent.

    Returns:
        (salary_min, salary_max, salary_currency, salary_period, salary_normalized_annual)
        If salary cannot be confidently normalized, salary_normalized is None.
    """
    currency = (raw_currency or "INR").upper().strip()
    period = (raw_period or "").lower().strip() if raw_period else None
    s_min = float(raw_min) if raw_min is not None else None
    s_max = float(raw_max) if raw_max is not None else None

    # Check raw text for clues if period or values are missing
    if raw_text:
        text = raw_text.strip()
        # Check currency symbols in text
        if "₹" in text or "inr" in text.lower() or "rs" in text.lower() or "lpa" in text.lower():
            currency = "INR"
        elif "$" in text or "usd" in text.lower():
            currency = "USD"
        elif "€" in text or "eur" in text.lower():
            currency = "EUR"
        elif "£" in text or "gbp" in text.lower():
            currency = "GBP"

        # Check LPA pattern: e.g. "6 - 12 LPA" or "8 LPA" or "₹6-8 Lakhs"
        lpa_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)?\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakh|lacs)", text, re.I)
        if lpa_match:
            val1 = float(lpa_match.group(1)) * 100_000
            val2 = float(lpa_match.group(2)) * 100_000 if lpa_match.group(2) else val1
            s_min = min(val1, val2)
            s_max = max(val1, val2)
            period = "year"
            currency = "INR"
        elif re.search(r"(\d+(?:\.\d+)?)\s*(?:lpa|lakh|lacs)", text, re.I):
            single_lpa = re.search(r"(\d+(?:\.\d+)?)\s*(?:lpa|lakh|lacs)", text, re.I)
            val = float(single_lpa.group(1)) * 100_000
            s_min = val
            s_max = val
            period = "year"
            currency = "INR"
        elif not period:
            if re.search(r"\b(?:per\s+hour|\/hr|\/hour|hourly)\b", text, re.I):
                period = "hour"
            elif re.search(r"\b(?:per\s+month|\/mo|\/month|monthly)\b", text, re.I):
                period = "month"
            elif re.search(r"\b(?:per\s+year|\/yr|\/year|annually|annual|p\.a\.)\b", text, re.I):
                period = "year"

    # Default period estimation if values look obviously annual or hourly
    if not period:
        high_val = s_max or s_min
        if high_val:
            if currency in ("USD", "EUR", "GBP"):
                if high_val <= 300:
                    period = "hour"
                elif high_val >= 15000:
                    period = "year"
                elif 1000 <= high_val < 15000:
                    period = "month"
            elif currency == "INR":
                if high_val >= 100000:
                    period = "year"
                elif 5000 <= high_val < 100000:
                    period = "month"

    # Normalization multipliers to annual
    # If cannot confidently determine period, do NOT guess normalized annual
    normalized_annual: Optional[float] = None
    target_val = s_max or s_min

    if target_val and period:
        if period == "year":
            normalized_annual = target_val
        elif period == "month":
            normalized_annual = target_val * 12.0
        elif period == "hour":
            normalized_annual = target_val * 2080.0  # 40 hours/week * 52 weeks
        elif period == "day":
            normalized_annual = target_val * 260.0   # 5 days/week * 52 weeks

    return s_min, s_max, currency, period, normalized_annual


def calculate_salary_statistics(
    salaries: List[float],
    currency: str = "INR",
) -> Dict[str, Any]:
    """Calculate mathematically correct statistical metrics on a list of salaries.
    Calculates: min, max, median, 25th percentile (Q1), 75th percentile (Q3).
    Handles odd and even lengths properly with standard linear interpolation.
    """
    valid_salaries = [float(s) for s in salaries if s is not None and s > 0]
    count = len(valid_salaries)

    if count == 0:
        return {
            "min": None,
            "max": None,
            "median": None,
            "p25": None,
            "p75": None,
            "currency": currency,
            "jobs_with_salary": 0,
        }

    arr = np.array(valid_salaries, dtype=float)
    s_min = round(float(np.min(arr)), 2)
    s_max = round(float(np.max(arr)), 2)
    s_median = round(float(np.median(arr)), 2)
    s_p25 = round(float(np.percentile(arr, 25)), 2)
    s_p75 = round(float(np.percentile(arr, 75)), 2)

    return {
        "min": s_min,
        "max": s_max,
        "median": s_median,
        "p25": s_p25,
        "p75": s_p75,
        "currency": currency,
        "jobs_with_salary": count,
    }
