import re

from src.analytics.domain_vocabulary import DOMAIN_KEYWORDS


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def extract_domains(text: str) -> dict[str, list[str]]:
    normalized = normalize_text(text)

    if not normalized:
        return {}

    results = {}

    for domain, keywords in DOMAIN_KEYWORDS.items():
        matches = []

        for keyword in keywords:
            normalized_keyword = normalize_text(keyword)

            pattern = (
                rf"(?<!\w)"
                rf"{re.escape(normalized_keyword)}"
                rf"(?!\w)"
            )

            if re.search(pattern, normalized):
                matches.append(keyword)

        if matches:
            results[domain] = sorted(matches)

    return results