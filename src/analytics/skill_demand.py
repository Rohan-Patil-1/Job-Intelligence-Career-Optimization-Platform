from collections import Counter
from dataclasses import dataclass

from src.analytics.skills import SkillAnalyzer
from src.analytics.skill_vocabulary import SKILL_CATEGORIES
from src.database.models import Job


@dataclass(frozen=True)
class SkillDemand:
    skill: str
    job_count: int
    total_jobs: int
    jobs_with_skill_data: int
    observed_percentage: float
    coverage_adjusted_percentage: float


@dataclass(frozen=True)
class CategoryDemand:
    category: str
    job_count: int
    percentage: float


class SkillDemandAnalyzer:
    """
    Analyze observed skill demand across job records.

    Because some sources provide partial job descriptions,
    these values represent observed skill mentions rather
    than definitive market demand.
    """

    def __init__(self, jobs: list[Job]) -> None:
        self.jobs = jobs
        self.skill_analyzer = SkillAnalyzer(jobs)

    def demand(self) -> list[SkillDemand]:
        if not self.jobs:
            return []

        counts = self.skill_analyzer.skill_counts()

        total_jobs = len(self.jobs)
        jobs_with_skill_data = self.skill_analyzer.jobs_with_skills()

        results = []

        for skill, count in counts.most_common():
            observed_percentage = (
                count / total_jobs
            ) * 100

            coverage_adjusted_percentage = (
                (count / jobs_with_skill_data) * 100
                if jobs_with_skill_data
                else 0.0
            )

            results.append(
                SkillDemand(
                    skill=skill,
                    job_count=count,
                    total_jobs=total_jobs,
                    jobs_with_skill_data=jobs_with_skill_data,
                    observed_percentage=round(
                        observed_percentage,
                        2,
                    ),
                    coverage_adjusted_percentage=round(
                        coverage_adjusted_percentage,
                        2,
                    ),
                )
            )

        return results

    def top_skills(
        self,
        limit: int = 10,
    ) -> list[SkillDemand]:
        if limit <= 0:
            return []

        return self.demand()[:limit]

    def category_counts(self) -> Counter:
        """
        Count each skill category at most once per job.
        """
        counts = Counter()

        for job in self.jobs:
            skills = self.skill_analyzer.skills_for_job(job)

            categories = {
                SKILL_CATEGORIES[skill]
                for skill in skills
                if skill in SKILL_CATEGORIES
            }

            counts.update(categories)

        return counts

    def category_demand(self) -> list[CategoryDemand]:
        """
        Calculate the percentage of jobs mentioning
        at least one skill from each category.
        """
        if not self.jobs:
            return []

        counts = self.category_counts()
        total_jobs = len(self.jobs)

        return [
            CategoryDemand(
                category=category,
                job_count=count,
                percentage=round(
                    (count / total_jobs) * 100,
                    2,
                ),
            )
            for category, count in counts.most_common()
        ]