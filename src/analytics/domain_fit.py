from dataclasses import dataclass
from collections import defaultdict

from src.analytics.domain_extractor import extract_domains
from src.database.models import Job


DOMAIN_SOURCES = (
    "title",
    "description",
    "requirements",
    "responsibilities",
)


@dataclass(frozen=True)
class DomainFit:
    detected_domains: tuple[str, ...]
    matched_domains: tuple[str, ...]
    evidence: dict[str, list[str]]
    score: float
    label: str

    evidence_count: int
    evidence_level: str
    evidence_sources: tuple[str, ...]
    evidence_by_source: dict[str, dict[str, list[str]]]


class DomainFitAnalyzer:
    def __init__(
        self,
        preferred_domains: set[str],
    ) -> None:
        self.preferred_domains = {
            domain.strip().lower()
            for domain in preferred_domains
            if domain.strip()
        }

    @staticmethod
    def _evidence_level(count: int) -> str:
        if count == 0:
            return "insufficient"
        if count <= 2:
            return "low"
        if count <= 4:
            return "medium"
        return "high"

    def analyze(self, job: Job) -> DomainFit:
        evidence_by_source = {}
        combined = defaultdict(set)

        for source in DOMAIN_SOURCES:
            value = getattr(job, source, None)

            if not value:
                continue

            extracted = extract_domains(value)

            if not extracted:
                continue

            evidence_by_source[source] = extracted

            for domain, keywords in extracted.items():
                combined[domain].update(keywords)

        evidence = {
            domain: sorted(keywords)
            for domain, keywords in sorted(combined.items())
        }

        detected = set(evidence)
        matched = detected & self.preferred_domains

        if not detected:
            score = 0.0
            label = "unknown"
        elif matched:
            score = 100.0
            label = "preferred"
        else:
            score = 40.0
            label = "other_domain"

        # Count unique (domain, keyword) pairs.
        # Repetition across fields does not inflate evidence.
        evidence_count = sum(
            len(keywords)
            for keywords in evidence.values()
        )

        return DomainFit(
            detected_domains=tuple(sorted(detected)),
            matched_domains=tuple(sorted(matched)),
            evidence=evidence,
            score=score,
            label=label,
            evidence_count=evidence_count,
            evidence_level=self._evidence_level(evidence_count),
            evidence_sources=tuple(
                source
                for source in DOMAIN_SOURCES
                if source in evidence_by_source
            ),
            evidence_by_source=evidence_by_source,
        )