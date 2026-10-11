from dataclasses import dataclass

from src.analytics.opportunity import OpportunityScorer
from src.analytics.opportunity_diagnostics import OpportunityDiagnostics
from src.database.models import Job
from src.profile.candidate import CandidateProfile


@dataclass(frozen=True)
class EnrichmentCandidate:
    job_id: int | None
    title: str
    company: str
    location: str
    opportunity_score: float
    recommendation: str
    evidence_score: float
    priority: int


class EnrichmentQueue:

    def __init__(self, candidate: CandidateProfile):
        self.scorer = OpportunityScorer(candidate)

    def build(self, jobs: list[Job]) -> list[EnrichmentCandidate]:
        queue = []

        for job in jobs:
            result = self.scorer.score_job(job)
            diagnostic = OpportunityDiagnostics.analyze(result)

            description = (job.description or "").strip()
            has_structured_details = any(
                bool(getattr(job, field, None))
                for field in (
                    "requirements",
                    "responsibilities",
                    "skills",
                )
            )

            needs_enrichment = (
                len(description) <= 500
                or not has_structured_details
            )

            if not needs_enrichment:
                continue

            if diagnostic.recommendation == "strong_review":
                priority = 1
            elif diagnostic.recommendation == "needs_more_evidence":
                priority = 2
            elif diagnostic.recommendation == "consider":
                priority = 3
            else:
                priority = 4

            queue.append(
                EnrichmentCandidate(
                    job_id=job.id,
                    title=job.title or "",
                    company=job.company or "",
                    location=job.location or "",
                    opportunity_score=result.opportunity_score,
                    recommendation=diagnostic.recommendation,
                    evidence_score=result.evidence_score,
                    priority=priority,
                )
            )

        return sorted(
            queue,
            key=lambda item: (
                item.priority,
                item.evidence_score,
                -item.opportunity_score,
            ),
        )