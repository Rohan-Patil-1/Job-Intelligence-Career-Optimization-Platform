from collections import Counter
from dataclasses import dataclass

from src.analytics.skill_extractor import extract_skills
from src.database.models import Job


@dataclass(frozen=True)
class SkillStat:
    skill: str
    job_count: int
    percentage: float


class SkillAnalyzer:
    """Analyze observed skill mentions across job records."""

    def __init__(self, jobs: list[Job]) -> None:
        self.jobs = jobs

    @staticmethod
    def _job_text(job: Job) -> str:
        return " ".join(
            value
            for value in (
                job.title,
                job.description,
                job.requirements,
                job.responsibilities,
                job.skills,
            )
            if value
        )

    def skills_for_job(self, job: Job) -> list[str]:
        return extract_skills(self._job_text(job))

    def skill_counts(self) -> Counter:
        counts = Counter()

        for job in self.jobs:
            counts.update(self.skills_for_job(job))

        return counts

    def skill_stats(self) -> list[SkillStat]:
        if not self.jobs:
            return []

        counts = self.skill_counts()
        total_jobs = len(self.jobs)

        return [
            SkillStat(
                skill=skill,
                job_count=count,
                percentage=round((count / total_jobs) * 100, 2),
            )
            for skill, count in counts.most_common()
        ]

    def jobs_with_skills(self) -> int:
        return sum(
            1
            for job in self.jobs
            if self.skills_for_job(job)
        )

    def coverage_percentage(self) -> float:
        if not self.jobs:
            return 0.0

        return round(
            (self.jobs_with_skills() / len(self.jobs)) * 100,
            2,
        )