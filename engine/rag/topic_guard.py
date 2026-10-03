import re
from typing import Tuple

# Curated domain vocabulary — if the query contains NONE of these, reject it
_DOMAIN_TERMS = {
    "labour", "labor", "job", "employment", "skill", "demand", "supply",
    "gap", "shortage", "forecast", "policy", "training", "iti", "pmkvy",
    "naps", "nats", "dvet", "udise", "aishe", "plfs", "nco", "esco",
    "nqr", "onet", "vacancy", "wage", "salary", "hiring", "recruit",
    "workforce", "occupation", "sector", "industry", "seeker", "employer",
    "portal", "dashboard", "copilot", "where", "find", "navigate",
    "apply", "resume", "upskill", "apprentice", "certification",
    "market", "intelligence", "engine", "lmi", "state", "india",
    "recommendation", "intervention", "budget", "capacity",
    "critical", "moderate", "balanced", "oversupply", "risk",
    "shap", "xgboost", "arima", "trend", "prediction",
    "software", "developer", "engineer", "technician", "nurse",
    "teacher", "data", "analyst", "score", "career", "role",
    "work", "field", "opportunity", "qualification", "course"
}

_BLOCKED_PATTERNS = re.compile(
    r"\b(write.*(code|program|script)|solve.*(math|equation)|recipe|joke|poem|"
    r"lyrics|translate|weather|cricket|movie|game|stock.*(price|market)|"
    r"crypto|bitcoin)\b",
    re.IGNORECASE,
)

def is_on_topic(query: str) -> Tuple[bool, str]:
    """Return (allowed, reason)."""
    if not query or not query.strip():
        return False, "empty_query"
    if _BLOCKED_PATTERNS.search(query):
        return False, "off_topic_blocked"
    tokens = set(re.findall(r"[a-z]+", query.lower()))
    if tokens & _DOMAIN_TERMS:
        return True, "domain_match"
    return False, "no_domain_terms"
