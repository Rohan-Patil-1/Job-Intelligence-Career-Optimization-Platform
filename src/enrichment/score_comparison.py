
from dataclasses import dataclass

from src.analytics.opportunity import (
    OpportunityScorer,
    OpportunityScore,
)
from src.analytics.opportunity_diagnostics import (
    OpportunityDiagnostics,
    OpportunityDiagnostic,
)
from src.database.models import Job
from src.profile.candidate import CandidateProfile


@dataclass(frozen=True)
class ScoreComparison:
    baseline: OpportunityScore
    provisional: OpportunityScore
    baseline_diagnostic: OpportunityDiagnostic
    provisional_diagnostic: OpportunityDiagnostic
    score_delta: float
    evidence_delta: float
    skill_match_delta: float
    newly_matched_skills: tuple[str, ...]
    newly_missing_skills: tuple[str, ...]
    validation_status: str
    source_type: str
    production_eligible: bool


class OpportunityScoreComparator:
    """
    Compare baseline and enriched descriptions using the
    existing opportunity scoring pipeline.

    The original SQLAlchemy Job is never modified.
    """

    def __init__(self, candidate: CandidateProfile):
        self.scorer = OpportunityScorer(candidate)

    def compare(
        self,
        *,
        job: Job,
        enriched_description: str,
        validation_status: str,
        source_type: str,
    ) -> ScoreComparison:

        if not enriched_description.strip():
            raise ValueError(
                "Enriched description must not be empty."
            )

        # Create a separate, transient Job object.
        # Do not attach it to a database session.
        provisional_job = Job()

        # Copy mapped column values, without relationships.
        for column in Job.__table__.columns:
            setattr(
                provisional_job,
                column.key,
                getattr(job, column.key),
            )

        # Override only the description.
        provisional_job.description = enriched_description

        baseline = self.scorer.score_job(job)
        provisional = self.scorer.score_job(provisional_job)

        baseline_diagnostic = OpportunityDiagnostics.analyze(
            baseline
        )
        provisional_diagnostic = OpportunityDiagnostics.analyze(
            provisional
        )

        baseline_matched = set(baseline.matched_skills)
        provisional_matched = set(provisional.matched_skills)

        baseline_missing = set(baseline.missing_skills)
        provisional_missing = set(provisional.missing_skills)

        return ScoreComparison(
            baseline=baseline,
            provisional=provisional,
            baseline_diagnostic=baseline_diagnostic,
            provisional_diagnostic=provisional_diagnostic,
            score_delta=round(
                provisional.opportunity_score
                - baseline.opportunity_score,
                2,
            ),
            evidence_delta=round(
                provisional.evidence_score
                - baseline.evidence_score,
                2,
            ),
            skill_match_delta=round(
                provisional.skill_match
                - baseline.skill_match,
                2,
            ),
            newly_matched_skills=tuple(
                sorted(provisional_matched - baseline_matched)
            ),
            newly_missing_skills=tuple(
                sorted(provisional_missing - baseline_missing)
            ),
            validation_status=validation_status,
            source_type=source_type,
            production_eligible=(
                validation_status == "verified"
                and source_type == "employer"
            ),
        )
