from dataclasses import dataclass
from src.analytics.role_fit import RoleFitAnalyzer
from src.analytics.job_matcher import JobMatcher
from src.analytics.seniority_fit import SeniorityFitAnalyzer
from src.database.models import Job
from src.profile.candidate import CandidateProfile
from src.analytics.domain_fit import DomainFitAnalyzer


@dataclass(frozen=True)
class OpportunityScore:
    job_id: int | None
    title: str
    company: str

    skill_match: float
    evidence_score: float
    role_fit: float
    role_label: str
    matched_role: str | None
    seniority_level: str
    seniority_fit: float
    seniority_label: str
    seniority_multiplier: float
    opportunity_score: float
    domain_fit: float
    domain_label: str
    matched_domains: tuple[str, ...]
    domain_evidence_level: str

    matched_skills: tuple[str, ...]
    missing_skills: tuple[str, ...]


class OpportunityScorer:
    """
    Score jobs using candidate-specific fit dimensions.

    Current dimensions:
        - Technical skill alignment
        - Skill evidence quality
        - Target role relevance
        - Seniority compatibility
        - Preferred domain relevance

    The final score uses weighted technical, role, and
    seniority alignment, applies a seniority compatibility
    multiplier, and adds a small evidence-based domain bonus.

    Individual dimensions remain available for explainability.
    """

    SKILL_WEIGHT = 0.45
    ROLE_WEIGHT = 0.30
    SENIORITY_WEIGHT = 0.25

    def __init__(
        self,
        candidate: CandidateProfile,
    ) -> None:
        self.candidate = candidate

        self.job_matcher = JobMatcher(
            candidate.normalized_skills()
        )

        self.role_analyzer = RoleFitAnalyzer(
            candidate.target_roles
        )

        self.seniority_analyzer = SeniorityFitAnalyzer(
            candidate.target_seniority
        )

        self.domain_analyzer = DomainFitAnalyzer(
            preferred_domains=candidate.preferred_domains
        )

    def score_job(
        self,
        job: Job,
    ) -> OpportunityScore:
        skill_result = self.job_matcher.match_job(job)

        seniority_result = (
            self.seniority_analyzer.analyze(job)
        )

        role_result = self.role_analyzer.analyze(job)
        # JobMatcher already discounts skill match according
        # to the amount of available skill evidence.
        technical_score = skill_result.ranking_score

        base_score = (
            technical_score * self.SKILL_WEIGHT
            + role_result.score * self.ROLE_WEIGHT
            + seniority_result.fit_score
            * self.SENIORITY_WEIGHT
        )

        seniority_multiplier = {
            "target": 1.00,
            "stretch": 0.90,
            "high_stretch": 0.70,
            "unlikely": 0.40,
            "poor_fit": 0.15,
            "unknown": 0.75,
        }.get(
            seniority_result.fit_label,
            0.75,
        )

        opportunity_score = (
            base_score * seniority_multiplier
        )

        domain_bonus = 0.0
        domain_result = self.domain_analyzer.analyze(job)
        if domain_result.label == "preferred":
            domain_bonus = {
                "insufficient": 0.0,
                "low": 2.0,
                "medium": 4.0,
                "high": 5.0,
            }.get(domain_result.evidence_level, 0.0)

        opportunity_score = min(
            100.0,
            opportunity_score + domain_bonus * seniority_multiplier,
        )

        return OpportunityScore(
            job_id=job.id,
            title=job.title,
            company=job.company,
            role_fit=role_result.score,
            role_label=role_result.label,
            matched_role=role_result.matched_role,

            skill_match=skill_result.match_percentage,
            evidence_score=skill_result.evidence_score,

            seniority_level=(
                seniority_result.job_level_label
            ),
            domain_fit=domain_result.score,
            domain_label=domain_result.label,
            matched_domains=domain_result.matched_domains,
            domain_evidence_level=domain_result.evidence_level,
            seniority_multiplier=seniority_multiplier,
            seniority_fit=(
                seniority_result.fit_score
            ),

            seniority_label=(
                seniority_result.fit_label
            ),

            opportunity_score=round(
                opportunity_score,
                2,
            ),

            matched_skills=(
                skill_result.matched_skills
            ),

            missing_skills=(
                skill_result.missing_skills
            ),
        )

    def rank_jobs(
        self,
        jobs: list[Job],
    ) -> list[OpportunityScore]:
        results = [
            self.score_job(job)
            for job in jobs
        ]

        return sorted(
            results,
            key=lambda item: (
                item.opportunity_score,
                item.evidence_score,
                item.skill_match,
            ),
            reverse=True,
        )