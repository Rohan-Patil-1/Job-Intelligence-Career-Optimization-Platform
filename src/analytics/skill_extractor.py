"""
Deterministic skill extraction from job descriptions.
"""

import re

from src.analytics.skill_vocabulary import SKILL_ALIASES


def normalize_text(text: str) -> str:
    """Normalize text for deterministic matching."""
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[\u2010-\u2015]", "-", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _contains_skill(text: str, alias: str) -> bool:
    """
    Check whether an alias occurs as a meaningful token/phrase.

    Uses word boundaries where possible to avoid substring matches such as:
    'r' matching unrelated words.
    """
    escaped = re.escape(alias)

    # Special handling for aliases containing non-word characters
    if re.search(r"\w", alias):
        pattern = rf"(?<!\w){escaped}(?!\w)"
    else:
        pattern = escaped

    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def extract_skills(text: str) -> list[str]:
    """
    Extract canonical skills from a job description.

    Returns:
        Sorted list of unique canonical skill names.
    """
    normalized = normalize_text(text)

    if not normalized:
        return []

    found_skills = set()

    for alias, canonical_skill in SKILL_ALIASES.items():
        if _contains_skill(normalized, alias):
            found_skills.add(canonical_skill)

    return sorted(found_skills)


def extract_skills_with_matches(text: str) -> dict[str, list[str]]:
    """
    Extract canonical skills and the aliases that triggered each match.

    Useful for debugging and later improving the vocabulary.
    """
    normalized = normalize_text(text)

    if not normalized:
        return {}

    matches: dict[str, list[str]] = {}

    for alias, canonical_skill in SKILL_ALIASES.items():
        if _contains_skill(normalized, alias):
            matches.setdefault(canonical_skill, []).append(alias)

    return {
        skill: sorted(aliases)
        for skill, aliases in sorted(matches.items())
    }