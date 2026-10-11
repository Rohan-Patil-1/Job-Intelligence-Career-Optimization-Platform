from dataclasses import dataclass

from src.analytics.skill_demand import SkillDemandAnalyzer
from src.database.models import Job


@dataclass(frozen=True)
class SkillGap:
    skill: str
    job_count: int
    observed_percentage: float


@dataclass(frozen=True)
class SkillMatchSummary:
    market_skills: int
    candidate_skills: int
    matched_skills: int
    missing_skills: int
    match_percentage: float
    weighted_match_percentage: float


class SkillGapAnalyzer:
    """Compare candidate skills against observed market skills."""

    def __init__(
        self,
        jobs: list[Job],
        candidate_skills: set[str],
    ) -> None:
        self.jobs = jobs

        self.candidate_skills = {
            skill.strip().lower()
            for skill in candidate_skills
            if skill.strip()
        }

        self.demand_analyzer = SkillDemandAnalyzer(jobs)

    def matched_skills(self) -> list[str]:
        market_skills = {
            item.skill
            for item in self.demand_analyzer.demand()
        }

        return sorted(
            market_skills & self.candidate_skills
        )

    def missing_skills(self) -> list[SkillGap]:
        return [
            SkillGap(
                skill=item.skill,
                job_count=item.job_count,
                observed_percentage=item.observed_percentage,
            )
            for item in self.demand_analyzer.demand()
            if item.skill not in self.candidate_skills
        ]

    def weighted_match_percentage(self) -> float:
        """
        Weight skill alignment by observed job frequency.

        Example:
            Python appears in 10 jobs.
            Docker appears in 1 job.

        Matching Python contributes more to alignment than
        matching Docker.
        """
        demand = self.demand_analyzer.demand()

        if not demand:
            return 0.0

        total_weight = sum(
            item.job_count
            for item in demand
        )

        if total_weight == 0:
            return 0.0

        matched_weight = sum(
            item.job_count
            for item in demand
            if item.skill in self.candidate_skills
        )

        return round(
            (matched_weight / total_weight) * 100,
            2,
        )

    def summary(self) -> SkillMatchSummary:
        market_skills = {
            item.skill
            for item in self.demand_analyzer.demand()
        }

        matched = market_skills & self.candidate_skills
        missing = market_skills - self.candidate_skills

        match_percentage = (
            (len(matched) / len(market_skills)) * 100
            if market_skills
            else 0.0
        )

        return SkillMatchSummary(
            market_skills=len(market_skills),
            candidate_skills=len(self.candidate_skills),
            matched_skills=len(matched),
            missing_skills=len(missing),
            match_percentage=round(
                match_percentage,
                2,
            ),
            weighted_match_percentage=(
                self.weighted_match_percentage()
            ),
        )